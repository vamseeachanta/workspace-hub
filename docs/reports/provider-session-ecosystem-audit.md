# Provider session ecosystem audit — 2026-04-23

Scope: provider session artifacts rooted at `/mnt/local-analysis/workspace-hub/logs/orchestrator` with saved provider artifacts used only as fallback when raw logs are unavailable.

## Executive summary
- `claude` — source=raw_logs | sessions=36 | post_records=86172 | python3/1k=8.65 | uv-python/1k=69.77
- `codex` — source=raw_logs | sessions=52 | post_records=19148 | python3/1k=18.8 | uv-python/1k=22.14
- `hermes` — source=raw_logs | sessions=21 | post_records=144131 | python3/1k=17.01 | uv-python/1k=15.0
- `gemini` — source=raw_logs | sessions=48 | post_records=6172 | python3/1k=47.15 | uv-python/1k=6.32

- Migration debt density (known stale reads with redirect hints per 1k records): `claude` 20.18, `gemini` 13.93, `codex` 0.0, `hermes` 0.0.
- Highest-volume known migration debt: `claude` with 1739 mapped stale reads across 4 rule clusters; top hotspot: `legacy_work_queue_transition` (1015).
- Highest-density known migration debt: `claude` with 1739 mapped stale reads; top hotspot: `legacy_work_queue_transition` (1015, 58.37% of known debt).
- Unmapped missing repo reads remain for: `codex`, `hermes`; this looks more like general path drift than known migration debt.
- Scope note: Migration-debt figures are based on remediation-mapped entries from each provider's top missing repo reads.

## Provider interpretation summary
- Focus this week: prioritize legacy-path redirect cleanup and prompt/doc updates on claude (urgency 80.0, issue: legacy_work_queue_transition), then address gemini (urgency 67.72, issue: legacy_local_work_queue_items).
- Recommended actions:
  - `claude` [urgent_now] — prioritize legacy-path redirect cleanup and prompt/doc updates (urgency 80.0, issue: legacy_work_queue_transition; health=red; movement: rank unchanged at #1; urgency 80.00 (+0.00 vs previous audit); migration debt improved; path drift improved)
  - `gemini` [next_up] — prioritize legacy-path redirect cleanup and prompt/doc updates (urgency 67.72, issue: legacy_local_work_queue_items; health=red; movement: rank unchanged at #2; urgency 67.72 (+12.00 vs previous audit); recent activity increased; migration debt improved; path drift worsened)
  - `codex` [next_up] — sample top missing repo reads to separate remap work from benign variance (urgency 41.0, issue: unmapped path drift; health=red; movement: rank unchanged at #3; urgency 41.00 (+7.70 vs previous audit); path drift worsened; corpus grew faster than event-time activity)
  - `hermes` [investigate] — sample top missing repo reads to separate remap work from benign variance (urgency 32.19, issue: unmapped path drift; health=yellow; movement: rank unchanged at #4; urgency 32.19 (+0.19 vs previous audit); path drift worsened; corpus grew faster than event-time activity)
- Health overview:
  - `claude` [red] — red: urgent action tier; high migration debt; 7d sustained activity; currently active
  - `gemini` [red] — red: high migration debt; path drift worsening; python3-heavy command hygiene; currently active
  - `codex` [red] — red: unmapped path drift remains; path drift worsening; corpus anomaly needs interpretation; 7d sustained activity
  - `hermes` [yellow] — yellow: unmapped path drift remains; path drift worsening; corpus anomaly needs interpretation; currently active
- Watchlist triggers:
  - `claude` [page] — urgent-now provider with legacy_work_queue_transition | follow-up: Escalate immediately on claude: prioritize legacy-path redirect cleanup and prompt/doc updates
  - `codex` [act_this_week] — red health due to unmapped path drift; corpus anomaly present | follow-up: Prioritize this week on codex: sample top missing repo reads to separate remap work from benign variance
  - `gemini` [act_this_week] — red health due to legacy_local_work_queue_items | follow-up: Prioritize this week on gemini: prioritize legacy-path redirect cleanup and prompt/doc updates
  - `hermes` [monitor] — yellow: unmapped path drift remains; path drift worsening; corpus anomaly needs interpretation; currently active; corpus anomaly present | follow-up: Monitor hermes in the next audit cycle
- Change alerts:
  - `codex` [trigger_escalated] — codex trigger escalated from investigate to act_this_week | follow-up: Prioritize this week on codex: sample top missing repo reads to separate remap work from benign variance
  - `hermes` [cleared_watchlist] — hermes cleared watchlist from investigate | follow-up: Monitor hermes in the next audit cycle
- Remediation playbooks:
  - `claude` [page] — issue=legacy_work_queue_transition | lane=governance-docs | owner=governance-maintainers | owner_surface=docs/governance/SESSION-GOVERNANCE.md | inspect=scripts/work-queue/verify-gate-evidence.py, scripts/work-queue/start_stage.py, scripts/work-queue/exit_stage.py | targets=docs/governance/SESSION-GOVERNANCE.md, docs/governance/TRUST-ARCHITECTURE.md, scripts/workflow/governance-checkpoints.yaml | steps: Inspect the top matched stale paths for legacy_work_queue_transition and confirm they should redirect rather than be recreated. | Open the canonical targets and migrate prompts/docs/tooling toward: docs/governance/SESSION-GOVERNANCE.md, docs/governance/TRUST-ARCHITECTURE.md, scripts/workflow/governance-checkpoints.yaml.
  - `gemini` [act_this_week] — issue=legacy_local_work_queue_items | lane=planning-workflow | owner=planning-ops | owner_surface=notes/agent-work-queue.md | inspect=.claude/work-queue/WRK-149.md, .claude/work-queue/working, .claude/work-queue/working/ | targets=GitHub issues, .planning/, notes/agent-work-queue.md | steps: Inspect the top matched stale paths for legacy_local_work_queue_items and confirm they should redirect rather than be recreated. | Open the canonical targets and migrate prompts/docs/tooling toward: GitHub issues, .planning/, notes/agent-work-queue.md.
  - `codex` [act_this_week] — issue=unmapped path drift | lane=drift-triage | owner=drift-triage | owner_surface=docs/ops/legacy-claude-reference-map.md | inspect=analysis/provider-session-ecosystem-audit.json, docs/reports/provider-session-ecosystem-audit.md | targets=docs/ops/legacy-claude-reference-map.md, docs/work-queue-workflow.md | steps: Sample the provider's top missing repo reads from the audit JSON and group them by path family. | Decide whether each path family is a legitimate missing file, a deleted legacy path, or a symbolic/non-file surface that needs remapping.
  - `hermes` [monitor] — issue=unmapped path drift | lane=drift-triage | owner=drift-triage | owner_surface=docs/ops/legacy-claude-reference-map.md | inspect=analysis/provider-session-ecosystem-audit.json, docs/reports/provider-session-ecosystem-audit.md | targets=docs/ops/legacy-claude-reference-map.md, docs/work-queue-workflow.md | steps: Sample the provider's top missing repo reads from the audit JSON and group them by path family. | Decide whether each path family is a legitimate missing file, a deleted legacy path, or a symbolic/non-file surface that needs remapping.
- Follow-up issue drafts:
  - `claude` [critical] — [critical] claude: remediate legacy_work_queue_transition | state=unchanged | owner=governance-maintainers | lane=governance-docs
  - `codex` [high] — [high] codex: remediate unmapped path drift | state=changed | owner=drift-triage | lane=drift-triage
  - `gemini` [high] — [high] gemini: remediate legacy_local_work_queue_items | state=unchanged | owner=planning-ops | lane=planning-workflow
- Issue posting readiness:
  - `claude` [ready] — should_open_issue=no | final_should_open=yes | evidence=complete | linked_issue=none | matched_on=none | reason=unchanged draft has no linked issue; safe to open once
  - `codex` [ready] — should_open_issue=yes | final_should_open=yes | evidence=complete | linked_issue=none | matched_on=none | reason=changed actionable draft with no linked issue found
  - `gemini` [ready] — should_open_issue=no | final_should_open=yes | evidence=complete | linked_issue=none | matched_on=none | reason=unchanged draft has no linked issue; safe to open once
- Cleared follow-up issue drafts:
  - `hermes` [cleared] — previous_title=[medium] hermes: remediate unmapped path drift | previous_severity=medium | previous_owner=drift-triage
- `claude` — rank=1 (prev=1, move=stable) | health=red | profile=sustained_background | 24h=1963 posts/53 sessions | 7d=8966 posts/173 sessions | urgency=80.0 | tier=urgent_now | activity=active (stable) | corpus=aligned | debt=high_debt (improving) | drift=improving | python=uv_preferred (stable) | health summary: red: urgent action tier; high migration debt; 7d sustained activity; currently active | movement: rank unchanged at #1; urgency 80.00 (+0.00 vs previous audit); migration debt improved; path drift improved | primary issue: legacy_work_queue_transition | action: prioritize legacy-path redirect cleanup and prompt/doc updates
- `gemini` — rank=2 (prev=2, move=stable) | health=red | profile=light_recent | 24h=24 posts/3 sessions | 7d=107 posts/22 sessions | urgency=67.72 | tier=next_up | activity=active (increasing) | corpus=aligned | debt=high_debt (improving) | drift=worsening | python=python3_heavy (stable) | health summary: red: high migration debt; path drift worsening; python3-heavy command hygiene; currently active | movement: rank unchanged at #2; urgency 67.72 (+12.00 vs previous audit); recent activity increased; migration debt improved; path drift worsened | primary issue: legacy_local_work_queue_items | action: prioritize legacy-path redirect cleanup and prompt/doc updates
- `codex` — rank=3 (prev=3, move=stable) | health=red | profile=sustained_background | 24h=470 posts/33 sessions | 7d=2664 posts/179 sessions | urgency=41.0 | tier=next_up | activity=active (stable) | corpus=positive_corpus_growth_beyond_recent_activity | debt=drift_only (stable) | drift=worsening | python=mixed (stable) | health summary: red: unmapped path drift remains; path drift worsening; corpus anomaly needs interpretation; 7d sustained activity | movement: rank unchanged at #3; urgency 41.00 (+7.70 vs previous audit); path drift worsened; corpus grew faster than event-time activity | primary issue: unmapped path drift | action: sample top missing repo reads to separate remap work from benign variance
- `hermes` — rank=4 (prev=4, move=stable) | health=yellow | profile=light_recent | 24h=12436 posts/80 sessions | 7d=43874 posts/347 sessions | urgency=32.19 | tier=investigate | activity=active (stable) | corpus=positive_corpus_growth_beyond_recent_activity | debt=drift_only (stable) | drift=worsening | python=mixed (stable) | health summary: yellow: unmapped path drift remains; path drift worsening; corpus anomaly needs interpretation; currently active | movement: rank unchanged at #4; urgency 32.19 (+0.19 vs previous audit); path drift worsened; corpus grew faster than event-time activity | primary issue: unmapped path drift | action: sample top missing repo reads to separate remap work from benign variance

## Recent activity since previous audit
- Previous audit timestamp: `2026-04-22T00:19:59Z`
- Recent post-audit activity: `hermes` 22375 post records / 160 sessions, `claude` 2355 post records / 81 sessions, `codex` 816 post records / 73 sessions, `gemini` 25 post records / 4 sessions.
- Scope note: This is event-time activity since the previous audit timestamp, not a census of newly exported historical/backfilled records.

## Rolling activity windows
- `last_24h` — `2026-04-22T16:20:22Z` → `2026-04-23T16:20:22Z`
  - Scope note: Last 24 hours of event-time activity ending at this audit timestamp.
  - Activity leaders: `hermes` 12436 post records / 80 sessions, `claude` 1963 post records / 53 sessions, `codex` 470 post records / 33 sessions, `gemini` 24 post records / 3 sessions.
- `last_7d` — `2026-04-16T16:20:22Z` → `2026-04-23T16:20:22Z`
  - Scope note: Last 7 days of event-time activity ending at this audit timestamp.
  - Activity leaders: `hermes` 43874 post records / 347 sessions, `claude` 8966 post records / 173 sessions, `codex` 2664 post records / 179 sessions, `gemini` 107 post records / 22 sessions.

## Corpus change since previous audit
- Previous audit timestamp: `2026-04-22T00:19:59Z`
- Scope note: Snapshot-to-snapshot corpus deltas reflect export additions/removals/reclassification and should be interpreted separately from event-time recent activity.
- Largest negative reconciliation gap: `claude`
- Largest positive reconciliation gap: `hermes`

## claude
- Source: raw_logs
- Sessions: 36
- Post-hook records: 86172
- Correction sessions: 0
- Unique runtime sessions: 278
- Prompt-like reads: 106
- Blank read targets: 0
- Missing repo reads: 8390
- Bare python3 bash calls: 745
- `uv run ... python` bash calls: 6012

### claude top tools
- `Bash` — 47113
- `Read` — 16477
- `Edit` — 7800
- `Write` — 7098
- `Grep` — 2236
- `Agent` — 938
- `ToolSearch` — 681
- `TaskUpdate` — 541

### claude top repos
- `workspace-hub` — 82186
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
- `scripts/work-queue/start_stage.py` — 138
- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` — 137
- `scripts/work-queue/exit_stage.py` — 137
- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` — 123
- `docs/plans/README.md` — 118
- `scripts/work-queue/close-item.sh` — 94
- `scripts/work-queue/whats-next.sh` — 70
- `.claude/skills/coordination/workspace/work-queue/SKILL.md` — 66

### claude top symbolic reads
- none

### claude top sibling-repo reads
- `digitalmodel/specs/data-needs.yaml` — 7
- `digitalmodel/specs/module-registry.yaml` — 5
- `digitalmodel/docs/domains/openfoam/naval_architecture/propeller_hull_interaction.pdf` — 2
- `digitalmodel/docs/domains/ship-design/maneuvering_ship.pdf` — 2
- `worldenergydata/tests/test_resource_estimation.py` — 2
- `digitalmodel/docs/domains/hydrodynamics/literature/viviani-2007-four-quadrant-wageningen-b-series.pdf` — 2
- `digitalmodel/docs/domains/drilling/references/REF-ENG-DECOM-vol-1-a-study-for-the-bureau-of-safety-and-environmental-enforcement-bsee-final-9-10-2020.pdf` — 1
- `worldenergydata/CHANGELOG.md` — 1
- `assethold/src/assethold/stocks/indicators.py` — 1
- `assethold/src/assethold/stocks/trend_detector.py` — 1

### claude top Bash command families
- `ls` — 7034
- `uv run` — 5791
- `grep` — 5583
- `cat` — 4647
- `find` — 3395
- `bash` — 2927
- `gh` — 1887
- `sed` — 1372

### claude recent activity since previous audit
- Post-hook records since prior audit: 2355
- Runtime sessions since prior audit: 81

### claude recent top tools
- `Bash` — 1378
- `Read` — 473
- `Edit` — 146
- `Grep` — 124
- `Write` — 111

### claude recent top reads
- `docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md` — 23
- `docs/plans/_template-issue-plan.md` — 19
- `digitalmodel/scripts/semantic_validate.py` — 19
- `docs/plans/README.md` — 16
- `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` — 11

### claude recent top writes
- `/mnt/local-analysis/workspace-hub/scripts/review/results/2026-04-22-plan-2462-claude.md` — 3
- `/mnt/local-analysis/workspace-hub/.planning/quick/apply_p2_2442.py` — 2
- `/mnt/local-analysis/workspace-hub/.claude/worktrees/ws-plan-2441-2444/scripts/review/results/2026-04-21-plan-2443-gemini-r3.md` — 2
- `/mnt/local-analysis/workspace-hub/scripts/review/results/2026-04-22-plan-2465-claude.md` — 2
- `/mnt/local-analysis/workspace-hub/scripts/review/results/2026-04-22-plan-2462-gemini.md` — 2

### claude recent top edits
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md` — 16
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-04-22-issue-2461-assetutilities-routing-and-source-hygiene.md` — 16
- `/mnt/local-analysis/workspace-hub/.claude/worktrees/ws-plan-2441-2444/docs/plans/2026-04-21-issue-2443-achantas-data-markdown-lint.md` — 12
- `/mnt/local-analysis/workspace-hub/.claude/worktrees/ws-plan-2441-2444/docs/plans/2026-04-21-issue-2444-aceengineer-admin-ci.md` — 10
- `/mnt/local-analysis/worktrees/ws-2460-2465-planwave/docs/plans/2026-04-22-issue-2459-assethold-post-smoke-ci-hardening.md` — 9

### claude recent top Bash command families
- `git` — 460
- `ls` — 266
- `gh` — 209
- `cat` — 72
- `grep` — 68
- `uv run` — 46
- `wc` — 39
- `head` — 28

### claude recent top missing repo reads
- `docs/plans/2026-04-22-issue-2462-digitalmodel-repo-wide-operator-map.md` — 4
- `.claude/worktrees/ws-2460-2465-w4/docs/plans/2026-04-22-issue-2463-aceengineer-website-canonical-routing.md` — 3
- `.claude/worktrees/ws-2460-2465-w4/docs/plans/2026-04-22-issue-2464-workspace-hub-routing-split.md` — 2
- `docs/plans/2026-04-23-issue-2454-c03-fpso-semantic-proof.md` — 2
- `.planning/quick/apply_p2_2442.py` — 1

### claude recent top sibling-repo reads
- none

### claude corpus change since previous audit
- Post-hook records: current 86172 vs previous 83817 (delta 2355)
- Sessions: current 36 vs previous 34 (delta 2)
- Missing repo reads: current 8390 vs previous 8376 (delta 14)
- Event-time post records since prior audit: 2355
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
- `digitalmodel/specs/module-registry.yaml` — 5
- `digitalmodel/docs/domains/openfoam/naval_architecture/propeller_hull_interaction.pdf` — 2
- `digitalmodel/docs/domains/ship-design/maneuvering_ship.pdf` — 2
- `worldenergydata/tests/test_resource_estimation.py` — 2
- `digitalmodel/docs/domains/hydrodynamics/literature/viviani-2007-four-quadrant-wageningen-b-series.pdf` — 2
- `digitalmodel/docs/domains/drilling/references/REF-ENG-DECOM-vol-1-a-study-for-the-bureau-of-safety-and-environmental-enforcement-bsee-final-9-10-2020.pdf` — 1
- `worldenergydata/CHANGELOG.md` — 1
- `assethold/src/assethold/stocks/indicators.py` — 1
- `assethold/src/assethold/stocks/trend_detector.py` — 1

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
- `/tmp/tmp.yX4KezaN1x/review-content.md` — 4

## codex
- Source: raw_logs
- Sessions: 52
- Post-hook records: 19148
- Correction sessions: 0
- Unique runtime sessions: 628
- Prompt-like reads: 1
- Blank read targets: 0
- Missing repo reads: 435
- Bare python3 bash calls: 360
- `uv run ... python` bash calls: 424

### codex top tools
- `Bash` — 16546
- `Read` — 1372
- `Grep` — 642
- `update_plan` — 394
- `list_mcp_resources` — 123
- `list_mcp_resource_templates` — 16
- `_fetch_commit` — 11
- `request_user_input` — 5

### codex top repos
- `workspace-hub` — 19148

### codex top reads
- `docs/plans/README.md` — 48
- `docs/standards/HARD-STOP-POLICY.md` — 23
- `docs/standards/AI_REVIEW_ROUTING_POLICY.md` — 16
- `AGENTS.md` — 16
- `docs/standards/CONTROL_PLANE_CONTRACT.md` — 15
- `config/scheduled-tasks/schedule-tasks.yaml` — 11
- `pyproject.toml` — 10
- `content/demos/index.html` — 9
- `src/worldenergydata/cost/data_collection/calibration_schema.py` — 9
- `CLAUDE.md` — 8

### codex top symbolic reads
- `github://vamseeachanta/workspace-hub/issues/2089` — 5
- `github://vamseeachanta/workspace-hub/issues/1583` — 5
- `github://vamseeachanta/workspace-hub/issues/2018` — 4
- `github://vamseeachanta/workspace-hub/issues/2459` — 4
- `github://vamseeachanta/workspace-hub/issues/2249` — 3
- `github://vamseeachanta/workspace-hub/issues/2344` — 3
- `github://vamseeachanta/workspace-hub/issues/2399` — 3
- `github://vamseeachanta/workspace-hub/issues/2330` — 3
- `github://vamseeachanta/workspace-hub/issues/2323` — 3
- `github://vamseeachanta/workspace-hub/issues/2289` — 3

### codex top sibling-repo reads
- none

### codex top Bash command families
- `sed` — 4560
- `rg` — 1887
- `nl` — 1381
- `ls` — 529
- `bash` — 473
- `uv run` — 453
- `find` — 437
- `git status` — 322

### codex recent activity since previous audit
- Post-hook records since prior audit: 816
- Runtime sessions since prior audit: 73

### codex recent top tools
- `Bash` — 337
- `Read` — 320
- `Grep` — 121
- `list_mcp_resources` — 25
- `update_plan` — 5

### codex recent top reads
- `docs/plans/README.md` — 12
- `src/worldenergydata/cost/data_collection/calibration_schema.py` — 9
- `src/worldenergydata/cost/data_collection/public_dataset.py` — 8
- `src/worldenergydata/cost/data_collection/__init__.py` — 8
- `docs/plans/2026-04-21-issue-334-annual-operator-disclosures-dataset.md` — 8

### codex recent top writes
- none

### codex recent top edits
- none

### codex recent top Bash command families
- `sed` — 181
- `rg` — 57
- `nl` — 38
- `pwd` — 37
- `git status` — 10
- `wc` — 4
- `ls` — 4
- `git` — 1

### codex recent top missing repo reads
- `src/worldenergydata/cost/data_collection/calibration_schema.py` — 9
- `src/worldenergydata/cost/data_collection/public_dataset.py` — 8
- `src/worldenergydata/cost/data_collection/__init__.py` — 8
- `docs/plans/2026-04-21-issue-334-annual-operator-disclosures-dataset.md` — 8
- `src/worldenergydata/cost/calibration/cost_predictor.py` — 7

### codex recent top sibling-repo reads
- none

### codex corpus change since previous audit
- Post-hook records: current 19148 vs previous 17843 (delta 1305)
- Sessions: current 52 vs previous 50 (delta 2)
- Missing repo reads: current 435 vs previous 225 (delta 210)
- Event-time post records since prior audit: 816
- Reconciliation gap vs event-time delta: 489
- Status: positive_corpus_growth_beyond_recent_activity
- Interpretation: Snapshot grew more than recent event-time activity, suggesting backfill or expanded export coverage.

### codex top missing repo reads
- `content/demos/index.html` — 9
- `src/worldenergydata/cost/data_collection/calibration_schema.py` — 9
- `src/worldenergydata/cost/data_collection/public_dataset.py` — 8
- `src/worldenergydata/cost/data_collection/__init__.py` — 8
- `docs/plans/2026-04-21-issue-334-annual-operator-disclosures-dataset.md` — 8
- `src/assethold/signals/watchlist.py` — 7
- `build.js` — 7
- `vercel.json` — 7
- `src/worldenergydata/cost/calibration/cost_predictor.py` — 7
- `tests/unit/cost/test_proxy_comparison.py` — 7

### codex top sibling-repo reads
- none

### codex remediation hints for stale repo reads
- none

### codex top missing external reads
- none

## hermes
- Source: raw_logs
- Sessions: 21
- Post-hook records: 144131
- Correction sessions: 21
- Unique runtime sessions: 1670
- Prompt-like reads: 1037
- Blank read targets: 26
- Missing repo reads: 341
- Bare python3 bash calls: 2451
- `uv run ... python` bash calls: 2162

### hermes top tools
- `Bash` — 60845
- `Read` — 27316
- `Grep` — 22315
- `Write` — 17817
- `Edit` — 12838
- `Task` — 1667
- `Browser` — 608
- `ToolSearch` — 293

### hermes top repos
- `workspace-hub` — 144131

### hermes top reads
- `scripts/analysis/provider_session_ecosystem_audit.py` — 387
- `docs/plans/README.md` — 361
- `docs/reports/provider-session-ecosystem-audit.md` — 299
- `tests/analysis/test_provider_session_ecosystem_audit.py` — 275
- `analysis/provider-session-ecosystem-audit.json` — 263
- `config/scheduled-tasks/schedule-tasks.yaml` — 252
- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` — 235
- `docs/plans/_template-issue-plan.md` — 158
- `scripts/_core/sync-agent-configs.sh` — 90
- `/home/vamsee/.hermes/config.yaml` — 90

### hermes top symbolic reads
- `github/github-issues` — 398
- `coordination/issue-planning-mode` — 311
- `github-issues` — 204
- `software-development/gh-work-execution` — 142
- `autonomous-ai-agents/claude-code` — 141
- `coordination/gh-work-planning` — 135
- `coordination/session-start-routine` — 129
- `coordination/provider-session-ecosystem-audit` — 118
- `coordination/provider-session-learning-transfer` — 109
- `issue-planning-mode` — 104

### hermes top sibling-repo reads
- `digitalmodel/specs/module-registry.yaml` — 14
- `digitalmodel/docs/roadmaps/orcawave-orcaflex-capability-roadmap.md` — 7
- `digitalmodel/docs/assessments/hull-library-audit.md` — 7
- `worldenergydata/.planning/quick/gemini-review.txt` — 6
- `worldenergydata/.planning/quick/codex-review.txt` — 4
- `worldenergydata/.planning/quick/claude-review.txt` — 4
- `digitalmodel/src/digitalmodel/solvers/orcaflex/installation_analysis.py` — 4
- `worldenergydata/docs/plans/README.md` — 4
- `digitalmodel/.claude/skills/orcaflex-batch-manager/SKILL.md` — 3
- `digitalmodel/.claude/skills/converted-agents/orcaflex/SKILL.md` — 3

### hermes top Bash command families
- `gh` — 14154
- `uv run` — 4182
- `git status` — 2355
- `git add` — 2220
- `bash` — 1734
- `find` — 1462
- `ls` — 1395
- `cat` — 1287

### hermes recent activity since previous audit
- Post-hook records since prior audit: 22375
- Runtime sessions since prior audit: 160

### hermes recent top tools
- `Bash` — 8694
- `Read` — 4739
- `Write` — 3399
- `Grep` — 3071
- `Edit` — 2103

### hermes recent top reads
- `github/github-issues` — 120
- `coordination/issue-planning-mode` — 109
- `docs/plans/README.md` — 88
- `/mnt/local-analysis/worktrees/ws-2451-plan/docs/plans/2026-04-22-issue-2451-worldenergydata-test-followup.md` — 88
- `docs/reports/digitalmodel-orcawave-orcaflex-issue-reconciliation.md` — 57

### hermes recent top writes
- `/mnt/local-analysis/workspace-hub/scripts/review/results/2026-04-22-plan-2460-claude.md` — 17
- `/mnt/local-analysis/workspace-hub/scripts/review/results/2026-04-22-plan-2460-codex.md` — 17
- `/mnt/local-analysis/workspace-hub/scripts/review/results/2026-04-22-plan-2460-gemini.md` — 17
- `/mnt/local-analysis/workspace-hub/digitalmodel/tests/solvers/orcaflex/reporting/fixture_helpers.py` — 16
- `/tmp/worldenergydata-annual-operator-disclosures-issue.md` — 15

### hermes recent top edits
- `/mnt/local-analysis/worktrees/ws-2451-plan/docs/plans/2026-04-22-issue-2451-worldenergydata-test-followup.md` — 600
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md` — 269
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-04-22-issue-2459-assethold-post-smoke-ci-hardening.md` — 198
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-04-22-issue-2332-provider-audit-python3-runtime-cleanup.md` — 153
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-04-21-issue-2444-aceengineer-admin-ci.md` — 125

### hermes recent top Bash command families
- `gh` — 3535
- `bash` — 344
- `set` — 250
- `uv run` — 237
- `git status` — 235
- `git add` — 183
- `codex` — 169
- `for` — 168

### hermes recent top missing repo reads
- `knowledge/wikis/engineering/index.md` — 15
- `knowledge/wikis/engineering/log.md` — 15
- `.worktrees/worldenergydata-337/src/worldenergydata/cost/data_collection/__init__.py` — 10
- `aceengineer-website/.agent-os/product/mission.md` — 9
- `aceengineer-website/.agent-os/product/roadmap.md` — 9

### hermes recent top sibling-repo reads
- `worldenergydata/docs/plans/README.md` — 4

### hermes corpus change since previous audit
- Post-hook records: current 144131 vs previous 114819 (delta 29312)
- Sessions: current 21 vs previous 19 (delta 2)
- Missing repo reads: current 341 vs previous 229 (delta 112)
- Event-time post records since prior audit: 22375
- Reconciliation gap vs event-time delta: 6937
- Status: positive_corpus_growth_beyond_recent_activity
- Interpretation: Snapshot grew more than recent event-time activity, suggesting backfill or expanded export coverage.

### hermes top missing repo reads
- `client_projects/engineering_workbooks/ballymore/jumper_manifold_to_plet/jumper_lift.py` — 24
- `scripts/hooks/pre-push.sh` — 19
- `docs/plans/2026-04-10-llm-wiki-resource-doc-repo-integration-blueprint.md` — 18
- `knowledge/wikis/engineering/index.md` — 15
- `knowledge/wikis/engineering/log.md` — 15
- `.worktrees/worldenergydata-337/src/worldenergydata/cost/data_collection/__init__.py` — 10
- `aceengineer-website/.agent-os/product/mission.md` — 9
- `aceengineer-website/.agent-os/product/roadmap.md` — 9
- `.planning/quick/review-2239.md` — 8
- `docs/handoffs/overnight-llm-wiki-stage1-source-map.md` — 7

### hermes top sibling-repo reads
- `digitalmodel/specs/module-registry.yaml` — 14
- `digitalmodel/docs/roadmaps/orcawave-orcaflex-capability-roadmap.md` — 7
- `digitalmodel/docs/assessments/hull-library-audit.md` — 7
- `worldenergydata/.planning/quick/gemini-review.txt` — 6
- `worldenergydata/.planning/quick/codex-review.txt` — 4
- `worldenergydata/.planning/quick/claude-review.txt` — 4
- `digitalmodel/src/digitalmodel/solvers/orcaflex/installation_analysis.py` — 4
- `worldenergydata/docs/plans/README.md` — 4
- `digitalmodel/.claude/skills/orcaflex-batch-manager/SKILL.md` — 3
- `digitalmodel/.claude/skills/converted-agents/orcaflex/SKILL.md` — 3

### hermes remediation hints for stale repo reads
- none

### hermes top missing external reads
- `/mnt/local-analysis/worktrees/digitalmodel-issue-521/scripts/benchmark/validate_owd_vs_spec.py` — 40
- `/mnt/local-analysis/worktrees/digitalmodel-issue-521/src/digitalmodel/hydrodynamics/diffraction/benchmark_runner.py` — 32
- `/mnt/local-analysis/worktrees/digitalmodel-issue-521/src/digitalmodel/hydrodynamics/diffraction/benchmark_input_comparison.py` — 24
- `/mnt/local-analysis/worktrees/digitalmodel-issue-521/tests/hydrodynamics/diffraction/test_benchmark_input_comparison.py` — 21
- `/mnt/local-analysis/worktrees/digitalmodel-issue-521/tests/hydrodynamics/diffraction/test_benchmark_runner.py` — 19
- `/mnt/local-analysis/worktrees/workspace-hub-2151/docs/modules/ai/readiness-evidence-bundle.schema.yaml` — 17
- `/mnt/local-analysis/worktrees/wh-2127/docs/governance/SESSION-GOVERNANCE.md` — 12
- `/mnt/local-analysis/worktrees/worldenergydata-2433/tests/modules/bsee/analysis/npv-data-source-comparison/test_cash_flow_components.py` — 12
- `/mnt/local-analysis/worktrees/wh-2127/tests/work-queue/test_session_governor.py` — 11
- `/mnt/local-analysis/worktrees/worldenergydata-2433/tests/conftest.py` — 10

## gemini
- Source: raw_logs
- Sessions: 48
- Post-hook records: 6172
- Correction sessions: 0
- Unique runtime sessions: 331
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
- `Browser` — 105
- `ToolSearch` — 9
- `generalist` — 3

### gemini top repos
- `workspace-hub` — 6172

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
- Post-hook records since prior audit: 25
- Runtime sessions since prior audit: 4

### gemini recent top tools
- `Grep` — 14
- `Read` — 8
- `Bash` — 1
- `Browser` — 1
- `generalist` — 1

### gemini recent top reads
- `worldenergydata` — 2
- `src/worldenergydata/cost/data_collection/public_dataset.py` — 1
- `src/worldenergydata/cost/data_collection/disclosure_ingest_contract.py` — 1
- `src/worldenergydata/cost/disclosure_analytics.py` — 1
- `worldenergydata/src/worldenergydata/cost/data_collection/public_dataset.py` — 1

### gemini recent top writes
- none

### gemini recent top edits
- none

### gemini recent top Bash command families
- `ls` — 1

### gemini recent top missing repo reads
- `src/worldenergydata/cost/data_collection/public_dataset.py` — 1
- `src/worldenergydata/cost/data_collection/disclosure_ingest_contract.py` — 1
- `src/worldenergydata/cost/disclosure_analytics.py` — 1

### gemini recent top sibling-repo reads
- none

### gemini corpus change since previous audit
- Post-hook records: current 6172 vs previous 6147 (delta 25)
- Sessions: current 48 vs previous 46 (delta 2)
- Missing repo reads: current 603 vs previous 600 (delta 3)
- Event-time post records since prior audit: 25
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

