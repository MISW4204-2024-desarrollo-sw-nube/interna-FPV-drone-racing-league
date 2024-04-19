# Use the official Kotlin image as the base image
FROM gradle:8.7.0-jdk21

# Set the working directory
WORKDIR /app

# Copy the build.gradle.kts file to the container
COPY . .

# Run the Gradle build
RUN gradle build
