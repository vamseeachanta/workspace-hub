# Provider session ecosystem audit — 2026-05-18

Scope: provider session artifacts rooted at `/mnt/local-analysis/workspace-hub/logs/orchestrator` with saved provider artifacts used only as fallback when raw logs are unavailable.

## Executive summary
- `claude` — source=raw_logs | sessions=61 | post_records=110989 | python3/1k=9.46 | uv-python/1k=55.84
- `codex` — source=raw_logs | sessions=76 | post_records=40631 | python3/1k=9.18 | uv-python/1k=20.43
- `hermes` — source=raw_logs | sessions=49 | post_records=271373 | python3/1k=10.3 | uv-python/1k=16.81
- `gemini` — source=raw_logs | sessions=69 | post_records=6198 | python3/1k=46.95 | uv-python/1k=6.29

- Migration debt density (known stale reads with redirect hints per 1k records): `claude` 15.53, `gemini` 13.88, `hermes` 0.76, `codex` 0.47.
- Highest-volume known migration debt: `claude` with 1724 mapped stale reads across 4 rule clusters; top hotspot: `legacy_work_queue_transition` (1004).
- Highest-density known migration debt: `claude` with 1724 mapped stale reads; top hotspot: `legacy_work_queue_transition` (1004, 58.24% of known debt).
- Scope note: Migration-debt figures are based on remediation-mapped entries from each provider's top missing repo reads.

## Provider interpretation summary
- Focus this week: prioritize legacy-path redirect cleanup and prompt/doc updates on claude (urgency 80.0, issue: legacy_work_queue_transition), then address gemini (urgency 75.72, issue: legacy_local_work_queue_items).
- Recommended actions:
  - `claude` [urgent_now] — prioritize legacy-path redirect cleanup and prompt/doc updates (urgency 80.0, issue: legacy_work_queue_transition; health=red; movement: rank unchanged at #1; urgency 80.00 (+0.00 vs previous audit); migration debt improved; path drift improved)
  - `gemini` [urgent_now] — prioritize legacy-path redirect cleanup and prompt/doc updates (urgency 75.72, issue: legacy_local_work_queue_items; health=red; movement: rank unchanged at #2; urgency 75.72 (+9.80 vs previous audit); recent activity increased; migration debt improved; path drift improved; corpus grew faster than event-time activity)
  - `hermes` [next_up] — prioritize legacy-path redirect cleanup and prompt/doc updates (urgency 37.42, issue: llm_wiki_spinout_path_drift; health=red; movement: rank unchanged at #3; urgency 37.42 (-3.80 vs previous audit); migration debt improved; path drift improved; corpus grew faster than event-time activity)
  - `codex` [investigate] — prioritize legacy-path redirect cleanup and prompt/doc updates (urgency 21.79, issue: llm_wiki_spinout_path_drift; health=yellow; movement: rank unchanged at #4; urgency 21.79 (-9.35 vs previous audit); migration debt improved; path drift worsened; python hygiene improved)
- Health overview:
  - `claude` [red] — red: urgent action tier; high migration debt; 7d sustained activity; currently active
  - `gemini` [red] — red: urgent action tier; high migration debt; python3-heavy command hygiene; corpus anomaly needs interpretation
  - `hermes` [red] — red: moderate migration debt; corpus anomaly needs interpretation; 7d sustained activity; currently active
  - `codex` [yellow] — yellow: moderate migration debt; path drift worsening; 7d sustained activity; currently active
- Watchlist triggers:
  - `claude` [page] — urgent-now provider with legacy_work_queue_transition | follow-up: Escalate immediately on claude: prioritize legacy-path redirect cleanup and prompt/doc updates
  - `gemini` [page] — urgent-now provider with legacy_local_work_queue_items | follow-up: Escalate immediately on gemini: prioritize legacy-path redirect cleanup and prompt/doc updates
  - `hermes` [act_this_week] — red health due to llm_wiki_spinout_path_drift; corpus anomaly present | follow-up: Prioritize this week on hermes: prioritize legacy-path redirect cleanup and prompt/doc updates
  - `codex` [investigate] — yellow health with sustained 7d activity and llm_wiki_spinout_path_drift | follow-up: Sample current traces on codex and verify whether llm_wiki_spinout_path_drift needs remap or docs cleanup
- Change alerts:
  - `codex` [trigger_escalated] — codex trigger escalated from monitor to investigate | follow-up: Sample current traces on codex and verify whether llm_wiki_spinout_path_drift needs remap or docs cleanup
  - `gemini` [trigger_escalated] — gemini trigger escalated from act_this_week to page | follow-up: Escalate immediately on gemini: prioritize legacy-path redirect cleanup and prompt/doc updates
- Remediation playbooks:
  - `claude` [page] — issue=legacy_work_queue_transition | lane=governance-docs | owner=governance-maintainers | owner_surface=docs/governance/SESSION-GOVERNANCE.md | inspect=scripts/work-queue/verify-gate-evidence.py, scripts/work-queue/exit_stage.py, scripts/work-queue/start_stage.py | targets=docs/governance/SESSION-GOVERNANCE.md, docs/governance/TRUST-ARCHITECTURE.md, scripts/workflow/governance-checkpoints.yaml | steps: Inspect the top matched stale paths for legacy_work_queue_transition and confirm they should redirect rather than be recreated. | Open the canonical targets and migrate prompts/docs/tooling toward: docs/governance/SESSION-GOVERNANCE.md, docs/governance/TRUST-ARCHITECTURE.md, scripts/workflow/governance-checkpoints.yaml.
  - `gemini` [page] — issue=legacy_local_work_queue_items | lane=planning-workflow | owner=planning-ops | owner_surface=notes/agent-work-queue.md | inspect=.claude/work-queue/WRK-149.md, .claude/work-queue/working, .claude/work-queue/working/ | targets=GitHub issues, .planning/, notes/agent-work-queue.md | steps: Inspect the top matched stale paths for legacy_local_work_queue_items and confirm they should redirect rather than be recreated. | Open the canonical targets and migrate prompts/docs/tooling toward: GitHub issues, .planning/, notes/agent-work-queue.md.
  - `hermes` [act_this_week] — issue=llm_wiki_spinout_path_drift | lane=monitoring | owner=audit-operators | owner_surface=docs/reports/provider-session-ecosystem-audit.md | inspect=knowledge/wikis/engineering/wiki/index.md, knowledge/wikis/engineering/wiki/log.md, knowledge/wikis/marine-engineering/wiki/index.md | targets=llm-wiki/wikis/, llm-wiki/docs/, docs/session-handoffs/2026-05-05-llm-wiki-spinout-max-completeness-handoff.md | steps: Inspect the top matched stale paths for llm_wiki_spinout_path_drift and confirm they should redirect rather than be recreated. | Open the canonical targets and migrate prompts/docs/tooling toward: llm-wiki/wikis/, llm-wiki/docs/, docs/session-handoffs/2026-05-05-llm-wiki-spinout-max-completeness-handoff.md.
  - `codex` [investigate] — issue=llm_wiki_spinout_path_drift | lane=monitoring | owner=audit-operators | owner_surface=docs/reports/provider-session-ecosystem-audit.md | inspect=knowledge/wikis/engineering/CLAUDE.md | targets=llm-wiki/wikis/, llm-wiki/docs/, docs/session-handoffs/2026-05-05-llm-wiki-spinout-max-completeness-handoff.md | steps: Inspect the top matched stale paths for llm_wiki_spinout_path_drift and confirm they should redirect rather than be recreated. | Open the canonical targets and migrate prompts/docs/tooling toward: llm-wiki/wikis/, llm-wiki/docs/, docs/session-handoffs/2026-05-05-llm-wiki-spinout-max-completeness-handoff.md.
- Follow-up issue drafts:
  - `claude` [critical] — [critical] claude: remediate legacy_work_queue_transition | state=unchanged | owner=governance-maintainers | lane=governance-docs
  - `gemini` [critical] — [critical] gemini: remediate legacy_local_work_queue_items | state=changed | owner=planning-ops | lane=planning-workflow
  - `hermes` [high] — [high] hermes: remediate llm_wiki_spinout_path_drift | state=unchanged | owner=audit-operators | lane=monitoring
  - `codex` [medium] — [medium] codex: remediate llm_wiki_spinout_path_drift | state=new | owner=audit-operators | lane=monitoring
- Issue posting readiness:
  - `claude` [ready] — should_open_issue=no | final_should_open=yes | evidence=complete | linked_issue=none | matched_on=none | reason=unchanged draft has no linked issue; safe to open once
  - `gemini` [ready] — should_open_issue=yes | final_should_open=yes | evidence=complete | linked_issue=none | matched_on=none | reason=changed actionable draft with no linked issue found
  - `hermes` [ready] — should_open_issue=no | final_should_open=yes | evidence=complete | linked_issue=none | matched_on=none | reason=unchanged draft has no linked issue; safe to open once
  - `codex` [ready] — should_open_issue=yes | final_should_open=yes | evidence=complete | linked_issue=none | matched_on=none | reason=new actionable draft with no linked issue found
- `claude` — rank=1 (prev=1, move=stable) | health=red | profile=sustained_background | 24h=666 posts/30 sessions | 7d=5832 posts/86 sessions | urgency=80.0 | tier=urgent_now | activity=active (stable) | corpus=aligned | debt=high_debt (improving) | drift=improving | python=uv_preferred (stable) | health summary: red: urgent action tier; high migration debt; 7d sustained activity; currently active | movement: rank unchanged at #1; urgency 80.00 (+0.00 vs previous audit); migration debt improved; path drift improved | primary issue: legacy_work_queue_transition | action: prioritize legacy-path redirect cleanup and prompt/doc updates
- `gemini` — rank=2 (prev=2, move=stable) | health=red | profile=light_recent | 24h=0 posts/0 sessions | 7d=8 posts/6 sessions | urgency=75.72 | tier=urgent_now | activity=active (increasing) | corpus=positive_corpus_growth_beyond_recent_activity | debt=high_debt (improving) | drift=improving | python=python3_heavy (stable) | health summary: red: urgent action tier; high migration debt; python3-heavy command hygiene; corpus anomaly needs interpretation | movement: rank unchanged at #2; urgency 75.72 (+9.80 vs previous audit); recent activity increased; migration debt improved; path drift improved; corpus grew faster than event-time activity | primary issue: legacy_local_work_queue_items | action: prioritize legacy-path redirect cleanup and prompt/doc updates
- `hermes` — rank=3 (prev=3, move=stable) | health=red | profile=sustained_background | 24h=679 posts/26 sessions | 7d=69268 posts/1330 sessions | urgency=37.42 | tier=next_up | activity=active (stable) | corpus=positive_corpus_growth_beyond_recent_activity | debt=moderate_debt (improving) | drift=improving | python=mixed (stable) | health summary: red: moderate migration debt; corpus anomaly needs interpretation; 7d sustained activity; currently active | movement: rank unchanged at #3; urgency 37.42 (-3.80 vs previous audit); migration debt improved; path drift improved; corpus grew faster than event-time activity | primary issue: llm_wiki_spinout_path_drift | action: prioritize legacy-path redirect cleanup and prompt/doc updates
- `codex` — rank=4 (prev=4, move=stable) | health=yellow | profile=sustained_background | 24h=580 posts/29 sessions | 7d=8870 posts/224 sessions | urgency=21.79 | tier=investigate | activity=active (stable) | corpus=aligned | debt=moderate_debt (improving) | drift=worsening | python=uv_preferred (improving) | health summary: yellow: moderate migration debt; path drift worsening; 7d sustained activity; currently active | movement: rank unchanged at #4; urgency 21.79 (-9.35 vs previous audit); migration debt improved; path drift worsened; python hygiene improved | primary issue: llm_wiki_spinout_path_drift | action: prioritize legacy-path redirect cleanup and prompt/doc updates

## Recent activity since previous audit
- Previous audit timestamp: `2026-05-11T09:15:03Z`
- Recent post-audit activity: `hermes` 69268 post records / 1330 sessions, `codex` 8870 post records / 224 sessions, `claude` 5835 post records / 86 sessions, `gemini` 8 post records / 6 sessions.
- Scope note: This is event-time activity since the previous audit timestamp, not a census of newly exported historical/backfilled records.

## Rolling activity windows
- `last_24h` — `2026-05-17T09:15:04Z` → `2026-05-18T09:15:04Z`
  - Scope note: Last 24 hours of event-time activity ending at this audit timestamp.
  - Activity leaders: `hermes` 679 post records / 26 sessions, `claude` 666 post records / 30 sessions, `codex` 580 post records / 29 sessions.
- `last_7d` — `2026-05-11T09:15:04Z` → `2026-05-18T09:15:04Z`
  - Scope note: Last 7 days of event-time activity ending at this audit timestamp.
  - Activity leaders: `hermes` 69268 post records / 1330 sessions, `codex` 8870 post records / 224 sessions, `claude` 5832 post records / 86 sessions, `gemini` 8 post records / 6 sessions.

## Corpus change since previous audit
- Previous audit timestamp: `2026-05-11T09:15:03Z`
- Scope note: Snapshot-to-snapshot corpus deltas reflect export additions/removals/reclassification and should be interpreted separately from event-time recent activity.
- Largest negative reconciliation gap: `claude`
- Largest positive reconciliation gap: `hermes`

## claude
- Source: raw_logs
- Sessions: 61
- Post-hook records: 110989
- Correction sessions: 0
- Unique runtime sessions: 721
- Prompt-like reads: 289
- Blank read targets: 0
- Missing repo reads: 8609
- Bare python3 bash calls: 1050
- `uv run ... python` bash calls: 6198

### claude top tools
- `Bash` — 61689
- `Read` — 20620
- `Edit` — 9125
- `Write` — 8204
- `unknown` — 3181
- `Grep` — 2605
- `Agent` — 1318
- `ToolSearch` — 681

### claude top repos
- `workspace-hub` — 106382
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
- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` — 215
- `docs/plans/README.md` — 190
- `docs/plans/_template-issue-plan.md` — 164
- `scripts/work-queue/exit_stage.py` — 137
- `scripts/work-queue/start_stage.py` — 135
- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` — 120
- `scripts/work-queue/close-item.sh` — 94
- `scripts/work-queue/whats-next.sh` — 70

### claude top symbolic reads
- none

### claude top sibling-repo reads
- `digitalmodel/src/digitalmodel/geotechnical/on_bottom_stability.py` — 9
- `digitalmodel/specs/data-needs.yaml` — 7
- `digitalmodel/specs/module-registry.yaml` — 5
- `digitalmodel/src/digitalmodel/naval_architecture/curves.py` — 3
- `digitalmodel/docs/domains/openfoam/naval_architecture/propeller_hull_interaction.pdf` — 2
- `digitalmodel/docs/domains/ship-design/maneuvering_ship.pdf` — 2
- `worldenergydata/tests/test_resource_estimation.py` — 2
- `digitalmodel/docs/domains/hydrodynamics/literature/viviani-2007-four-quadrant-wageningen-b-series.pdf` — 2
- `digitalmodel/tests/fixtures/reporting/riser_lazy_wave_fpso.metadata.json` — 2
- `digitalmodel/docs/domains/drilling/references/REF-ENG-DECOM-vol-1-a-study-for-the-bureau-of-safety-and-environmental-enforcement-bsee-final-9-10-2020.pdf` — 1

### claude top non-repo artifact reads
- none

### claude top Bash command families
- `ls` — 9769
- `grep` — 7414
- `uv run` — 6096
- `cat` — 5380
- `find` — 4106
- `gh` — 3492
- `bash` — 2998
- `git` — 1534

### claude recent activity since previous audit
- Post-hook records since prior audit: 5835
- Runtime sessions since prior audit: 86

### claude recent top tools
- `Bash` — 2792
- `unknown` — 1436
- `Read` — 944
- `Edit` — 326
- `Write` — 224

### claude recent top reads
- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` — 31
- `docs/DATA_RESIDENCE_POLICY.md` — 24
- `docs/plans/2026-05-13-issue-2685-citation-pilot-option-a-plan.md` — 23
- `data/document-index/mounted-source-registry.yaml` — 23
- `config/workstations/registry.yaml` — 20

### claude recent top writes
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-05-14-issue-2708-orcaflex-live-validation.md` — 3
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-05-14-issue-2710-solver-submit-ux.md` — 3
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-05-14-issue-2711-helix-provider-data-pilot.md` — 3
- `/mnt/local-analysis/workspace-hub-2703/.claude/skills/workspace-hub-learned/credential-scanner-safe-skill-authoring/SKILL.md` — 2
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-05-14-issue-2709-aqwa-runner-adapter.md` — 2

### claude recent top edits
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-05-12-issue-2675-ai-ecosystem-reverse-prompt-plan.md` — 34
- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` — 25
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-05-16-issue-2722-pre-commit-conflict-marker-hook.md` — 19
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-05-13-issue-2685-citation-pilot-option-a-plan.md` — 17
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-05-13-issue-2694-cathodic-protection-edition-merge-plan.md` — 17

### claude recent top Bash command families
- `ls` — 435
- `echo` — 420
- `gh` — 396
- `grep` — 263
- `cat` — 166
- `find` — 100
- `git add` — 88
- `git log` — 83

### claude recent top missing repo reads
- `scripts/review/results/2026-05-13-plan-2675-claude.md.err` — 1
- `scripts/review/results/2026-05-13-plan-2675-gemini.md.err` — 1
- `scripts/dispatch/overnight-2026-05-13/00-tonight-hermes-upgrade-2696.sh` — 1
- `scripts/review/results/2026-05-16-plan-2720-disagreement.md` — 1
- `scripts/review/results/2026-05-18-plan-2726-gemini.md.err` — 1

### claude recent top sibling-repo reads
- `digitalmodel/src/digitalmodel/geotechnical/on_bottom_stability.py` — 2
- `digitalmodel/src/digitalmodel/marine_ops/marine_engineering/mooring_analysis/catenary_solver_backup.py` — 1
- `digitalmodel/src/digitalmodel/marine_ops/marine_engineering/mooring_analysis/catenary_solver_v2.py` — 1
- `digitalmodel/src/digitalmodel/marine_ops/marine_engineering/mooring_analysis/catenary_solver_fixed.py` — 1

### claude recent top non-repo artifact reads
- none

### claude corpus change since previous audit
- Post-hook records: current 110989 vs previous 105154 (delta 5835)
- Sessions: current 61 vs previous 53 (delta 8)
- Missing repo reads: current 8609 vs previous 8824 (delta -215)
- Event-time post records since prior audit: 5835
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
- `digitalmodel/src/digitalmodel/geotechnical/on_bottom_stability.py` — 9
- `digitalmodel/specs/data-needs.yaml` — 7
- `digitalmodel/specs/module-registry.yaml` — 5
- `digitalmodel/src/digitalmodel/naval_architecture/curves.py` — 3
- `digitalmodel/docs/domains/openfoam/naval_architecture/propeller_hull_interaction.pdf` — 2
- `digitalmodel/docs/domains/ship-design/maneuvering_ship.pdf` — 2
- `worldenergydata/tests/test_resource_estimation.py` — 2
- `digitalmodel/docs/domains/hydrodynamics/literature/viviani-2007-four-quadrant-wageningen-b-series.pdf` — 2
- `digitalmodel/tests/fixtures/reporting/riser_lazy_wave_fpso.metadata.json` — 2
- `digitalmodel/docs/domains/drilling/references/REF-ENG-DECOM-vol-1-a-study-for-the-bureau-of-safety-and-environmental-enforcement-bsee-final-9-10-2020.pdf` — 1

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
- Sessions: 76
- Post-hook records: 40631
- Correction sessions: 0
- Unique runtime sessions: 1201
- Prompt-like reads: 39
- Blank read targets: 0
- Missing repo reads: 1206
- Bare python3 bash calls: 373
- `uv run ... python` bash calls: 830

### codex top tools
- `Bash` — 31307
- `Read` — 6424
- `Grep` — 1827
- `update_plan` — 417
- `list_mcp_resources` — 207
- `_add_comment_to_issue` — 117
- `_fetch_commit` — 24
- `_get_repo` — 23

### codex top repos
- `workspace-hub` — 40631

### codex top reads
- `docs/plans/README.md` — 248
- `docs/standards/HARD-STOP-POLICY.md` — 82
- `AGENTS.md` — 79
- `docs/plans/_template-issue-plan.md` — 76
- `docs/standards/CONTROL_PLANE_CONTRACT.md` — 54
- `config/scheduled-tasks/schedule-tasks.yaml` — 53
- `docs/standards/AI_REVIEW_ROUTING_POLICY.md` — 51
- `docs/ops/scheduled-tasks.md` — 49
- `README.md` — 42
- `.gitignore` — 40

### codex top symbolic reads
- `github://vamseeachanta/digitalmodel/issues/500` — 79
- `github://vamseeachanta/digitalmodel/issues/605` — 40
- `github://vamseeachanta/workspace-hub/issues/2488` — 32
- `github://vamseeachanta/digitalmodel/issues/606` — 31
- `github://vamseeachanta/digitalmodel/issues/611` — 27
- `github://vamseeachanta/workspace-hub/issues/2486` — 24
- `github://vamseeachanta/workspace-hub/issues/2510` — 20
- `github://vamseeachanta/digitalmodel/issues/609` — 20
- `github://vamseeachanta/workspace-hub/issues/2726` — 18
- `github://vamseeachanta/workspace-hub/issues/2511` — 17

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
- `sed` — 7463
- `rg` — 2920
- `nl` — 2754
- `find` — 1153
- `uv run` — 931
- `ls` — 812
- `git status` — 777
- `pwd` — 585

### codex recent activity since previous audit
- Post-hook records since prior audit: 8870
- Runtime sessions since prior audit: 224

### codex recent top tools
- `Bash` — 6664
- `Read` — 1773
- `Grep` — 357
- `_create_issue` — 14
- `_add_comment_to_issue` — 12

### codex recent top reads
- `github://vamseeachanta/digitalmodel/issues/500` — 79
- `docs/plans/README.md` — 55
- `github://vamseeachanta/digitalmodel/issues/605` — 40
- `github://vamseeachanta/digitalmodel/issues/606` — 31
- `github://vamseeachanta/digitalmodel/issues/611` — 27

### codex recent top writes
- none

### codex recent top edits
- none

### codex recent top Bash command families
- `sed` — 1558
- `nl` — 1313
- `rg` — 663
- `find` — 409
- `for` — 171
- `ls` — 158
- `uv run` — 140
- `git status` — 133

### codex recent top missing repo reads
- `src/digitalmodel/marine_ops/installation/jumper_installation.py` — 21
- `src/digitalmodel/marine_ops/installation/jumper_lift.py` — 21
- `src/digitalmodel/hydrodynamics/diffraction/input_schemas.py` — 15
- `src/digitalmodel/solvers/orcaflex/modular_generator/__init__.py` — 14
- `docs/domains/orcaflex/subsea/jumper/installation/ballymore_plet_plem/spec.yml` — 11

### codex recent top sibling-repo reads
- none

### codex recent top non-repo artifact reads
- none

### codex corpus change since previous audit
- Post-hook records: current 40631 vs previous 31761 (delta 8870)
- Sessions: current 76 vs previous 69 (delta 7)
- Missing repo reads: current 1206 vs previous 818 (delta 388)
- Event-time post records since prior audit: 8870
- Reconciliation gap vs event-time delta: 0
- Status: aligned
- Interpretation: Snapshot post-record change aligns with recent event-time activity.

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
- Sessions: 49
- Post-hook records: 271373
- Correction sessions: 47
- Unique runtime sessions: 4622
- Prompt-like reads: 1801
- Blank read targets: 112
- Missing repo reads: 1531
- Bare python3 bash calls: 2795
- `uv run ... python` bash calls: 4561

### hermes top tools
- `Bash` — 106820
- `Read` — 71553
- `Grep` — 36422
- `Write` — 26564
- `Edit` — 24884
- `Task` — 2850
- `Browser` — 1104
- `ToolSearch` — 478

### hermes top repos
- `workspace-hub` — 271373

### hermes top reads
- `/mnt/local-analysis/worktrees/workspace-hub-2720/scripts/readiness/telegram_hermes_readiness.py` — 1438
- `/mnt/local-analysis/worktrees/workspace-hub-2720/tests/readiness/test_telegram_hermes_readiness.py` — 1033
- `/mnt/local-analysis/worktrees/workspace-hub-2720/scripts/telegram_dispatch/policy.py` — 718
- `docs/plans/README.md` — 711
- `/mnt/local-analysis/worktrees/workspace-hub-2657/scripts/analysis/provider_session_ecosystem_audit.py` — 666
- `scripts/analysis/provider_session_ecosystem_audit.py` — 529
- `/mnt/local-analysis/worktrees/workspace-hub-2720/tests/telegram_dispatch/test_dispatch_policy.py` — 472
- `docs/plans/_template-issue-plan.md` — 409
- `/mnt/local-analysis/llm-wiki/scripts/llm_wiki_rag_benchmark.py` — 398
- `tests/analysis/test_provider_session_ecosystem_audit.py` — 350

### hermes top symbolic reads
- `github/github-issues` — 1887
- `software-development/gh-work-execution` — 1170
- `coordination/gh-work-planning` — 1034
- `coordination/issue-planning-mode` — 902
- `hermes-agent` — 774
- `research/llm-wiki` — 680
- `software-development/test-driven-development` — 622
- `development/artifact-commit-verification` — 545
- `operations/telegram-hermes-bot` — 527
- `github-issues` — 482

### hermes top sibling-repo reads
- `worldenergydata/scripts/marketing/generate_hurricane_mooring_risk_infographic.py` — 63
- `worldenergydata/reports/modules/marketing/hurricane_mooring_safety_infographic_stats.json` — 62
- `digitalmodel/examples/demos/gtm/data/ctv_operability_kincardine.json` — 29
- `digitalmodel/specs/module-registry.yaml` — 13
- `digitalmodel/docs/plans/README.md` — 13
- `worldenergydata/tests/modules/marketing/test_hurricane_mooring_risk_infographic.py` — 13
- `digitalmodel/docs/plans/_template-issue-plan.md` — 10
- `digitalmodel/docs/roadmaps/orcawave-orcaflex-capability-roadmap.md` — 7
- `digitalmodel/docs/assessments/hull-library-audit.md` — 7
- `worldenergydata/.planning/quick/gemini-review.txt` — 6

### hermes top non-repo artifact reads
- none

### hermes top Bash command families
- `gh` — 18244
- `uv run` — 9082
- `set` — 7797
- `git status` — 5673
- `git diff` — 3094
- `bash` — 2756
- `git add` — 2630
- `git` — 2186

### hermes recent activity since previous audit
- Post-hook records since prior audit: 69268
- Runtime sessions since prior audit: 1330

### hermes recent top tools
- `Read` — 27427
- `Bash` — 21953
- `Edit` — 8158
- `Grep` — 7439
- `Write` — 2888

### hermes recent top reads
- `/mnt/local-analysis/worktrees/workspace-hub-2720/scripts/readiness/telegram_hermes_readiness.py` — 1438
- `github/github-issues` — 1183
- `/mnt/local-analysis/worktrees/workspace-hub-2720/tests/readiness/test_telegram_hermes_readiness.py` — 1033
- `software-development/gh-work-execution` — 765
- `/mnt/local-analysis/worktrees/workspace-hub-2720/scripts/telegram_dispatch/policy.py` — 718

### hermes recent top writes
- `/mnt/local-analysis/llm-wiki/tests/test_llm_wiki_rag_benchmark.py` — 218
- `/mnt/local-analysis/llm-wiki/tests/test_rag_benchmark_artifacts.py` — 150
- `/tmp/issue-2720-code-review-diff.patch` — 112
- `/tmp/issue-78-start.md` — 92
- `/mnt/local-analysis/llm-wiki/scripts/llm_wiki_rag_benchmark.py` — 86

### hermes recent top edits
- `/mnt/local-analysis/llm-wiki/scripts/llm_wiki_rag_benchmark.py` — 1250
- `/mnt/local-analysis/worktrees/workspace-hub-2720/tests/readiness/test_telegram_hermes_readiness.py` — 986
- `/mnt/local-analysis/worktrees/workspace-hub-2720/scripts/readiness/telegram_hermes_readiness.py` — 798
- `/mnt/local-analysis/worktrees/workspace-hub-2720/tests/telegram_dispatch/test_dispatch_policy.py` — 490
- `/mnt/local-analysis/worktrees/workspace-hub-2720/scripts/telegram_dispatch/policy.py` — 422

### hermes recent top Bash command families
- `uv run` — 3780
- `set` — 2967
- `git status` — 1993
- `gh` — 1879
- `git diff` — 1592
- `python` — 485
- `scripts/legal/legal-sanity-scan.sh` — 479
- `git` — 443

### hermes recent top missing repo reads
- `scripts/review/results/2026-05-16-plan-2720-codex.md` — 40
- `scripts/review/results/2026-05-16-plan-2720-gemini.md` — 40
- `scripts/review/results/2026-05-16-plan-2720-claude.md` — 36
- `scripts/review/results/2026-05-16-plan-2720-disagreement.md` — 34
- `.planning/quick/review-2720-r4-claude.out` — 12

### hermes recent top sibling-repo reads
- `worldenergydata/scripts/marketing/generate_hurricane_mooring_risk_infographic.py` — 63
- `worldenergydata/reports/modules/marketing/hurricane_mooring_safety_infographic_stats.json` — 62
- `digitalmodel/examples/demos/gtm/data/ctv_operability_kincardine.json` — 27
- `worldenergydata/tests/modules/marketing/test_hurricane_mooring_risk_infographic.py` — 13
- `digitalmodel/docs/plans/_template-issue-plan.md` — 8

### hermes recent top non-repo artifact reads
- none

### hermes corpus change since previous audit
- Post-hook records: current 271373 vs previous 200061 (delta 71312)
- Sessions: current 49 vs previous 42 (delta 7)
- Missing repo reads: current 1531 vs previous 1284 (delta 247)
- Event-time post records since prior audit: 69268
- Reconciliation gap vs event-time delta: 2044
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
- `knowledge/wikis/marine-engineering/wiki/index.md` — 28
- `knowledge/wikis/engineering/wiki/workflows/orcawave-to-orcaflex-pipeline.md` — 25
- `client_projects/engineering_workbooks/ballymore/jumper_manifold_to_plet/jumper_lift.py` — 24

### hermes top sibling-repo reads
- `worldenergydata/scripts/marketing/generate_hurricane_mooring_risk_infographic.py` — 63
- `worldenergydata/reports/modules/marketing/hurricane_mooring_safety_infographic_stats.json` — 62
- `digitalmodel/examples/demos/gtm/data/ctv_operability_kincardine.json` — 29
- `digitalmodel/specs/module-registry.yaml` — 13
- `digitalmodel/docs/plans/README.md` — 13
- `worldenergydata/tests/modules/marketing/test_hurricane_mooring_risk_infographic.py` — 13
- `digitalmodel/docs/plans/_template-issue-plan.md` — 10
- `digitalmodel/docs/roadmaps/orcawave-orcaflex-capability-roadmap.md` — 7
- `digitalmodel/docs/assessments/hull-library-audit.md` — 7
- `worldenergydata/.planning/quick/gemini-review.txt` — 6

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
- `/mnt/local-analysis/worktrees/workspace-hub-2720/tests/telegram_dispatch/test_dispatch_policy.py` — 472
- `/mnt/local-analysis/worktrees/workspace-hub-2720/config/workstations/registry.yaml` — 270
- `/mnt/local-analysis/worktrees/workspace-hub-2720/scripts/telegram_dispatch/redaction.py` — 258
- `/mnt/local-analysis/llm-wiki/docs/reports/2026-05-16-rag-benchmark-scorecard.md` — 210
- `/mnt/local-analysis/worktrees/workspace-hub-2720/tests/telegram_dispatch/test_redaction.py` — 204
- `/mnt/local-analysis/worktrees/workspace-hub-2720/.planning/quick/review-2720-implementation-current.md` — 150
- `/mnt/local-analysis/worktrees/workspace-hub-2720/scripts/legal/legal-sanity-scan.sh` — 132

## gemini
- Source: raw_logs
- Sessions: 69
- Post-hook records: 6198
- Correction sessions: 0
- Unique runtime sessions: 353
- Prompt-like reads: 18
- Blank read targets: 0
- Missing repo reads: 602
- Bare python3 bash calls: 291
- `uv run ... python` bash calls: 39

### gemini top tools
- `Bash` — 2288
- `Read` — 2181
- `Grep` — 655
- `Write` — 535
- `Edit` — 394
- `Browser` — 131
- `ToolSearch` — 9
- `generalist` — 3

### gemini top repos
- `workspace-hub` — 6198

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
- Post-hook records since prior audit: 8
- Runtime sessions since prior audit: 6

### gemini recent top tools
- `Browser` — 8

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
- Post-hook records: current 6198 vs previous 6189 (delta 9)
- Sessions: current 69 vs previous 62 (delta 7)
- Missing repo reads: current 602 vs previous 604 (delta -2)
- Event-time post records since prior audit: 8
- Reconciliation gap vs event-time delta: 1
- Status: positive_corpus_growth_beyond_recent_activity
- Interpretation: Snapshot grew more than recent event-time activity, suggesting backfill or expanded export coverage.

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

