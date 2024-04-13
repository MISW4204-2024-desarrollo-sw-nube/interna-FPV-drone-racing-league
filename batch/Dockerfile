
# Use the official Python image as the base image
FROM python:latest

# Set the working directory in the container
WORKDIR /app

# Copy the Dockerfile file to the working directory
COPY ./uploader/async_video_processor.py .
COPY ./uploader/requirements.txt .
COPY ./uploader/base.py .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run Celery with the "batch_video" queue
ENTRYPOINT ["celery", "-A", "async_video_processor.celery", "worker", "-Q", "batch_videos", "-E", "-l", "info"]
