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
3. `filesystem_only_inventory`
4. `unresolved_high_confidence_findings`
5. `suppressed_carry_forward_findings`
6. `operational_errors_or_skipped_inputs`

Within a section, findings sort by the YAML contract in this order:
- `escalation_state` (`candidate` before `no-escalation`)
- `severity` (`high`, `medium`, `low`)
- `confidence` (`high`, `medium`, `low`)
- `is_new` (newer first)
- `finding_key` ascending as the deterministic final tie-breaker

## Filesystem-only inventory

#2488 adds a policy-driven `filesystem-inventory` v2 family without adding a new top-level legacy `signal_vocabulary` entry. The YAML contract is:

- `weekly_summary_sections[].id`: `filesystem_only_inventory`
- `ranking_policy.section_order`: `filesystem_only_inventory` immediately after `changed_findings`
- result key: `filesystem_inventory_findings`
- flat v2 rule key: `filesystem-inventory.filesystem-only-active`
- finding classification/rule id: `filesystem-only-active`
- JSON summary key: `inventory_summary`

`inventory_summary.counts` records tracked and filesystem `SKILL.md` totals, active counts, filesystem-only active counts, missing tracked active counts, and archived-only filesystem-only counts. `inventory_summary.paths` separates `filesystem_only_active`, `missing_tracked_active`, and `filesystem_only_archived`; each path object has exactly `path` and `informational`. `_archive` and `_archived` path segments are excluded from active loss-risk by the archive alias family. `_core` and `_internal` are still counted as active loss-risk when filesystem-only, but their path objects carry `informational: true`.

The recurring audit remains report-only: unresolved filesystem-only active findings are high-signal maintenance candidates, not cron failures and not automatic `git add -f` actions.

## Carry-forward behavior

Unchanged findings should be compacted into carry-forward output instead of resurfacing as headline churn. A finding that remains unresolved but changes materially must appear in `changed_findings`.

## Escalation

v1 uses a binary escalation model only:
- `no-escalation`
- `candidate`

The YAML rules define when a finding becomes a `candidate` versus staying `no-escalation`, and repeated weekly runs must keep the same escalation state unless the evidence changes materially.
