# theNet-2.0

**Status: Iteration 15 — policy-gated authorization decision complete; CI passed (run 38111295066, 163 tests).**

theNet-2.0 implements a relational, evolutionary network architecture while keeping infrastructure integrations explicit and verifiable.

## Architectural sequence

Genesis → Relation → Φ Structure → Ω Pohyb → Ω² Memory → ΦΩ² Resonance → Γ Convergence → Π Meaning → Ψ Expression → Θ Self-Knowledge → Ρ Relational Co-definition → Σ / ΙΩΤΑ closure → prepared evolution → identity and evidence verification → policy-gated authorization decision.

## Current executable slice

The thenet_core package provides immutable records and deterministic identifiers for Genesis, Relation, AgentState, Structure, Pohyb, MemoryEntry, Resonance, Convergence, Meaning, Expression, SelfKnowledge, CoDefinition, Closure and CommitIntent. Ed25519 attestations verify canonical signed claims under a supplied local trust policy.

AuthorizationPolicy and AuthorizationDecision evaluate whether a prepared intent is bound to valid signed evidence and allowed action, target, context and issuer policy. Evidence is re-verified during the decision and its digest must bind the exact intent ID, action, target, identity binding and proposed-change digest. The decision is a record only; it does not execute changes.

The core does not connect to databases, network services, DID registries or key stores. Trust policy and key-map provenance remain external. A successful authorization decision is not proof of real-world identity, proposal truth, secure policy distribution, persistent nonce replay prevention or verified closure provenance. Secrets and private keys must never be committed.

## Platform layers

1. Infrastructure: DNS, TCP/IP, TLS 1.3, HTTP/2, WebSockets and managed/cloud storage.
2. Relational layer: PostgreSQL + TimescaleDB, Neo4j, Redis and S3-compatible storage (target architecture).
3. Identity layer: decentralized identifiers and Ed25519 key pairs.
4. Incentive layer: relational accounting and verifiable contribution rewards.
5. Evolution layer: local evolution, verified-pattern synchronization, coherence thresholds, sandboxing and benchmarks.
6. Interface layer: React + TypeScript web app, React Native mobile app, desktop client, REST/WebSocket/gRPC APIs.

These are target architecture choices, not a claim that services are provisioned or connected.

## Development

- Reference implementation: https://github.com/Crazy-Chimera/theNet
- Target repository: https://github.com/Crazy-Chimera/theNet-2.0
- Development protocol: docs/DEVELOPMENT_PROTOCOL.md
- Architecture contract: docs/ARCHITECTURE.md
- Context and invariants: docs/CONTEXT.md
