import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [apiStatus, setApiStatus] = useState('checking');

  // Auto-detect API URL for production/development
  const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api'
    : '/api';

  // Check API health on component mount
  useEffect(() => {
    checkApiHealth();
  }, []);

  const checkApiHealth = async () => {
    try {
      const response = await fetch(`${API_URL}/health`);
      if (response.ok) {
        setApiStatus('healthy');
      } else {
        setApiStatus('unhealthy');
      }
    } catch (error) {
      setApiStatus('unhealthy');
      console.error('API health check failed:', error);
    }
  };

  const analyzeNews = async () => {
    if (!text.trim()) {
      alert('Please enter some text to analyze');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text }),
      });

      const data = await response.json();

      if (data.success) {
        setResult(data.result);
        // Add to history (keep last 10)
        setHistory(prev => [{
          id: Date.now(),
          text: text.length > 100 ? text.substring(0, 100) + '...' : text,
          ...data.result,
          timestamp: new Date().toLocaleTimeString()
        }, ...prev.slice(0, 9)]);
      } else {
        alert('Analysis failed: ' + (data.error || 'Unknown error'));
      }
    } catch (error) {
      alert('Failed to connect to API: ' + error.message);
      setApiStatus('unhealthy');
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = () => {
    setHistory([]);
  };

  const getConfidenceColor = (confidence) => {
    if (confidence > 0.8) return '#e74c3c';
    if (confidence > 0.6) return '#f39c12';
    return '#27ae60';
  };

  const getApiStatusColor = () => {
    switch (apiStatus) {
      case 'healthy': return '#27ae60';
      case 'unhealthy': return '#e74c3c';
      default: return '#f39c12';
    }
  };

  const getApiStatusText = () => {
    switch (apiStatus) {
      case 'healthy': return 'API Connected';
      case 'unhealthy': return 'API Disconnected';
      default: return 'Checking API...';
    }
  };

  return (
    <div className="App">
      <div className="container">
        <header className="app-header">
          <div className="header-content">
            <h1>🚨 Fake News Detector</h1>
            <p>AI-powered news authenticity analysis</p>
          </div>
          <div className="api-status" style={{ color: getApiStatusColor() }}>
            ● {getApiStatusText()}
          </div>
        </header>

        <div className="main-content">
          <div className="input-section">
            <h2>Analyze News Article</h2>
            <p className="section-description">
              Paste a news headline or article content below to check its authenticity
            </p>
            
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Enter news title or content here...&#10;Example: 'Scientists discover revolutionary new energy source that will change the world'"
              rows="6"
              disabled={loading}
              className="news-input"
            />
            
            <div className="input-actions">
              <button 
                onClick={analyzeNews} 
                disabled={loading}
                className="analyze-btn"
              >
                {loading ? (
                  <>
                    <div className="loading-spinner"></div>
                    Analyzing...
                  </>
                ) : (
                  '🔍 Analyze News'
                )}
              </button>
              
              <button 
                onClick={() => setText('')}
                disabled={loading}
                className="clear-btn"
              >
                Clear
              </button>
            </div>
          </div>

          {result && (
            <div className="result-section">
              <h2>Analysis Result</h2>
              <div className={`result-card ${result.class.toLowerCase()}`}>
                <div className="result-header">
                  <h3>
                    {result.class === 'FAKE' ? '🚫 FAKE NEWS' : '✅ REAL NEWS'}
                  </h3>
                  <span 
                    className="confidence-badge"
                    style={{ backgroundColor: getConfidenceColor(result.confidence) }}
                  >
                    Confidence: {(result.confidence * 100).toFixed(1)}%
                  </span>
                </div>
                
                <div className="probability-section">
                  <h4>Probability Analysis:</h4>
                  <div className="probability-meter">
                    <div className="probability-bar">
                      <div 
                        className="real-probability" 
                        style={{ width: `${result.probabilities.real * 100}%` }}
                      >
                        <span className="probability-text">
                          REAL: {(result.probabilities.real * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div 
                        className="fake-probability" 
                        style={{ width: `${result.probabilities.fake * 100}%` }}
                      >
                        <span className="probability-text">
                          FAKE: {(result.probabilities.fake * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {result.note && (
                  <div className="result-note">
                    <p><strong>Note:</strong> {result.note}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {history.length > 0 && (
            <div className="history-section">
              <div className="history-header">
                <h2>Recent Analyses</h2>
                <button onClick={clearHistory} className="clear-history-btn">
                  Clear History
                </button>
              </div>
              <div className="history-list">
                {history.map((item) => (
                  <div key={item.id} className="history-item">
                    <div className="history-content">
                      <span className="history-text">{item.text}</span>
                      <span className="history-time">{item.timestamp}</span>
                    </div>
                    <div className="history-result">
                      <span className={`history-label ${item.class.toLowerCase()}`}>
                        {item.class}
                      </span>
                      <span className="history-confidence">
                        {(item.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <footer className="app-footer">
          <p>
            <strong>Fake News Detector</strong> - Powered by Machine Learning & Natural Language Processing
          </p>
          <p className="footer-note">
            Note: This tool provides AI-based analysis and should be used as a supplementary verification method.
          </p>
        </footer>
      </div>
    </div>
  );
}

export default App;