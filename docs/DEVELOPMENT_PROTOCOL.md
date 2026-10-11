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

**CI result:** run 38110020640 passed for commit f357d7a4669ae464d1b51d6faf8bc57145de8a4f.

## Iteration 8 — Π Meaning complete

**Goal:** represent an explicit interpretation linked to check records in a convergence decision.

**Contract:** the interpretation must be non-empty and cite at least one unique basis check ID that exists in the referenced convergence. Basis IDs are canonicalized, so their input order does not affect the meaning identifier. Interpretations can describe accepted or rejected outcomes.

**Trust boundary:** this layer validates references only. It does not establish that an interpretation is true, high quality, authored by a trusted actor, or semantically correct.

**CI result:** run 38110123950 passed for commit 9533b5b2d0f2004581d5c6528918b88b411b6a43.

## Iteration 9 — Ψ Expression complete

**Goal:** represent a deterministic output artifact that is explicitly bound to a declared Meaning.

**Contract:** an Expression requires a Meaning plus non-empty channel, format and content. It stores a SHA-256 content digest rather than raw content. Its deterministic identifier binds the Meaning ID, intended channel, format, digest and schema version.

**Trust boundary:** the record describes intended output only. It does not dispatch content, authenticate the referenced Meaning, or prove delivery, receipt or acceptance.

**CI result:** run 38110210904 passed for commit 68dc818e8d89cd74272b365d578da843707ec0fc.

## Iteration 10 — Θ Self-Knowledge complete

**Goal:** create a deterministic self-model snapshot tied to a known Expression.

**Contract:** the self-model text is represented by a SHA-256 digest. The record includes canonicalized, unique capability declarations and requires at least one explicit limitation. Its ID binds the Expression, Meaning, model digest, capability claims, limitation claims and schema version.

**Trust boundary:** declarations are caller-supplied. The module does not prove that capabilities exist, that limitations are complete, that the system is conscious, or that self-modification is authorized.

**CI result:** run 38110302464 passed for commit 97571730549a933d8d1673252151a92546712969.

## Iteration 11 — Ρ Relational Co-definition complete

**Goal:** represent a shared definition assembled from explicitly attributed contributions.

**Contract:** a co-definition requires non-empty context and at least two contributions from distinct contributor IDs. Each contribution links to a SelfKnowledge snapshot, stores a digest of its content, and records explicit assent. Contributions are canonically ordered. Agreement is "agreed" only when all assents; otherwise it is "disputed". Verification status remains "unverified".

**Trust boundary:** contributor IDs and assent are supplied declarations. The module does not authenticate identities, establish legal authority, verify contribution truth, or infer consent beyond the explicit boolean supplied.

**CI result:** run 38110404811 passed for commit 8c1035f18ac79b94b79baa622d335e9fc290b175.

## Iteration 12 — Σ / ΙΩΤΑ closure complete

**Goal:** integrate the implemented existence-architecture layers into one deterministic closure snapshot.

**Contract:** Genesis, Structure, Resonance, Convergence, Meaning, Expression, SelfKnowledge and CoDefinition must be correctly typed and reference one another consistently. The co-definition must include the supplied SelfKnowledge record. Proposal decision and contributor agreement remain separate fields. The closure is always marked "unverified".

**Trust boundary:** this is a cross-reference integrity check over supplied immutable records. It does not authenticate identities or evidence, prove semantics, execute or activate proposals, provision infrastructure, or establish metaphysical unity.

**Acceptance:** valid full-chain binding, deterministic identity, wrong types, mismatched Genesis/structure/resonance/convergence/meaning/expression/self-model references, missing co-definition provenance, disputed agreement, immutability and no external-verification or activation claim.

**CI result:** run 38110619932 passed for commit 506b3bbb01dcd7c4e078fa4d77a4c87e7b6caf7b. Two earlier runs exposed test-fixture/assertion issues, which were corrected before this passing run (131 tests passed).

## Iteration 13 — Prepared commit intent complete

**Goal:** represent a deterministic, bounded intent for a proposed system change without granting execution authority.

**Contract:** the intent must bind to a Closure whose supplied convergence decision is accepted and whose declared co-definition assent is unanimous. It binds the Closure ID, SelfKnowledge identity binding, action, target and SHA-256 digest of proposed change content. The status is always "prepared" and authorization is always "not_authorized".

**Trust boundary:** convergence checks and assent are caller-supplied claims; closure is unverified. This module does not authenticate identities/evidence, authorize or execute changes, mutate state, or create Git commits.

**Acceptance:** valid prepared intent, deterministic identity, action/target/change binding, invalid types and empty fields, rejected convergence, disputed assent, immutability and no execution/authorization claims.


**CI result:** run 38110703374 passed for commit 010acfc162f2681c8896c8bb0059adfc92546cc6. The workflow completed package build, installation and the full test suite successfully.
\n\n## Iteration 14 — Ed25519 signed attestation\n\n**Goal:** verify signed claims against an explicitly supplied local trust policy before later authorization is considered.\n\n**Contract:** sign canonical versioned claims binding issuer, subject, context, payload digest, issue/expiry times, nonce and key ID. Verification checks signature, configured issuer/key match, permitted context, revocation state and validity window at an explicit UTC instant.\n\n**Trust boundary:** the trust map is supplied by the caller. A successful signature check does not establish real-world identity, payload truth, secure trust-store distribution or persistent anti-replay. Authorization and execution are not included.\n\n**Acceptance:** valid signature, wrong key, unknown key, issuer mismatch, revoked key, disallowed context, expired/not-yet-valid claims, tampered signed claims, malformed input and immutability. CI verification pending.\n