import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setResponse('');
    try {
      const backendURL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';
      const result = await axios.post(`${backendURL}/query`, { query });
      setResponse(result.data.response || '');
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

        <form className="app-form" onSubmit={handleSubmit} aria-label="Query form">
          <label htmlFor="query-input" className="visually-hidden">Enter a research topic</label>
          <input
            id="query-input"
            className="app-input"
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a finance research question..."
            disabled={loading}
            aria-disabled={loading}
            aria-label="Research query"
          />
          <button
            className="app-button"
            type="submit"
            disabled={loading || !query.trim()}
            aria-busy={loading ? 'true' : 'false'}
          >
            {loading ? 'Researching…' : 'Ask'}
          </button>
        </form>

        <div className="app-response-container" role="status" aria-live="polite" aria-relevant="additions text">
          <h2 className="app-response-title">Response</h2>

          {loading ? (
            <div className="generated-stack">
              <div className="generated generated-title" />
              <div className="generated generated-line" />
              <div className="generated generated-line" />
              <div className="generated generated-line short" />
            </div>
          ) : (
            <div
              className="app-response-content fade-in"
              dangerouslySetInnerHTML={{ __html: response }}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
