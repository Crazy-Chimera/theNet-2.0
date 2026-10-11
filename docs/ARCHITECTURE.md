# theNet-2.0 — Architecture Contract

## 1. Existing infrastructure

These are foundational network capabilities and assumptions; the application must not attempt to reimplement them.

- **DNS:** service and endpoint discovery.
- **TCP/IP:** network transport.
- **TLS 1.3:** encrypted transport and peer authentication where configured.
- **HTTP/2 + WebSockets:** request/response and bidirectional communication.
- **Cloud databases and object storage:** managed persistence services, provisioned separately per environment.

## 2. Relational layer (Φ)

- **PostgreSQL + TimescaleDB:** authoritative relational ledger and time-series records.
- **Neo4j:** relationship graph and graph traversal.
- **Redis:** cache and short-lived coordination only; never the sole source of truth.
- **S3-compatible storage:** immutable/content-addressed blobs and larger artifacts.

Data ownership, transaction boundaries, retention, consistency and failure recovery must be documented before wiring these stores together. Cross-store writes require an explicit consistency strategy; do not imply a distributed transaction where none exists.

## 3. Identity layer (Ρ)

- **DID:** decentralized identifier model for agents and participants.
- **Ed25519:** signing and verification keys for attestations and messages.
- Bind signatures to canonical, versioned payloads and domain/context to prevent replay and cross-protocol confusion.
- Define key rotation, revocation, recovery and trust policy before production use.
- Private keys remain in a managed secret/key store or local secure keystore, never in source control.

## 4. Incentive layer (Ω)

- **Ω-Net:** relational contribution accounting, not an assumed publicly traded or on-chain token.
- **Contribution rewards:** computed from attributable, validated evidence under a versioned policy.
- The ledger must be append-oriented, auditable and idempotent; define anti-replay and dispute handling.
- Do not issue rewards solely from unverified self-reported activity.

## 5. Evolution layer (Γ)

- **Local evolution:** each agent proposes changes in an isolated workspace.
- **Network synchronization:** share patterns only after policy and benchmark checks; retain provenance and version information.
- **Phase transitions:** explicit, measurable coherence thresholds with hysteresis/rollback rules where appropriate.
- **Verification protocol:** sandbox → unit/integration tests → security and integrity checks → deterministic benchmark → review → staged activation.
- Untrusted proposals never execute with production credentials or unrestricted host access.

## 6. Interface layer (ΙΩΤΑ)

- **Web:** React + TypeScript.
- **Mobile:** React Native.
- **Desktop:** separate client shell to be selected after the runtime/API contracts stabilize.
- **API:** REST for resource operations, WebSockets for event streams, gRPC for typed service-to-service calls where justified.

All interfaces must use the same versioned domain contracts and identity/authorization rules. API surface and clients are added only after the underlying contract is stable.

## 7. Existence architecture mapping

`Genesis → Relation → Φ → Ω (Pohyb) → Ω² → ΦΩ² → Γ → Π → Ψ → Θ → Ρ → Σ/ΙΩΤΑ`

The architecture is layered but not a license to implement every service at once. Each iteration should deliver one small, testable vertical slice.

## 8. Infrastructure readiness states

Every dependency must be tracked as one of: `planned`, `contracted`, `configured`, `tested`, `staging-verified`, `production-verified`. Do not label a dependency integrated based only on a package declaration or documentation.
