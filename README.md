# theNet-2.0

**Status: Iteration 18 — live PostgreSQL 16 integration tests added; CI passed (run 38114828761, 178 tests).**

theNet-2.0 implements a relational, evolutionary network architecture while keeping infrastructure integrations explicit and verifiable.

## Architectural sequence

Genesis → Relation → Φ Structure → Ω Pohyb → Ω² Memory → ΦΩ² Resonance → Γ Convergence → Π Meaning → Ψ Expression → Θ Self-Knowledge → Ρ Relational Co-definition → Σ / ΙΩΤΑ closure → prepared evolution → signed evidence → policy-gated authorization → nonce replay protection.

## Current executable slice

The thenet_core package provides immutable records and deterministic identifiers for the architecture's domain layers, Ed25519 signed attestations, policy-gated authorization decisions, and nonce replay protection.

Authorization re-verifies each attestation and checks the action, target, subject, context, required issuers, and canonical digest of the exact CommitIntent. It then atomically claims all issuer/key-scoped nonces before returning an authorized decision. A missing nonce store fails closed.

`InMemoryNonceStore` is thread-safe and all-or-none for a single process, but it is not durable and does not coordinate multiple workers or hosts. The `PostgresNonceStore` adapter uses a database uniqueness constraint and one transaction per batch; apply `migrations/0001_nonce_claims.sql` first and inject a DB-API connection factory. A conflicting claim rolls back the whole batch. Database errors are rolled back and re-raised, so the caller must fail closed. CI now runs integration tests against a PostgreSQL 16 service, covering persistence across store instances, transaction rollback on a conflicting batch, concurrent claims from 12 independent connections, and expiry cleanup/reuse. This validates the adapter against a real PostgreSQL server in CI, but does not establish production deployment readiness or test a separately provisioned multi-host environment. An authorized decision is still only a record: it does not execute a change, mutate system state, or create a Git commit.

Trust policy and trust-map provenance remain external. Signature validity does not prove real-world identity or claim truth. Secrets and private keys must never be committed.

## Durable nonce store

```python
from thenet_core import PostgresNonceStore

# Supply a connection factory from your PostgreSQL driver, e.g. psycopg.connect.
nonce_store = PostgresNonceStore(connection_factory)
```

The connection factory must return a fresh DB-API connection. Apply the SQL migration before use. The table primary key `(scope, nonce)` coordinates duplicate claims across processes sharing the same PostgreSQL database; expired rows are pruned inside each claim transaction. Configure connection timeouts, TLS, credentials and database availability in deployment infrastructure.
\n## Platform layers

1. Infrastructure: DNS, TCP/IP, TLS 1.3, HTTP/2, WebSockets and managed/cloud storage.
2. Relational layer: PostgreSQL + TimescaleDB, Neo4j, Redis and S3-compatible storage (target architecture).
3. Identity layer: decentralized identifiers and Ed25519 key pairs.
4. Incentive layer: relational accounting and verifiable contribution rewards.
5. Evolution layer: local evolution, verified-pattern synchronization, coherence thresholds, sandboxing and benchmarks.
6. Interface layer: React + TypeScript web app, React Native mobile app, desktop client, REST/WebSocket/gRPC APIs.

These are target architecture choices, not a claim that services are provisioned or connected.

## Development

- Reference implementation: https://github.com/Crazy-Chimera/theNet
- Target repository: https://github.com/Crazy-Chimera/theNet-2.0
- Development protocol: docs/DEVELOPMENT_PROTOCOL.md
- Architecture contract: docs/ARCHITECTURE.md
- Context and invariants: docs/CONTEXT.md
