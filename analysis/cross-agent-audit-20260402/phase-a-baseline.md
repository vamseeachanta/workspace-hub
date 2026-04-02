# Phase A — Cross-Agent Tool & File Frequency Baseline

## Issue: #1720 | Date: 2026-04-02

---

## 0. Corpus Summary

| Agent | Sessions | Total Records | Post-hook Records | Date Range |
|-------|----------|---------------|-------------------|------------|
| Claude | 24 | 153,859 | 73,646 | 2026-03-02 → 2026-03-25 |
| Hermes | 2 | 13,554 | 13,554 | 2026-04-01 → 2026-04-02 |
| Codex | 399 | 409 | — (text logs) | — |

**Total structured records**: 167,413
**Codex**: 371 code review verdicts, 2 WRK log entries across 399 log files

Note: Codex logs are predominantly plain-text review verdicts (`### Verdict: APPROVE/MINOR/MAJOR`)
and WRK execution entries. They lack structured tool-call data, so Codex is excluded from
file-frequency and command analyses below. Codex tool distribution reflects log categories only.

---

## 1. Top 50 Files by READ Frequency

### Combined (Claude + Hermes)

| Rank | File | Reads |
|------|------|-------|
| 1 | `scripts/work-queue/verify-gate-evidence.py` | 732 |
| 2 | `scripts/work-queue/generate-html-review.py` | 249 |
| 3 | `scripts/work-queue/exit_stage.py` | 137 |
| 4 | `scripts/work-queue/start_stage.py` | 135 |
| 5 | `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` | 120 |
| 6 | `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` | 115 |
| 7 | `scripts/work-queue/close-item.sh` | 94 |
| 8 | `scripts/work-queue/whats-next.sh` | 70 |
| 9 | `.claude/skills/coordination/workspace/work-queue/SKILL.md` | 66 |
| 10 | `scripts/work-queue/archive-item.sh` | 61 |
| 11 | `scripts/work-queue/claim-item.sh` | 60 |
| 12 | `config/scheduled-tasks/schedule-tasks.yaml` | 55 |
| 13 | `scripts/data/doc_intelligence/schema.py` | 49 |
| 14 | `scripts/quality/check-all.sh` | 47 |
| 15 | `scripts/review/cross-review.sh` | 46 |
| 16 | `.claude/settings.json` | 46 |
| 17 | `.claude/skills/development/skill-eval/scripts/eval-skills.py` | 45 |
| 18 | `scripts/work-queue/verify_checklist.py` | 43 |
| 19 | `scripts/work-queue/stages/stage-01-capture.yaml` | 42 |
| 20 | `scripts/review/submit-to-codex.sh` | 41 |
| 21 | `scripts/cron/comprehensive-learning-nightly.sh` | 41 |
| 22 | `scripts/knowledge/update-github-issue.py` | 41 |
| 23 | `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md` | 37 |
| 24 | `scripts/work-queue/stages/stage-05-user-review-plan-draft.yaml` | 35 |
| 25 | `assetutilities/src/assetutilities/common/data.py` | 34 |
| 26 | `.claude/work-queue/scripts/generate-index.py` | 33 |
| 27 | `.claude/hooks/enforce-active-stage.sh` | 33 |
| 28 | `scripts/learning/comprehensive-learning.sh` | 32 |
| 29 | `scripts/work-queue/stage_exit_checks.py` | 32 |
| 30 | `.claude/skills/workspace-hub/comprehensive-learning/SKILL.md` | 31 |
| 31 | `knowledge/seeds/naval-architecture-resources.yaml` | 31 |
| 32 | `scripts/cron/harness-update.sh` | 31 |
| 33 | `.claude/skills/workspace-hub/session-start/SKILL.md` | 30 |
| 34 | `tests/unit/test_generate_html_review.py` | 30 |
| 35 | `github-issues` | 30 |
| 36 | `scripts/work-queue/stages/stage-10-work-execution.yaml` | 29 |
| 37 | `scripts/data/document-index/config.yaml` | 29 |
| 38 | `AGENTS.md` | 28 |
| 39 | `scripts/work-queue/stages/stage-07-user-review-plan-final.yaml` | 28 |
| 40 | `.claude/skills/workspace-hub/workflow-html/SKILL.md` | 27 |
| 41 | `scripts/work-queue/gate_checks_extra.py` | 27 |
| 42 | `scripts/analysis/session-analysis.sh` | 26 |
| 43 | `scripts/cron/setup-cron.sh` | 26 |
| 44 | `digitalmodel/src/digitalmodel/cathodic_protection/__init__.py` | 26 |
| 45 | `data/document-index/standards-transfer-ledger.yaml` | 26 |
| 46 | `scripts/data/naval-architecture/download-naval-arch-docs.sh` | 26 |
| 47 | `scripts/data/document-index/phase-b-extract.py` | 26 |
| 48 | `.claude/skills/engineering/doc-extraction/SKILL.md` | 26 |
| 49 | `scripts/data/doc-intelligence/extract-document.py` | 26 |
| 50 | `scripts/agents/work.sh` | 25 |

### Claude Only (Top 30)

| Rank | File | Reads |
|------|------|-------|
| 1 | `scripts/work-queue/verify-gate-evidence.py` | 732 |
| 2 | `scripts/work-queue/generate-html-review.py` | 249 |
| 3 | `scripts/work-queue/exit_stage.py` | 137 |
| 4 | `scripts/work-queue/start_stage.py` | 135 |
| 5 | `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` | 120 |
| 6 | `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` | 115 |
| 7 | `scripts/work-queue/close-item.sh` | 94 |
| 8 | `scripts/work-queue/whats-next.sh` | 70 |
| 9 | `.claude/skills/coordination/workspace/work-queue/SKILL.md` | 66 |
| 10 | `scripts/work-queue/archive-item.sh` | 61 |
| 11 | `scripts/work-queue/claim-item.sh` | 60 |
| 12 | `scripts/quality/check-all.sh` | 47 |
| 13 | `scripts/data/doc_intelligence/schema.py` | 47 |
| 14 | `.claude/skills/development/skill-eval/scripts/eval-skills.py` | 45 |
| 15 | `scripts/review/cross-review.sh` | 43 |
| 16 | `scripts/work-queue/verify_checklist.py` | 43 |
| 17 | `scripts/work-queue/stages/stage-01-capture.yaml` | 42 |
| 18 | `scripts/review/submit-to-codex.sh` | 41 |
| 19 | `scripts/knowledge/update-github-issue.py` | 41 |
| 20 | `.claude/settings.json` | 39 |
| 21 | `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md` | 37 |
| 22 | `scripts/cron/comprehensive-learning-nightly.sh` | 35 |
| 23 | `scripts/work-queue/stages/stage-05-user-review-plan-draft.yaml` | 35 |
| 24 | `assetutilities/src/assetutilities/common/data.py` | 34 |
| 25 | `.claude/work-queue/scripts/generate-index.py` | 33 |
| 26 | `.claude/hooks/enforce-active-stage.sh` | 33 |
| 27 | `scripts/learning/comprehensive-learning.sh` | 32 |
| 28 | `scripts/work-queue/stage_exit_checks.py` | 32 |
| 29 | `.claude/skills/workspace-hub/comprehensive-learning/SKILL.md` | 30 |
| 30 | `.claude/skills/workspace-hub/session-start/SKILL.md` | 30 |

### Hermes Only (Top 30)

| Rank | File | Reads |
|------|------|-------|
| 1 | `config/scheduled-tasks/schedule-tasks.yaml` | 44 |
| 2 | `scripts/cron/harness-update.sh` | 31 |
| 3 | `github-issues` | 30 |
| 4 | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` | 25 |
| 5 | `scripts/cron/gsd-researcher-nightly.sh` | 25 |
| 6 | `docs/strategy/gtm/job-market-scan/dashboard.md` | 22 |
| 7 | `scripts/maintenance/ai-tools-status.sh` | 20 |
| 8 | `docs/modules/tiers/TIER2_REPOSITORY_INDEX.md` | 20 |
| 9 | `overnight-parallel-agent-prompts` | 18 |
| 10 | `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md` | 17 |
| 11 | `gsd-operational-audit` | 17 |
| 12 | `docs/work-queue-workflow.md` | 16 |
| 13 | `data/document-index/registry.yaml` | 16 |
| 14 | `.claude/get-shit-done/bin/lib/state.cjs` | 15 |
| 15 | `docs/roadmaps/orcawave-orcaflex-capability-roadmap.md` | 15 |
| 16 | `writing-plans` | 14 |
| 17 | `data/document-index/standards-transfer-ledger.yaml` | 14 |
| 18 | `scripts/gtm/job-market-scanner.py` | 14 |
| 19 | `digitalmodel/src/digitalmodel/fatigue/sn_library.py` | 13 |
| 20 | `docs/plans/2026-04-01-orcawave-orcaflex-intensive-plan.md` | 12 |
| 21 | `docs/architecture/digitalmodel-architecture.md` | 12 |
| 22 | `data/document-index/enhancement-plan.yaml` | 11 |
| 23 | `.claude/hooks/cross-review-gate.sh` | 11 |
| 24 | `multi-provider-adversarial-review` | 11 |
| 25 | `docs/ops/scheduled-tasks.md` | 10 |
| 26 | `data/document-index/mounted-source-registry.yaml` | 10 |
| 27 | `scripts/cron/setup-cron.sh` | 10 |
| 28 | `docs/research/engineering-capability-map.md` | 10 |
| 29 | `scripts/_core/sync-agent-configs.sh` | 10 |
| 30 | `skeleton-test-coverage-uplift` | 10 |

---

## 2. Top 50 Files by WRITE/EDIT Frequency

### Combined (Claude + Hermes)

| Rank | File | Writes |
|------|------|--------|
| 1 | `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` | 130 |
| 2 | `scripts/work-queue/generate-html-review.py` | 116 |
| 3 | `scripts/work-queue/whats-next.sh` | 89 |
| 4 | `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` | 67 |
| 5 | `assetutilities/src/assetutilities/common/data.py` | 61 |
| 6 | `specs/wrk/WRK-658/plan.md` | 61 |
| 7 | `scripts/work-queue/verify-gate-evidence.py` | 58 |
| 8 | `scripts/work-queue/start_stage.py` | 57 |
| 9 | `scripts/work-queue/exit_stage.py` | 50 |
| 10 | `.claude/work-queue/assets/WRK-1028/plan-draft-review.html` | 47 |
| 11 | `.claude/skills/coordination/workspace/work-queue/SKILL.md` | 45 |
| 12 | `.claude/work-queue/assets/WRK-1028/WRK-1028-lifecycle.html` | 41 |
| 13 | `scripts/quality/check-all.sh` | 40 |
| 14 | `specs/wrk/WRK-1105/plan.md` | 38 |
| 15 | `specs/wrk/WRK-1035/plan.md` | 35 |
| 16 | `config/scheduled-tasks/schedule-tasks.yaml` | 34 |
| 17 | `.claude/work-queue/pending/WRK-1006.md` | 33 |
| 18 | `.claude/skills/workspace-hub/workflow-html/SKILL.md` | 33 |
| 19 | `/mnt/workspace-hub/.claude/work-queue/assets/WRK-5082/geometry-dimensions-WRK-1360.md` | 33 |
| 20 | `scripts/analysis/module_status_matrix.py` | 32 |
| 21 | `.claude/skills/development/skill-eval/scripts/eval-skills.py` | 31 |
| 22 | `assetutilities/src/assetutilities/common/yml_utilities.py` | 30 |
| 23 | `/tmp/issue-1668-revised.md` | 30 |
| 24 | `.claude/work-queue/pending/WRK-5082.md` | 26 |
| 25 | `digitalmodel/tests/reservoir/test_stratigraphic.py` | 24 |
| 26 | `scripts/gtm/job-market-scanner.py` | 22 |
| 27 | `scripts/cron/comprehensive-learning-nightly.sh` | 21 |
| 28 | `.claude/work-queue/assets/WRK-1244/plan.md` | 21 |
| 29 | `.claude/settings.json` | 20 |
| 30 | `.claude/work-queue/pending/WRK-234.md` | 20 |
| 31 | `scripts/monitoring/tests/test_cron_health_check.sh` | 20 |
| 32 | `.claude/work-queue/pending/WRK-1001.md` | 19 |
| 33 | `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md` | 19 |
| 34 | `scripts/review/cross-review.sh` | 19 |
| 35 | `scripts/work-queue/close-item.sh` | 19 |
| 36 | `teamresumes/cv/gp/custom/Geeta_CV_Recommendations.md` | 19 |
| 37 | `specs/wrk/WRK-1127/wrk-1127-feature-first-planning.md` | 19 |
| 38 | `docs/modules/tiers/TIER2_REPOSITORY_INDEX.md` | 19 |
| 39 | `scripts/operations/connection/vnc-dev-secondary.sh` | 18 |
| 40 | `.claude/work-queue/assets/WRK-1036/stage-state.yaml` | 18 |
| 41 | `scripts/work-queue/archive-item.sh` | 18 |
| 42 | `scripts/work-queue/dep_graph.py` | 18 |
| 43 | `.claude/docs/roadmap-2026-h1.md` | 18 |
| 44 | `scripts/data/document-index/assess-deep-extraction-yield.py` | 18 |
| 45 | `tests/analysis/test_module_status_matrix.py` | 18 |
| 46 | `scripts/work-queue/claim-item.sh` | 17 |
| 47 | `docs/superpowers/plans/2026-03-13-stream-a-data-completeness.md` | 17 |
| 48 | `specs/modules/virtual-dancing-thimble.md` | 16 |
| 49 | `docs/superpowers/plans/2026-03-13-stream-b-calculation-coverage.md` | 16 |
| 50 | `specs/modules/wrk-1247-xlsx-formula-extraction-poc.md` | 16 |

### Claude Only (Top 30)

| Rank | File | Writes |
|------|------|--------|
| 1 | `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` | 130 |
| 2 | `scripts/work-queue/generate-html-review.py` | 116 |
| 3 | `scripts/work-queue/whats-next.sh` | 89 |
| 4 | `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` | 67 |
| 5 | `assetutilities/src/assetutilities/common/data.py` | 61 |
| 6 | `specs/wrk/WRK-658/plan.md` | 61 |
| 7 | `scripts/work-queue/verify-gate-evidence.py` | 58 |
| 8 | `scripts/work-queue/start_stage.py` | 57 |
| 9 | `scripts/work-queue/exit_stage.py` | 50 |
| 10 | `.claude/work-queue/assets/WRK-1028/plan-draft-review.html` | 47 |
| 11 | `.claude/skills/coordination/workspace/work-queue/SKILL.md` | 45 |
| 12 | `.claude/work-queue/assets/WRK-1028/WRK-1028-lifecycle.html` | 41 |
| 13 | `scripts/quality/check-all.sh` | 40 |
| 14 | `specs/wrk/WRK-1105/plan.md` | 38 |
| 15 | `specs/wrk/WRK-1035/plan.md` | 35 |
| 16 | `.claude/work-queue/pending/WRK-1006.md` | 33 |
| 17 | `.claude/skills/workspace-hub/workflow-html/SKILL.md` | 33 |
| 18 | `/mnt/workspace-hub/.claude/work-queue/assets/WRK-5082/geometry-dimensions-WRK-1360.md` | 33 |
| 19 | `.claude/skills/development/skill-eval/scripts/eval-skills.py` | 31 |
| 20 | `assetutilities/src/assetutilities/common/yml_utilities.py` | 30 |
| 21 | `.claude/work-queue/pending/WRK-5082.md` | 26 |
| 22 | `.claude/work-queue/assets/WRK-1244/plan.md` | 21 |
| 23 | `.claude/work-queue/pending/WRK-234.md` | 20 |
| 24 | `.claude/work-queue/pending/WRK-1001.md` | 19 |
| 25 | `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md` | 19 |
| 26 | `scripts/review/cross-review.sh` | 19 |
| 27 | `scripts/work-queue/close-item.sh` | 19 |
| 28 | `teamresumes/cv/gp/custom/Geeta_CV_Recommendations.md` | 19 |
| 29 | `specs/wrk/WRK-1127/wrk-1127-feature-first-planning.md` | 19 |
| 30 | `scripts/operations/connection/vnc-dev-secondary.sh` | 18 |

### Hermes Only (Top 30)

| Rank | File | Writes |
|------|------|--------|
| 1 | `scripts/analysis/module_status_matrix.py` | 32 |
| 2 | `/tmp/issue-1668-revised.md` | 30 |
| 3 | `config/scheduled-tasks/schedule-tasks.yaml` | 27 |
| 4 | `digitalmodel/tests/reservoir/test_stratigraphic.py` | 24 |
| 5 | `scripts/gtm/job-market-scanner.py` | 22 |
| 6 | `scripts/monitoring/tests/test_cron_health_check.sh` | 20 |
| 7 | `docs/modules/tiers/TIER2_REPOSITORY_INDEX.md` | 19 |
| 8 | `tests/analysis/test_module_status_matrix.py` | 18 |
| 9 | `scripts/cron/gsd-researcher-nightly.sh` | 15 |
| 10 | `scripts/quality/test-health-dashboard.py` | 15 |
| 11 | `scripts/document-intelligence/batch-process-standards.py` | 15 |
| 12 | `docs/strategy/gtm/job-market-scan/README.md` | 15 |
| 13 | `scripts/analysis/repo_architecture_scanner.py` | 12 |
| 14 | `docs/plans/2026-04-01-orcawave-orcaflex-intensive-plan.md` | 11 |
| 15 | `scripts/analysis/architecture-scanner.py` | 11 |
| 16 | `scripts/monitoring/cron-health-check.sh` | 10 |
| 17 | `docs/roadmaps/orcawave-orcaflex-capability-roadmap.md` | 10 |
| 18 | `.claude/docs/self-learning-workflow.md` | 9 |
| 19 | `scripts/cron/setup-cron.sh` | 9 |
| 20 | `tests/analysis/test_repo_architecture_scanner.py` | 9 |
| 21 | `tests/solver/test_queue_health.py` | 9 |
| 22 | `digitalmodel/tests/orcaflex/test_qa.py` | 9 |
| 23 | `docs/assessments/hull-library-audit.md` | 8 |
| 24 | `scripts/_core/sync-agent-configs.sh` | 8 |
| 25 | `docs/ops/scheduled-tasks.md` | 8 |
| 26 | `/tmp/issue-1668-body.md` | 8 |
| 27 | `scripts/cron/harness-update.sh` | 8 |
| 28 | `scripts/maintenance/ai-tools-status.sh` | 8 |
| 29 | `digitalmodel/src/digitalmodel/cathodic_protection/__init__.py` | 8 |
| 30 | `.claude/hooks/cross-review-gate.sh` | 7 |

---

## 3. Top 20 Bash Commands

### Claude

| Rank | Command | Count |
|------|---------|-------|
| 1 | `ls` | 5658 |
| 2 | `grep/search` | 4934 |
| 3 | `uv run` | 4849 |
| 4 | `cat <file>` | 4075 |
| 5 | `find` | 3054 |
| 6 | `bash` | 2700 |
| 7 | `#` | 1574 |
| 8 | `sed` | 1240 |
| 9 | `cd <dir>` | 979 |
| 10 | `git add` | 875 |
| 11 | `ssh` | 785 |
| 12 | `head <file>` | 731 |
| 13 | `git log` | 604 |
| 14 | `mkdir` | 563 |
| 15 | `sleep` | 521 |
| 16 | `git status` | 461 |
| 17 | `wc` | 460 |
| 18 | `gh issue` | 418 |
| 19 | `for` | 391 |
| 20 | `git diff` | 329 |

### Hermes

| Rank | Command | Count |
|------|---------|-------|
| 1 | `cd <dir>` | 5189 |
| 2 | `gh issue` | 400 |
| 3 | `#` | 204 |
| 4 | `ls` | 199 |
| 5 | `find` | 122 |
| 6 | `mkdir` | 57 |
| 7 | `cat <file>` | 51 |
| 8 | `chmod` | 39 |
| 9 | `head <file>` | 38 |
| 10 | `node` | 33 |
| 11 | `python` | 32 |
| 12 | `grep/search` | 30 |
| 13 | `pip` | 24 |
| 14 | `wc` | 22 |
| 15 | `rm` | 19 |
| 16 | `pwd` | 19 |
| 17 | `bash` | 18 |
| 18 | `echo` | 18 |
| 19 | `~/.hermes/hermes-agent/.venv/bin/python3` | 16 |
| 20 | `/home/vamsee/miniforge3/bin/python` | 16 |

---

## 4. Tool Call Distribution

### Claude

Total post-hook calls: **73,646**

| Tool | Count | Pct |
|------|-------|-----|
| Bash | 40,093 | 54.4% |
| Read | 13,811 | 18.8% |
| Edit | 6,724 | 9.1% |
| Write | 6,436 | 8.7% |
| Grep | 1,758 | 2.4% |
| Agent | 730 | 1.0% |
| ToolSearch | 681 | 0.9% |
| TaskUpdate | 541 | 0.7% |
| WebSearch | 519 | 0.7% |
| Glob | 392 | 0.5% |
| TaskOutput | 323 | 0.4% |
| Skill | 309 | 0.4% |
| TaskCreate | 280 | 0.4% |
| StructuredOutput | 257 | 0.3% |
| WebFetch | 221 | 0.3% |
| mcp__claude-in-chrome__computer | 110 | 0.1% |
| mcp__claude-in-chrome__navigate | 94 | 0.1% |
| mcp__claude-in-chrome__javascript_tool | 94 | 0.1% |
| EnterPlanMode | 83 | 0.1% |
| TaskStop | 34 | 0.0% |
| unknown | 32 | 0.0% |
| mcp__claude-in-chrome__tabs_context_mcp | 29 | 0.0% |
| AskUserQuestion | 18 | 0.0% |
| ExitPlanMode | 17 | 0.0% |
| mcp__claude-in-chrome__read_page | 12 | 0.0% |
| mcp__claude-in-chrome__get_page_text | 12 | 0.0% |
| mcp__claude-in-chrome__tabs_create_mcp | 10 | 0.0% |
| TaskList | 8 | 0.0% |
| SendMessage | 5 | 0.0% |
| mcp__claude-in-chrome__find | 4 | 0.0% |
| CronCreate | 3 | 0.0% |
| mcp__claude-in-chrome__form_input | 3 | 0.0% |
| CronDelete | 1 | 0.0% |
| TeamCreate | 1 | 0.0% |
| TaskGet | 1 | 0.0% |

### Hermes

Total post-hook calls: **13,554**

| Tool | Count | Pct |
|------|-------|-----|
| terminal | 6,691 | 49.4% |
| read_file | 2,044 | 15.1% |
| search_files | 1,410 | 10.4% |
| write_file | 724 | 5.3% |
| todo | 692 | 5.1% |
| execute_code | 558 | 4.1% |
| patch | 555 | 4.1% |
| skill_view | 169 | 1.2% |
| memory | 169 | 1.2% |
| skill_manage | 124 | 0.9% |
| delegate_task | 102 | 0.8% |
| process | 102 | 0.8% |
| session_search | 90 | 0.7% |
| skills_list | 86 | 0.6% |
| clarify | 20 | 0.1% |
| browser_navigate | 9 | 0.1% |
| cronjob | 7 | 0.1% |
| browser_close | 2 | 0.0% |

### Codex (log categories only)

Total log entries: **409**

| Category | Count | Pct |
|----------|-------|-----|
| Review | 371 | 90.7% |
| unknown | 36 | 8.8% |
| LogEntry | 2 | 0.5% |

---

## 5. Temporal Pattern — Tool Calls per Day

| Date | Claude | Hermes | Combined |
|------|--------|--------|----------|
| 2026-03-02 | 146 | 0 | 146 |
| 2026-03-03 | 749 | 0 | 749 |
| 2026-03-04 | 456 | 0 | 456 |
| 2026-03-05 | 462 | 0 | 462 |
| 2026-03-06 | 512 | 0 | 512 |
| 2026-03-07 | 2,474 | 0 | 2,474 |
| 2026-03-08 | 5,551 | 0 | 5,551 |
| 2026-03-09 | 8,278 | 0 | 8,278 |
| 2026-03-10 | 7,811 | 0 | 7,811 |
| 2026-03-11 | 4,893 | 0 | 4,893 |
| 2026-03-12 | 6,787 | 0 | 6,787 |
| 2026-03-13 | 5,778 | 0 | 5,778 |
| 2026-03-14 | 3,272 | 0 | 3,272 |
| 2026-03-15 | 2,928 | 0 | 2,928 |
| 2026-03-16 | 5,338 | 0 | 5,338 |
| 2026-03-17 | 2,120 | 0 | 2,120 |
| 2026-03-18 | 1,091 | 0 | 1,091 |
| 2026-03-19 | 1,926 | 0 | 1,926 |
| 2026-03-20 | 2,212 | 0 | 2,212 |
| 2026-03-21 | 2,415 | 0 | 2,415 |
| 2026-03-22 | 1,072 | 0 | 1,072 |
| 2026-03-23 | 2,625 | 0 | 2,625 |
| 2026-03-24 | 2,112 | 0 | 2,112 |
| 2026-03-25 | 2,638 | 0 | 2,638 |
| 2026-04-01 | 0 | 6,691 | 6,691 |
| 2026-04-02 | 0 | 6,863 | 6,863 |

**Claude**: avg 3,069 calls/day, peak 8,278 calls/day
**Hermes**: avg 6,777 calls/day, peak 6,863 calls/day

---

## 6. Repo Distribution

### Claude

| Repo | Tool Calls | Pct |
|------|------------|-----|
| workspace-hub | 70,303 | 95.5% |
| digitalmodel | 1,900 | 2.6% |
| assetutilities | 535 | 0.7% |
| worldenergydata | 201 | 0.3% |
| agent-a597ec3f | 100 | 0.1% |
| aceengineer-admin | 87 | 0.1% |
| agent-a1fcef76 | 58 | 0.1% |
| wrk-1132-standards-search | 55 | 0.1% |
| agent-a4dd71d2 | 39 | 0.1% |
| assethold | 38 | 0.1% |
| OGManufacturing | 32 | 0.0% |
| doris | 28 | 0.0% |
| agent-adc58889 | 23 | 0.0% |
| client_projects | 19 | 0.0% |
| wrk-1119-permission-model | 19 | 0.0% |
| saipem | 19 | 0.0% |
| agent-a2ce3a27 | 18 | 0.0% |
| agent-a33c7a4d | 15 | 0.0% |
| agent-a2e2ea6a | 14 | 0.0% |
| agent-a452d517 | 13 | 0.0% |
| agent-a23d34b0 | 13 | 0.0% |
| agent-a9ab6c88 | 13 | 0.0% |
| agent-a9fabb73 | 11 | 0.0% |
| agent-a7642626 | 11 | 0.0% |
| agent-a46ed1ee | 11 | 0.0% |
| agent-a215b88f | 11 | 0.0% |
| agent-a1d87b6a | 10 | 0.0% |
| agent-a3637eb9 | 10 | 0.0% |
| achantas-data | 10 | 0.0% |
| agent-a182b46f | 9 | 0.0% |
| rock-oil-field | 7 | 0.0% |
| frontierdeepwater | 6 | 0.0% |
| teamresumes | 5 | 0.0% |
| CAD-DEVELOPMENTS | 2 | 0.0% |
| seanation | 1 | 0.0% |

### Hermes (inferred from file paths)

| Repo | Tool Calls | Pct |
|------|------------|-----|
| workspace-hub | 12,388 | 91.4% |
| digitalmodel | 1,097 | 8.1% |
| aceengineer-strategy | 69 | 0.5% |

---

## 7. Co-occurrence Matrix — Module Pairs Worked Together

Top 30 module pairs that co-occur in the same session:

| Module A | Module B | Sessions Together |
|----------|----------|-------------------|
| `.claude/skills` | `.claude/work-queue` | 25 |
| `.claude/skills` | `/home` | 24 |
| `.claude/skills` | `scripts/work-queue` | 24 |
| `.claude/work-queue` | `scripts/work-queue` | 24 |
| `.claude/skills` | `/tmp` | 24 |
| `.claude/work-queue` | `/home` | 23 |
| `.claude/work-queue` | `/tmp` | 23 |
| `.claude/skills` | `/mnt` | 23 |
| `/home` | `scripts/work-queue` | 22 |
| `/home` | `/tmp` | 22 |
| `/tmp` | `scripts/work-queue` | 22 |
| `.claude/work-queue` | `/mnt` | 22 |
| `/mnt` | `/tmp` | 22 |
| `/home` | `/mnt` | 21 |
| `/mnt` | `scripts/work-queue` | 21 |
| `.claude/skills` | `scripts/review` | 19 |
| `.claude/skills` | `specs/modules` | 19 |
| `.claude/work-queue` | `scripts/review` | 19 |
| `.claude/work-queue` | `specs/modules` | 19 |
| `scripts/work-queue` | `specs/modules` | 19 |
| `.claude/skills` | `specs/wrk` | 19 |
| `.claude/work-queue` | `specs/wrk` | 19 |
| `scripts/work-queue` | `specs/wrk` | 19 |
| `/home` | `scripts/review` | 18 |
| `/home` | `specs/modules` | 18 |
| `scripts/review` | `scripts/work-queue` | 18 |
| `/tmp` | `scripts/review` | 18 |
| `/home` | `specs/wrk` | 18 |
| `/mnt` | `specs/wrk` | 18 |
| `/tmp` | `specs/wrk` | 18 |

---

## Key Findings

### Most Accessed Files
The top 5 most-read files account for heavy consultation patterns:
1. `scripts/work-queue/verify-gate-evidence.py` — 732 reads
2. `scripts/work-queue/generate-html-review.py` — 249 reads
3. `scripts/work-queue/exit_stage.py` — 137 reads
4. `scripts/work-queue/start_stage.py` — 135 reads
5. `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` — 120 reads

### Most Modified Files
The top 5 most-modified files indicate hot-edit zones:
1. `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` — 130 writes
2. `scripts/work-queue/generate-html-review.py` — 116 writes
3. `scripts/work-queue/whats-next.sh` — 89 writes
4. `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` — 67 writes
5. `assetutilities/src/assetutilities/common/data.py` — 61 writes

### Agent Work Patterns
- Claude dominates with 73,646 structured tool calls across 24 sessions
- Hermes contributed 13,554 calls across 2 sessions (newer agent)
- Codex operates as a review bot: 371 verdicts, minimal autonomous execution

### Cross-Agent Overlap
Hermes and Claude show complementary patterns — Hermes leans heavily on search_files
while Claude has broader tool usage (Bash, Read, Write, Edit, Grep, Glob, Agent, WebFetch).

---

## Intermediate Data Files

All CSV/JSON intermediate data saved to `analysis/cross-agent-audit-20260402/phase-a-data/`:

- `read_files_claude.csv`
- `read_files_hermes.csv`
- `read_files_combined.csv`
- `write_files_claude.csv`
- `write_files_hermes.csv`
- `write_files_combined.csv`
- `bash_cmds_claude.csv`
- `bash_cmds_hermes.csv`
- `tool_dist.json`
- `daily_activity.csv`
- `repo_dist.json`
- `co_occurrence.csv`
- `session_modules.json`
- `analysis_results.json`