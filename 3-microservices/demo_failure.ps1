# Phase 3 failure demo: stop one private service and show gateway degraded fallback.
param([string]$ComposeFile = "docker-compose.yml")
$ErrorActionPreference = "Stop"
docker compose -f $ComposeFile stop advisory-service
try {
  Invoke-RestMethod -Method Post -Uri "http://localhost:3050/api/chat" `
    -ContentType "application/json" -Body '{"message":"When should I irrigate sugarcane?","lang":"en"}' |
    ConvertTo-Json
} finally {
  docker compose -f $ComposeFile start advisory-service
}
