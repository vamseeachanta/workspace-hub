# Codex inline adversarial review r8 — public plan #3454

- Reviewed artifact SHA-256: `02e19c4f4b309c0cc0e9cd6fff29dca39b3d56a393b7eea11f596b5855011ee3`
- Verdict: **MAJOR**
- Posture: defect-hunting; no edits, staging, approval, or implementation authority

## Findings

1. The bootstrap described launcher behavior without fully binding the exact launcher/manifest bytes that would establish the runtime root of trust.
2. The driver accepted a caller-supplied regular lock FD without proving it named the fixed canonical lock leaf, so independent callers could hold distinct locks.
3. Recovery required a caller-preseeded nonce instead of deriving the nonce from the sole validated existing candidate/receipt pair under the canonical lock.
4. The plan called the manifest one-read while helpers reopened/reparsed a mutable path; the claim exceeded the actual hash-bound behavior.
5. Cross-authority acceptance required entire plans to match exactly even though privacy redaction intentionally makes that impossible; only shared contract/state blocks can be byte-identical.
6. Public/private state ownership was contradictory: public verification persisted bounded candidate/receipt refs while prose assigned all persistence to the opaque authority.

## Disposition in working v9

The revision binds a pinned manifest and launcher bootstrap, proves the inherited lock FD equals the canonical no-follow leaf, derives recovery nonces under that lock, uses one fully sealed manifest byte source with hash-bound FD duplication, narrows parity to shared blocks, and separates bounded public handoff refs from private cross-repo persistence. Fresh exact-artifact review is still required.
