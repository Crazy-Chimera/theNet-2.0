# theNet-2.0

**Status: Iteration 1 — architecture and development contract.**

theNet-2.0 is the next implementation of a relational, evolutionary network architecture, following the existing `Crazy-Chimera/theNet` project while keeping infrastructure integrations explicit and verifiable.

## Architectural sequence

Genesis → Relation → Φ Structure → Ω Pohyb → Ω² Memory → ΦΩ² Resonance → Γ Convergence → Π Meaning → Ψ Expression → Θ Self-Knowledge → Ρ Relational Co-definition → Σ / ΙΩΤΑ closure.

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

No runtime or infrastructure integration is considered complete until its tests and verification evidence are recorded.
