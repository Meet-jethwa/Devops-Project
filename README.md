# Sugarcane irrigation advisory lab

This project is an educational FastAPI/NLP advisory system for sugarcane
irrigation questions. It demonstrates the same application in three deployment
styles:

1. A monolith
2. A three-tier application
3. A microservice application

Sensor and weather values are simulated demo values. They are labelled as
simulated in the code and must not be treated as a real irrigation controller
or agronomic prescription.

## What is preserved

- [`1.pdf`](./1.pdf) is the project/use-case
  specification.
- [`app/static/`](./app/static/) is the
  original no-build HTML/CSS/JavaScript frontend.
- The saved serving models are copied into
  [`1-monolith/models/`](./1-monolith/models/) and reused by the NLP services.
  The microservice NLP image loads both the saved MaxEnt intent model and the
  saved CRF slot model, with the serving gazetteer as its fallback.
- Training datasets, evaluation reports, plots, notebooks, PyTorch
  checkpoints, and SentencePiece artifacts were removed because they are not
  needed to run the deployment demo.
- The containers do not install or import PyTorch.

## API contract

All three versions preserve the frontend-facing routes:

```text
GET  /api/health
POST /api/chat
POST /api/feedback
```

Chat input:

```json
{
  "message": "When should I irrigate sugarcane?",
  "lang": "en",
  "session_id": "browser-session"
}
```

The frontend continues to call relative `/api/...` URLs. No frontend rewrite
is required.

## Runtime model files

The serving deployments use only the saved inference artifacts:

- `baseline_maxent_model.joblib` for intent classification
- `crf_slot_tagger.joblib` where the CRF artifact is available

The saved MaxEnt artifact records scikit-learn version `1.9.1`; runtime
requirements pin that version for compatibility.

Gemini advisory generation is optional and uses the current stable
`gemini-2.5-flash` model by default. Chat responses report
`advisory_source: "gemini"` or `"template"` so the source is visible.

## Prepare a local Python environment

From the repository root, create and activate a virtual environment, then
install the shared local requirements:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The root requirements file is for local development and tests. Docker images
use their own smaller service-specific requirement files. PyTorch is not
included because the serving containers use only the saved MaxEnt and CRF
artifacts.

## Phase 1: monolith

Folder: [`1-monolith/`](./1-monolith/)

The monolith contains the frontend, FastAPI routes, NLP pipeline,
recommendation rules, advisory templates, and JSONL feedback logging in one
deployable image.

Build and run from the repository root:

```powershell
docker build -f 1-monolith\Dockerfile -t floraai-monolith .
docker run --rm -p 8000:8000 floraai-monolith
```

Open `http://localhost:8000/` or `http://localhost:8000/chat`.

Open the application through this HTTP URL, not by double-clicking
`app/static/index.html`. The frontend needs the server's `/static/` assets and
`/api/` routes.

The image uses a slim Python base, pinned runtime requirements, a non-root
user, and a healthcheck for `/api/health`.

## Phase 2: three-tier

Folder: [`2-three-tier/`](./2-three-tier/)

```text
Browser -> nginx presentation -> FastAPI logic -> PostgreSQL data
```

The browser can reach only nginx. The logic tier does not serve static files.
PostgreSQL uses a named volume and `data/init.sql` creates the feedback table.

Run:

```powershell
Copy-Item 2-three-tier\.env.example 2-three-tier\.env
docker compose --env-file 2-three-tier\.env -f 2-three-tier\docker-compose.yml up --build
```

Open `http://localhost:8080/`.

Stop with `Ctrl+C`. Remove the persistent database volume only when you
intentionally want to erase the stored feedback:

```powershell
docker compose -f 2-three-tier\docker-compose.yml down
docker volume rm dev_three-tier-postgres-data
```

## Phase 3: microservices

Folder: [`3-microservices/`](./3-microservices/)

```text
Browser -> nginx -> gateway
                    -> nlp-service
                    -> recommendation-service
                    -> advisory-service
                    -> feedback-service -> PostgreSQL
```

The gateway calls NLP, recommendation, and advisory in that order. Nginx is
available on host port `3050`; private
requests carry the same `X-Request-ID`. Downstream calls have timeouts. If a
downstream service is unavailable, the gateway returns a clear fallback with
`"degraded": true`.

Run:

```powershell
cd 3-microservices
docker compose up --build
```

Open `http://localhost:3050/`.

To demonstrate failure isolation:

```powershell
cd 3-microservices
.\demo_failure.ps1
```

The script stops `advisory-service`, sends a chat request, prints the degraded
response, and starts the service again.

## Tests and smoke test

Tests are split by service under
[`3-microservices/tests/`](./3-microservices/tests/).
The monolith contract tests are under
[`1-monolith/tests/`](./1-monolith/tests/).

Install test packages into your chosen Python environment:

```powershell
python -m pip install pytest httpx fastapi
```

Run:

```powershell
python -m pytest 1-monolith\tests 2-three-tier\tests 3-microservices\tests
```

The comparison script is
[`scripts/smoke_test.ps1`](./scripts/smoke_test.ps1).
Start the deployments in separate PowerShell windows, then run:

```powershell
.\scripts\smoke_test.ps1
```

It sends the same question to the three URLs and prints the advisory and
degraded status side by side. The current comparison question is:

```text
How much urea for tillering stage?
```

The output should show a non-`General Query` intent and a non-empty
`STAGE=tillering` slot for all three versions. The advisory should provide
fertilizer guidance rather than an irrigation duration.

## Documentation

- [`detail.md`](./detail.md) is a shareable project explanation covering what
  was built, how it works, Gemini configuration, and the complete folder
  structure without private machine paths.
- [`docs/architecture.md`](./docs/architecture.md)
  contains Mermaid diagrams and a comparison table.
- [`.github/workflows/ci.yml`](./.github/workflows/ci.yml)
  runs tests, checks every frontend JavaScript file with `node --check`, and
  builds the Docker images in GitHub Actions.
- [`1-monolith/README.md`](./1-monolith/README.md),
  [`2-three-tier/README.md`](./2-three-tier/README.md),
  and [`3-microservices/README.md`](./3-microservices/README.md)
  contain version-specific instructions.

## Validation status

The following checks were completed during setup:

```text
Python syntax compilation: passed
Phase 2 Docker Compose configuration: passed
Phase 3 Docker Compose configuration: passed
Generated project caches: removed
```

Live pytest execution and Docker image builds must be run on a machine with
pytest installed and Docker Desktop's Linux engine running. Do not describe
those checks as passed until their commands complete successfully.

## Demo command summary

These commands represent the demo sequence; the long-running containers should
be kept in separate PowerShell windows:

```powershell
Copy-Item 1-monolith\.env.example 1-monolith\.env
docker build -f 1-monolith\Dockerfile -t floraai-monolith .
docker run --rm --env-file 1-monolith\.env -p 8000:8000 floraai-monolith
Copy-Item 2-three-tier\.env.example 2-three-tier\.env
docker compose --env-file 2-three-tier\.env -f 2-three-tier\docker-compose.yml up --build
Copy-Item 3-microservices\.env.example 3-microservices\.env
cd 3-microservices; docker compose --env-file .env up --build
.\scripts\smoke_test.ps1
```
