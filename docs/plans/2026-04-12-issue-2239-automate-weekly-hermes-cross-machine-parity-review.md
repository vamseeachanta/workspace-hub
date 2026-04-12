# Plan for #2239: automate weekly Hermes cross-machine parity review

> Status: draft
> Complexity: T2
> Date: 2026-04-12
> Issue: https://github.com/vamseeachanta/workspace-hub/issues/2239
> Review artifacts: scripts/review/results/2026-04-12-plan-2239-claude.md | scripts/review/results/2026-04-12-plan-2239-codex.md | scripts/review/results/2026-04-12-plan-2239-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `config/scheduled-tasks/schedule-tasks.yaml` — canonical source of truth for scheduled automation; weekly jobs already exist for `ai-tools-status`, `model-ids`, `skills-curation`, and `provider-session-ecosystem-audit`, so #2239 should be implemented as another YAML-declared task rather than an ad-hoc cron entry.
- Found: `docs/ops/scheduled-tasks.md` — operator-facing schedule inventory already documents weekly jobs and machine roles; #2239 must update this document alongside YAML so the scheduled task is discoverable.
- Found: `scripts/cron/setup-cron.sh` is referenced by both the issue and docs as the installer; because cron is YAML-driven, the plan should validate that no direct installer edit is needed unless the dry-run output shows a gap.
- Found: `scripts/readiness/harness-config.yaml` — existing Hermes health checks already cover binary/config/patch/external-skills parity and can provide evidence inputs for the weekly parity job.
- Gap: no `weekly-parity` script or task exists anywhere under `scripts/cron/` or current schedule declarations.

### Standards
| Standard | Status | Source |
|---|---|---|
| Control-plane adapter model | done | `docs/standards/CONTROL_PLANE_CONTRACT.md` |
| Hard-stop policy for non-engineering harness work | not applicable to implementation gate, but planning still mandatory | `docs/standards/HARD-STOP-POLICY.md` |

### LLM Wiki pages consulted
- No relevant wiki pages found; this is harness/operations work anchored in repo docs and configs rather than domain wiki content.

### Documents consulted
- `docs/ops/hermes-weekly-cross-machine-parity-checklist.md` — defines the weekly evidence contract the automation should operationalize: Hermes settings review, Linux/macOS parity, Windows frontier-model repo-ecosystem parity, output capture, and follow-on issue rules.
- `docs/ops/scheduled-tasks.md` — confirms existing weekly cadence windows and machine-role table; suggests Monday/Sunday weekly slot is acceptable and that `ace-linux-1` / `dev-primary` is the full cron host.
- `config/scheduled-tasks/schedule-tasks.yaml` — shows the task schema (`id`, `schedule`, `machines`, `requires`, `command`, `log`, `description`) and existing weekly patterns to mirror.
- `scripts/readiness/harness-config.yaml` — identifies Hermes managed checks already available for reuse (`binary_exists`, `venv_import`, `patch_applied`, `external_skills_dir`, `config_managed_keys`).
- Related issue #2089 — governance/cadence parent for weekly review.
- Related issue #1583 — canonical Hermes baseline-definition issue that the weekly parity job should reference in findings.
- Related issue #2094 — multi-machine readiness matrix issue that overlaps with evidence modeling and should be referenced rather than duplicated.

### Gaps identified
- No executable weekly parity review script exists.
- No dated artifact destination under `logs/` exists yet for weekly parity summaries.
- No schedule entry currently installs a weekly parity review job.
- No templated follow-on issue emission exists for parity drift findings.

<!-- Verification: distinct sources >= 3. Current count: 7 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-12-issue-2239-automate-weekly-hermes-cross-machine-parity-review.md` |
| Implementation script | `scripts/cron/weekly-hermes-parity-review.sh` |
| Schedule config | `config/scheduled-tasks/schedule-tasks.yaml` |
| Operator docs | `docs/ops/scheduled-tasks.md` |
| Output logs | `logs/weekly-parity/*.md` or `logs/weekly-parity/*.yaml` |
| Tests | `tests/work-queue/test-weekly-hermes-parity-review.sh` |
| Plan review — Claude | `scripts/review/results/2026-04-12-plan-2239-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-12-plan-2239-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-12-plan-2239-gemini.md` |

---

## Deliverable

A weekly scheduled parity-review workflow that reads the canonical Hermes checklist, collects machine-by-machine evidence, writes a dated weekly artifact, and integrates cleanly with the repo’s YAML-driven scheduling system.

---

## Pseudocode

```text
main():
    load machine inventory and Hermes managed-key expectations
    derive weekly output path under logs/weekly-parity/
    collect local dev-primary evidence (versions, config drift, skills visibility)
    collect remote evidence for reachable Linux/macOS hosts using existing access assumptions
    record Windows status using best available local/bridge artifacts when direct reach is unavailable
    classify findings as pass / drift / unreachable / blocked
    render summary artifact with per-machine sections and follow-on issue recommendations
    optionally post a concise summary comment to #2089 when running in scheduled mode
    exit non-zero only for script errors, not for ordinary machine drift findings
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/cron/weekly-hermes-parity-review.sh` | implement the weekly evidence collection and summary generation |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | declare the new weekly task in the canonical scheduler source |
| Modify | `docs/ops/scheduled-tasks.md` | document the new weekly task, cadence, and output log path |
| Create | `tests/work-queue/test-weekly-hermes-parity-review.sh` | shell-level regression coverage for artifact generation / graceful failure behavior |
| Update | `docs/plans/README.md` | add this plan to the index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_weekly_parity_script_writes_dated_artifact` | script creates a dated output artifact in the expected directory | temp workspace + mocked commands | one `logs/weekly-parity/*` file exists |
| `test_weekly_parity_script_marks_unreachable_machine_nonfatal` | unreachable remote host is reported but does not crash the run | mocked ssh failure for one host | artifact contains `unreachable` and script exits 0 |
| `test_schedule_yaml_declares_weekly_parity_task` | schedule includes the new task with required fields | updated YAML | validator passes and dry-run renders the entry |
| `test_summary_includes_issue_links_and_follow_on_guidance` | output links #1583 / #2089 and preserves follow-on guidance | generated artifact | issue references and follow-on section present |

---

## Acceptance Criteria

- [ ] New regression tests pass: `bash tests/work-queue/test-weekly-hermes-parity-review.sh`
- [ ] Schedule schema remains valid: `uv run --no-project python scripts/cron/validate-schedule.py`
- [ ] Cron installer renders the new task: `bash scripts/cron/setup-cron.sh --dry-run | grep weekly-hermes-parity-review`
- [ ] Manual script run writes a dated weekly artifact under `logs/weekly-parity/`
- [ ] Script handles at least one unreachable machine without aborting the entire review
- [ ] `docs/ops/scheduled-tasks.md` documents the new task and artifact path
- [ ] Plan review artifacts are posted before implementation begins

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR | inventory source is incomplete; Windows evidence interface undefined; v1 scope must explicitly defer auto issue creation |
| Codex | MAJOR | checklist machine set does not match canonical registry/readiness sources; output retention/commenting/evidence interfaces underspecified |
| Gemini | MINOR | add macOS + second Windows coverage to readiness source, define SSH timeout behavior, and avoid v1 issue-spam automation |

**Overall result:** FAIL (re-draft required before implementation)

Revisions made based on review:
- none yet — plan must be revised to define canonical machine inventory, explicit Windows evidence inputs, timeout behavior, and narrower v1 GitHub automation scope before re-review

---

## Risks and Open Questions

- Risk: Windows machines lack SSH and may require bridge artifacts or manual evidence ingestion rather than direct command execution.
- Risk: macOS host reachability may be intermittent, so the first implementation should treat it as optional evidence rather than a hard failure.
- Risk: auto-creating follow-on GitHub issues from cron could create noise if severity thresholds are not explicit.
- Open: should the first version auto-comment on #2089 every run, or only when drift is detected?
- Open: should weekly artifacts be Markdown, YAML, or both for human + machine consumption?

---

## Complexity: T2

**T2** — this is a bounded multi-file harness automation change touching one new script, one schedule declaration, docs, and regression coverage, but it does not require architecture-level decomposition.
