import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setResult(null);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setAnalyzing(false);
    setError(null);
    setResult(null);
    
    try {
      const formData = new FormData();
      formData.append('file', file);

      setAnalyzing(true);
      
      const response = await axios.post(`${API_BASE_URL}/api/analyze`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setResult(response.data);
      
    } catch (error) {
      console.error('Process failed:', error);
      setError(error.response?.data?.detail || 'Failed to analyze audio. Please try again.');
    } finally {
      setUploading(false);
      setAnalyzing(false);
    }
  };

  const getCringeEmoji = (score) => {
    if (score < 0.3) return '😎';
    if (score < 0.5) return '😊';
    if (score < 0.7) return '😬';
    return '🫣';
  };

  const getCringeLevel = (score) => {
    if (score < 0.3) return 'Smooth';
    if (score < 0.5) return 'Normal';
    if (score < 0.7) return 'Awkward';
    return 'Very Cringe';
  };

  const getProgressBarColor = (score) => {
    if (score < 0.3) return '#4CAF50';
    if (score < 0.5) return '#FFC107';
    if (score < 0.7) return '#FF9800';
    return '#F44336';
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>🎤 Uncringer</h1>
        <p className="subtitle">AI-Powered Audio Cringe Detection</p>
      </header>
      
      <main className="main-content">
        <div className="upload-section">
          <div className="upload-box">
            <input 
              type="file" 
              accept=".mp3,.wav,.m4a,.webm,.ogg" 
              onChange={handleFileChange}
              id="file-input"
              disabled={uploading || analyzing}
            />
            <label htmlFor="file-input" className="file-label">
              <span className="file-icon">📁</span>
              {file ? file.name : 'Choose audio file'}
            </label>
            <button 
              onClick={handleUpload} 
              disabled={!file || uploading || analyzing}
              className={`upload-btn ${uploading || analyzing ? 'loading' : ''}`}
            >
              {uploading ? 'Uploading...' : analyzing ? 'Analyzing...' : 'Upload & Analyze'}
            </button>
          </div>
        </div>

        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}

        {result && (
          <div className="results-section">
            <div className="result-card">
              <div className="cringe-meter">
                <div className="emoji-display">
                  {getCringeEmoji(result.cringe_score)}
                </div>
                <h2 className={`cringe-level ${result.is_cringe ? 'is-cringe' : 'not-cringe'}`}>
                  {getCringeLevel(result.cringe_score)}
                </h2>
                <div className="confidence-score">
                  Model Confidence: {Math.round(result.confidence * 100)}%
                </div>
              </div>

              <div className="score-visualization">
                <div className="score-bar-container">
                  <div 
                    className="score-bar-fill" 
                    style={{
                      width: `${result.cringe_score * 100}%`,
                      backgroundColor: getProgressBarColor(result.cringe_score)
                    }}
                  />
                  <div className="score-markers">
                    <span className="marker" style={{left: '0%'}}>0</span>
                    <span className="marker" style={{left: '30%'}}>30</span>
                    <span className="marker" style={{left: '50%'}}>50</span>
                    <span className="marker" style={{left: '70%'}}>70</span>
                    <span className="marker" style={{left: '100%'}}>100</span>
                  </div>
                </div>
                <p className="score-label">
                  Cringe Score: <strong>{Math.round(result.cringe_score * 100)}</strong>/100
                </p>
              </div>

              {result.features && (
                <details className="features-details">
                  <summary>📊 Audio Analysis Details</summary>
                  <div className="features-grid">
                    <div className="feature-item">
                      <span className="feature-label">Duration:</span>
                      <span className="feature-value">{result.features.duration.toFixed(1)}s</span>
                    </div>
                    <div className="feature-item">
                      <span className="feature-label">Awkward Pauses:</span>
                      <span className="feature-value">{result.features.pause_count}</span>
                    </div>
                    <div className="feature-item">
                      <span className="feature-label">Longest Pause:</span>
                      <span className="feature-value">{result.features.longest_pause}s</span>
                    </div>
                    <div className="feature-item">
                      <span className="feature-label">Voice Cracks:</span>
                      <span className="feature-value">{result.features.voice_cracks}</span>
                    </div>
                    <div className="feature-item">
                      <span className="feature-label">Energy Drops:</span>
                      <span className="feature-value">{result.features.energy_drops}</span>
                    </div>
                    <div className="feature-item">
                      <span className="feature-label">Speaking Rate:</span>
                      <span className="feature-value">{result.features.speaking_rate} wpm</span>
                    </div>
                    <div className="feature-item">
                      <span className="feature-label">Pitch Mean:</span>
                      <span className="feature-value">{result.features.pitch_mean.toFixed(1)} Hz</span>
                    </div>
                    <div className="feature-item">
                      <span className="feature-label">Pitch Variance:</span>
                      <span className="feature-value">{result.features.pitch_variance.toFixed(1)}</span>
                    </div>
                  </div>
                </details>
              )}
            </div>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>Powered by BigQuery ML & Google Cloud</p>
      </footer>
    </div>
  );
}

export default App;