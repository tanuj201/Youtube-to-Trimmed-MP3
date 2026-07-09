FROM python:3.12-slim

# Install system dependencies (ffmpeg)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency files first to cache layer
COPY backend/requirements.txt .

# Install Python requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source files
COPY . .

# Set working directory to backend folder for running the app
WORKDIR /app/backend

# Expose port
EXPOSE 5000

# Start Flask server
CMD ["python", "app.py"]
