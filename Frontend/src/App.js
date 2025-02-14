import React, { useState } from 'react';
import axios from 'axios';

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
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>Financial AI Agent</h1>
      <form onSubmit={handleSubmit} style={{ marginBottom: '20px' }}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your financial query"
          style={{ width: '300px', padding: '10px', marginRight: '10px' }}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Submit'}
        </button>
      </form>

      {response && (
        <div className="container">
          <h2>Response:</h2>
          {/* Render the HTML content using dangerouslySetInnerHTML */}
          <div dangerouslySetInnerHTML={{ __html: response }} />
        </div>
      )}
    </div>
  );
}

export default App;