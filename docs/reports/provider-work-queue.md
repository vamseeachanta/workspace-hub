# Provider work queue

Generated: 2026-05-02T21:20:07.142569Z
Current week: 2026-W18
Recommended provider order: gemini, codex, claude

Execution-ready means the issue already carries `status:plan-approved` or an explicit agent label.

## claude

- Routing priority: high
- Execution-ready candidates: 5
- Total routed candidates: 166

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2540 epic(llm-wiki): overnight Elements corpus planning wave after #2536 | yes | strategy/workflow/architecture language | priority:high, cat:data-pipeline, domain:knowledge-management, status:plan-approved |
| #2510 feat(cad): build Python layout/CAD automation demo for chip/package geometries | yes | strategy/workflow/architecture language | priority:medium, cat:engineering, cat:tooling, status:plan-approved, domain:semiconductor, domain:chip-design |
| #2559 feat(acma-codes): promote OCIMF Tandem preview into LLM-wiki source summary | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:documentation, status:plan-approved |
| #2566 test(naval-arch): full CI and package validation for yaw and rudder-stock sweep workflows | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:engineering-calculations, domain:hydrodynamics, domain:naval-architecture, status:plan-approved |
| #2568 feat(naval-arch): preliminary turning-circle and tactical-diameter estimator input workflow | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:engineering-calculations, domain:hydrodynamics, domain:naval-architecture, status:plan-approved |
| #2431 Compliance alert: W17 — 20% (critical) | no | strategy/workflow/architecture language | priority:high, priority:critical, compliance-alert |
| #2517 Compliance alert: W18 — 42% (high) | no | strategy/workflow/architecture language | priority:high, priority:medium, priority:critical, compliance-alert |
| #2519 feat(hermes): orchestrate AI provider usage and workstation dispatch | no | strategy/workflow/architecture language | enhancement, cat:ai-orchestration, cat:harness, priority:critical, domain:ai-orchestration, domain:workstations |

## codex

- Routing priority: highest
- Execution-ready candidates: 11
- Total routed candidates: 32

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2269 feat(openfoam): standardize ESI v2312 baseline workflow and validation | yes | existing codex agent label | enhancement, priority:high, cat:engineering, cat:documentation, status:working, machine:dev-secondary |
| #2346 feat(gtm): prospect-data customized-demo pipeline — 48hr turnaround + pre-staged vessel templates | yes | existing codex agent label | priority:high, cat:engineering, domain:gtm, status:working, agent:codex, status:plan-approved |
| #2364 feat(knowledge): execute Batch Pack 1 to promote API/standards-portal metadata into thin wiki domains | yes | existing codex agent label | enhancement, priority:high, cat:documentation, domain:knowledge-management, status:working, agent:codex |
| #2368 feat(knowledge): generate faceted portal pages for large LLM-wiki domains | yes | existing codex agent label | enhancement, priority:high, cat:documentation, domain:knowledge-management, status:working, agent:codex |
| #2373 feat(knowledge): execute Batch Pack 4 for non-ACMA standards summary promotion | yes | existing codex agent label | enhancement, priority:high, cat:data-pipeline, domain:knowledge-management, status:working, agent:codex |
| #2402 feat(doc-intel): build embeddings index L2+L3 + query CLI (single authoritative tier) | yes | existing codex agent label | enhancement, priority:high, cat:data-pipeline, domain:document-intelligence, status:working, agent:codex |
| #2270 feat(blender): standardize headless baseline workflow and smoke render validation | yes | existing codex agent label | enhancement, priority:medium, cat:engineering, cat:documentation, status:working, machine:dev-secondary |
| #2272 test(portability): add repeatable OpenFOAM and Blender smoke verification | yes | existing codex agent label | enhancement, priority:medium, cat:engineering, cat:harness, status:working, machine:multi |

## gemini

- Routing priority: highest
- Execution-ready candidates: 0
- Total routed candidates: 2

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2295 WRK: 2025 TX franchise No Tax Due + PIR — SKEstates and AceEngineer | no | research/triage/audit language | enhancement, priority:high, cat:personal-finance, domain:tax-preparation |
| #2501 chore(planning): #2105 governance-lock — handoff vs live-state discrepancy | no | research/triage/audit language | priority:medium, cat:documentation, cat:harness |

