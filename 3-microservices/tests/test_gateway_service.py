# Gateway smoke tests.
# It exists to verify the public gateway health endpoint without downstream services.
# Analogy: check that the reception desk is open before calling back offices.
from fastapi.testclient import TestClient

from conftest import load_service


def test_gateway_health():
    client = TestClient(load_service("gateway", "services/gateway/main.py").app)
    assert client.get("/health").status_code == 200
