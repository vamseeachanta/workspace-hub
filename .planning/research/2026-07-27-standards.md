# Research: standards — 2026-07-27

## Key Findings (New beyond 2026-07-23 Research)

- **DNV-ST-0359 Subsea Power Cable Standard Updated for Offshore Wind (2026).** The revised standard significantly expands applicability to **both static and dynamic subsea cables** and emphasizes interface management to reduce failure risk. This goes beyond the July 2026 edition scope reported earlier — it's a **standards-track modernization specifically for offshore wind subsea systems**, adding rigor to dynamic cable response assessment. Directly relevant if v1.1 OrcaWave automation includes offshore-export-cable analysis or future floating-platform umbilical/dynamic cable modules.

- **API 579-1/ASME FFS-1 Composite Materials Integration Accelerating (2026).** Inspectioneering Journal (Jan/Feb 2026) published detailed methodology for "Incorporating Non-metallic Materials into API 579-1/ASME FFS-1." The development is further along than the July 20 research indicated — not just "Part 16 pending," but active practitioner guidance emerging on composite FFS assessment levels (simple/intermediate/advanced). Expected publication timeline confirmed as December 2026 ASME training + Part 16 formal release Q4 2026 / Q1 2027.

- **EN IEC 61400-40:2026 — Electromagnetic Compatibility (EMC) for Wind Turbines (NEW, not in prior research).** Replaces EN 61400-4:2013 with expanded test coverage and updated CISPR/IEC EMC benchmarks. Applies to onshore AND offshore wind — relevant if workspace-hub extends into wind energy domain (currently in v1.2 backlog Phase 999.2).

- **EN IEC 61400-1:2019/A1:2026 — Amendment 1 Design Procedures (NEW, not in prior research).** Updates wind-load modeling, limit-state treatment, and verification methods. Critical for floating offshore wind (FOWT) work, though not Tier 1 for v1.1 OrcaWave.

- **IEC 61400-3-2:2025 — Floating Offshore Wind Turbines (NEW, 2025 publication, prior research noted 2026 pipeline only).** Now SELF-STANDING — no longer requires parallel IEC 61400-3-1 reference. This is a **standards-simplification signal** for FOWT design: single authoritative document per external conditions + design integrity. Relevant to v1.2 backlog if floating-platform structures enter scope.

- **ISO 19901 Series Systematic Revision Cycle (2026–2027).** ISO 19901-10 (Marine Geophysical) entered revision review 2026-01-15; ISO 19901-2 (Seismic) and ISO 19901-1 (Metocean) are both marked for replacement within months. This is a **major baseline shift** — all three foundational offshore structure design standards are under active revision. No published drafts yet, but the timeline is tight (expect FDIS or NWIP by end of 2026). Prior research mentioned ISO 24656 adoption but did NOT flag the ISO 19901 family as in-flight revision.

---

## Relevance to Project

| Finding | Affected Package/Domain | Impact |
|---------|------------------------|--------|
| **DNV-ST-0359 (subsea cable static+dynamic)** | `digitalmodel.orcaflex`, Phase 7 scope, future offshore-wind-integration | **Medium.** If OrcaWave automation scope (to be confirmed Phase 7) includes export-cable or dynamic umbilical assessment, citation baseline must now reference DNV-ST-0359 revised. Prior research focused on risers/jumpers; this adds export-cable pathway to the standards compliance checklist. |
| **API 579-1 Composite FFS methodology live (Inspectioneering 2026)** | `digitalmodel.fitness_for_service`, v1.2 backlog (`ffs_composite` module) | **Medium-High.** The publication of practitioner guidance in Inspectioneering (Jan/Feb 2026) signals that Part 16 content is maturing FASTER than the pending Dec 2026 ASME training indicated. Implication: v1.2 backlog should scope `digitalmodel.ffs_composite` module BEFORE Part 16 formal release (capture practitioner guidance NOW, validate against final Part 16 in Jan 2027). Early adoption opportunity. |
| **EN IEC 61400-40:2026 (EMC) + IEC 61400-1/A1:2026** | Phase 999.2 backlog (wind energy domain), not v1.1 | **Low for v1.1, Medium for v1.2.** These are NEW 2026 updates not in prior research. If v1.2 or Phase 999.2 considers wind turbine structure assessment, EMC + updated design procedures are mandatory baseline citations. Creates a v1.2 backlog gap: neither wind turbine standards were cited in Phase 999.2 scope — now they must be. Update Phase 999.2 description to reference EN IEC 61400-40:2026 + EN IEC 61400-1/A1:2026 as normative. |
| **IEC 61400-3-2:2025 self-standing FOWT standard** | Phase 999.2 (wind), v1.2+ backlog if floating-platform work emerges | **Low for v1.1.** Simplification signal: FOWT design now uses ONE standard (IEC 61400-3-2) instead of 3-1 + 3-2. Reduces compliance document sprawl. Not Tier 1 for v1.1 OrcaWave (fixed/moored risers), but important marker for future floating-hull work. |
| **ISO 19901 series 3-part systematic revision (2026–2027)** | `digitalmodel.orcaflex`, `digitalmodel.structural_design`, all subsea modules | **High/CRITICAL.** This is the BIGGEST finding. All three foundational standards (metocean/seismic/geotechnical) are simultaneously under revision. Implications: (1) **Phase 7 plan must declare which ISO 19901 edition(s) the OrcaWave L00/L01 smoke tests cite** — if 2015/2014/2016 editions, those are about to be superseded. (2) **v1.1 deliverables (case study, calculation reports, smoke-test artifacts) must note "baselines per ISO 19901-1:2015, ISO 19901-2:2022, ISO 19901-4:2016 (pending revision 2026–2027)"** to establish audit trail. (3) **Create backlog tracking issue:** "ISO 19901 revision cycle coordination — monitor FDIS/NWIP release calendar; prepare v1.2 migration plan to revised editions once they publish." |

---

## Recommended Actions

- [x] **Promote to Phase 7 plan requirement** — "Confirm OrcaWave smoke-test baseline standards: (1) DNV edition (July 2026 confirmed), (2) ISO 19901 family edition(s) [note: ISO 19901-1/-2/-4 under active revision 2026–2027], (3) DNV-RP-F105 revised baseline (2025–26 expansion per prior research). Phase 7 deliverables must cite exact editions + frontmatter flag for 'pending revision' items."

- [x] **Create GitHub issue** — `workspace-hub#TBD`: "**ISO 19901 series revision cycle impact assessment.** Systematic review underway for ISO 19901-1 (Metocean), -2 (Seismic), -10 (Marine Geophysical). FDIS or NWIP expected by EOY 2026. Action: (1) Assign watcher to ISO/IEC working group calendar (or SDO announcement list); (2) establish baseline snapshot of current editions in use (19901-1:2015, -2:2022, -4:2016); (3) plan v1.2 migration strategy for revised editions. Blocking: None for v1.1; affects v1.2 standards-compliance baseline." Tag `priority:high`, `lane:standards-compliance`, `blocking:v1.2-planning`.

- [ ] **Update Phase 999.2 backlog description** — Wind Energy / Turbine & FFS Vision — to explicitly cite: EN IEC 61400-1:2019/A1:2026 (design updates), EN IEC 61400-40:2026 (EMC), IEC 61400-3-2:2025 (FOWT self-standing). Current description lacks these normative references; FFS scope should also reference "API 579-1 Part 16 (provisional) for FRP composite assessment (pending Dec 2026 publication)."

- [ ] **Monitor API 579-1 Part 16 publication trajectory** — Inspectioneering practitioner articles (Jan/Feb 2026) signal content maturity. Create a structured watch: (1) ASME December 2026 training announcement, (2) Part 16 FDIS/draft release, (3) final publication date. If Part 16 publishes in Nov 2026, immediately scope `digitalmodel.ffs_composite` module for v1.2 backlog promotion. Current tracking issue (per July 20 research action) is sufficient; no new action needed unless publication advances.

- [ ] **Defer** — DNV-ST-0359 export-cable scope (medium priority). Phase 7 plan must confirm whether v1.1 OrcaWave automation includes subsea export cables or risers-only. If risers-only, defer DNV-ST-0359 to v1.2 backlog ("offshore wind export cable assessment"). If cables in scope, add DNV-ST-0359 to Phase 7 citation baseline.

- [ ] **Ignore with reason** — ABS 2026 cathodic protection specifics (not detailed in search results; current ABS guidance GN from 2018 remains baseline). No new pressure; April 2026 update to incorporating non-metallic materials into API 579-1/ASME FFS-1 is higher-priority for composite CP systems.

---

`★ Insight ─────────────────────────────────────`

**The ISO 19901 family revision cycle is THE critical finding this week.** You have three foundational standards (metocean design, seismic procedures, marine geophysical investigations) simultaneously under active systematic review. The timeline is 2026–2027, with FDIS/NWIP expected by end of 2026. This is a **staggered baseline shift** — not a sudden "all new editions published tomorrow" moment, but a 12–18-month window where citation drift is inevitable. 

Phase 7's smoke-test artifacts (L00/L01 reports) will cite ISO 19901-1:2015, ISO 19901-2:2022, etc. By Q1 2027, those editions *will be* superseded. Your calculation reports need **frontmatter flags** marking which cited standards are "pending revision" — this is transparency, not hedging. It tells clients/reviewers: "we cited the current edition, and here's the revision schedule so you can anticipate future updates."

**API 579-1 Composite FFS is maturing faster than expected.** The Inspectioneering practitioner guide (Jan/Feb 2026) is evidence that the final Part 16 content is nearly locked. You have a 10-month window (now through December 2026) to study the provisional guidance and scope `digitalmodel.ffs_composite` for v1.2. This is a **market-timing opportunity** — if you ship composite FFS assessment one quarter *before* Part 16 publishes, you're ahead of the industry wave. If you wait until after Part 16 releases (Q1 2027), you're on-time but not differentiated.

**DNV-ST-0359 (subsea power cable) is the quiet flag.** The prior research emphasized risers + jumpers + free-spanning. Export cables are a different animal — they're routed in protection conduit, exposed to scouring, subject to thermal cycling. If workspace-hub ever adds offshore-wind-specific workflows, cable assessment MUST be separate module (not bundled with riser VIV). The DNV-ST-0359 update signals that DNV is tightening cable-specific guidance — worth monitoring if your Phase 7 scope expands toward distributed offshore generation systems.

`─────────────────────────────────────────────────`

---

## Sources

- [DNV-ST-0359 Subsea Power Cables for Wind Power Plants – DNV](https://www.dnv.com/energy/standards-guidelines/dnv-st-0359-subsea-power-cables-for-wind-power-plants/)
- [DNV Updates Subsea Cable Standard for Offshore Wind Applications – Windtech International](https://www.windtech-international.com/product-news/dnv-updates-subsea-cable-standard-for-offshore-wind-applications)
- [Incorporating Non-metallic Materials into API 579-1/ASME FFS-1 – Inspectioneering (Feb 2026)](https://inspectioneering.com/journal/2026-02-26/11928/behind-the-bulletin-incorporating-non-metallic-materials-into-api-579-1asme-ff)
- [API 579-1/ASME FFS-1 Part 16 Assessment Levels for FRP Assets – UTComp](https://utcomp.com/api-579-1-asme-ffs-1-update/api-579-part-16-assessment-levels-for-frp-assets/)
- [EN IEC 61400-1:2019/A1:2026 Wind Turbine Design Requirements Amendment – ITEH Standards](https://www.standards.iteh.ai/catalog/standards/clc/8007ffa4-bb0c-4cbd-b306-74394bbf66b1/en-iec-61400-1-2019-a1-2026)
- [IEC 61400-3-2 Ed. 1.0 b:2025 Floating Offshore Wind Turbine Design Requirements – ANSI Webstore](https://webstore.ansi.org/standards/iec/IEC61400Ed2025)
- [April 2026 Energy Engineering Standards: Wind and Biofuel Updates – ITEH](https://standards.iteh.ai/articles/blog/energy-and-heat-transfer/energy-standards-update-apr-2026)
- [ISO 19901-10:2021 Marine Geophysical Investigations – ISO](https://www.iso.org/standard/77017.html)
- [ISO 19901-2:2022 Seismic Design Procedures – ISO](https://www.iso.org/standard/77217.html)
- [ISO 19901-1:2015 Metocean Design and Operating Considerations – ISO](https://www.iso.org/standard/60183.html)

---

**Decision gate for Phase 7:** Are jumpers + export cables in OrcaWave v1.1 scope, or risers-only? This determines whether DNV-ST-0359 is a Phase 7 blocking dependency. Current evidence suggests risers-only (per prior phase descriptions), but confirmation in plan is required.
