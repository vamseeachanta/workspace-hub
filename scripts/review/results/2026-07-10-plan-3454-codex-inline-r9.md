# Codex inline adversarial review r9 — public plan #3454

- Reviewed artifact SHA-256: `b9cea055330775d1ded2653715b202c745eb0d8a54ad309743b408af088af74c`
- Verdict: **MAJOR**
- Posture: exact-SHA defect hunt; no edits, staging, approval, or implementation authority

## Findings

1. Inherited lock, manifest, live settings-root, and probe-root descriptors leaked from Bash to unrelated descendants. That could extend the lock lifetime and expose live descriptors to subject tests; the design needs a supervising process plus per-child FD allowlists.
2. The legal deny-map remained a mutable reopened path even though prose claimed one retained input across subject/final scans.
3. The lifecycle sequence omitted the explicit `status:plan-review` transition and ambiguously placed the user-created approval marker after approval.
4. The paired structured-review lane had no independently landed protocol-capable dispatcher owner; a subject verifier could not safely authenticate its own review evidence.

## Disposition

The lifecycle wording is revised. The generalized independent review trust root, provider layout, retained-input, canonical-lock, FD allowlist, and parity/redaction work is promoted to [#3467](https://github.com/vamseeachanta/workspace-hub/issues/3467). This plan remains blocked and will not advance until that dependency lands and a new exact revision replaces the provisional executable fence.
