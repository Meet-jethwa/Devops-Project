-- Initialize durable feedback storage for the Phase 2 logic tier.
CREATE TABLE IF NOT EXISTS feedback (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    request_id VARCHAR(100) NOT NULL,
    action VARCHAR(8) NOT NULL CHECK (action IN ('accept', 'override')),
    override_text VARCHAR(500)
);

CREATE INDEX IF NOT EXISTS feedback_request_id_idx ON feedback (request_id);
