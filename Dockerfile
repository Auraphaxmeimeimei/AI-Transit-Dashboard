FROM python:3.10-slim

# Install system dependencies (needed for OpenCV / video)
RUN apt-get update && apt-get install -y ffmpeg libglib2.0-0 libsm6 libxext6 libgl1

# Create app directory
WORKDIR /app

# Copy requirements first (cache optimization)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy main app file
COPY app.py /app/app.py

# ⬅️ CRITICAL: copy your assets folder so Dash can find images
COPY assets /app/assets

# Expose port (HuggingFace Space runs on 7860)
EXPOSE 7860

# Start Dash app
CMD ["python", "app.py"]
