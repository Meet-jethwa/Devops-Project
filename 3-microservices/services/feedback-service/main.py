# Feedback service: store user feedback in PostgreSQL.
# It exists so feedback data has one clear owner in the microservice design.
# Analogy: this is the clerk who keeps the suggestion book.
import os
from datetime import datetime, timezone
from typing import Any

import asyncpg
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://flora:change-me@postgres:5432/flora")
app = FastAPI(title="Feedback service", version="3.0.0")
pool: asyncpg.Pool | None = None


class Feedback(BaseModel):
    request_id: str = Field(min_length=1, max_length=100)
    action: str = Field(pattern="^(accept|override)$")
    override_text: str | None = Field(default=None, max_length=500)


@app.middleware("http")
async def request_log(request: Request, call_next):
    response = await call_next(request)
    print(
        f"request_id={request.headers.get('X-Request-ID', '-')} "
        f"path={request.url.path} status={response.status_code}",
        flush=True,
    )
    return response


@app.on_event("startup")
async def startup() -> None:
    global pool
    try:
        pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
        async with pool.acquire() as conn:
            await conn.execute(
                """CREATE TABLE IF NOT EXISTS feedback (
                    id BIGSERIAL PRIMARY KEY,
                    request_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    override_text TEXT,
                    created_at TIMESTAMPTZ NOT NULL
                )"""
            )
    except (OSError, asyncpg.PostgresError):
        pool = None


@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "status": "ok" if pool else "degraded",
        "service": "feedback-service",
        "database": "postgresql" if pool else "unavailable",
    }


@app.post("/feedback")
async def feedback(item: Feedback) -> dict[str, bool]:
    if pool is None:
        return {"ok": False}
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO feedback(request_id, action, override_text, created_at) "
            "VALUES($1, $2, $3, $4)",
            item.request_id,
            item.action,
            item.override_text,
            datetime.now(timezone.utc),
        )
    return {"ok": True}


@app.get("/feedback/count")
async def feedback_count() -> dict[str, int]:
    if pool is None:
        return {"count": 0}
    async with pool.acquire() as conn:
        count = await conn.fetchval("SELECT COUNT(*) FROM feedback")
    return {"count": int(count)}
