# Tier-1 Indexing Freshness Audit — Contract

> **Issue:** [#2465](https://github.com/vamseeachanta/workspace-hub/issues/2465)
> **Plan:** `docs/plans/2026-04-22-issue-2465-daily-tier1-indexing-freshness-audit.md`
> **Implementation:** `scripts/cron/tier1-indexing-freshness.sh`
> **Latest report:** `docs/reports/tier-1-indexing-freshness-latest.md`
> **Upstream rule source:** `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md`

This contract defines the **daily** local audit that keeps tier-1 routing/indexing surfaces honest. It is the sustaining loop for the upstream contract `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md`. The audit only **reports**; remediation lives in the per-repo child issues #2461–#2464.

The audit runs locally with no network calls. It uses curated routing surfaces only and never treats raw inventory (`docs/CONTENT_INDEX.md`, etc.) as authority. MUST NOT treat any tier-1 indexing scorecard under docs/reports/ as required canonical authority.

## Scope

In scope:

- Daily presence check of the canonical routing triad (`AGENTS.md`, `README.md`, `docs/README.md`) for each tier-1 repo.
- Daily presence check of the operator map (`docs/maps/<repo>-operator-map.md`) and the canonical machine-readable registry (`docs/registry/module-routing.yaml`) for each tier-1 repo.
- Source-hygiene drift detection (tracked backup artifacts under each repo's source roots).
- Legacy-reference drift detection (broken active references in the canonical routing triad and operator map).
- Daily refresh of `docs/reports/tier-1-indexing-freshness-latest.md` and a dated snapshot under `docs/reports/tier-1-indexing-freshness-YYYY-MM-DD.md`.
- Emission of one cron-health evidence line per #2291 contract.

Out of scope:

- Any modification to tier-1 source code (this is the per-repo issues' job).
- Network calls, remote crawls (`/mnt/ace/data`, `/mnt/local-analysis/`), and any external service.
- Stricter enforcement (CI gate, pre-commit hook). Layered later once the per-repo remediations stabilize.
- Authority to override the upstream contract `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md`.

## Inputs

| Input | Source | Failure mode |
|---|---|---|
| Tier-1 repo set | `docs/BUSINESS_BRAIN.md` `### Tier-1` table | If the heading is missing or unparseable, exit 2 with `reason=brain-missing` |
| Required surface list | `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md` | If the contract file is missing, exit 2 with `reason=contract-missing` (no internal copy of the rule set) |
| Per-repo scan-roots | This contract's `## Per-Repo Scan-Root Table` | If a row is missing, the audit treats that repo as `red` and notes the omission |
| Today's date stamp | `date -u +%Y-%m-%d`, override via `TIER1_FRESHNESS_TODAY` env | None |
| Optional cadence registration | `data/document-index/freshness-cadences.yaml` (#2105) | None — citation-only when the asset_type is registered elsewhere |

## Per-Repo Checks

For each tier-1 repo from `docs/BUSINESS_BRAIN.md`:

1. **Required surfaces present** — every entry in the upstream contract's _Required Trusted Routing Surfaces_ table must exist:
   - `AGENTS.md`
   - `README.md`
   - `docs/README.md`
   - `docs/maps/<repo>-operator-map.md`
   - `docs/registry/module-routing.yaml`
2. **Source-hygiene drift** — no tracked backup artifacts (`*.bak`, `*.orig`, `*~`, `*.swp`) exist under the per-repo scan-roots listed in the table below.
3. **Legacy-reference drift** — every active reference inside the canonical routing triad (`AGENTS.md`, `README.md`, `docs/README.md`) and the operator map must resolve to an existing path in the repo. Migration notes and explicit retirement notes are exempted by being in code-fenced blocks tagged with `legacy` (per upstream contract's `Legacy Product-Doc Retirement Rule`).

Per-repo status:

| Status | Condition |
|---|---|
| green | all required surfaces present, no source-hygiene drift, no broken active references |
| yellow | exactly one required surface missing, or minor drift (one source-hygiene artifact, or one broken reference) |
| red | two or more required surfaces missing, OR tracked backup artifact under source paths in any tracked location, OR a broken active reference cited as a current canonical surface |

## Per-Repo Scan-Root Table

The audit script walks the following paths to check source-hygiene drift. Paths are **relative to the workspace-hub root**; every cell is a directory the audit reads but never writes.

| Repo | Scan-roots | Skipped subtrees |
|---|---|---|
| workspace-hub | `scripts/`, `config/`, `docs/`, `.claude/skills/`, `.claude/rules/` | `.git/`, `node_modules/`, `.venv/`, `__pycache__/`, `logs/` |
| digitalmodel | `digitalmodel/src/`, `digitalmodel/digitalmodel/`, `digitalmodel/scripts/`, `digitalmodel/tests/` | `digitalmodel/.git/`, `digitalmodel/.venv/`, `digitalmodel/__pycache__/`, `digitalmodel/.pytest_cache/` |
| assetutilities | `assetutilities/src/`, `assetutilities/assetutilities/`, `assetutilities/scripts/`, `assetutilities/tests/` | `assetutilities/.git/`, `assetutilities/.venv/`, `assetutilities/__pycache__/` |
| aceengineer-website | `aceengineer-website/src/`, `aceengineer-website/content/`, `aceengineer-website/scripts/` | `aceengineer-website/.git/`, `aceengineer-website/node_modules/`, `aceengineer-website/.next/` |

If a scan-root does not exist on disk for a repo, that's a finding — the audit reports it, but absence alone is not the same as drift.

## Pass/Fail Thresholds

The audit derives a **portfolio status** from per-repo statuses:

| Portfolio status | Condition |
|---|---|
| green | every tier-1 repo is green |
| yellow | at least one tier-1 repo is yellow and none are red |
| red | at least one tier-1 repo is red, OR the upstream contract file is missing, OR `docs/BUSINESS_BRAIN.md` cannot be parsed |

## Escalation

The audit reports via three exit codes — matching the sibling-cron convention in `scripts/cron/control-plane-drift.sh`:

| Portfolio status | Exit code | Meaning |
|---|---|---|
| green | exit 0 | nothing to do |
| yellow | exit 1 | drift detected, no surface missing |
| red | exit 2 | escalate now: required surface missing, legacy reference present, or upstream contract unavailable |

When the portfolio status is `red`, the report header MUST contain a single-line `Action required: <count> tier-1 repo(s) have missing required surfaces or legacy references. See per-repo findings below.` prefix so a reader sees urgency without live escalation.

The audit emits one cron-health evidence line at end of run (per #2291 contract):

```text
task=tier1-indexing-freshness status=<green|yellow|red> artifact=<path> log=<path> ts=<iso8601>
```

When the upstream contract file is missing, the evidence line additionally carries `reason=contract-missing`.

## Negative-Authority Clause

The audit MUST NOT treat any tier-1 indexing scorecard under docs/reports/ as required canonical authority. Scorecards may be cited as historical attestation but never as the rule source. The rule source is the upstream contract `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md`.

Raw inventory surfaces (e.g., `docs/CONTENT_INDEX.md`) MUST NOT be consumed as canonical routing authority by this audit. The audit confirms routing only through curated routing surfaces.

## Legacy-Pattern Avoidance

The audit's report and the audit script itself MUST NOT contain references to retired product-doc files, retired path fragments, or provider-specific stale navigation surfaces (per `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md` `Legacy Product-Doc Retirement Rule`).

When legacy references are detected in the audited repos, the audit reports them under the affected repo's `Current concerns` and demotes its status — it does not silently include the offending text in the freshness report.

## Routine-Management Appendix

A pre-existing remote scheduler routine `aefef5167f2f` is named in `docs/reports/tier-1-indexing-freshness-latest.md` at cadence `30 3 * * *`. That routine predates the in-repo implementation. The ecosystem pattern for remote scheduler routines is documented in memory (`project_daily_readiness_cron.md` — `daily-readiness` cron pattern, `trig_019GWtRosbZ9rw1HxrGpsvy9`-style routine ids).

Operator playbook for the cut-over from the remote routine to this in-repo audit:

1. **List the remote routine** via the orchestrator's UI or API: search for routine id `aefef5167f2f`.
2. **Disable the remote routine** OR re-point it to invoke `bash scripts/cron/tier1-indexing-freshness.sh` against the workspace-hub clone on the host. Disabling is preferred because the in-repo schedule entry (`config/scheduled-tasks/schedule-tasks.yaml::tier1-indexing-freshness`) covers the cadence on `dev-primary` / `ace-linux-1`.
3. **Verify the cut-over** by checking that `docs/reports/tier-1-indexing-freshness-latest.md` is now refreshed by the in-repo script: the in-repo run writes the report header `_Generated by `scripts/cron/tier1-indexing-freshness.sh`_`. If that footer is absent, the remote routine is still authoring the file.
4. **Confirm the dual-writer cut-over before turning on CI regression** — the freshness staleness regression test is permissive while both writers may produce the artifact; once the remote routine is disabled, the test moves to strict mode.

## Dated-Snapshot Retention Policy

Each run writes a dated snapshot at `docs/reports/tier-1-indexing-freshness-YYYY-MM-DD.md` and overwrites the latest pointer at `docs/reports/tier-1-indexing-freshness-latest.md`. **Today's** dated snapshot is committed alongside `-latest`. Older dated snapshots accumulate on the running host's working tree and are cleaned up opportunistically by housekeeping cron — they are not retroactively committed. This bounds archival debt while keeping the latest pointer reviewable in git.

## Read-Only Discipline

The audit only writes under `docs/reports/` and `logs/freshness/`. It MUST NOT modify any tier-1 source tree. The behavioral test `test_audit_is_read_only_against_tier1_source_trees` in `tests/scripts/cron/test_tier1_indexing_freshness.py` enforces this against a synthetic fixture; live runs additionally rely on the `set -uo pipefail` strict-mode guard plus explicit output-path constraints.

## References

- Upstream rule source: `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md`
- Cron-health evidence-line contract (#2291): `docs/plans/2026-04-15-issue-2291-cron-health-hardening-and-task-evidence-contracts.md`
- Freshness-cadences registry (#2105): `data/document-index/freshness-cadences.yaml` (this audit registers `tier-1-indexing-freshness` as a daily cadence; existing daily cadence entries also apply)
- Sibling-cron convention: `scripts/cron/control-plane-drift.sh`
- Cadence helpers: `scripts/cron/lib/cadence-common.sh`
