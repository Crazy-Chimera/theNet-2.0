-- Iteration 17: durable nonce claims for replay protection.
-- Apply once before configuring PostgresNonceStore.
CREATE TABLE IF NOT EXISTS thenet_nonce_claims (
    scope TEXT NOT NULL,
    nonce TEXT NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    claimed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT thenet_nonce_claims_scope_nonce_pk PRIMARY KEY (scope, nonce)
);

CREATE INDEX IF NOT EXISTS thenet_nonce_claims_expires_at_idx
    ON thenet_nonce_claims (expires_at);
