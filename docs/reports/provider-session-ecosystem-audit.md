# Provider session ecosystem audit — 2026-04-13

Scope: provider session artifacts rooted at `/mnt/local-analysis/workspace-hub/logs/orchestrator` with saved provider artifacts used only as fallback when raw logs are unavailable.

## Executive summary
- `claude` — source=raw_logs | sessions=26 | post_records=74657 | python3/1k=8.63 | uv-python/1k=79.22
- `codex` — source=raw_logs | sessions=44 | post_records=31413 | python3/1k=10.16 | uv-python/1k=12.57
- `hermes` — source=raw_logs | sessions=13 | post_records=74634 | python3/1k=18.68 | uv-python/1k=23.61
- `gemini` — source=raw_logs | sessions=39 | post_records=5901 | python3/1k=49.14 | uv-python/1k=6.61

- Migration debt density (known stale reads with redirect hints per 1k records): `gemini` 14.23, `claude` 13.02, `codex` 0.0, `hermes` 0.0.
- Highest-volume known migration debt: `claude` with 972 mapped stale reads across 4 rule clusters; top hotspot: `legacy_work_queue_transition` (318).
- Highest-density known migration debt: `gemini` with 84 mapped stale reads; top hotspot: `legacy_local_work_queue_items` (37, 44.05% of known debt).
- Unmapped missing repo reads remain for: `hermes`; this looks more like general path drift than known migration debt.
- Scope note: Migration-debt figures are based on remediation-mapped entries from each provider's top missing repo reads.

## claude
- Source: raw_logs
- Sessions: 26
- Post-hook records: 74657
- Correction sessions: 0
- Unique runtime sessions: 37
- Prompt-like reads: 70
- Blank read targets: 0
- Missing repo reads: 7560
- Bare python3 bash calls: 644
- `uv run ... python` bash calls: 5914

### claude top tools
- `Bash` — 40503
- `Read` — 14202
- `Edit` — 6810
- `Write` — 6476
- `Grep` — 1836
- `Agent` — 736
- `ToolSearch` — 681
- `TaskUpdate` — 541

### claude top repos
- `workspace-hub` — 71314
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
- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` — 123
- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` — 115
- `scripts/work-queue/close-item.sh` — 94
- `scripts/work-queue/whats-next.sh` — 70
- `.claude/skills/coordination/workspace/work-queue/SKILL.md` — 66
- `scripts/work-queue/archive-item.sh` — 62

### claude top symbolic reads
- none

### claude top Bash command families
- `ls` — 5865
- `grep` — 5207
- `uv run` — 5126
- `cat` — 4306
- `find` — 3138
- `bash` — 2783
- `sed` — 1316
- `git add` — 993

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
- Sessions: 44
- Post-hook records: 31413
- Correction sessions: 0
- Unique runtime sessions: 407
- Prompt-like reads: 0
- Blank read targets: 0
- Missing repo reads: 0
- Bare python3 bash calls: 319
- `uv run ... python` bash calls: 395

### codex top tools
- `Bash` — 30558
- `update_plan` — 750
- `list_mcp_resources` — 31
- `mcp__codex_apps__github_fetch_file` — 27
- `list_mcp_resource_templates` — 16
- `request_user_input` — 10
- `mcp__codex_apps__github_search` — 9
- `spawn_agent` — 4

### codex top repos
- `workspace-hub` — 31413

### codex top reads
- none

### codex top symbolic reads
- none

### codex top Bash command families
- `sed` — 3868
- `rg` — 1739
- `nl` — 1308
- `ls` — 508
- `bash` — 446
- `find` — 423
- `for` — 306
- `git status` — 285

### codex top missing repo reads
- none

### codex remediation hints for stale repo reads
- none

### codex top missing external reads
- none

## hermes
- Source: raw_logs
- Sessions: 13
- Post-hook records: 74634
- Correction sessions: 13
- Unique runtime sessions: 1097
- Prompt-like reads: 797
- Blank read targets: 0
- Missing repo reads: 210
- Bare python3 bash calls: 1394
- `uv run ... python` bash calls: 1762

### hermes top tools
- `Bash` — 35289
- `Read` — 12329
- `Grep` — 12051
- `Write` — 9114
- `Edit` — 3951
- `Task` — 1092
- `Browser` — 347
- `ToolSearch` — 194

### hermes top repos
- `workspace-hub` — 74634

### hermes top reads
- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` — 203
- `config/scheduled-tasks/schedule-tasks.yaml` — 164
- `docs/reports/provider-session-ecosystem-audit.md` — 145
- `analysis/provider-session-ecosystem-audit.json` — 93
- `scripts/_core/sync-agent-configs.sh` — 85
- `scripts/analysis/provider_session_ecosystem_audit.py` — 76
- `scripts/cron/harness-update.sh` — 73
- `scripts/gtm/job-market-scanner.py` — 67
- `docs/plans/README.md` — 65
- `tests/analysis/test_provider_session_ecosystem_audit.py` — 65

### hermes top symbolic reads
- `github-issues` — 119
- `overnight-parallel-agent-prompts` — 81
- `gh-work-planning` — 76
- `claude-code` — 50
- `gh-work-execution` — 49
- `issue-planning-mode` — 48
- `hermes-ecosystem-integration` — 38
- `issue-portfolio-triage` — 36
- `writing-plans` — 35
- `subagent-sandbox-limitations` — 29

### hermes top Bash command families
- `gh` — 6492
- `uv run` — 2922
- `git add` — 1631
- `find` — 1396
- `ls` — 1332
- `git status` — 1153
- `cat` — 1090
- `git log` — 984

### hermes top missing repo reads
- `client_projects/engineering_workbooks/ballymore/jumper_manifold_to_plet/jumper_lift.py` — 24
- `docs/plans/2026-04-10-llm-wiki-resource-doc-repo-integration-blueprint.md` — 18
- `scripts/hooks/pre-push.sh` — 8
- `.planning/quick/review-2239.md` — 8
- `digitalmodel/docs/roadmaps/orcawave-orcaflex-capability-roadmap.md` — 7
- `digitalmodel/docs/assessments/hull-library-audit.md` — 7
- `digitalmodel/specs/module-registry.yaml` — 7
- `docs/handoffs/overnight-llm-wiki-stage1-source-map.md` — 7
- `docs/handoffs/overnight-llm-wiki-stage2-skill-repo-map.md` — 7
- `docs/handoffs/overnight-llm-wiki-stage3-architecture.md` — 7

### hermes remediation hints for stale repo reads
- none

### hermes top missing external reads
- `/home/vamsee/gmail-archive/config/accounts.yaml` — 4
- `/mnt/local-analysis/worktrees/wh-2128/scripts/hooks/pre-push.sh` — 3
- `/home/vamsee/.hermes/skills/mlops/research/dspy/SKILL.md` — 2
- `/tmp/everything-claude-code/README.md` — 2
- `/tmp/everything-claude-code/the-longform-guide.md` — 2
- `/tmp/everything-claude-code/the-shortform-guide.md` — 2
- `/tmp/everything-claude-code/the-security-guide.md` — 2
- `/tmp/everything-claude-code/AGENTS.md` — 2
- `/tmp/everything-claude-code/hooks/hooks.json` — 2
- `/tmp/everything-claude-code/mcp-configs/mcp-servers.json` — 2

## gemini
- Source: raw_logs
- Sessions: 39
- Post-hook records: 5901
- Correction sessions: 0
- Unique runtime sessions: 287
- Prompt-like reads: 18
- Blank read targets: 0
- Missing repo reads: 590
- Bare python3 bash calls: 290
- `uv run ... python` bash calls: 39

### gemini top tools
- `Bash` — 2267
- `Read` — 2035
- `Grep` — 563
- `Write` — 535
- `Edit` — 394
- `Browser` — 97
- `ToolSearch` — 9
- `ask_user` — 1

### gemini top repos
- `workspace-hub` — 5901

### gemini top reads
- `.claude/work-queue/` — 29
- `scripts/operations/compliance/migrate_specs_to_workspace.sh` — 28
- `.` — 22
- `CLAUDE.md` — 21
- `.claude/work-queue` — 17
- `.claude/work-queue/WRK-149.md` — 17
- `digitalmodel/scripts/benchmark/validate_owd_vs_spec.py` — 16
- `.claude/work-queue/pending` — 15
- `digitalmodel/src/digitalmodel` — 15
- `.gitignore` — 12

### gemini top symbolic reads
- `digitalmodel` — 27
- `worldenergydata` — 13
- `assethold` — 8
- `scripts` — 8
- `src` — 7
- `tests` — 7
- `digitalmodel/scripts/python/digitalmodel/modules` — 6
- `config` — 5
- `assetutilities` — 5
- `doris` — 5

### gemini top Bash command families
- `ls` — 463
- `find` — 274
- `cat` — 182
- `python3` — 173
- `grep` — 149
- `git` — 120
- `mkdir` — 78
- `git status` — 72

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
1. Record every provider into `logs/orchestrator/<provider>/session_*.jsonl`; Gemini currently has no corpus, which blocks parity analysis.
2. Treat symbolic skill/tool reads separately from filesystem reads. Hermes emits many skill names in `file`, and counting them as missing files creates noisy false positives.
3. Normalize Codex command logging before analysis. Its spaced command encoding hides policy violations unless commands are de-spaced first.
4. Add a recurring provider audit run that refreshes both JSON and markdown artifacts so refactors can prove drift is shrinking.
5. Keep pushing `uv run ... python` migration. Hermes and Codex still show meaningful bare `python3` usage density.

