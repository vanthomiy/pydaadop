# Base image: Python 3.10
FROM python:3.10-slim

# Install git and other dependencies
RUN apt-get update && apt-get install -y git && apt-get clean

# Set working directory in the container
WORKDIR /app

# Copy requirements.txt into the container
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the example.env file into the container
COPY example.env .env

# Load environment variables from the .env file
RUN export $(cat .env | xargs)

# Expose the port the FastAPI app will run on
EXPOSE ${FAST_API_PORT}

WORKDIR /app

# Command to run FastAPI using uvicorn
CMD ["uvicorn", "api:app", "--host", "${FAST_API_BASE_URL}", "--port", "${FAST_API_PORT}"]