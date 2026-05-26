# Plan Review — #2801 — Claude r3 (adversarial, DELTA on D1/D2/D3 only)

**Scope:** the post-r2 user decisions D1 (cadence), D2 (declared-baseline conformance), D3 (behavior probe in v1). Codex r2 never saw these.
**Verdict:** MAJOR (1 MAJOR + 3 MINOR) on the delta.

## MAJOR
- **D1-1 — "weekly cron" wiring covers only dev-primary.** `scripts/cron/weekly-hermes-parity-review.sh` is in ace-linux-1's crontab. Wiring the collector there means ONLY dev-primary self-reports; ace-linux-2 + the Windows machines never refresh → matrix permanently MISSING-EVIDENCE for them. Self-report must run on EACH machine's own scheduler. Recommended reconciliation: invoke the collector from `nightly-readiness.sh` (which ALREADY runs per-machine on every machine) gated by commit-on-change — this delivers per-machine coverage AND the user's no-churn goal (commit-on-change solves churn regardless of run frequency). NOTE: this refines the user's literal "weekly" choice → "nightly-checked, commit-only-on-change"; surface for confirmation, do not silently override.

## MINOR
- **D2-1 — baseline `required_data_access` may name repos the collector never probes.** Collector checks a FIXED tier1 set (assetutilities, digitalmodel, worldenergydata, assethold). If a machine's `required_data_access` lists a repo outside that set, conformance can never be satisfied. Fix: validate `required_data_access ⊆ collector-probed-repos` at matrix build; mismatch → MISSING-BASELINE/config-error, not BELOW-BASELINE.
- **D2-2 — compute_floor comparison needs numeric coercion.** Collector emits `ram_total: "31Gi"` (string). Floor compare must parse to int; a parse failure must → MISSING-EVIDENCE, not a silent false CONFORMS/BELOW. Add coercion + a parse-failure test.
- **D3-1 — b5 settings_permissions_hash is a cross-platform false-divergence trap.** Hashing settings.json without canonicalization → Windows CRLF vs Linux LF (and key ordering) produce different hashes for identical policy → false DIVERGES. Fix: parse JSON, sort keys, strip insignificant whitespace, force LF, THEN sha256. Also verify b1 (plan-approval-gate.sh) has a side-effect-free invocation path (no log append / no write); if unverifiable → emit n/a.

## Checked (not defective)
- NO-MAJORITY tie logic now only applies to uniform dims (cold dims use conformance) — internally consistent.
- Serialization allowlist (C4) still holds for the new behavior/baseline fields (hashes + enums only).
