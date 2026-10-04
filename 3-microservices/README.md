# Phase 3 microservices

This deployment leaves the existing frontend untouched. `nginx` is the edge
proxy. The gateway, NLP,
recommendation, advisory, feedback, and PostgreSQL are private on the
Compose network.

```powershell
cd 3-microservices
Copy-Item .env.example .env
docker compose --env-file .env up --build
Invoke-RestMethod http://localhost:3050/api/health
Invoke-RestMethod -Method Post http://localhost:3050/api/chat -ContentType application/json `
  -Body '{"message":"How much urea for tillering stage?","lang":"en"}'
.\demo_failure.ps1
```

The gateway calls NLP, then recommendation, then advisory. It propagates
`X-Request-ID`, applies an eight-second timeout to each downstream call, preserves the frontend response keys (`request_id`, `intent`,
`confidence`, `slots`, `advisory`, `demo_data`, `suggestions`, and `lang`), and
adds `advisory_source`. It adds `degraded: true` when a dependency is
unavailable.
`advisory_source` is `gemini` only after a successful Gemini response;
otherwise it is `template`. NLP loads the saved MaxEnt and CRF joblib
artifacts and uses the copied project gazetteer without importing torch. The
recommendation service uses intent and slots: rain/weather slots check
moisture first, while fertilizer intent gives fertilizer guidance without
irrigation hours. The recommendation context is intentionally labelled
simulated sensor/weather data; it is not an agronomic control signal. Feedback
is stored in PostgreSQL.

The advisory image copies `1-monolith/templates.py` and uses `render_advisory`
for all six supported languages: English, Hindi, Marathi, Gujarati, Punjabi,
and Kannada. Gemini requests have a six-second timeout. Nginx waits up to
twelve seconds for the gateway.

Only nginx is reachable from the host on port `3050`. The gateway and all
other services are private containers on the Compose network.
