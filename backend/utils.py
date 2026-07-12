import os
import uuid
import yt_dlp

COOKIES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cookies.txt')

def _setup_cookies():
    """Write YouTube cookies from environment variable to a file (runs once at import)."""
    cookies_data = os.environ.get('YOUTUBE_COOKIES', '')
    if cookies_data:
        with open(COOKIES_FILE, 'w') as f:
            f.write(cookies_data)

_setup_cookies()

def _get_base_opts():
    """Return yt-dlp options with cookies if available."""
    opts = {
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'android']
            }
        }
    }
    if os.path.exists(COOKIES_FILE) and os.path.getsize(COOKIES_FILE) > 0:
        opts['cookiefile'] = COOKIES_FILE
    return opts

def fetch_metadata(url):
    """
    Fetches video metadata (title, thumbnail, duration) without downloading the video.
    """
    ydl_opts = _get_base_opts()
    ydl_opts['skip_download'] = True
    ydl_opts['format'] = 'bestaudio/best'
    
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
        return {
            'success': False,
            'error': str(e)
        }

def process_audio(url, start_time, end_time, output_dir):
    """
    Downloads the best audio, trims it using ffmpeg, and converts to MP3.
    Returns the path to the final .mp3 file.
    """
    # Create a unique filename to prevent collisions
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
        # Pass trim arguments to ffmpeg during the post-processing phase
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
            return {
                'success': True,
                'filepath': final_path,
                'filename': f"[Trimmed] {file_id}.mp3"
            }
        else:
            return {'success': False, 'error': 'File not found after processing.'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}
