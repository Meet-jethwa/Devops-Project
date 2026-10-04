# Phase 3 advisory image.
FROM python:3.12-slim
WORKDIR /app
COPY 3-microservices/services/advisory-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY 3-microservices/services/advisory-service/main.py .
COPY 1-monolith/templates.py /app/templates.py
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
