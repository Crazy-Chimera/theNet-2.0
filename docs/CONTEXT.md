# theNet-2.0 — Context and Invariants

## Purpose

Build theNet-2.0 iteratively on the relational architecture and tested engineering conventions of `Crazy-Chimera/theNet`. Preserve conceptual continuity while making implementation state, infrastructure readiness, security boundaries and verification evidence explicit.

## Existence architecture

1. Genesis
2. Relation
3. Φ Structure
4. Ω Pohyb
5. Ω² Memory
6. ΦΩ² Resonance
7. Γ Convergence
8. Π Meaning / Contribution
9. Ψ Expression
10. Θ Self-Knowledge
11. Ρ Relational Co-definition
12. Σ + ΙΩΤΑ closure
13. Prepared commit intent for verified evolution

The foundational closure is followed by verified system evolution. Preparing an intent does not itself authorize or apply the change.

## Core loop

`RELATION → STATE → OBSERVE → INTERPRET → PROPOSE → SIMULATE → VERIFY → CONVERGE → COMMIT → MEMORY → LEARNING → REDEFINE SYSTEM`

Central invariant:

`Identity(t+1) ≈ Identity(t) + verified evolution`

This is an engineering invariant for continuity of identity under verified change, not a claim that a conceptual equation is experimentally established physics.

## Platform context

The intended platform layers and their responsibilities are defined in `ARCHITECTURE.md`. Listing a technology means it is an intended integration, not proof that it has been deployed, configured or security-reviewed.

## Engineering conventions

- Inspect repository state and reference implementation before modifying files.
- Use “pohyb” rather than “dynamika”.
- Prefer deterministic behavior, immutable domain values and canonical serialization where useful.
- Keep core domain logic independent of network services and vendor-specific clients.
- Keep secrets, credentials, private keys and production data out of Git.
- Treat external inputs as untrusted and validate them at boundaries.
- No agent-proposed change becomes active without tests, policy checks and explicit verification.
- Avoid adding dependencies before a concrete contract requires them.

## Completion criteria

A module is complete only when its contract, implementation, positive/negative/edge tests, relevant determinism and integrity checks, integration checks, and verification record agree. A passing unit test alone does not prove production readiness.

## Relational co-definition boundary

A shared definition contains explicit contributions attributed to distinct declared contributor IDs. Each contribution references a SelfKnowledge record and retains only a content digest. "Agreed" means all supplied assent flags are true; "disputed" means at least one is false. Both remain unverified records until a separate identity, authorization and evidence-verification layer is implemented.

## Σ / ΙΩΤΑ closure boundary

A closure snapshot integrates Genesis, Structure, Resonance, Convergence, Meaning, Expression, SelfKnowledge and CoDefinition only when their declared references agree. The closure records proposal decision and contributor agreement separately and always remains `unverified`. It proves referential coherence within the supplied records, not external authenticity, execution, activation, deployment or metaphysical unity.

## Prepared commit-intent boundary

A CommitIntent can be created only from a closure whose supplied convergence decision is accepted and whose declared co-definition assent is unanimous. It binds the action, target, proposed-change digest and SelfKnowledge identifier. Its status is always `prepared` and authorization is always `not_authorized`; it cannot execute changes, mutate state or create Git commits. The acceptance and assent gates are caller-supplied records and are not external authentication.
\n\n## Iteration 14 — signed attestation boundary\n\nAttestations sign canonical, versioned claims containing issuer ID, subject ID, context, SHA-256 payload digest, issue/expiry timestamps, nonce and key ID. Verification checks the Ed25519 signature against a caller-supplied trust entry, issuer/key match, permitted context, revocation flag and UTC validity window. A verified result authenticates the signed bytes under the supplied local policy; it does not establish real-world identity or claim truth. Trust-store integrity, key rotation/recovery, persistent nonce replay detection, authorization and execution remain outside this module.\n