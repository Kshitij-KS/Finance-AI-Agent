import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import DOMPurify from 'dompurify';

function App() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [sources, setSources] = useState([]);
  const [confidence, setConfidence] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [mode, setMode] = useState('query');
  const [showAbout, setShowAbout] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setResponse('');
    setSources([]);
    setConfidence(null);
    setError('');

    try {
      const backendURL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';
      const result = await axios.post(`${backendURL}/${mode}`, { query });

      setResponse(result.data.response || '');
      setSources(result.data.Sources || []);
      setConfidence(
        result.data.Confidence_score !== undefined ? result.data.Confidence_score : null
      );
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  const confidenceLabel = (score) => {
    if (score >= 0.80) return { label: 'High', className: 'confidence-high' };
    if (score >= 0.60) return { label: 'Medium', className: 'confidence-medium' };
    return { label: 'Low', className: 'confidence-low' };
  };

  return (
    <div className="app-root">
      <div className="app-card" role="region" aria-label="Finance AI agent">

        {/* ── HEADER ── */}
        <div className="app-header">
          <div className="app-header-badge">AI · Finance Research</div>
          <h1 className="app-title">Finance AI Research Agent</h1>
          <p className="app-subtitle">Real-time financial intelligence from the world's most trusted sources.</p>
          <button
            className="about-toggle"
            onClick={() => setShowAbout(v => !v)}
            aria-expanded={showAbout}
          >
            {showAbout ? '✕ Close' : 'ℹ How it works'}
          </button>
        </div>

        {/* ── ABOUT PANEL ── */}
        {showAbout && (
          <div className="about-panel" role="region" aria-label="About this tool">
            <div className="about-grid">

              <div className="about-card">
                <div className="about-icon">🔍</div>
                <h3>How it works</h3>
                <p>
                  Every query triggers a live web search across dozens of financial sources.
                  Your question is never answered from a static database — it's always fresh,
                  cross-referenced data from real-time results.
                </p>
              </div>

              <div className="about-card">
                <div className="about-icon">⚡</div>
                <h3>Quick Answer</h3>
                <p>
                  Searches the web and delivers a concise, bullet-pointed summary in seconds.
                  Best for fast lookups — stock prices, policy changes, earnings dates, definitions.
                </p>
              </div>

              <div className="about-card">
                <div className="about-icon">📑</div>
                <h3>Deep Research</h3>
                <p>
                  Runs three parallel search angles — base facts, expert analysis, and future
                  outlook — then synthesises them into a structured report with an executive
                  summary, key findings, and implications. Ideal for investment research.
                </p>
              </div>

              <div className="about-card">
                <div className="about-icon">🛡️</div>
                <h3>Source Credibility</h3>
                <p>
                  Every source is scored by domain authority. Regulators like RBI, SEBI, the Fed,
                  IMF, and World Bank score <strong>1.0</strong>. Tier-1 outlets — Bloomberg,
                  Reuters, FT, WSJ — score <strong>0.93–0.95</strong>. Investment banks like
                  JPMorgan and Goldman Sachs score <strong>0.92</strong>. Indian financial media
                  (ET, Mint, Business Standard) score <strong>0.72–0.80</strong>.
                  Unknown sites default to <strong>0.50</strong>.
                </p>
              </div>

              <div className="about-card">
                <div className="about-icon">📊</div>
                <h3>Confidence Score</h3>
                <p>
                  Calculated as <strong>60% best source + 40% average</strong> across all results.
                  This means one authoritative source (e.g. RBI = 1.0) meaningfully raises
                  the score even if other results are from unknown sites. Thresholds:
                  <strong> High ≥ 80%</strong>, <strong>Medium ≥ 60%</strong>,
                  <strong> Low &lt; 60%</strong>.
                </p>
              </div>

              <div className="about-card">
                <div className="about-icon">🤖</div>
                <h3>The AI Model</h3>
                <p>
                  Powered by <strong>Llama 3.3 70B</strong> via Groq's ultra-fast inference
                  platform. The model reads the retrieved sources and synthesises them — it
                  is explicitly instructed never to speculate beyond what the sources say,
                  keeping hallucinations minimal.
                </p>
              </div>

            </div>

            <div className="about-disclaimer">
              ⚠️ <strong>Disclaimer:</strong> This tool is for informational research only and
              does not constitute financial advice. Always consult a registered financial
              advisor before making investment decisions.
            </div>
          </div>
        )}

        {/* ── MODE SELECTOR ── */}
        <div className="mode-selector">
          <label htmlFor="mode">Mode:</label>
          <select
            id="mode"
            value={mode}
            onChange={(e) => setMode(e.target.value)}
            disabled={loading}
          >
            <option value="query">⚡ Quick Answer</option>
            <option value="research">📑 Deep Research</option>
          </select>
        </div>

        {mode === 'research' && (
          <p className="research-hint">
            ⏳ Deep Research analyses multiple sources and writes a full report — this can take
            up to <strong>60 seconds</strong>.
          </p>
        )}

        {/* ── FORM ── */}
        <form className="app-form" onSubmit={handleSubmit} aria-label="Query form">
          <input
            className="app-input"
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a finance question…"
            maxLength={500}
            disabled={loading}
            aria-disabled={loading}
          />
          <button
            className="app-button"
            type="submit"
            disabled={loading || !query.trim()}
            aria-busy={loading ? 'true' : 'false'}
          >
            {loading
              ? mode === 'research'
                ? 'Researching…'
                : 'Thinking…'
              : 'Ask'}
          </button>
        </form>

        {/* ── RESPONSE ── */}
        <div className="app-response-container" role="status" aria-live="polite">
          <h2 className="app-response-title">Response</h2>

          {loading ? (
            <div className="generated-stack">
              {mode === 'research' && (
                <p className="loading-hint">Searching the web and writing your report…</p>
              )}
              <div className="generated generated-title" />
              <div className="generated generated-line" />
              <div className="generated generated-line" />
              <div className="generated generated-line short" />
            </div>
          ) : (
            <>
              {error && (
                <div className="error-banner" role="alert">
                  <span className="error-icon">⚠️</span> {error}
                </div>
              )}

              {confidence !== null && !error && (() => {
                const { label, className } = confidenceLabel(confidence);
                const pct = Math.round(confidence * 100);
                return (
                  <div className="confidence-wrapper">
                    <div className={`confidence-badge ${className}`}>
                      <span>SOURCE CONFIDENCE</span>
                      <span>·</span>
                      <strong className={className}>{label} ({pct}%)</strong>
                    </div>
                    <div className="confidence-bar-track">
                      <div
                        className={`confidence-bar-fill ${className}`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })()}

              {response && (
                <div
                  className="app-response-content fade-in"
                  dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(response) }}
                />
              )}

              {sources.length > 0 && (
                <div className="sources-section">
                  <h3>Sources</h3>
                  <ul>
                    {sources.map((s, i) => (
                      <li key={i}>
                        <a href={s.url} target="_blank" rel="noopener noreferrer">
                          {s.domain}
                        </a>{' '}
                        <span className="source-score">(credibility: {s.score})</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
