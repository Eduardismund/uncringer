import React, { useState } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="App">
      <h1>🎤 Uncringer</h1>
      <p>Upload audio to analyze cringe levels</p>
      
      <div className="upload-box">
        <input 
          type="file" 
          accept=".mp3,.wav,.m4a" 
          onChange={handleFileChange}
        />
        <button 
          onClick={handleUpload} 
          disabled={!file || uploading}
        >
          {uploading ? 'Uploading...' : 'Upload & Analyze'}
        </button>
      </div>

      {result && (
        <div className="result">
          <h3>Upload Successful!</h3>
          <p>File ID: {result.file_id}</p>
          <p>Storage URL: {result.gcs_url}</p>
        </div>
      )}
    </div>
  );
}

export default App;