# Build the FastAPI logic tier without packaging or serving frontend assets.
FROM python:3.12-slim

WORKDIR /workspace
COPY 2-three-tier/logic/requirements.txt /workspace/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY 1-monolith/pipeline.py /workspace/src/pipeline.py
COPY 1-monolith/gazetteer.py /workspace/src/gazetteer.py
COPY 1-monolith/templates.py /workspace/src/templates.py
COPY 1-monolith/gemini.py /workspace/gemini.py
COPY 1-monolith/models /workspace/src/models
COPY 2-three-tier/logic/main.py /workspace/logic/main.py
RUN touch /workspace/src/__init__.py /workspace/logic/__init__.py

EXPOSE 8000
CMD ["uvicorn", "logic.main:app", "--host", "0.0.0.0", "--port", "8000"]
