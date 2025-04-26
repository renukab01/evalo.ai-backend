import os
import librosa
import numpy as np
import soundfile as sf
import speech_recognition as sr
import google.generativeai as genai
from pydub import AudioSegment
from dotenv import load_dotenv
import json
import tempfile
import requests
from urllib.parse import urlparse
import re

# Load environment variables
load_dotenv()

# Setup Environment
GENAI_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GENAI_API_KEY:
    raise EnvironmentError("Set GOOGLE_API_KEY in .env file or as environment variable.")

# Configure Gemini AI
genai.configure(api_key=GENAI_API_KEY)

def download_audio(audio_url):
    """
    Download audio from URL to a temporary file
    """
    try:
        # Get the file extension from the URL
        parsed_url = urlparse(audio_url)
        path = parsed_url.path
        extension = os.path.splitext(path)[1]
        if not extension:
            extension = '.mp3'  # Default extension
            
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix=extension, delete=False)
        
        # Download the file
        response = requests.get(audio_url, stream=True)
        if response.status_code == 200:
            with open(temp_file.name, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return temp_file.name
        else:
            print(f"Failed to download audio: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None

def convert_audio_to_wav(audio_file_path):
    """
    Convert any audio format to WAV format for speech recognition compatibility
    """
    try:
        # Get file extension
        file_name, file_extension = os.path.splitext(audio_file_path)
        output_path = f"{file_name}_converted.wav"
        
        # Convert if not already wav
        if file_extension.lower() != '.wav':
            audio = AudioSegment.from_file(audio_file_path)
            audio.export(output_path, format="wav")
            print(f"Converted {audio_file_path} to {output_path}")
            return output_path
        else:
            return audio_file_path
    except Exception as e:
        print(f"Error converting audio file: {e}")
        return None

def transcribe_audio(audio_file_path):
    """
    Transcribe the audio file to text
    """
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None

def extract_audio_features(audio_file_path):
    """
    Extract audio features that might indicate clarity and confidence:
    - Speech rate
    - Pauses
    - Volume variations
    - Pitch variations
    """
    try:
        # Load audio file
        y, sr = librosa.load(audio_file_path, sr=None)
        
        # Calculate features
        
        # 1. Speech energy/volume
        rms = librosa.feature.rms(y=y)[0]
        mean_volume = np.mean(rms)
        std_volume = np.std(rms)
        
        # 2. Speech rate estimation (based on zero crossings)
        zero_crossings = librosa.feature.zero_crossing_rate(y)[0]
        mean_zero_crossings = np.mean(zero_crossings)
        
        # 3. Pauses detection
        # Detect segments with low energy (potential pauses)
        silence_threshold = 0.01
        is_silence = rms < silence_threshold
        silence_segments = np.sum(is_silence)
        silence_ratio = silence_segments / len(rms)
        
        # 4. Pitch variations
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_mean = np.mean(pitches[pitches > 0]) if np.any(pitches > 0) else 0
        pitch_std = np.std(pitches[pitches > 0]) if np.any(pitches > 0) else 0
        
        return {
            "mean_volume": float(mean_volume),
            "volume_variation": float(std_volume),
            "speech_rate": float(mean_zero_crossings),
            "silence_ratio": float(silence_ratio),
            "pitch_mean": float(pitch_mean) if not np.isnan(pitch_mean) else 0,
            "pitch_variation": float(pitch_std) if not np.isnan(pitch_std) else 0
        }
    except Exception as e:
        print(f"Error extracting audio features: {e}")
        return None

def analyze_voice(audio_url):
    """
    Analyze voice recording for clarity and confidence from a URL
    """
    print(f"\n🔊 Analyzing voice recording from URL: {audio_url}...")
    
    # Download the audio file
    audio_file_path = download_audio(audio_url)
    if not audio_file_path:
        return None
    
    # Convert audio to WAV if needed
    wav_file_path = convert_audio_to_wav(audio_file_path)
    if not wav_file_path:
        return None
    
    # Extract audio features
    audio_features = extract_audio_features(wav_file_path)
    if not audio_features:
        return None
    
    # Transcribe audio
    transcript = transcribe_audio(wav_file_path)
    if not transcript:
        return None
    
    # Analyze with Gemini
    prompt = f"""You are an expert at analyzing speech patterns for clarity and confidence.
    
Based on the following transcript and audio features, analyze the speaker's clarity and confidence.

Transcript: "{transcript}"

Audio Features:
- Mean Volume: {audio_features['mean_volume']}
- Volume Variation: {audio_features['volume_variation']}
- Speech Rate: {audio_features['speech_rate']}
- Silence Ratio: {audio_features['silence_ratio']}
- Pitch Mean: {audio_features['pitch_mean']}
- Pitch Variation: {audio_features['pitch_variation']}

Provide a detailed analysis in the following JSON format WITHOUT ANY MARKDOWN FORMATTING OR EXPLANATION BEFORE OR AFTER THE JSON:
{{
  "clarity": {{
    "score": 8
  }},
  "confidence": {{
    "score": 7
  }},
  "speech_patterns": "Description of speech patterns"
}}

Score both clarity and confidence on a scale of 1-10, where 1 is very poor and 10 is excellent.
Do not focus on the grammar of the transcript, only the clarity and confidence of the speaker.
THE RESPONSE MUST BE VALID JSON WITH NO MARKDOWN FORMATTING OR TEXT OUTSIDE THE JSON OBJECT.
"""
    
    try:
        client = genai.GenerativeModel("gemini-1.5-flash")
        response = client.generate_content(prompt)
        response_text = response.text
        
        # Remove any markdown code block formatting if present
        if '```json' in response_text:
            response_text = response_text.replace('```json', '').replace('```', '').strip()
        
        # Clean the response to ensure it's valid JSON
        response_text = response_text.strip()
        # Remove any extra text before or after the JSON object
        response_text = re.sub(r'^[^{]*', '', response_text)
        response_text = re.sub(r'[^}]*$', '', response_text)
        
        # Parse the response as JSON
        result_json = json.loads(response_text)
        
        # Clean up any temporary files
        try:
            os.remove(audio_file_path)
            if wav_file_path != audio_file_path:
                os.remove(wav_file_path)
        except:
            pass
            
        return {
            "clarity": str(result_json["clarity"]["score"]),
            "confidence": str(result_json["confidence"]["score"]),
            "speech_patterns": str(result_json["speech_patterns"]),
        }
    except Exception as e:
        print(f"❌ Error analyzing voice or parsing response: {e}")
        print(f"Raw response: {response_text if 'response_text' in locals() else 'No response'}")
        
        # Clean up any temporary files
        try:
            os.remove(audio_file_path)
            if wav_file_path != audio_file_path:
                os.remove(wav_file_path)
        except:
            pass
            
        return None 