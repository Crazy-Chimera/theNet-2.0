# Step-by-step Development Protocol

## Iteration cycle
1. Inspect repository, current branch/head, modules and infrastructure.
2. Define purpose, input/output, invariants, failure behavior, trust boundary and acceptance criteria.
3. Implement one bounded module or vertical slice.
4. Review scope, security, compatibility and dependencies.
5. Add positive, negative, edge-case, integrity and determinism tests.
6. Run checks and record exact results; never claim unrun checks.
7. Integrate dependent modules only after contract/tests pass.
8. Update architecture, usage and operational status.
9. Commit a small, descriptive change after verification.
10. Review evidence before the next iteration.

## Gates
- Do not skip a failing gate or build on an ambiguous contract.
- Keep infrastructure adapters separate from core domain logic.
- Use deterministic local tests; explicitly configure real external services.
- Never store credentials in code, tests, logs, commits or example configuration.
- Deployment claims require actual deployment and runtime health evidence.

## Iterations 1–13
The earlier iterations establish Genesis → Relation → AgentState → Structure → Pohyb → Memory → Resonance → Convergence → Meaning → Expression → Self-Knowledge → Co-definition → Closure → prepared CommitIntent. Individual historical CI evidence is retained in repository history.

## Iteration 14 — Ed25519 signed attestation
**Contract:** canonical claims bind issuer, subject, context, payload digest, issue/expiry times, nonce and key ID. Verification checks signature, issuer/key match, allowed context, revocation and validity at an explicit UTC instant.
**Trust boundary:** trust map is caller-supplied; signature validity does not establish real-world identity, claim truth, secure trust-store distribution or persistent anti-replay.
**CI:** run 38111078596 passed for commit f42f64e81521932f6c286aca4de4f6addf4bd0f0 (152 tests).

## Iteration 15 — policy-gated authorization decision
**Contract:** policy supplies allowed actions, targets, context and required issuer IDs. Each required issuer must provide a unique valid Ed25519 attestation whose subject is the intent identity binding and whose signed payload binds intent ID, action, target, identity binding and proposed-change digest.
**Trust boundary:** policy and trust map remain caller-supplied. An authorized decision is not an execution token.
**CI:** run 38111295066 passed for commit f307921524af1dc29adb1899a25c15f3cf1377b7 (163 tests).

## Iteration 16 — nonce replay protection
**Goal:** prevent a valid attestation nonce from authorizing more than once while its validity window remains active.
**Contract:** nonce scope is issuer plus key ID. A NonceStore must atomically claim all nonce tuples or none. Authorization fails closed without a store, re-verifies evidence before claiming nonces, and returns rejected/replay_detected if a claim is already active.
**Acceptance:** second use rejected, expired claims pruned, batch claims atomic, duplicate claims rejected, and concurrent claims yield one winner.
**Trust boundary:** InMemoryNonceStore is process-local and non-durable. Production requires a shared durable transactional implementation; no such adapter is included in this iteration.
**CI:** run 38111490989 passed for commit 552039bf443265ec20ddd98bf01be9befbbbdadc (168 tests passed).


## Iteration 17 — transactional PostgreSQL nonce store
**Goal:** provide a durable `NonceStore` adapter so workers sharing PostgreSQL can coordinate nonce claims across process restarts.
**Contract:** `PostgresNonceStore` accepts a DB-API connection factory. The migration creates `thenet_nonce_claims` with a primary key on `(scope, nonce)` and an expiry index. Each batch deletes expired rows, inserts all claims using `ON CONFLICT DO NOTHING`, and commits only if every insert succeeds. A conflict rolls back the batch and returns `False`; database exceptions roll back and propagate.
**Failure behavior:** the authorization caller must treat database errors as a failed authorization attempt. Do not fall back automatically to `InMemoryNonceStore`, because that would weaken cross-process replay protection.
**Verification:** CI run 38114620072 passed for implementation commit 8a1ae575bf30d43b8a83914aa30d0e5da9a4561d (174 tests passed). Unit tests exercise commit, conflict rollback, exception rollback and validation using a fake DB-API connection.
**Limitations:** CI did not connect to a live PostgreSQL server. Cross-process behavior relies on PostgreSQL transaction and unique-constraint semantics and still requires a live integration test, migration execution, connection/security configuration and operational monitoring before production use.


## Iteration 18 — live PostgreSQL integration verification
**Goal:** verify the transactional nonce adapter against a real PostgreSQL service rather than only a DB-API fake.
**CI setup:** workflow run 38114828761 starts a PostgreSQL 16 service container, installs Psycopg 3 for tests, and sets `THENET_TEST_POSTGRES_DSN` only in the CI job environment.
**Integration coverage:** persistence across separate store instances; all-or-none rollback when a batch contains a conflicting nonce; 12 concurrent attempts using independent database connections with exactly one successful claim; and expired-claim pruning followed by reuse.
**Verification:** CI run 38114828761 passed for implementation commit 38a519f770418feac3a3fc9a85fed332632129c2. Build and package installation succeeded; **178 tests passed in 0.60 seconds**, including live PostgreSQL integration tests.
**Limitations:** this is an ephemeral PostgreSQL 16 CI service, not a production deployment. Production readiness still requires deployment-specific credentials/TLS, connection limits/timeouts, migration management, observability, backups and operational failure testing. No production database or multi-host deployment is claimed.


## Iteration 19 — fail closed on nonce-store errors
**Goal:** ensure storage outages and ambiguous transaction outcomes cannot be reported as successful authorization.
**Contract:** exceptions from `NonceStore.claim_many` return `rejected/nonce_store_unavailable`; an already-consumed nonce returns `rejected/replay_detected`. No fallback to process-local state is performed.
**Ambiguous commit test:** CI run 38115193371 passed for commit fe8f01861890cc994481bf384e1e997f810dd52f. The test simulates a nonce claim committed before the client loses confirmation; the first attempt fails closed and the retry is rejected as a replay.
**Limitation:** this iteration did not recover the original decision after an ambiguous commit; it prevented duplicate authorization by failing closed.

## Iteration 20 — atomic idempotent authorization-result persistence
**Goal:** recover a previously committed authorization decision after an ambiguous client/database outcome without claiming its nonce a second time.
**Schema:** migration `0002_authorization_results.sql` creates `thenet_authorization_results`, keyed by operation ID, with request digest, JSON result and expiry.
**Contract:** `PostgresNonceStore.claim_result` inserts the operation result and all nonce claims in the same transaction. A retry with the same operation ID and request digest returns the stored result; a different digest under the same operation ID returns a conflict; a nonce conflict rolls back the new result and all new claims. Stored results expire no later than the shortest nonce/attestation expiry.
**Authorization integration:** `authorize_commit_intent` uses `claim_result` when the provided store implements it. The request digest binds the intent ID, evidence IDs and policy fields. Legacy stores implementing only `claim_many` retain fail-closed replay protection, without result recovery.
**Verification:** CI run 38115316244 passed for implementation commit 4fec4740b70bc57b58655acae49da9139348b756, including the live PostgreSQL 16 integration suite.
**Limitations:** this persists authorization decisions only; it does not execute a change or guarantee idempotency of downstream side effects. Production readiness still requires deployment-specific migration management, database security, observability, backup and failure testing.


## Iteration 21 — retry and concurrency verification for idempotent authorization
**Goal:** verify that an authorization decision remains stable when the client loses commit confirmation, concurrent callers retry the same operation, or the same operation ID is presented with different policy input.
**Integration coverage:** (1) simulate a committed result whose confirmation is lost, then retry and recover the persisted decision; (2) run eight concurrent authorization calls for the same intent and require the same authorized result with one persisted result/nonce; (3) reject reuse of the same operation ID/intent with a changed policy digest.
**Fix discovered by tests:** the authorization preflight previously required claim_many even when a store implemented the stronger atomic claim_result contract. Validation now accepts a store implementing either callable method and rejects stores implementing neither. This allows result-only atomic stores to reach the idempotent result path.
**Verification:** initial test commit c389d4e90748ed2e3f22b8a977975300b29a9724 exposed the interface mismatch (CI run 38120530034 failed: 1 failed, 186 passed). Fix commit a99bb7f10d0cd5224778452a37f4fb79dd9aed5d passed CI run 38121526379; the build, package installation, and full test step completed successfully.
**Limitations:** these tests validate the adapter and authorization behavior against the ephemeral PostgreSQL service in CI. They do not establish production deployment readiness or idempotency of external side effects; the package still records decisions and does not execute the authorized change.
