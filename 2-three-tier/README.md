# Three-tier Phase 2

This deployment keeps the existing `app/static` frontend unchanged. Nginx is
the presentation tier, FastAPI is the logic tier, and PostgreSQL is the data
tier for feedback.

## Start

From the repository root:

```powershell
Copy-Item 2-three-tier\.env.example 2-three-tier\.env
docker compose --env-file 2-three-tier\.env -f 2-three-tier\docker-compose.yml up --build
```

Open <http://localhost:8080/> in a browser. The browser can reach only Nginx;
Nginx proxies `/api/*` to `logic:8000`, and the logic container reaches
PostgreSQL at `data:5432` on the private Compose network.

PostgreSQL data is retained in the named `three-tier-postgres-data` volume.
Remove that volume explicitly when a clean database is required.

The logic image copies the saved models into `/workspace/src/models`, beside
the copied `src.pipeline` module. It uses the requirements file in
`2-three-tier/logic/requirements.txt`.

The logic container receives `GEMINI_API_KEY` and `GEMINI_MODEL` from
`2-three-tier\.env`. Gemini is optional. A successful response contains
`advisory_source: "gemini"`; otherwise the local advisory has
`advisory_source: "template"`.
