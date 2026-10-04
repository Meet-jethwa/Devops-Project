# Three-version smoke test: send one request through each architecture.
# It exists to compare the same user message across the lab deployments.
# Analogy: the same order is placed at three stores to compare the service counters.
$ErrorActionPreference = "Stop"
$body = '{"message":"How much urea for tillering stage?","lang":"en","session_id":"smoke-test"}'
$versions = @(
  @{Name = "monolith"; Url = "http://localhost:8000/api/chat"},
  @{Name = "three-tier"; Url = "http://localhost:8080/api/chat"},
  @{Name = "microservices"; Url = "http://localhost:3050/api/chat"}
)
foreach ($version in $versions) {
  try {
    $result = Invoke-RestMethod -Method Post -Uri $version.Url -ContentType "application/json" -Body $body
    [PSCustomObject]@{
      Version = $version.Name
      Intent = $result.intent
      Slots = ($result.slots | ConvertTo-Json -Compress)
      Advisory = $result.advisory
      Source = $result.advisory_source
      Degraded = $result.degraded
    }
  } catch {
    [PSCustomObject]@{Version = $version.Name; Advisory = "unavailable: $($_.Exception.Message)"; Degraded = $true}
  }
}
