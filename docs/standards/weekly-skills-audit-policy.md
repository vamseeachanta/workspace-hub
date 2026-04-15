# Weekly skills audit policy

Authoritative source: `config/skills/weekly-audit-policy.yaml`

This document explains the v1 policy contract for weekly skills-audit output. If this document ever conflicts with the YAML file, the YAML file wins.

## Purpose

The weekly audit is meant to produce low-noise, deterministic maintenance signals for the skills ecosystem. It is not a license for broad taxonomy redesign, bulk renames, or automatic merges.

## Signal vocabulary

The YAML locks a small machine-readable signal vocabulary so #2281 does not invent classification inputs ad hoc. The main signals are:

- `same_canonical_name`
- `same_primary_intent`
- `wrapper_redirect`
- `explicit_canonical_target`
- `substantial_overlap`
- `distinct_deliverable_surface`
- `generic_leaf_only`
- `maintained_replacement_exists`
- `conflicting_evidence`
- `insufficient_evidence`

Each classification bucket in YAML declares `match_all`, `match_any`, and `exclude_if_any` conditions against these signals.

## Bucket intent

- `exact-duplicate`: same canonical intent, strong consolidation signal
- `canonical-wrapper-pair`: thin pointer to a canonical skill, not a merge candidate
- `near-duplicate-same-intent`: likely duplicate but not proven enough for automatic action
- `adjacent-specialization`: related skills that should remain separate
- `generic-leaf-collision`: naming/path collision without same-intent proof
- `stale-superseded`: older skill replaced by a maintained canonical successor
- `needs-human-review`: ambiguity remains after deterministic rules are applied

## Precedence

The precedence order is intentionally explicit and single-winner. If multiple buckets appear plausible, the first matching bucket in the YAML precedence list wins. If evidence is still ambiguous, route the finding to `needs-human-review`.

## Ranking

The YAML also locks deterministic ranking behavior so #2281 does not invent its own ordering. Weekly sections appear in this order:

1. `new_findings`
2. `changed_findings`
3. `unresolved_high_confidence_findings`
4. `suppressed_carry_forward_findings`
5. `operational_errors_or_skipped_inputs`

Within a section, findings sort by the YAML contract in this order:
- `escalation_state` (`candidate` before `no-escalation`)
- `severity` (`high`, `medium`, `low`)
- `confidence` (`high`, `medium`, `low`)
- `is_new` (newer first)
- `finding_key` ascending as the deterministic final tie-breaker

## Carry-forward behavior

Unchanged findings should be compacted into carry-forward output instead of resurfacing as headline churn. A finding that remains unresolved but changes materially must appear in `changed_findings`.

## Escalation

v1 uses a binary escalation model only:
- `no-escalation`
- `candidate`

The YAML rules define when a finding becomes a `candidate` versus staying `no-escalation`, and repeated weekly runs must keep the same escalation state unless the evidence changes materially.
