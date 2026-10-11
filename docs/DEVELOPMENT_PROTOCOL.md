# Step-by-step Development Protocol

## Iteration cycle

1. **Context:** inspect target repository, reference implementation, current branch/head, existing modules and infrastructure.
2. **Contract:** state purpose, input/output, invariants, failure behavior, trust boundary and acceptance criteria.
3. **Implementation:** change one bounded module or vertical slice.
4. **Review:** inspect diff for scope, security, compatibility and unnecessary dependencies.
5. **Tests:** add positive, negative, edge-case and determinism/integrity tests as relevant.
6. **Verification:** run the relevant test suite and checks; record exact commands/results. Never claim checks that were not run.
7. **Integration:** connect to dependent modules only after the contract and tests pass.
8. **Documentation:** update architecture, usage and operational state.
9. **Commit:** create a small, descriptive commit after verification; avoid mixing unrelated iterations.
10. **Observation and learning:** review runtime signals, failures and evidence before starting the next iteration.

## Iteration gates

- Do not skip a failing gate; fix and rerun it.
- Do not build dependent modules on a failing or ambiguous contract.
- Keep infrastructure adapters separate from core domain logic.
- Use fakes/local services for deterministic tests; require explicit environment configuration for real external services.
- Do not store credentials in code, tests, logs, commits or example configuration.
- A deployment claim requires actual deployment and runtime health evidence.

## Standard evidence

For each iteration record the goal, contract, changed files, tests and exact results, integrity considerations, limitations, commit SHA and next bounded step.

## Iteration 1 — complete

Context, architecture layers, invariants and development gates are documented. No infrastructure was represented as deployed.

## Iteration 2 — complete

**Goal:** establish the first executable vertical slice: Genesis → Relation → AgentState.

**Verification:** GitHub Actions passed for commit `1a331050b09ad9b8926a0730a736fa0597f688db`.

## Iteration 3 — complete

**Goal:** implement Φ Structure as a validated snapshot over Genesis, AgentState and Relation.

**Contract:** structure identity is deterministic and independent of input ordering; states share the supplied Genesis; subject IDs and record IDs are unique; every directed relation endpoint resolves to a subject in the snapshot; returned collections are immutable tuples.

**Verification:** GitHub Actions passed for commit `112db354f15669ecd9233b2391788011d9ba52c5` (run 38109576077).

## Iteration 4 — implementation submitted; CI verification pending

**Goal:** implement Ω Pohyb as an immutable record of a state transition.

**Contract:** both states must be AgentState records for the same subject and Genesis; their identifiers must differ; cause must be non-empty; movement identity is deterministic from the transition fields. Recording a movement does not mutate state, execute an agent, authorize the transition or persist data.

**Acceptance:** valid transition, deterministic identity, invalid types, cross-subject/cross-Genesis transitions, no-op transition, empty cause and immutability tests.

**Known limits:** state records contain identifiers and timestamps, not a full state payload. Movement is a transition record, not a transition engine or proof of authorization. Timestamps remain non-empty strings and are not parsed/normalized as strict UTC.
