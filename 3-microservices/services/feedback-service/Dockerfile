# Phase 3 feedback image.
FROM python:3.12-slim
WORKDIR /app
COPY 3-microservices/services/feedback-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY 3-microservices/services/feedback-service/main.py .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
