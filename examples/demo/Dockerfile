FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY examples/demo ./examples/demo
RUN pip install --upgrade pip
RUN pip install --no-cache-dir .
EXPOSE 8000
CMD ["uvicorn", "examples.demo.api:app", "--host", "0.0.0.0", "--port", "8000"]
