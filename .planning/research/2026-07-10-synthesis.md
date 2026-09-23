# Weekly Research Synthesis — 2026-07-10

**Scope note:** Only 1 of the expected ~4 nightly-domain research reports (competitor-market) was provided in this session. PROJECT.md references "nightly 4-domain research automation" — technical, regulatory, data-source, and competitor-market tracks are the likely set. This synthesis covers competitor-market only; the other 3 domains should be pulled in and re-synthesized if they exist for this week.

## Action Table

| Finding | Impact | Action | Status |
|---------|--------|--------|--------|
| SACS V12 cloud parallelization (Azure, 10x+ speedup on load cases) threatens local-license pricing model | High | Promote to PROJECT.md | Pending |
| OpenFAST OSS expansion into floating/marine turbine hydro-servo-elastic modeling | High | Promote to PROJECT.md | Pending |
| ANSYS 2026 R1 GPU morphing + Sherlock reliability bundling raises compute-heavy competitive bar | Medium | Monitor | Pending |
| Sesam Manager consolidation (DNV unified UI, 30+ modules) — market leader repositioning, not a direct feature threat | Medium | Monitor | Pending |
| Flexcom v8 stable, no 2026 feature announcements — Wood Group consolidating not innovating | Low | Create GitHub issue (probe wrapper/bridge demand) | Pending |

## Top 3 Insights for PROJECT.md

1. **Competitive positioning should be explicit, not implicit.** The report converges on a single differentiator across all four competitor threats (SACS, ANSYS, OpenFAST, Sesam): standards traceability + local/cloud-agnostic autonomy + riser/mooring specificity. PROJECT.md currently has no "Market Position" or "Competitive Differentiation" section — this is the first research cycle to produce a synthesized thesis worth codifying rather than leaving in a dated report that will fall out of the 90-day retention window. Ties directly to the already-shipped `calc-citation-contract.md` (DNV-OS-E301 pilot) — the report validates that citation sidecars are a market-facing asset, not just an internal governance artifact.

2. **OpenFAST is the highest-priority OSS threat and needs a concrete counter-artifact, not just awareness.** Unlike SACS/ANSYS (commercial, pricing-model threats), OpenFAST is free and actively expanding into marine/floating-turbine territory — the only threat that could erode `digitalmodel`'s OrcaWave positioning at zero cost to a prospective client. A published riser/mooring case study is the recommended counter and is concrete enough to become a Phase entry, not just a backlog note.

3. **Flexcom's stagnation is an outreach opportunity, not just a monitoring item.** This is the one finding in the report that suggests inbound business development rather than internal engineering work — Flexcom's stable-but-non-innovating trajectory under Wood Group means its user base (deep riser domain expertise, likely underserved by iteration speed) is a plausible warm lead pool. This connects to the existing outreach patterns in memory (`feedback_vamsee_technical_outreach_email_style`) rather than requiring new process.

## Cross-Domain Connections

- **Competitor-market ↔ v1.1 OrcaWave Automation milestone (ROADMAP.md Phase 7):** The SACS cloud-parallelization and OpenFAST findings both bear directly on the in-flight OrcaWave automation milestone (Phase 7, solver verification gate, 0/3 plans complete). The batch report generation and OrcaFlex integration target features in PROJECT.md's v1.1 milestone are exactly the capabilities that would let AceEngineer credibly claim "cloud-agnostic, standards-traceable" positioning against SACS — the research and the active roadmap phase are validating the same bet from different directions.
- **Competitor-market ↔ calc-citation-contract rule:** The report's recommended differentiator ("standards-to-calc traceback") is not aspirational — it's already a live, enforced rule (`.claude/rules/calc-citation-contract.md`, DNV-OS-E301 pilot at [#2685](https://github.com/vamseeachanta/workspace-hub/issues/2685)). This is a case where existing engineering governance work has accidentally produced the market differentiator the research recommends — worth naming explicitly in any external-facing positioning material.

## Detailed Action Items

- [ ] Promote: "Market Position" section to PROJECT.md — competitive thesis (standards traceability + local/cloud-agnostic autonomy + riser/mooring specificity) vs. SACS/ANSYS/OpenFAST/Sesam, referencing the live `calc-citation-contract.md` pilot as proof-in-hand
- [ ] Issue: `workspace-hub` — "Publish 1 OrcaWave riser/mooring case study vs. OpenFAST to demonstrate riser-specific insight OpenFAST cannot deliver" (per source report's recommended action, not yet filed)
- [ ] Issue: `digitalmodel` — "Explore Flexcom results bridge/wrapper for parametric bulk runs — probe existing Flexcom-user relationships for demand before scoping" (per source report's recommended action, not yet filed)
- [ ] Monitor: OrcaFlex 2026-Q3/Q4 licensing announcements (SACS cloud pricing does not yet include OrcaFlex-equivalent capability — reassess when Q3/Q4 lands)
- [ ] Monitor: ANSYS 2026 R1 Mechanical API expansion details (report notes API scope was announced but not detailed — revisit when ANSYS publishes specifics)
- [ ] Gap: confirm whether technical/regulatory/data-source research tracks ran this week (nightly 4-domain automation per PROJECT.md) — if reports exist under `docs/reports/` but weren't surfaced to this session, re-run synthesis including them
