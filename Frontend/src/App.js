import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query) return;

    setLoading(true);
    try {
      const result = await axios.post('http://localhost:5000/query', {
        query: query,
      });
      setResponse(result.data.response);
    } catch (error) {
      console.error('Error fetching response:', error);
      setResponse(`Error: ${error.response?.data?.error || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-root">
      <div className="app-card">
        <h1 className="app-title">Financial AI Agent</h1>
        <form className="app-form" onSubmit={handleSubmit}>
          <input
            className="app-input"
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask your financial question..."
            disabled={loading}
          />
          <button
            className="app-button"
            type="submit"
            disabled={loading}
          >
            {loading ? 'Processing...' : 'Submit'}
          </button>
        </form>
        {response && (
          <div className="app-response-container">
            <h2 className="app-response-title">Response:</h2>
            <div
              className="app-response-content"
              dangerouslySetInnerHTML={{ __html: response }}
            />
          </div>
        )}
      </div>
      <div className="app-footer">
        <span>Powered by your Financial AI Agent &copy; {new Date().getFullYear()}</span>
      </div>
    </div>
  );
}

export default App;
