<!-- Phase 1 monolith documentation: serving, deployment, and failure behavior. -->
# Phase 1 monolith

This folder is a deployable copy of the existing app. The frontend files are
unchanged. `api.py` preserves the existing `/`, `/chat`, `/api/health`,
`/api/chat`, and `/api/feedback` routes and response shapes. `pipeline.py`
loads only the saved MaxEnt and CRF joblib artifacts in `models/`; it has no
`torch` import and does not train models. `templates.py` and `gazetteer.py` are the serving copies of the existing
generation dependencies. The gazetteer identifies crop, stage, weather, and
other agriculture slots, while the CRF artifact can refine those labels.
`gemini.py` optionally calls Gemini for localized
advisory wording and reports whether the answer came from `gemini` or the local
`template` fallback.

## Docker

Build from the repository root:

```text
docker build -f 1-monolith/Dockerfile -t floraai-monolith .
Copy-Item 1-monolith\.env.example 1-monolith\.env
docker run --rm --env-file 1-monolith\.env -p 8000:8000 floraai-monolith
```

The image uses a slim Python base, pinned runtime dependencies, and a non-root
`app` user. The Docker healthcheck calls `/api/health`.

## Non-Docker

Install `1-monolith/requirements.runtime.txt`, then run from the copied folder:

```text
cd 1-monolith
python -m uvicorn api:app --host 127.0.0.1 --port 8000
```

The API supports both package-style imports (as used by Docker) and direct
execution from this folder.

## Crash behavior

Invalid request bodies return the existing HTTP 422 contract. Pipeline/model
load failures are isolated at startup and `/api/health` reports
`model_loaded: false`; chat falls back to the existing demo response instead
of crashing the process. Unexpected per-request pipeline failures are logged
to stderr and receive the same demo fallback. Feedback is appended to
`models/feedback_log.jsonl`.

When Gemini is not configured or is unavailable, the local templates are used.
The chat response contains `advisory_source: "gemini"` only after a successful
Gemini response; otherwise it contains `advisory_source: "template"`.
