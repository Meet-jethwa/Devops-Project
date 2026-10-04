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
  -Body '{"message":"How long should I irrigate sugarcane?","lang":"en"}'
.\demo_failure.ps1
```

The gateway calls NLP, then recommendation, then advisory. It propagates
`X-Request-ID`, applies a 2.5-second timeout to each downstream call, preserves the frontend response keys (`request_id`, `intent`,
`confidence`, `slots`, `advisory`, `demo_data`, `suggestions`, and `lang`), and
adds `advisory_source`. It adds `degraded: true` when a dependency is
unavailable.
`advisory_source` is `gemini` only after a successful Gemini response;
otherwise it is `template`. NLP loads the saved
MaxEnt joblib and uses the project gazetteer without importing torch. The
recommendation context is intentionally labelled simulated sensor/weather
data; it is not an agronomic control signal. Feedback is stored in PostgreSQL.

Only nginx is reachable from the host on port `3050`. The gateway and all
other services are private containers on the Compose network.
