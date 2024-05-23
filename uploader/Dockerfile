# Use the official Python 3 Docker image as the base image
FROM python:3

# Create a new directory named 'backend' in the Docker image
RUN mkdir /backend

# Set the working directory in the Docker image to '/backend'
WORKDIR /backend

# Add the 'requirements.txt' file from the local system to the '/backend' directory in the Docker image
ADD requirements.txt /backend/

# Run the 'pip install' command to install the Python packages listed in the 'requirements.txt' file
RUN pip install -r requirements.txt

# Add all files from the local system to the '/backend' directory in the Docker image
ADD * /backend/

# Expose port 8080 in the Docker image
EXPOSE 8080

# Define environment variable to tell Flask to run on the container's IP address and port 8080.
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080
ENV POSTGRES_DB=postgres
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=1234
ENV POSTGRES_PORT=5432
ENV POSTGRES_HOST=10.84.64.3
ENV JWT_SECRET_KEY=1234
ENV ROOT=/shared
ENV UNPROCCESSED_VIDEOS_NAME=unprocessed_videos
ENV PROCESSED_VIDEOS_NAME=processed_videos
ENV GCLOUD_PROJECT=ifpv-drone-racing-league-003
ENV CS_BUCKET_NAME=ifpv-videos
ENV TOPIC_ID=ifpv-videos-topic
ENV TOPIC_SCHEMA_PATH=./schema.json
ENV GCLOUD_DATABASE_CONNECTION_NAME=ifpv-drone-racing-league-003:us-east1:postgres

# Run the application.
CMD ["python", "api_commands.py"]