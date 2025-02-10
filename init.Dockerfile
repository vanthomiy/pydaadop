# Base image: Python 3.10
FROM python:3.10-slim

# Install git and other dependencies
RUN apt-get update && apt-get install -y git && apt-get clean

# Copy requirements.txt into the container
COPY requirements.txt .

ARG CACHEBUST=1
# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the example.env file into the container
COPY example.env .env

# Copy the .py files into the container
COPY . .

# Set the working directory
WORKDIR /

# Set the entrypoint to run the Python script
ENTRYPOINT ["python", "init.py"]