# Provider session ecosystem audit — 2026-04-10

Scope: provider session artifacts rooted at `/mnt/local-analysis/workspace-hub/logs/orchestrator` with saved provider artifacts used only as fallback when raw logs are unavailable.

## Executive summary
- `claude` — source=raw_logs | sessions=24 | post_records=73646 | python3/1k=8.62 | uv-python/1k=80.21
- `codex` — source=raw_logs | sessions=41 | post_records=15589 | python3/1k=20.46 | uv-python/1k=25.15
- `hermes` — source=raw_logs | sessions=9 | post_records=69971 | python3/1k=24.1 | uv-python/1k=31.27
- `gemini` — source=raw_logs | sessions=36 | post_records=4585 | python3/1k=43.62 | uv-python/1k=6.98

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
- Sessions: 41
- Post-hook records: 15589
- Correction sessions: 0
- Unique runtime sessions: 400
- Prompt-like reads: 0
- Blank read targets: 0
- Bare python3 bash calls: 319
- `uv run ... python` bash calls: 392

### codex top tools
- `Bash` — 15183
- `update_plan` — 375
- `list_mcp_resources` — 14
- `list_mcp_resource_templates` — 8
- `request_user_input` — 5
- `spawn_agent` — 2
- `wait_agent` — 1
- `close_agent` — 1

### codex top repos
- `workspace-hub` — 15589

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
- Sessions: 9
- Post-hook records: 69971
- Correction sessions: 9
- Unique runtime sessions: 0
- Prompt-like reads: 533
- Blank read targets: 639
- Bare python3 bash calls: 1686
- `uv run ... python` bash calls: 2188

### hermes top tools
- `Bash` — 38403
- `Read` — 10908
- `Write` — 7910
- `Grep` — 7807
- `Edit` — 3474
- `Task` — 807
- `Browser` — 367
- `UserInput` — 144

### hermes top repos
- `workspace-hub` — 69971

### hermes top reads
- `config/scheduled-tasks/schedule-tasks.yaml` — 167
- `scripts/cron/harness-update.sh` — 112
- `scripts/gtm/job-market-scanner.py` — 89
- `docs/standards/AI_REVIEW_ROUTING_POLICY.md` — 77
- `scripts/cron/gsd-researcher-nightly.sh` — 72
- `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md` — 65
- `scripts/monitoring/cron-health-check.sh` — 53
- `assetutilities/src/assetutilities/agent_os/commands/create_module_agent.py` — 49
- `docs/work-queue-workflow.md` — 47
- `docs/roadmaps/orcawave-orcaflex-capability-roadmap.md` — 47

### hermes top symbolic reads
- `github-issues` — 112
- `overnight-parallel-agent-prompts` — 72
- `gh-work-planning` — 50
- `writing-plans` — 47
- `issue-portfolio-triage` — 40
- `gh-work-execution` — 37
- `gsd-operational-audit` — 34
- `multi-provider-adversarial-review` — 27
- `hermes-model-switching` — 27
- `claude-code` — 27

### hermes top missing repo reads
- `client_projects/engineering_workbooks/ballymore/jumper_manifold_to_plet/jumper_lift.py` — 27
- `digitalmodel/docs/roadmaps/orcawave-orcaflex-capability-roadmap.md` — 9
- `digitalmodel/docs/assessments/hull-library-audit.md` — 9
- `digitalmodel/specs/module-registry.yaml` — 9
- `worldenergydata/.planning/quick/gemini-review.txt` — 9
- `.planning/research/2026-04-01-python-ecosystem.md` — 8
- `.planning/skills/evals/workflow-gatepass.yaml` — 6
- `.planning/skills/evals/work-queue.yaml` — 6
- `scripts/quality/tests/test_doc_staleness_scanner.py` — 6
- `config/cron/schedule-tasks.yaml` — 6

### hermes top missing external reads
- `/home/vamsee/gmail-archive/config/accounts.yaml` — 4
- `/home/vamsee/workspace-hub/config/scheduled-tasks/schedule-tasks.yaml` — 2
- `/home/vamsee/workspace-hub/.claude/settings.json` — 2
- `/home/vamsee/.hermes/skills/mlops/research/dspy/SKILL.md` — 2
- `/tmp/everything-claude-code/README.md` — 2
- `/tmp/everything-claude-code/the-longform-guide.md` — 2
- `/tmp/everything-claude-code/the-shortform-guide.md` — 2
- `/tmp/everything-claude-code/the-security-guide.md` — 2
- `/tmp/everything-claude-code/AGENTS.md` — 2
- `/tmp/everything-claude-code/hooks/hooks.json` — 2

## gemini
- Source: raw_logs
- Sessions: 36
- Post-hook records: 4585
- Correction sessions: 0
- Unique runtime sessions: 282
- Prompt-like reads: 16
- Blank read targets: 6
- Bare python3 bash calls: 200
- `uv run ... python` bash calls: 32

### gemini top tools
- `Bash` — 1720
- `Read` — 1603
- `Grep` — 458
- `Write` — 379
- `Edit` — 324
- `Browser` — 96
- `search_file_content` — 4
- `ask_user` — 1

### gemini top repos
- `workspace-hub` — 4585

### gemini top reads
- `.claude/work-queue/` — 29
- `.claude/work-queue/WRK-149.md` — 16
- `digitalmodel/scripts/benchmark/validate_owd_vs_spec.py` — 16
- `CLAUDE.md` — 15
- `scripts/operations/compliance/migrate_specs_to_workspace.sh` — 14
- `.claude/work-queue/pending` — 14
- `.` — 13
- `.claude/work-queue` — 13
- `.claude/skills/coordination/workspace/work-queue/SKILL.md` — 12
- `digitalmodel/src/digitalmodel` — 11

### gemini top symbolic reads
- `digitalmodel` — 20
- `worldenergydata` — 10
- `assethold` — 6
- `scripts` — 6
- `src` — 5
- `tests` — 5
- `doris` — 5
- `assetutilities` — 4
- `config` — 3
- `digitalmodel/scripts/python/digitalmodel/modules` — 3

### gemini top missing repo reads
- `.claude/work-queue/WRK-149.md` — 16
- `.claude/skills/coordination/workspace/work-queue/SKILL.md` — 12
- `.claude/work-queue/working` — 11
- `.claude/work-queue/working/` — 8
- `scripts/agents/lib/workflow-guards.sh` — 7
- `.gitmodules` — 6
- `scripts/agents/plan.sh` — 6
- `scripts/work-queue/generate-html-review.py` — 6
- `scripts/agents/execute.sh` — 5
- `.claude/hooks/post-task-review.sh` — 5

### gemini top missing external reads
- `/tmp/pending-queue-snapshot.txt` — 1
- `/tmp/test-output.md` — 1

## Ecosystem strengthening recommendations
1. Record every provider into `logs/orchestrator/<provider>/session_*.jsonl`; Gemini currently has no corpus, which blocks parity analysis.
2. Treat symbolic skill/tool reads separately from filesystem reads. Hermes emits many skill names in `file`, and counting them as missing files creates noisy false positives.
3. Normalize Codex command logging before analysis. Its spaced command encoding hides policy violations unless commands are de-spaced first.
4. Add a recurring provider audit run that refreshes both JSON and markdown artifacts so refactors can prove drift is shrinking.
5. Keep pushing `uv run ... python` migration. Hermes and Codex still show meaningful bare `python3` usage density.

