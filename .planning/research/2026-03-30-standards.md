Based on my research across API, DNV, ABS, and ISO standards from the past 6 months, here's the findings relevant to your workspace-hub project:

---

# Research: standards — 2026-03-30

## Key Findings

- **DNV July 2025 edition (effective 1 Jan 2026) — 77 documents published for rules hearing, with 2026 edition now open for public hearing (1 Mar – 12 Apr 2026).** Structural design standards OS-C103 (column-stabilized units), OS-C105 (TLPs), and OS-C106 (deep-draught floating units) were restructured for clarity and alignment. Cyber secure notation added as mandatory for offshore units. Key gap: prior research (2026-03-26) noted July 2025 edition was effective 1 Jan 2026; current hearing is for July 2026 edition publication.

- **ABS Offshore Rules consolidation (effective 1 Jan 2026, notices updated January 2026).** The legacy FPI Rules and Facilities Rules withdrawn; all new offshore unit design must use consolidated Offshore Rules and Facilities Guide. New survey requirements include hull structure examination, corrosion control reporting, and critical inspection areas (ISIP/SCIP). No breaking changes to existing digitalmodel modules but website marketing copy must reference consolidated rules, not legacy standards.

- **API 579-1/ASME FFS-1 Part 16 (Fiber Reinforced Polymer Equipment) in development.** The existing API 579-1/ASME FFS-1 4th Edition (December 2021) remains current. New Part 16 adds assessment methods for FRP equipment — relevant to future material domain expansion (Phase 999.2 backlog mentions FFS as complement to wall thickness/fatigue modules). Current version: 4th Edition Dec 2021; no active 2026 edition revision announced for core parts.

- **DNV-ST-F101 Submarine pipeline systems (current edition Aug 2021).** Remains the global standard for submarine pipelines with Load and Resistance Factor Design (LRFD). No 2026 revision announcement in search results. Cross-reference: prior research (2026-03-26) noted DNV-RP-F109 on-bottom stability. Both are active standards for Phase 1 digitalmodel modules (on-bottom stability plan 01-02, wall thickness plan 01-03).

- **ISO 19901 series — Part 4 (Geotechnical) currently 2016 edition; Part 2 (Seismic) 2022 edition with FDIS for 2026+ revision underway. Part 8 (Marine soil investigations) 2023 edition.** New ISO/FDIS 19901-2 in approval phase for 2026 publication. Part 4 (geotechnical, CPT-based pile design) is most relevant to on-bottom stability, but 2016 edition still current. Prior research already flagged Part 4 as future module candidate (Phase 999.2 backlog).

## Relevance to Project

| Finding | Affected Package / Workflow |
|---|---|
| **DNV July 2025 + 2026 hearing** | **digitalmodel** — Any YAML traceability manifests referencing OS-C103/C105/C106 need identifiers updated if you're using 2025 edition as baseline. The 2026 hearing (closing 12 Apr) may introduce breaking changes; monitor through April. |
| **ABS Offshore Rules consolidation** | **aceengineer-website** — Calculation showcase and compliance marketing must reference the consolidated Offshore Rules (effective 1 Jan 2026), not legacy FPI/Facilities Rules. This is infrastructure but not code. |
| **API 579 Part 16 (FRP)** | **digitalmodel Phase 999.2** — Backlog item for fitness-for-service modules. Part 16 development signals market demand for FRP assessment alongside steel. When Part 16 is published (timeline TBD in search results), it becomes a required standard for FRP material domain. |
| **DNV-ST-F101 submarine pipelines** | **digitalmodel** — Wall thickness and on-bottom stability modules ship with DNV-ST-F101 compliance. No 2026 revision found, but standard remains current. |
| **ISO 19901 geotechnical** | **digitalmodel Phase 1 plan 01-02** — On-bottom stability module. Part 4 (2016) is current; Part 2 (seismic, 2022) has FDIS pending for 2026. Future-watch: when Part 4 third edition publishes (likely 2026-2027), CPT-based pile design becomes a calculation module candidate. |

## Recommended Actions

- [ ] **Create GitHub issue** — Monitor DNV 2026 hearing (closes 12 Apr 2026) for breaking changes to OS-C103/C105/C106; if any impact on calculation modules, update YAML manifests and standards traceability before 1 July 2026 publication.
- [ ] **Create GitHub issue** — Audit aceengineer-website marketing copy and calculator descriptions for references to legacy ABS FPI/Facilities Rules; update all references to consolidated Offshore Rules by end of Q2 2026 (before enterprise GTM cycle).
- [ ] **Promote to PROJECT.md** — Add note under Engineering Domains that API 579 Part 16 (FRP assessment) is under development; when published, it becomes a Tier 1 candidate for Phase 999.2 (fitness-for-service expansion).
- [ ] **Monitor (low priority)** — ISO 19901-2 FDIS approved 2026 edition. When published mid-2026, review Part 2 seismic clauses for relevance to floating unit analysis (if future scope includes TLP/spar design). Current relevance: zero (not in v1.0 or v1.1 scope).
- [ ] **Ignore** — ISO 19901-4 third edition (geotechnical) publication timeline unknown; Phase 1 on-bottom stability uses current best practices. Will revisit when Part 4 publishes.
- [ ] **Ignore** — DNV-RP-F101 (corroded pipeline assessment) is software tool, not standards update. Current Phase 1 modules do not implement corroded pipeline assessment; future phase candidate only.

---

**Summary:** The dominant near-term action is **monitoring DNV 2026 hearing outcome (closes 12 April 2026)** for OS-C103/C105/C106 changes, and **updating aceengineer-website marketing copy** to reference consolidated ABS rules (already effective 1 Jan 2026). No breaking changes to shipped Phase 1 calculation modules detected. API 579 Part 16 signals long-term fitness-for-service roadmap (Phase 999.2).

---

Sources:
- [DNV July 2025 edition announcement](https://www.dnv.com/news/2025/now-available-july-2025-edition-of-dnv-class-rules-and-documents-for-ship-and-offshore/)
- [DNV Rules 2026 Hearing Period Now Open](https://www.dnv.com/news/2026/dnv-rules-2026-hearing-period-now-open/)
- [ABS New Offshore Rules 2025 (IIMS)](https://www.iims.org.uk/abs-new-offshore-rules-2025/)
- [ABS January 2026 Notices (PDF)](https://ww2.eagle.org/content/dam/eagle/rules-and-resources/RuleManager2/notices/january-2026/3-or-nandgi-jan26.pdf)
- [API 579-1/ASME FFS-1 Training Course](https://www.asme.org/learning-development/find-course/api-579-1-asme-ffs-1-fitness-service-evaluation)
- [DNV-ST-F101 Submarine pipeline systems](https://www.dnv.com/energy/standards-guidelines/dnv-st-f101-submarine-pipeline-systems/)
- [ISO 19901-4:2016 Geotechnical and foundation design](https://www.iso.org/standard/61144.html)
- [ISO 19901-2:2022 Seismic design (with 2026 FDIS pending)](https://www.iso.org/standard/77217.html)
