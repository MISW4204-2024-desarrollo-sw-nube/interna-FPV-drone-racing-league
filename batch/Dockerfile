
# Use the official Python image as the base image
FROM python:latest

# Set the working directory in the container
WORKDIR /app

# Copy the Dockerfile file to the working directory
COPY ./batch/celery.sh .
COPY ./uploader/async_video_processor.py .
COPY ./uploader/requirements.txt .
COPY ./uploader/base.py .
COPY ./uploader/celeryconfig.py .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN ["chmod", "+x", "celery.sh"]
# Run Celery with the "batch_video" queue
ENTRYPOINT ["/app/celery.sh"]
