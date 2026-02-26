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
    if (score >= 0.85) return { label: 'High', className: 'confidence-high' };
    if (score >= 0.65) return { label: 'Medium', className: 'confidence-medium' };
    return { label: 'Low', className: 'confidence-low' };
  };

  return (
    <div className="app-root">
      <div className="app-card" role="region" aria-label="Finance AI agent">
        <h1 className="app-title">Finance AI Research Agent</h1>

        {/* MODE SELECTOR */}
        <div className="mode-selector">
          <label htmlFor="mode">Mode:</label>
          <select
            id="mode"
            value={mode}
            onChange={(e) => setMode(e.target.value)}
            disabled={loading}
          >
            <option value="query">Quick Answer</option>
            <option value="research">Deep Research</option>
          </select>
        </div>

        {mode === 'research' && (
          <p className="research-hint">
            ⏳ Deep Research analyses multiple sources and writes a full report — this can take
            up to <strong>60 seconds</strong>.
          </p>
        )}

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

        {/* RESPONSE */}
        <div
          className="app-response-container"
          role="status"
          aria-live="polite"
        >
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
              {/* ERROR BANNER */}
              {error && (
                <div className="error-banner" role="alert">
                  <span className="error-icon">⚠️</span> {error}
                </div>
              )}

              {/* CONFIDENCE SCORE */}
              {confidence !== null && !error && (() => {
                const { label, className } = confidenceLabel(confidence);
                const pct = Math.round(confidence * 100);
                return (
                  <div className="confidence-wrapper">
                    <div className={`confidence-badge ${className}`}>
                      Source Confidence: <strong>{label}</strong> ({pct}%)
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

              {/* MAIN RESPONSE */}
              {response && (
                <div
                  className="app-response-content fade-in"
                  dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(response) }}
                />
              )}

              {/* SOURCES */}
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
