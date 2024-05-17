# Use the official Python 3 Docker image as the base image
FROM python:3

ENV PUBSUB_VERIFICATION_TOKEN=1234
ENV POSTGRES_DB=postgres
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=1234
ENV POSTGRES_PORT=5432
ENV POSTGRES_HOST=10.84.64.3
ENV ROOT=/shared
ENV GCLOUD_PROJECT=ifpv-drone-racing-league-003

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

# Expose port 5000 in the Docker image
EXPOSE 443


CMD ["python", "./subscriber_video_processor.py"]