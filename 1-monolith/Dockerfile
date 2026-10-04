# Phase 1 production image for the serving-only monolith.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

COPY 1-monolith/requirements.runtime.txt ./requirements.runtime.txt
RUN pip install --no-cache-dir -r requirements.runtime.txt \
    && addgroup --system app \
    && adduser --system --ingroup app app

COPY 1-monolith/ /app/monolith/
RUN chown -R app:app /app
USER app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=3)"
CMD ["uvicorn", "monolith.api:app", "--host", "0.0.0.0", "--port", "8000"]
