# Provider work queue

Generated: 2026-07-10T17:25:08.735786Z
Current week: 2026-W28
Recommended provider order: gemini, claude, codex

Execution-ready means the issue already carries `status:plan-approved`. agent:* labels are routing hints only and do not grant execution approval.

## claude

- Routing priority: high
- Execution-ready candidates: 53
- Total routed candidates: 183

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2815 feat(workstations): Windows Task Scheduler reads schedule-tasks.yaml + EqualityReport live-validation [#2801 family] | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:harness, machine:ace-win-1, status:plan-review, status:plan-approved |
| #2816 feat(workstations): collect-equality.ps1 — accurate Windows compute + restore RAM floor [#2801 family] | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:harness, status:plan-review, status:plan-approved, gate:completeness |
| #3063 uv-workflow(assetutilities): register all 17 routed transforms (blocked on #88 packaging) | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:engineering, domain:workflow-standardization, status:plan-approved, dispatch:ready |
| #3064 uv-workflow(worldenergydata): clean-clone verify all 9 + offline fixtures for data loaders | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:engineering, domain:workflow-standardization, status:plan-approved, dispatch:ready |
| #3065 uv-workflow(digitalmodel): register dm#711 backlog lanes + widen tests-workflows to all rows | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:engineering, domain:workflow-standardization, status:plan-approved, dispatch:ready |
| #3282 wf-api(assetutilities): ResultEnvelope + run_workflow() + registry request/response schema [FOUNDATIONAL] | yes | strategy/workflow/architecture language | enhancement, priority:high, domain:workflow-standardization, status:plan-approved, gate:completeness, lane:claude |
| #3283 wf-api(ecosystem): determinism harness — provenance stamp + result hash + golden-baseline template | yes | strategy/workflow/architecture language | enhancement, priority:high, domain:workflow-standardization, status:plan-approved, gate:completeness, lane:codex |
| #3285 wf-api(digitalmodel): adopt ResultEnvelope + schemas + goldens (FFS, buckling, mooring, wall-thickness) | yes | strategy/workflow/architecture language | enhancement, priority:high, domain:workflow-standardization, status:plan-approved, gate:completeness, lane:codex |

## codex

- Routing priority: high
- Execution-ready candidates: 4
- Total routed candidates: 15

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #3385 Ecosystem: dedicated SME-verification section on digitalmodel + worldenergydata Pages (progressive reconciliation/baseline links) | yes | implementation/test/fix language | enhancement, priority:medium, cat:documentation, cat:website, status:plan-approved, gate:completeness |
| #3030 Dispatch-time codex weekly-quota gate: suspend lane:codex routing when available <10% | yes | implementation/test/fix language | domain:ai-tools, status:plan-approved, gate:completeness, lane:claude |
| #3143 bug(automation): a preserve/prune process destroys /tmp git worktrees + feature branches mid-session | yes | implementation/test/fix language | bug, cat:harness/ops, status:plan-approved, gate:completeness |
| #3239 Generate Deckhand deliverables from the digitalmodel.reporting block library (report-as-backbone) | yes | implementation/test/fix language | enhancement, domain:reporting, domain:gtm, status:plan-approved, gate:completeness, lane:codex |
| #2880 feat(codex): make yolo-equivalent permission defaults travel across machines | no | existing codex agent label | enhancement, priority:high, cat:harness, domain:ai-config, machine:multi, agent:codex |
| #3026 ace-linux-2: gnome-shell crash recovery (2026-06-10) + /dev/sda end-of-life replacement plan | no | implementation/test/fix language | priority:high, lane:claude |
| #3430 standard: replayable public input and source snapshot contract | no | implementation/test/fix language | enhancement, priority:high, cat:data-pipeline, domain:audit-trail, type:follow-up, status:needs-plan |
| #2920 Roll out update-harness-tools.sh across machine ecosystem | no | implementation/test/fix language | priority:medium, domain:machine-setup, lane:claude |

## gemini

- Routing priority: highest
- Execution-ready candidates: 0
- Total routed candidates: 2

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2854 gap(memory): Hermes read-back leg missing — consolidated memory never flows back into ~/.hermes/memories (parallel to #2841 Codex) | no | research/triage/audit language | priority:medium, cat:ai-orchestration, domain:knowledge-management-platform, lane:claude |
| #3031 triage: backfill placeholder bodies on gh-next-id.sh / backfill-github-refs.sh created issues | no | research/triage/audit language | priority:medium, domain:work-queue |

