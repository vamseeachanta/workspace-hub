# Plan for #1583: Hermes Config Parity via Repo Ecosystem Templates

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-05-13
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/1583
> **Review artifacts:** scripts/review/results/2026-05-13-plan-1583-codex.md; Claude T2 review deferred to morning triage per user routing.

---

## Resource Intelligence Summary

### Existing repo code
- Found: `config/agents/hermes/config.yaml.template` — repo-managed Hermes config template already exists and uses placeholder-based repo paths rather than live `~/.hermes/config.yaml` values.
- Found: `config/agents/hermes/SOUL.md` — repo-backed Hermes runtime persona exists; memory confirms `~/.hermes/SOUL.md` is symlinked to this canonical file on the current workspace.
- Found: `scripts/_core/sync-agent-configs.sh` — Hermes sync logic already exists: renders `__WS_HUB_PATH__`, validates YAML, merges managed keys, preserves machine-local `terminal.backend` and `terminal.cwd`, and skips force overwrite unless requested.
- Found: `scripts/_core/tests/test_sync_agent_helpers.sh` — existing tests cover Hermes placeholder expansion, terminal override preservation, YAML validation failure safety, and no-create behavior on invalid YAML using temporary HOME directories.
- Found: `config/scheduled-tasks/schedule-tasks.yaml` — `harness-update` includes `dev-secondary` and `ace-linux-2` with staggered `01:45` schedule.
- Found: `docs/ops/scheduled-tasks.md` — documents ace-linux-2 / dev-secondary contribute variant and `harness-update` at `01:45 daily`.
- Found: `scripts/cron/weekly-hermes-parity-review.sh` — weekly parity report exists and references governance #2089 plus baseline #1583; it probes local/SSH tool versions and Windows bridge artifacts, but does not yet prove effective Hermes config baseline or sync dry-run parity on every machine.

### Standards
| Standard | Status | Source |
|---|---|---|
| Control-plane contract | applicable | `docs/standards/CONTROL_PLANE_CONTRACT.md` requires root `AGENTS.md` as canonical entry point and provider-specific adapters as non-contradictory extensions. Hermes parity work must keep repo-managed Hermes config as an adapter/baseline, not a replacement for `AGENTS.md`. |
| Scheduled-task source of truth | applicable | `config/scheduled-tasks/schedule-tasks.yaml` lines 1-5 state all cron/task-scheduler entries must be declared there; no direct crontab edits should be treated as canonical. |
| /goal invocation rule | applicable | `.claude/rules/goal-invocation.md` requires fetching #2695 and latest comment, validating catalog entries 1-30, checking plan approval, never self-approving, and surfacing Hermes delegation for execution-heavy work. |

### LLM Wiki pages consulted
- N/A — this is harness/config parity work, not domain-knowledge extraction. The issue-class-specific bundle is Harness/Infra, so the required sources are `CONTROL_PLANE_CONTRACT.md`, `config/agents/`, and `.claude/rules/`.

### Documents consulted
- Issue #1583 — original scope requests Hermes config/SOUL templates, sync script extension, custom skills versioning, ace-linux-2 `harness-update`, memory policy, and scheduled-task docs. Later comments say repo-side baseline is largely implemented; live ace-linux-2 deployment/bootstrap remains the external blocker.
- Issue #2695 — `/goal` catalog confirms Tier 2 #29 `Cross-machine / headless-ops apparatus refit [execution-heavy]`; this matches #1583 and points to Hermes -> Codex as a good execution hand after planning approval. Bootstrap weekly picklist excerpt was fetched and names picks #2694, #2685, #1962, and #2665, with skipped items #2686 and #2656; #1583 is absent, so this run is a user-explicit override rather than scheduled weekly work. The latest #2695 comment also explicitly records that two Hermes background lanes, including #1583, were touching the workspace-hub commit surface and that commit serialization was honored.
- Issue #2089 — weekly Hermes/provider settings review remains open and is the governance/cadence parent for recurring parity drift checks.
- Issue #1582 — Hermes installation/configuration on ace-linux-2 remains open; it is a dependency for live bootstrap verification.
- Issue #1564 — ace-linux-2 crontab sync remains open; it is a dependency for live `harness-update` deployment verification.
- `docs/plans/README.md` — requires plan index row and adversarial review before posting `status:plan-review`.
- `docs/plans/_template-issue-plan.md` — requires embedded evidence, artifact map, TDD list, acceptance criteria, review summary, and risks.

### Gaps identified
- Gap 1: No canonical plan file exists for #1583 under `docs/plans/`; this plan creates it before any additional config-template work.
- Gap 2: Existing repo implementation appears mostly landed, but no approval-gated plan currently reconciles the implemented state, expanded baseline scope, and external-machine blockers.
- Gap 3: `weekly-hermes-parity-review.sh` is a useful start but does not yet prove effective Hermes baseline parity: config template render/merge behavior, `skills.external_dirs`, `custom-skills` disposition, wiki/knowledge path settings, SOUL path, memory snapshot restore/readiness, and sync dry-run output are not summarized per machine.
- Gap 4: ace-linux-2 live deployment remains unverified because #1582 and #1564 are still open; #1583 should not be closed on repo-side evidence alone. Any live-machine parity row without safe non-secret evidence must be classified `unverified`/`blocked`, never `pass`.
- Gap 5: Windows parity is partially represented via bridge artifacts, but licensed-win-2 has no canonical artifact contract in `weekly-hermes-parity-review.sh`; that should be split or explicitly blocked, not silently counted as pass.
- Gap 6: Existing issue #1583 body contains superseded memory-policy language. Comments correct it via #1782, but final closeout should avoid resurrecting the old `do NOT sync memories` policy.
- Gap 7: Original #1583 section C requested `config/agents/hermes/custom-skills/` and sync/copy/symlink to `~/.hermes/skills/`; repo search currently shows no such implemented path. Implementation must either build this explicitly or document why repo-backed `skills.external_dirs` supersedes it, with user-visible acceptance language.
- Gap 8: Later #1583 comments expanded the baseline to include knowledge/wiki path settings (`wiki.path` or equivalent repo-linked knowledge roots). Implementation must include those settings in the baseline doc/report or explicitly classify them as machine-local/out-of-scope with a blocker reason.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-14T03:52:19Z via `gh issue view`):
- `#1583` — OPEN — Hermes config parity via repo ecosystem templates — labels include stale `status:plan-approved` and `status:working` but no local plan file exists; current instruction requires refreshed plan-review gate before further implementation. No issue comment contains explicit pre-authorization to proceed after this refreshed plan, so stop at `status:plan-review` after review. Before label changes, post/preserve a comment that distinguishes prior implementation evidence (including commit 83b4c4a5 and earlier validation comments) from the new refreshed-plan gate; then remove stale higher/execution labels only to prevent accidental execution against old approval, not to erase historical work.
- `#2695` — OPEN — feat(harness): /goal use-case catalog for repo ecosystem (claude+codex+hermes) — catalog contains Tier 2 #29 `Cross-machine / headless-ops apparatus refit [execution-heavy]`. Latest weekly picklist comment fetched via `gh issue view 2695 --comments | tail -220`; #1583 is not listed in PICKLIST or SKIPPED, so the current user request is an explicit override under the rule.
- `#2089` — OPEN — feat(harness): weekly Hermes + AI provider settings review for repo ecosystem.
- `#1582` — OPEN — Install and configure Hermes on ace-linux-2.
- `#1564` — OPEN — Sync crontab on ace-linux-2 from schedule-tasks.yaml.

**File existence / plan search**:
```
$ search_files target=files path=docs/plans pattern='*1583*'
{"total_count": 0}
```

**Goal rule excerpt** (`.claude/rules/goal-invocation.md`):
```
Before invoking /goal or planning-goal/planning-code-goal:
1. Fetch canonical catalog issue #2695 body and latest weekly-picklist comment.
2. Validate requested work against catalog entries 1-30.
3. Check whether the target issue has status:plan-approved.
4. Do not self-apply status:plan-approved.
4.5. For [execution-heavy] or [bidirectional] catalog matches, surface the Hermes delegation option.
```

**Control-plane contract excerpt** (`docs/standards/CONTROL_PLANE_CONTRACT.md`):
```
AGENTS.md is the canonical entry point for every repository.
Provider-specific configuration lives in dedicated directories. These are adapters, not alternatives to AGENTS.md.
Adapters MUST NOT contradict AGENTS.md.
```

**Hermes sync implementation excerpt** (`scripts/_core/sync-agent-configs.sh`):
```
sync_hermes_yaml_config() renders config/agents/hermes/config.yaml.template,
validates YAML, merges managed keys from the template, and preserves
terminal.backend plus terminal.cwd from the existing machine-local config.
```

**Hermes sync test excerpt** (`scripts/_core/tests/test_sync_agent_helpers.sh`):
```
run_hermes_placeholder_and_terminal_test writes a temporary HOME/.hermes/config.yaml
with terminal.backend=remote and terminal.cwd=/custom/path, runs sync-agent-configs.sh,
then asserts those machine-local values are preserved while template timeout and
skills.external_dirs are applied.
```

**Scheduled-task excerpt** (`config/scheduled-tasks/schedule-tasks.yaml`):
```
harness-update schedule_by_machine:
  dev-secondary: "45 1 * * *"
  ace-linux-2: "45 1 * * *"
machines: [dev-primary, ace-linux-1, dev-secondary, ace-linux-2, licensed-win-1, licensed-win-2]
```

**Docs excerpt** (`docs/ops/scheduled-tasks.md`):
```
ace-linux-2 / dev-secondary contribute variant:
01:45 daily | harness-update | AI harness tools update (GStack, Hermes, Superpowers, GSD)
```

**Reproduction proofs**:
- Runtime failure reproduction: N/A — issue is harness/config parity plus external-machine verification, not a single failing unit test.
- Planning-gate reproduction: searched `docs/plans/*1583*`; no plan existed before this file.
- Live config mutation: intentionally not performed; no read/write against live `~/.hermes/config.yaml`, `auth.json`, or `.env` is required for planning.

Distinct source count: 11 (`#1583`, `#2695`, `#2089`, `#1582`, `#1564`, `config/agents/hermes/config.yaml.template`, `config/agents/hermes/SOUL.md`, `scripts/_core/sync-agent-configs.sh`, `scripts/_core/tests/test_sync_agent_helpers.sh`, `config/scheduled-tasks/schedule-tasks.yaml`, `docs/ops/scheduled-tasks.md`, plus `CONTROL_PLANE_CONTRACT.md`).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-13-issue-1583-hermes-config-parity-plan.md` |
| Plan index row | `docs/plans/README.md` |
| Existing Hermes template | `config/agents/hermes/config.yaml.template` |
| Existing Hermes SOUL | `config/agents/hermes/SOUL.md` |
| Existing sync implementation | `scripts/_core/sync-agent-configs.sh` |
| Existing sync tests | `scripts/_core/tests/test_sync_agent_helpers.sh`, `scripts/_core/tests/test_sync_agent_configs.sh` |
| Existing scheduled-task source | `config/scheduled-tasks/schedule-tasks.yaml` |
| Existing scheduled-task docs | `docs/ops/scheduled-tasks.md` |
| Existing weekly parity script | `scripts/cron/weekly-hermes-parity-review.sh` |
| Future parity baseline doc, if approved | `docs/ops/hermes-config-parity.md` |
| Future custom-skills baseline, if approved/not superseded | `config/agents/hermes/custom-skills/` and/or `docs/ops/hermes-config-parity.md` disposition section |
| Future wiki/knowledge path baseline | `docs/ops/hermes-config-parity.md` and, if template-managed, `config/agents/hermes/config.yaml.template` |
| Future weekly parity tests, if script changes | `scripts/cron/tests/test_weekly_hermes_parity_review.py` or existing shell-test harness if preferred |
| Plan review — Codex | `scripts/review/results/2026-05-13-plan-1583-codex.md` |
| Plan review — Claude | Deferred to morning triage per user routing; no Claude verdict artifact exists yet. |

---

## Deliverable

An approval-ready implementation plan that reconciles #1583 with the existing repo-side Hermes parity implementation, defines the remaining baseline/verification work, and blocks final issue closure on explicit ace-linux-2 live bootstrap evidence rather than repo-side assumptions.

After user approval, the implementation deliverable should be a documented and test-backed Hermes parity baseline plus a stronger weekly parity report that can distinguish pass, drift, blocked, and external-machine-unverified states across ace-linux-1, ace-linux-2, and Windows bridge artifacts without mutating live secrets, live Hermes config, or live memory/config directories during dry-run probes.

---

## Pseudocode

```
function render_machine_parity_evidence(machine):
    collect tool versions: hermes, claude, git, uv or platform-specific bridge artifact
    verify repo template files exist and are readable
    collect safe live evidence: file presence, symlink targets, non-secret config keys, and rendered template diff summary with auth/env redacted
    create temp HOME fixture for render/unit probes
    require sync-agent-configs dry-run side-effect fix before any live-HOME dry-run is permitted
    until that fix exists, do not run dry-run against live HOME; classify live dry-run evidence as blocked
    parse sandbox dry-run output for Hermes config, SOUL, memories, skills/external_dirs, custom-skills disposition, and wiki/knowledge path signals
    classify machine as pass only when safe live non-secret evidence is present; otherwise drift, blocked, unreachable, unverified, or unsupported
    never read auth.json, .env, API keys, tokens, or credentials
    write markdown evidence row with source issue links (#1583, #2089, blocker issue if any)

function closeout_guard(issue_1583):
    require repo tests passing
    require weekly parity artifact or explicit blocker comment
    require ace-linux-2 setup-cron verification from #1564 or documented unresolved dependency
    require ace-linux-2 Hermes install/bootstrap verification from #1582 or documented unresolved dependency
    if external-machine evidence missing: do not close; post blocked state and leave status non-completed
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/plans/2026-05-13-issue-1583-hermes-config-parity-plan.md` | Canonical approval-gated plan required before more implementation work. |
| Update | `docs/plans/README.md` | Add plan index row per planning workflow. |
| Create, after approval if missing | `docs/ops/hermes-config-parity.md` | Canonical list of Hermes parity-managed files/settings, machine-local exclusions, secrets policy, custom-skills disposition, wiki/knowledge path disposition, and verification commands. |
| Modify, after approval if needed | `scripts/cron/weekly-hermes-parity-review.sh` | Expand weekly parity evidence beyond versions to include safe live non-secret template/SOUL/skills evidence, sandbox render probes, and clearer blocked/unverified states. |
| Create/modify, after approval if script changes | `scripts/cron/tests/test_weekly_hermes_parity_review.py` or `scripts/_core/tests/test_sync_agent_configs.sh` | TDD coverage for parity report classification and non-secret, non-mutating behavior. |
| Modify, after approval if needed | `docs/ops/scheduled-tasks.md` | Cross-link #1583 baseline and #2089 recurring review; preserve ace-linux-2 01:45 schedule evidence. |
| Modify, after approval only if evidence shows a gap | `config/scheduled-tasks/schedule-tasks.yaml` | Expected no-op unless review finds schedule drift; source of truth already includes ace-linux-2 and Windows hosts. |
| Modify, after approval | `scripts/_core/sync-agent-configs.sh` | Required: fix dry-run mkdir side effects before any live-HOME dry-run may be used for parity reporting; also adjust missing baseline fields if found. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_hermes_parity_doc_lists_managed_and_local_files` | New parity doc separates repo-managed templates from machine-local secrets and handles custom-skills plus wiki/knowledge roots. | `docs/ops/hermes-config-parity.md` | Mentions `config.yaml.template`, `SOUL.md`, memory snapshots, `skills.external_dirs`, wiki/knowledge path settings, and either `custom-skills` implementation or supersession rationale; excludes `auth.json` and `.env` from repo sync. |
| `test_weekly_parity_report_references_1583_and_2089` | Weekly script/report remains anchored to baseline and governance issues. | run report in temp output dir or inspect generated markdown | Report includes #1583 and #2089 links. |
| `test_weekly_parity_does_not_read_secret_files` | Script avoids `auth.json`, `.env`, token/API key extraction. | static scan of script and generated report | No secret-file reads or credential strings; only presence/status if absolutely needed. |
| `test_weekly_parity_live_machine_requires_safe_evidence` | Weekly report cannot mark a machine pass from sandbox-only render evidence. | mocked machine with only temp-HOME dry-run success and no safe live config/SOUL/skills evidence | Status is `unverified` or `blocked`, not `pass`. |
| `test_weekly_parity_report_rows_include_effective_baseline_signals` | Generated report rows expose the requested effective-baseline fields instead of only tool versions. | mocked local/SSH/Windows rows with config/SOUL/skills/custom-skills/wiki/memory/sync-dry-run states | Each row includes config template/render state, SOUL state, `skills.external_dirs`, custom-skills disposition, wiki/knowledge path disposition, memory snapshot/readiness, and sync dry-run state or explicit `blocked`/`unverified` reason. |
| `test_weekly_parity_classifies_unreachable_ace_linux_2_as_blocked_not_pass` | External-machine failure cannot close #1583 accidentally. | mocked SSH failure/timeout | Status row is `unreachable` or `blocked`, not `pass`. |
| `test_sync_agent_configs_hermes_placeholder_and_terminal` | Existing sync preserves terminal backend/cwd and applies template defaults. | temp HOME existing config | PASS in `scripts/_core/tests/test_sync_agent_helpers.sh`. |
| `test_sync_agent_configs_dry_run_no_live_home_side_effects` | Dry-run parity probes do not create memory/config directories in live HOME. | temp HOME / mocked HOME with absent memories dir | No directory creation unless non-dry-run or explicitly isolated temp HOME. |
| `test_scheduled_tasks_docs_match_yaml` | ace-linux-2 docs stay aligned with YAML schedule. | `schedule-tasks.yaml` and `docs/ops/scheduled-tasks.md` | `01:45 daily` for ace-linux-2 harness-update. |

---

## Acceptance Criteria

Planning-stage acceptance criteria:
- [ ] Plan file exists at `docs/plans/2026-05-13-issue-1583-hermes-config-parity-plan.md`.
- [ ] `docs/plans/README.md` has a #1583 row.
- [ ] Review state is explicit: Codex T1 artifact is saved under `scripts/review/results/` with verdict MINOR or better for in-window plan-review posting; Claude T2 remains deferred to morning triage per user routing. The plan may be posted to `status:plan-review` after Codex MINOR, but it is not implementation-approved. Provider-unavailable/deferred artifacts are evidence of attempted or scheduled review, not substitutes for user approval.
- [ ] A ready-for-user-approval/comment-for-user-decision is posted to #1583 and the issue is left at `status:plan-review`, not self-approved. The comment preserves prior implementation evidence and states that the refreshed plan supersedes the old approval gate for new work; stale `status:plan-approved` and `status:working` labels are then removed or explicitly called out if label mutation fails, so the issue cannot be executed under old approval.

Implementation-stage acceptance criteria after user approval:
- [ ] Canonical Hermes parity baseline doc exists and lists managed repo files/settings, machine-local exclusions, custom-skills disposition, wiki/knowledge path disposition, and verification commands.
- [ ] Weekly parity review/report checks effective Hermes baseline evidence, not only tool versions: safe live non-secret config/SOUL/skills evidence plus sandbox render probes. Report rows include config template/render state, SOUL state, `skills.external_dirs`, custom-skills disposition, wiki/knowledge path disposition, memory snapshot/readiness, and sync dry-run state or an explicit blocked/unverified reason. Sandbox-only evidence cannot produce `pass`; it yields `unverified`/`blocked` until live evidence exists.
- [ ] Secret-bearing files (`auth.json`, `.env`, API keys/tokens/passwords/credentials/connection strings) are neither committed nor summarized; any encountered secret is redacted as `[REDACTED]`.
- [ ] Existing repo-side tests pass:
  - `uv run --extra dev pytest tests/docs/test_scheduled_tasks_docs.py -q`
  - `bash scripts/_core/tests/test_sync_agent_helpers.sh`
  - `bash scripts/_core/tests/test_sync_agent_configs.sh`
  - `uv run --no-project python scripts/cron/validate-schedule.py`
- [ ] `tmp_home=$(mktemp -d); mkdir -p "$tmp_home/.hermes"; HOME="$tmp_home" bash scripts/_core/sync-agent-configs.sh --dry-run` or an equivalent sandboxed dry-run shows Hermes config/SOUL/memory sync lines and no syntax errors; live HOME dry-run remains banned until `sync-agent-configs.sh` dry-run directory creation is fixed and tested.
- [ ] ace-linux-2 live status is explicitly resolved: either verified via #1582/#1564 evidence or #1583 remains open with a blocked-on-external-machine comment.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Codex | MINOR | 2026-05-14 T1 rerun returned MINOR. Findings: stale review-summary wording, ambiguous Codex-now/Claude-later gate, and missing compact #2695 picklist excerpt. This revision addresses all three. |
| Claude | DEFERRED | User requested Claude T2 in morning triage. T2 review remains expected before implementation; do not treat this plan as approved without user action. |
| Gemini | NOT RUN | Default repo workflow expects 2+ providers. If Gemini is unavailable or skipped due user-specified Codex T1/Claude T2 routing, preserve that exception explicitly in the issue comment and keep state at `status:plan-review`. |

**Overall result:** PLAN-REVIEW READY FOR USER DECISION AFTER CODEX T1; NOT APPROVED. Codex T1 is MINOR with non-blocking findings addressed in this plan revision. Claude T2 remains deferred to morning triage per user routing, so implementation must not begin unless the user explicitly pre-authorizes or later approves after reviewing this state.

Revisions made based on review:
- Added explicit custom-skills disposition requirement.
- Changed dry-run probing to require temp HOME/sandbox for render probes and made live-HOME dry-run side-effect fix mandatory before live use.
- Added safe live non-secret parity evidence requirement so sandbox-only dry-run cannot mark a machine `pass`.
- Added stale `status:plan-approved` / `status:working` cleanup to planning-stage acceptance.
- Added wiki/knowledge path disposition to gaps, artifact map, files, tests, and implementation acceptance.
- Corrected sandbox dry-run command to precreate `$HOME/.hermes` so memory restore dry-run lines are reachable.
- Added requirement to preserve prior implementation evidence before removing stale approval/working labels.
- Added explicit generated-report-row coverage for every effective-baseline signal, not just broad classification.
- Strengthened planning-stage review gate language to require 2+ provider verdicts MINOR-or-better; provider-unavailable artifacts do not equal approval-ready.
- Added latest #2695 picklist evidence: #1583 is not on bootstrap picklist, so this run is a user-explicit override.
- Addressed Codex MINOR rerun findings by updating review summary to current MINOR state, separating Codex T1 plan-review posting from deferred Claude T2/user approval, and preserving compact #2695 picklist evidence in the plan.

---

## Risks and Open Questions

- **Risk:** Existing issue #1583 already has `status:plan-approved` and `status:working` from earlier work plus prior implementation comments. The refreshed no-plan workflow must not treat those as permission to mutate config templates, but it also must not erase history. Preserve prior implementation evidence in the plan-review comment, then remove stale execution/approval labels when posting the refreshed `status:plan-review`, unless GitHub label mutation is blocked; in that case, post the drift explicitly and stop.
- **Risk:** Dirty unrelated workspace changes are present in `docs/plans/README.md`, `.claude/state/`, provider reports, and other files. Commit only #1583 plan/review artifacts and the #1583 README row; do not sweep unrelated files into the commit.
- **Risk:** ace-linux-2 verification requires external machine state and likely depends on #1582 and #1564. Do not close #1583 on local repo evidence alone.
- **Risk:** Hermes config under audit is the active runtime. Do not mutate live `~/.hermes/config.yaml` during planning or review; implementation should use templates, temp HOME fixtures, and dry-run probes.
- **Risk:** Memory policy in the original issue body is superseded by #1782. Do not reintroduce old guidance that memories must never be repo-snapshotted.
- **Open:** Should licensed-win-2 parity artifact contract be included in this issue or split to a child issue? Current weekly script marks it blocked due no canonical artifact path.
- **Open:** Should `config/agents/hermes/custom-skills/` be implemented as a physical repo-managed directory, or should the plan explicitly supersede it with `skills.external_dirs` pointing to canonical repo skills? Recommended: document supersession unless user needs machine-local custom skills distinct from repo skills.
- **Open:** Which Hermes key, if any, should canonicalize wiki/knowledge roots (`wiki.path` or equivalent)? If Hermes has no stable key, document the setting as unsupported/machine-local and keep the report row `blocked` rather than inventing config.
- **Open:** If ace-linux-2 remains unavailable after approval, should #1583 close as repo-complete with explicit child blockers, or remain open until live bootstrap evidence exists? Recommended: remain open unless the user explicitly accepts blocker conversion.

---

## Complexity: T2

**T2** — multi-file harness/config plan with existing implementation reconciliation, external-machine blockers, scheduled-task documentation, shell/Python tests, and adversarial review. The future execution is mostly mechanical and fits `/goal` catalog Tier 2 #29 `[execution-heavy]`, but closure depends on live machine verification outside the repo.
