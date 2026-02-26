import os
from dotenv import load_dotenv
from textwrap import dedent
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from groq import Groq as GroqClient
from ddgs import DDGS
import markdown2
from urllib.parse import urlparse

load_dotenv()

# ── Validation ───────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("groq_api_key")
if not GROQ_API_KEY:
    raise RuntimeError("groq_api_key environment variable is required")

# ── App setup ────────────────────────────────────────────────────────────────
app = Flask(__name__)

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    os.getenv("FRONTEND_URL", "https://fin-ai.vercel.app"),
]
CORS(app, origins=ALLOWED_ORIGINS)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["30 per minute"],
    storage_uri="memory://",
)

client = GroqClient(api_key=GROQ_API_KEY)

# ── Constants ────────────────────────────────────────────────────────────────
QUERY_MODEL    = "llama-3.3-70b-versatile"
RESEARCH_MODEL = "llama-3.3-70b-versatile"
MAX_QUERY_LEN  = 500
MAX_SEARCH_RESULTS = 6

DEFAULT_CRED_SCORE = 0.5
SOURCE_SCORES = {
    # ── Indian Regulators & Government ───────────────────────────────────────
    "rbi.org.in":                    1.0,   # Reserve Bank of India
    "sebi.gov.in":                   1.0,   # Securities & Exchange Board of India
    "finmin.nic.in":                 1.0,   # Ministry of Finance, India
    "nseindia.com":                  0.95,  # National Stock Exchange
    "bseindia.com":                  0.95,  # Bombay Stock Exchange
    "pib.gov.in":                    0.9,   # Press Information Bureau (India govt)
    "indiabudget.gov.in":            1.0,   # India Budget portal

    # ── Global Regulators & Central Banks ────────────────────────────────────
    "federalreserve.gov":            1.0,   # US Federal Reserve
    "sec.gov":                       1.0,   # US SEC
    "treasury.gov":                  1.0,   # US Treasury
    "ecb.europa.eu":                 1.0,   # European Central Bank
    "bankofengland.co.uk":           1.0,   # Bank of England
    "imf.org":                       1.0,   # International Monetary Fund
    "worldbank.org":                 1.0,   # World Bank
    "bis.org":                       1.0,   # Bank for International Settlements
    "oecd.org":                      0.98,  # OECD

    # ── Tier-1 Global Financial News ─────────────────────────────────────────
    "reuters.com":                   0.95,
    "bloomberg.com":                 0.95,
    "ft.com":                        0.95,  # Financial Times
    "wsj.com":                       0.93,  # Wall Street Journal
    "cnbc.com":                      0.85,
    "economist.com":                 0.93,
    "barrons.com":                   0.90,  # Barron's
    "marketwatch.com":               0.85,
    "trading economics.com":         0.82,
    "investing.com":                 0.78,

    # ── Investment Banks & Research ──────────────────────────────────────────
    "jpmorgan.com":                  0.92,  # JPMorgan Chase
    "goldmansachs.com":              0.92,  # Goldman Sachs
    "morganstanley.com":             0.92,  # Morgan Stanley
    "blackrock.com":                 0.90,  # BlackRock
    "vanguard.com":                  0.88,  # Vanguard
    "fidelity.com":                  0.87,  # Fidelity
    "ubs.com":                       0.88,  # UBS
    "credit-suisse.com":             0.85,
    "mckinsey.com":                  0.88,  # McKinsey & Company

    # ── Indian Financial Media ────────────────────────────────────────────────
    "economictimes.indiatimes.com":  0.78,
    "livemint.com":                  0.80,
    "moneycontrol.com":              0.72,
    "financialexpress.com":          0.75,
    "business-standard.com":         0.78,
    "thehindubusinessline.com":      0.78,
    "ndtvprofit.com":                0.70,

    # ── Other Reliable Finance Sources ───────────────────────────────────────
    "morningstar.com":               0.88,  # Morningstar (fund research)
    "tradingview.com":               0.72,
    "statista.com":                  0.80,
    "macrotrends.net":               0.75,
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def web_search(query: str, max_results: int = MAX_SEARCH_RESULTS) -> list:
    """Search DuckDuckGo directly and return a list of result dicts."""
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "url":   r.get("href", ""),
                    "body":  r.get("body", ""),
                })
    except Exception:
        pass
    return results


def format_search_context(results: list) -> str:
    """Convert search results into a numbered context block for the prompt."""
    if not results:
        return "No search results found."
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"[{i}] {r['title']}\nURL: {r['url']}\n{r['body']}\n")
    return "\n".join(lines)


def score_sources(results: list) -> list:
    scored = []
    for r in results:
        domain = urlparse(r["url"]).netloc.replace("www.", "")
        scored.append({
            "url":    r["url"],
            "domain": domain,
            "score":  SOURCE_SCORES.get(domain, DEFAULT_CRED_SCORE),
        })
    return scored


def beautify_markdown(content: str) -> str:
    return markdown2.markdown(content)


def validate_query(data):
    if not data or not isinstance(data, dict):
        return None, (jsonify({"error": "JSON body required"}), 400)
    user_query = data.get("query", "").strip()
    if not user_query:
        return None, (jsonify({"error": "Query is required"}), 400)
    if len(user_query) > MAX_QUERY_LEN:
        return None, (jsonify({"error": f"Query too long (max {MAX_QUERY_LEN} characters)"}), 400)
    return user_query, None


def call_groq(model: str, system: str, user: str) -> str:
    """Call Groq chat completion — no tool calls, pure text generation."""
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        temperature=0.3,
        max_tokens=4096,
    )
    return resp.choices[0].message.content


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/query", methods=["POST"])
@limiter.limit("10 per minute")
def query_mode():
    user_query, err = validate_query(request.json)
    if err:
        return err

    try:
        results = web_search(user_query)

        # Retry with authoritative sources if nothing found
        if not results:
            fallback = f"{user_query} site:rbi.org.in OR site:sebi.gov.in OR site:reuters.com"
            results = web_search(fallback)

        context = format_search_context(results)

        system = dedent("""\
            You are an elite financial research analyst.
            You will be given web search results as context.
            Answer the user's question concisely in 5–8 bullet points.
            Base your answer ONLY on the provided search results.
            Do NOT speculate beyond the sources.
            Format your response in clean Markdown.
        """)

        user_msg = f"""Question: {user_query}

Search Results:
{context}

Please answer the question in 5–8 bullet points using only the above sources."""

        content = call_groq(QUERY_MODEL, system, user_msg)
        scored  = score_sources(results)
        confidence = round(sum(s["score"] for s in scored) / len(scored), 2) if scored else 0.0

        return jsonify({
            "response":         beautify_markdown(content),
            "Sources":          scored,
            "Confidence_score": confidence,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/research", methods=["POST"])
@limiter.limit("5 per minute")
def research_mode():
    user_query, err = validate_query(request.json)
    if err:
        return err

    try:
        # Search with multiple angle queries for deeper coverage
        base_results     = web_search(user_query, max_results=5)
        analysis_results = web_search(f"{user_query} analysis expert opinion", max_results=4)
        future_results   = web_search(f"{user_query} future outlook implications 2025", max_results=3)

        all_results = base_results + analysis_results + future_results
        # Deduplicate by URL
        seen_urls   = set()
        unique_results = []
        for r in all_results:
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                unique_results.append(r)

        context = format_search_context(unique_results)

        system = dedent("""\
            You are an elite financial research analyst producing a comprehensive report.
            You will be given web search results as context.
            Use ONLY the provided sources — do not invent facts.
            Write in Financial Report style with clear section headers.
            Format beautifully in Markdown with headers, bullet points, and bold key terms.
        """)

        user_msg = f"""Topic: {user_query}

Search Results:
{context}

Write a comprehensive financial research report (minimum 1000 words) with these sections:
# [Compelling Headline]

## Executive Summary
[2–3 paragraph overview]

## Background & Context
[Historical context and current landscape]

## Key Findings
[Main discoveries with supporting evidence from the sources]

## Impact Analysis
[Current implications, stakeholder perspectives, industry effects]

## Future Outlook
[Emerging trends, expert predictions, challenges and opportunities]

## Sources & Methodology
[List sources used, note the search methodology]

---
*Research conducted by Finance AI Agent | {__import__('datetime').date.today()}*"""

        content = call_groq(RESEARCH_MODEL, system, user_msg)
        scored  = score_sources(unique_results)
        confidence = round(sum(s["score"] for s in scored) / len(scored), 2) if scored else 0.0

        return jsonify({
            "response":         beautify_markdown(content),
            "Sources":          scored,
            "Confidence_score": confidence,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
