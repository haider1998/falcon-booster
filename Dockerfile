# Use the official Python image from the Docker Hub
FROM python:3.11.8-slim

# Install git and ssh
RUN apt-get update && apt-get install -y git openssh-client

# Create a directory for the SSH keys
RUN mkdir -p /root/.ssh

# Copy the private SSH key into the container
COPY id_rsa /root/.ssh/id_rsa

# Set the correct permissions for the SSH key
RUN chmod 600 /root/.ssh/id_rsa

# Add GitHub to known hosts to prevent SSH from asking for confirmation
RUN ssh-keyscan github.com >> /root/.ssh/known_hosts

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Set environment variables for GitPython
ENV GIT_PYTHON_REFRESH=quiet

# Command to run the application
CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000"]