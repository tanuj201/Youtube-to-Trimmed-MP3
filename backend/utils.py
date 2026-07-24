import os
import uuid
import yt_dlp
import base64
import string

COOKIES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cookies.txt')

def _setup_cookies():
    cookies_data = os.environ.get('YOUTUBE_COOKIES', '')
    if not cookies_data:
        print("WARNING: YOUTUBE_COOKIES env var is empty", flush=True)
        return

    cookies_data = cookies_data.strip()

    if cookies_data.startswith('#') or cookies_data.startswith('.'):
        content = cookies_data
        print(f"Raw cookie content ({len(content)} bytes)", flush=True)
    elif '|' in cookies_data and '\n' not in cookies_data:
        content = cookies_data.replace('|', '\n')
        print(f"Pipe-separated cookies ({len(content)} bytes)", flush=True)
    else:
        try:
            clean = ''.join(c for c in cookies_data if c in string.ascii_letters + string.digits + '+/=')
            content = base64.b64decode(clean).decode('utf-8')
            print(f"Base64 decoded ({len(content)} bytes)", flush=True)
        except Exception as e:
            print(f"Decode failed ({e}), using raw ({len(cookies_data)} bytes)", flush=True)
            content = cookies_data

    with open(COOKIES_FILE, 'w', newline='\n') as f:
        f.write(content)

    print(f"Cookie file written: {os.path.getsize(COOKIES_FILE)} bytes", flush=True)
    with open(COOKIES_FILE, 'r') as f:
        lines = f.readlines()
        print(f"Lines: {len(lines)}", flush=True)
        for i, line in enumerate(lines[:3]):
            print(f"  [{i}] {line.rstrip()[:120]}", flush=True)

_setup_cookies()

def _get_base_opts():
    opts = {
        'quiet': True,
        'no_warnings': True,
    }
    if os.path.exists(COOKIES_FILE) and os.path.getsize(COOKIES_FILE) > 0:
        opts['cookiefile'] = COOKIES_FILE
    return opts

def fetch_metadata(url):
    ydl_opts = _get_base_opts()
    ydl_opts['skip_download'] = True

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'success': True,
                'title': info.get('title', 'Unknown Title'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': info.get('duration', 0)
            }
    except Exception as e:
        print(f"fetch_metadata error: {e}", flush=True)
        return {'success': False, 'error': str(e)}

def process_audio(url, start_time, end_time, output_dir):
    file_id = str(uuid.uuid4())
    base_filepath = os.path.join(output_dir, file_id)

    ydl_opts = _get_base_opts()
    ydl_opts.update({
        'format': 'bestaudio/best',
        'outtmpl': base_filepath,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'postprocessor_args': [
            '-ss', str(start_time),
            '-to', str(end_time)
        ]
    })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        final_path = base_filepath + '.mp3'

        if os.path.exists(final_path):
            return {'success': True, 'filepath': final_path, 'filename': f"[Trimmed] {file_id}.mp3"}
        else:
            return {'success': False, 'error': 'File not found after processing.'}

    except Exception as e:
        print(f"process_audio error: {e}", flush=True)
        return {'success': False, 'error': str(e)}
