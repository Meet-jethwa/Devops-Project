# Phase 3 gateway image; only nginx and this service are published.
FROM python:3.12-slim
WORKDIR /app
COPY 3-microservices/services/gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY 3-microservices/services/gateway/main.py .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
