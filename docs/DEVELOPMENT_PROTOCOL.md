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

For each iteration record:
- iteration number and goal;
- contract and changed files;
- tests and exact results;
- security/integrity considerations;
- known limitations;
- commit SHA and next bounded step.

## Iteration 1 — complete

Context, architecture layers, invariants and development gates are documented. No infrastructure was represented as deployed.

## Iteration 2 — implementation submitted; CI evidence pending

**Goal:** establish the first executable vertical slice: Genesis → Relation → AgentState.

**Contract:** immutable versioned values; non-empty string boundary validation; stable SHA-256 identifiers over canonical JSON; directed relations; AgentState identity anchored to a Genesis identifier; no network/database dependencies.

**Acceptance:** positive, invalid-input, immutability, identity sensitivity and determinism tests; package builds; CI runs on pushes and pull requests.

**Verification status:** source and tests are committed, but runtime test/build results must be read from GitHub Actions before declaring this iteration verified.
