2026-04-12T10:08:48.576286Z ERROR codex_core_skills::loader: failed to stat skills entry /mnt/local-analysis/workspace-hub/.claude/skills/skills (symlink): No such file or directory (os error 2)
OpenAI Codex v0.120.0 (research preview)
--------
workdir: /mnt/local-analysis/workspace-hub
model: gpt-5.4
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR, /home/vamsee/.codex/memories]
reasoning effort: medium
reasoning summaries: none
session id: 019d812a-79f3-79e2-a312-323d034133c0
--------
user
# Final Lightweight Plan Re-Review — Issue #2239

This is a final lightweight adversarial re-review after a third targeted redraft.
Focus only on whether the previously remaining blockers are now sufficiently closed for plan approval.

Remaining blockers from prior round:
- explicit non-SSH evidence mapping, especially `licensed-win-2`
- checklist vs registry mismatch handling for `macbook-portable`
- default-no-comment test coverage

## Current revised plan

     1|# Plan for #2239: automate weekly Hermes cross-machine parity review
     2|
     3|> Status: draft
     4|> Complexity: T2
     5|> Date: 2026-04-12
     6|> Issue: https://github.com/vamseeachanta/workspace-hub/issues/2239
     7|> Review artifacts: scripts/review/results/2026-04-12-plan-2239-claude.md | scripts/review/results/2026-04-12-plan-2239-codex.md | scripts/review/results/2026-04-12-plan-2239-gemini.md
     8|
     9|---
    10|
    11|## Resource Intelligence Summary
    12|
    13|### Existing repo code
    14|- Found: `config/scheduled-tasks/schedule-tasks.yaml` — canonical source of truth for scheduled automation; weekly jobs already exist for `ai-tools-status`, `model-ids`, `skills-curation`, and `provider-session-ecosystem-audit`, so #2239 should be implemented as another YAML-declared task rather than an ad-hoc cron entry.
    15|- Found: `docs/ops/scheduled-tasks.md` — operator-facing schedule inventory already documents weekly jobs and machine roles; #2239 must update this document alongside YAML so the scheduled task is discoverable.
    16|- Found: `scripts/cron/setup-cron.sh` is referenced by both the issue and docs as the installer; because cron is YAML-driven, the plan should validate that no direct installer edit is needed unless the dry-run output shows a gap.
    17|- Found: `scripts/readiness/harness-config.yaml` — existing Hermes health checks already cover binary/config/patch/external-skills parity and can provide evidence inputs for the weekly parity job.
    18|- Gap: no `weekly-parity` script or task exists anywhere under `scripts/cron/` or current schedule declarations.
    19|
    20|### Standards
    21|| Standard | Status | Source |
    22||---|---|---|
    23|| Control-plane adapter model | done | `docs/standards/CONTROL_PLANE_CONTRACT.md` |
    24|| Hard-stop policy for non-engineering harness work | not applicable to implementation gate, but planning still mandatory | `docs/standards/HARD-STOP-POLICY.md` |
    25|
    26|### LLM Wiki pages consulted
    27|- No relevant wiki pages found; this is harness/operations work anchored in repo docs and configs rather than domain wiki content.
    28|
    29|### Documents consulted
    30|- `docs/ops/hermes-weekly-cross-machine-parity-checklist.md` — defines the weekly evidence contract the automation should operationalize: Hermes settings review, Linux/macOS parity, Windows frontier-model repo-ecosystem parity, output capture, and follow-on issue rules.
    31|- `docs/ops/scheduled-tasks.md` — confirms existing weekly cadence windows and machine-role table; suggests Monday/Sunday weekly slot is acceptable and that `ace-linux-1` / `dev-primary` is the full cron host.
    32|- `config/scheduled-tasks/schedule-tasks.yaml` — shows the task schema (`id`, `schedule`, `machines`, `requires`, `command`, `log`, `description`) and existing weekly patterns to mirror.
    33|- `config/workstations/registry.yaml` — canonical workstation inventory currently includes Linux and Windows hosts, but not `macbook-portable`; v1 parity automation must treat registry as the authoritative machine set plus explicitly documented exceptions.
    34|- `scripts/readiness/harness-config.yaml` — identifies Hermes managed checks already available for reuse (`binary_exists`, `venv_import`, `patch_applied`, `external_skills_dir`, `config_managed_keys`) but is not sufficient as the sole inventory source.
    35|- Related issue #2089 — governance/cadence parent for weekly review.
    36|- Related issue #1583 — canonical Hermes baseline-definition issue that the weekly parity job should reference in findings.
    37|- Related issue #2094 — multi-machine readiness matrix issue that overlaps with evidence modeling and should be referenced rather than duplicated.
    38|- Related issue #2240 — macOS parity scaffolding issue that should establish registry/readiness support before #2239 assumes macOS evidence can be collected automatically.
    39|
    40|### Gaps identified
    41|- No executable weekly parity review script exists.
    42|- No dated artifact destination under `logs/` exists yet for weekly parity summaries.
    43|- No schedule entry currently installs a weekly parity review job.
    44|- No templated follow-on issue emission exists for parity drift findings.
    45|
    46|<!-- Verification: distinct sources >= 3. Current count: 7 -->
    47|
    48|---
    49|
    50|## Artifact Map
    51|
    52|| Artifact | Path |
    53||---|---|
    54|| This plan | `docs/plans/2026-04-12-issue-2239-automate-weekly-hermes-cross-machine-parity-review.md` |
    55|| Implementation script | `scripts/cron/weekly-hermes-parity-review.sh` |
    56|| Schedule config | `config/scheduled-tasks/schedule-tasks.yaml` |
    57|| Operator docs | `docs/ops/scheduled-tasks.md` |
    58|| Output logs | `logs/weekly-parity/*.md` or `logs/weekly-parity/*.yaml` |
    59|| Tests | `tests/work-queue/test-weekly-hermes-parity-review.sh` |
    60|| Plan review — Claude | `scripts/review/results/2026-04-12-plan-2239-claude.md` |
    61|| Plan review — Codex | `scripts/review/results/2026-04-12-plan-2239-codex.md` |
    62|| Plan review — Gemini | `scripts/review/results/2026-04-12-plan-2239-gemini.md` |
    63|
    64|---
    65|
    66|## Deliverable
    67|
    68|A weekly scheduled parity-review workflow that reads the canonical Hermes checklist, collects direct evidence for supported machines, renders explicit `blocked`/`unsupported` status for machines without a defined evidence interface, writes a dated weekly artifact, and integrates cleanly with the repo’s YAML-driven scheduling system.
    69|
    70|### V1 machine/evidence contract
    71|- `dev-primary` / `ace-linux-1`: direct local probes
    72|- `dev-secondary` / `ace-linux-2`: timeout-wrapped SSH probes
    73|- `licensed-win-1`: explicit readiness/bridge artifact at `.claude/state/harness-readiness-licensed-win-1.yaml`
    74|- `licensed-win-2`: reported as `blocked` in v1 until a canonical artifact path/report contract exists
    75|- `macbook-portable`: reported as `unsupported` or `blocked` in v1 until #2240 lands canonical registry/readiness support
    76|
    77|V1 must never silently skip an in-scope machine.
    78|
    79|---
    80|
    81|## Pseudocode
    82|
    83|```text
    84|main():
    85|    load machine inventory from config/workstations/registry.yaml
    86|    load Hermes managed-key expectations from scripts/readiness/harness-config.yaml
    87|    derive weekly output path under logs/weekly-parity/
    88|    collect local dev-primary evidence (versions, config drift, skills visibility)
    89|    collect remote evidence for reachable Linux/macOS hosts using timeout-wrapped SSH probes
    90|    ingest Windows evidence from explicit bridge/readiness artifact paths when direct reach is unavailable
    91|    classify each machine as pass / drift / unreachable / blocked / unsupported
    92|    render summary artifact with per-machine sections and follow-on recommendations
    93|    optionally post a concise summary comment to #2089 only when an explicit flag enables it
    94|    never auto-create GitHub issues in v1
    95|    exit non-zero only for script errors, not for ordinary machine drift findings
    96|```
    97|
    98|---
    99|
   100|## Files to Change
   101|
   102|| Action | Path | Reason |
   103||---|---|---|
   104|| Create | `scripts/cron/weekly-hermes-parity-review.sh` | implement the weekly evidence collection and summary generation |
   105|| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | declare the new weekly task in the canonical scheduler source |
   106|| Modify | `docs/ops/scheduled-tasks.md` | document the new weekly task, cadence, and output log path |
   107|| Create | `tests/work-queue/test-weekly-hermes-parity-review.sh` | shell-level regression coverage for artifact generation / graceful failure behavior |
   108|| Update | `docs/plans/README.md` | add this plan to the index |
   109|
   110|**Dependencies / non-owned surfaces:**
   111|- `config/workstations/registry.yaml` and `scripts/readiness/harness-config.yaml` should be treated as read-only inputs in #2239 unless #2240 lands first or is explicitly folded into this issue during plan revision.
   112|
   113|
   114|---
   115|
   116|## TDD Test List
   117|
   118|| Test name | What it verifies | Expected input | Expected output |
   119||---|---|---|---|
   120|| `test_weekly_parity_script_writes_dated_artifact` | script creates a dated output artifact in the expected directory | temp workspace + mocked commands | one `logs/weekly-parity/*` file exists |
   121|| `test_weekly_parity_script_marks_unreachable_machine_nonfatal` | unreachable remote host is reported but does not crash the run | mocked ssh failure for one host | artifact contains `unreachable` and script exits 0 |
   122|| `test_weekly_parity_script_ingests_windows_bridge_artifact` | Windows readiness artifact is parsed and surfaced explicitly | mocked `.claude/state/harness-readiness-licensed-win-1.yaml` input | artifact contains Windows machine status |
   123|| `test_weekly_parity_script_marks_licensed_win_2_blocked_without_artifact_contract` | second Windows host is not silently omitted when no canonical artifact path exists | registry includes `licensed-win-2`, no artifact mapping configured | artifact marks `licensed-win-2` as `blocked` |
   124|| `test_weekly_parity_script_marks_checklist_only_macos_blocked_or_unsupported` | checklist/registry mismatch is surfaced honestly | checklist includes `macbook-portable`, registry/readiness support absent | artifact marks macOS as `blocked` or `unsupported` |
   125|| `test_weekly_parity_script_uses_timeout_wrapped_remote_probes` | SSH-based evidence collection cannot hang indefinitely | mocked remote probe call | script exits within timeout path and records timeout state |
   126|| `test_schedule_yaml_declares_weekly_parity_task` | schedule includes the new task with required fields | updated YAML | validator passes and dry-run renders the entry |
   127|| `test_summary_includes_issue_links_and_follow_on_guidance` | output links #1583 / #2089 and preserves follow-on guidance | generated artifact | issue references and follow-on section present |
   128|| `test_missing_evidence_never_counts_as_pass` | unsupported/missing machine evidence is reported honestly | absent macOS/Windows evidence sources | artifact marks machine as `blocked` or `unsupported`, never `pass` |
   129|| `test_github_commenting_respects_explicit_flag` | commenting stays off by default and only runs when explicitly enabled | scheduled run with and without comment flag | no comment by default; comment only when flag set |
   130|
   131|
   132|---
   133|
   134|## Acceptance Criteria
   135|
   136|- [ ] New regression tests pass: `bash tests/work-queue/test-weekly-hermes-parity-review.sh`
   137|- [ ] Schedule schema remains valid: `uv run --no-project python scripts/cron/validate-schedule.py`
   138|- [ ] Cron installer renders the new task: `bash scripts/cron/setup-cron.sh --dry-run | grep weekly-hermes-parity-review`
   139|- [ ] Manual script run writes a dated weekly artifact under `logs/weekly-parity/`
   140|- [ ] Script handles at least one unreachable machine without aborting the entire review
   141|- [ ] Script treats unsupported/missing machine evidence as `blocked` or `unsupported`, never `pass`
   142|- [ ] Windows evidence source(s) are explicitly defined and covered by tests before automation claims Windows parity
   143|- [ ] GitHub commenting is either explicitly feature-flagged for v1 or deferred from v1 scope
   144|- [ ] `docs/ops/scheduled-tasks.md` documents the new task and artifact path
   145|- [ ] Plan review artifacts are posted before implementation begins
   146|
   147|---
   148|
   149|## Adversarial Review Summary
   150|
   151|| Provider | Verdict | Key findings |
   152||---|---|---|
   153|| Claude | MAJOR | inventory source is incomplete; Windows evidence interface undefined; v1 scope must explicitly defer auto issue creation |
   154|| Codex | MAJOR | rerun still finds non-SSH evidence mapping underspecified, especially `licensed-win-2` / checklist-registry mismatch handling |
   155|| Gemini | APPROVE with MINOR | rerun accepts bounded v1 scope but asks for comment-flag test and cleanup of stale review-state text |
   156|
   157|**Overall result:** FAIL after rerun (re-draft still required before implementation)
   158|
   159|Revisions made based on review:
   160|- first revision incorporated canonical registry inventory, timeout-wrapped probes, explicit Windows bridge-artifact ingestion, and v1 deferral of auto-issue creation
   161|- second revision defines the v1 machine/evidence contract explicitly (`licensed-win-1` supported, `licensed-win-2` blocked until canonical artifact path exists, `macbook-portable` unsupported/blocked until #2240 lands), adds registry/checklist mismatch tests, and adds an explicit default-no-comment test
   162|
   163|---
   164|
   165|## Risks and Open Questions
   166|
   167|- Risk: Windows machines lack SSH and may require bridge artifacts or manual evidence ingestion rather than direct command execution.
   168|- Risk: macOS host reachability may be intermittent, so the first implementation should treat it as optional evidence rather than a hard failure.
   169|- Risk: auto-creating follow-on GitHub issues from cron could create noise if severity thresholds are not explicit.
   170|- Open: should the first version auto-comment on #2089 every run, or only when drift is detected?
   171|- Open: should weekly artifacts be Markdown, YAML, or both for human + machine consumption?
   172|
   173|---
   174|
   175|## Complexity: T2
   176|
   177|**T2** — this is a bounded multi-file harness automation change touching one new script, one schedule declaration, docs, and regression coverage, but it does not require architecture-level decomposition.
   178|

## Review questions
1. Are the prior blockers now explicitly handled?
2. Is the plan now approval-ready, or does any MAJOR blocker remain?
3. If not approval-ready, what single blocking gap remains?

## Required output
- Verdict: APPROVE, MINOR, or MAJOR
- Remaining blocker(s)
- Short rationale
warning: Codex's Linux sandbox uses bubblewrap and needs access to create user namespaces.
codex
Verdict: APPROVE

Remaining blocker(s)
- None.

Short rationale
- `licensed-win-2` is now explicitly handled via a non-SSH evidence decision: it is not silently skipped, and v1 requires it to be reported as `blocked` until a canonical artifact contract exists. That closes the prior evidence-mapping blocker.
- `macbook-portable` mismatch handling is now explicit: the plan states registry is authoritative plus documented exceptions, assigns `macbook-portable` to `blocked`/`unsupported` until #2240, and adds a test for checklist-only coverage. That closes the registry/checklist blocker.
- Default-no-comment behavior is now covered in both logic and tests through the explicit flag model and `test_github_commenting_respects_explicit_flag`. That closes the test-coverage blocker.

The plan is approval-ready. The only residual issue is editorial: the adversarial review summary still says `FAIL after rerun`, which should be updated when the plan status is promoted, but that is not a MAJOR blocker.
tokens used
112,075
Verdict: APPROVE

Remaining blocker(s)
- None.

Short rationale
- `licensed-win-2` is now explicitly handled via a non-SSH evidence decision: it is not silently skipped, and v1 requires it to be reported as `blocked` until a canonical artifact contract exists. That closes the prior evidence-mapping blocker.
- `macbook-portable` mismatch handling is now explicit: the plan states registry is authoritative plus documented exceptions, assigns `macbook-portable` to `blocked`/`unsupported` until #2240, and adds a test for checklist-only coverage. That closes the registry/checklist blocker.
- Default-no-comment behavior is now covered in both logic and tests through the explicit flag model and `test_github_commenting_respects_explicit_flag`. That closes the test-coverage blocker.

The plan is approval-ready. The only residual issue is editorial: the adversarial review summary still says `FAIL after rerun`, which should be updated when the plan status is promoted, but that is not a MAJOR blocker.
