# Phase 3 torch-free NLP image.
FROM python:3.12-slim
WORKDIR /app
COPY 3-microservices/services/nlp-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY 3-microservices/services/nlp-service/main.py .
COPY 1-monolith/models /models
COPY 1-monolith/gazetteer.py /app/gazetteer.py
ENV MODEL_PATH=/models/baseline_maxent_model.joblib
ENV CRF_MODEL_PATH=/models/crf_slot_tagger.joblib
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
