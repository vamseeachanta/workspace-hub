# Provider session ecosystem audit — 2026-04-22

Scope: provider session artifacts rooted at `/mnt/local-analysis/workspace-hub/logs/orchestrator` with saved provider artifacts used only as fallback when raw logs are unavailable.

## Executive summary
- `claude` — source=raw_logs | sessions=34 | post_records=83817 | python3/1k=8.88 | uv-python/1k=71.45
- `codex` — source=raw_logs | sessions=50 | post_records=17843 | python3/1k=18.89 | uv-python/1k=23.59
- `hermes` — source=raw_logs | sessions=19 | post_records=114819 | python3/1k=17.93 | uv-python/1k=17.81
- `gemini` — source=raw_logs | sessions=46 | post_records=6147 | python3/1k=47.34 | uv-python/1k=6.34

- Migration debt density (known stale reads with redirect hints per 1k records): `claude` 20.75, `gemini` 13.99, `codex` 0.0, `hermes` 0.0.
- Highest-volume known migration debt: `claude` with 1739 mapped stale reads across 4 rule clusters; top hotspot: `legacy_work_queue_transition` (1015).
- Highest-density known migration debt: `claude` with 1739 mapped stale reads; top hotspot: `legacy_work_queue_transition` (1015, 58.37% of known debt).
- Unmapped missing repo reads remain for: `codex`, `hermes`; this looks more like general path drift than known migration debt.
- Scope note: Migration-debt figures are based on remediation-mapped entries from each provider's top missing repo reads.

## Provider interpretation summary
- Focus this week: prioritize legacy-path redirect cleanup and prompt/doc updates on claude (urgency 80.0, issue: legacy_work_queue_transition), then address gemini (urgency 55.72, issue: legacy_local_work_queue_items).
- Recommended actions:
  - `claude` [urgent_now] — prioritize legacy-path redirect cleanup and prompt/doc updates (urgency 80.0, issue: legacy_work_queue_transition; health=red; movement: rank unchanged at #1; urgency 80.00 (+24.77 vs previous audit); recent activity increased; migration debt worsened; path drift worsened)
  - `gemini` [next_up] — prioritize legacy-path redirect cleanup and prompt/doc updates (urgency 55.72, issue: legacy_local_work_queue_items; health=red; movement: rank unchanged at #2; urgency 55.72 (+8.04 vs previous audit); migration debt worsened; path drift worsened; corpus grew faster than event-time activity)
  - `codex` [investigate] — sample top missing repo reads to separate remap work from benign variance (urgency 33.3, issue: unmapped path drift; health=yellow; movement: rank unchanged at #3; urgency 33.30 (+25.59 vs previous audit); recent activity increased; path drift worsened; corpus grew faster than event-time activity)
  - `hermes` [investigate] — sample top missing repo reads to separate remap work from benign variance (urgency 32.0, issue: unmapped path drift; health=yellow; movement: rank unchanged at #4; urgency 32.00 (+27.96 vs previous audit); recent activity increased; path drift improved; corpus grew faster than event-time activity)
- Health overview:
  - `claude` [red] — red: urgent action tier; high migration debt; migration debt worsening; path drift worsening
  - `gemini` [red] — red: high migration debt; migration debt worsening; path drift worsening; python3-heavy command hygiene
  - `codex` [yellow] — yellow: unmapped path drift remains; path drift worsening; corpus anomaly needs interpretation; 7d sustained activity
  - `hermes` [yellow] — yellow: unmapped path drift remains; corpus anomaly needs interpretation; 7d sustained activity; currently active
- Watchlist triggers:
  - `claude` [page] — urgent-now provider with legacy_work_queue_transition | follow-up: Escalate immediately on claude: prioritize legacy-path redirect cleanup and prompt/doc updates
  - `gemini` [act_this_week] — red health due to legacy_local_work_queue_items; corpus anomaly present | follow-up: Prioritize this week on gemini: prioritize legacy-path redirect cleanup and prompt/doc updates
  - `codex` [investigate] — yellow health with sustained 7d activity and unmapped path drift; corpus anomaly present | follow-up: Sample current traces on codex and verify whether unmapped path drift needs remap or docs cleanup
  - `hermes` [investigate] — yellow health with sustained 7d activity and unmapped path drift; corpus anomaly present | follow-up: Sample current traces on hermes and verify whether unmapped path drift needs remap or docs cleanup
- Change alerts:
  - `claude` [trigger_escalated] — claude trigger escalated from act_this_week to page | follow-up: Escalate immediately on claude: prioritize legacy-path redirect cleanup and prompt/doc updates
- Remediation playbooks:
  - `claude` [page] — issue=legacy_work_queue_transition | lane=governance-docs | owner=governance-maintainers | owner_surface=docs/governance/SESSION-GOVERNANCE.md | inspect=scripts/work-queue/verify-gate-evidence.py, scripts/work-queue/start_stage.py, scripts/work-queue/exit_stage.py | targets=docs/governance/SESSION-GOVERNANCE.md, docs/governance/TRUST-ARCHITECTURE.md, scripts/workflow/governance-checkpoints.yaml | steps: Inspect the top matched stale paths for legacy_work_queue_transition and confirm they should redirect rather than be recreated. | Open the canonical targets and migrate prompts/docs/tooling toward: docs/governance/SESSION-GOVERNANCE.md, docs/governance/TRUST-ARCHITECTURE.md, scripts/workflow/governance-checkpoints.yaml.
  - `gemini` [act_this_week] — issue=legacy_local_work_queue_items | lane=planning-workflow | owner=planning-ops | owner_surface=notes/agent-work-queue.md | inspect=.claude/work-queue/WRK-149.md, .claude/work-queue/working, .claude/work-queue/working/ | targets=GitHub issues, .planning/, notes/agent-work-queue.md | steps: Inspect the top matched stale paths for legacy_local_work_queue_items and confirm they should redirect rather than be recreated. | Open the canonical targets and migrate prompts/docs/tooling toward: GitHub issues, .planning/, notes/agent-work-queue.md.
  - `codex` [investigate] — issue=unmapped path drift | lane=drift-triage | owner=drift-triage | owner_surface=docs/ops/legacy-claude-reference-map.md | inspect=analysis/provider-session-ecosystem-audit.json, docs/reports/provider-session-ecosystem-audit.md | targets=docs/ops/legacy-claude-reference-map.md, docs/work-queue-workflow.md | steps: Sample the provider's top missing repo reads from the audit JSON and group them by path family. | Decide whether each path family is a legitimate missing file, a deleted legacy path, or a symbolic/non-file surface that needs remapping.
  - `hermes` [investigate] — issue=unmapped path drift | lane=drift-triage | owner=drift-triage | owner_surface=docs/ops/legacy-claude-reference-map.md | inspect=analysis/provider-session-ecosystem-audit.json, docs/reports/provider-session-ecosystem-audit.md | targets=docs/ops/legacy-claude-reference-map.md, docs/work-queue-workflow.md | steps: Sample the provider's top missing repo reads from the audit JSON and group them by path family. | Decide whether each path family is a legitimate missing file, a deleted legacy path, or a symbolic/non-file surface that needs remapping.
- Follow-up issue drafts:
  - `claude` [critical] — [critical] claude: remediate legacy_work_queue_transition | state=changed | owner=governance-maintainers | lane=governance-docs
  - `gemini` [high] — [high] gemini: remediate legacy_local_work_queue_items | state=unchanged | owner=planning-ops | lane=planning-workflow
  - `codex` [medium] — [medium] codex: remediate unmapped path drift | state=unchanged | owner=drift-triage | lane=drift-triage
  - `hermes` [medium] — [medium] hermes: remediate unmapped path drift | state=unchanged | owner=drift-triage | lane=drift-triage
- Issue posting readiness:
  - `claude` [ready] — should_open_issue=yes | final_should_open=yes | evidence=complete | linked_issue=none | matched_on=none | reason=changed actionable draft with no linked issue found
  - `gemini` [ready] — should_open_issue=no | final_should_open=yes | evidence=complete | linked_issue=none | matched_on=none | reason=unchanged draft has no linked issue; safe to open once
  - `codex` [ready] — should_open_issue=no | final_should_open=yes | evidence=complete | linked_issue=none | matched_on=none | reason=unchanged draft has no linked issue; safe to open once
  - `hermes` [ready] — should_open_issue=no | final_should_open=yes | evidence=complete | linked_issue=none | matched_on=none | reason=unchanged draft has no linked issue; safe to open once
- `claude` — rank=1 (prev=1, move=stable) | health=red | profile=light_recent | 24h=2295 posts/58 sessions | 7d=8506 posts/141 sessions | urgency=80.0 | tier=urgent_now | activity=active (increasing) | corpus=aligned | debt=high_debt (worsening) | drift=worsening | python=uv_preferred (stable) | health summary: red: urgent action tier; high migration debt; migration debt worsening; path drift worsening | movement: rank unchanged at #1; urgency 80.00 (+24.77 vs previous audit); recent activity increased; migration debt worsened; path drift worsened | primary issue: legacy_work_queue_transition | action: prioritize legacy-path redirect cleanup and prompt/doc updates
- `gemini` — rank=2 (prev=2, move=stable) | health=red | profile=light_recent | 24h=0 posts/0 sessions | 7d=170 posts/32 sessions | urgency=55.72 | tier=next_up | activity=idle (stable) | corpus=positive_corpus_growth_beyond_recent_activity | debt=high_debt (worsening) | drift=worsening | python=python3_heavy (stable) | health summary: red: high migration debt; migration debt worsening; path drift worsening; python3-heavy command hygiene | movement: rank unchanged at #2; urgency 55.72 (+8.04 vs previous audit); migration debt worsened; path drift worsened; corpus grew faster than event-time activity | primary issue: legacy_local_work_queue_items | action: prioritize legacy-path redirect cleanup and prompt/doc updates
- `codex` — rank=3 (prev=3, move=stable) | health=yellow | profile=sustained_background | 24h=10 posts/3 sessions | 7d=1683 posts/89 sessions | urgency=33.3 | tier=investigate | activity=active (increasing) | corpus=positive_corpus_growth_beyond_recent_activity | debt=drift_only (stable) | drift=worsening | python=mixed (stable) | health summary: yellow: unmapped path drift remains; path drift worsening; corpus anomaly needs interpretation; 7d sustained activity | movement: rank unchanged at #3; urgency 33.30 (+25.59 vs previous audit); recent activity increased; path drift worsened; corpus grew faster than event-time activity | primary issue: unmapped path drift | action: sample top missing repo reads to separate remap work from benign variance
- `hermes` — rank=4 (prev=4, move=stable) | health=yellow | profile=sustained_background | 24h=4 posts/1 sessions | 7d=32781 posts/267 sessions | urgency=32.0 | tier=investigate | activity=active (increasing) | corpus=positive_corpus_growth_beyond_recent_activity | debt=drift_only (stable) | drift=improving | python=mixed (stable) | health summary: yellow: unmapped path drift remains; corpus anomaly needs interpretation; 7d sustained activity; currently active | movement: rank unchanged at #4; urgency 32.00 (+27.96 vs previous audit); recent activity increased; path drift improved; corpus grew faster than event-time activity | primary issue: unmapped path drift | action: sample top missing repo reads to separate remap work from benign variance

## Recent activity since previous audit
- Previous audit timestamp: `2026-04-20T21:46:16Z`
- Recent post-audit activity: `claude` 2351 post records / 62 sessions, `hermes` 589 post records / 3 sessions, `codex` 10 post records / 3 sessions.
- Scope note: This is event-time activity since the previous audit timestamp, not a census of newly exported historical/backfilled records.

## Rolling activity windows
- `last_24h` — `2026-04-21T00:19:59Z` → `2026-04-22T00:19:59Z`
  - Scope note: Last 24 hours of event-time activity ending at this audit timestamp.
  - Activity leaders: `claude` 2295 post records / 58 sessions, `codex` 10 post records / 3 sessions, `hermes` 4 post records / 1 sessions.
- `last_7d` — `2026-04-15T00:19:59Z` → `2026-04-22T00:19:59Z`
  - Scope note: Last 7 days of event-time activity ending at this audit timestamp.
  - Activity leaders: `hermes` 32781 post records / 267 sessions, `claude` 8506 post records / 141 sessions, `codex` 1683 post records / 89 sessions, `gemini` 170 post records / 32 sessions.

## Corpus change since previous audit
- Previous audit timestamp: `2026-04-20T21:46:16Z`
- Scope note: Snapshot-to-snapshot corpus deltas reflect export additions/removals/reclassification and should be interpreted separately from event-time recent activity.
- Largest negative reconciliation gap: `claude`
- Largest positive reconciliation gap: `hermes`

## claude
- Source: raw_logs
- Sessions: 34
- Post-hook records: 83817
- Correction sessions: 0
- Unique runtime sessions: 197
- Prompt-like reads: 101
- Blank read targets: 0
- Missing repo reads: 8376
- Bare python3 bash calls: 744
- `uv run ... python` bash calls: 5989

### claude top tools
- `Bash` — 45735
- `Read` — 16004
- `Edit` — 7654
- `Write` — 6987
- `Grep` — 2112
- `Agent` — 927
- `ToolSearch` — 681
- `TaskUpdate` — 541

### claude top repos
- `workspace-hub` — 79955
- `digitalmodel` — 1900
- `assetutilities` — 535
- `worldenergydata` — 201
- `agent-a597ec3f` — 100
- `aceengineer-admin` — 87
- `issue-2348-exec` — 76
- `agent-a1fcef76` — 58

### claude top reads
- `scripts/work-queue/verify-gate-evidence.py` — 740
- `scripts/work-queue/generate-html-review.py` — 249
- `scripts/work-queue/start_stage.py` — 138
- `scripts/work-queue/exit_stage.py` — 137
- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` — 133
- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` — 123
- `docs/plans/README.md` — 102
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
- `ls` — 6768
- `uv run` — 5745
- `grep` — 5515
- `cat` — 4575
- `find` — 3381
- `bash` — 2927
- `gh` — 1678
- `sed` — 1368

### claude recent activity since previous audit
- Post-hook records since prior audit: 2351
- Runtime sessions since prior audit: 62

### claude recent top tools
- `Bash` — 1360
- `Read` — 326
- `unknown` — 251
- `Edit` — 190
- `Write` — 96

### claude recent top reads
- `docs/plans/README.md` — 11
- `.claude/skills/coordination/issue-planning-mode/SKILL.md` — 10
- `.github/workflows/baseline-check.yml` — 8
- `.claude/worktrees/issue-2348-exec/scripts/gtm/job-market-scanner.py` — 8
- `docs/plans/_template-issue-plan.md` — 8

### claude recent top writes
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md` — 6
- `/mnt/local-analysis/workspace-hub/scripts/review/attest-plan-claims.sh` — 3
- `/mnt/local-analysis/workspace-hub/docs/session-handoffs/2026-04-20-gtm-plan-review-implementation.md` — 1
- `/mnt/local-analysis/workspace-hub/.planning/handoffs/2026-04-20-doc-intel-session-2-handoff.md` — 1
- `/mnt/local-analysis/workspace-hub/scripts/review/results/2026-04-20-v2-plan-2367-codex.md` — 1

### claude recent top edits
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-04-20-issue-2017-plan.md` — 56
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-04-21-issue-2442-assethold-python-tests.md` — 16
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-04-20-issue-2391-sitemap-404-fix.md` — 15
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-04-21-issue-2441-digitalmodel-pylife-dep.md` — 14
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-04-20-issue-2367-pdf-cta-wiring.md` — 13

### claude recent top Bash command families
- `gh` — 324
- `ls` — 271
- `git` — 89
- `cd` — 64
- `git log` — 53
- `grep` — 47
- `cat` — 46
- `git add` — 41

### claude recent top missing repo reads
- none

### claude recent top sibling-repo reads
- none

### claude corpus change since previous audit
- Post-hook records: current 83817 vs previous 81466 (delta 2351)
- Sessions: current 34 vs previous 33 (delta 1)
- Missing repo reads: current 8376 vs previous 7565 (delta 811)
- Event-time post records since prior audit: 2351
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
- Sessions: 50
- Post-hook records: 17843
- Correction sessions: 0
- Unique runtime sessions: 512
- Prompt-like reads: 1
- Blank read targets: 0
- Missing repo reads: 225
- Bare python3 bash calls: 337
- `uv run ... python` bash calls: 421

### codex top tools
- `Bash` — 16021
- `Read` — 880
- `Grep` — 412
- `update_plan` — 386
- `list_mcp_resources` — 83
- `list_mcp_resource_templates` — 16
- `_fetch_commit` — 11
- `request_user_input` — 5

### codex top repos
- `workspace-hub` — 17843

### codex top reads
- `docs/plans/README.md` — 32
- `docs/standards/HARD-STOP-POLICY.md` — 15
- `docs/standards/AI_REVIEW_ROUTING_POLICY.md` — 14
- `docs/standards/CONTROL_PLANE_CONTRACT.md` — 12
- `config/scheduled-tasks/schedule-tasks.yaml` — 10
- `content/demos/index.html` — 9
- `AGENTS.md` — 8
- `CLAUDE.md` — 8
- `scripts/_core/sync-agent-configs.sh` — 7
- `data/document-index/resource-intelligence-maturity.yaml` — 7

### codex top symbolic reads
- `github://vamseeachanta/workspace-hub/issues/2089` — 5
- `github://vamseeachanta/workspace-hub/issues/1583` — 5
- `github://vamseeachanta/workspace-hub/issues/2249` — 3
- `github://vamseeachanta/workspace-hub/issues/2344` — 3
- `github://vamseeachanta/workspace-hub/issues/2399` — 3
- `github://vamseeachanta/workspace-hub/issues/2330` — 3
- `github://vamseeachanta/workspace-hub/issues/2323` — 3
- `github://vamsee/workspace-hub/issues/2249` — 2
- `github://vamseeachanta/workspace-hub/issues/2250` — 2
- `github://vamseeachanta/workspace-hub/issues/2290` — 2

### codex top sibling-repo reads
- none

### codex top Bash command families
- `sed` — 4259
- `rg` — 1811
- `nl` — 1334
- `ls` — 519
- `bash` — 473
- `uv run` — 453
- `find` — 437
- `git status` — 312

### codex recent activity since previous audit
- Post-hook records since prior audit: 10
- Runtime sessions since prior audit: 3

### codex recent top tools
- `Bash` — 10

### codex recent top reads
- none

### codex recent top writes
- none

### codex recent top edits
- none

### codex recent top Bash command families
- `sed` — 5
- `nl` — 4
- `pwd` — 1

### codex recent top missing repo reads
- none

### codex recent top sibling-repo reads
- none

### codex corpus change since previous audit
- Post-hook records: current 17843 vs previous 17317 (delta 526)
- Sessions: current 50 vs previous 50 (delta 0)
- Missing repo reads: current 225 vs previous 163 (delta 62)
- Event-time post records since prior audit: 10
- Reconciliation gap vs event-time delta: 516
- Status: positive_corpus_growth_beyond_recent_activity
- Interpretation: Snapshot grew more than recent event-time activity, suggesting backfill or expanded export coverage.

### codex top missing repo reads
- `content/demos/index.html` — 9
- `build.js` — 7
- `vercel.json` — 7
- `package.json` — 6
- `.claude/CLAUDE.md` — 6
- `content/demos/jumper-installation.html` — 5
- `content/partials/head-common.html` — 5
- `sitemap.xml` — 5
- `docs/reports/2026-04-17-issue-39-market-hours-signals-consumers-plan.md` — 4
- `examples/demos/gtm/output/demo_02_wall_thickness_report.html` — 4

### codex top sibling-repo reads
- none

### codex remediation hints for stale repo reads
- none

### codex top missing external reads
- none

## hermes
- Source: raw_logs
- Sessions: 19
- Post-hook records: 114819
- Correction sessions: 19
- Unique runtime sessions: 1443
- Prompt-like reads: 866
- Blank read targets: 26
- Missing repo reads: 229
- Bare python3 bash calls: 2059
- `uv run ... python` bash calls: 2045

### hermes top tools
- `Bash` — 50170
- `Read` — 20949
- `Grep` — 18175
- `Write` — 13830
- `Edit` — 9148
- `Task` — 1394
- `Browser` — 512
- `ToolSearch` — 229

### hermes top repos
- `workspace-hub` — 114819

### hermes top reads
- `scripts/analysis/provider_session_ecosystem_audit.py` — 382
- `tests/analysis/test_provider_session_ecosystem_audit.py` — 273
- `docs/reports/provider-session-ecosystem-audit.md` — 243
- `config/scheduled-tasks/schedule-tasks.yaml` — 242
- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` — 235
- `docs/plans/README.md` — 219
- `analysis/provider-session-ecosystem-audit.json` — 213
- `docs/plans/_template-issue-plan.md` — 98
- `scripts/_core/sync-agent-configs.sh` — 90
- `/home/vamsee/.hermes/config.yaml` — 90

### hermes top symbolic reads
- `github/github-issues` — 256
- `github-issues` — 190
- `coordination/issue-planning-mode` — 167
- `autonomous-ai-agents/claude-code` — 132
- `coordination/provider-session-ecosystem-audit` — 107
- `coordination/provider-session-learning-transfer` — 97
- `issue-planning-mode` — 89
- `workspace-hub/provider-session-ecosystem-audit-and-exporters` — 87
- `gh-work-planning` — 85
- `coordination/gh-work-planning` — 84

### hermes top sibling-repo reads
- `digitalmodel/specs/module-registry.yaml` — 14
- `digitalmodel/docs/roadmaps/orcawave-orcaflex-capability-roadmap.md` — 7
- `digitalmodel/docs/assessments/hull-library-audit.md` — 7
- `worldenergydata/.planning/quick/gemini-review.txt` — 6
- `worldenergydata/.planning/quick/codex-review.txt` — 4
- `worldenergydata/.planning/quick/claude-review.txt` — 4
- `digitalmodel/src/digitalmodel/solvers/orcaflex/installation_analysis.py` — 4
- `digitalmodel/.claude/skills/orcaflex-batch-manager/SKILL.md` — 3
- `digitalmodel/.claude/skills/converted-agents/orcaflex/SKILL.md` — 3
- `digitalmodel/.claude/skills/engineering/cad-engineering-specialist/SKILL.md` — 3

### hermes top Bash command families
- `gh` — 10242
- `uv run` — 3825
- `git status` — 1996
- `git add` — 1972
- `find` — 1422
- `ls` — 1372
- `bash` — 1246
- `cat` — 1243

### hermes recent activity since previous audit
- Post-hook records since prior audit: 589
- Runtime sessions since prior audit: 3

### hermes recent top tools
- `Bash` — 199
- `Edit` — 145
- `Read` — 117
- `Grep` — 78
- `Write` — 50

### hermes recent top reads
- `scripts/analysis/provider_session_ecosystem_audit.py` — 17
- `tests/analysis/test_provider_session_ecosystem_audit.py` — 12
- `docs/plans/2026-04-20-issue-2399-next-model-release-readiness-contract.md` — 6
- `analysis/provider-session-ecosystem-audit.json` — 4
- `docs/reports/provider-session-ecosystem-audit.md` — 3

### hermes recent top writes
- `/mnt/local-analysis/workspace-hub/docs/reports/2026-04-20-provider-audit-followup-bundle.md` — 1
- `/mnt/local-analysis/workspace-hub/.planning/quick/provider-audit-2406-comment.md` — 1
- `/mnt/local-analysis/workspace-hub/.planning/quick/provider-audit-2333-comment.md` — 1
- `/tmp/issue-repo-organization-refactor.md` — 1
- `/tmp/issue-llm-wiki-spinout.md` — 1

### hermes recent top edits
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-04-20-issue-2399-next-model-release-readiness-contract.md` — 42
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-04-20-issue-2408-workspace-hub-model-release-readiness-contract-and-upgrade-playbook.md` — 23
- `/mnt/local-analysis/workspace-hub/tests/analysis/test_provider_session_ecosystem_audit.py` — 20
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-04-20-issue-2398-llm-wiki-spinout-vs-embedded-architecture.md` — 19
- `/mnt/local-analysis/workspace-hub/docs/plans/2026-04-20-issue-2397-canonical-folder-structure-and-refactor-contract.md` — 14

### hermes recent top Bash command families
- `gh` — 44
- `python3` — 33
- `codex` — 21
- `gemini` — 21
- `git status` — 7
- `bash` — 5
- `uv run` — 5
- `git diff` — 4

### hermes recent top missing repo reads
- none

### hermes recent top sibling-repo reads
- none

### hermes corpus change since previous audit
- Post-hook records: current 114819 vs previous 102042 (delta 12777)
- Sessions: current 19 vs previous 19 (delta 0)
- Missing repo reads: current 229 vs previous 212 (delta 17)
- Event-time post records since prior audit: 589
- Reconciliation gap vs event-time delta: 12188
- Status: positive_corpus_growth_beyond_recent_activity
- Interpretation: Snapshot grew more than recent event-time activity, suggesting backfill or expanded export coverage.

### hermes top missing repo reads
- `client_projects/engineering_workbooks/ballymore/jumper_manifold_to_plet/jumper_lift.py` — 24
- `docs/plans/2026-04-10-llm-wiki-resource-doc-repo-integration-blueprint.md` — 18
- `scripts/hooks/pre-push.sh` — 14
- `.planning/quick/review-2239.md` — 8
- `docs/handoffs/overnight-llm-wiki-stage1-source-map.md` — 7
- `docs/handoffs/overnight-llm-wiki-stage2-skill-repo-map.md` — 7
- `docs/handoffs/overnight-llm-wiki-stage3-architecture.md` — 7
- `docs/handoffs/2026-04-10-llm-wiki-next-actions.md` — 5
- `docs/plans/2026-04-13-issue-2246-normalize-summary-artifact-identity-between-phase-b-and-phase-c.md` — 5
- `docs/plans/2026-04-13-issue-2247-bounded-authoritative-domain-writeback-targeted-classification-runs.md` — 5

### hermes top sibling-repo reads
- `digitalmodel/specs/module-registry.yaml` — 14
- `digitalmodel/docs/roadmaps/orcawave-orcaflex-capability-roadmap.md` — 7
- `digitalmodel/docs/assessments/hull-library-audit.md` — 7
- `worldenergydata/.planning/quick/gemini-review.txt` — 6
- `worldenergydata/.planning/quick/codex-review.txt` — 4
- `worldenergydata/.planning/quick/claude-review.txt` — 4
- `digitalmodel/src/digitalmodel/solvers/orcaflex/installation_analysis.py` — 4
- `digitalmodel/.claude/skills/orcaflex-batch-manager/SKILL.md` — 3
- `digitalmodel/.claude/skills/converted-agents/orcaflex/SKILL.md` — 3
- `digitalmodel/.claude/skills/engineering/cad-engineering-specialist/SKILL.md` — 3

### hermes remediation hints for stale repo reads
- none

### hermes top missing external reads
- `/mnt/local-analysis/worktrees/workspace-hub-2151/docs/modules/ai/readiness-evidence-bundle.schema.yaml` — 17
- `/mnt/local-analysis/worktrees/wh-2127/docs/governance/SESSION-GOVERNANCE.md` — 12
- `/mnt/local-analysis/worktrees/wh-2127/tests/work-queue/test_session_governor.py` — 11
- `/mnt/local-analysis/worktrees/workspace-hub-2151/scripts/analysis/readiness_bundle_schema.py` — 9
- `/mnt/local-analysis/worktrees/workspace-hub-2151/tests/analysis/test_readiness_bundle_schema.py` — 9
- `/mnt/local-analysis/worktrees/wh-2128/tests/enforcement/test_install_hooks_stage_prompt_drift.py` — 9
- `/home/vamsee/.codex/sessions/2026/04/19/rollout-2026-04-19T*.jsonl` — 8
- `/mnt/local-analysis/worktrees/workspace-hub-2151/tests/fixtures/readiness/windows-valid.yaml` — 7
- `/mnt/local-analysis/worktrees/workspace-hub-2151/tests/fixtures/readiness/linux-valid.yaml` — 7
- `/mnt/local-analysis/worktrees/workspace-hub-2151/tests/fixtures/readiness/invalid-access-mode.yaml` — 7

## gemini
- Source: raw_logs
- Sessions: 46
- Post-hook records: 6147
- Correction sessions: 0
- Unique runtime sessions: 327
- Prompt-like reads: 18
- Blank read targets: 0
- Missing repo reads: 600
- Bare python3 bash calls: 291
- `uv run ... python` bash calls: 39

### gemini top tools
- `Bash` — 2287
- `Read` — 2173
- `Grep` — 641
- `Write` — 535
- `Edit` — 394
- `Browser` — 104
- `ToolSearch` — 9
- `generalist` — 2

### gemini top repos
- `workspace-hub` — 6147

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
- `worldenergydata` — 17
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
- `ls` — 467
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

### gemini corpus change since previous audit
- Post-hook records: current 6147 vs previous 6082 (delta 65)
- Sessions: current 46 vs previous 45 (delta 1)
- Missing repo reads: current 600 vs previous 577 (delta 23)
- Event-time post records since prior audit: 0
- Reconciliation gap vs event-time delta: 65
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

