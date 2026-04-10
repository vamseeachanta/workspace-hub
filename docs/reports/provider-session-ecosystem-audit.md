# Provider session ecosystem audit — 2026-04-10

Scope: provider session artifacts rooted at `/mnt/local-analysis/workspace-hub/logs/orchestrator` with saved provider artifacts used only as fallback when raw logs are unavailable.

## Executive summary
- `claude` — source=raw_logs | sessions=24 | post_records=73646 | python3/1k=8.62 | uv-python/1k=80.21
- `codex` — source=raw_logs | sessions=42 | post_records=15662 | python3/1k=20.37 | uv-python/1k=25.22
- `hermes` — source=raw_logs | sessions=10 | post_records=58611 | python3/1k=21.69 | uv-python/1k=28.92
- `gemini` — source=raw_logs | sessions=36 | post_records=5884 | python3/1k=49.29 | uv-python/1k=6.63

## claude
- Source: raw_logs
- Sessions: 24
- Post-hook records: 73646
- Correction sessions: 0
- Unique runtime sessions: 0
- Prompt-like reads: 64
- Blank read targets: 0
- Bare python3 bash calls: 635
- `uv run ... python` bash calls: 5907

### claude top tools
- `Bash` — 40093
- `Read` — 13811
- `Edit` — 6724
- `Write` — 6436
- `Grep` — 1758
- `Agent` — 730
- `ToolSearch` — 681
- `TaskUpdate` — 541

### claude top repos
- `workspace-hub` — 70303
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
- Sessions: 42
- Post-hook records: 15662
- Correction sessions: 0
- Unique runtime sessions: 402
- Prompt-like reads: 0
- Blank read targets: 0
- Bare python3 bash calls: 319
- `uv run ... python` bash calls: 395

### codex top tools
- `Bash` — 15256
- `update_plan` — 375
- `list_mcp_resources` — 14
- `list_mcp_resource_templates` — 8
- `request_user_input` — 5
- `spawn_agent` — 2
- `wait_agent` — 1
- `close_agent` — 1

### codex top repos
- `workspace-hub` — 15662

### codex top reads
- none

### codex top symbolic reads
- none

### codex top missing repo reads
- none

### codex top missing external reads
- none

## hermes
- Source: raw_logs
- Sessions: 10
- Post-hook records: 58611
- Correction sessions: 10
- Unique runtime sessions: 900
- Prompt-like reads: 630
- Blank read targets: 0
- Bare python3 bash calls: 1271
- `uv run ... python` bash calls: 1695

### hermes top tools
- `Bash` — 31008
- `Read` — 8944
- `Grep` — 7711
- `Write` — 6574
- `Edit` — 2886
- `Task` — 699
- `Browser` — 347
- `ToolSearch` — 182

### hermes top repos
- `workspace-hub` — 58611

### hermes top reads
- `config/scheduled-tasks/schedule-tasks.yaml` — 130
- `scripts/cron/harness-update.sh` — 73
- `scripts/gtm/job-market-scanner.py` — 67
- `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md` — 49
- `docs/standards/AI_REVIEW_ROUTING_POLICY.md` — 49
- `assetutilities/src/assetutilities/agent_os/commands/create_module_agent.py` — 49
- `scripts/cron/gsd-researcher-nightly.sh` — 47
- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` — 47
- `scripts/monitoring/cron-health-check.sh` — 46
- `/tmp/ballymore_data.json` — 43

### hermes top symbolic reads
- `github-issues` — 82
- `overnight-parallel-agent-prompts` — 65
- `gh-work-planning` — 50
- `gh-work-execution` — 37
- `issue-portfolio-triage` — 35
- `claude-code` — 32
- `writing-plans` — 30
- `hermes-model-switching` — 27
- `workspace-hub-batch-issue-execution` — 26
- `subagent-sandbox-limitations` — 25

### hermes top missing repo reads
- `client_projects/engineering_workbooks/ballymore/jumper_manifold_to_plet/jumper_lift.py` — 24
- `docs/plans/2026-04-10-llm-wiki-resource-doc-repo-integration-blueprint.md` — 8
- `digitalmodel/docs/roadmaps/orcawave-orcaflex-capability-roadmap.md` — 7
- `digitalmodel/docs/assessments/hull-library-audit.md` — 7
- `digitalmodel/specs/module-registry.yaml` — 7
- `docs/handoffs/overnight-llm-wiki-stage1-source-map.md` — 7
- `docs/handoffs/overnight-llm-wiki-stage2-skill-repo-map.md` — 7
- `docs/handoffs/overnight-llm-wiki-stage3-architecture.md` — 7
- `worldenergydata/.planning/quick/gemini-review.txt` — 6
- `scripts/hooks/pre-push.sh` — 6

### hermes top missing external reads
- `/home/vamsee/gmail-archive/config/accounts.yaml` — 4
- `/home/vamsee/.hermes/skills/mlops/research/dspy/SKILL.md` — 2
- `/tmp/everything-claude-code/README.md` — 2
- `/tmp/everything-claude-code/the-longform-guide.md` — 2
- `/tmp/everything-claude-code/the-shortform-guide.md` — 2
- `/tmp/everything-claude-code/the-security-guide.md` — 2
- `/tmp/everything-claude-code/AGENTS.md` — 2
- `/tmp/everything-claude-code/hooks/hooks.json` — 2
- `/tmp/everything-claude-code/mcp-configs/mcp-servers.json` — 2
- `/home/vamsee/.hermes/skills/autonomous-ai-agents/hermes-agent/SKILL.md` — 2

## gemini
- Source: raw_logs
- Sessions: 36
- Post-hook records: 5884
- Correction sessions: 0
- Unique runtime sessions: 282
- Prompt-like reads: 18
- Blank read targets: 0
- Bare python3 bash calls: 290
- `uv run ... python` bash calls: 39

### gemini top tools
- `Bash` — 2266
- `Read` — 2023
- `Grep` — 555
- `Write` — 535
- `Edit` — 394
- `Browser` — 96
- `ToolSearch` — 9
- `search_file_content` — 5

### gemini top repos
- `workspace-hub` — 5884

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

### gemini top missing external reads
- `/tmp/pending-queue-snapshot.txt` — 1
- `/tmp/test-output.md` — 1

## Ecosystem strengthening recommendations
1. Record every provider into `logs/orchestrator/<provider>/session_*.jsonl`; Gemini currently has no corpus, which blocks parity analysis.
2. Treat symbolic skill/tool reads separately from filesystem reads. Hermes emits many skill names in `file`, and counting them as missing files creates noisy false positives.
3. Normalize Codex command logging before analysis. Its spaced command encoding hides policy violations unless commands are de-spaced first.
4. Add a recurring provider audit run that refreshes both JSON and markdown artifacts so refactors can prove drift is shrinking.
5. Keep pushing `uv run ... python` migration. Hermes and Codex still show meaningful bare `python3` usage density.

