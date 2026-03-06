# Base image: Python 3.10
FROM python:3.10-slim

# Install git and other dependencies
RUN apt-get update && apt-get install -y git && apt-get clean

# Retrieve the expected environment variables
ARG FAST_API_BASE_URL
ARG FAST_API_PORT

# Set working directory in the container
WORKDIR /app

# Copy requirements.txt into the container
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the example.env file into the container
COPY example.env .env

# Copy the api.py file into the container
COPY api.py .

# Expose the port the FastAPI app will run on
EXPOSE ${FAST_API_PORT}

WORKDIR /app

# Command to run FastAPI using uvicorn
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port 8000"]
