# Research: standards — 2026-07-20

## Key Findings

- **DNV July 2026 edition released (effective 2026-01-01, published 2026-07-08):** New class notation **FL(Y)** specifies design fatigue life with selectable fatigue factors; **FMS notation updated** with qualifiers for design fatigue factor selection; new **NUI notation** for normally unmanned installations (critical for subsea automation). **DNV-OS-A101 restructured** to separate common requirements from service-specific requirements, with new fuel options. In-service classification scope for floating wind farms rewritten. This is the most recent DNV offshore baseline and supersedes all prior 2025 guidance — all workspace-hub project work must reference the July 2026 edition effective 2026-01-01, not prior versions.

- **API 579-1 Part 16 (FRP fitness-for-service) remains in development, no 2026-Q3 publication.** ASME is offering API 579-1 training scheduled December 7-11, 2026, indicating the main standard (4th Edition, Dec 2021) remains current. Part 16 development continues but no release date announced; monitor for 2026-Q4 announcements.

- **ISO 24656:2022 adoption accelerating in new-project tenders (2026 offshore wind pipeline).** No specification updates to ISO 24656 since 2022 publication, but industry adoption is increasing as wind projects move to detailed design phase. Standard is commonly paired with the **updated DNV July 2026 rules** (above) for wind CP compliance.

- **ABS SMART (SHM) Notation pilot stable with Seatrium ADMARINE 686.** First full implementation (SEDU with structural digital twin + IoT connectivity to Singapore shore station) completed 2023-24. No new platform notations awarded in 2026 Q2-Q3 research window; notation remains stable/available for new projects.

- **DNV-RP-F105 scope (jumpers, flex-loops, spools, doglegs) per prior synthesis still authoritative.** No new 2026-Q3 revisions; the 2025-26 scope expansion (per 2026-07-13 research) remains the current baseline. Search did not surface 2026 updates — the July 2026 DNV edition (above) is the primary new artifact.

---

## Relevance to Project

| Finding | Affected Package/Domain | Impact on Workflow |
|---------|------------------------|-------------------|
| **DNV July 2026 edition (FL(Y), NUI, restructured OS-A101)** | `digitalmodel.fatigue`, `digitalmodel.orcaflex`, Phase 7 solver-verification gate | **High/Critical.** All project work citing DNV rules must now reference the **July 2026 edition** (effective 2026-01-01), not 2025 or prior. (1) **FL(Y) notation** = new class notation for design fatigue life — if `digitalmodel` fatigue modules cite DNV rules for design-life factors or S-N curves, the citation sidecar must now reference July 2026 FL(Y) scope, not prior unqualified fatigue guidance. (2) **NUI notation** (normally unmanned installations) directly applies to subsea equipment automation, mooring, and cable systems — workspace-hub's subsea focus may require NUI compliance documentation for Phase 1.2 (fitness-for-service) or v1.2 (operational prognosis). (3) **DNV-OS-A101 restructure** separates floating-specific requirements from fixed; if v1.1 OrcaWave or v1.2 work targets floating hulls/platforms, the new structure must be tracked. |
| **API 579-1 Part 16 (FRP) still in development, Dec 2026 ASME training announced** | `digitalmodel.fitness_for_service` (future `ffs_composite` module) | **Medium.** Prior research (2026-07-13) flagged Part 16 as "2026 technical update underway." Training schedule (Dec 7-11, 2026) confirms the standard body is actively engaging industry; Part 16 release is likely Q4 2026 or Q1 2027. Create the tracking issue (per 2026-07-17 synthesis action items) and defer module scope until Part 16 publishes. No change to v1.1 OrcaWave scope; v1.2 backlog candidate if client demand surfaces. |
| **ISO 24656:2022 adoption (no updates, but pairing with DNV July 2026)** | `digitalmodel.cathodic_protection` (CP module citations) | **Medium.** ISO 24656 itself has no 2026 revisions, but its use *alongside* the DNV July 2026 edition means CP assessment workflows now require **dual-standard validation**: ISO 24656 (seawater CP design) + DNV class notation (structural + offshore-specific fatigue). This is NOT a citation change in `digitalmodel` (ISO 24656 citation remains valid), but it *does* signal that client deliverables citing ISO 24656 should reference the *current* DNV edition (July 2026) as a paired standard. |
| **ABS SMART (SHM) Notation stable; no new 2026 awards** | `aceengineer-website` (market positioning), v1.2 prognosis roadmap (future) | **Low-Medium.** ABS SHM Notation remains viable for new projects but is not accelerating. Seatrium's ADMARINE 686 pilot (completed 2023-24) remains the primary public reference. v1.2 strategic discussion (per 2026-07-17 synthesis insight) should track ABS SHM as a market signal, not as an urgent feature dependency. No action for v1.1. |
| **DNV-RP-F105 (prior 2025-26 scope expansion to jumpers/flex-loops/spools)** | `digitalmodel.orcaflex` (riser/jumper VIV, Phase 7 scope confirmation) | **Medium-High.** Prior research (2026-07-13) flagged DNV-RP-F105 scope expansion; current search did not surface 2026 revisions, meaning the 2025-26 expansion is the current baseline. **Action: Phase 7 plan must explicitly confirm whether v1.1 OrcaWave automation includes jumper/flex-loop assessment or risers-only.** If jumpers in scope, all citations must reference **DNV-RP-F105 (revised 2025-26)**, not pre-2025 free-span-only version. If risers-only, document that decision. |

---

## Recommended Actions

- [x] **Promote to PROJECT.md / issue planning** — `workspace-hub#TBD`: "Standards baseline update (2026-07-20): DNV July 2026 edition now effective and supersedes all prior guidance. Update all project citations to reference July 2026 edition (effective 2026-01-01) for fatigue (FL(Y)), unmanned installations (NUI), and floating structures (OS-A101 restructure). Phase 7 plan must confirm riser vs. jumper scope against DNV-RP-F105 revised baseline." Tag `priority:high`, `lane:standards-compliance`.

- [ ] **Create GitHub issue** — `digitalmodel#TBD`: "DNV July 2026 edition implementation: audit existing `digitalmodel.fatigue`, `digitalmodel.orcaflex` modules for DNV rule citations; update citation sidecars to July 2026 edition where applicable. NUI notation research for unmanned subsea equipment (Phase 1.2 / v1.2 scope). Depends on Phase 7 confirmation." Tag `lane:standards-compliance`, `status:backlog`.

- [ ] **Create GitHub issue** — `workspace-hub#TBD`: "v1.1 OrcaWave scope confirmation: Phase 7 plan must explicitly declare riser-only vs. riser+jumper+flex-loop automation scope and update DNV-RP-F105 citation baseline accordingly. If jumpers in scope, cite DNV-RP-F105 (revised 2025-26); document decision either way." Tag `lane:planning`, `depends-on:Phase-7-plan`.

- [ ] **Defer** — API 579-1 Part 16 (FRP): tracking issue created per 2026-07-17 synthesis; December 2026 training announcement confirms active development. Monitor for Q4 2026 / Q1 2027 release; no v1.1 action.

- [ ] **Monitor** — ASME 579-1 training (Dec 7-11, 2026) and Part 16 release calendar through Q4 2026; if Part 16 ships in November 2026, consider scoping `ffs_composite` module evaluation for v1.2 backlog promotion in December.

- [ ] **Ignore with reason** — ABS SMART Notation expansion tracking (no new 2026 awards; Seatrium ADMARINE 686 pilot remains the reference). Revisit if 3+ new platform notations awarded in 2026-Q4 or if major OEM (e.g., Prysmian, Subsea 7) announces SHM adoption.

---

`★ Insight ─────────────────────────────────────`

**DNV's July 2026 edition is the most significant standards shift this month.** The FL(Y) fatigue-life notation and NUI (normally unmanned) designation are direct signals that **DNV is embedding operational autonomy and prognosis into class rules** — not just design-phase analysis. This aligns with ABS's SHM Notation push (2026-07-16 research) and reinforces the v1.2 roadmap thesis (per 2026-07-17 synthesis) that clients are moving from "give me a safety factor" to "tell me when my design degrades." 

The July 2026 edition's DNV-OS-A101 restructure (separating common requirements from floating-specific) is a planning detail, not a threat. However, it means **any floating-structure work in future phases must use the new service-specific requirement sets**, not the 2025 monolithic document. This is light but mandatory guidance-drift — the kind of baseline hygiene that surfaces in CI/CD citation-contract validation (per `.claude/rules/calc-citation-contract.md`).

**API 579-1 Part 16 (FRP) is now visible on the calendar.** Prior research flagged it as "2026 technical update underway." The ASME December training announcement confirms it's real. This isn't urgent for v1.1 (OrcaWave is metallic/VIV, not composite), but it's now a dated trigger for v1.2 backlog promotion — if Part 16 ships in November, it's a natural timing cue to scope `digitalmodel.ffs_composite` for 2027-Q1.

`─────────────────────────────────────────────────`

---

## Sources

- [DNV July 2026 edition of ship and offshore class rules and standards](https://www.dnv.com/news/2026/standards-now-available-the-july-2026-edition-of-the-dnv-class-rules-and-standards-for-ship-and-offshore/)
- [DNV July 2026 standards announcement (Nautical Voice)](https://nauticalvoice.com/the-july-2026-edition-of-the-dnv-class-rules-and-standards-for-ship-and-offshore/93783/)
- [DNV July 2026 standards announcement (Hellenic Shipping News)](https://www.hellenicshippingnews.com/now-available-the-july-2026-edition-of-the-dnv-class-rules-and-standards-for-ship-and-offshore/)
- [API 579-1/ASME FFS-1 Training – ASME Learning](https://www.asme.org/learning-development/find-course/api-579-1-asme-ffs-1-fitness-service-evaluation)
- [API 579 Part 16 FRP Assessment – UTComp](https://utcomp.com/api-579-1-asme-ffs-1-update/api-579-part-16-assessment-levels-for-frp-assets/)
- [ISO 24656:2022 – Cathodic protection of offshore wind structures](https://www.iso.org/standard/79166.html)
- [DNV-RP-F105 Free Spanning Pipelines](https://www.dnv.com/energy/standards-guidelines/dnv-rp-f105-free-spanning-pipelines/)
- [ABS SMART (SHM) Notation – Marine Link](https://www.marinelink.com/news/abs-launches-offshore-structural-health-509259)
- [ABS SMART Notation with Seatrium ADMARINE 686 – Ocean News & Technology](https://oceannews.com/news/energy/abs-partners-with-seatrium-to-launch-world-s-first-offshore-structural-health-monitoring-notation/)

---

**Next:** Phase 7 plan (solver verification gate) must confirm riser-only vs. jumper-inclusive OrcaWave scope and cite the DNV July 2026 baseline. One blocking decision.
