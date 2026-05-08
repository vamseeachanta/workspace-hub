# Provider session ecosystem audit — 2026-05-08

Scope: provider session artifacts rooted at `/mnt/local-analysis/workspace-hub/logs/orchestrator` with saved provider artifacts used only as fallback when raw logs are unavailable.

## Executive summary
- `claude` — source=raw_logs | sessions=51 | post_records=104337 | python3/1k=8.87 | uv-python/1k=59.01
- `codex` — source=raw_logs | sessions=66 | post_records=30875 | python3/1k=11.82 | uv-python/1k=21.25
- `hermes` — source=raw_logs | sessions=39 | post_records=192069 | python3/1k=14.14 | uv-python/1k=14.93
- `gemini` — source=raw_logs | sessions=59 | post_records=6185 | python3/1k=47.05 | uv-python/1k=6.31

- Migration debt density (known stale reads with redirect hints per 1k records): `claude` 16.67, `gemini` 13.9, `codex` 2.3, `hermes` 1.52.
- Highest-volume known migration debt: `claude` with 1739 mapped stale reads across 4 rule clusters; top hotspot: `legacy_work_queue_transition` (1015).
- Highest-density known migration debt: `claude` with 1739 mapped stale reads; top hotspot: `legacy_work_queue_transition` (1015, 58.37% of known debt).
- Scope note: Migration-debt figures are based on remediation-mapped entries from each provider's top missing repo reads.

## Provider interpretation summary
- Focus this week: prioritize legacy-path redirect cleanup and prompt/doc updates on claude (urgency 80.0, issue: legacy_work_queue_transition), then address gemini (urgency 47.72, issue: legacy_local_work_queue_items).
- Recommended actions:
  - `claude` [urgent_now] — prioritize legacy-path redirect cleanup and prompt/doc updates (urgency 80.0, issue: legacy_work_queue_transition; health=red; movement: rank unchanged at #1; urgency 80.00 (+20.00 vs previous audit); recent activity increased; path drift improved)
  - `gemini` [next_up] — prioritize legacy-path redirect cleanup and prompt/doc updates (urgency 47.72, issue: legacy_local_work_queue_items; health=red; movement: rank unchanged at #2; urgency 47.72 (+0.00 vs previous audit))
  - `hermes` [next_up] — prioritize legacy-path redirect cleanup and prompt/doc updates (urgency 41.4, issue: llm_wiki_spinout_path_drift; health=red; movement: rank unchanged at #3; urgency 41.40 (+27.91 vs previous audit); recent activity increased; migration debt improved; path drift improved; corpus grew faster than event-time activity)
  - `codex` [investigate] — prioritize legacy-path redirect cleanup and prompt/doc updates (urgency 26.12, issue: nested_repo_context_drift; health=yellow; movement: rank unchanged at #4; urgency 26.12 (+14.80 vs previous audit); recent activity increased; path drift improved)
- Health overview:
  - `claude` [red] — red: urgent action tier; high migration debt; 7d sustained activity; currently active
  - `gemini` [red] — red: high migration debt; python3-heavy command hygiene
  - `hermes` [red] — red: moderate migration debt; corpus anomaly needs interpretation; 7d sustained activity; currently active
  - `codex` [yellow] — yellow: moderate migration debt; 7d sustained activity
- Watchlist triggers:
  - `claude` [page] — urgent-now provider with legacy_work_queue_transition | follow-up: Escalate immediately on claude: prioritize legacy-path redirect cleanup and prompt/doc updates
  - `gemini` [act_this_week] — red health due to legacy_local_work_queue_items | follow-up: Prioritize this week on gemini: prioritize legacy-path redirect cleanup and prompt/doc updates
  - `hermes` [act_this_week] — red health due to llm_wiki_spinout_path_drift; corpus anomaly present | follow-up: Prioritize this week on hermes: prioritize legacy-path redirect cleanup and prompt/doc updates
  - `codex` [investigate] — yellow health with sustained 7d activity and nested_repo_context_drift | follow-up: Sample current traces on codex and verify whether nested_repo_context_drift needs remap or docs cleanup
- Change alerts:
  - `claude` [trigger_escalated] — claude trigger escalated from act_this_week to page | follow-up: Escalate immediately on claude: prioritize legacy-path redirect cleanup and prompt/doc updates
  - `hermes` [trigger_escalated] — hermes trigger escalated from investigate to act_this_week | follow-up: Prioritize this week on hermes: prioritize legacy-path redirect cleanup and prompt/doc updates
- Remediation playbooks:
  - `claude` [page] — issue=legacy_work_queue_transition | lane=governance-docs | owner=governance-maintainers | owner_surface=docs/governance/SESSION-GOVERNANCE.md | inspect=scripts/work-queue/verify-gate-evidence.py, scripts/work-queue/start_stage.py, scripts/work-queue/exit_stage.py | targets=docs/governance/SESSION-GOVERNANCE.md, docs/governance/TRUST-ARCHITECTURE.md, scripts/workflow/governance-checkpoints.yaml | steps: Inspect the top matched stale paths for legacy_work_queue_transition and confirm they should redirect rather than be recreated. | Open the canonical targets and migrate prompts/docs/tooling toward: docs/governance/SESSION-GOVERNANCE.md, docs/governance/TRUST-ARCHITECTURE.md, scripts/workflow/governance-checkpoints.yaml.
  - `gemini` [act_this_week] — issue=legacy_local_work_queue_items | lane=planning-workflow | owner=planning-ops | owner_surface=notes/agent-work-queue.md | inspect=.claude/work-queue/WRK-149.md, .claude/work-queue/working, .claude/work-queue/working/ | targets=GitHub issues, .planning/, notes/agent-work-queue.md | steps: Inspect the top matched stale paths for legacy_local_work_queue_items and confirm they should redirect rather than be recreated. | Open the canonical targets and migrate prompts/docs/tooling toward: GitHub issues, .planning/, notes/agent-work-queue.md.
  - `hermes` [act_this_week] — issue=llm_wiki_spinout_path_drift | lane=monitoring | owner=audit-operators | owner_surface=docs/reports/provider-session-ecosystem-audit.md | inspect=knowledge/wikis/engineering/wiki/index.md, knowledge/wikis/engineering/wiki/log.md, knowledge/wikis/marine-engineering/wiki/index.md | targets=llm-wiki/wikis/, llm-wiki/docs/, docs/session-handoffs/2026-05-05-llm-wiki-spinout-max-completeness-handoff.md | steps: Inspect the top matched stale paths for llm_wiki_spinout_path_drift and confirm they should redirect rather than be recreated. | Open the canonical targets and migrate prompts/docs/tooling toward: llm-wiki/wikis/, llm-wiki/docs/, docs/session-handoffs/2026-05-05-llm-wiki-spinout-max-completeness-handoff.md.
  - `codex` [investigate] — issue=nested_repo_context_drift | lane=monitoring | owner=audit-operators | owner_surface=docs/reports/provider-session-ecosystem-audit.md | inspect=src/worldenergydata/cost/data_collection/calibration_schema.py, src/worldenergydata/cost/data_collection/public_dataset.py, src/worldenergydata/cost/data_collection/__init__.py | targets=worldenergydata/src/worldenergydata/, worldenergydata/tests/unit/cost/, worldenergydata/docs/plans/ | steps: Inspect the top matched stale paths for nested_repo_context_drift and confirm they should redirect rather than be recreated. | Open the canonical targets and migrate prompts/docs/tooling toward: worldenergydata/src/worldenergydata/, worldenergydata/tests/unit/cost/, worldenergydata/docs/plans/.
- Follow-up issue drafts:
  - `claude` [critical] — [critical] claude: remediate legacy_work_queue_transition | state=changed | owner=governance-maintainers | lane=governance-docs
  - `gemini` [high] — [high] gemini: remediate legacy_local_work_queue_items | state=unchanged | owner=planning-ops | lane=planning-workflow
  - `hermes` [high] — [high] hermes: remediate llm_wiki_spinout_path_drift | state=changed | owner=audit-operators | lane=monitoring
  - `codex` [medium] — [medium] codex: remediate nested_repo_context_drift | state=unchanged | owner=audit-operators | lane=monitoring
- Issue posting readiness:
  - `claude` [ready] — should_open_issue=yes | final_should_open=yes | evidence=complete | linked_issue=none | matched_on=none | reason=changed actionable draft with no linked issue found
  - `gemini` [ready] — should_open_issue=no | final_should_open=yes | evidence=complete | linked_issue=none | matched_on=none | reason=unchanged draft has no linked issue; safe to open once
  - `hermes` [ready] — should_open_issue=yes | final_should_open=yes | evidence=complete | linked_issue=none | matched_on=none | reason=changed actionable draft with no linked issue found
  - `codex` [ready] — should_open_issue=no | final_should_open=yes | evidence=complete | linked_issue=none | matched_on=none | reason=unchanged draft has no linked issue; safe to open once
- `claude` — rank=1 (prev=1, move=stable) | health=red | profile=sustained_background | 24h=52 posts/6 sessions | 7d=7986 posts/56 sessions | urgency=80.0 | tier=urgent_now | activity=active (increasing) | corpus=aligned | debt=high_debt (stable) | drift=improving | python=uv_preferred (stable) | health summary: red: urgent action tier; high migration debt; 7d sustained activity; currently active | movement: rank unchanged at #1; urgency 80.00 (+20.00 vs previous audit); recent activity increased; path drift improved | primary issue: legacy_work_queue_transition | action: prioritize legacy-path redirect cleanup and prompt/doc updates
- `gemini` — rank=2 (prev=2, move=stable) | health=red | profile=light_recent | 24h=0 posts/0 sessions | 7d=4 posts/4 sessions | urgency=47.72 | tier=next_up | activity=idle (stable) | corpus=aligned | debt=high_debt (stable) | drift=stable | python=python3_heavy (stable) | health summary: red: high migration debt; python3-heavy command hygiene | movement: rank unchanged at #2; urgency 47.72 (+0.00 vs previous audit) | primary issue: legacy_local_work_queue_items | action: prioritize legacy-path redirect cleanup and prompt/doc updates
- `hermes` — rank=3 (prev=3, move=stable) | health=red | profile=sustained_background | 24h=828 posts/36 sessions | 7d=9083 posts/403 sessions | urgency=41.4 | tier=next_up | activity=active (increasing) | corpus=positive_corpus_growth_beyond_recent_activity | debt=moderate_debt (improving) | drift=improving | python=mixed (stable) | health summary: red: moderate migration debt; corpus anomaly needs interpretation; 7d sustained activity; currently active | movement: rank unchanged at #3; urgency 41.40 (+27.91 vs previous audit); recent activity increased; migration debt improved; path drift improved; corpus grew faster than event-time activity | primary issue: llm_wiki_spinout_path_drift | action: prioritize legacy-path redirect cleanup and prompt/doc updates
- `codex` — rank=4 (prev=4, move=stable) | health=yellow | profile=sustained_background | 24h=48 posts/2 sessions | 7d=1455 posts/27 sessions | urgency=26.12 | tier=investigate | activity=quiet (increasing) | corpus=aligned | debt=moderate_debt (stable) | drift=improving | python=mixed (stable) | health summary: yellow: moderate migration debt; 7d sustained activity | movement: rank unchanged at #4; urgency 26.12 (+14.80 vs previous audit); recent activity increased; path drift improved | primary issue: nested_repo_context_drift | action: prioritize legacy-path redirect cleanup and prompt/doc updates

## Recent activity since previous audit
- Previous audit timestamp: `2026-05-07T09:37:54Z`
- Recent post-audit activity: `hermes` 1857 post records / 70 sessions, `claude` 52 post records / 6 sessions, `codex` 48 post records / 2 sessions.
- Scope note: This is event-time activity since the previous audit timestamp, not a census of newly exported historical/backfilled records.

## Rolling activity windows
- `last_24h` — `2026-05-07T11:03:24Z` → `2026-05-08T11:03:24Z`
  - Scope note: Last 24 hours of event-time activity ending at this audit timestamp.
  - Activity leaders: `hermes` 828 post records / 36 sessions, `claude` 52 post records / 6 sessions, `codex` 48 post records / 2 sessions.
- `last_7d` — `2026-05-01T11:03:24Z` → `2026-05-08T11:03:24Z`
  - Scope note: Last 7 days of event-time activity ending at this audit timestamp.
  - Activity leaders: `hermes` 9083 post records / 403 sessions, `claude` 7986 post records / 56 sessions, `codex` 1455 post records / 27 sessions, `gemini` 4 post records / 4 sessions.

## Corpus change since previous audit
- Previous audit timestamp: `2026-05-07T09:37:54Z`
- Scope note: Snapshot-to-snapshot corpus deltas reflect export additions/removals/reclassification and should be interpreted separately from event-time recent activity.
- Largest negative reconciliation gap: `claude`
- Largest positive reconciliation gap: `hermes`

## claude
- Source: raw_logs
- Sessions: 51
- Post-hook records: 104337
- Correction sessions: 0
- Unique runtime sessions: 620
- Prompt-like reads: 280
- Blank read targets: 0
- Missing repo reads: 8819
- Bare python3 bash calls: 925
- `uv run ... python` bash calls: 6157

### claude top tools
- `Bash` — 58362
- `Read` — 19508
- `Edit` — 8772
- `Write` — 7935
- `Grep` — 2549
- `unknown` — 1745
- `Agent` — 1229
- `ToolSearch` — 681

### claude top repos
- `workspace-hub` — 99753
- `digitalmodel` — 1900
- `assetutilities` — 535
- `worldenergydata` — 201
- `workspace-hub-2510-plan` — 196
- `reconcile-main-20260427` — 122
- `agent-a597ec3f` — 100
- `issue-2348-exec` — 90

### claude top reads
- `scripts/work-queue/verify-gate-evidence.py` — 740
- `scripts/work-queue/generate-html-review.py` — 249
- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` — 180
- `docs/plans/README.md` — 169
- `docs/plans/_template-issue-plan.md` — 150
- `scripts/work-queue/start_stage.py` — 138
- `scripts/work-queue/exit_stage.py` — 137
- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` — 123
- `scripts/work-queue/close-item.sh` — 94
- `scripts/work-queue/whats-next.sh` — 70

### claude top symbolic reads
- none

### claude top sibling-repo reads
- `digitalmodel/specs/data-needs.yaml` — 7
- `digitalmodel/src/digitalmodel/naval_architecture/curves.py` — 5
- `digitalmodel/specs/module-registry.yaml` — 5
- `digitalmodel/docs/domains/openfoam/naval_architecture/propeller_hull_interaction.pdf` — 2
- `digitalmodel/docs/domains/ship-design/maneuvering_ship.pdf` — 2
- `worldenergydata/tests/test_resource_estimation.py` — 2
- `digitalmodel/docs/domains/hydrodynamics/literature/viviani-2007-four-quadrant-wageningen-b-series.pdf` — 2
- `digitalmodel/tests/fixtures/reporting/riser_lazy_wave_fpso.metadata.json` — 2
- `digitalmodel/docs/domains/drilling/references/REF-ENG-DECOM-vol-1-a-study-for-the-bureau-of-safety-and-environmental-enforcement-bsee-final-9-10-2020.pdf` — 1
- `worldenergydata/CHANGELOG.md` — 1

### claude top non-repo artifact reads
- none

### claude top Bash command families
- `ls` — 9177
- `grep` — 7110
- `uv run` — 6058
- `cat` — 5191
- `find` — 3992
- `gh` — 3067
- `bash` — 2980
- `git` — 1490

### claude recent activity since previous audit
- Post-hook records since prior audit: 52
- Runtime sessions since prior audit: 6

### claude recent top tools
- `Bash` — 25
- `Read` — 20
- `Grep` — 2
- `unknown` — 2
- `Agent` — 1

### claude recent top reads
- `scripts/analysis/provider_session_ecosystem_audit.py` — 4
- `docs/plans/2026-05-07-issue-2655-codex-nested-repo-context-drift.md` — 3
- `docs/ops/legacy-claude-reference-map.md` — 3
- `scripts/review/results/2026-05-07-plan-2655-codex.md` — 2
- `tests/analysis/test_provider_session_ecosystem_audit.py` — 2

### claude recent top writes
- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/reference_claude_dreaming_managed_agents.md` — 1

### claude recent top edits
- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` — 1

### claude recent top Bash command families
- `ls` — 11
- `python3` — 5
- `uv run` — 3
- `find` — 2
- `grep` — 2
- `gh` — 1
- `(ls` — 1

### claude recent top missing repo reads
- `scripts/review/results/2026-05-07-plan-2655-gemini.md.err` — 1

### claude recent top sibling-repo reads
- none

### claude recent top non-repo artifact reads
- none

### claude corpus change since previous audit
- Post-hook records: current 104337 vs previous 104285 (delta 52)
- Sessions: current 51 vs previous 50 (delta 1)
- Missing repo reads: current 8819 vs previous 8818 (delta 1)
- Event-time post records since prior audit: 52
- Reconciliation gap vs event-time delta: 0
- Status: aligned
- Interpretation: Snapshot post-record change aligns with recent event-time activity.

### claude top missing repo reads
- `scripts/work-queue/verify-gate-evidence.py` — 740
- `scripts/work-queue/generate-html-review.py` — 249
- `scripts/work-queue/start_stage.py` — 138
- `scripts/work-queue/exit_stage.py` — 137
- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` — 123
- `scripts/work-queue/close-item.sh` — 94
- `scripts/work-queue/whats-next.sh` — 70
- `.claude/skills/coordination/workspace/work-queue/SKILL.md` — 66
- `scripts/work-queue/archive-item.sh` — 62
- `scripts/work-queue/claim-item.sh` — 60

### claude top sibling-repo reads
- `digitalmodel/specs/data-needs.yaml` — 7
- `digitalmodel/src/digitalmodel/naval_architecture/curves.py` — 5
- `digitalmodel/specs/module-registry.yaml` — 5
- `digitalmodel/docs/domains/openfoam/naval_architecture/propeller_hull_interaction.pdf` — 2
- `digitalmodel/docs/domains/ship-design/maneuvering_ship.pdf` — 2
- `worldenergydata/tests/test_resource_estimation.py` — 2
- `digitalmodel/docs/domains/hydrodynamics/literature/viviani-2007-four-quadrant-wageningen-b-series.pdf` — 2
- `digitalmodel/tests/fixtures/reporting/riser_lazy_wave_fpso.metadata.json` — 2
- `digitalmodel/docs/domains/drilling/references/REF-ENG-DECOM-vol-1-a-study-for-the-bureau-of-safety-and-environmental-enforcement-bsee-final-9-10-2020.pdf` — 1
- `worldenergydata/CHANGELOG.md` — 1

### claude top non-repo artifact reads
- none

### claude remediation hints for stale repo reads
- `scripts/work-queue/verify-gate-evidence.py` (740), `scripts/work-queue/start_stage.py` (138), `scripts/work-queue/exit_stage.py` (137) — 1015 combined reads
  - Redirect to: `docs/governance/SESSION-GOVERNANCE.md`, `docs/governance/TRUST-ARCHITECTURE.md`, `scripts/workflow/governance-checkpoints.yaml`, `.claude/hooks/plan-approval-gate.sh`, `.claude/hooks/session-governor-check.sh`, `scripts/review/cross-review.sh`
  - Guidance: Legacy stage-transition tooling was removed during workflow migration; redirect callers to governance docs/hooks instead of recreating the old executables.
  - Reference: `docs/ops/legacy-claude-reference-map.md`
- `scripts/work-queue/close-item.sh` (94), `scripts/work-queue/whats-next.sh` (70), `scripts/work-queue/archive-item.sh` (62), `scripts/work-queue/claim-item.sh` (60) — 286 combined reads
  - Redirect to: `scripts/refresh-agent-work-queue.py`, `scripts/refresh-agent-work-queue.sh`, `notes/agent-work-queue.md`, `.planning/`, `GitHub issues`
  - Guidance: The repo no longer uses local queue scripts as the source of truth; prefer GitHub issue updates plus .planning evidence.
  - Reference: `docs/ops/legacy-claude-reference-map.md`
- `scripts/work-queue/generate-html-review.py` (249) — 249 combined reads
  - Redirect to: `scripts/review/cross-review.sh`, `templates/review-standard.html`, `docs/work-queue-workflow.md`
  - Guidance: Historical HTML review generation is no longer canonical; use the current cross-review workflow and stored review evidence instead.
  - Reference: `docs/ops/legacy-claude-reference-map.md`
- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` (123), `.claude/skills/coordination/workspace/work-queue/SKILL.md` (66) — 189 combined reads
  - Redirect to: `AGENTS.md`, `.claude/commands/gsd/*`, `.gemini/get-shit-done/workflows/*`, `docs/work-queue-workflow.md`
  - Guidance: The old work-queue skill tree was replaced by GSD-oriented command/workflow surfaces; redirect readers instead of restoring deleted skill files.
  - Reference: `docs/ops/legacy-claude-reference-map.md`

### claude top missing external reads
- `/tmp/tmp.4XN7Wckbxl/review-content.md` — 18
- `/tmp/workspace-hub-2510-plan/docs/plans/2026-04-26-issue-2510-python-layout-cad-automation-demo.md` — 13
- `/tmp/tmp.4fvalbgSpv/review-content.md` — 10
- `/tmp/tmp.Y7GHawx2jw/review-content.md` — 9
- `/mnt/local-analysis/kaggle-rogii-2026/docs/plans/README.md` — 7
- `/tmp/tmp.sHUq6zx1JY/review-content.md` — 6
- `/tmp/claude-1000/-mnt-local-analysis-workspace-hub/bbee1363-b468-43b8-993b-a3d911b74098/tasks/btc1dobmw.output` — 6
- `/tmp/dm-570-571-fix/tests/solvers/orcaflex/test_orcaflex_cli.py` — 6
- `/tmp/tmp.Y2upjk3JCH/review-content.md` — 5
- `/tmp/tmp.SmqPbkghat/review-content.md` — 5

## codex
- Source: raw_logs
- Sessions: 66
- Post-hook records: 30875
- Correction sessions: 0
- Unique runtime sessions: 944
- Prompt-like reads: 35
- Blank read targets: 0
- Missing repo reads: 730
- Bare python3 bash calls: 365
- `uv run ... python` bash calls: 656

### codex top tools
- `Bash` — 24513
- `Read` — 4162
- `Grep` — 1255
- `update_plan` — 408
- `list_mcp_resources` — 193
- `_add_comment_to_issue` — 105
- `_fetch_commit` — 21
- `list_mcp_resource_templates` — 18

### codex top repos
- `workspace-hub` — 30875

### codex top reads
- `docs/plans/README.md` — 186
- `docs/standards/HARD-STOP-POLICY.md` — 75
- `docs/plans/_template-issue-plan.md` — 56
- `config/scheduled-tasks/schedule-tasks.yaml` — 48
- `docs/ops/scheduled-tasks.md` — 44
- `docs/standards/AI_REVIEW_ROUTING_POLICY.md` — 41
- `AGENTS.md` — 40
- `scripts/skills/weekly_skills_audit.py` — 39
- `.gitignore` — 39
- `scripts/cron/skills-curation.sh` — 38

### codex top symbolic reads
- `github://vamseeachanta/workspace-hub/issues/2488` — 32
- `github://vamseeachanta/workspace-hub/issues/2486` — 24
- `github://vamseeachanta/workspace-hub/issues/2510` — 17
- `github://vamseeachanta/workspace-hub/issues/2511` — 16
- `github://vamseeachanta/workspace-hub/issues/2460` — 14
- `github://vamseeachanta/workspace-hub/issues/2471` — 14
- `github://vamseeachanta/workspace-hub/issues/2462` — 13
- `github://vamseeachanta/workspace-hub/issues/2503` — 13
- `github://vamseeachanta/workspace-hub/issues/2464` — 12
- `github://vamseeachanta/workspace-hub/issues/2465` — 11

### codex top sibling-repo reads
- none

### codex top non-repo artifact reads
- `content/demos/index.html` — 9
- `build.js` — 7
- `content/partials/head-common.html` — 7
- `vercel.json` — 7
- `package.json` — 6
- `content/demos/jumper-installation.html` — 5
- `examples/demos/gtm/output/demo_02_wall_thickness_report.html` — 4
- `examples/demos/gtm/output/demo_03_mudmat_installation_report.html` — 4
- `examples/demos/gtm/output/demo_01_freespan_report.html` — 3
- `examples/demos/gtm/output/demo_04_shallow_pipelay_report.html` — 3

### codex top Bash command families
- `sed` — 5842
- `rg` — 2253
- `nl` — 1441
- `uv run` — 791
- `find` — 735
- `ls` — 652
- `git status` — 636
- `bash` — 518

### codex recent activity since previous audit
- Post-hook records since prior audit: 48
- Runtime sessions since prior audit: 2

### codex recent top tools
- `Bash` — 48

### codex recent top reads
- none

### codex recent top writes
- none

### codex recent top edits
- none

### codex recent top Bash command families
- `sed` — 13
- `rg` — 8
- `find` — 8
- `codex` — 7
- `pkill` — 2
- `ls` — 1
- `git` — 1
- `which` — 1

### codex recent top missing repo reads
- none

### codex recent top sibling-repo reads
- none

### codex recent top non-repo artifact reads
- none

### codex corpus change since previous audit
- Post-hook records: current 30875 vs previous 30827 (delta 48)
- Sessions: current 66 vs previous 65 (delta 1)
- Missing repo reads: current 730 vs previous 730 (delta 0)
- Event-time post records since prior audit: 48
- Reconciliation gap vs event-time delta: 0
- Status: aligned
- Interpretation: Snapshot post-record change aligns with recent event-time activity.

### codex top missing repo reads
- `knowledge/wikis/engineering/CLAUDE.md` — 10
- `src/worldenergydata/cost/data_collection/calibration_schema.py` — 9
- `src/worldenergydata/cost/data_collection/public_dataset.py` — 8
- `src/worldenergydata/cost/data_collection/__init__.py` — 8
- `docs/plans/2026-04-21-issue-334-annual-operator-disclosures-dataset.md` — 8
- `src/assethold/signals/watchlist.py` — 7
- `sitemap.xml` — 7
- `.github/workflows/ci.yml` — 7
- `src/worldenergydata/cost/calibration/cost_predictor.py` — 7
- `tests/unit/cost/test_proxy_comparison.py` — 7

### codex top sibling-repo reads
- none

### codex top non-repo artifact reads
- `content/demos/index.html` — 9
- `build.js` — 7
- `content/partials/head-common.html` — 7
- `vercel.json` — 7
- `package.json` — 6
- `content/demos/jumper-installation.html` — 5
- `examples/demos/gtm/output/demo_02_wall_thickness_report.html` — 4
- `examples/demos/gtm/output/demo_03_mudmat_installation_report.html` — 4
- `examples/demos/gtm/output/demo_01_freespan_report.html` — 3
- `examples/demos/gtm/output/demo_04_shallow_pipelay_report.html` — 3

### codex remediation hints for stale repo reads
- `src/worldenergydata/cost/data_collection/calibration_schema.py` (9), `src/worldenergydata/cost/data_collection/public_dataset.py` (8), `src/worldenergydata/cost/data_collection/__init__.py` (8), `docs/plans/2026-04-21-issue-334-annual-operator-disclosures-dataset.md` (8), `src/assethold/signals/watchlist.py` (7), `sitemap.xml` (7), `src/worldenergydata/cost/calibration/cost_predictor.py` (7), `tests/unit/cost/test_proxy_comparison.py` (7) — 61 combined reads
  - Redirect to: `worldenergydata/src/worldenergydata/`, `worldenergydata/tests/unit/cost/`, `worldenergydata/docs/plans/`, `assethold/src/assethold/`, `aceengineer-website/sitemap.xml`
  - Guidance: Codex/Hermes sessions may run from workspace-hub while inspecting nested tier-1 repos; prepend the owning repo root before treating these reads as missing workspace-hub files.
  - Reference: `docs/ops/legacy-claude-reference-map.md`
- `knowledge/wikis/engineering/CLAUDE.md` (10) — 10 combined reads
  - Redirect to: `llm-wiki/wikis/`, `llm-wiki/docs/`, `docs/session-handoffs/2026-05-05-llm-wiki-spinout-max-completeness-handoff.md`, `docs/sessions/2026-05-07-nest-llm-wiki-kaggle-into-hub.md`
  - Guidance: The LLM-wiki artifact store moved out of workspace-hub/knowledge into the llm-wiki repository; redirect wiki-content reads to llm-wiki and keep control-plane work in workspace-hub.
  - Reference: `docs/ops/legacy-claude-reference-map.md`

### codex top missing external reads
- none

## hermes
- Source: raw_logs
- Sessions: 39
- Post-hook records: 192069
- Correction sessions: 37
- Unique runtime sessions: 2928
- Prompt-like reads: 1754
- Blank read targets: 63
- Missing repo reads: 1240
- Bare python3 bash calls: 2716
- `uv run ... python` bash calls: 2868

### hermes top tools
- `Bash` — 80964
- `Read` — 40567
- `Grep` — 27870
- `Write` — 22745
- `Edit` — 16284
- `Task` — 1952
- `Browser` — 745
- `ToolSearch` — 463

### hermes top repos
- `workspace-hub` — 192069

### hermes top reads
- `docs/plans/README.md` — 527
- `scripts/analysis/provider_session_ecosystem_audit.py` — 430
- `docs/reports/provider-session-ecosystem-audit.md` — 303
- `tests/analysis/test_provider_session_ecosystem_audit.py` — 295
- `config/scheduled-tasks/schedule-tasks.yaml` — 263
- `docs/plans/_template-issue-plan.md` — 251
- `analysis/provider-session-ecosystem-audit.json` — 248
- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` — 214
- `docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md` — 142
- `/home/vamsee/.hermes/config.yaml` — 96

### hermes top symbolic reads
- `github/github-issues` — 661
- `coordination/issue-planning-mode` — 581
- `coordination/gh-work-planning` — 440
- `software-development/gh-work-execution` — 322
- `github-issues` — 312
- `coordination/session-start-routine` — 278
- `coordination/provider-session-ecosystem-audit` — 216
- `software-development/multi-provider-adversarial-review` — 193
- `autonomous-ai-agents/claude-code` — 167
- `software-development/overnight-parallel-agent-prompts` — 159

### hermes top sibling-repo reads
- `digitalmodel/specs/module-registry.yaml` — 13
- `digitalmodel/docs/roadmaps/orcawave-orcaflex-capability-roadmap.md` — 7
- `digitalmodel/docs/assessments/hull-library-audit.md` — 7
- `worldenergydata/.planning/quick/gemini-review.txt` — 6
- `digitalmodel/docs/plans/README.md` — 5
- `worldenergydata/.planning/quick/codex-review.txt` — 4
- `worldenergydata/.planning/quick/claude-review.txt` — 4
- `digitalmodel/src/digitalmodel/solvers/orcaflex/installation_analysis.py` — 4
- `worldenergydata/.planning/quick/review-343-rerun-gemini.out` — 4
- `digitalmodel/.claude/skills/orcaflex-batch-manager/SKILL.md` — 3

### hermes top non-repo artifact reads
- none

### hermes top Bash command families
- `gh` — 16158
- `uv run` — 4937
- `set` — 4044
- `git status` — 3354
- `bash` — 2594
- `git add` — 2446
- `git` — 1651
- `find` — 1564

### hermes recent activity since previous audit
- Post-hook records since prior audit: 1857
- Runtime sessions since prior audit: 70

### hermes recent top tools
- `Read` — 726
- `Bash` — 507
- `Grep` — 406
- `Write` — 133
- `Edit` — 71

### hermes recent top reads
- `business.gtm-parametric-demo-reports` — 42
- `digitalmodel.digitalmodel-code-explorer` — 35
- `github.github-issues` — 35
- `gtm-parametric-demo-reports` — 34
- `digitalmodel/docs/plans/2026-05-07-issue-596-repo-structure-normalization.md` — 27

### hermes recent top writes
- `/mnt/local-analysis/workspace-hub/digitalmodel/docs/plans/2026-05-07-issue-596-repo-structure-normalization.md` — 4
- `/mnt/local-analysis/workspace-hub/digitalmodel/examples/demos/gtm/data/ctv_operability_kincardine.json` — 3
- `/mnt/ace/digitalmodel/references/vessel-suitability/ctv-operability-kincardine-seaops.md` — 3
- `/mnt/local-analysis/workspace-hub/digitalmodel/examples/demos/gtm/tests/test_ctv_operability_reference.py` — 3
- `/tmp/digitalmodel-issue-591-entail-otc-comment.md` — 3

### hermes recent top edits
- `/mnt/local-analysis/workspace-hub/digitalmodel/docs/plans/2026-05-07-issue-596-repo-structure-normalization.md` — 27
- `/mnt/ace/digitalmodel/references/vessel-suitability/REFERENCE-INDEX.md` — 8
- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/structural/stress/nonlinear.py` — 7
- `/mnt/ace/digitalmodel/references/vessel-suitability/entail-otc-2026-brochure-extraction.md` — 4
- `/mnt/local-analysis/workspace-hub/digitalmodel/examples/demos/gtm/README.md` — 3

### hermes recent top Bash command families
- `git status` — 66
- `gh` — 65
- `uv run` — 49
- `set` — 45
- `git` — 38
- `python` — 17
- `printf` — 15
- `date` — 15

### hermes recent top missing repo reads
- none

### hermes recent top sibling-repo reads
- `digitalmodel/docs/plans/README.md` — 5
- `digitalmodel/docs/plans/_template-issue-plan.md` — 2

### hermes recent top non-repo artifact reads
- none

### hermes corpus change since previous audit
- Post-hook records: current 192069 vs previous 188802 (delta 3267)
- Sessions: current 39 vs previous 39 (delta 0)
- Missing repo reads: current 1240 vs previous 1240 (delta 0)
- Event-time post records since prior audit: 1857
- Reconciliation gap vs event-time delta: 1410
- Status: positive_corpus_growth_beyond_recent_activity
- Interpretation: Snapshot grew more than recent event-time activity, suggesting backfill or expanded export coverage.

### hermes top missing repo reads
- `.claude/worktrees/ecosystem-sync/docs/plans/2026-04-20-aceengineer-ecosystem-sync-plan.md` — 67
- `knowledge/wikis/engineering/wiki/index.md` — 52
- `knowledge/wikis/engineering/wiki/log.md` — 35
- `knowledge/wikis/marine-engineering/wiki/index.md` — 28
- `knowledge/wikis/engineering/wiki/workflows/orcawave-to-orcaflex-pipeline.md` — 25
- `client_projects/engineering_workbooks/ballymore/jumper_manifold_to_plet/jumper_lift.py` — 24
- `knowledge/wikis/engineering/wiki/entities/orcaflex-solver.md` — 22
- `knowledge/wikis/engineering/wiki/entities/orcawave-solver.md` — 22
- `knowledge/wikis/engineering/wiki/entities/diffraction-analysis-system.md` — 21
- `knowledge/wikis/engineering/SCHEMA.md` — 20

### hermes top sibling-repo reads
- `digitalmodel/specs/module-registry.yaml` — 13
- `digitalmodel/docs/roadmaps/orcawave-orcaflex-capability-roadmap.md` — 7
- `digitalmodel/docs/assessments/hull-library-audit.md` — 7
- `worldenergydata/.planning/quick/gemini-review.txt` — 6
- `digitalmodel/docs/plans/README.md` — 5
- `worldenergydata/.planning/quick/codex-review.txt` — 4
- `worldenergydata/.planning/quick/claude-review.txt` — 4
- `digitalmodel/src/digitalmodel/solvers/orcaflex/installation_analysis.py` — 4
- `worldenergydata/.planning/quick/review-343-rerun-gemini.out` — 4
- `digitalmodel/.claude/skills/orcaflex-batch-manager/SKILL.md` — 3

### hermes top non-repo artifact reads
- none

### hermes remediation hints for stale repo reads
- `knowledge/wikis/engineering/wiki/index.md` (52), `knowledge/wikis/engineering/wiki/log.md` (35), `knowledge/wikis/marine-engineering/wiki/index.md` (28), `knowledge/wikis/engineering/wiki/workflows/orcawave-to-orcaflex-pipeline.md` (25), `knowledge/wikis/engineering/wiki/entities/orcaflex-solver.md` (22), `knowledge/wikis/engineering/wiki/entities/orcawave-solver.md` (22), `knowledge/wikis/engineering/wiki/entities/diffraction-analysis-system.md` (21), `knowledge/wikis/engineering/SCHEMA.md` (20) — 225 combined reads
  - Redirect to: `llm-wiki/wikis/`, `llm-wiki/docs/`, `docs/session-handoffs/2026-05-05-llm-wiki-spinout-max-completeness-handoff.md`, `docs/sessions/2026-05-07-nest-llm-wiki-kaggle-into-hub.md`
  - Guidance: The LLM-wiki artifact store moved out of workspace-hub/knowledge into the llm-wiki repository; redirect wiki-content reads to llm-wiki and keep control-plane work in workspace-hub.
  - Reference: `docs/ops/legacy-claude-reference-map.md`
- `.claude/worktrees/ecosystem-sync/docs/plans/2026-04-20-aceengineer-ecosystem-sync-plan.md` (67) — 67 combined reads
  - Redirect to: `main repo branch/worktree`, `docs/plans/`, `.planning/`, `GitHub issues`
  - Guidance: Provider logs sometimes retain ephemeral worktree or temp paths; treat these as session-local and re-resolve the durable artifact from the main repo, .planning, or GitHub issue evidence before acting.
  - Reference: `docs/ops/legacy-claude-reference-map.md`

### hermes top missing external reads
- `/mnt/local-analysis/worktrees/ws-2451-plan/docs/plans/2026-04-22-issue-2451-worldenergydata-test-followup.md` — 88
- `/mnt/local-analysis/recovery-finish-20260428/assethold/.github/workflows/python-tests.yml` — 53
- `/tmp/ballymore_data.json` — 43
- `/mnt/local-analysis/worktrees/digitalmodel-issue-521/scripts/benchmark/validate_owd_vs_spec.py` — 40
- `/mnt/local-analysis/worktrees/digitalmodel-issue-521/src/digitalmodel/hydrodynamics/diffraction/benchmark_runner.py` — 32
- `/tmp/workspace-hub-2511-impl/scripts/semiconductor/package_fem_benchmark.py` — 30
- `/mnt/local-analysis/worktrees/ws-2448-plan/docs/plans/2026-04-22-issue-2448-assethold-smoke-followup.md` — 29
- `/mnt/local-analysis/worktrees/provider-capacity-aware-20260503-0259-2510-plan-patch/docs/plans/2026-04-26-issue-2510-python-layout-cad-automation-demo.md` — 25
- `/mnt/local-analysis/worktrees/digitalmodel-issue-521/src/digitalmodel/hydrodynamics/diffraction/benchmark_input_comparison.py` — 24
- `/mnt/local-analysis/workspace-hub-issue-2488-impl/scripts/skills/weekly_skills_audit.py` — 22

## gemini
- Source: raw_logs
- Sessions: 59
- Post-hook records: 6185
- Correction sessions: 0
- Unique runtime sessions: 343
- Prompt-like reads: 18
- Blank read targets: 0
- Missing repo reads: 604
- Bare python3 bash calls: 291
- `uv run ... python` bash calls: 39

### gemini top tools
- `Bash` — 2288
- `Read` — 2181
- `Grep` — 655
- `Write` — 535
- `Edit` — 394
- `Browser` — 118
- `ToolSearch` — 9
- `generalist` — 3

### gemini top repos
- `workspace-hub` — 6185

### gemini top reads
- `.claude/work-queue/` — 29
- `scripts/operations/compliance/migrate_specs_to_workspace.sh` — 28
- `CLAUDE.md` — 23
- `.` — 22
- `.claude/work-queue` — 18
- `.claude/work-queue/WRK-149.md` — 17
- `.claude/work-queue/pending` — 16
- `digitalmodel/scripts/benchmark/validate_owd_vs_spec.py` — 16
- `digitalmodel/src/digitalmodel` — 15
- `AGENTS.md` — 14

### gemini top symbolic reads
- `digitalmodel` — 31
- `worldenergydata` — 19
- `tests` — 10
- `assethold` — 9
- `config` — 8
- `scripts` — 8
- `doris` — 8
- `src` — 7
- `docs` — 6
- `assetutilities` — 6

### gemini top sibling-repo reads
- `digitalmodel/scripts/python/digitalmodel/modules` — 6
- `worldenergydata/specs/README.md` — 4
- `digitalmodel/docs/modules` — 4
- `digitalmodel/tests/infrastructure/common/test_cathodic_protection_b401.py` — 4
- `digitalmodel/specs/modules/racing-placid-gazelle.md` — 2
- `digitalmodel/specs/README.md` — 2
- `digitalmodel/src/digitalmodel/asset_integrity/tests/test_update_deep_additional.py` — 2
- `digitalmodel/src/digitalmodel/asset_integrity/tests/test_yml_utilities_additional.py` — 2
- `digitalmodel/src/digitalmodel/asset_integrity/tests/test_pyintegrity_bs7910_ecs_2500ft_buoy_jt.py` — 2
- `digitalmodel/src/digitalmodel/asset_integrity/tests/test_pyintegrity_bs7910_multi_process.py` — 2

### gemini top non-repo artifact reads
- none

### gemini top Bash command families
- `ls` — 468
- `find` — 274
- `cat` — 195
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

### gemini recent top reads
- none

### gemini recent top writes
- none

### gemini recent top edits
- none

### gemini recent top Bash command families
- none

### gemini recent top missing repo reads
- none

### gemini recent top sibling-repo reads
- none

### gemini recent top non-repo artifact reads
- none

### gemini corpus change since previous audit
- Post-hook records: current 6185 vs previous 6185 (delta 0)
- Sessions: current 59 vs previous 59 (delta 0)
- Missing repo reads: current 604 vs previous 604 (delta 0)
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
- `scripts/work-queue/verify-gate-evidence.py` — 9
- `scripts/work-queue/` — 8
- `scripts/agents/providers/claude.sh` — 7

### gemini top sibling-repo reads
- `digitalmodel/scripts/python/digitalmodel/modules` — 6
- `worldenergydata/specs/README.md` — 4
- `digitalmodel/docs/modules` — 4
- `digitalmodel/tests/infrastructure/common/test_cathodic_protection_b401.py` — 4
- `digitalmodel/specs/modules/racing-placid-gazelle.md` — 2
- `digitalmodel/specs/README.md` — 2
- `digitalmodel/src/digitalmodel/asset_integrity/tests/test_update_deep_additional.py` — 2
- `digitalmodel/src/digitalmodel/asset_integrity/tests/test_yml_utilities_additional.py` — 2
- `digitalmodel/src/digitalmodel/asset_integrity/tests/test_pyintegrity_bs7910_ecs_2500ft_buoy_jt.py` — 2
- `digitalmodel/src/digitalmodel/asset_integrity/tests/test_pyintegrity_bs7910_multi_process.py` — 2

### gemini top non-repo artifact reads
- none

### gemini remediation hints for stale repo reads
- `.claude/work-queue/WRK-149.md` (17), `.claude/work-queue/working` (11), `.claude/work-queue/working/` (9) — 37 combined reads
  - Redirect to: `GitHub issues`, `.planning/`, `notes/agent-work-queue.md`, `docs/work-queue-workflow.md`
  - Guidance: Local queue item files are compatibility surfaces, not canonical work tracking; prefer the GitHub issue and .planning artifact instead.
  - Reference: `docs/ops/legacy-claude-reference-map.md`
- `scripts/agents/lib/workflow-guards.sh` (11), `scripts/agents/execute.sh` (10), `scripts/agents/providers/claude.sh` (7) — 28 combined reads
  - Redirect to: `AGENTS.md`, `docs/modules/ai/AGENT_EQUIVALENCE_ARCHITECTURE.md`, `docs/work-queue-workflow.md`, `scripts/review/cross-review.sh`, `scripts/planning/ensemble-plan.sh`
  - Guidance: The old scripts/agents wrapper tree is gone; use the current policy-first workflow and current review/planning surfaces instead.
  - Reference: `docs/ops/legacy-claude-reference-map.md`
- `.claude/skills/coordination/workspace/work-queue/SKILL.md` (12) — 12 combined reads
  - Redirect to: `AGENTS.md`, `.claude/commands/gsd/*`, `.gemini/get-shit-done/workflows/*`, `docs/work-queue-workflow.md`
  - Guidance: The old work-queue skill tree was replaced by GSD-oriented command/workflow surfaces; redirect readers instead of restoring deleted skill files.
  - Reference: `docs/ops/legacy-claude-reference-map.md`
- `scripts/work-queue/verify-gate-evidence.py` (9) — 9 combined reads
  - Redirect to: `docs/governance/SESSION-GOVERNANCE.md`, `docs/governance/TRUST-ARCHITECTURE.md`, `scripts/workflow/governance-checkpoints.yaml`, `.claude/hooks/plan-approval-gate.sh`, `.claude/hooks/session-governor-check.sh`, `scripts/review/cross-review.sh`
  - Guidance: Legacy stage-transition tooling was removed during workflow migration; redirect callers to governance docs/hooks instead of recreating the old executables.
  - Reference: `docs/ops/legacy-claude-reference-map.md`

### gemini top missing external reads
- `/tmp/pending-queue-snapshot.txt` — 1
- `/tmp/test-output.md` — 1

## Ecosystem strengthening recommendations
1. Keep exporting every provider into `logs/orchestrator/<provider>/session_*.jsonl` before the audit so the recent-delta section stays trustworthy.
2. Treat symbolic skill/tool reads separately from filesystem reads. Hermes emits many skill names in `file`, and counting them as missing files creates noisy false positives.
3. Preserve Codex command-shape fidelity in both export and audit layers. Recent native sessions use a mix of spaced-encoded commands and ordinary shell strings.
4. Use the recent-activity section to prioritize follow-up review on providers with actual post-audit event-time work instead of re-reading the full historical corpus every time. Recent read/write/edit hotspots should drive the next docs/tests hardening pass.
5. Keep pushing `uv run ... python` migration. Hermes, Gemini, and Codex still show meaningful bare `python3` usage density.

