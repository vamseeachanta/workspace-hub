# Provider session ecosystem audit — 2026-04-20

Scope: provider session artifacts rooted at `/mnt/local-analysis/workspace-hub/logs/orchestrator` with saved provider artifacts used only as fallback when raw logs are unavailable.

## Executive summary
- `claude` — source=raw_logs | sessions=33 | post_records=80561 | python3/1k=9.06 | uv-python/1k=74.04
- `codex` — source=raw_logs | sessions=50 | post_records=17317 | python3/1k=19.46 | uv-python/1k=24.31
- `hermes` — source=raw_logs | sessions=19 | post_records=102042 | python3/1k=17.02 | uv-python/1k=19.87
- `gemini` — source=raw_logs | sessions=45 | post_records=6082 | python3/1k=47.85 | uv-python/1k=6.41

- Migration debt density (known stale reads with redirect hints per 1k records): `gemini` 13.81, `claude` 12.07, `codex` 0.0, `hermes` 0.0.
- Highest-volume known migration debt: `claude` with 972 mapped stale reads across 4 rule clusters; top hotspot: `legacy_work_queue_transition` (318).
- Highest-density known migration debt: `gemini` with 84 mapped stale reads; top hotspot: `legacy_local_work_queue_items` (37, 44.05% of known debt).
- Unmapped missing repo reads remain for: `codex`, `hermes`; this looks more like general path drift than known migration debt.
- Scope note: Migration-debt figures are based on remediation-mapped entries from each provider's top missing repo reads.

## Provider interpretation summary
- Focus this week: prioritize legacy-path redirect cleanup and prompt/doc updates on claude (urgency 74.65, issue: legacy_work_queue_transition), then address gemini (urgency 47.68, issue: legacy_local_work_queue_items).
- Recommended actions:
  - `claude` [urgent_now] — prioritize legacy-path redirect cleanup and prompt/doc updates (urgency 74.65, issue: legacy_work_queue_transition; health=red; movement: rank unchanged at #1; urgency 74.65 (+5.10 vs previous audit); path drift improved; corpus was pruned or rebuilt)
  - `gemini` [next_up] — prioritize legacy-path redirect cleanup and prompt/doc updates (urgency 47.68, issue: legacy_local_work_queue_items; health=red; movement: rank unchanged at #2; urgency 47.68 (+0.00 vs previous audit))
  - `codex` [investigate] — sample top missing repo reads to separate remap work from benign variance (urgency 10.13, issue: unmapped path drift; health=yellow; movement: rank unchanged at #3; urgency 10.13 (+0.00 vs previous audit))
- Health overview:
  - `claude` [red] — red: urgent action tier; high migration debt; corpus anomaly needs interpretation
  - `gemini` [red] — red: high migration debt; python3-heavy command hygiene
  - `codex` [yellow] — yellow: unmapped path drift remains; 7d sustained activity
  - `hermes` [yellow] — yellow: unmapped path drift remains; 7d sustained activity
- Watchlist triggers:
  - `claude` [page] — urgent-now provider with legacy_work_queue_transition | follow-up: Escalate immediately on claude: prioritize legacy-path redirect cleanup and prompt/doc updates
  - `gemini` [act_this_week] — red health due to legacy_local_work_queue_items | follow-up: Prioritize this week on gemini: prioritize legacy-path redirect cleanup and prompt/doc updates
  - `codex` [investigate] — yellow health with sustained 7d activity and unmapped path drift | follow-up: Sample current traces on codex and verify whether unmapped path drift needs remap or docs cleanup
  - `hermes` [investigate] — yellow health with sustained 7d activity and unmapped path drift | follow-up: Sample current traces on hermes and verify whether unmapped path drift needs remap or docs cleanup
- Change alerts:
  - `claude` [trigger_escalated] — claude trigger escalated from act_this_week to page | follow-up: Escalate immediately on claude: prioritize legacy-path redirect cleanup and prompt/doc updates
- Remediation playbooks:
  - `claude` [page] — issue=legacy_work_queue_transition | lane=governance-docs | owner=governance-maintainers | owner_surface=docs/governance/SESSION-GOVERNANCE.md | inspect=scripts/work-queue/start_stage.py, scripts/work-queue/exit_stage.py, scripts/work-queue/verify_checklist.py | targets=docs/governance/SESSION-GOVERNANCE.md, docs/governance/TRUST-ARCHITECTURE.md, scripts/workflow/governance-checkpoints.yaml | steps: Inspect the top matched stale paths for legacy_work_queue_transition and confirm they should redirect rather than be recreated. | Open the canonical targets and migrate prompts/docs/tooling toward: docs/governance/SESSION-GOVERNANCE.md, docs/governance/TRUST-ARCHITECTURE.md, scripts/workflow/governance-checkpoints.yaml.
  - `gemini` [act_this_week] — issue=legacy_local_work_queue_items | lane=planning-workflow | owner=planning-ops | owner_surface=notes/agent-work-queue.md | inspect=.claude/work-queue/WRK-149.md, .claude/work-queue/working, .claude/work-queue/working/ | targets=GitHub issues, .planning/, notes/agent-work-queue.md | steps: Inspect the top matched stale paths for legacy_local_work_queue_items and confirm they should redirect rather than be recreated. | Open the canonical targets and migrate prompts/docs/tooling toward: GitHub issues, .planning/, notes/agent-work-queue.md.
  - `codex` [investigate] — issue=unmapped path drift | lane=drift-triage | owner=drift-triage | owner_surface=docs/ops/legacy-claude-reference-map.md | inspect=analysis/provider-session-ecosystem-audit.json, docs/reports/provider-session-ecosystem-audit.md | targets=docs/ops/legacy-claude-reference-map.md, docs/work-queue-workflow.md | steps: Sample the provider's top missing repo reads from the audit JSON and group them by path family. | Decide whether each path family is a legitimate missing file, a deleted legacy path, or a symbolic/non-file surface that needs remapping.
  - `hermes` [investigate] — issue=unmapped path drift | lane=drift-triage | owner=drift-triage | owner_surface=docs/ops/legacy-claude-reference-map.md | inspect=analysis/provider-session-ecosystem-audit.json, docs/reports/provider-session-ecosystem-audit.md | targets=docs/ops/legacy-claude-reference-map.md, docs/work-queue-workflow.md | steps: Sample the provider's top missing repo reads from the audit JSON and group them by path family. | Decide whether each path family is a legitimate missing file, a deleted legacy path, or a symbolic/non-file surface that needs remapping.
- `claude` — rank=1 (prev=1, move=stable) | health=red | profile=light_recent | 24h=1868 posts/9 sessions | 7d=5800 posts/95 sessions | urgency=74.65 | tier=urgent_now | activity=quiet (stable) | corpus=corpus_pruned_or_rebuilt | debt=high_debt (stable) | drift=improving | python=uv_preferred (stable) | health summary: red: urgent action tier; high migration debt; corpus anomaly needs interpretation | movement: rank unchanged at #1; urgency 74.65 (+5.10 vs previous audit); path drift improved; corpus was pruned or rebuilt | primary issue: legacy_work_queue_transition | action: prioritize legacy-path redirect cleanup and prompt/doc updates
- `gemini` — rank=2 (prev=2, move=stable) | health=red | profile=light_recent | 24h=0 posts/0 sessions | 7d=181 posts/31 sessions | urgency=47.68 | tier=next_up | activity=idle (stable) | corpus=aligned | debt=high_debt (stable) | drift=stable | python=python3_heavy (stable) | health summary: red: high migration debt; python3-heavy command hygiene | movement: rank unchanged at #2; urgency 47.68 (+0.00 vs previous audit) | primary issue: legacy_local_work_queue_items | action: prioritize legacy-path redirect cleanup and prompt/doc updates
- `codex` — rank=3 (prev=3, move=stable) | health=yellow | profile=sustained_background | 24h=213 posts/7 sessions | 7d=1566 posts/70 sessions | urgency=10.13 | tier=investigate | activity=idle (stable) | corpus=aligned | debt=drift_only (stable) | drift=stable | python=mixed (stable) | health summary: yellow: unmapped path drift remains; 7d sustained activity | movement: rank unchanged at #3; urgency 10.13 (+0.00 vs previous audit) | primary issue: unmapped path drift | action: sample top missing repo reads to separate remap work from benign variance
- `hermes` — rank=4 (prev=4, move=stable) | health=yellow | profile=sustained_background | 24h=760 posts/13 sessions | 7d=23457 posts/203 sessions | urgency=4.33 | tier=monitor | activity=idle (stable) | corpus=aligned | debt=drift_only (stable) | drift=stable | python=mixed (stable) | health summary: yellow: unmapped path drift remains; 7d sustained activity | movement: rank unchanged at #4; urgency 4.33 (+0.00 vs previous audit) | primary issue: unmapped path drift | action: sample top missing repo reads to separate remap work from benign variance

## Recent activity since previous audit
- Previous audit timestamp: `2026-04-20T16:39:16Z`
- Recent post-audit activity: `claude` 10 post records / 2 sessions.
- Scope note: This is event-time activity since the previous audit timestamp, not a census of newly exported historical/backfilled records.

## Rolling activity windows
- `last_24h` — `2026-04-19T16:48:52Z` → `2026-04-20T16:48:52Z`
  - Scope note: Last 24 hours of event-time activity ending at this audit timestamp.
  - Activity leaders: `claude` 1868 post records / 9 sessions, `hermes` 760 post records / 13 sessions, `codex` 213 post records / 7 sessions.
- `last_7d` — `2026-04-13T16:48:52Z` → `2026-04-20T16:48:52Z`
  - Scope note: Last 7 days of event-time activity ending at this audit timestamp.
  - Activity leaders: `hermes` 23457 post records / 203 sessions, `claude` 5800 post records / 95 sessions, `codex` 1566 post records / 70 sessions, `gemini` 181 post records / 31 sessions.

## Corpus change since previous audit
- Previous audit timestamp: `2026-04-20T16:39:16Z`
- Scope note: Snapshot-to-snapshot corpus deltas reflect export additions/removals/reclassification and should be interpreted separately from event-time recent activity.
- Largest negative reconciliation gap: `claude`
- Largest positive reconciliation gap: `codex`

## claude
- Source: raw_logs
- Sessions: 33
- Post-hook records: 80561
- Correction sessions: 0
- Unique runtime sessions: 136
- Prompt-like reads: 96
- Blank read targets: 0
- Missing repo reads: 7599
- Bare python3 bash calls: 730
- `uv run ... python` bash calls: 5965

### claude top tools
- `Bash` — 43752
- `Read` — 15586
- `Edit` — 7352
- `Write` — 6844
- `Grep` — 2021
- `Agent` — 860
- `ToolSearch` — 681
- `TaskUpdate` — 541

### claude top repos
- `workspace-hub` — 76775
- `digitalmodel` — 1900
- `assetutilities` — 535
- `worldenergydata` — 201
- `agent-a597ec3f` — 100
- `aceengineer-admin` — 87
- `agent-a1fcef76` — 58
- `wrk-1132-standards-search` — 55

### claude top reads
- `scripts/work-queue/verify-gate-evidence.py` — 740
- `scripts/work-queue/generate-html-review.py` — 249
- `scripts/work-queue/start_stage.py` — 138
- `scripts/work-queue/exit_stage.py` — 137
- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` — 126
- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` — 123
- `scripts/work-queue/close-item.sh` — 94
- `docs/plans/README.md` — 81
- `scripts/work-queue/whats-next.sh` — 70
- `.claude/skills/coordination/workspace/work-queue/SKILL.md` — 66

### claude top symbolic reads
- none

### claude top Bash command families
- `ls` — 6412
- `uv run` — 5698
- `grep` — 5419
- `cat` — 4489
- `find` — 3368
- `bash` — 2890
- `sed` — 1341
- `gh` — 1270

### claude recent activity since previous audit
- Post-hook records since prior audit: 10
- Runtime sessions since prior audit: 2

### claude recent top tools
- `Bash` — 10

### claude recent top Bash command families
- `ls` — 4
- `gh` — 3
- `cat` — 1
- `head` — 1
- `/tmp/adversarial-plan-review-prompt.md)` — 1

### claude recent top missing repo reads
- none

### claude corpus change since previous audit
- Post-hook records: current 80561 vs previous 80552 (delta 9)
- Sessions: current 33 vs previous 33 (delta 0)
- Missing repo reads: current 7599 vs previous 7599 (delta 0)
- Event-time post records since prior audit: 10
- Reconciliation gap vs event-time delta: -1
- Status: corpus_pruned_or_rebuilt
- Interpretation: Snapshot shrank relative to recent event-time activity, suggesting pruning, rebuild, or reclassification.

### claude top missing repo reads
- `scripts/work-queue/generate-html-review.py` — 249
- `scripts/work-queue/start_stage.py` — 138
- `scripts/work-queue/exit_stage.py` — 137
- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` — 123
- `scripts/work-queue/close-item.sh` — 94
- `.claude/skills/coordination/workspace/work-queue/SKILL.md` — 66
- `scripts/work-queue/archive-item.sh` — 62
- `scripts/work-queue/claim-item.sh` — 60
- `scripts/work-queue/verify_checklist.py` — 43
- `scripts/work-queue/stages/stage-01-capture.yaml` — 42

### claude remediation hints for stale repo reads
- `scripts/work-queue/start_stage.py` (138), `scripts/work-queue/exit_stage.py` (137), `scripts/work-queue/verify_checklist.py` (43) — 318 combined reads
  - Redirect to: `docs/governance/SESSION-GOVERNANCE.md`, `docs/governance/TRUST-ARCHITECTURE.md`, `scripts/workflow/governance-checkpoints.yaml`, `.claude/hooks/plan-approval-gate.sh`, `.claude/hooks/session-governor-check.sh`, `scripts/review/cross-review.sh`
  - Guidance: Legacy stage-transition tooling was removed during workflow migration; redirect callers to governance docs/hooks instead of recreating the old executables.
  - Reference: `docs/ops/legacy-claude-reference-map.md`
- `scripts/work-queue/generate-html-review.py` (249) — 249 combined reads
  - Redirect to: `scripts/review/cross-review.sh`, `templates/review-standard.html`, `docs/work-queue-workflow.md`
  - Guidance: Historical HTML review generation is no longer canonical; use the current cross-review workflow and stored review evidence instead.
  - Reference: `docs/ops/legacy-claude-reference-map.md`
- `scripts/work-queue/close-item.sh` (94), `scripts/work-queue/archive-item.sh` (62), `scripts/work-queue/claim-item.sh` (60) — 216 combined reads
  - Redirect to: `scripts/refresh-agent-work-queue.py`, `scripts/refresh-agent-work-queue.sh`, `notes/agent-work-queue.md`, `.planning/`, `GitHub issues`
  - Guidance: The repo no longer uses local queue scripts as the source of truth; prefer GitHub issue updates plus .planning evidence.
  - Reference: `docs/ops/legacy-claude-reference-map.md`
- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` (123), `.claude/skills/coordination/workspace/work-queue/SKILL.md` (66) — 189 combined reads
  - Redirect to: `AGENTS.md`, `.claude/commands/gsd/*`, `.gemini/get-shit-done/workflows/*`, `docs/work-queue-workflow.md`
  - Guidance: The old work-queue skill tree was replaced by GSD-oriented command/workflow surfaces; redirect readers instead of restoring deleted skill files.
  - Reference: `docs/ops/legacy-claude-reference-map.md`

### claude top missing external reads
- `/tmp/tmp.4XN7Wckbxl/review-content.md` — 18
- `/tmp/tmp.4fvalbgSpv/review-content.md` — 10
- `/tmp/tmp.Y7GHawx2jw/review-content.md` — 9
- `/tmp/tmp.sHUq6zx1JY/review-content.md` — 6
- `/tmp/tmp.Y2upjk3JCH/review-content.md` — 5
- `/tmp/tmp.SmqPbkghat/review-content.md` — 5
- `/tmp/tmp.mIXvhD1xZj/review-content.md` — 5
- `/tmp/tmp.xgxlrsu4AN/review-content.md` — 5
- `/tmp/gt1r-frame/frame_preview.png` — 5
- `/tmp/tmp.yX4KezaN1x/review-content.md` — 4

## codex
- Source: raw_logs
- Sessions: 50
- Post-hook records: 17317
- Correction sessions: 0
- Unique runtime sessions: 477
- Prompt-like reads: 1
- Blank read targets: 0
- Missing repo reads: 247
- Bare python3 bash calls: 337
- `uv run ... python` bash calls: 421

### codex top tools
- `Bash` — 15886
- `Read` — 625
- `update_plan` — 384
- `Grep` — 315
- `list_mcp_resources` — 61
- `list_mcp_resource_templates` — 13
- `_fetch_commit` — 6
- `request_user_input` — 5

### codex top repos
- `workspace-hub` — 17317

### codex top reads
- `docs/plans/README.md` — 20
- `docs/standards/HARD-STOP-POLICY.md` — 12
- `config/scheduled-tasks/schedule-tasks.yaml` — 9
- `data/document-index/resource-intelligence-maturity.yaml` — 7
- `content/demos/index.html` — 7
- `scripts/cron/setup-cron.sh` — 6
- `scripts/cron/validate-schedule.py` — 6
- `docs/plans/_template-issue-plan.md` — 6
- `docs/plans/2026-04-17-issue-2342-2343-demo-detail-pages.md` — 6
- `package.json` — 6

### codex top symbolic reads
- `CNAME` — 2

### codex top Bash command families
- `sed` — 4207
- `rg` — 1782
- `nl` — 1330
- `ls` — 518
- `bash` — 473
- `uv run` — 453
- `find` — 436
- `git status` — 311

### codex recent activity since previous audit
- Post-hook records since prior audit: 0
- Runtime sessions since prior audit: 0

### codex recent top tools
- none

### codex recent top Bash command families
- none

### codex recent top missing repo reads
- none

### codex corpus change since previous audit
- Post-hook records: current 17317 vs previous 17317 (delta 0)
- Sessions: current 50 vs previous 50 (delta 0)
- Missing repo reads: current 247 vs previous 247 (delta 0)
- Event-time post records since prior audit: 0
- Reconciliation gap vs event-time delta: 0
- Status: aligned
- Interpretation: Snapshot post-record change aligns with recent event-time activity.

### codex top missing repo reads
- `content/demos/index.html` — 7
- `package.json` — 6
- `build.js` — 5
- `content/demos/jumper-installation.html` — 5
- `content/partials/head-common.html` — 5
- `vercel.json` — 5
- `docs/reports/2026-04-17-issue-39-market-hours-signals-consumers-plan.md` — 4
- `examples/demos/gtm/output/demo_02_wall_thickness_report.html` — 4
- `examples/demos/gtm/output/demo_03_mudmat_installation_report.html` — 4
- `github://vamseeachanta/workspace-hub/issues/2249` — 3

### codex remediation hints for stale repo reads
- none

### codex top missing external reads
- none

## hermes
- Source: raw_logs
- Sessions: 19
- Post-hook records: 102042
- Correction sessions: 18
- Unique runtime sessions: 1344
- Prompt-like reads: 862
- Blank read targets: 26
- Missing repo reads: 270
- Bare python3 bash calls: 1737
- `uv run ... python` bash calls: 2028

### hermes top tools
- `Bash` — 45767
- `Read` — 18227
- `Grep` — 16295
- `Write` — 12612
- `Edit` — 6654
- `Task` — 1346
- `Browser` — 512
- `ToolSearch` — 221

### hermes top repos
- `workspace-hub` — 102042

### hermes top reads
- `config/scheduled-tasks/schedule-tasks.yaml` — 238
- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` — 234
- `docs/reports/provider-session-ecosystem-audit.md` — 209
- `docs/plans/README.md` — 189
- `analysis/provider-session-ecosystem-audit.json` — 142
- `scripts/analysis/provider_session_ecosystem_audit.py` — 107
- `tests/analysis/test_provider_session_ecosystem_audit.py` — 95
- `scripts/_core/sync-agent-configs.sh` — 90
- `scripts/cron/harness-update.sh` — 88
- `docs/plans/_template-issue-plan.md` — 82

### hermes top symbolic reads
- `github/github-issues` — 219
- `github-issues` — 148
- `coordination/issue-planning-mode` — 139
- `autonomous-ai-agents/claude-code` — 126
- `gh-work-planning` — 85
- `overnight-parallel-agent-prompts` — 81
- `issue-planning-mode` — 72
- `coordination/cross-review-policy` — 72
- `claude-code` — 65
- `coordination/session-start-routine` — 65

### hermes top Bash command families
- `gh` — 9142
- `uv run` — 3492
- `git add` — 1791
- `git status` — 1647
- `find` — 1421
- `ls` — 1360
- `cat` — 1243
- `git log` — 1085

### hermes recent activity since previous audit
- Post-hook records since prior audit: 0
- Runtime sessions since prior audit: 0

### hermes recent top tools
- none

### hermes recent top Bash command families
- none

### hermes recent top missing repo reads
- none

### hermes corpus change since previous audit
- Post-hook records: current 102042 vs previous 102042 (delta 0)
- Sessions: current 19 vs previous 19 (delta 0)
- Missing repo reads: current 270 vs previous 270 (delta 0)
- Event-time post records since prior audit: 0
- Reconciliation gap vs event-time delta: 0
- Status: aligned
- Interpretation: Snapshot post-record change aligns with recent event-time activity.

### hermes top missing repo reads
- `client_projects/engineering_workbooks/ballymore/jumper_manifold_to_plet/jumper_lift.py` — 24
- `docs/plans/2026-04-10-llm-wiki-resource-doc-repo-integration-blueprint.md` — 18
- `scripts/hooks/pre-push.sh` — 14
- `digitalmodel/specs/module-registry.yaml` — 9
- `.planning/quick/review-2239.md` — 8
- `digitalmodel/docs/roadmaps/orcawave-orcaflex-capability-roadmap.md` — 7
- `digitalmodel/docs/assessments/hull-library-audit.md` — 7
- `docs/handoffs/overnight-llm-wiki-stage1-source-map.md` — 7
- `docs/handoffs/overnight-llm-wiki-stage2-skill-repo-map.md` — 7
- `docs/handoffs/overnight-llm-wiki-stage3-architecture.md` — 7

### hermes remediation hints for stale repo reads
- none

### hermes top missing external reads
- `/mnt/local-analysis/worktrees/workspace-hub-2151/docs/modules/ai/readiness-evidence-bundle.schema.yaml` — 17
- `/mnt/local-analysis/worktrees/wh-2127/docs/governance/SESSION-GOVERNANCE.md` — 12
- `/mnt/local-analysis/worktrees/wh-2127/tests/work-queue/test_session_governor.py` — 11
- `/mnt/local-analysis/worktrees/workspace-hub-2151/scripts/analysis/readiness_bundle_schema.py` — 9
- `/mnt/local-analysis/worktrees/workspace-hub-2151/tests/analysis/test_readiness_bundle_schema.py` — 9
- `/mnt/local-analysis/worktrees/wh-2128/tests/enforcement/test_install_hooks_stage_prompt_drift.py` — 9
- `/mnt/local-analysis/worktrees/workspace-hub-2151/tests/fixtures/readiness/windows-valid.yaml` — 7
- `/mnt/local-analysis/worktrees/workspace-hub-2151/tests/fixtures/readiness/linux-valid.yaml` — 7
- `/mnt/local-analysis/worktrees/workspace-hub-2151/tests/fixtures/readiness/invalid-access-mode.yaml` — 7
- `/mnt/local-analysis/worktrees/wh-2128/scripts/enforcement/install-hooks.sh` — 7

## gemini
- Source: raw_logs
- Sessions: 45
- Post-hook records: 6082
- Correction sessions: 0
- Unique runtime sessions: 318
- Prompt-like reads: 18
- Blank read targets: 0
- Missing repo reads: 665
- Bare python3 bash calls: 291
- `uv run ... python` bash calls: 39

### gemini top tools
- `Bash` — 2281
- `Read` — 2135
- `Grep` — 621
- `Write` — 535
- `Edit` — 394
- `Browser` — 104
- `ToolSearch` — 9
- `ask_user` — 1

### gemini top repos
- `workspace-hub` — 6082

### gemini top reads
- `.claude/work-queue/` — 29
- `scripts/operations/compliance/migrate_specs_to_workspace.sh` — 28
- `.` — 22
- `CLAUDE.md` — 21
- `.claude/work-queue` — 18
- `.claude/work-queue/WRK-149.md` — 17
- `.claude/work-queue/pending` — 16
- `digitalmodel/scripts/benchmark/validate_owd_vs_spec.py` — 16
- `digitalmodel/src/digitalmodel` — 15
- `.claude/work-queue/INDEX.md` — 13

### gemini top symbolic reads
- `digitalmodel` — 31
- `worldenergydata` — 17
- `assethold` — 9
- `scripts` — 8
- `doris` — 8
- `src` — 7
- `tests` — 7
- `config` — 6
- `assetutilities` — 6
- `acma-projects` — 5

### gemini top Bash command families
- `ls` — 467
- `find` — 274
- `cat` — 191
- `python3` — 173
- `grep` — 149
- `git` — 120
- `mkdir` — 78
- `git status` — 72

### gemini recent activity since previous audit
- Post-hook records since prior audit: 0
- Runtime sessions since prior audit: 0

### gemini recent top tools
- none

### gemini recent top Bash command families
- none

### gemini recent top missing repo reads
- none

### gemini corpus change since previous audit
- Post-hook records: current 6082 vs previous 6082 (delta 0)
- Sessions: current 45 vs previous 45 (delta 0)
- Missing repo reads: current 665 vs previous 665 (delta 0)
- Event-time post records since prior audit: 0
- Reconciliation gap vs event-time delta: 0
- Status: aligned
- Interpretation: Snapshot post-record change aligns with recent event-time activity.

### gemini top missing repo reads
- `.claude/work-queue/WRK-149.md` — 17
- `.claude/skills/coordination/workspace/work-queue/SKILL.md` — 12
- `scripts/agents/lib/workflow-guards.sh` — 11
- `.claude/work-queue/working` — 11
- `scripts/agents/execute.sh` — 10
- `.claude/work-queue/working/` — 9
- `.gitmodules` — 9
- `scripts/agents/providers/claude.sh` — 7
- `scripts/agents/plan.sh` — 7
- `specs/wrk/WRK-188/worldenergydata-wave1-migration.md` — 6

### gemini remediation hints for stale repo reads
- `.claude/work-queue/WRK-149.md` (17), `.claude/work-queue/working` (11), `.claude/work-queue/working/` (9) — 37 combined reads
  - Redirect to: `GitHub issues`, `.planning/`, `notes/agent-work-queue.md`, `docs/work-queue-workflow.md`
  - Guidance: Local queue item files are compatibility surfaces, not canonical work tracking; prefer the GitHub issue and .planning artifact instead.
  - Reference: `docs/ops/legacy-claude-reference-map.md`
- `scripts/agents/lib/workflow-guards.sh` (11), `scripts/agents/execute.sh` (10), `scripts/agents/providers/claude.sh` (7), `scripts/agents/plan.sh` (7) — 35 combined reads
  - Redirect to: `AGENTS.md`, `docs/modules/ai/AGENT_EQUIVALENCE_ARCHITECTURE.md`, `docs/work-queue-workflow.md`, `scripts/review/cross-review.sh`, `scripts/planning/ensemble-plan.sh`
  - Guidance: The old scripts/agents wrapper tree is gone; use the current policy-first workflow and current review/planning surfaces instead.
  - Reference: `docs/ops/legacy-claude-reference-map.md`
- `.claude/skills/coordination/workspace/work-queue/SKILL.md` (12) — 12 combined reads
  - Redirect to: `AGENTS.md`, `.claude/commands/gsd/*`, `.gemini/get-shit-done/workflows/*`, `docs/work-queue-workflow.md`
  - Guidance: The old work-queue skill tree was replaced by GSD-oriented command/workflow surfaces; redirect readers instead of restoring deleted skill files.
  - Reference: `docs/ops/legacy-claude-reference-map.md`

### gemini top missing external reads
- `/tmp/pending-queue-snapshot.txt` — 1
- `/tmp/test-output.md` — 1

## Ecosystem strengthening recommendations
1. Keep exporting every provider into `logs/orchestrator/<provider>/session_*.jsonl` before the audit so the recent-delta section stays trustworthy.
2. Treat symbolic skill/tool reads separately from filesystem reads. Hermes emits many skill names in `file`, and counting them as missing files creates noisy false positives.
3. Preserve Codex command-shape fidelity in both export and audit layers. Recent native sessions use a mix of spaced-encoded commands and ordinary shell strings.
4. Use the recent-activity section to prioritize follow-up review on providers with actual post-audit event-time work instead of re-reading the full historical corpus every time.
5. Keep pushing `uv run ... python` migration. Hermes, Gemini, and Codex still show meaningful bare `python3` usage density.

