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
