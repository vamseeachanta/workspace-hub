# Provider work queue

Generated: 2026-07-27T05:21:11.963242Z
Current week: 2026-W31
Recommended provider order: codex, agy, claude

Execution-ready means the issue already carries `status:plan-approved`. agent:* labels are routing hints only and do not grant execution approval.

## claude

- Routing priority: high
- Execution-ready candidates: 54
- Total routed candidates: 176

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #3282 wf-api(assetutilities): ResultEnvelope + run_workflow() + registry request/response schema [FOUNDATIONAL] | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:engineering, domain:workflow, status:plan-approved, gate:completeness |
| #3283 wf-api(ecosystem): determinism harness — provenance stamp + result hash + golden-baseline template | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:engineering, domain:workflow, status:plan-approved, gate:completeness |
| #3285 wf-api(digitalmodel): adopt ResultEnvelope + schemas + goldens (FFS, buckling, mooring, wall-thickness) | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:engineering, domain:workflow, status:plan-approved, gate:completeness |
| #3291 seamless(ci): uv caching across assetutilities / assethold / digitalmodel test workflows | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:harness, status:plan-approved, gate:completeness, lane:claude |
| #3294 seamless(review): make adversarial-review dispatchers run headless (codex env -u CLAUDECODE, gemini non-interactive) | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:harness, status:plan-approved, gate:completeness, lane:claude |
| #3295 seamless(contract): reconcile registry schema_version into a unified v2 superset (unblocks #3282) | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:engineering, domain:workflow, status:plan-approved, gate:completeness |
| #3297 wf-api(assetutilities): make the engine embeddable — injected root, no cwd-coupled side effects [PREREQ for #3282] | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:engineering, domain:workflow, status:plan-approved, gate:completeness |
| #3307 wf-api(digitalmodel): engine embed-port — mirror #3297 for digitalmodel's own engine [prereq for #3285] | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:engineering, domain:workflow, status:plan-approved, gate:completeness |

## codex

- Routing priority: highest
- Execution-ready candidates: 7
- Total routed candidates: 24

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #3430 standard: replayable public input and source snapshot contract | yes | implementation/test/fix language | enhancement, priority:high, cat:data, status:plan-approved, type:follow-up, gate:completeness |
| #3385 Ecosystem: dedicated SME-verification section on digitalmodel + worldenergydata Pages (progressive reconciliation/baseline links) | yes | implementation/test/fix language | enhancement, priority:medium, cat:documentation, domain:website, status:plan-approved, gate:completeness |
| #3472 feat(operations): add pressure-aware daily OS maintenance cleanup | yes | implementation/test/fix language | priority:medium, cat:tooling, domain:testing, machine:dev-primary, status:plan-approved, gate:completeness |
| #3239 Generate Deckhand deliverables from the digitalmodel.reporting block library (report-as-backbone) | yes | implementation/test/fix language | enhancement, cat:business, domain:gtm, domain:content, status:plan-approved, gate:completeness |
| #3532 fix(memory): reserve cross-provider runtime budget for operational feedback | yes | implementation/test/fix language | enhancement, cat:harness, status:plan-approved, gate:completeness, lane:claude, domain:ai |
| #3554 bug(equality): Windows publish-equality misclassifies missing flock as contention and reports success | yes | implementation/test/fix language | bug, cat:harness, domain:workstations, machine:multi, status:plan-approved, gate:completeness |
| #3571 equality/reconcile tooling gaps on ace-win-1: junction-following restore wiped canonical skills; Windows host-identity + flock gaps | yes | implementation/test/fix language | cat:operations, domain:workstations, status:plan-approved, gate:completeness, lane:claude |
| #3585 phone-media: EXIF-date organizer + cross-phone dedupe | no | implementation/test/fix language | priority:medium, cat:data, domain:family |

## agy

- Routing priority: highest
- Execution-ready candidates: 0
- Total routed candidates: 0

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|

