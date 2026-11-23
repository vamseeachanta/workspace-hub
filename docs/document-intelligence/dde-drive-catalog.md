# DDE Remote Drive Catalog

> **Mount:** `/mnt/remote/ace-linux-2/dde` (SSHFS from ace-linux-2)
> **Device:** 2.8 TB, 70% used (2.0 TB consumed)
> **Status:** NOT indexed in workspace-hub pipeline — this catalog is the first inventory
> **Generated:** 2026-04-02

---

## Overview

The DDE drive is a legacy data drive on ace-linux-2 containing historical project work,
literature, standards collections, and cloud sync exports. It pre-dates the structured
`/mnt/ace` organization and has significant overlap but also UNIQUE content not found
elsewhere.

---

## Directory Inventory

### Engineering Work (HIGH VALUE)

| Directory | Contents | Est. Files | Overlap with /mnt/ace | Unique Value |
|-----------|----------|------------|----------------------|--------------|
| `documents/` | 99 project folders (0063-0200+) | 5,000+ | HIGH — mirrors /mnt/ace/docs | May have files not migrated |
| `Orcaflex/` | OrcaFlex .dat models | 20+ | LOW — different projects | Drilling riser dev, Shell Stones WH fatigue |
| `FreeSpanVIVFatigue/` | 13 MATLAB scripts | 13 | NONE — unique | Pipeline VIV fatigue analysis (2H methods) |
| `o-drive/017 ODA/` | Drilling data analytics | 50+ | NONE — unique | MOLE algorithm, torque-and-drag, well data |
| `o-drive/018 FFS/` | Fitness-for-Service | 8+ | NONE — unique | FFS presentations, KBR Caesar Tonga |
| `o-drive/00 Offshore/` | Offshore engineering | varies | UNKNOWN | Check for unique content |
| `dropbox_contents/Engineering/` | 15+ project folders | 100+ | PARTIAL | KBR FFS projects (0191-0196), KM riser analysis |

### Standards & Literature (HIGH VALUE)

| Directory | Contents | Est. Files | Overlap with /mnt/ace | Unique Value |
|-----------|----------|------------|----------------------|--------------|
| `0000 O&G/0000 Codes & Standards/` | 36 org dirs | 1,000+ | PARTIAL — has extra orgs | ASME, ASCE, AWS, NACE, IEC, NFPA, FAA, CFR, GLND, AISC, AMJIG, AMS, ANSI, AS, ASNT, AWHEM not in /mnt/ace |
| `0000 O&G/Oil and Gas Codes/` | API, DNV, ISO, ASTM copies | 500+ | HIGH — duplicates | British Library collection |
| `0000 O&G/Codes & Standards Database.xls` | Master index spreadsheet | 1 | NONE — unique | Historical cataloging of entire standards collection |
| `Literature/Engineering/` | Engineering textbooks | 50+ | LOW | Heat transfer, reservoir eng, environmental, FFT |
| `Literature/Oil and Gas/` | O&G industry literature | 80+ | LOW | Reservoir eng, peak oil analysis, pipeline repair |
| `Literature/Safety Reviews/` | Safety literature | varies | NONE — unique | HSE reference material |
| Loose PDFs at root | ASTM, DNV, pipeline docs | 5+ | PARTIAL | Quick-access reference copies |

### Business & Personal (MEDIUM VALUE)

| Directory | Contents | Est. Files | Category |
|-----------|----------|------------|----------|
| `g-drive/` | Google Drive export | 30+ | AceEngineer financials, idea logs, invoices, doc register |
| `g-drive/AceEngineer Inc_/` | Company documents | varies | Incorporation, operations |
| `o-drive/00 OXY/` | Oxy career docs | 20+ | Pay stubs, career docs, merger info |
| `o-drive/00_Financial_analysis/` | Financial analysis | varies | Investment/financial data |
| `o-drive/00 MAN/` | Technical manuals (self-authored) | 15+ | IT admin, data science, D3.js, engineering practices, IoT |
| `dropbox_contents/References/` | Reference materials | 3+ | Python cheat sheets, employee learnings |
| `Information_Important/` | Important personal docs | 15+ | Green card, SPE membership, contacts |
| `Personal/` | Personal | varies | OTC 2015 conference |

### Non-Engineering (LOW PRIORITY)

| Directory | Contents | Notes |
|-----------|----------|-------|
| `Literature/BookSummaries/` | Business book summaries | 35+ executive summaries — MBA-level |
| `Literature/MBA/` | MBA materials | Academic coursework |
| `Literature/Finance/` | Finance literature | CFA/investment reference |
| `Literature/Career/` | Career materials | Job search, interview tips |
| `Literature/GMAT/`, `Literature/GRE/` | Test prep | Historical |
| `Literature/HBR/` | Harvard Business Review | Leadership/management |
| `TECH Animation Fundaes/` | 3DS Max, Blender manuals | 3D animation reference |
| `TECH Writing/` | BBC, Economist style guides | Writing reference |

---

## Unique Standards Organizations on DDE (NOT in /mnt/ace/O&G-Standards)

These organizations exist in DDE `0000 O&G/0000 Codes & Standards/` but are
ABSENT from `/mnt/ace/O&G-Standards/`:

| Org | Full Name | Engineering Relevance |
|-----|-----------|----------------------|
| AISC | American Institute of Steel Construction | Structural steel design |
| AMJIG | (Unknown/legacy) | Verify contents |
| AMS | Aerospace Material Specifications | Materials for high-spec applications |
| ANSI | American National Standards Institute | Cross-cutting standards |
| AS | Australian Standards | International projects |
| ASCE | American Society of Civil Engineers | Structural/geotechnical |
| ASME | Am. Soc. of Mechanical Engineers | Pressure vessels, piping — CRITICAL |
| ASNT | Am. Soc. for Nondestructive Testing | NDT/NDE inspection |
| AWHEM | (Unknown/legacy) | Verify contents |
| AWS | American Welding Society | Welding standards — CRITICAL |
| CFR | Code of Federal Regulations | US regulatory compliance |
| FAA | Federal Aviation Administration | Aviation (niche) |
| GLND | (Unknown/legacy) | Verify contents |
| HSE | Health & Safety Executive (UK) | UK offshore safety — IMPORTANT |
| IADC-TPC | IADC/drilling related | Drilling standards |
| IEC | International Electrotechnical Commission | Electrical/subsea |
| NACE | National Assoc. of Corrosion Engineers | Corrosion — CRITICAL for CP domain |
| NFPA | National Fire Protection Association | Fire safety |

**Recommendation:** Migrate ASME, AWS, NACE, ASCE, HSE, IEC, and ANSI directories to
`/mnt/ace/O&G-Standards/` to consolidate the standards library.

---

## MATLAB Code Inventory

### FreeSpanVIVFatigue/ (Pipeline VIV Fatigue Analysis)

Implements DNV-RP-F105 pipeline free-span VIV fatigue methodology.
**NOTE: Copyrighted code — clean-room reimplementation required (see #1773).**

| Script | Purpose |
|--------|---------|
| `FreeSpanVIVFatigue.m` | Main entry point |
| `TwoHspanvivSetup.m` | Configuration/setup |
| `TwoHspanvivGetInputs.m` | Input parameter reader |
| `TwoHspanvivReadFile.m` | Data file reader |
| `TwoHspanvivCrossflowScreen.m` | Cross-flow VIV screening |
| `TwoHspanvivCrossflowFatigue.m` | Cross-flow fatigue calculation |
| `TwoHspanvivInlineScreen.m` | In-line VIV screening |
| `TwoHspanvivInlineFatigue.m` | In-line fatigue calculation |
| `TwoHspanvivDamageAssessment.m` | Fatigue damage assessment |
| `TwoHspanvivCombineDamage.m` | Combined damage calculation |
| `TwoHspanvivCreateResultFile.m` | Output report generation |
| `WeibullCurrentFit.m` | Current profile Weibull fitting |
| `ToDo.txt` | Development notes |

**Value:** Candidate for Python port into digitalmodel VIV module.

---

## Recommended Actions

### Immediate (can do now)
1. Register DDE sources in `mounted-source-registry.yaml` (3 new entries: dde_standards, dde_literature, dde_engineering)
2. Copy `Codes & Standards Database.xls` to workspace-hub for analysis
3. Scan DDE `0000 O&G/` for standard orgs missing from /mnt/ace

### Short-term (next sprint)
4. Run SHA-256 dedup of `documents/` vs `/mnt/ace/docs/` to find unique project files
5. Migrate ASME, AWS, NACE, ASCE, HSE, IEC standards to `/mnt/ace/O&G-Standards/`
6. Index DDE unique content into Phase A pipeline

### Medium-term (backlog)
7. Port FreeSpanVIVFatigue MATLAB to Python (dark-intelligence-workflow)
8. Extract `o-drive/017 ODA/` MOLE algorithm documentation
9. Catalog DDE `Literature/Engineering/` textbooks into domain taxonomy
