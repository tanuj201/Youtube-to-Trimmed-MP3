import os
import logging
from flask import Flask, request, jsonify, send_file, after_this_request
from flask_cors import CORS
from utils import fetch_metadata, process_audio
import urllib.parse
import re

logging.basicConfig(level=logging.INFO)

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

@app.route('/api/debug')
def debug():
    from utils import COOKIES_FILE
    info = {
        'env_exists': bool(os.environ.get('YOUTUBE_COOKIES')),
        'env_length': len(os.environ.get('YOUTUBE_COOKIES', '')),
        'env_first_50': os.environ.get('YOUTUBE_COOKIES', '')[:50],
        'file_exists': os.path.exists(COOKIES_FILE),
        'file_size': os.path.getsize(COOKIES_FILE) if os.path.exists(COOKIES_FILE) else 0,
    }
    if info['file_exists']:
        with open(COOKIES_FILE, 'r') as f:
            lines = f.readlines()
            info['file_lines'] = len(lines)
            info['line_0'] = lines[0].rstrip()[:100] if lines else 'EMPTY'
            info['line_1'] = lines[1].rstrip()[:100] if len(lines) > 1 else 'EMPTY'
        with open(COOKIES_FILE, 'rb') as f:
            raw = f.read(200)
            info['file_hex_start'] = raw[:50].hex()
    return jsonify(info)

@app.route('/')
def index():
    return send_file(os.path.join(app.static_folder, 'index.html'))

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
        @after_this_request
        def remove_file(response):
            try:
                os.remove(filepath)
            except Exception as error:
                app.logger.error("Error removing downloaded file: %s", error)
            return response
        safe_title = sanitize_filename(title)
        download_name = f"[Trimmed] {safe_title}.mp3"
        encoded_filename = urllib.parse.quote(download_name)
        return send_file(
            filepath,
            as_attachment=True,
            download_name=download_name,
            mimetype='audio/mpeg'
        )
    else:
        return jsonify({'error': result.get('error', 'Processing failed')}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
