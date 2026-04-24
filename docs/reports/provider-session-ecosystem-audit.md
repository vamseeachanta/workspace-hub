# Provider session ecosystem audit — 2026-04-24

Scope: provider session artifacts rooted at `/mnt/local-analysis/workspace-hub/logs/orchestrator` with saved provider artifacts used only as fallback when raw logs are unavailable.

## Executive summary
- `claude` — source=raw_logs | sessions=37 | post_records=89063 | python3/1k=8.53 | uv-python/1k=67.5
- `codex` — source=raw_logs | sessions=53 | post_records=20144 | python3/1k=17.92 | uv-python/1k=21.25
- `hermes` — source=raw_logs | sessions=22 | post_records=160131 | python3/1k=16.76 | uv-python/1k=14.05
- `gemini` — source=raw_logs | sessions=48 | post_records=6173 | python3/1k=47.14 | uv-python/1k=6.32

- Migration debt density (known stale reads with redirect hints per 1k records): `claude` 19.53, `gemini` 13.93, `codex` 0.0, `hermes` 0.0.
- Highest-volume known migration debt: `claude` with 1739 mapped stale reads across 4 rule clusters; top hotspot: `legacy_work_queue_transition` (1015).
- Highest-density known migration debt: `claude` with 1739 mapped stale reads; top hotspot: `legacy_work_queue_transition` (1015, 58.37% of known debt).
- Unmapped missing repo reads remain for: `codex`, `hermes`; this looks more like general path drift than known migration debt.
- Scope note: Migration-debt figures are based on remediation-mapped entries from each provider's top missing repo reads.

## Provider interpretation summary
- Focus this week: prioritize legacy-path redirect cleanup and prompt/doc updates on claude (urgency 88.0, issue: legacy_work_queue_transition), then address gemini (urgency 47.72, issue: legacy_local_work_queue_items).
- Recommended actions:
  - `claude` [urgent_now] — prioritize legacy-path redirect cleanup and prompt/doc updates (urgency 88.0, issue: legacy_work_queue_transition; health=red; movement: rank unchanged at #1; urgency 88.00 (+0.00 vs previous audit); migration debt improved; path drift improved; corpus was pruned or rebuilt)
  - `gemini` [next_up] — prioritize legacy-path redirect cleanup and prompt/doc updates (urgency 47.72, issue: legacy_local_work_queue_items; health=red; movement: rank unchanged at #2; urgency 47.72 (+0.00 vs previous audit))
  - `codex` [investigate] — sample top missing repo reads to separate remap work from benign variance (urgency 13.0, issue: unmapped path drift; health=yellow; movement: rank unchanged at #3; urgency 13.00 (-28.00 vs previous audit); recent activity cooled; path drift improved)
- Health overview:
  - `claude` [red] — red: urgent action tier; high migration debt; corpus anomaly needs interpretation; currently active
  - `gemini` [red] — red: high migration debt; python3-heavy command hygiene
  - `codex` [yellow] — yellow: unmapped path drift remains
  - `hermes` [yellow] — yellow: unmapped path drift remains; 7d sustained activity
- Watchlist triggers:
  - `claude` [page] — urgent-now provider with legacy_work_queue_transition | follow-up: Escalate immediately on claude: prioritize legacy-path redirect cleanup and prompt/doc updates
  - `gemini` [act_this_week] — red health due to legacy_local_work_queue_items | follow-up: Prioritize this week on gemini: prioritize legacy-path redirect cleanup and prompt/doc updates
  - `hermes` [investigate] — yellow health with sustained 7d activity and unmapped path drift | follow-up: Sample current traces on hermes and verify whether unmapped path drift needs remap or docs cleanup
  - `codex` [monitor] — yellow: unmapped path drift remains | follow-up: Monitor codex in the next audit cycle
- Change alerts:
  - `codex` [cleared_watchlist] — codex cleared watchlist from act_this_week | follow-up: Monitor codex in the next audit cycle
- Remediation playbooks:
  - `claude` [page] — issue=legacy_work_queue_transition | lane=governance-docs | owner=governance-maintainers | owner_surface=docs/governance/SESSION-GOVERNANCE.md | inspect=scripts/work-queue/verify-gate-evidence.py, scripts/work-queue/start_stage.py, scripts/work-queue/exit_stage.py | targets=docs/governance/SESSION-GOVERNANCE.md, docs/governance/TRUST-ARCHITECTURE.md, scripts/workflow/governance-checkpoints.yaml | steps: Inspect the top matched stale paths for legacy_work_queue_transition and confirm they should redirect rather than be recreated. | Open the canonical targets and migrate prompts/docs/tooling toward: docs/governance/SESSION-GOVERNANCE.md, docs/governance/TRUST-ARCHITECTURE.md, scripts/workflow/governance-checkpoints.yaml.
  - `gemini` [act_this_week] — issue=legacy_local_work_queue_items | lane=planning-workflow | owner=planning-ops | owner_surface=notes/agent-work-queue.md | inspect=.claude/work-queue/WRK-149.md, .claude/work-queue/working, .claude/work-queue/working/ | targets=GitHub issues, .planning/, notes/agent-work-queue.md | steps: Inspect the top matched stale paths for legacy_local_work_queue_items and confirm they should redirect rather than be recreated. | Open the canonical targets and migrate prompts/docs/tooling toward: GitHub issues, .planning/, notes/agent-work-queue.md.
  - `codex` [monitor] — issue=unmapped path drift | lane=drift-triage | owner=drift-triage | owner_surface=docs/ops/legacy-claude-reference-map.md | inspect=analysis/provider-session-ecosystem-audit.json, docs/reports/provider-session-ecosystem-audit.md | targets=docs/ops/legacy-claude-reference-map.md, docs/work-queue-workflow.md | steps: Sample the provider's top missing repo reads from the audit JSON and group them by path family. | Decide whether each path family is a legitimate missing file, a deleted legacy path, or a symbolic/non-file surface that needs remapping.
  - `hermes` [investigate] — issue=unmapped path drift | lane=drift-triage | owner=drift-triage | owner_surface=docs/ops/legacy-claude-reference-map.md | inspect=analysis/provider-session-ecosystem-audit.json, docs/reports/provider-session-ecosystem-audit.md | targets=docs/ops/legacy-claude-reference-map.md, docs/work-queue-workflow.md | steps: Sample the provider's top missing repo reads from the audit JSON and group them by path family. | Decide whether each path family is a legitimate missing file, a deleted legacy path, or a symbolic/non-file surface that needs remapping.
- Follow-up issue drafts:
  - `claude` [critical] — [critical] claude: remediate legacy_work_queue_transition | state=unchanged | owner=governance-maintainers | lane=governance-docs
  - `gemini` [high] — [high] gemini: remediate legacy_local_work_queue_items | state=unchanged | owner=planning-ops | lane=planning-workflow
  - `hermes` [medium] — [medium] hermes: remediate unmapped path drift | state=unchanged | owner=drift-triage | lane=drift-triage
- Issue posting readiness:
  - `claude` [ready] — should_open_issue=no | final_should_open=yes | evidence=complete | linked_issue=none | matched_on=none | reason=unchanged draft has no linked issue; safe to open once
  - `gemini` [ready] — should_open_issue=no | final_should_open=yes | evidence=complete | linked_issue=none | matched_on=none | reason=unchanged draft has no linked issue; safe to open once
  - `hermes` [ready] — should_open_issue=no | final_should_open=yes | evidence=complete | linked_issue=none | matched_on=none | reason=unchanged draft has no linked issue; safe to open once
- Cleared follow-up issue drafts:
  - `codex` [cleared] — previous_title=[high] codex: remediate unmapped path drift | previous_severity=high | previous_owner=drift-triage
- `claude` — rank=1 (prev=1, move=stable) | health=red | profile=light_recent | 24h=3121 posts/67 sessions | 7d=10796 posts/211 sessions | urgency=88.0 | tier=urgent_now | activity=active (stable) | corpus=corpus_pruned_or_rebuilt | debt=high_debt (improving) | drift=improving | python=uv_preferred (stable) | health summary: red: urgent action tier; high migration debt; corpus anomaly needs interpretation; currently active | movement: rank unchanged at #1; urgency 88.00 (+0.00 vs previous audit); migration debt improved; path drift improved; corpus was pruned or rebuilt | primary issue: legacy_work_queue_transition | action: prioritize legacy-path redirect cleanup and prompt/doc updates
- `gemini` — rank=2 (prev=2, move=stable) | health=red | profile=light_recent | 24h=0 posts/0 sessions | 7d=94 posts/16 sessions | urgency=47.72 | tier=next_up | activity=idle (stable) | corpus=aligned | debt=high_debt (stable) | drift=stable | python=python3_heavy (stable) | health summary: red: high migration debt; python3-heavy command hygiene | movement: rank unchanged at #2; urgency 47.72 (+0.00 vs previous audit) | primary issue: legacy_local_work_queue_items | action: prioritize legacy-path redirect cleanup and prompt/doc updates
- `codex` — rank=3 (prev=3, move=stable) | health=yellow | profile=light_recent | 24h=943 posts/28 sessions | 7d=3413 posts/198 sessions | urgency=13.0 | tier=investigate | activity=idle (decreasing) | corpus=aligned | debt=drift_only (stable) | drift=improving | python=mixed (stable) | health summary: yellow: unmapped path drift remains | movement: rank unchanged at #3; urgency 13.00 (-28.00 vs previous audit); recent activity cooled; path drift improved | primary issue: unmapped path drift | action: sample top missing repo reads to separate remap work from benign variance
- `hermes` — rank=4 (prev=4, move=stable) | health=yellow | profile=sustained_background | 24h=8300 posts/102 sessions | 7d=58849 posts/476 sessions | urgency=5.13 | tier=monitor | activity=idle (decreasing) | corpus=aligned | debt=drift_only (stable) | drift=stable | python=mixed (stable) | health summary: yellow: unmapped path drift remains; 7d sustained activity | movement: rank unchanged at #4; urgency 5.13 (-28.00 vs previous audit); recent activity cooled | primary issue: unmapped path drift | action: sample top missing repo reads to separate remap work from benign variance

## Recent activity since previous audit
- Previous audit timestamp: `2026-04-24T14:26:59Z`
- Recent post-audit activity: `claude` 174 post records / 11 sessions.
- Scope note: This is event-time activity since the previous audit timestamp, not a census of newly exported historical/backfilled records.

## Rolling activity windows
- `last_24h` — `2026-04-23T15:10:53Z` → `2026-04-24T15:10:53Z`
  - Scope note: Last 24 hours of event-time activity ending at this audit timestamp.
  - Activity leaders: `hermes` 8300 post records / 102 sessions, `claude` 3121 post records / 67 sessions, `codex` 943 post records / 28 sessions.
- `last_7d` — `2026-04-17T15:10:53Z` → `2026-04-24T15:10:53Z`
  - Scope note: Last 7 days of event-time activity ending at this audit timestamp.
  - Activity leaders: `hermes` 58849 post records / 476 sessions, `claude` 10796 post records / 211 sessions, `codex` 3413 post records / 198 sessions, `gemini` 94 post records / 16 sessions.

## Corpus change since previous audit
- Previous audit timestamp: `2026-04-24T14:26:59Z`
- Scope note: Snapshot-to-snapshot corpus deltas reflect export additions/removals/reclassification and should be interpreted separately from event-time recent activity.
- Largest negative reconciliation gap: `claude`
- Largest positive reconciliation gap: `codex`

## claude
- Source: raw_logs
- Sessions: 37
- Post-hook records: 89063
- Correction sessions: 0
- Unique runtime sessions: 332
- Prompt-like reads: 109
- Blank read targets: 0
- Missing repo reads: 8454
- Bare python3 bash calls: 760
- `uv run ... python` bash calls: 6012

### claude top tools
- `Bash` — 49102
- `Read` — 17052
- `Edit` — 7889
- `Write` — 7222
- `Grep` — 2288
- `Agent` — 987
- `ToolSearch` — 681
- `TaskUpdate` — 541

### claude top repos
- `workspace-hub` — 85041
- `digitalmodel` — 1900
- `assetutilities` — 535
- `worldenergydata` — 201
- `agent-a597ec3f` — 100
- `issue-2348-exec` — 90
- `aceengineer-admin` — 87
- `agent-a1fcef76` — 58

### claude top reads
- `scripts/work-queue/verify-gate-evidence.py` — 740
- `scripts/work-queue/generate-html-review.py` — 249
- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` — 143
- `scripts/work-queue/start_stage.py` — 138
- `scripts/work-queue/exit_stage.py` — 137
- `docs/plans/README.md` — 125
- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` — 123
- `scripts/work-queue/close-item.sh` — 94
- `docs/plans/_template-issue-plan.md` — 82
- `scripts/work-queue/whats-next.sh` — 70

### claude top symbolic reads
- none

### claude top sibling-repo reads
- `digitalmodel/specs/data-needs.yaml` — 7
- `digitalmodel/specs/module-registry.yaml` — 5
- `digitalmodel/examples/demos/gtm/prospect_adapter.py` — 3
- `digitalmodel/docs/domains/openfoam/naval_architecture/propeller_hull_interaction.pdf` — 2
- `digitalmodel/docs/domains/ship-design/maneuvering_ship.pdf` — 2
- `worldenergydata/tests/test_resource_estimation.py` — 2
- `digitalmodel/docs/domains/hydrodynamics/literature/viviani-2007-four-quadrant-wageningen-b-series.pdf` — 2
- `digitalmodel/tests/fixtures/reporting/riser_lazy_wave_fpso.metadata.json` — 2
- `digitalmodel/examples/demos/gtm/tests/test_prospect_pipeline_e2e.py` — 2
- `digitalmodel/docs/domains/drilling/references/REF-ENG-DECOM-vol-1-a-study-for-the-bureau-of-safety-and-environmental-enforcement-bsee-final-9-10-2020.pdf` — 1

### claude top non-repo artifact reads
- none

### claude top Bash command families
- `ls` — 7532
- `uv run` — 5800
- `grep` — 5793
- `cat` — 4753
- `find` — 3540
- `bash` — 2948
- `gh` — 2037
- `sed` — 1389

### claude recent activity since previous audit
- Post-hook records since prior audit: 174
- Runtime sessions since prior audit: 11

### claude recent top tools
- `Bash` — 116
- `Read` — 39
- `Write` — 10
- `Edit` — 5
- `Agent` — 4

### claude recent top reads
- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` — 3
- `docs/plans/_template-issue-plan.md` — 3
- `docs/plans/2026-04-24-issue-279-orcaflex-reporting-standardization.md` — 2
- `scripts/review/results/2026-04-24-plan-279-adversarial.md` — 2
- `scripts/review/results/2026-04-24-plan-279-claude.md` — 2

### claude recent top writes
- `/mnt/local-analysis/workspace-hub/docs/handoffs/session-2026-04-24-aceengineer-about-canonical-check-exit.md` — 1
- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_reflog_as_ground_truth.md` — 1
- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_stash_caret_3_for_untracked.md` — 1
- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_autosync_silent_pusher.md` — 1
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-04-24-issue-279-orcaflex-reporting-standardization.md` — 1

### claude recent top edits
- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` — 2
- `/mnt/local-analysis/workspace-hub/scripts/review/submit-to-gemini.sh` — 1
- `/mnt/local-analysis/workspace-hub/docs/handoffs/session-2026-04-24-aceengineer-about-canonical-check-exit.md` — 1
- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/project_aceengineer_copy_canonical_sources.md` — 1

### claude recent top Bash command families
- `ls` — 33
- `grep` — 19
- `gh` — 14
- `cd` — 7
- `cat` — 5
- `echo` — 5
- `git log` — 4
- `for` — 3

### claude recent top missing repo reads
- `scripts/review/results/20260424T145554Z-plan-2471.md-plan-claude.md` — 1
- `scripts/review/results/20260424T145830Z-plan-2471.md-plan-gemini.md` — 1
- `scripts/review/results/20260424T145857Z-plan-2471.md-plan-gemini.md` — 1

### claude recent top sibling-repo reads
- none

### claude recent top non-repo artifact reads
- none

### claude corpus change since previous audit
- Post-hook records: current 89063 vs previous 88891 (delta 172)
- Sessions: current 37 vs previous 37 (delta 0)
- Missing repo reads: current 8454 vs previous 8451 (delta 3)
- Event-time post records since prior audit: 174
- Reconciliation gap vs event-time delta: -2
- Status: corpus_pruned_or_rebuilt
- Interpretation: Snapshot shrank relative to recent event-time activity, suggesting pruning, rebuild, or reclassification.

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
- `digitalmodel/specs/module-registry.yaml` — 5
- `digitalmodel/examples/demos/gtm/prospect_adapter.py` — 3
- `digitalmodel/docs/domains/openfoam/naval_architecture/propeller_hull_interaction.pdf` — 2
- `digitalmodel/docs/domains/ship-design/maneuvering_ship.pdf` — 2
- `worldenergydata/tests/test_resource_estimation.py` — 2
- `digitalmodel/docs/domains/hydrodynamics/literature/viviani-2007-four-quadrant-wageningen-b-series.pdf` — 2
- `digitalmodel/tests/fixtures/reporting/riser_lazy_wave_fpso.metadata.json` — 2
- `digitalmodel/examples/demos/gtm/tests/test_prospect_pipeline_e2e.py` — 2
- `digitalmodel/docs/domains/drilling/references/REF-ENG-DECOM-vol-1-a-study-for-the-bureau-of-safety-and-environmental-enforcement-bsee-final-9-10-2020.pdf` — 1

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
- `/tmp/tmp.4fvalbgSpv/review-content.md` — 10
- `/tmp/tmp.Y7GHawx2jw/review-content.md` — 9
- `/tmp/tmp.sHUq6zx1JY/review-content.md` — 6
- `/tmp/tmp.Y2upjk3JCH/review-content.md` — 5
- `/tmp/tmp.SmqPbkghat/review-content.md` — 5
- `/tmp/tmp.mIXvhD1xZj/review-content.md` — 5
- `/tmp/tmp.xgxlrsu4AN/review-content.md` — 5
- `/tmp/gt1r-frame/frame_preview.png` — 5
- `/mnt/local-analysis/worktrees/workspace-hub-issue-2096/docs/document-intelligence/intelligence-accessibility-map.md` — 5

## codex
- Source: raw_logs
- Sessions: 53
- Post-hook records: 20144
- Correction sessions: 0
- Unique runtime sessions: 659
- Prompt-like reads: 7
- Blank read targets: 0
- Missing repo reads: 463
- Bare python3 bash calls: 361
- `uv run ... python` bash calls: 428

### codex top tools
- `Bash` — 16853
- `Read` — 1730
- `Grep` — 887
- `update_plan` — 398
- `list_mcp_resources` — 149
- `list_mcp_resource_templates` — 17
- `_create_branch` — 16
- `_fetch_commit` — 14

### codex top repos
- `workspace-hub` — 20144

### codex top reads
- `docs/plans/README.md` — 65
- `docs/standards/HARD-STOP-POLICY.md` — 28
- `AGENTS.md` — 19
- `docs/standards/AI_REVIEW_ROUTING_POLICY.md` — 18
- `docs/plans/_template-issue-plan.md` — 16
- `docs/standards/CONTROL_PLANE_CONTRACT.md` — 16
- `pyproject.toml` — 12
- `config/scheduled-tasks/schedule-tasks.yaml` — 11
- `CLAUDE.md` — 10
- `tests/docs/test_banned_stale_references.py` — 9

### codex top symbolic reads
- `github://vamseeachanta/workspace-hub/issues/2018` — 6
- `github://vamseeachanta/workspace-hub/issues/2424` — 6
- `github://vamseeachanta/workspace-hub/issues/2460` — 6
- `github://vamseeachanta/workspace-hub/issues/2452` — 6
- `github://vamseeachanta/workspace-hub/issues/2089` — 5
- `github://vamseeachanta/workspace-hub/issues/1583` — 5
- `github://vamseeachanta/workspace-hub/issues/2289` — 5
- `github://vamseeachanta/workspace-hub/issues/2467` — 5
- `github://vamseeachanta/workspace-hub/issues/2468` — 5
- `github://vamseeachanta/workspace-hub/issues/2459` — 4

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
- `sed` — 4703
- `rg` — 1911
- `nl` — 1386
- `ls` — 534
- `bash` — 477
- `uv run` — 454
- `find` — 439
- `git status` — 333

### codex recent activity since previous audit
- Post-hook records since prior audit: 0
- Runtime sessions since prior audit: 0

### codex recent top tools
- none

### codex recent top reads
- none

### codex recent top writes
- none

### codex recent top edits
- none

### codex recent top Bash command families
- none

### codex recent top missing repo reads
- none

### codex recent top sibling-repo reads
- none

### codex recent top non-repo artifact reads
- none

### codex corpus change since previous audit
- Post-hook records: current 20144 vs previous 20144 (delta 0)
- Sessions: current 53 vs previous 53 (delta 0)
- Missing repo reads: current 463 vs previous 524 (delta -61)
- Event-time post records since prior audit: 0
- Reconciliation gap vs event-time delta: 0
- Status: aligned
- Interpretation: Snapshot post-record change aligns with recent event-time activity.

### codex top missing repo reads
- `src/worldenergydata/cost/data_collection/calibration_schema.py` — 9
- `src/worldenergydata/cost/data_collection/public_dataset.py` — 8
- `src/worldenergydata/cost/data_collection/__init__.py` — 8
- `docs/plans/2026-04-21-issue-334-annual-operator-disclosures-dataset.md` — 8
- `src/assethold/signals/watchlist.py` — 7
- `src/worldenergydata/cost/calibration/cost_predictor.py` — 7
- `tests/unit/cost/test_proxy_comparison.py` — 7
- `.claude/CLAUDE.md` — 6
- `.github/workflows/python-tests.yml` — 6
- `tests/unit/cost/test_cost_predictor.py` — 6

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
- none

### codex top missing external reads
- none

## hermes
- Source: raw_logs
- Sessions: 22
- Post-hook records: 160131
- Correction sessions: 22
- Unique runtime sessions: 1807
- Prompt-like reads: 1139
- Blank read targets: 26
- Missing repo reads: 684
- Bare python3 bash calls: 2684
- `uv run ... python` bash calls: 2250

### hermes top tools
- `Bash` — 67999
- `Read` — 30418
- `Grep` — 24322
- `Write` — 20105
- `Edit` — 14000
- `Task` — 1835
- `Browser` — 691
- `ToolSearch` — 311

### hermes top repos
- `workspace-hub` — 160131

### hermes top reads
- `docs/plans/README.md` — 413
- `scripts/analysis/provider_session_ecosystem_audit.py` — 387
- `docs/reports/provider-session-ecosystem-audit.md` — 332
- `analysis/provider-session-ecosystem-audit.json` — 281
- `tests/analysis/test_provider_session_ecosystem_audit.py` — 275
- `config/scheduled-tasks/schedule-tasks.yaml` — 252
- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` — 235
- `docs/plans/_template-issue-plan.md` — 179
- `docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md` — 154
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` — 91

### hermes top symbolic reads
- `github/github-issues` — 438
- `coordination/issue-planning-mode` — 427
- `github-issues` — 221
- `coordination/gh-work-planning` — 201
- `software-development/gh-work-execution` — 177
- `coordination/session-start-routine` — 151
- `autonomous-ai-agents/claude-code` — 143
- `software-development/overnight-parallel-agent-prompts` — 134
- `coordination/provider-session-ecosystem-audit` — 127
- `software-development/multi-provider-adversarial-review` — 125

### hermes top sibling-repo reads
- `digitalmodel/specs/module-registry.yaml` — 14
- `worldenergydata/docs/plans/README.md` — 8
- `digitalmodel/docs/roadmaps/orcawave-orcaflex-capability-roadmap.md` — 7
- `digitalmodel/docs/assessments/hull-library-audit.md` — 7
- `worldenergydata/.planning/quick/gemini-review.txt` — 6
- `worldenergydata/.planning/quick/codex-review.txt` — 4
- `worldenergydata/.planning/quick/claude-review.txt` — 4
- `digitalmodel/src/digitalmodel/solvers/orcaflex/installation_analysis.py` — 4
- `worldenergydata/.planning/quick/review-343-rerun-gemini.out` — 4
- `digitalmodel/.claude/skills/orcaflex-batch-manager/SKILL.md` — 3

### hermes top non-repo artifact reads
- none

### hermes top Bash command families
- `gh` — 15639
- `uv run` — 4331
- `git status` — 2829
- `git add` — 2331
- `bash` — 1756
- `find` — 1506
- `ls` — 1452
- `python3` — 1334

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
- Post-hook records: current 160131 vs previous 160131 (delta 0)
- Sessions: current 22 vs previous 22 (delta 0)
- Missing repo reads: current 684 vs previous 684 (delta 0)
- Event-time post records since prior audit: 0
- Reconciliation gap vs event-time delta: 0
- Status: aligned
- Interpretation: Snapshot post-record change aligns with recent event-time activity.

### hermes top missing repo reads
- `.claude/worktrees/ecosystem-sync/docs/plans/2026-04-20-aceengineer-ecosystem-sync-plan.md` — 67
- `client_projects/engineering_workbooks/ballymore/jumper_manifold_to_plet/jumper_lift.py` — 24
- `scripts/hooks/pre-push.sh` — 19
- `knowledge/wikis/engineering/index.md` — 19
- `knowledge/wikis/engineering/log.md` — 19
- `docs/plans/2026-04-10-llm-wiki-resource-doc-repo-integration-blueprint.md` — 18
- `.worktrees/worldenergydata-337/src/worldenergydata/cost/data_collection/__init__.py` — 18
- `.claude/worktrees/ecosystem-sync/docs/plans/2026-04-20-aceengineer-ecosystem-sync-hermes-handback.md` — 15
- `.claude/worktrees/ecosystem-sync/docs/plans/2026-04-20-aceengineer-ecosystem-sync-review.md` — 15
- `.claude/worktrees/ecosystem-sync/docs/plans/2026-04-19-aceengineer-ecosystem-sync-design.md` — 15

### hermes top sibling-repo reads
- `digitalmodel/specs/module-registry.yaml` — 14
- `worldenergydata/docs/plans/README.md` — 8
- `digitalmodel/docs/roadmaps/orcawave-orcaflex-capability-roadmap.md` — 7
- `digitalmodel/docs/assessments/hull-library-audit.md` — 7
- `worldenergydata/.planning/quick/gemini-review.txt` — 6
- `worldenergydata/.planning/quick/codex-review.txt` — 4
- `worldenergydata/.planning/quick/claude-review.txt` — 4
- `digitalmodel/src/digitalmodel/solvers/orcaflex/installation_analysis.py` — 4
- `worldenergydata/.planning/quick/review-343-rerun-gemini.out` — 4
- `digitalmodel/.claude/skills/orcaflex-batch-manager/SKILL.md` — 3

### hermes top non-repo artifact reads
- none

### hermes remediation hints for stale repo reads
- none

### hermes top missing external reads
- `/mnt/local-analysis/worktrees/ws-2451-plan/docs/plans/2026-04-22-issue-2451-worldenergydata-test-followup.md` — 88
- `/mnt/local-analysis/worktrees/digitalmodel-issue-521/scripts/benchmark/validate_owd_vs_spec.py` — 40
- `/mnt/local-analysis/worktrees/digitalmodel-issue-521/src/digitalmodel/hydrodynamics/diffraction/benchmark_runner.py` — 32
- `/mnt/local-analysis/worktrees/ws-2448-plan/docs/plans/2026-04-22-issue-2448-assethold-smoke-followup.md` — 29
- `/mnt/local-analysis/worktrees/digitalmodel-issue-521/src/digitalmodel/hydrodynamics/diffraction/benchmark_input_comparison.py` — 24
- `/mnt/local-analysis/worktrees/digitalmodel-issue-521/tests/hydrodynamics/diffraction/test_benchmark_input_comparison.py` — 21
- `/mnt/local-analysis/worktrees/digitalmodel-issue-521/tests/hydrodynamics/diffraction/test_benchmark_runner.py` — 19
- `/mnt/local-analysis/worktrees/workspace-hub-issue-2281/scripts/skills/weekly_skills_audit.py` — 18
- `/mnt/local-analysis/worktrees/workspace-hub-2151/docs/modules/ai/readiness-evidence-bundle.schema.yaml` — 17
- `/mnt/local-analysis/worktrees/workspace-hub-issue-2281/tests/skills/test_weekly_skills_audit.py` — 17

## gemini
- Source: raw_logs
- Sessions: 48
- Post-hook records: 6173
- Correction sessions: 0
- Unique runtime sessions: 332
- Prompt-like reads: 18
- Blank read targets: 0
- Missing repo reads: 603
- Bare python3 bash calls: 291
- `uv run ... python` bash calls: 39

### gemini top tools
- `Bash` — 2288
- `Read` — 2181
- `Grep` — 655
- `Write` — 535
- `Edit` — 394
- `Browser` — 106
- `ToolSearch` — 9
- `generalist` — 3

### gemini top repos
- `workspace-hub` — 6173

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
- Post-hook records: current 6173 vs previous 6173 (delta 0)
- Sessions: current 48 vs previous 48 (delta 0)
- Missing repo reads: current 603 vs previous 603 (delta 0)
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

