# Phase 2 API contract test for the copied serving pipeline.
# It exists to catch a missing intent or slot in the logic tier.
# Analogy: this is a quick inspection before the logic desk answers a farmer.
import importlib.util
import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[2]
MONOLITH = ROOT / "1-monolith"
LOGIC_PATH = ROOT / "2-three-tier" / "logic" / "main.py"
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
sys.path.insert(0, str(MONOLITH))

spec = importlib.util.spec_from_file_location("three_tier_logic", LOGIC_PATH)
logic = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(logic)

pipeline_spec = importlib.util.spec_from_file_location("pipeline", MONOLITH / "pipeline.py")
pipeline_module = importlib.util.module_from_spec(pipeline_spec)
assert pipeline_spec.loader is not None
pipeline_spec.loader.exec_module(pipeline_module)
logic.PIPELINE = pipeline_module.AdvisoryPipeline()
logic.MODEL_LOADED = logic.PIPELINE.intent_model is not None

client = TestClient(logic.app)


def test_fertilizer_question_has_intent_and_slots():
    response = client.post(
        "/api/chat",
        json={"message": "How much urea for tillering stage?", "lang": "en"},
    )
    body = response.json()
    assert body["intent"] != "General Query"
    assert body["slots"]
