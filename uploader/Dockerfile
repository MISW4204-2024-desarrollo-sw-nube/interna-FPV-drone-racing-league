# Use the official Python 3 Docker image as the base image
FROM python:3

# Create a new directory named 'backend' in the Docker image
RUN mkdir /backend

# Set the working directory in the Docker image to '/backend'
WORKDIR /backend

# Copy the 'res' directory from the local system to the '/backend/res' directory in the Docker image
COPY res /backend/res

# Add the 'requirements.txt' file from the local system to the '/backend' directory in the Docker image
ADD requirements.txt /backend/

# Run the 'pip install' command to install the Python packages listed in the 'requirements.txt' file
RUN pip install -r requirements.txt

# Add all files from the local system to the '/backend' directory in the Docker image
ADD * /backend/

# Expose port 5000 in the Docker image
EXPOSE 5000