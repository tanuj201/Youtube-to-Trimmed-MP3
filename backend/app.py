import os
from flask import Flask, request, jsonify, send_file, after_this_request
from flask_cors import CORS
from utils import fetch_metadata, process_audio
import urllib.parse
import re

app = Flask(__name__)
CORS(app) # Allow frontend to communicate with backend

# Ensure temp directory exists
TEMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__name__)), 'temp')
os.makedirs(TEMP_DIR, exist_ok=True)

@app.route('/api/fetch-info', methods=['POST'])
def fetch_info():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
        
    result = fetch_metadata(url)
    if result['success']:
        return jsonify({
            'title': result['title'],
            'thumbnail': result['thumbnail'],
            'duration': result['duration']
        }), 200
    else:
        return jsonify({'error': result.get('error', 'Failed to fetch metadata')}), 500

def sanitize_filename(filename):
    # Remove invalid characters for Windows/Linux filenames
    return re.sub(r'[\\/*?:"<>|]', "", filename)

@app.route('/api/convert', methods=['POST'])
def convert():
    data = request.json
    url = data.get('url')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    title = data.get('title', 'Trimmed_Audio')
    
    if not url or start_time is None or end_time is None:
        return jsonify({'error': 'URL, start_time, and end_time are required'}), 400
        
    try:
        start_time = float(start_time)
        end_time = float(end_time)
    except ValueError:
        return jsonify({'error': 'Invalid timestamps'}), 400

    if start_time >= end_time:
        return jsonify({'error': 'start_time must be less than end_time'}), 400

    result = process_audio(url, start_time, end_time, TEMP_DIR)
    
    if result['success']:
        filepath = result['filepath']
        
        # Cleanup file after sending
        @after_this_request
        def remove_file(response):
            try:
                os.remove(filepath)
            except Exception as error:
                app.logger.error("Error removing downloaded file: %s", error)
            return response

        # Format a nice filename for the user
        safe_title = sanitize_filename(title)
        download_name = f"[Trimmed] {safe_title}.mp3"
        
        # Handle ASCII encoding issues for the attachment filename
        encoded_filename = urllib.parse.quote(download_name)
        
        # In Flask < 2.2 as_attachment=True, attachment_filename=download_name
        # In Flask >= 2.2 download_name is used
        return send_file(
            filepath,
            as_attachment=True,
            download_name=download_name,
            mimetype='audio/mpeg'
        )
    else:
        return jsonify({'error': result.get('error', 'Processing failed')}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
