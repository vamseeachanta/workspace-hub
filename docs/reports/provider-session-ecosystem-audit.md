# Provider session ecosystem audit — 2026-05-25

Scope: provider session artifacts rooted at `/mnt/local-analysis/workspace-hub/logs/orchestrator` with saved provider artifacts used only as fallback when raw logs are unavailable.

## Executive summary
- `claude` — source=raw_logs | sessions=66 | post_records=115036 | python3/1k=9.35 | uv-python/1k=54.1
- `codex` — source=raw_logs | sessions=80 | post_records=42243 | python3/1k=8.83 | uv-python/1k=20.26
- `hermes` — source=raw_logs | sessions=53 | post_records=402328 | python3/1k=7.36 | uv-python/1k=18.96
- `gemini` — source=raw_logs | sessions=71 | post_records=6200 | python3/1k=46.94 | uv-python/1k=6.29

- Migration debt density (known stale reads with redirect hints per 1k records): `claude` 14.99, `gemini` 13.87, `hermes` 0.51, `codex` 0.45.
- Highest-volume known migration debt: `claude` with 1724 mapped stale reads across 4 rule clusters; top hotspot: `legacy_work_queue_transition` (1004).
- Highest-density known migration debt: `claude` with 1724 mapped stale reads; top hotspot: `legacy_work_queue_transition` (1004, 58.24% of known debt).
- Scope note: Migration-debt figures are based on remediation-mapped entries from each provider's top missing repo reads.

## Provider interpretation summary
- Focus this week: prioritize legacy-path redirect cleanup and prompt/doc updates on claude (urgency 80.0, issue: legacy_work_queue_transition), then address gemini (urgency 47.72, issue: legacy_local_work_queue_items).
- Recommended actions:
  - `claude` [urgent_now] — prioritize legacy-path redirect cleanup and prompt/doc updates (urgency 80.0, issue: legacy_work_queue_transition; health=red; movement: rank unchanged at #1; urgency 80.00 (-8.00 vs previous audit); migration debt improved; path drift improved)
  - `gemini` [next_up] — prioritize legacy-path redirect cleanup and prompt/doc updates (urgency 47.72, issue: legacy_local_work_queue_items; health=red; movement: rank unchanged at #2; urgency 47.72 (-13.10 vs previous audit); recent activity cooled)
  - `codex` [investigate] — prioritize legacy-path redirect cleanup and prompt/doc updates (urgency 16.03, issue: llm_wiki_spinout_path_drift; health=yellow; movement: moved up 1 slot to #3; urgency 16.03 (-13.70 vs previous audit); recent activity cooled; path drift improved; corpus grew faster than event-time activity)
  - `hermes` [investigate] — prioritize legacy-path redirect cleanup and prompt/doc updates (urgency 13.67, issue: llm_wiki_spinout_path_drift; health=yellow; movement: moved down 1 slot to #4; urgency 13.67 (-20.42 vs previous audit); recent activity cooled; migration debt improved; path drift improved; corpus grew faster than event-time activity)
- Health overview:
  - `claude` [red] — red: urgent action tier; high migration debt; 7d sustained activity; currently active
  - `gemini` [red] — red: high migration debt; python3-heavy command hygiene
  - `codex` [yellow] — yellow: moderate migration debt; corpus anomaly needs interpretation; 7d sustained activity
  - `hermes` [yellow] — yellow: moderate migration debt; corpus anomaly needs interpretation; 7d sustained activity
- Watchlist triggers:
  - `claude` [page] — urgent-now provider with legacy_work_queue_transition | follow-up: Escalate immediately on claude: prioritize legacy-path redirect cleanup and prompt/doc updates
  - `gemini` [act_this_week] — red health due to legacy_local_work_queue_items | follow-up: Prioritize this week on gemini: prioritize legacy-path redirect cleanup and prompt/doc updates
  - `codex` [investigate] — yellow health with sustained 7d activity and llm_wiki_spinout_path_drift; corpus anomaly present | follow-up: Sample current traces on codex and verify whether llm_wiki_spinout_path_drift needs remap or docs cleanup
  - `hermes` [investigate] — yellow health with sustained 7d activity and llm_wiki_spinout_path_drift; corpus anomaly present | follow-up: Sample current traces on hermes and verify whether llm_wiki_spinout_path_drift needs remap or docs cleanup
- Change alerts:
  - `codex` [urgency_rank_improved_priority] — codex moved up from rank #4 to #3 | follow-up: Sample current traces on codex and verify whether llm_wiki_spinout_path_drift needs remap or docs cleanup
- Remediation playbooks:
  - `claude` [page] — issue=legacy_work_queue_transition | lane=governance-docs | owner=governance-maintainers | owner_surface=docs/governance/SESSION-GOVERNANCE.md | inspect=scripts/work-queue/verify-gate-evidence.py, scripts/work-queue/exit_stage.py, scripts/work-queue/start_stage.py | targets=docs/governance/SESSION-GOVERNANCE.md, docs/governance/TRUST-ARCHITECTURE.md, scripts/workflow/governance-checkpoints.yaml | steps: Inspect the top matched stale paths for legacy_work_queue_transition and confirm they should redirect rather than be recreated. | Open the canonical targets and migrate prompts/docs/tooling toward: docs/governance/SESSION-GOVERNANCE.md, docs/governance/TRUST-ARCHITECTURE.md, scripts/workflow/governance-checkpoints.yaml.
  - `gemini` [act_this_week] — issue=legacy_local_work_queue_items | lane=planning-workflow | owner=planning-ops | owner_surface=notes/agent-work-queue.md | inspect=.claude/work-queue/WRK-149.md, .claude/work-queue/working, .claude/work-queue/working/ | targets=GitHub issues, .planning/, notes/agent-work-queue.md | steps: Inspect the top matched stale paths for legacy_local_work_queue_items and confirm they should redirect rather than be recreated. | Open the canonical targets and migrate prompts/docs/tooling toward: GitHub issues, .planning/, notes/agent-work-queue.md.
  - `codex` [investigate] — issue=llm_wiki_spinout_path_drift | lane=monitoring | owner=audit-operators | owner_surface=docs/reports/provider-session-ecosystem-audit.md | inspect=knowledge/wikis/engineering/CLAUDE.md | targets=llm-wiki/wikis/, llm-wiki/docs/, docs/session-handoffs/2026-05-05-llm-wiki-spinout-max-completeness-handoff.md | steps: Inspect the top matched stale paths for llm_wiki_spinout_path_drift and confirm they should redirect rather than be recreated. | Open the canonical targets and migrate prompts/docs/tooling toward: llm-wiki/wikis/, llm-wiki/docs/, docs/session-handoffs/2026-05-05-llm-wiki-spinout-max-completeness-handoff.md.
  - `hermes` [investigate] — issue=llm_wiki_spinout_path_drift | lane=monitoring | owner=audit-operators | owner_surface=docs/reports/provider-session-ecosystem-audit.md | inspect=knowledge/wikis/engineering/wiki/index.md, knowledge/wikis/engineering/wiki/log.md, knowledge/wikis/marine-engineering/wiki/index.md | targets=llm-wiki/wikis/, llm-wiki/docs/, docs/session-handoffs/2026-05-05-llm-wiki-spinout-max-completeness-handoff.md | steps: Inspect the top matched stale paths for llm_wiki_spinout_path_drift and confirm they should redirect rather than be recreated. | Open the canonical targets and migrate prompts/docs/tooling toward: llm-wiki/wikis/, llm-wiki/docs/, docs/session-handoffs/2026-05-05-llm-wiki-spinout-max-completeness-handoff.md.
- Follow-up issue drafts:
  - `claude` [critical] — [critical] claude: remediate legacy_work_queue_transition | state=unchanged | owner=governance-maintainers | lane=governance-docs
  - `gemini` [high] — [high] gemini: remediate legacy_local_work_queue_items | state=unchanged | owner=planning-ops | lane=planning-workflow
  - `codex` [medium] — [medium] codex: remediate llm_wiki_spinout_path_drift | state=unchanged | owner=audit-operators | lane=monitoring
  - `hermes` [medium] — [medium] hermes: remediate llm_wiki_spinout_path_drift | state=unchanged | owner=audit-operators | lane=monitoring
- Issue posting readiness:
  - `claude` [ready] — should_open_issue=no | final_should_open=yes | evidence=complete | linked_issue=none | matched_on=none | reason=unchanged draft has no linked issue; safe to open once
  - `gemini` [ready] — should_open_issue=no | final_should_open=yes | evidence=complete | linked_issue=none | matched_on=none | reason=unchanged draft has no linked issue; safe to open once
  - `codex` [ready] — should_open_issue=no | final_should_open=yes | evidence=complete | linked_issue=none | matched_on=none | reason=unchanged draft has no linked issue; safe to open once
  - `hermes` [ready] — should_open_issue=no | final_should_open=yes | evidence=complete | linked_issue=none | matched_on=none | reason=unchanged draft has no linked issue; safe to open once
- Rank movements since previous audit:
  - `codex` — moved up 1 slot to #3; urgency 16.03 (-13.70 vs previous audit); recent activity cooled; path drift improved; corpus grew faster than event-time activity
  - `hermes` — moved down 1 slot to #4; urgency 13.67 (-20.42 vs previous audit); recent activity cooled; migration debt improved; path drift improved; corpus grew faster than event-time activity
- `claude` — rank=1 (prev=1, move=stable) | health=red | profile=sustained_background | 24h=0 posts/0 sessions | 7d=4047 posts/73 sessions | urgency=80.0 | tier=urgent_now | activity=active (stable) | corpus=aligned | debt=high_debt (improving) | drift=improving | python=uv_preferred (stable) | health summary: red: urgent action tier; high migration debt; 7d sustained activity; currently active | movement: rank unchanged at #1; urgency 80.00 (-8.00 vs previous audit); migration debt improved; path drift improved | primary issue: legacy_work_queue_transition | action: prioritize legacy-path redirect cleanup and prompt/doc updates
- `gemini` — rank=2 (prev=2, move=stable) | health=red | profile=light_recent | 24h=0 posts/0 sessions | 7d=1 posts/1 sessions | urgency=47.72 | tier=next_up | activity=idle (decreasing) | corpus=aligned | debt=high_debt (stable) | drift=stable | python=python3_heavy (stable) | health summary: red: high migration debt; python3-heavy command hygiene | movement: rank unchanged at #2; urgency 47.72 (-13.10 vs previous audit); recent activity cooled | primary issue: legacy_local_work_queue_items | action: prioritize legacy-path redirect cleanup and prompt/doc updates
- `codex` — rank=3 (prev=4, move=up) | health=yellow | profile=sustained_background | 24h=0 posts/0 sessions | 7d=1532 posts/95 sessions | urgency=16.03 | tier=investigate | activity=quiet (decreasing) | corpus=positive_corpus_growth_beyond_recent_activity | debt=moderate_debt (stable) | drift=improving | python=uv_preferred (stable) | health summary: yellow: moderate migration debt; corpus anomaly needs interpretation; 7d sustained activity | movement: moved up 1 slot to #3; urgency 16.03 (-13.70 vs previous audit); recent activity cooled; path drift improved; corpus grew faster than event-time activity | primary issue: llm_wiki_spinout_path_drift | action: prioritize legacy-path redirect cleanup and prompt/doc updates
- `hermes` — rank=4 (prev=3, move=down) | health=yellow | profile=sustained_background | 24h=0 posts/0 sessions | 7d=118763 posts/1190 sessions | urgency=13.67 | tier=investigate | activity=idle (decreasing) | corpus=positive_corpus_growth_beyond_recent_activity | debt=moderate_debt (improving) | drift=improving | python=uv_preferred (stable) | health summary: yellow: moderate migration debt; corpus anomaly needs interpretation; 7d sustained activity | movement: moved down 1 slot to #4; urgency 13.67 (-20.42 vs previous audit); recent activity cooled; migration debt improved; path drift improved; corpus grew faster than event-time activity | primary issue: llm_wiki_spinout_path_drift | action: prioritize legacy-path redirect cleanup and prompt/doc updates

## Recent activity since previous audit
- Previous audit timestamp: `2026-05-22T01:48:58Z`
- Recent post-audit activity: `claude` 811 post records / 7 sessions, `codex` 13 post records / 1 sessions.
- Scope note: This is event-time activity since the previous audit timestamp, not a census of newly exported historical/backfilled records.

## Rolling activity windows
- `last_24h` — `2026-05-24T09:15:31Z` → `2026-05-25T09:15:31Z`
  - Scope note: Last 24 hours of event-time activity ending at this audit timestamp.
  - Activity leaders: no provider activity captured in this window.
- `last_7d` — `2026-05-18T09:15:31Z` → `2026-05-25T09:15:31Z`
  - Scope note: Last 7 days of event-time activity ending at this audit timestamp.
  - Activity leaders: `hermes` 118763 post records / 1190 sessions, `claude` 4047 post records / 73 sessions, `codex` 1532 post records / 95 sessions, `gemini` 1 post records / 1 sessions.

## Corpus change since previous audit
- Previous audit timestamp: `2026-05-22T01:48:58Z`
- Scope note: Snapshot-to-snapshot corpus deltas reflect export additions/removals/reclassification and should be interpreted separately from event-time recent activity.
- Largest negative reconciliation gap: `claude`
- Largest positive reconciliation gap: `hermes`

## claude
- Source: raw_logs
- Sessions: 66
- Post-hook records: 115036
- Correction sessions: 0
- Unique runtime sessions: 793
- Prompt-like reads: 292
- Blank read targets: 0
- Missing repo reads: 8624
- Bare python3 bash calls: 1076
- `uv run ... python` bash calls: 6223

### claude top tools
- `Bash` — 63879
- `Read` — 21279
- `Edit` — 9507
- `Write` — 8421
- `unknown` — 3710
- `Grep` — 2613
- `Agent` — 1380
- `ToolSearch` — 681

### claude top repos
- `workspace-hub` — 110311
- `digitalmodel` — 1900
- `assetutilities` — 535
- `worldenergydata` — 201
- `workspace-hub-2510-plan` — 196
- `reconcile-main-20260427` — 122
- `agent-a597ec3f` — 100
- `issue-2348-exec` — 90

### claude top reads
- `scripts/work-queue/verify-gate-evidence.py` — 732
- `scripts/work-queue/generate-html-review.py` — 249
- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` — 225
- `docs/plans/README.md` — 198
- `docs/plans/_template-issue-plan.md` — 173
- `scripts/work-queue/exit_stage.py` — 137
- `scripts/work-queue/start_stage.py` — 135
- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` — 120
- `scripts/work-queue/close-item.sh` — 94
- `.claude/skills/coordination/issue-planning-mode/SKILL.md` — 74

### claude top symbolic reads
- `assethold/Makefile` — 1

### claude top sibling-repo reads
- `digitalmodel/pyproject.toml` — 34
- `assetutilities/src/assetutilities/common/data.py` — 34
- `llm-wiki/wikis/engineering-standards/CLAUDE.md` — 26
- `digitalmodel/scripts/semantic_validate.py` — 25
- `sabithaandkrishnaestates/taxes/2025/form-1120-filing-guide.md` — 23
- `assetutilities/pyproject.toml` — 22
- `digitalmodel/src/digitalmodel/citations/schema.py` — 22
- `digitalmodel/src/digitalmodel/cathodic_protection/__init__.py` — 18
- `digitalmodel/src/digitalmodel/cathodic_protection/dnv_rp_b401.py` — 18
- `teamresumes/cv/gp/custom/Geeta_CV_Recommendations.md` — 17

### claude top non-repo artifact reads
- none

### claude top Bash command families
- `ls` — 10093
- `grep` — 7629
- `uv run` — 6144
- `cat` — 5481
- `find` — 4188
- `gh` — 3697
- `bash` — 3051
- `echo` — 1766

### claude recent activity since previous audit
- Post-hook records since prior audit: 811
- Runtime sessions since prior audit: 7

### claude recent top tools
- `Bash` — 462
- `Read` — 145
- `Edit` — 127
- `unknown` — 36
- `Write` — 34

### claude recent top reads
- `/mnt/local-analysis/digitalmodel/src/digitalmodel/naval_architecture/b1528_sirocco_current_heading_rudder_report.py` — 26
- `docs/plans/2026-05-22-issue-2778-wiki-sibling-routing-contract.md` — 7
- `/mnt/local-analysis/llm-wiki/wikis/engineering-standards/wiki/standards/api-rp-2d.md` — 6
- `/mnt/local-analysis/digitalmodel/tests/naval_architecture/test_issue_2760_sirocco_current_rudder_revision.py` — 4
- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` — 4

### claude recent top writes
- `/tmp/issue-llm-wiki-search-routing.md` — 3
- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/project_wiki_sibling_naming_locked.md` — 2
- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/reference_ocimf_meg4_citation_style.md` — 1
- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/reference_ocimf_annex_a_graphic_style.md` — 1
- `/mnt/local-analysis/workspace-hub/docs/session-handoffs/2026-05-22-issue-2760-sirocco-pass-h-exit.md` — 1

### claude recent top edits
- `/mnt/local-analysis/digitalmodel/src/digitalmodel/naval_architecture/b1528_sirocco_current_heading_rudder_report.py` — 71
- `/mnt/local-analysis/digitalmodel/tests/naval_architecture/test_issue_2760_sirocco_current_rudder_revision.py` — 16
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-05-22-issue-2778-wiki-sibling-routing-contract.md` — 13
- `/mnt/local-analysis/digitalmodel/tests/naval_architecture/test_b1528_sirocco_current_heading_rudder.py` — 8
- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` — 3

### claude recent top Bash command families
- `ls` — 49
- `gh` — 46
- `grep` — 43
- `cat` — 40
- `Coef.xlsx"` — 35
- `echo` — 34
- `find` — 24
- `git` — 20

### claude recent top missing repo reads
- `.planning/handoffs/2026-05-22-issue-2778-hardover.md` — 1
- `scripts/review/results/2026-05-22-plan-2778-disagreement.md` — 1
- `scripts/review/results/2026-05-22-plan-2778-claude.md` — 1
- `scripts/review/results/2026-05-22-plan-2778-codex.md` — 1
- `scripts/review/results/2026-05-22-plan-2778-gemini.md` — 1

### claude recent top sibling-repo reads
- none

### claude recent top non-repo artifact reads
- none

### claude corpus change since previous audit
- Post-hook records: current 115036 vs previous 114225 (delta 811)
- Sessions: current 66 vs previous 64 (delta 2)
- Missing repo reads: current 8624 vs previous 8615 (delta 9)
- Event-time post records since prior audit: 811
- Reconciliation gap vs event-time delta: 0
- Status: aligned
- Interpretation: Snapshot post-record change aligns with recent event-time activity.

### claude top missing repo reads
- `scripts/work-queue/verify-gate-evidence.py` — 732
- `scripts/work-queue/generate-html-review.py` — 249
- `scripts/work-queue/exit_stage.py` — 137
- `scripts/work-queue/start_stage.py` — 135
- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` — 120
- `scripts/work-queue/close-item.sh` — 94
- `scripts/work-queue/whats-next.sh` — 70
- `.claude/skills/coordination/workspace/work-queue/SKILL.md` — 66
- `scripts/work-queue/archive-item.sh` — 61
- `scripts/work-queue/claim-item.sh` — 60

### claude top sibling-repo reads
- `digitalmodel/pyproject.toml` — 34
- `assetutilities/src/assetutilities/common/data.py` — 34
- `llm-wiki/wikis/engineering-standards/CLAUDE.md` — 26
- `digitalmodel/scripts/semantic_validate.py` — 25
- `sabithaandkrishnaestates/taxes/2025/form-1120-filing-guide.md` — 23
- `assetutilities/pyproject.toml` — 22
- `digitalmodel/src/digitalmodel/citations/schema.py` — 22
- `digitalmodel/src/digitalmodel/cathodic_protection/__init__.py` — 18
- `digitalmodel/src/digitalmodel/cathodic_protection/dnv_rp_b401.py` — 18
- `teamresumes/cv/gp/custom/Geeta_CV_Recommendations.md` — 17

### claude top non-repo artifact reads
- none

### claude remediation hints for stale repo reads
- `scripts/work-queue/verify-gate-evidence.py` (732), `scripts/work-queue/exit_stage.py` (137), `scripts/work-queue/start_stage.py` (135) — 1004 combined reads
  - Redirect to: `docs/governance/SESSION-GOVERNANCE.md`, `docs/governance/TRUST-ARCHITECTURE.md`, `scripts/workflow/governance-checkpoints.yaml`, `.claude/hooks/plan-approval-gate.sh`, `.claude/hooks/session-governor-check.sh`, `scripts/review/cross-review.sh`
  - Guidance: Legacy stage-transition tooling was removed during workflow migration; redirect callers to governance docs/hooks instead of recreating the old executables.
  - Reference: `docs/ops/legacy-claude-reference-map.md`
- `scripts/work-queue/close-item.sh` (94), `scripts/work-queue/whats-next.sh` (70), `scripts/work-queue/archive-item.sh` (61), `scripts/work-queue/claim-item.sh` (60) — 285 combined reads
  - Redirect to: `scripts/refresh-agent-work-queue.py`, `scripts/refresh-agent-work-queue.sh`, `notes/agent-work-queue.md`, `.planning/`, `GitHub issues`
  - Guidance: The repo no longer uses local queue scripts as the source of truth; prefer GitHub issue updates plus .planning evidence.
  - Reference: `docs/ops/legacy-claude-reference-map.md`
- `scripts/work-queue/generate-html-review.py` (249) — 249 combined reads
  - Redirect to: `scripts/review/cross-review.sh`, `templates/review-standard.html`, `docs/work-queue-workflow.md`
  - Guidance: Historical HTML review generation is no longer canonical; use the current cross-review workflow and stored review evidence instead.
  - Reference: `docs/ops/legacy-claude-reference-map.md`
- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` (120), `.claude/skills/coordination/workspace/work-queue/SKILL.md` (66) — 186 combined reads
  - Redirect to: `AGENTS.md`, `.claude/commands/gsd/*`, `.gemini/get-shit-done/workflows/*`, `docs/work-queue-workflow.md`
  - Guidance: The old work-queue skill tree was replaced by GSD-oriented command/workflow surfaces; redirect readers instead of restoring deleted skill files.
  - Reference: `docs/ops/legacy-claude-reference-map.md`

### claude top missing external reads
- `/tmp/tmp.4XN7Wckbxl/review-content.md` — 18
- `/mnt/workspace-hub/.claude/work-queue/assets/WRK-5082/geometry-dimensions-WRK-1360.md` — 13
- `/tmp/workspace-hub-2510-plan/docs/plans/2026-04-26-issue-2510-python-layout-cad-automation-demo.md` — 13
- `/mnt/workspace-hub/digitalmodel/src/digitalmodel/solvers/gmsh_meshing/mesh_generator.py` — 12
- `/mnt/workspace-hub/digitalmodel/tests/solvers/calculix/test_fem_chain.py` — 11
- `/tmp/tmp.4fvalbgSpv/review-content.md` — 10
- `/mnt/workspace-hub/.claude/skills/engineering/cad/freecad-automation/SKILL.md` — 10
- `/tmp/tmp.Y7GHawx2jw/review-content.md` — 9
- `/mnt/workspace-hub/digitalmodel/src/digitalmodel/hydrodynamics/hull_library/profile_schema.py` — 9
- `/mnt/workspace-hub/.claude/work-queue/working/WRK-1251.md` — 8

## codex
- Source: raw_logs
- Sessions: 80
- Post-hook records: 42243
- Correction sessions: 0
- Unique runtime sessions: 1300
- Prompt-like reads: 40
- Blank read targets: 0
- Missing repo reads: 1253
- Bare python3 bash calls: 373
- `uv run ... python` bash calls: 856

### codex top tools
- `Bash` — 32019
- `Read` — 7104
- `Grep` — 1997
- `update_plan` — 418
- `list_mcp_resources` — 211
- `_add_comment_to_issue` — 118
- `_get_repo` — 34
- `_fetch_commit` — 33

### codex top repos
- `workspace-hub` — 42243

### codex top reads
- `docs/plans/README.md` — 280
- `docs/plans/_template-issue-plan.md` — 94
- `docs/standards/HARD-STOP-POLICY.md` — 84
- `AGENTS.md` — 81
- `config/scheduled-tasks/schedule-tasks.yaml` — 69
- `docs/standards/CONTROL_PLANE_CONTRACT.md` — 67
- `docs/standards/AI_REVIEW_ROUTING_POLICY.md` — 51
- `docs/ops/scheduled-tasks.md` — 49
- `config/workstations/registry.yaml` — 45
- `scripts/_core/sync-agent-configs.sh` — 43

### codex top symbolic reads
- `github://vamseeachanta/digitalmodel/issues/500` — 79
- `github://vamseeachanta/digitalmodel/issues/605` — 40
- `github://vamseeachanta/workspace-hub/issues/2488` — 32
- `github://vamseeachanta/digitalmodel/issues/606` — 31
- `github://vamseeachanta/digitalmodel/issues/611` — 27
- `github://vamseeachanta/workspace-hub/issues/2486` — 24
- `github://vamseeachanta/workspace-hub/issues/2726` — 22
- `github://vamseeachanta/workspace-hub/issues/2510` — 20
- `github://vamseeachanta/digitalmodel/issues/609` — 20
- `github://vamseeachanta/workspace-hub/issues/2511` — 17

### codex top sibling-repo reads
- `digitalmodel/src/digitalmodel/citations/schema.py` — 6
- `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` — 4
- `digitalmodel/src/digitalmodel/citations/registry.py` — 4
- `aceengineer-website/vercel.json` — 3
- `assethold/.github/workflows/python-tests.yml` — 3
- `assethold/AGENTS.md` — 3
- `digitalmodel/tests/citations/test_registry.py` — 2
- `digitalmodel/README.md` — 1
- `aceengineer-website/package.json` — 1
- `aceengineer-website/build.js` — 1

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
- `sed` — 7659
- `rg` — 2958
- `nl` — 2771
- `find` — 1184
- `uv run` — 967
- `ls` — 824
- `git status` — 812
- `pwd` — 613

### codex recent activity since previous audit
- Post-hook records since prior audit: 13
- Runtime sessions since prior audit: 1

### codex recent top tools
- `Bash` — 13

### codex recent top reads
- none

### codex recent top writes
- none

### codex recent top edits
- none

### codex recent top Bash command families
- `ls` — 2
- `sed` — 1
- `git status` — 1
- `ps` — 1
- `git stash` — 1
- `timeout` — 1
- `find` — 1

### codex recent top missing repo reads
- none

### codex recent top sibling-repo reads
- none

### codex recent top non-repo artifact reads
- none

### codex corpus change since previous audit
- Post-hook records: current 42243 vs previous 42187 (delta 56)
- Sessions: current 80 vs previous 80 (delta 0)
- Missing repo reads: current 1253 vs previous 1280 (delta -27)
- Event-time post records since prior audit: 13
- Reconciliation gap vs event-time delta: 43
- Status: positive_corpus_growth_beyond_recent_activity
- Interpretation: Snapshot grew more than recent event-time activity, suggesting backfill or expanded export coverage.

### codex top missing repo reads
- `src/digitalmodel/marine_ops/installation/jumper_installation.py` — 21
- `src/digitalmodel/marine_ops/installation/jumper_lift.py` — 21
- `src/digitalmodel/hydrodynamics/diffraction/input_schemas.py` — 15
- `src/digitalmodel/solvers/orcaflex/modular_generator/__init__.py` — 14
- `docs/domains/orcaflex/subsea/jumper/installation/ballymore_plet_plem/spec.yml` — 11
- `src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py` — 11
- `knowledge/wikis/engineering/CLAUDE.md` — 10
- `src/digitalmodel/solvers/orcaflex/modular_generator/schema/root.py` — 10
- `src/worldenergydata/cost/data_collection/calibration_schema.py` — 9
- `docs/domains/orcaflex/subsea/jumper/installation/ballymore_mf_plet/spec.yml` — 9

### codex top sibling-repo reads
- `digitalmodel/src/digitalmodel/citations/schema.py` — 6
- `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` — 4
- `digitalmodel/src/digitalmodel/citations/registry.py` — 4
- `aceengineer-website/vercel.json` — 3
- `assethold/.github/workflows/python-tests.yml` — 3
- `assethold/AGENTS.md` — 3
- `digitalmodel/tests/citations/test_registry.py` — 2
- `digitalmodel/README.md` — 1
- `aceengineer-website/package.json` — 1
- `aceengineer-website/build.js` — 1

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
- `knowledge/wikis/engineering/CLAUDE.md` (10) — 10 combined reads
  - Redirect to: `llm-wiki/wikis/`, `llm-wiki/docs/`, `docs/session-handoffs/2026-05-05-llm-wiki-spinout-max-completeness-handoff.md`, `docs/sessions/2026-05-07-nest-llm-wiki-kaggle-into-hub.md`
  - Guidance: The LLM-wiki artifact store moved out of workspace-hub/knowledge into the llm-wiki repository; redirect wiki-content reads to llm-wiki and keep control-plane work in workspace-hub.
  - Reference: `docs/ops/legacy-claude-reference-map.md`
- `src/worldenergydata/cost/data_collection/calibration_schema.py` (9) — 9 combined reads
  - Redirect to: `worldenergydata/src/worldenergydata/`, `worldenergydata/tests/unit/cost/`, `worldenergydata/docs/plans/`, `assethold/src/assethold/`, `aceengineer-website/sitemap.xml`
  - Guidance: Codex/Hermes sessions may run from workspace-hub while inspecting nested tier-1 repos; prepend the owning repo root before treating these reads as missing workspace-hub files.
  - Reference: `docs/ops/legacy-claude-reference-map.md`

### codex top missing external reads
- none

## hermes
- Source: raw_logs
- Sessions: 53
- Post-hook records: 402328
- Correction sessions: 51
- Unique runtime sessions: 6187
- Prompt-like reads: 1914
- Blank read targets: 846
- Missing repo reads: 1662
- Bare python3 bash calls: 2962
- `uv run ... python` bash calls: 7628

### hermes top tools
- `Bash` — 151526
- `Read` — 129792
- `Grep` — 51426
- `Write` — 32929
- `Edit` — 27997
- `Task` — 3986
- `Browser` — 2737
- `browser_console` — 838

### hermes top repos
- `workspace-hub` — 402328

### hermes top reads
- `/mnt/local-analysis/digitalmodel/src/digitalmodel/naval_architecture/b1528_sirocco_current_heading_rudder_report.py` — 4222
- `/mnt/local-analysis/digitalmodel/tests/naval_architecture/test_b1528_sirocco_current_heading_rudder.py` — 1597
- `/mnt/local-analysis/digitalmodel/tests/naval_architecture/test_issue_2760_sirocco_current_rudder_revision.py` — 1542
- `/mnt/local-analysis/digitalmodel/src/digitalmodel/naval_architecture/data/b1528_sirocco_current_heading_rudder.yml` — 1485
- `docs/plans/README.md` — 1462
- `/mnt/local-analysis/worktrees/workspace-hub-2720/scripts/readiness/telegram_hermes_readiness.py` — 1438
- `/mnt/local-analysis/worktrees/workspace-hub-2720/tests/readiness/test_telegram_hermes_readiness.py` — 1033
- `docs/plans/2026-05-20-issue-2760-b1528-sirocco-force-review-revision.md` — 1032
- `docs/plans/_template-issue-plan.md` — 888
- `/mnt/local-analysis/worktrees/workspace-hub-2720/scripts/telegram_dispatch/policy.py` — 718

### hermes top symbolic reads
- `github/github-issues` — 4473
- `coordination/issue-planning-mode` — 4344
- `software-development/gh-work-execution` — 3774
- `github-issues` — 3177
- `workspace-hub/worktree-branch-sync-hygiene` — 2538
- `software-development/test-driven-development` — 1806
- `coordination/gh-work-planning` — 1484
- `hermes-agent` — 1192
- `development/artifact-commit-verification` — 1115
- `research/llm-wiki` — 885

### hermes top sibling-repo reads
- `worldenergydata/scripts/marketing/generate_hurricane_mooring_risk_infographic.py` — 63
- `worldenergydata/scripts/maintenance/verify_repo_structure.py` — 62
- `worldenergydata/reports/modules/marketing/hurricane_mooring_safety_infographic_stats.json` — 62
- `worldenergydata/.github/workflows/ci.yml` — 60
- `digitalmodel/examples/demos/gtm/tests/test_ctv_operability_reference.py` — 58
- `digitalmodel/examples/demos/gtm/demo_02_wall_thickness_multicode.py` — 57
- `worldenergydata/data/modules/marine_safety/input/fatality_incidents.csv` — 57
- `worldenergydata/data/modules/marine_safety/input/foundering_incidents.csv` — 57
- `worldenergydata/data/modules/marine_safety/input/hatch_incidents.csv` — 57
- `worldenergydata/docs/plans/2026-05-12-issue-403-hurricane-mooring-risk-infographic.md` — 56

### hermes top non-repo artifact reads
- none

### hermes top Bash command families
- `gh` — 22598
- `set` — 15857
- `uv run` — 13857
- `git status` — 10309
- `git diff` — 5728
- `python` — 4101
- `bash` — 3781
- `git` — 3302

### hermes recent activity since previous audit
- Post-hook records since prior audit: 0
- Runtime sessions since prior audit: 0

### hermes recent top tools
- none

### hermes recent top reads
- none

### hermes recent top writes
- none

### hermes recent top edits
- none

### hermes recent top Bash command families
- none

### hermes recent top missing repo reads
- none

### hermes recent top sibling-repo reads
- none

### hermes recent top non-repo artifact reads
- none

### hermes corpus change since previous audit
- Post-hook records: current 402328 vs previous 316593 (delta 85735)
- Sessions: current 53 vs previous 53 (delta 0)
- Missing repo reads: current 1662 vs previous 1623 (delta 39)
- Event-time post records since prior audit: 0
- Reconciliation gap vs event-time delta: 85735
- Status: positive_corpus_growth_beyond_recent_activity
- Interpretation: Snapshot grew more than recent event-time activity, suggesting backfill or expanded export coverage.

### hermes top missing repo reads
- `.claude/worktrees/ecosystem-sync/docs/plans/2026-04-20-aceengineer-ecosystem-sync-plan.md` — 67
- `knowledge/wikis/engineering/wiki/index.md` — 52
- `scripts/review/results/2026-05-16-plan-2720-codex.md` — 40
- `scripts/review/results/2026-05-16-plan-2720-gemini.md` — 40
- `scripts/review/results/2026-05-16-plan-2720-claude.md` — 36
- `knowledge/wikis/engineering/wiki/log.md` — 35
- `scripts/review/results/2026-05-16-plan-2720-disagreement.md` — 34
- `client_projects/engineering_workbooks/ballymore/jumper_manifold_to_plet/claude_excel_addin/jumper_lift.py` — 32
- `knowledge/wikis/marine-engineering/wiki/index.md` — 28
- `knowledge/wikis/engineering/wiki/workflows/orcawave-to-orcaflex-pipeline.md` — 25

### hermes top sibling-repo reads
- `worldenergydata/scripts/marketing/generate_hurricane_mooring_risk_infographic.py` — 63
- `worldenergydata/scripts/maintenance/verify_repo_structure.py` — 62
- `worldenergydata/reports/modules/marketing/hurricane_mooring_safety_infographic_stats.json` — 62
- `worldenergydata/.github/workflows/ci.yml` — 60
- `digitalmodel/examples/demos/gtm/tests/test_ctv_operability_reference.py` — 58
- `digitalmodel/examples/demos/gtm/demo_02_wall_thickness_multicode.py` — 57
- `worldenergydata/data/modules/marine_safety/input/fatality_incidents.csv` — 57
- `worldenergydata/data/modules/marine_safety/input/foundering_incidents.csv` — 57
- `worldenergydata/data/modules/marine_safety/input/hatch_incidents.csv` — 57
- `worldenergydata/docs/plans/2026-05-12-issue-403-hurricane-mooring-risk-infographic.md` — 56

### hermes top non-repo artifact reads
- none

### hermes remediation hints for stale repo reads
- `knowledge/wikis/engineering/wiki/index.md` (52), `knowledge/wikis/engineering/wiki/log.md` (35), `knowledge/wikis/marine-engineering/wiki/index.md` (28), `knowledge/wikis/engineering/wiki/workflows/orcawave-to-orcaflex-pipeline.md` (25) — 140 combined reads
  - Redirect to: `llm-wiki/wikis/`, `llm-wiki/docs/`, `docs/session-handoffs/2026-05-05-llm-wiki-spinout-max-completeness-handoff.md`, `docs/sessions/2026-05-07-nest-llm-wiki-kaggle-into-hub.md`
  - Guidance: The LLM-wiki artifact store moved out of workspace-hub/knowledge into the llm-wiki repository; redirect wiki-content reads to llm-wiki and keep control-plane work in workspace-hub.
  - Reference: `docs/ops/legacy-claude-reference-map.md`
- `.claude/worktrees/ecosystem-sync/docs/plans/2026-04-20-aceengineer-ecosystem-sync-plan.md` (67) — 67 combined reads
  - Redirect to: `main repo branch/worktree`, `docs/plans/`, `.planning/`, `GitHub issues`
  - Guidance: Provider logs sometimes retain ephemeral worktree or temp paths; treat these as session-local and re-resolve the durable artifact from the main repo, .planning, or GitHub issue evidence before acting.
  - Reference: `docs/ops/legacy-claude-reference-map.md`

### hermes top missing external reads
- `/mnt/local-analysis/worktrees/workspace-hub-2720/scripts/readiness/telegram_hermes_readiness.py` — 1438
- `/mnt/local-analysis/worktrees/workspace-hub-2720/tests/readiness/test_telegram_hermes_readiness.py` — 1033
- `/mnt/local-analysis/worktrees/workspace-hub-2720/scripts/telegram_dispatch/policy.py` — 718
- `/mnt/local-analysis/worktrees/workspace-hub-2657/scripts/analysis/provider_session_ecosystem_audit.py` — 666
- `/mnt/local-analysis/agent-worktrees/workspace-hub-issue-2766-ace-linux-1-normalization/scripts/readiness/telegram_hermes_readiness.py` — 555
- `/mnt/local-analysis/worktrees/workspace-hub-2720/tests/telegram_dispatch/test_dispatch_policy.py` — 472
- `/mnt/local-analysis/agent-worktrees/workspace-hub-issue-2766-ace-linux-1-normalization/scripts/workstations/check-tier1-repo-baseline.py` — 372
- `/mnt/local-analysis/agent-worktrees/workspace-hub-issue-2766-ace-linux-1-normalization/tests/workstations/test_check_tier1_repo_baseline.py` — 359
- `/mnt/local-analysis/agent-worktrees/workspace-hub-issue-2766-ace-linux-1-normalization/tests/readiness/test_telegram_hermes_readiness_tier1_baseline.py` — 289
- `/mnt/local-analysis/worktrees/workspace-hub-2720/config/workstations/registry.yaml` — 270

## gemini
- Source: raw_logs
- Sessions: 71
- Post-hook records: 6200
- Correction sessions: 0
- Unique runtime sessions: 355
- Prompt-like reads: 18
- Blank read targets: 0
- Missing repo reads: 611
- Bare python3 bash calls: 291
- `uv run ... python` bash calls: 39

### gemini top tools
- `Bash` — 2288
- `Read` — 2181
- `Grep` — 655
- `Write` — 535
- `Edit` — 394
- `Browser` — 133
- `ToolSearch` — 9
- `generalist` — 3

### gemini top repos
- `workspace-hub` — 6200

### gemini top reads
- `.claude/work-queue/` — 29
- `scripts/operations/compliance/migrate_specs_to_workspace.sh` — 28
- `CLAUDE.md` — 23
- `.` — 22
- `.claude/work-queue` — 18
- `.claude/work-queue/WRK-149.md` — 17
- `.claude/work-queue/pending` — 16
- `digitalmodel/scripts/benchmark/validate_owd_vs_spec.py` — 16
- `AGENTS.md` — 14
- `.claude/work-queue/INDEX.md` — 13

### gemini top symbolic reads
- `digitalmodel` — 31
- `worldenergydata` — 19
- `digitalmodel/src/digitalmodel` — 15
- `tests` — 10
- `assethold` — 9
- `digitalmodel/src` — 9
- `config` — 8
- `scripts` — 8
- `doris` — 8
- `src` — 7

### gemini top sibling-repo reads
- `digitalmodel/scripts/benchmark/validate_owd_vs_spec.py` — 16
- `digitalmodel/pyproject.toml` — 11
- `digitalmodel/tests/marine_ops/artificial_lift/dynacard/test_diagnostics.py` — 8
- `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/benchmark_runner.py` — 6
- `digitalmodel/CLAUDE.md` — 5
- `digitalmodel/src/digitalmodel/subsea/pipeline/pipeline_pressure.py` — 5
- `worldenergydata/specs/README.md` — 4
- `assethold/docs/domain/realestate/re_multifamily/examples/` — 4
- `worldenergydata/.claude` — 4
- `digitalmodel/src/digitalmodel/infrastructure/base_configs/config_framework.py` — 4

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
- Post-hook records: current 6200 vs previous 6200 (delta 0)
- Sessions: current 71 vs previous 71 (delta 0)
- Missing repo reads: current 611 vs previous 611 (delta 0)
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
- `digitalmodel/scripts/benchmark/validate_owd_vs_spec.py` — 16
- `digitalmodel/pyproject.toml` — 11
- `digitalmodel/tests/marine_ops/artificial_lift/dynacard/test_diagnostics.py` — 8
- `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/benchmark_runner.py` — 6
- `digitalmodel/CLAUDE.md` — 5
- `digitalmodel/src/digitalmodel/subsea/pipeline/pipeline_pressure.py` — 5
- `worldenergydata/specs/README.md` — 4
- `assethold/docs/domain/realestate/re_multifamily/examples/` — 4
- `worldenergydata/.claude` — 4
- `digitalmodel/src/digitalmodel/infrastructure/base_configs/config_framework.py` — 4

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

