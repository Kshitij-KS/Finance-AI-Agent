import os
from dotenv import load_dotenv
from textwrap import dedent
from flask import Flask, jsonify, request
from flask_cors import CORS
from agno.agent.agent import Agent
from agno.models.groq.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools
import markdown2
from urllib.parse import urlparse

load_dotenv()

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv("groq_api_key")
QUERY_MODEL = "llama-3.1-8b-instant"
RESEARCH_MODEL = "llama-3.3-70b-versatile"

DEFAULT_CRED_SCORE = 0.5

SOURCE_SCORES = {
    "reuters.com": 0.95,
    "bloomberg.com": 0.95,
    "rbi.org.in": 1.0,
    "sebi.gov.in": 1.0,
    "economictimes.indiatimes.com": 0.7,
}

DESCRIPTION =dedent("""\ You are an elite research analyst in the financial services domain.
Your expertise encompasses:
 - Deep investigative financial research and analysis 
 - Fact-checking and source verification 
 - Data-driven reporting and visualization 
 - Expert interview synthesis 
 - Trend analysis and future predictions 
 - Complex topic simplification 
 - Ethical practices 
 - Balanced perspective presentation 
 - Global context integration\ 
 """)
 
QUERY_INSTRUCTIONS = dedent("""
MANDATORY WORKFLOW (STRICT):
1. You MUST call duckduckgo_search before answering.
2. Use only tool results.
3. Answer in 5–8 bullets.

RULES:
- Answer concisely (5–8 bullet points max)
- Do NOT speculate
- Cite sources by domain name only
""")

QUERY_EXPECTED_OUTPUT = dedent("""
Answer:
{Concise answer}

Sources:
{List of sources used}
""")

def beautify_markdown(content: str) -> str:
    if "- Running: duckduckgo_search" in content:
        content = content.split("\n\n", 1)[-1]
    return markdown2.markdown(content)


def normalize_sources(raw):
    return [{"url": r["url"]} for r in raw if isinstance(r, dict) and r.get("url")]


def score_sources(sources):
    scored = []
    for s in sources:
        domain = urlparse(s["url"]).netloc.replace("www.", "")
        scored.append({
            "url": s["url"],
            "domain": domain,
            "score": SOURCE_SCORES.get(domain, DEFAULT_CRED_SCORE)
        })
    return scored


def extract_sources_from_run(result):
    collected = []
    run_data = result.to_dict()

    runs = run_data.get("runs", [])
    if not runs:
        return collected

    messages = runs[0].get("messages", [])
    for msg in messages:
        if msg.get("role") == "tool" and msg.get("name") == "duckduckgo_search":
            output = msg.get("content", [])
            if isinstance(output, list):
                for item in output:
                    url = item.get("url") or item.get("link")
                    if url:
                        collected.append({"url": url})
    return collected


def run_agent_with_retry(agent, query):
    """
    Run agent once, retry once with a constrained query if no sources found.
    """
    result = agent.run(query)
    sources = extract_sources_from_run(result)

    if sources:
        return result, sources

    # Retry
    retry_query = f"{query} site:rbi.org.in OR site:sebi.gov.in OR site:reuters.com latest"
    retry_result = agent.run(retry_query)
    retry_sources = extract_sources_from_run(retry_result)

    return retry_result, retry_sources


def build_agent(model_id, instructions, expected_output=None):
    return Agent(
        model=Groq(id=model_id, api_key=GROQ_API_KEY),
        tools=[DuckDuckGoTools(), Newspaper4kTools()],
        description=DESCRIPTION,
        instructions=instructions,
        expected_output=expected_output,
        markdown=True,
        show_tool_calls=True,
        add_datetime_to_instructions=True,
    )

@app.route("/query", methods=["POST"])
def query_mode():
    user_query = request.json.get("query")
    if not user_query:
        return jsonify({"error": "Query is required"}), 400

    agent = build_agent(QUERY_MODEL, QUERY_INSTRUCTIONS, QUERY_EXPECTED_OUTPUT)

    try:
        result, collected_sources = run_agent_with_retry(agent, user_query)

        normalized = normalize_sources(collected_sources)
        scored = score_sources(normalized)
        confidence = round(sum(s["score"] for s in scored) / len(scored), 2) if scored else 0.0

        return jsonify({
            "response": beautify_markdown(result.content),
            "Sources": scored,
            "Confidence_score": confidence
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/research", methods=["POST"])
def research_mode():
    user_query = request.json.get("query")
    if not user_query:
        return jsonify({"error": "Query is required"}), 400

    agent = Agent(
    model=Groq(id=RESEARCH_MODEL, api_key=GROQ_API_KEY),
    tools=[DuckDuckGoTools(), Newspaper4kTools()],
    description=dedent("""\
        You are an elite research analyst in the financial services domain.
        Your expertise encompasses:
        - Deep investigative financial research and analysis
        - Fact-checking and source verification
        - Data-driven reporting and visualization
        - Expert interview synthesis
        - Trend analysis and future predictions
        - Complex topic simplification
        - Ethical practices
        - Balanced perspective presentation
        - Global context integration\
    """),
    instructions=dedent("""\
        1. Research Phase
           - Search for 5 authoritative sources on the topic
           - Prioritize recent publications and expert opinions
           - Identify key stakeholders and perspectives

        2. Analysis Phase
           - Extract and verify critical information
           - Cross-reference facts across multiple sources
           - Identify emerging patterns and trends
           - Evaluate conflicting viewpoints

        3. Writing Phase
           - Craft an attention-grabbing headline
           - Structure content in Financial Report style
           - Include relevant quotes and statistics
           - Maintain objectivity and balance
           - Explain complex concepts clearly
           - Write atleast 1500 words

        4. Quality Control
           - Verify all facts and attributions
           - Ensure narrative flow and readability
           - Add context where necessary
           - Add as many relevant points as you can
           - Include future implications\
    """),
    expected_output=dedent("""\
        {Compelling Headline}

        Executive Summary\
        {Concise overview of key findings and significance}

        Background & Context\
        {Historical context and importance in 300 words}
        {Current landscape overview in 200 words}

        Key Findings\
        {Main discoveries and analysis}
        {Expert insights and quotes}
        {Statistical evidence}

        Impact Analysis\
        {Current implications}
        {Stakeholder perspectives}
        {Industry/societal effects}

        Future Outlook\
        {Emerging trends}
        {Expert predictions}
        {Potential challenges and opportunities}

        Expert Insights\
        {Notable quotes and analysis from industry leaders}
        {Contrasting viewpoints}

        Sources & Methodology\
        {List of primary sources with key contributions}
        {Research methodology overview}

        ---
        Research conducted by Financial Agent,
        Credit Rating Style Report,
        Published: {current_date},
        Last Updated: {current_time}\
    """),
    markdown=True,
    show_tool_calls=True,
    add_datetime_to_instructions=True,
)

    try:
        result, collected_sources = run_agent_with_retry(agent, user_query)

        normalized = normalize_sources(collected_sources)
        scored = score_sources(normalized)
        confidence = round(sum(s["score"] for s in scored) / len(scored), 2) if scored else 0.0

        return jsonify({
            "response": beautify_markdown(result.content),
            "Sources": scored,
            "Confidence_score": confidence
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)