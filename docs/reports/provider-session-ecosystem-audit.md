# Provider session ecosystem audit — 2026-07-13

Scope: provider session artifacts rooted at `/mnt/local-analysis/workspace-hub/logs/orchestrator` with saved provider artifacts used only as fallback when raw logs are unavailable.

## Executive summary
- `claude` — source=raw_logs | sessions=94 | post_records=122229 | python3/1k=9.16 | uv-python/1k=51.13
- `codex` — source=raw_logs | sessions=126 | post_records=188117 | python3/1k=14.99 | uv-python/1k=20.4
- `hermes` — source=raw_logs | sessions=50 | post_records=7829811 | python3/1k=9.55 | uv-python/1k=18.72
- `gemini` — source=raw_logs | sessions=78 | post_records=6210 | python3/1k=46.86 | uv-python/1k=6.28

- Migration debt density (known stale reads with redirect hints per 1k records): `claude` 14.1, `gemini` 13.85, `hermes` 0.41, `codex` 0.05.
- Highest-volume known migration debt: `hermes` with 3213 mapped stale reads across 2 rule clusters; top hotspot: `session_local_worktree_path_drift` (1809).
- Highest-density known migration debt: `claude` with 1724 mapped stale reads; top hotspot: `legacy_work_queue_transition` (1004, 58.24% of known debt).
- Scope note: Migration-debt figures are based on remediation-mapped entries from each provider's top missing repo reads.

## Provider interpretation summary
- Focus this week: prioritize legacy-path redirect cleanup and prompt/doc updates on claude (urgency 80.0, issue: legacy_work_queue_transition), then address gemini (urgency 47.72, issue: legacy_local_work_queue_items).
- Recommended actions:
  - `claude` [urgent_now] — prioritize legacy-path redirect cleanup and prompt/doc updates (urgency 80.0, issue: legacy_work_queue_transition; health=red; movement: rank unchanged at #1; urgency 80.00 (-8.00 vs previous audit); migration debt improved; path drift improved)
  - `gemini` [next_up] — prioritize legacy-path redirect cleanup and prompt/doc updates (urgency 47.72, issue: legacy_local_work_queue_items; health=red; movement: rank unchanged at #2; urgency 47.72 (+0.00 vs previous audit))
  - `hermes` [investigate] — prioritize legacy-path redirect cleanup and prompt/doc updates (urgency 32.23, issue: session_local_worktree_path_drift; health=yellow; movement: rank unchanged at #3; urgency 32.23 (+0.00 vs previous audit); corpus grew faster than event-time activity)
  - `codex` [investigate] — prioritize legacy-path redirect cleanup and prompt/doc updates (urgency 31.35, issue: llm_wiki_spinout_path_drift; health=yellow; movement: rank unchanged at #4; urgency 31.35 (+7.97 vs previous audit); path drift improved; corpus grew faster than event-time activity)
- Health overview:
  - `claude` [red] — red: urgent action tier; high migration debt; 7d sustained activity; currently active
  - `gemini` [red] — red: high migration debt; python3-heavy command hygiene
  - `hermes` [yellow] — yellow: moderate migration debt; corpus anomaly needs interpretation
  - `codex` [yellow] — yellow: moderate migration debt; corpus anomaly needs interpretation; 7d sustained activity; currently active
- Watchlist triggers:
  - `claude` [page] — urgent-now provider with legacy_work_queue_transition | follow-up: Escalate immediately on claude: prioritize legacy-path redirect cleanup and prompt/doc updates
  - `gemini` [act_this_week] — red health due to legacy_local_work_queue_items | follow-up: Prioritize this week on gemini: prioritize legacy-path redirect cleanup and prompt/doc updates
  - `codex` [investigate] — yellow health with sustained 7d activity and llm_wiki_spinout_path_drift; corpus anomaly present | follow-up: Sample current traces on codex and verify whether llm_wiki_spinout_path_drift needs remap or docs cleanup
  - `hermes` [monitor] — yellow: moderate migration debt; corpus anomaly needs interpretation; corpus anomaly present | follow-up: Monitor hermes in the next audit cycle
- Change alerts:
  - `hermes` [cleared_watchlist] — hermes cleared watchlist from monitor | follow-up: Monitor hermes in the next audit cycle
- Remediation playbooks:
  - `claude` [page] — issue=legacy_work_queue_transition | lane=governance-docs | owner=governance-maintainers | owner_surface=docs/governance/SESSION-GOVERNANCE.md | inspect=scripts/work-queue/verify-gate-evidence.py, scripts/work-queue/exit_stage.py, scripts/work-queue/start_stage.py | targets=docs/governance/SESSION-GOVERNANCE.md, docs/governance/TRUST-ARCHITECTURE.md, scripts/workflow/governance-checkpoints.yaml | steps: Inspect the top matched stale paths for legacy_work_queue_transition and confirm they should redirect rather than be recreated. | Open the canonical targets and migrate prompts/docs/tooling toward: docs/governance/SESSION-GOVERNANCE.md, docs/governance/TRUST-ARCHITECTURE.md, scripts/workflow/governance-checkpoints.yaml.
  - `gemini` [act_this_week] — issue=legacy_local_work_queue_items | lane=planning-workflow | owner=planning-ops | owner_surface=notes/agent-work-queue.md | inspect=.claude/work-queue/WRK-149.md, .claude/work-queue/working, .claude/work-queue/working/ | targets=GitHub issues, .planning/, notes/agent-work-queue.md | steps: Inspect the top matched stale paths for legacy_local_work_queue_items and confirm they should redirect rather than be recreated. | Open the canonical targets and migrate prompts/docs/tooling toward: GitHub issues, .planning/, notes/agent-work-queue.md.
  - `hermes` [monitor] — issue=session_local_worktree_path_drift | lane=monitoring | owner=audit-operators | owner_surface=docs/reports/provider-session-ecosystem-audit.md | inspect=.claude/worktrees/ecosystem-sync/docs/plans/2026-04-20-aceengineer-ecosystem-sync-plan.md | targets=main repo branch/worktree, docs/plans/, .planning/ | steps: Inspect the top matched stale paths for session_local_worktree_path_drift and confirm they should redirect rather than be recreated. | Open the canonical targets and migrate prompts/docs/tooling toward: main repo branch/worktree, docs/plans/, .planning/.
  - `codex` [investigate] — issue=llm_wiki_spinout_path_drift | lane=monitoring | owner=audit-operators | owner_surface=docs/reports/provider-session-ecosystem-audit.md | inspect=knowledge/wikis/engineering/CLAUDE.md | targets=llm-wiki/wikis/, llm-wiki/docs/, docs/session-handoffs/2026-05-05-llm-wiki-spinout-max-completeness-handoff.md | steps: Inspect the top matched stale paths for llm_wiki_spinout_path_drift and confirm they should redirect rather than be recreated. | Open the canonical targets and migrate prompts/docs/tooling toward: llm-wiki/wikis/, llm-wiki/docs/, docs/session-handoffs/2026-05-05-llm-wiki-spinout-max-completeness-handoff.md.
- Follow-up issue drafts:
  - `claude` [critical] — [critical] claude: remediate legacy_work_queue_transition | state=unchanged | owner=governance-maintainers | lane=governance-docs
  - `gemini` [high] — [high] gemini: remediate legacy_local_work_queue_items | state=unchanged | owner=planning-ops | lane=planning-workflow
  - `codex` [medium] — [medium] codex: remediate llm_wiki_spinout_path_drift | state=unchanged | owner=audit-operators | lane=monitoring
- Issue posting readiness:
  - `claude` [ready] — should_open_issue=no | final_should_open=yes | evidence=complete | linked_issue=none | matched_on=none | reason=unchanged draft has no linked issue; safe to open once
  - `gemini` [ready] — should_open_issue=no | final_should_open=yes | evidence=complete | linked_issue=none | matched_on=none | reason=unchanged draft has no linked issue; safe to open once
  - `codex` [ready] — should_open_issue=no | final_should_open=yes | evidence=complete | linked_issue=none | matched_on=none | reason=unchanged draft has no linked issue; safe to open once
- `claude` — rank=1 (prev=1, move=stable) | health=red | profile=sustained_background | 24h=1 posts/1 sessions | 7d=1780 posts/16 sessions | urgency=80.0 | tier=urgent_now | activity=active (stable) | corpus=aligned | debt=high_debt (improving) | drift=improving | python=uv_preferred (stable) | health summary: red: urgent action tier; high migration debt; 7d sustained activity; currently active | movement: rank unchanged at #1; urgency 80.00 (-8.00 vs previous audit); migration debt improved; path drift improved | primary issue: legacy_work_queue_transition | action: prioritize legacy-path redirect cleanup and prompt/doc updates
- `gemini` — rank=2 (prev=2, move=stable) | health=red | profile=dormant | 24h=0 posts/0 sessions | 7d=0 posts/0 sessions | urgency=47.72 | tier=next_up | activity=idle (stable) | corpus=aligned | debt=high_debt (stable) | drift=stable | python=python3_heavy (stable) | health summary: red: high migration debt; python3-heavy command hygiene | movement: rank unchanged at #2; urgency 47.72 (+0.00 vs previous audit) | primary issue: legacy_local_work_queue_items | action: prioritize legacy-path redirect cleanup and prompt/doc updates
- `hermes` — rank=3 (prev=3, move=stable) | health=yellow | profile=dormant | 24h=0 posts/0 sessions | 7d=0 posts/0 sessions | urgency=32.23 | tier=investigate | activity=idle (stable) | corpus=positive_corpus_growth_beyond_recent_activity | debt=moderate_debt (stable) | drift=stable | python=mixed (stable) | health summary: yellow: moderate migration debt; corpus anomaly needs interpretation | movement: rank unchanged at #3; urgency 32.23 (+0.00 vs previous audit); corpus grew faster than event-time activity | primary issue: session_local_worktree_path_drift | action: prioritize legacy-path redirect cleanup and prompt/doc updates
- `codex` — rank=4 (prev=4, move=stable) | health=yellow | profile=sustained_background | 24h=153 posts/8 sessions | 7d=22592 posts/286 sessions | urgency=31.35 | tier=investigate | activity=active (stable) | corpus=positive_corpus_growth_beyond_recent_activity | debt=moderate_debt (stable) | drift=improving | python=mixed (stable) | health summary: yellow: moderate migration debt; corpus anomaly needs interpretation; 7d sustained activity; currently active | movement: rank unchanged at #4; urgency 31.35 (+7.97 vs previous audit); path drift improved; corpus grew faster than event-time activity | primary issue: llm_wiki_spinout_path_drift | action: prioritize legacy-path redirect cleanup and prompt/doc updates

## Recent activity since previous audit
- Previous audit timestamp: `2026-07-06T09:15:03Z`
- Recent post-audit activity: `codex` 22595 post records / 286 sessions, `claude` 1780 post records / 16 sessions.
- Scope note: This is event-time activity since the previous audit timestamp, not a census of newly exported historical/backfilled records.

## Rolling activity windows
- `last_24h` — `2026-07-12T09:15:04Z` → `2026-07-13T09:15:04Z`
  - Scope note: Last 24 hours of event-time activity ending at this audit timestamp.
  - Activity leaders: `codex` 153 post records / 8 sessions, `claude` 1 post records / 1 sessions.
- `last_7d` — `2026-07-06T09:15:04Z` → `2026-07-13T09:15:04Z`
  - Scope note: Last 7 days of event-time activity ending at this audit timestamp.
  - Activity leaders: `codex` 22592 post records / 286 sessions, `claude` 1780 post records / 16 sessions.

## Corpus change since previous audit
- Previous audit timestamp: `2026-07-06T09:15:03Z`
- Scope note: Snapshot-to-snapshot corpus deltas reflect export additions/removals/reclassification and should be interpreted separately from event-time recent activity.
- Largest negative reconciliation gap: `claude`
- Largest positive reconciliation gap: `hermes`

## claude
- Source: raw_logs
- Sessions: 94
- Post-hook records: 122229
- Correction sessions: 0
- Unique runtime sessions: 851
- Prompt-like reads: 292
- Blank read targets: 0
- Missing repo reads: 9463
- Bare python3 bash calls: 1120
- `uv run ... python` bash calls: 6249

### claude top tools
- `Bash` — 65334
- `Read` — 21565
- `Edit` — 9704
- `unknown` — 8847
- `Write` — 8497
- `Grep` — 2613
- `Agent` — 1420
- `ToolSearch` — 681

### claude top repos
- `workspace-hub` — 115651
- `digitalmodel` — 1900
- `assetutilities` — 535
- `wt-2893-statusline-plan` — 482
- `issue-2981-skill-frontmatter-yaml-valid` — 212
- `worldenergydata` — 201
- `workspace-hub-2510-plan` — 196
- `wt-drive-mounts` — 187

### claude top reads
- `scripts/work-queue/verify-gate-evidence.py` — 732
- `scripts/work-queue/generate-html-review.py` — 249
- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` — 231
- `docs/plans/README.md` — 198
- `docs/plans/_template-issue-plan.md` — 173
- `scripts/work-queue/exit_stage.py` — 137
- `scripts/work-queue/start_stage.py` — 135
- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` — 120
- `scripts/work-queue/close-item.sh` — 94
- `.claude/skills/coordination/issue-planning-mode/SKILL.md` — 76

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
- `ls` — 10161
- `grep` — 7766
- `uv run` — 6169
- `cat` — 5508
- `find` — 4195
- `gh` — 3761
- `bash` — 3051
- `echo` — 1956

### claude recent activity since previous audit
- Post-hook records since prior audit: 1780
- Runtime sessions since prior audit: 16

### claude recent top tools
- `unknown` — 750
- `Bash` — 710
- `Edit` — 131
- `Read` — 128
- `Write` — 47

### claude recent top reads
- `docs/plans/2026-07-09-issue-3403-voice-dictation-vnc-contract.md` — 9
- `/mnt/local-analysis/wt-wed-kc-ingest/docs/modules/bsee/analysis/production/FDAS_V30/extract_drilling_completion_days.py` — 7
- `/mnt/local-analysis/wt-wed-wo-rename/scripts/refresh_bsee_all.py` — 5
- `/mnt/local-analysis/wt-wed-wo-rename/reports/lower_tertiary/wo-april-2026-validation.md` — 4
- `/mnt/local-analysis/wt-wed-wo-rename/packages/worldenergydata-bsee/src/worldenergydata/bsee/data/refresh/url_registry.py` — 3

### claude recent top writes
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-07-06-issue-wed-848-phase-norm-layer.md` — 2
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-07-06-issue-wed-849-per-well-economics.md` — 2
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-07-06-issue-wed-850-nav-spine.md` — 2
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-07-06-issue-dm-1444-capabilities-ia-spec.md` — 2
- `/mnt/local-analysis/wt-wed-kc-ingest/tests/integration/test_kc_ingest_fidelity.py` — 1

### claude recent top edits
- `/mnt/local-analysis/wt-wed-wo-rename/docs/plans/2026-07-06-issue-847-boem-reserves-discovery-ingest.md` — 12
- `/mnt/local-analysis/wt-wed-wo-rename/reports/lower_tertiary/wo-april-2026-validation.md` — 9
- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/project_wed_field_hub_ia_epic.md` — 7
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-07-06-issue-dm-1456-section-onepager-gaps.md` — 7
- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/project_dm_capabilities_page_expansion.md` — 6

### claude recent top Bash command families
- `grep` — 79
- `git show` — 73
- `echo` — 60
- `sed` — 58
- `gh` — 47
- `ls` — 45
- `/mnt/local-analysis/worldenergydata/.venv/bin/python` — 33
- `git` — 23

### claude recent top missing repo reads
- none

### claude recent top sibling-repo reads
- none

### claude recent top non-repo artifact reads
- none

### claude corpus change since previous audit
- Post-hook records: current 122229 vs previous 120449 (delta 1780)
- Sessions: current 94 vs previous 89 (delta 5)
- Missing repo reads: current 9463 vs previous 9448 (delta 15)
- Event-time post records since prior audit: 1780
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
- Sessions: 126
- Post-hook records: 188117
- Correction sessions: 0
- Unique runtime sessions: 2959
- Prompt-like reads: 40
- Blank read targets: 0
- Missing repo reads: 1689
- Bare python3 bash calls: 2819
- `uv run ... python` bash calls: 3838

### codex top tools
- `Bash` — 165419
- `Read` — 7376
- `wait` — 4823
- `wait_agent` — 2404
- `Grep` — 2036
- `spawn_agent` — 1157
- `update_plan` — 1058
- `close_agent` — 837

### codex top repos
- `workspace-hub` — 188117

### codex top reads
- `docs/plans/README.md` — 274
- `docs/plans/_template-issue-plan.md` — 92
- `docs/standards/HARD-STOP-POLICY.md` — 84
- `AGENTS.md` — 80
- `config/scheduled-tasks/schedule-tasks.yaml` — 69
- `docs/standards/CONTROL_PLANE_CONTRACT.md` — 62
- `docs/ops/scheduled-tasks.md` — 49
- `docs/standards/AI_REVIEW_ROUTING_POLICY.md` — 48
- `config/workstations/registry.yaml` — 43
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
- `sed` — 25023
- `nl` — 14207
- `rg` — 11110
- `find` — 9409
- `gh` — 8772
- `git status` — 7734
- `git diff` — 7167
- `git` — 6380

### codex recent activity since previous audit
- Post-hook records since prior audit: 22595
- Runtime sessions since prior audit: 286

### codex recent top tools
- `Bash` — 14935
- `wait` — 4823
- `wait_agent` — 1440
- `send_message` — 488
- `followup_task` — 250

### codex recent top reads
- none

### codex recent top writes
- none

### codex recent top edits
- none

### codex recent top Bash command families
- `sed` — 1782
- `nl` — 1228
- `gh` — 933
- `find` — 851
- `git status` — 801
- `rg` — 735
- `git diff` — 724
- `git` — 708

### codex recent top missing repo reads
- none

### codex recent top sibling-repo reads
- none

### codex recent top non-repo artifact reads
- none

### codex corpus change since previous audit
- Post-hook records: current 188117 vs previous 164514 (delta 23603)
- Sessions: current 126 vs previous 119 (delta 7)
- Missing repo reads: current 1689 vs previous 1690 (delta -1)
- Event-time post records since prior audit: 22595
- Reconciliation gap vs event-time delta: 1008
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
- `scripts/review/results/2026-04-25-plan-2488-codex.md` — 10
- `scripts/review/results/20260425T125029Z-plan-2488-codex.md` — 10
- `src/digitalmodel/solvers/orcaflex/modular_generator/schema/root.py` — 10

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

### codex top missing external reads
- none

## hermes
- Source: raw_logs
- Sessions: 50
- Post-hook records: 7829811
- Correction sessions: 49
- Unique runtime sessions: 5935
- Prompt-like reads: 37125
- Blank read targets: 10584
- Missing repo reads: 138726
- Bare python3 bash calls: 74736
- `uv run ... python` bash calls: 146556

### hermes top tools
- `Bash` — 3057885
- `Read` — 2167722
- `Grep` — 1053567
- `Write` — 748143
- `Edit` — 610605
- `Task` — 78111
- `Browser` — 65151
- `browser_console` — 21600

### hermes top repos
- `workspace-hub` — 7829811

### hermes top reads
- `/mnt/local-analysis/digitalmodel/src/digitalmodel/naval_architecture/b1528_sirocco_current_heading_rudder_report.py` — 32886
- `docs/plans/README.md` — 24273
- `/mnt/local-analysis/worktrees/workspace-hub-2720/scripts/readiness/telegram_hermes_readiness.py` — 19575
- `/mnt/local-analysis/worktrees/workspace-hub-2657/scripts/analysis/provider_session_ecosystem_audit.py` — 17982
- `scripts/analysis/provider_session_ecosystem_audit.py` — 14310
- `/mnt/local-analysis/worktrees/workspace-hub-2720/tests/readiness/test_telegram_hermes_readiness.py` — 14067
- `/mnt/local-analysis/digitalmodel/tests/naval_architecture/test_b1528_sirocco_current_heading_rudder.py` — 13986
- `docs/plans/_template-issue-plan.md` — 13932
- `/mnt/local-analysis/llm-wiki/scripts/generate_public_graph_manifests.py` — 12123
- `/mnt/local-analysis/digitalmodel/src/digitalmodel/naval_architecture/data/b1528_sirocco_current_heading_rudder.yml` — 11178

### hermes top symbolic reads
- `github/github-issues` — 60129
- `coordination/issue-planning-mode` — 46926
- `software-development/gh-work-execution` — 44172
- `github-issues` — 32778
- `coordination/gh-work-planning` — 30483
- `workspace-hub/worktree-branch-sync-hygiene` — 23571
- `hermes-agent` — 21762
- `software-development/test-driven-development` — 21303
- `research/llm-wiki` — 19089
- `development/artifact-commit-verification` — 18009

### hermes top sibling-repo reads
- `worldenergydata/scripts/marketing/generate_hurricane_mooring_risk_infographic.py` — 1701
- `worldenergydata/scripts/maintenance/verify_repo_structure.py` — 1674
- `worldenergydata/reports/modules/marketing/hurricane_mooring_safety_infographic_stats.json` — 1674
- `worldenergydata/.github/workflows/ci.yml` — 1620
- `digitalmodel/examples/demos/gtm/tests/test_ctv_operability_reference.py` — 1566
- `digitalmodel/examples/demos/gtm/demo_02_wall_thickness_multicode.py` — 1539
- `worldenergydata/data/modules/marine_safety/input/fatality_incidents.csv` — 1539
- `worldenergydata/data/modules/marine_safety/input/foundering_incidents.csv` — 1539
- `worldenergydata/data/modules/marine_safety/input/hatch_incidents.csv` — 1539
- `worldenergydata/docs/plans/2026-05-12-issue-403-hurricane-mooring-risk-infographic.md` — 1512

### hermes top non-repo artifact reads
- none

### hermes top Bash command families
- `gh` — 517374
- `set` — 255771
- `uv run` — 255447
- `git status` — 172206
- `git diff` — 91449
- `bash` — 78921
- `python` — 72333
- `git add` — 71334

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
- Post-hook records: current 7829811 vs previous 6089853 (delta 1739958)
- Sessions: current 50 vs previous 50 (delta 0)
- Missing repo reads: current 138726 vs previous 107898 (delta 30828)
- Event-time post records since prior audit: 0
- Reconciliation gap vs event-time delta: 1739958
- Status: positive_corpus_growth_beyond_recent_activity
- Interpretation: Snapshot grew more than recent event-time activity, suggesting backfill or expanded export coverage.

### hermes top missing repo reads
- `docs/plans/2026-05-20-issue-2760-b1528-sirocco-force-review-revision.md` — 6615
- `scripts/review/results/2026-05-20-plan-2766-claude.md` — 2079
- `scripts/review/results/2026-05-20-plan-2766-codex.md` — 2079
- `scripts/review/results/2026-05-20-plan-2766-disagreement.md` — 2079
- `.claude/worktrees/ecosystem-sync/docs/plans/2026-04-20-aceengineer-ecosystem-sync-plan.md` — 1809
- `scripts/review/results/2026-04-22-plan-2332-codex.md` — 1728
- `scripts/review/results/2026-04-25-plan-2488-codex.md` — 1701
- `scripts/review/results/2026-04-22-plan-2332-gemini.md` — 1512
- `knowledge/wikis/engineering/wiki/index.md` — 1404
- `scripts/review/results/2026-05-20-plan-2754-codex-r2.md` — 1242

### hermes top sibling-repo reads
- `worldenergydata/scripts/marketing/generate_hurricane_mooring_risk_infographic.py` — 1701
- `worldenergydata/scripts/maintenance/verify_repo_structure.py` — 1674
- `worldenergydata/reports/modules/marketing/hurricane_mooring_safety_infographic_stats.json` — 1674
- `worldenergydata/.github/workflows/ci.yml` — 1620
- `digitalmodel/examples/demos/gtm/tests/test_ctv_operability_reference.py` — 1566
- `digitalmodel/examples/demos/gtm/demo_02_wall_thickness_multicode.py` — 1539
- `worldenergydata/data/modules/marine_safety/input/fatality_incidents.csv` — 1539
- `worldenergydata/data/modules/marine_safety/input/foundering_incidents.csv` — 1539
- `worldenergydata/data/modules/marine_safety/input/hatch_incidents.csv` — 1539
- `worldenergydata/docs/plans/2026-05-12-issue-403-hurricane-mooring-risk-infographic.md` — 1512

### hermes top non-repo artifact reads
- none

### hermes remediation hints for stale repo reads
- `.claude/worktrees/ecosystem-sync/docs/plans/2026-04-20-aceengineer-ecosystem-sync-plan.md` (1809) — 1809 combined reads
  - Redirect to: `main repo branch/worktree`, `docs/plans/`, `.planning/`, `GitHub issues`
  - Guidance: Provider logs sometimes retain ephemeral worktree or temp paths; treat these as session-local and re-resolve the durable artifact from the main repo, .planning, or GitHub issue evidence before acting.
  - Reference: `docs/ops/legacy-claude-reference-map.md`
- `knowledge/wikis/engineering/wiki/index.md` (1404) — 1404 combined reads
  - Redirect to: `llm-wiki/wikis/`, `llm-wiki/docs/`, `docs/session-handoffs/2026-05-05-llm-wiki-spinout-max-completeness-handoff.md`, `docs/sessions/2026-05-07-nest-llm-wiki-kaggle-into-hub.md`
  - Guidance: The LLM-wiki artifact store moved out of workspace-hub/knowledge into the llm-wiki repository; redirect wiki-content reads to llm-wiki and keep control-plane work in workspace-hub.
  - Reference: `docs/ops/legacy-claude-reference-map.md`

### hermes top missing external reads
- `/mnt/local-analysis/worktrees/workspace-hub-2720/scripts/readiness/telegram_hermes_readiness.py` — 19575
- `/mnt/local-analysis/worktrees/workspace-hub-2657/scripts/analysis/provider_session_ecosystem_audit.py` — 17982
- `/mnt/local-analysis/worktrees/workspace-hub-2720/tests/readiness/test_telegram_hermes_readiness.py` — 14067
- `/mnt/local-analysis/worktrees/workspace-hub-2720/scripts/telegram_dispatch/policy.py` — 9693
- `/mnt/local-analysis/worktrees/workspace-hub-2720/tests/telegram_dispatch/test_dispatch_policy.py` — 6372
- `/mnt/local-analysis/worktrees/workspace-hub-2657/tests/analysis/test_provider_session_ecosystem_audit.py` — 6210
- `/mnt/local-analysis/worktrees/workspace-hub-2720/config/workstations/registry.yaml` — 3645
- `/mnt/local-analysis/worktrees/workspace-hub-2720/scripts/telegram_dispatch/redaction.py` — 3510
- `/mnt/local-analysis/agent-worktrees/workspace-hub-issue-2766-ace-linux-1-normalization/scripts/readiness/telegram_hermes_readiness.py` — 3267
- `/mnt/local-analysis/llm-wiki/docs/reports/2026-05-16-rag-benchmark-scorecard.md` — 2835

## gemini
- Source: raw_logs
- Sessions: 78
- Post-hook records: 6210
- Correction sessions: 0
- Unique runtime sessions: 362
- Prompt-like reads: 18
- Blank read targets: 0
- Missing repo reads: 615
- Bare python3 bash calls: 291
- `uv run ... python` bash calls: 39

### gemini top tools
- `Bash` — 2288
- `Read` — 2181
- `Grep` — 655
- `Write` — 535
- `Edit` — 394
- `Browser` — 143
- `ToolSearch` — 9
- `generalist` — 3

### gemini top repos
- `workspace-hub` — 6210

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
- Post-hook records: current 6210 vs previous 6210 (delta 0)
- Sessions: current 78 vs previous 78 (delta 0)
- Missing repo reads: current 615 vs previous 615 (delta 0)
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

