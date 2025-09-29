import functions_framework
import librosa
import numpy as np
import tempfile
import os
import requests
import json
from flask import jsonify

@functions_framework.http
def extract_audio_features(request):
    """HTTP Cloud Function to extract audio features from URL"""
    
    # Handle CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    
    try:
        # Get audio URL from request
        request_json = request.get_json(silent=True)
        if not request_json or 'audio_url' not in request_json:
            return jsonify({'error': 'audio_url parameter required'}), 400, headers
        
        audio_url = request_json['audio_url']
        print(f"Processing audio URL: {audio_url}")
        
        # Download audio
        response = requests.get(audio_url, timeout=30)
        response.raise_for_status()
        
        # Save to temp file
        file_ext = '.mp3' if '.mp3' in audio_url else '.wav'
        with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp_file:
            tmp_file.write(response.content)
            tmp_path = tmp_file.name
        
        try:
            # Extract features using librosa
            features = extract_features(tmp_path)
            
            return jsonify({
                'success': True,
                'features': features
            }), 200, headers
            
        finally:
            # Clean up
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500, headers


def extract_features(audio_path):
    """Extract your exact audio features using librosa"""
    
    # Load audio
    y, sr = librosa.load(audio_path, sr=16000)
    
    # Extract all features (your exact logic)
    features = {
        'duration': float(len(y) / sr),
        'pause_count': count_pauses(y, sr),
        'longest_pause': get_longest_pause(y, sr),
        'pitch_mean': get_pitch_mean(y, sr),
        'pitch_variance': get_pitch_variance(y, sr),
        'voice_cracks': count_voice_cracks(y, sr),
        'energy_mean': float(np.mean(librosa.feature.rms(y=y))),
        'energy_drops': count_energy_drops(y),
        'speaking_rate': estimate_speaking_rate(y, sr),
    }
    
    return features


def count_pauses(y, sr):
    """Count awkward pauses (>0.5s silence)"""
    intervals = librosa.effects.split(y, top_db=20)
    pauses = 0
    for i in range(len(intervals) - 1):
        gap = (intervals[i + 1][0] - intervals[i][1]) / sr
        if gap > 0.5:
            pauses += 1
    return pauses


def get_longest_pause(y, sr):
    """Find longest silence"""
    intervals = librosa.effects.split(y, top_db=20)
    max_pause = 0
    for i in range(len(intervals) - 1):
        gap = (intervals[i + 1][0] - intervals[i][1]) / sr
        max_pause = max(max_pause, gap)
    return round(float(max_pause), 2)


def get_pitch_mean(y, sr):
    """Average pitch"""
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    pitch_values = []
    for t in range(pitches.shape[1]):
        index = magnitudes[:, t].argmax()
        pitch = pitches[index, t]
        if pitch > 0:
            pitch_values.append(pitch)
    return float(np.mean(pitch_values)) if pitch_values else 0


def get_pitch_variance(y, sr):
    """Pitch variance (nervousness indicator)"""
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    pitch_values = []
    for t in range(pitches.shape[1]):
        index = magnitudes[:, t].argmax()
        pitch = pitches[index, t]
        if pitch > 0:
            pitch_values.append(pitch)
    return float(np.var(pitch_values)) if pitch_values else 0


def count_voice_cracks(y, sr):
    """Count sudden pitch drops (voice cracks)"""
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    cracks = 0
    prev_pitch = 0
    for t in range(pitches.shape[1]):
        index = magnitudes[:, t].argmax()
        pitch = pitches[index, t]
        if pitch > 0 and prev_pitch > 0:
            if pitch < prev_pitch * 0.7:  # 30% drop = crack
                cracks += 1
        prev_pitch = pitch
    return cracks


def count_energy_drops(y):
    """Count sudden volume/confidence drops"""
    rms = librosa.feature.rms(y=y)[0]
    drops = 0
    for i in range(1, len(rms)):
        if rms[i] < rms[i-1] * 0.6:  # 40% drop
            drops += 1
    return drops


def estimate_speaking_rate(y, sr):
    """Rough estimate of words per minute"""
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return round(float(tempo * 1.5))  # Approximation