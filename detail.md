# Sugarcane Irrigation Advisory Lab

This document explains the project in a shareable way. It does not contain
machine-specific file locations, usernames, passwords, or real API keys.

## 1. Project idea

The project is a sugarcane irrigation advisory application. A user asks a
question such as:

```text
When should I irrigate after rain?
```

The application:

1. Receives the question through a FastAPI endpoint.
2. Cleans and analyses the text.
3. Detects the user's intent, such as irrigation or fertilizer use.
4. Extracts useful slots, such as rain, crop stage, or irrigation method.
5. Applies a recommendation rule.
6. Creates an advisory in the selected language.
7. Returns the answer to the unchanged HTML/CSS/JavaScript frontend.

The sensor and weather values are simulated demonstration values. They are not
connected to real field sensors and must not be treated as an automatic
irrigation controller or a guaranteed agricultural prescription.

## 2. API contract

All three versions expose the same frontend-facing contract:

```text
GET  /api/health
POST /api/chat
POST /api/feedback
```

Example chat request:

```json
{
  "message": "When should I irrigate after rain?",
  "lang": "en",
  "session_id": "browser-session"
}
```

The frontend uses relative URLs such as `/api/chat`. Therefore, the same
frontend can work with the monolith, three-tier, or microservice deployment.

## 3. What was implemented

### Monolithic architecture

The first version puts the frontend, FastAPI API, NLP pipeline,
recommendation logic, advisory generation, and JSONL feedback logging in one
deployable container.

If one part of the monolith crashes, the whole application may become
unavailable. Its advantage is that it is simple to build and understand.

### Three-tier architecture

The second version separates the application into:

```text
Presentation tier: Nginx
Logic tier: FastAPI and NLP pipeline
Data tier: PostgreSQL
```

Nginx serves the frontend and forwards `/api/` requests to FastAPI. FastAPI
performs inference and writes feedback to PostgreSQL. Only Nginx is exposed to
the browser.

### Microservice architecture

The third version separates responsibilities into services:

```text
Nginx
  -> gateway
       -> nlp-service
       -> recommendation-service
       -> advisory-service
       -> feedback-service -> PostgreSQL
```

The gateway calls the services in order. It passes an `X-Request-ID` header
between services so a request can be followed in the logs. Downstream calls
have timeouts. If a service is unavailable, the gateway returns a clear
fallback response with `degraded: true`.

## 4. NLP and advisory flow

### Text cleaning

The pipeline removes unwanted control characters, normalizes spacing, and
handles the selected language.

### Intent classification

The saved MaxEnt model classifies the main purpose of the question. Examples
include:

- Water Management
- Fertilizer Use
- Plant Protection
- Market Information
- General Query

The model is loaded from a saved `.joblib` file. The deployment does not train
the model when a container starts.

### Slot extraction

The gazetteer is a domain vocabulary containing known agriculture terms. It
helps identify important words in a question. The saved CRF model can use
these token labels to extract structured slots.

For example, a question may provide slots such as:

```text
weather: rain
method: drip
crop_stage: tillering
```

The gazetteer also provides a rule-based fallback when the saved slot model is
not available.

The microservice NLP image copies this same gazetteer and loads the saved CRF
slot model. This keeps slot extraction consistent with the monolith and
three-tier logic service instead of using a separate simplified word list.

### Recommendation

The recommendation logic selects an action such as:

- irrigate
- skip irrigation
- delay irrigation
- light irrigation
- monitor

The recommendation includes a reason and context. Any sensor or weather
context used by the demonstration is explicitly labelled as simulated.
Rain or weather slots cause the service to check moisture first. Fertilizer
intent produces fertilizer guidance without irrigation hours. Other questions
use the simulated soil-moisture rule.

### Advisory templates

The templates file contains safe local advisory wording and language variants.
It maps structured recommendation values such as action, timing, duration,
rain expectation, and fertigation to readable text.

The local templates are important because they provide a dependable fallback
when an external AI service is not configured or cannot be reached.
The microservice advisory image copies and calls the same `render_advisory`
function, so English, Hindi, Marathi, Gujarati, Punjabi, and Kannada use the
same six-language template source.

Every chat response includes `advisory_source`. It is `gemini` only when a
successful Gemini response was received; otherwise it is `template`. The smoke
test prints this value, so the demo does not claim Gemini output without
evidence.

## 5. Gemini integration

Gemini is used as an optional advisory-text generator. It does not replace
the intent model or recommendation rules.

The application sends Gemini:

- The selected language code
- The recommendation produced by the application
- The simulated-data warning
- Instructions not to invent measurements, doses, or guarantees

The model setting is:

```env
GEMINI_MODEL=gemini-2.5-flash
```

The key is configured locally using an environment file:

```env
GEMINI_API_KEY=my_api_key
GEMINI_MODEL=gemini-2.5-flash
```

`my_api_key` is only a placeholder. A real key must never be written in
source code or committed to version control.

If the key is blank, the request fails, or Gemini returns an unusable response,
the application uses its local advisory templates. This keeps the demo
functional without hiding an error behind a fake successful Gemini result.

## 6. Folder structure

```text
project-root/
|
|-- 1-monolith/
|   |-- api.py
|   |-- pipeline.py
|   |-- gazetteer.py
|   |-- templates.py
|   |-- gemini.py
|   |-- models/
|   |   |-- baseline_maxent_model.joblib
|   |   |-- crf_slot_tagger.joblib
|   |-- static/
|   |   |-- index.html
|   |   |-- chat.html
|   |   |-- styles.css
|   |   |-- app.js
|   |   |-- chat.js
|   |   |-- logo.png
|   |   |-- assets/
|   |-- tests/
|   |-- Dockerfile
|   |-- requirements.runtime.txt
|   |-- .env.example
|   |-- README.md
|
|-- 2-three-tier/
|   |-- docker-compose.yml
|   |-- .env.example
|   |-- .env
|   |-- data/
|   |   |-- init.sql
|   |-- logic/
|   |   |-- main.py
|   |   |-- Dockerfile
|   |   |-- requirements.txt
|   |-- nginx/
|   |   |-- nginx.conf
|   |-- README.md
|
|-- 3-microservices/
|   |-- docker-compose.yml
|   |-- .env.example
|   |-- nginx/
|   |   |-- nginx.conf
|   |-- services/
|   |   |-- gateway/
|   |   |-- nlp-service/
|   |   |-- recommendation-service/
|   |   |-- advisory-service/
|   |   |-- feedback-service/
|   |-- tests/
|   |-- demo_failure.ps1
|   |-- README.md
|
|-- app/
|   |-- static/
|       |-- Original shared frontend files
|
|-- docs/
|   |-- architecture.md
|   |-- screenshots/
|
|-- scripts/
|   |-- smoke_test.ps1
|
|-- .github/
|   |-- workflows/
|       |-- ci.yml
|
|-- requirements.txt
|-- README.md
|-- detail.md
|-- 1.pdf
|-- .gitignore
```

The `.env` files are local configuration files and should not be shared when
they contain real secrets. The `.env.example` files show the required variable
names without exposing a secret.

## 7. Beginner run guide

Install Python 3.10 or newer, Docker Desktop, and a web browser. Start Docker
Desktop and wait until its engine is running. Use PowerShell from the project
root.

Create local environment files when needed:

```powershell
Copy-Item 1-monolith\.env.example 1-monolith\.env
Copy-Item 2-three-tier\.env.example 2-three-tier\.env
Copy-Item 3-microservices\.env.example 3-microservices\.env
```

Gemini is optional. Replace `my_api_key` only in a local `.env` file if a real
key is available. Never commit a real key. A missing or unavailable Gemini
key uses local templates and reports `advisory_source: "template"`.

### Run the monolith

```powershell
docker build -f 1-monolith\Dockerfile -t floraai-monolith .
docker run --rm --name floraai-monolith `
  --env-file 1-monolith\.env -p 8000:8000 floraai-monolith
```

Open `http://localhost:8000/`. Health is available at
`http://localhost:8000/api/health`. Stop it with `Ctrl+C`.

### Run the three-tier version

```powershell
docker compose --env-file 2-three-tier\.env `
  -f 2-three-tier\docker-compose.yml up --build
```

Open `http://localhost:8080/` and check
`http://localhost:8080/api/health`. Stop it with `Ctrl+C`, then run:

```powershell
docker compose -f 2-three-tier\docker-compose.yml down
```

The named PostgreSQL volume remains so feedback is preserved.

### Run the microservices version

```powershell
Set-Location 3-microservices
docker compose --env-file .env up --build
```

Open `http://localhost:3050/` and check:

```powershell
Invoke-RestMethod http://localhost:3050/api/health
```

Do not open `/api/chat` directly in a browser address bar. That sends `GET`,
while chat requires `POST` with JSON. Use the frontend or:

```powershell
$body = @{
  message = "what is sugarcane"
  lang = "en"
  session_id = "run-test"
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri http://localhost:3050/api/chat `
  -ContentType "application/json" `
  -Body $body
```

A direct `GET` returning `405 Method Not Allowed` is expected. To demonstrate
failure isolation, run `.\demo_failure.ps1` from another PowerShell window.
It stops the advisory service, sends a request, prints the degraded fallback,
and starts the service again. Stop the stack with `docker compose down`.

### Test and compare

```powershell
python -m pytest 1-monolith\tests 2-three-tier\tests 3-microservices\tests
.\scripts\smoke_test.ps1
```

The smoke script sends the same question to all three deployments and prints
the advisory, its source, and the microservice degraded status.
It currently sends:

```text
How much urea for tillering stage?
```

The expected comparison is a non-`General Query` intent, a non-empty
`STAGE=tillering` slot, and fertilizer guidance without irrigation hours in
all three responses. The script also prints intent and slots.

### Common problems

- Start Docker Desktop if Docker cannot connect.
- If port `8000` is busy, use another host mapping such as `8010:8000`.
- If port `8080` is busy, change `PRESENTATION_PORT` in
  `2-three-tier\.env`.
- If CSS is missing, recreate the Nginx container with
  `docker compose --env-file .env up -d --build --force-recreate nginx`.
- Do not double-click `index.html`; the frontend needs HTTP for `/static/`
  assets and `/api/` requests.

## 8. Viva questions and honest answers

1. **Why build three versions?** To compare deployment structure, scaling,
   data ownership, and failure isolation with the same application.
2. **What is the monolith?** One deployable application contains the frontend,
   API, NLP, recommendation rules, and feedback logging.
3. **What does Nginx do?** It serves the frontend and forwards API requests to
   private backend services.
4. **Why use three tiers?** Presentation, application logic, and data are
   separated and can be managed independently.
5. **Why PostgreSQL?** It provides structured, persistent feedback storage.
6. **Why are sensors simulated?** This is a deployment lab without connected
   farm hardware or real field data.
7. **What does NLP do?** It detects intent and extracts agriculture-related
   slots from the question.
8. **Are models trained at startup?** No. Containers load saved inference
   artifacts only.
9. **Why no PyTorch?** The serving path needs the saved MaxEnt and CRF
   artifacts plus the rule-based gazetteer, not training libraries.
10. **What happens when a service fails?** The gateway uses a timeout and
    returns a safe fallback with `degraded: true`.
11. **Why use `X-Request-ID`?** It connects logs for one request across
    services.
12. **Why is Gemini optional?** Local templates keep the demo functional
    without an API key, internet, or external quota.
13. **How is Gemini usage shown?** The response says `gemini` only after
    usable Gemini text; otherwise it says `template`.
14. **Why are microservices not always better?** They add network,
    deployment, monitoring, and debugging complexity.
15. **Can this control irrigation automatically?** No. It is an educational
    advisory using simulated context and must be checked in the field.
16. **Does the frontend change between versions?** No. Relative `/api/` URLs
    let the deployment decide how requests are routed.

17. **How are timeouts configured?** Microservice Gemini requests use a
    six-second timeout, gateway downstream calls use eight seconds, and Nginx
    waits up to twelve seconds for the gateway.

## 9. Testing and CI

The project includes API contract tests, service health tests, regression tests
for fertilizer slots and Marathi output, a smoke script, and a GitHub Actions
workflow that runs tests, checks JavaScript syntax with `node --check`, and
builds the Docker images.

## 10. Cleanup decisions

Training datasets, evaluation reports, plots, notebooks, old training source,
PyTorch checkpoints, SentencePiece artifacts, and generated caches were
removed because they are not required to run the deployment demo. Saved
inference models, serving code, frontend files, Docker files, tests, and
documentation were kept.

## 11. Important limitations

- This is an educational deployment demonstration.
- Sensor and weather values are simulated.
- Recommendations must be checked against real field conditions.
- Gemini requires a valid internet connection and API key.
- Local templates remain necessary when Gemini is unavailable.
- Microservices add operational complexity.
- PostgreSQL feedback persists only while its Docker volume is preserved.
