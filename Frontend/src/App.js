import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [sources, setSources] = useState([]);
  const [confidence, setConfidence] = useState(null);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState('query');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setLoading(true);
    setResponse('');
    setSources([]);
    setConfidence(null);

    try {
      const backendURL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';
      const result = await axios.post(`${backendURL}/${mode}`, { query });
      
      setResponse(result.data.response || '');
      setSources(result.data.Sources || []);
      setConfidence(result.data.Confidence_score !== undefined
          ? result.data.Confidence_score : null
      );
    } catch (error) {
      const msg = `Error: ${error.response?.data?.error || error.message}`;
      setResponse(msg);
    } finally {
      setLoading(false);
    }
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

        <form
          className="app-form"
          onSubmit={handleSubmit}
          aria-label="Query form"
        >
          <input
            className="app-input"
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a finance question..."
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
              <div className="generated generated-title" />
              <div className="generated generated-line" />
              <div className="generated generated-line" />
              <div className="generated generated-line short" />
            </div>
          ) : (
            <>
              {/* CONFIDENCE SCORE */}
              {confidence !== null && (
                <div className="confidence-badge">
                  Confidence score:{' '}
                  <strong>{confidence}</strong>
                </div>
              )}

              {/* MAIN RESPONSE */}
              <div
                className="app-response-content fade-in"
                dangerouslySetInnerHTML={{ __html: response }}
              />

              {/* SOURCES */}
              {sources.length > 0 && (
                <div className="sources-section">
                  <h3>Sources</h3>
                  <ul>
                    {sources.map((s, i) => (
                      <li key={i}>
                        <a
                          href={s.url}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          {s.domain}
                        </a>{' '}
                        <span className="source-score">
                          (credibility: {s.score})
                        </span>
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
