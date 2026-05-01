# Provider work queue

Generated: 2026-05-01T09:20:47.335387Z
Current week: 2026-W18
Recommended provider order: gemini, codex, claude

Execution-ready means the issue already carries `status:plan-approved` or an explicit agent label.

## claude

- Routing priority: high
- Execution-ready candidates: 9
- Total routed candidates: 163

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2540 epic(llm-wiki): overnight Elements corpus planning wave after #2536 | yes | strategy/workflow/architecture language | priority:high, cat:data-pipeline, domain:knowledge-management, status:plan-approved |
| #2571 feat(naval-arch): B1528 SIROCCO time-trace benchmark report with rudder inflow feedback | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:engineering-calculations, domain:hydrodynamics, domain:visualization, domain:naval-architecture |
| #2490 chore(ci-health): digitalmodel Quality Gates coverage gate blocker (split from #2441) | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:infrastructure, status:plan-approved |
| #2510 feat(cad): build Python layout/CAD automation demo for chip/package geometries | yes | strategy/workflow/architecture language | priority:medium, cat:engineering, cat:tooling, status:plan-approved, domain:semiconductor, domain:chip-design |
| #2541 feat(llm-wiki): plan curated SESA LNG corpus extraction from Elements | yes | strategy/workflow/architecture language | priority:medium, cat:data-pipeline, domain:marine, domain:knowledge-management, status:plan-approved |
| #2544 feat(llm-wiki): scout Woodfibre LNG corpus for bounded extraction candidates | yes | strategy/workflow/architecture language | priority:medium, cat:data-pipeline, domain:marine, domain:knowledge-management, status:plan-approved |
| #2566 test(naval-arch): full CI and package validation for yaw and rudder-stock sweep workflows | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:engineering-calculations, domain:hydrodynamics, domain:naval-architecture, status:plan-approved |
| #2567 feat(naval-arch): standards-backed steering gear and rudder-stock design checks | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:engineering-calculations, domain:hydrodynamics, domain:naval-architecture, status:plan-approved |

## codex

- Routing priority: highest
- Execution-ready candidates: 12
- Total routed candidates: 35

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2269 feat(openfoam): standardize ESI v2312 baseline workflow and validation | yes | existing codex agent label | enhancement, priority:high, cat:engineering, cat:documentation, status:working, machine:dev-secondary |
| #2346 feat(gtm): prospect-data customized-demo pipeline — 48hr turnaround + pre-staged vessel templates | yes | existing codex agent label | priority:high, cat:engineering, domain:gtm, status:working, agent:codex, status:plan-approved |
| #2364 feat(knowledge): execute Batch Pack 1 to promote API/standards-portal metadata into thin wiki domains | yes | existing codex agent label | enhancement, priority:high, cat:documentation, domain:knowledge-management, status:working, agent:codex |
| #2368 feat(knowledge): generate faceted portal pages for large LLM-wiki domains | yes | existing codex agent label | enhancement, priority:high, cat:documentation, domain:knowledge-management, status:working, agent:codex |
| #2373 feat(knowledge): execute Batch Pack 4 for non-ACMA standards summary promotion | yes | existing codex agent label | enhancement, priority:high, cat:data-pipeline, domain:knowledge-management, status:working, agent:codex |
| #2402 feat(doc-intel): build embeddings index L2+L3 + query CLI (single authoritative tier) | yes | existing codex agent label | enhancement, priority:high, cat:data-pipeline, domain:document-intelligence, status:working, agent:codex |
| #2462 feat(digitalmodel): repo-wide operator map and canonical routing surfaces beyond OrcaWave/OrcaFlex | yes | existing codex agent label | enhancement, priority:high, cat:engineering, cat:documentation, domain:repo-organization, status:working |
| #2270 feat(blender): standardize headless baseline workflow and smoke render validation | yes | existing codex agent label | enhancement, priority:medium, cat:engineering, cat:documentation, status:working, machine:dev-secondary |

## gemini

- Routing priority: highest
- Execution-ready candidates: 0
- Total routed candidates: 2

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2295 WRK: 2025 TX franchise No Tax Due + PIR — SKEstates and AceEngineer | no | research/triage/audit language | enhancement, priority:high, cat:personal-finance, domain:tax-preparation |
| #2501 chore(planning): #2105 governance-lock — handoff vs live-state discrepancy | no | research/triage/audit language | priority:medium, cat:documentation, cat:harness |

