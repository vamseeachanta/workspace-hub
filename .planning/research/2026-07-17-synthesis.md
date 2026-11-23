# Weekly Research Synthesis — 2026-07-17

**Scope:** 3 nightly-domain reports this week — `standards` (07-13), `ai-tooling` (07-15), `competitor-market` (07-16) — reviewed against current `PROJECT.md`/`ROADMAP.md` state and last week's synthesis (07-10) for continuity.

## Action Table

| Finding | Impact | Action | Status |
|---------|--------|--------|--------|
| Standards+competitor theses converge for 3rd straight week: standards traceability + local/cloud autonomy + riser/mooring/jumper specificity | High | Promote to PROJECT.md ("Market Position" section) | Pending |
| OpenFAST MoorDyn VIV now in riser/mooring dynamics space — direct threat to `digitalmodel.orcaflex` | High | Create GitHub issue (case study counter, time-boxed) | Pending |
| DNV-RP-F105 (2025-26 revision) now covers jumpers/flex-loops/spools, not just free spans | High | Create GitHub issue + confirm v1.1 OrcaWave scope covers jumpers | Pending |
| OrcaFlex v11.6c ships embedded Python (external functions, post-calc actions) | High | Create GitHub issue (digitalmodel Phase 8: OrcFxAPI Python sidecar) | Pending |
| Anthropic Agent SDK multi-agent orchestration GA (May 2026) validates existing subagent architecture | High | Promote to PROJECT.md ("AI Tooling Foundation" note) | Pending |
| Claude Code 3-level agent nesting + fallback-model config (June 2026) | Medium-High | Create GitHub issue (fallback-model config for Fable 5→Opus, closes 2026-07-04 quota gap) | Pending |
| ISO 24656:2022 — first dedicated offshore wind CP standard | Medium | Create GitHub issue + audit `digitalmodel.cathodic_protection` citations | Pending |
| ABS Offshore SHM Notation — design-time → operational-time market shift | Medium | Promote to PROJECT.md (v1.2 strategic context, no v1.1 action) | Pending |
| MCP 2026-07-28 RC — Tasks extension for long-running async work | Medium | Create GitHub issue (nightly-automation migration audit) | Pending |
| API 579-1 Part 16 (FRP fitness-for-service) in development | Medium | Create GitHub issue (monitor release, no action until published) | Pending |
| SACS cloud pricing locked at $13.3K/seat, no new threat | Low | Monitor | Pending |
| ANSYS 2026 R1 stable, no R2 roadmap | Low | Monitor | Pending |
| GSD v1.40 `--minimal` (94% token reduction) | Low | Monitor (reference memory for future token-constrained subagent chains) | Pending |
| MarineHydro.jl (Julia OSS floating-hydro solver) | Low | Monitor (2-3yr horizon; backlog if v1.0 ships) | Pending |
| ISO/DIS 8351 (anode composition/testing draft) | Low | Monitor | Pending |
| Codex Remote GA (mobile approval loop) | Low | Ignore — `merge-when-clean.sh` already covers async merge checking | Pending |
| Flexcom stagnation (no 2026 features) | Low | Ignore with reason — speculative demand, not competitive urgency | Pending |

## Top 3 Insights for PROJECT.md

1. **The "Market Position" thesis has now survived three independent weekly research cycles (07-09, 07-13, 07-16) without contradiction — it should move from research-report prose into a durable PROJECT.md section.** Standards research (ISO 24656, DNV-RP-F105 expansion, ABS SHM) and competitor-market research (SACS cloud lock-in, OpenFAST OSS expansion) are converging from two entirely different domains onto the identical claim: AceEngineer's defensible position is standards traceability + local/cloud-agnostic execution + riser/mooring/jumper specificity. A finding this stable across independent research tracks is exactly the kind of signal PROJECT.md's "evolves at phase transitions" cadence exists to capture — waiting for a formal milestone boundary risks losing the thread once these reports age out of the 90-day retention window.

2. **OpenFAST's MoorDyn VIV expansion is the single highest-urgency, most time-boxed action item this week and deserves a ROADMAP.md Phase entry, not a backlog issue.** Unlike every other finding (standards drafts years from finalization, ANSYS with no roadmap, MarineHydro.jl 2-3 years out), this is free, actively funded (2026 DOE cycle), and directly targets `digitalmodel.orcaflex`'s core domain at zero cost to a prospective client. The competitor-market report already proposes concrete dates (draft by 2026-07-23, publish by 2026-08-06) — that's a scheduling commitment, which means it belongs in ROADMAP.md's Phase structure where it can be tracked against Phase 7's solver-verification-gate dependency, not left as an unscheduled GitHub issue.

3. **The Anthropic Agent SDK's GA validates workspace-hub's subagent architecture and gives a concrete, low-effort fix for the 2026-07-04 Fable 5 quota incident.** `model-routing.md`'s "automatic fallback whenever Fable is unavailable" policy was written as a manual workaround after that incident; Claude Code's June 2026 fallback-model configuration turns it into a first-class harness feature. This is worth a short "AI Tooling Foundation" note in PROJECT.md's Current State — not because the SDK changes any code today, but because it closes a documented operational gap with zero new engineering.

## Cross-Domain Connections

- **Standards ↔ Competitor-market (riser/jumper convergence):** DNV-RP-F105's 2025-26 scope expansion to jumpers/flex-loops and OpenFAST's new MoorDyn VIV capability are the same competitive surface approached from opposite directions — one tightens the regulatory bar, the other threatens to commoditize it for free. The recommended OrcaWave case study should explicitly cite the *revised* DNV-RP-F105 (not the pre-2025 free-span-only version) as proof OpenFAST's generic VIV modeling cannot substitute for jumper-specific standards compliance.
- **AI-tooling ↔ ROADMAP backlog (Phase 999.4/999.5):** The Anthropic Agent SDK's hierarchical (3-level) agent spawning and the MCP Tasks extension are not abstract ecosystem news — they're the exact infrastructure the currently-backlogged Phase 999.4 ("Extend Autoresearch to Agent & Template Definitions") and 999.5 ("High-Iteration Autoresearch") phases assume will exist. Both backlog phases can now cite official SDK/MCP support as de-risking evidence when promoted via `$gsd-review-backlog`.
- **AI-tooling ↔ model-routing.md:** Fallback-model GA directly closes a gap the rule file currently papers over with policy language ("Opus = automatic fallback whenever Fable is unavailable... a policy, not an incident"). Once implemented in harness config, that sentence becomes enforced by tooling rather than by agent discipline.
- **Standards (ABS SHM) ↔ Competitor-market (SACS/ANSYS bundling real-time monitoring):** Both reports independently flag the same v1.2-horizon question — clients moving from "give me a safety factor" to "tell me when my design degrades in the field." Neither report treats it as v1.1-urgent, but naming it once in both places (rather than twice, separately) avoids the synthesis re-discovering it next week.

## Detailed Action Items

- [ ] Promote: "Market Position" section → PROJECT.md — three-week-stable thesis (standards traceability + local/cloud-agnostic autonomy + riser/mooring/jumper specificity), citing ISO 24656:2022, DNV-RP-F105 revision, ABS SHM Notation, SACS cloud pricing, and OpenFAST MoorDyn VIV as the evidentiary base; reference live `calc-citation-contract.md` DNV-OS-E301 pilot as proof-in-hand
- [ ] Promote: "AI Tooling Foundation" note → PROJECT.md Current State — Agent SDK GA validates subagent architecture; note fallback-model config as the fix for the 2026-07-04 Fable 5 quota incident
- [ ] Issue (high priority): `workspace-hub` — "OpenFAST MoorDyn VIV counter case study: publish OrcaWave riser/jumper analysis citing DNV-RP-F105 (revised) by 2026-08-06, draft by 2026-07-23" — recommend as ROADMAP.md Phase entry given the explicit date commitment, not a backlog issue
- [ ] Issue: `digitalmodel` — "DNV-RP-F105 scope expansion (jumpers/flex-loops/spools): confirm v1.1 OrcaWave automation covers jumpers or risers-only; update citation sidecars if in scope"
- [ ] Issue: `digitalmodel` — "OrcaFlex v11.6c embedded Python sidecar integration — scope Phase 8: parametric update → OrcFxAPI Python call → result extraction, depends on Phase 7 solver-verification gate"
- [ ] Issue: `workspace-hub` — "Claude Code fallback-model configuration: set Opus 4.8 as automatic Fable 5 fallback in harness config, closing 2026-07-04 quota-death gap per model-routing.md"
- [ ] Issue: `digitalmodel` — "ISO 24656:2022 marine CP audit: verify `digitalmodel.cathodic_protection` cites ISO 24656 (not ISO 12473) for offshore wind/floating-structure work"
- [ ] Issue: `workspace-hub` — "MCP 2026-07-28 Tasks extension readiness audit: evaluate migrating `scripts/nightly/` detached-run automation to MCP-native async tasks once RC stabilizes"
- [ ] Issue: `digitalmodel` — "API 579-1 Part 16 (FRP fitness-for-service) tracking: monitor 2026 publication, scope `ffs_composite` module only if client demand emerges"
- [ ] Monitor: ANSYS 2026 R2 announcement (H2 2026) for expanded Mechanical API / offshore hydrodynamics surface
- [ ] Monitor: SACS/OrcaFlex Q3-Q4 2026 licensing announcements — reassess local-execution differentiator if OrcaFlex shifts toward cloud-primary
- [ ] Monitor: MCP 2026-07-28 RC stability through Q3 before committing to Tasks-extension migration
- [ ] Monitor: MarineHydro.jl toward v1.0/production readiness — file backlog partnership issue only when it ships
- [ ] Defer: GSD v1.40 `--minimal` flag — not for main-session harness; keep as a reference memory pointer for future token-constrained subagent epics
