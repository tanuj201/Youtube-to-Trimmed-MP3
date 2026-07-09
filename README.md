# YouTube to Trimmed MP3 Converter

A premium, modern web application that allows users to fetch a YouTube video, preview it, select a specific time segment using an interactive dual-range slider, and download only the trimmed audio segment as a high-quality MP3 file.

Designed with a sleek, glowing dark-mode UI, this tool runs locally with a lightweight Python Flask backend powered by `yt-dlp` and `ffmpeg` for high-performance and precise audio trimming.

---

## Key Features

- **Interactive URL Fetching**: Fetches video title, duration, and thumbnail preview in real time.
- **Custom Dual-Slider Trimming**: A sleek, custom-designed dual-range slider to visually select the precise start and end times.
- **Microsecond-Precise Cuts**: Backend uses `ffmpeg` to trim the audio stream precisely to the requested segment before conversion.
- **High-Quality MP3 Output**: Automatically converts and outputs the selected segment as a 192kbps MP3.
- **Premium User Interface**: Dark-mode interface built with Tailwind CSS, custom modern typography, and smooth micro-animations.

---

## Tech Stack

- **Frontend**: Clean HTML5, Vanilla JavaScript, Tailwind CSS (Visual styling)
- **Backend**: Python (Flask)
- **Core Dependencies**:
  - `yt-dlp` (For media stream fetching)
  - `ffmpeg` (For precise audio trimming and extraction)

---

## Installation & Setup

### Prerequisites

1. **Python 3.12+**: Make sure Python is installed and added to your system's PATH.
2. **FFmpeg**: Ensure FFmpeg is installed and added to your system's PATH.

### Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/youtube-to-mp3-trimmer.git
   cd youtube-to-mp3-trimmer
   ```

2. **Set up the backend**:
   Navigate to the `backend` folder, install the required packages, and run the server:
   ```bash
   cd backend
   pip install -r requirements.txt
   python app.py
   ```
   The Flask server will start running on `http://127.0.0.1:5000`.

3. **Run the frontend**:
   Open the `index.html` file inside the `frontend` folder directly in your browser, or run a lightweight local server:
   ```bash
   cd ../frontend
   python -m http.server 8000
   ```
   Then open `http://localhost:8000` in your web browser.

---

## License

This project is licensed under the MIT License.
