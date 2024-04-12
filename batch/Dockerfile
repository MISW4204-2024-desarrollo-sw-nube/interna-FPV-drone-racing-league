
# Use the official Python image as the base image
FROM python:latest

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the working directory
COPY . .

# Run Celery with the "batch_video" queue
ENTRYPOINT ["celery", "-A", "videos.celery", "worker", "-Q", "batch_videos", "-E", "-l", "info"]
