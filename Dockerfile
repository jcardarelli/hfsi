# Use a Python base image (assuming Fetch.AI dependencies are in Python)
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install necessary system dependencies
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    curl \
    libssl-dev \
    libffi-dev \
    python3-dev \
    python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt to the container
COPY requirements.txt /app/

# Install Python dependencies (you would need to provide this file)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your Fetch.AI agent or application code
COPY . /app/

# Expose the necessary ports (depends on your Fetch.AI application; this is just an example)
EXPOSE 5000