# Provider work queue

Generated: 2026-04-22T05:20:06.563573Z
Current week: 2026-W17
Recommended provider order: codex, gemini, claude

Execution-ready means the issue already carries `status:plan-approved` or an explicit agent label.

## claude

- Routing priority: high
- Execution-ready candidates: 12
- Total routed candidates: 170

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2348 triage: promote #1707/#1708/#1709 from review-backlog — live scanner has ToS/rate-limit exposure | yes | strategy/workflow/architecture language | bug, priority:high, domain:gtm, status:plan-approved |
| #2408 feat(release-readiness): workspace-hub-only model-release readiness contract and upgrade playbook | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:ai-orchestration, cat:harness, domain:release-management, status:plan-approved |
| #2433 chore(ci-health): worldenergydata main CI — 22+ collection errors blocking 5 Dependabot PRs (#329-#333) | yes | strategy/workflow/architecture language | priority:high, cat:infrastructure, status:plan-approved |
| #2442 chore(ci-health): assethold CI — python-tests.yml never green since 2025-09-28 (7 months); YAML parse + deprecated actions | yes | strategy/workflow/architecture language | priority:high, cat:infrastructure, status:plan-approved |
| #2320 chore(skills): mine session logs for dead-skill candidates — usage-signal input to #2280 weekly audit | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:skills, domain:skills, status:plan-approved |
| #2322 chore(rules): promote binary-checkable .claude/rules/*.md prose to Level 2 scripts per enforcement gradient | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:harness, domain:agent-discipline, status:plan-approved |
| #2323 feat(review): single-command cross-AI plan-review fan-out (Claude + Codex + Gemini) with disagreement capture | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:ai-orchestration, domain:ai-orchestration, status:plan-approved |
| #2324 chore(memory): curate MEMORY.md index before 200-line truncation — consolidate stale project_* and feedback_* | yes | strategy/workflow/architecture language | priority:medium, cat:maintenance, domain:memory, status:plan-approved |

## codex

- Routing priority: highest
- Execution-ready candidates: 0
- Total routed candidates: 28

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2188 test(reporting): add mixed-state golden fixture bundles for licensed-win probe reporting | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |
| #2189 test(reporting): lock deterministic shared-asset canonical placement across latest/history/staged bundles | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |
| #2190 feat(reporting): add manifest-indexed pruning for orphaned shared assets after successful publication | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |
| #2194 feat(reporting): emit cross-tool reporter delta artifacts against previous weekly baseline | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |
| #2195 test(reporting): add publication recovery state-machine transition suite for staged/gated/recoverable flows | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |
| #2199 feat(claude): validate hook wiring and backfill session_id parity for historical provider-audit coverage | no | implementation/test/fix language | enhancement, priority:medium, cat:harness |
| #2200 test(operations): add wrapper-level subprocess smoke coverage for provider-session-ecosystem-audit.sh | no | implementation/test/fix language | enhancement, priority:medium, cat:harness |
| #2202 feat(operations): extend readiness bundle schema for additional canonical check evidence contracts | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |

## gemini

- Routing priority: highest
- Execution-ready candidates: 1
- Total routed candidates: 2

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2346 feat(gtm): prospect-data customized-demo pipeline — 48hr turnaround + pre-staged vessel templates | yes | research/triage/audit language | priority:high, cat:engineering, domain:gtm, status:plan-approved |
| #2295 WRK: 2025 TX franchise No Tax Due + PIR — SKEstates and AceEngineer | no | research/triage/audit language | enhancement, priority:high, cat:personal-finance, domain:tax-preparation |

