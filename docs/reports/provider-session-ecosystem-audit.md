# Provider session ecosystem audit — 2026-04-20

Scope: provider session artifacts rooted at `/mnt/local-analysis/workspace-hub/logs/orchestrator` with saved provider artifacts used only as fallback when raw logs are unavailable.

## Executive summary
- `claude` — source=raw_logs | sessions=32 | post_records=79674 | python3/1k=9.11 | uv-python/1k=74.83
- `codex` — source=raw_logs | sessions=49 | post_records=17284 | python3/1k=19.5 | uv-python/1k=24.36
- `hermes` — source=raw_logs | sessions=17 | post_records=101282 | python3/1k=17.09 | uv-python/1k=20.02
- `gemini` — source=raw_logs | sessions=44 | post_records=6081 | python3/1k=47.85 | uv-python/1k=6.41

- Migration debt density (known stale reads with redirect hints per 1k records): `gemini` 13.81, `claude` 12.2, `codex` 0.0, `hermes` 0.0.
- Highest-volume known migration debt: `claude` with 972 mapped stale reads across 4 rule clusters; top hotspot: `legacy_work_queue_transition` (318).
- Highest-density known migration debt: `gemini` with 84 mapped stale reads; top hotspot: `legacy_local_work_queue_items` (37, 44.05% of known debt).
- Unmapped missing repo reads remain for: `codex`, `hermes`; this looks more like general path drift than known migration debt.
- Scope note: Migration-debt figures are based on remediation-mapped entries from each provider's top missing repo reads.

## Recent activity since previous audit
- Previous audit timestamp: `2026-04-16T23:34:23Z`
- Recent post-audit activity: `claude` 2258 post records / 26 sessions, `codex` 774 post records / 26 sessions, `hermes` 594 post records / 6 sessions, `gemini` 16 post records / 8 sessions.
- Scope note: This is event-time activity since the previous audit timestamp, not a census of newly exported historical/backfilled records.

## claude
- Source: raw_logs
- Sessions: 32
- Post-hook records: 79674
- Correction sessions: 0
- Unique runtime sessions: 134
- Prompt-like reads: 91
- Blank read targets: 0
- Missing repo reads: 7597
- Bare python3 bash calls: 726
- `uv run ... python` bash calls: 5962

### claude top tools
- `Bash` — 43234
- `Read` — 15422
- `Edit` — 7259
- `Write` — 6777
- `Grep` — 2016
- `Agent` — 820
- `ToolSearch` — 681
- `TaskUpdate` — 541

### claude top repos
- `workspace-hub` — 75932
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
- `scripts/work-queue/whats-next.sh` — 70
- `.claude/skills/coordination/workspace/work-queue/SKILL.md` — 66
- `scripts/work-queue/archive-item.sh` — 62

### claude top symbolic reads
- none

### claude top Bash command families
- `ls` — 6340
- `uv run` — 5672
- `grep` — 5376
- `cat` — 4463
- `find` — 3362
- `bash` — 2888
- `sed` — 1336
- `gh` — 1225

### claude recent activity since previous audit
- Post-hook records since prior audit: 2258
- Runtime sessions since prior audit: 26

### claude recent top tools
- `Bash` — 1337
- `Read` — 359
- `Edit` — 302
- `Write` — 173
- `Grep` — 43

### claude recent top Bash command families
- `gh` — 231
- `ls` — 175
- `grep` — 94
- `node` — 81
- `cat` — 70
- `git add` — 57
- `cd` — 52
- `ps` — 46

### claude recent top missing repo reads
- `.claude/worktrees/agent-a34203b3/docs/document-intelligence/pyramid-conformance-checks.md` — 2
- `.claude/worktrees/agent-a1397be7/docs/plans/2026-04-19-revision-dispatch-prompt-2207-provenance-reuse-contract.md` — 1
- `.claude/worktrees/agent-a1397be7/docs/document-intelligence/standards-codes-provenance-reuse-contract.md` — 1
- `.claude/worktrees/agent-a1397be7/docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` — 1
- `.claude/worktrees/agent-a1397be7/scripts/review/results/2026-04-17-plan-2207-claude-adversarial.md` — 1

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
- Sessions: 49
- Post-hook records: 17284
- Correction sessions: 0
- Unique runtime sessions: 476
- Prompt-like reads: 0
- Blank read targets: 0
- Missing repo reads: 119
- Bare python3 bash calls: 337
- `uv run ... python` bash calls: 421

### codex top tools
- `Bash` — 15883
- `update_plan` — 384
- `Read` — 308
- `mcp__codex_apps__github_fetch_file` — 192
- `Grep` — 179
- `list_mcp_resources` — 60
- `mcp__codex_apps__github_search` — 41
- `mcp__codex_apps__github_fetch_issue` — 39

### codex top repos
- `workspace-hub` — 17284

### codex top reads
- `docs/plans/README.md` — 11
- `content/demos/index.html` — 7
- `docs/plans/2026-04-17-issue-2342-2343-demo-detail-pages.md` — 6
- `package.json` — 6
- `docs/standards/HARD-STOP-POLICY.md` — 5
- `build.js` — 5
- `content/demos/jumper-installation.html` — 5
- `content/partials/head-common.html` — 5
- `docs/plans/_template-issue-plan.md` — 4
- `docs/reports/2026-04-17-issue-39-market-hours-signals-consumers-plan.md` — 4

### codex top symbolic reads
- `CNAME` — 2

### codex top Bash command families
- `sed` — 4207
- `rg` — 1781
- `nl` — 1330
- `ls` — 518
- `bash` — 473
- `uv run` — 453
- `find` — 436
- `git status` — 310

### codex recent activity since previous audit
- Post-hook records since prior audit: 774
- Runtime sessions since prior audit: 26

### codex recent top tools
- `Read` — 302
- `Grep` — 173
- `Bash` — 141
- `_fetch` — 33
- `_fetch_issue` — 20

### codex recent top Bash command families
- `sed` — 84
- `pwd` — 11
- `nl` — 11
- `rg` — 8
- `mkdir` — 3
- `git show` — 3
- `git status` — 2
- `git` — 2

### codex recent top missing repo reads
- `content/demos/index.html` — 7
- `package.json` — 6
- `build.js` — 5
- `content/demos/jumper-installation.html` — 5
- `content/partials/head-common.html` — 5

### codex top missing repo reads
- `content/demos/index.html` — 7
- `package.json` — 6
- `build.js` — 5
- `content/demos/jumper-installation.html` — 5
- `content/partials/head-common.html` — 5
- `docs/reports/2026-04-17-issue-39-market-hours-signals-consumers-plan.md` — 4
- `examples/demos/gtm/output/demo_02_wall_thickness_report.html` — 4
- `examples/demos/gtm/output/demo_03_mudmat_installation_report.html` — 4
- `vercel.json` — 4
- `examples/demos/gtm/output/demo_01_freespan_report.html` — 3

### codex remediation hints for stale repo reads
- none

### codex top missing external reads
- none

## hermes
- Source: raw_logs
- Sessions: 17
- Post-hook records: 101282
- Correction sessions: 17
- Unique runtime sessions: 1331
- Prompt-like reads: 862
- Blank read targets: 26
- Missing repo reads: 268
- Bare python3 bash calls: 1731
- `uv run ... python` bash calls: 2028

### hermes top tools
- `Bash` — 45590
- `Read` — 17976
- `Grep` — 16129
- `Write` — 12578
- `Edit` — 6525
- `Task` — 1344
- `Browser` — 512
- `ToolSearch` — 221

### hermes top repos
- `workspace-hub` — 101282

### hermes top reads
- `config/scheduled-tasks/schedule-tasks.yaml` — 238
- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` — 233
- `docs/reports/provider-session-ecosystem-audit.md` — 199
- `docs/plans/README.md` — 189
- `analysis/provider-session-ecosystem-audit.json` — 128
- `scripts/_core/sync-agent-configs.sh` — 90
- `scripts/cron/harness-update.sh` — 88
- `scripts/analysis/provider_session_ecosystem_audit.py` — 86
- `docs/plans/_template-issue-plan.md` — 82
- `tests/analysis/test_provider_session_ecosystem_audit.py` — 76

### hermes top symbolic reads
- `github/github-issues` — 219
- `github-issues` — 145
- `coordination/issue-planning-mode` — 139
- `autonomous-ai-agents/claude-code` — 124
- `gh-work-planning` — 85
- `overnight-parallel-agent-prompts` — 81
- `coordination/cross-review-policy` — 72
- `issue-planning-mode` — 70
- `claude-code` — 65
- `coordination/session-start-routine` — 65

### hermes top Bash command families
- `gh` — 9082
- `uv run` — 3467
- `git add` — 1789
- `git status` — 1630
- `find` — 1421
- `ls` — 1360
- `cat` — 1243
- `git log` — 1084

### hermes recent activity since previous audit
- Post-hook records since prior audit: 594
- Runtime sessions since prior audit: 6

### hermes recent top tools
- `Bash` — 217
- `Read` — 157
- `Grep` — 102
- `Write` — 79
- `Edit` — 39

### hermes recent top Bash command families
- `gh` — 98
- `uv run` — 21
- `git status` — 10
- `bash` — 9
- `pwd` — 6
- `date` — 4
- `claude` — 4
- `env` — 3

### hermes recent top missing repo reads
- none

### hermes top missing repo reads
- `client_projects/engineering_workbooks/ballymore/jumper_manifold_to_plet/jumper_lift.py` — 24
- `docs/plans/2026-04-10-llm-wiki-resource-doc-repo-integration-blueprint.md` — 18
- `scripts/hooks/pre-push.sh` — 14
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
- Sessions: 44
- Post-hook records: 6081
- Correction sessions: 0
- Unique runtime sessions: 317
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
- `Browser` — 103
- `ToolSearch` — 9
- `ask_user` — 1

### gemini top repos
- `workspace-hub` — 6081

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
- Post-hook records since prior audit: 16
- Runtime sessions since prior audit: 8

### gemini recent top tools
- `Read` — 8
- `Browser` — 4
- `Grep` — 3
- `Bash` — 1

### gemini recent top Bash command families
- `cat` — 1

### gemini recent top missing repo reads
- none

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

