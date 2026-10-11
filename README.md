# theNet-2.0

**Status: Iteration 9 — Ψ Expression implemented; CI verification pending.**

theNet-2.0 is an implementation of a relational, evolutionary network architecture, following the existing `Crazy-Chimera/theNet` project while keeping infrastructure integrations explicit and verifiable.

## Architectural sequence

Genesis → Relation → Φ Structure → Ω Pohyb → Ω² Memory → ΦΩ² Resonance → Γ Convergence → Π Meaning → Ψ Expression → Θ Self-Knowledge → Ρ Relational Co-definition → Σ / ΙΩΤΑ closure.

## Current executable slice

The `thenet_core` package implements:
- `Genesis`: immutable origin record with deterministic identifier.
- `Relation`: immutable directed relation with deterministic identifier.
- `AgentState`: immutable state record anchored to a Genesis identifier.
- `Structure`: deterministic snapshot validating state ancestry, unique subjects and relation endpoints.
- `Movement`: immutable transition record between distinct states of the same subject and Genesis.
- `MemoryEntry`: immutable metadata linking a movement into a per-subject state chain; stores a payload digest rather than raw payload.
- `Resonance`: deterministic coherence snapshot binding a structure to memory entries whose Genesis, subject, chain continuity and terminal state at each chain tip validate.
- `VerificationCheck` and `Convergence`: deterministic accept/reject decision from explicit required checks; missing or failed checks reject a proposal.
- `Meaning`: a declared interpretation linked to existing convergence check records; it does not elevate interpretation into fact.
- `Expression`: immutable output metadata bound to a Meaning and a content digest; raw content is not retained and no delivery is performed.
- Canonical JSON and SHA-256 identity derivation.
- Automated positive, invalid-input, immutability, integrity and determinism tests.

The domain core has no runtime dependencies and does not connect to databases, network services, DID registries or key stores.

## Platform layers

1. Existing infrastructure: DNS, TCP/IP, TLS 1.3, HTTP/2, WebSockets and managed/cloud storage.
2. Relational layer (Φ): PostgreSQL + TimescaleDB ledger, Neo4j graph, Redis cache and S3-compatible blob storage.
3. Identity layer (Ρ): decentralized identifiers (DID) and Ed25519 key pairs.
4. Incentive layer (Ω): Ω-Net relational accounting and verifiable contribution rewards.
5. Evolution layer (Γ): local agent evolution, synchronization of verified patterns, coherence thresholds, sandboxing and benchmarks.
6. Interface layer (ΙΩΤΑ): React + TypeScript web app, React Native mobile app, desktop client, REST/WebSocket/gRPC APIs.

These are target architecture choices, not a claim that every service is already provisioned or connected. Each integration must be introduced in its own iteration with configuration, contracts, tests and operational verification. Secrets and private keys must never be committed.

## Development

- Reference implementation: [Crazy-Chimera/theNet](https://github.com/Crazy-Chimera/theNet)
- Target repository: [Crazy-Chimera/theNet-2.0](https://github.com/Crazy-Chimera/theNet-2.0)
- Development protocol: `docs/DEVELOPMENT_PROTOCOL.md`
- Architecture contract: `docs/ARCHITECTURE.md`
- Context and invariants: `docs/CONTEXT.md`

Convergence evaluates supplied check records only. Meaning validates references to those records, not the truth or semantics of the interpretation. Expression binds intended output metadata to a Meaning but does not dispatch it or prove delivery. These modules do not authenticate evidence, execute proposals, or activate changes. No runtime or infrastructure integration is considered complete until its tests and verification evidence are recorded.
