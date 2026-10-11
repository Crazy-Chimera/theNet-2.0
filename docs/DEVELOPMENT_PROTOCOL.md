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

## Iterations 1–5 — complete

Iterations 1–2 documented the architecture and established Genesis → Relation → AgentState. Iteration 2 CI passed for `1a331050b09ad9b8926a0730a736fa0597f688db`.

Iteration 3 implemented Φ Structure; CI passed for `112db354f15669ecd9233b2391788011d9ba52c5` (run 38109576077).

Iteration 4 implemented Ω Pohyb; CI passed for `d5ddd2ef42b8dfc093f68dc88b36817e1d115849` (run 38109681779).

Iteration 5 implemented Ω² Memory; CI passed for `36663f2ec7f0a05b7d3ab02147bfd575018ca438` (run 38109761052).

## Iteration 6 — implementation submitted; CI verification pending

**Goal:** implement ΦΩ² Resonance as a deterministic coherence snapshot across a structure and linked memory records.

**Contract:** every memory entry must share the structure Genesis, refer to a represented subject, and end at that subject's current state. Referenced predecessor entries must be included and form a contiguous chain. Entry IDs are unique and canonical ordering makes resonance identity independent of input ordering.

**Acceptance:** coherent chain, order-independent deterministic identity, invalid types, foreign Genesis, terminal-state mismatch, missing predecessor, duplicate entries and immutability.

**Known limits:** this validates supplied metadata only. It does not authenticate signatures, prove causality, provide external persistence or calculate semantic resonance.
