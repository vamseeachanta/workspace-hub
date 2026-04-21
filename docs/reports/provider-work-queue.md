# Provider work queue

Generated: 2026-04-21T13:20:07.681040Z
Current week: 2026-W17
Recommended provider order: codex, gemini, claude

Execution-ready means the issue already carries `status:plan-approved` or an explicit agent label.

## claude

- Routing priority: high
- Execution-ready candidates: 9
- Total routed candidates: 160

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2348 triage: promote #1707/#1708/#1709 from review-backlog — live scanner has ToS/rate-limit exposure | yes | strategy/workflow/architecture language | bug, priority:high, domain:gtm, status:plan-approved |
| #2408 feat(release-readiness): workspace-hub-only model-release readiness contract and upgrade playbook | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:ai-orchestration, cat:harness, domain:release-management, status:plan-approved |
| #2320 chore(skills): mine session logs for dead-skill candidates — usage-signal input to #2280 weekly audit | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:skills, domain:skills, status:plan-approved |
| #2322 chore(rules): promote binary-checkable .claude/rules/*.md prose to Level 2 scripts per enforcement gradient | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:harness, domain:agent-discipline, status:plan-approved |
| #2323 feat(review): single-command cross-AI plan-review fan-out (Claude + Codex + Gemini) with disagreement capture | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:ai-orchestration, domain:ai-orchestration, status:plan-approved |
| #2324 chore(memory): curate MEMORY.md index before 200-line truncation — consolidate stale project_* and feedback_* | yes | strategy/workflow/architecture language | priority:medium, cat:maintenance, domain:memory, status:plan-approved |
| #2403 feat(doc-intel): embeddings model-selection spike — BGE-M3 / Voyage / text-embedding-3-large | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:data-pipeline, cat:research, domain:document-intelligence, status:plan-approved |
| #2327 digitalmodel: CadQuery spike for parametric offshore geometry generation | yes | strategy/workflow/architecture language | priority:low, cat:engineering, cat:research, status:plan-approved |

## codex

- Routing priority: highest
- Execution-ready candidates: 0
- Total routed candidates: 38

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2167 test(knowledge): build session-read coherence golden fixture suite for alias, symbolic, and missing-path cases | no | implementation/test/fix language | enhancement, priority:medium, cat:documentation, cat:harness |
| #2169 feat(operations): define Windows licensed-tool probe adapter contract for readiness bundles | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |
| #2171 test(reporting): add end-to-end weekly publication smoke scenarios for latest/history bundle assembly | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |
| #2173 feat(knowledge): wire provider-session ecosystem audit into weekly registry build manifest and publication bundle | no | implementation/test/fix language | enhancement, priority:medium, cat:documentation, cat:harness |
| #2175 test(operations): add fixture-backed OrcaFlex Windows probe smoke matrix across readiness states | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |
| #2176 test(operations): add OrcaWave diffraction smoke fixtures and AQWA install-vs-usable classification tests | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |
| #2178 feat(reporting): add bundle checksum manifest and tree-diff helper for assembled publication outputs | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |
| #2179 feat(validation): add weekly unresolved session-read regression gate with baseline and fail budget | no | implementation/test/fix language | enhancement, priority:medium, cat:documentation, cat:harness |

## gemini

- Routing priority: highest
- Execution-ready candidates: 1
- Total routed candidates: 2

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2346 feat(gtm): prospect-data customized-demo pipeline — 48hr turnaround + pre-staged vessel templates | yes | research/triage/audit language | priority:high, cat:engineering, domain:gtm, status:plan-approved |
| #2295 WRK: 2025 TX franchise No Tax Due + PIR — SKEstates and AceEngineer | no | research/triage/audit language | enhancement, priority:high, cat:personal-finance, domain:tax-preparation |

