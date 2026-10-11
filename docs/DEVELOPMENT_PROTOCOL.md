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

## Iteration 6 — ΦΩ² Resonance complete

**Goal:** implement ΦΩ² Resonance as a deterministic coherence snapshot across a structure and linked memory records.

**Contract:** every memory entry shares the structure Genesis and refers to a represented subject. Historical entries may end at prior states; each chain tip matches the current structure state. Referenced predecessor entries are included and form a contiguous chain. Entry IDs are unique and canonical ordering makes resonance identity independent of input ordering.

**Acceptance:** coherent chain, order-independent deterministic identity, invalid types, foreign Genesis, terminal-state mismatch, missing predecessor, duplicate entries and immutability.

**CI correction:** the initial implementation incorrectly required every historical entry to end at the current state. Validation was corrected to check the current state only at chain tips. Corrected CI passed in run 38109920516 for commit 02a9996bf93a3b689c5f9845a87211f2730d32c4.

**Known limits:** this validates supplied metadata only. It does not authenticate signatures, prove causality, provide external persistence or calculate semantic resonance.


## Iteration 7 — Γ Convergence complete

**Goal:** create a deterministic decision record for a proposal based on explicit verification checks.

**Contract:** required check IDs must be unique and non-empty. Check records must be typed, unique and limited to the declared required set. A proposal is accepted only if every required check is present and passing; missing or failed checks reject it. Canonical ordering makes the result independent of input order.

**Trust boundary:** check status and evidence digests are supplied claims. This module does not authenticate evidence, run checks, interpret semantics, execute proposals or activate changes.

**Acceptance:** complete passing checks, missing check, failed check, deterministic order independence, duplicate/unrequested checks, invalid types and immutability.


**CI result:** run 38110020640 passed for commit f357d7a4669ae464d1b51d6faf8bc57145de8a4f.

## Iteration 8 — Π Meaning implementation submitted; CI verification pending

**Goal:** represent an explicit interpretation linked to check records in a convergence decision.

**Contract:** the interpretation must be non-empty and cite at least one unique basis check ID that exists in the referenced convergence. Basis IDs are canonicalized, so their input order does not affect the meaning identifier. Interpretations can describe accepted or rejected proposals.

**Trust boundary:** this layer validates references only. It does not establish that an interpretation is true, high quality, authored by a trusted actor, or semantically correct.

**Acceptance:** valid evidence references, deterministic identity, order independence, interpretation of rejected outcomes, invalid convergence, empty interpretation/basis, duplicate/unknown basis IDs and immutability.
