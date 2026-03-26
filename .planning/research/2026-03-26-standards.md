Here is the compiled research report:

---

# Research: standards — 2026-03-26

## Key Findings

- **DNV-RP-C203 2024 edition** — Revised fatigue analysis methodology for subsea connectors: new S-N curves for seawater with cathodic protection, updated notch model, and increased fatigue strength based on reassessed and newly acquired test data. Published 2024, now the current edition. ([DNV-RP-C203 page](https://www.dnv.com/energy/standards-guidelines/dnv-rp-c203-fatigue-design-of-offshore-steel-structures/), [2016 vs 2024 benchmark](https://sdcverifier.com/benchmarks/dnv-rp-c203-fatigue-comparison-2016-vs-2024/), [ScienceDirect paper on subsea connector methodology](https://www.sciencedirect.com/science/article/abs/pii/S095183392500022X))

- **DNV July 2025 classification rules (in force 1 Jan 2026)** — 119 documents published. Restructured structural standards for column-stabilized units, TLPs, and deep-draught floating units (OS-C103, OS-C105, OS-C106). New CO2 reconditioning notation. Updated NCS (N) notation alignment. ([DNV announcement](https://www.dnv.com/news/2025/now-available-july-2025-edition-of-dnv-class-rules-and-documents-for-ship-and-offshore/), [MarineLink coverage](https://www.marinelink.com/news/dnv-updates-class-rules-ships-offshore-515110))

- **ISO 19901-4:2025 (Geotechnical Design)** — Third edition published, superseding 2016. Adds unified CPT-based pile design for sands, intermediate foundation guidance for fixed structures, pile capacity reassessment clause, and performance-based design considerations. ([ISO 19901-4:2025](https://www.iso.org/standard/79594.html))

- **ABS new Offshore Rules — full transition 1 Jan 2026** — The legacy FPI Rules and Facilities Rules are withdrawn. All new offshore unit design must use the consolidated Offshore Rules and Facilities Guide. New survey requirements for hull structure examination, corrosion control reporting, and critical inspection areas (ISIP/SCIP). ([ABS new offshore rules](https://www.iims.org.uk/abs-new-offshore-rules-2025/), [ABS January 2026 notices (PDF)](https://ww2.eagle.org/content/dam/eagle/rules-and-resources/RuleManager2/notices/january-2026/3-or-nandgi-jan26.pdf))

- **ASME B31.4-2025 edition published** — New edition exists for liquid pipeline transportation systems. Specific amendment details not publicly enumerated, but the edition is current as of early 2026. ([StudyLib reference](https://studylib.net/doc/28234813/asme-b31.4-2025))

## Relevance to Project

| Finding | Affected Package / Workflow |
|---|---|
| DNV-RP-C203 2024 S-N curve revisions | **digitalmodel** — spectral fatigue module (Phase 1, plan 01-04). The S-N curves for seawater+CP and the notch model changes directly affect fatigue life outputs. The existing implementation likely references 2016-era curves. |
| DNV July 2025 structural standards restructure | **digitalmodel** — any module referencing DNV OS-C103/C105/C106. YAML traceability manifests need updated standard identifiers. |
| ISO 19901-4:2025 geotechnical edition | **digitalmodel** — on-bottom stability module (Phase 1, plan 01-02) references soil parameters. New CPT-based pile design and intermediate foundation clauses may affect downstream stability inputs for pipeline/structure interaction. |
| ABS Offshore Rules consolidation | **aceengineer-website** — calculation showcase and compliance marketing must reference the consolidated rules, not legacy FPI/Facilities Rules that are now withdrawn. |
| ASME B31.4-2025 | **digitalmodel** — wall thickness module (Phase 1, plan 01-03). Verify implementation against 2025 edition clause numbering and any coefficient changes. |

## Recommended Actions

- [ ] **Create GitHub issue** — Update digitalmodel spectral fatigue module to DNV-RP-C203 2024 S-N curves (seawater+CP and notch model). Benchmark against [2016 vs 2024 comparison](https://sdcverifier.com/benchmarks/dnv-rp-c203-fatigue-comparison-2016-vs-2024/) to quantify impact.
- [ ] **Create GitHub issue** — Audit YAML traceability manifests for any references to superseded DNV OS-C103/C105/C106 document IDs; update to July 2025 edition identifiers.
- [ ] **Create GitHub issue** — Review ASME B31.4-2025 wall thickness clauses against digitalmodel implementation (plan 01-03) for any coefficient or formula changes from the previous edition.
- [ ] **Promote to PROJECT.md** — Add ISO 19901-4:2025 as a tracked standard in the engineering domains section, noting the new CPT-based pile design method as a future calculation module candidate.
- [ ] **Ignore (low priority)** — ABS Offshore Rules consolidation is relevant to website content but not to calculation code. Flag for Phase 3 (GTM/website) when writing compliance-related marketing copy.

---

Sources:
- [DNV-RP-C203 Fatigue design of offshore steel structures](https://www.dnv.com/energy/standards-guidelines/dnv-rp-c203-fatigue-design-of-offshore-steel-structures/)
- [DNV RP-C203 Fatigue Comparison: 2016 vs 2024](https://sdcverifier.com/benchmarks/dnv-rp-c203-fatigue-comparison-2016-vs-2024/)
- [Background for revised fatigue analysis methodology of subsea connectors in DNV-RP-C203 (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S095183392500022X)
- [DNV July 2025 edition announcement](https://www.dnv.com/news/2025/now-available-july-2025-edition-of-dnv-class-rules-and-documents-for-ship-and-offshore/)
- [ISO 19901-4:2025](https://www.iso.org/standard/79594.html)
- [ABS new offshore rules 2025 (IIMS)](https://www.iims.org.uk/abs-new-offshore-rules-2025/)
- [ABS January 2026 notices (PDF)](https://ww2.eagle.org/content/dam/eagle/rules-and-resources/RuleManager2/notices/january-2026/3-or-nandgi-jan26.pdf)
- [ASME B31.4-2025 (StudyLib)](https://studylib.net/doc/28234813/asme-b31.4-2025)
- [DNV-RP-F109 on-bottom stability](https://www.dnv.com/energy/standards-guidelines/dnv-rp-f109-on-bottom-stability-design-of-submarine-pipelines/)
- [BSEE Regulations & Standards](https://www.bsee.gov/what-we-do/offshore-regulatory-programs/regulations-standards)
