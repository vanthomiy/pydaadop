FROM python:3.12-slim

WORKDIR /app

# Install build dependencies
RUN pip install --no-cache-dir --upgrade pip
\
# Ensure Pydantic v2 is installed so pydantic.core_schema is available
RUN pip install --no-cache-dir "pydantic==2.9.2" "pydantic-core"

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install the package
RUN pip install --no-cache-dir .

# Copy the examples so users can run a sample app
COPY examples/ ./examples/

EXPOSE 8000

# Default: run the example FastAPI app (override via docker run command)
CMD ["uvicorn", "examples.setups.basic.api:app", "--host", "0.0.0.0", "--port", "8000"]
