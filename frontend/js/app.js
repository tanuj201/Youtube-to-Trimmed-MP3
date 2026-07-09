document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const fetchForm = document.getElementById('fetch-form');
    const urlInput = document.getElementById('youtube-url');
    const fetchBtn = document.getElementById('fetch-btn');
    const fetchLoader = document.getElementById('fetch-loader');
    const fetchError = document.getElementById('fetch-error');
    const previewSection = document.getElementById('preview-section');
    
    // Preview Elements
    const videoThumbnail = document.getElementById('video-thumbnail');
    const videoTitle = document.getElementById('video-title');
    const videoDurationText = document.getElementById('video-duration-text');
    
    // Slider Elements
    const sliderMin = document.getElementById('slider-min');
    const sliderMax = document.getElementById('slider-max');
    const sliderProgress = document.getElementById('slider-progress');
    const timeStartInput = document.getElementById('time-start');
    const timeEndInput = document.getElementById('time-end');
    
    // Action Elements
    const convertBtn = document.getElementById('convert-btn');
    const processLoader = document.getElementById('process-loader');

    // State
    let videoDurationSeconds = 0;
    
    // --- Utility Functions ---
    const formatTime = (totalSeconds) => {
        const h = Math.floor(totalSeconds / 3600);
        const m = Math.floor((totalSeconds % 3600) / 60);
        const s = Math.floor(totalSeconds % 60);
        return [h, m, s]
            .map(val => val < 10 ? '0' + val : val)
            .join(':');
    };

    const parseTime = (timeStr) => {
        const parts = timeStr.split(':').map(Number);
        if (parts.length === 3) {
            return parts[0] * 3600 + parts[1] * 60 + parts[2];
        }
        return 0; // Fallback
    };

    // --- API Fetch Logic ---
    fetchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const url = urlInput.value.trim();
        if (!url.includes('youtube.com/') && !url.includes('youtu.be/')) {
            fetchError.classList.remove('hidden');
            document.getElementById('fetch-error-msg').textContent = 'Invalid YouTube URL.';
            return;
        }
        
        // Reset states
        fetchError.classList.add('hidden');
        previewSection.classList.add('hidden');
        previewSection.classList.remove('opacity-100');
        fetchLoader.classList.remove('hidden');
        fetchLoader.classList.add('flex');
        fetchBtn.disabled = true;
        fetchBtn.classList.add('opacity-50', 'cursor-not-allowed');
        processLoader.classList.add('hidden');
        convertBtn.classList.remove('hidden');

        try {
            const response = await fetch('http://127.0.0.1:5000/api/fetch-info', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: url })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to fetch video details');
            }

            // Update UI with real data
            videoTitle.textContent = data.title;
            videoThumbnail.src = data.thumbnail || 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?q=80&w=2070&auto=format&fit=crop';
            videoDurationSeconds = data.duration;
            videoDurationText.textContent = formatTime(videoDurationSeconds);
            
            // Initialize Sliders
            sliderMin.max = videoDurationSeconds;
            sliderMax.max = videoDurationSeconds;
            sliderMin.value = 0;
            sliderMax.value = videoDurationSeconds;
            
            updateSliderUI();

            // Hide loader, show preview
            fetchLoader.classList.remove('flex');
            fetchLoader.classList.add('hidden');
            fetchBtn.disabled = false;
            fetchBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            
            previewSection.classList.remove('hidden');
            // Small timeout for fade-in transition
            setTimeout(() => {
                previewSection.classList.add('opacity-100');
            }, 50);

        } catch (error) {
            fetchLoader.classList.remove('flex');
            fetchLoader.classList.add('hidden');
            fetchBtn.disabled = false;
            fetchBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            fetchError.classList.remove('hidden');
            document.getElementById('fetch-error-msg').textContent = error.message;
        }
    });

    // --- Dual Slider Logic ---
    const updateSliderUI = () => {
        let minVal = parseInt(sliderMin.value);
        let maxVal = parseInt(sliderMax.value);

        // Ensure handles don't cross each other
        if (minVal >= maxVal) {
            sliderMin.value = maxVal - 1;
            minVal = maxVal - 1;
        }

        // Update Progress Bar
        const percentMin = (minVal / videoDurationSeconds) * 100;
        const percentMax = (maxVal / videoDurationSeconds) * 100;
        
        sliderProgress.style.left = percentMin + "%";
        sliderProgress.style.width = (percentMax - percentMin) + "%";

        // Update Text Inputs
        timeStartInput.value = formatTime(minVal);
        timeEndInput.value = formatTime(maxVal);
    };

    const updateSliderFromInputs = () => {
        let minVal = parseTime(timeStartInput.value);
        let maxVal = parseTime(timeEndInput.value);

        // Validation bounds
        if (minVal < 0) minVal = 0;
        if (maxVal > videoDurationSeconds) maxVal = videoDurationSeconds;
        if (minVal >= maxVal) minVal = maxVal - 1;

        sliderMin.value = minVal;
        sliderMax.value = maxVal;
        
        // Ensure inputs are formatted cleanly if user typed sloppy
        timeStartInput.value = formatTime(minVal);
        timeEndInput.value = formatTime(maxVal);

        updateSliderUI();
    };

    // Event Listeners for Sliders
    sliderMin.addEventListener('input', updateSliderUI);
    sliderMax.addEventListener('input', updateSliderUI);

    // Event Listeners for Text Inputs (Update on Blur or Enter)
    timeStartInput.addEventListener('change', updateSliderFromInputs);
    timeEndInput.addEventListener('change', updateSliderFromInputs);
    
    // --- Convert Action (Real API) ---
    convertBtn.addEventListener('click', async () => {
        convertBtn.classList.add('hidden');
        processLoader.classList.remove('hidden');

        try {
            const response = await fetch('http://127.0.0.1:5000/api/convert', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    url: urlInput.value.trim(),
                    start_time: sliderMin.value,
                    end_time: sliderMax.value,
                    title: videoTitle.textContent
                })
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || 'Conversion failed');
            }

            // Get filename from Content-Disposition header if possible
            let filename = `[Trimmed] ${videoTitle.textContent}.mp3`;
            const disposition = response.headers.get('Content-Disposition');
            if (disposition && disposition.includes('attachment')) {
                const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                const matches = filenameRegex.exec(disposition);
                if (matches != null && matches[1]) { 
                    filename = matches[1].replace(/['"]/g, '');
                }
            }

            // Convert response to blob and download
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = downloadUrl;
            a.download = decodeURIComponent(filename);
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(downloadUrl);
            a.remove();
            
        } catch (error) {
            alert('Error during conversion: ' + error.message);
        } finally {
            processLoader.classList.add('hidden');
            convertBtn.classList.remove('hidden');
        }
    });
});
