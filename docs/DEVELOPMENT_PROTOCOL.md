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

## Iteration 2 — complete

**Goal:** establish the first executable vertical slice: Genesis → Relation → AgentState.

**Contract:** immutable versioned values; non-empty string boundary validation; stable SHA-256 identifiers over canonical JSON; directed relations; AgentState identity anchored to a Genesis identifier; no network/database dependencies.

**Verification:** GitHub Actions passed for commit `1a331050b09ad9b8926a0730a736fa0597f688db`. The workflow builds and installs the package and runs the test suite.

## Iteration 3 — implementation submitted; CI evidence pending

**Goal:** implement Φ Structure as a validated snapshot over Genesis, AgentState and Relation.

**Contract:** structure identity is deterministic and independent of input ordering; states share the supplied Genesis; subject IDs and record IDs are unique; every directed relation endpoint resolves to a subject in the snapshot; returned collections are immutable tuples.

**Acceptance:** positive, invalid-type, foreign-Genesis, dangling-endpoint, duplicate-subject, immutability and deterministic-order tests. CI must pass before this iteration is marked complete.

**Known limits:** identifiers are content-derived hashes, not proof of real-world identity, authorization or authenticity. Timestamp strings are required to be non-empty but are not yet parsed or normalized to a strict UTC format.
