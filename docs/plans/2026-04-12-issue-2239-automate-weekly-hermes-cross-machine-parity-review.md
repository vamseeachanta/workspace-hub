# Plan for #2239: automate weekly Hermes cross-machine parity review

> Status: adversarial-reviewed
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
- `config/workstations/registry.yaml` — canonical workstation inventory currently includes Linux and Windows hosts, but not `macbook-portable`; v1 parity automation must treat registry as the authoritative machine set plus explicitly documented exceptions.
- `scripts/readiness/harness-config.yaml` — identifies Hermes managed checks already available for reuse (`binary_exists`, `venv_import`, `patch_applied`, `external_skills_dir`, `config_managed_keys`) but is not sufficient as the sole inventory source.
- Related issue #2089 — governance/cadence parent for weekly review.
- Related issue #1583 — canonical Hermes baseline-definition issue that the weekly parity job should reference in findings.
- Related issue #2094 — multi-machine readiness matrix issue that overlaps with evidence modeling and should be referenced rather than duplicated.
- Related issue #2240 — macOS parity scaffolding issue that should establish registry/readiness support before #2239 assumes macOS evidence can be collected automatically.

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

A weekly scheduled parity-review workflow that reads the canonical Hermes checklist, collects direct evidence for supported machines, renders explicit `blocked`/`unsupported` status for machines without a defined evidence interface, writes a dated weekly artifact, and integrates cleanly with the repo’s YAML-driven scheduling system.

### V1 machine/evidence contract
- `dev-primary` / `ace-linux-1`: direct local probes
- `dev-secondary` / `ace-linux-2`: timeout-wrapped SSH probes
- `licensed-win-1`: explicit readiness/bridge artifact at `.claude/state/harness-readiness-licensed-win-1.yaml`
- `licensed-win-2`: reported as `blocked` in v1 until a canonical artifact path/report contract exists
- `macbook-portable`: reported as `unsupported` or `blocked` in v1 until #2240 lands canonical registry/readiness support

V1 must never silently skip an in-scope machine.

---

## Pseudocode

```text
main():
    load machine inventory from config/workstations/registry.yaml
    load Hermes managed-key expectations from scripts/readiness/harness-config.yaml
    derive weekly output path under logs/weekly-parity/
    collect local dev-primary evidence (versions, config drift, skills visibility)
    collect remote evidence for reachable Linux/macOS hosts using timeout-wrapped SSH probes
    ingest Windows evidence from explicit bridge/readiness artifact paths when direct reach is unavailable
    classify each machine as pass / drift / unreachable / blocked / unsupported
    render summary artifact with per-machine sections and follow-on recommendations
    optionally post a concise summary comment to #2089 only when an explicit flag enables it
    never auto-create GitHub issues in v1
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

**Dependencies / non-owned surfaces:**
- `config/workstations/registry.yaml` and `scripts/readiness/harness-config.yaml` should be treated as read-only inputs in #2239 unless #2240 lands first or is explicitly folded into this issue during plan revision.


---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_weekly_parity_script_writes_dated_artifact` | script creates a dated output artifact in the expected directory | temp workspace + mocked commands | one `logs/weekly-parity/*` file exists |
| `test_weekly_parity_script_marks_unreachable_machine_nonfatal` | unreachable remote host is reported but does not crash the run | mocked ssh failure for one host | artifact contains `unreachable` and script exits 0 |
| `test_weekly_parity_script_ingests_windows_bridge_artifact` | Windows readiness artifact is parsed and surfaced explicitly | mocked `.claude/state/harness-readiness-licensed-win-1.yaml` input | artifact contains Windows machine status |
| `test_weekly_parity_script_marks_licensed_win_2_blocked_without_artifact_contract` | second Windows host is not silently omitted when no canonical artifact path exists | registry includes `licensed-win-2`, no artifact mapping configured | artifact marks `licensed-win-2` as `blocked` |
| `test_weekly_parity_script_marks_checklist_only_macos_blocked_or_unsupported` | checklist/registry mismatch is surfaced honestly | checklist includes `macbook-portable`, registry/readiness support absent | artifact marks macOS as `blocked` or `unsupported` |
| `test_weekly_parity_script_uses_timeout_wrapped_remote_probes` | SSH-based evidence collection cannot hang indefinitely | mocked remote probe call | script exits within timeout path and records timeout state |
| `test_schedule_yaml_declares_weekly_parity_task` | schedule includes the new task with required fields | updated YAML | validator passes and dry-run renders the entry |
| `test_summary_includes_issue_links_and_follow_on_guidance` | output links #1583 / #2089 and preserves follow-on guidance | generated artifact | issue references and follow-on section present |
| `test_missing_evidence_never_counts_as_pass` | unsupported/missing machine evidence is reported honestly | absent macOS/Windows evidence sources | artifact marks machine as `blocked` or `unsupported`, never `pass` |
| `test_github_commenting_respects_explicit_flag` | commenting stays off by default and only runs when explicitly enabled | scheduled run with and without comment flag | no comment by default; comment only when flag set |


---

## Acceptance Criteria

- [ ] New regression tests pass: `bash tests/work-queue/test-weekly-hermes-parity-review.sh`
- [ ] Schedule schema remains valid: `uv run --no-project python scripts/cron/validate-schedule.py`
- [ ] Cron installer renders the new task: `bash scripts/cron/setup-cron.sh --dry-run | grep weekly-hermes-parity-review`
- [ ] Manual script run writes a dated weekly artifact under `logs/weekly-parity/`
- [ ] Script handles at least one unreachable machine without aborting the entire review
- [ ] Script treats unsupported/missing machine evidence as `blocked` or `unsupported`, never `pass`
- [ ] Windows evidence source(s) are explicitly defined and covered by tests before automation claims Windows parity
- [ ] GitHub commenting is either explicitly feature-flagged for v1 or deferred from v1 scope
- [ ] `docs/ops/scheduled-tasks.md` documents the new task and artifact path
- [ ] Plan review artifacts are posted before implementation begins

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | APPROVE with MINOR | latest draft closes the v1 machine/evidence contract; remaining work is editorial state cleanup only |
| Codex | APPROVE | final lightweight rerun confirms non-SSH mapping, checklist/registry handling, and default-no-comment coverage are now explicit |
| Gemini | APPROVE | final lightweight rerun confirms all prior blockers are resolved |

**Overall result:** PASS — ready for user approval

Revisions made based on review:
- first revision incorporated canonical registry inventory, timeout-wrapped probes, explicit Windows bridge-artifact ingestion, and v1 deferral of auto-issue creation
- second revision defined the v1 machine/evidence contract explicitly (`licensed-win-1` supported, `licensed-win-2` blocked until canonical artifact path exists, `macbook-portable` unsupported/blocked until #2240 lands), added registry/checklist mismatch tests, and added an explicit default-no-comment test
- final lightweight rerun from Codex and Gemini approved the plan with no remaining MAJOR blockers

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
