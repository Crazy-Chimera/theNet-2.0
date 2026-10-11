-- Iteration 20: durable idempotent authorization results.
-- Apply after 0001_nonce_claims.sql.
CREATE TABLE IF NOT EXISTS thenet_authorization_results (
    operation_id TEXT PRIMARY KEY,
    request_digest TEXT NOT NULL,
    result_json JSONB NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS thenet_authorization_results_expires_at_idx
    ON thenet_authorization_results (expires_at);
