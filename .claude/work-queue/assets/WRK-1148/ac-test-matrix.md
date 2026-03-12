# WRK-1148 — AC Test Matrix

| # | Acceptance Criterion | Test | Result | Evidence |
|---|---------------------|------|--------|----------|
| AC1 | ≥8 references identified and summarised | `grep -c "^## [0-9]"` → 8 | **PASS** | Returns 8 |
| AC2 | Each entry: title, authors, year, key contribution, key formulae | Manual inspection of §1–8 | **PASS** | All 8 sections contain all fields |
| AC3 | Parameter definitions aligned across sources (t, w, C_L, J) | `grep -E "J\s*="`, `C_L =`, `t =`, `w =` in canonical table | **PASS** | All 4 in parameter table §0 |
| AC4 | Applicability ranges noted per method | `grep -cE "J range\|applies"` → 8 | **PASS** | Each section has Applicability Range subsection |
| AC5 | Va and Vt formulae present in actuator-disk section | `grep -cE "Va\|Vt"` → 27 | **PASS** | §1 contains Va_disc, Va_ff, Va_R, Vt_R formulae |
| AC6 | Output file exists and is readable | `wc -l` → 616 lines | **PASS** | File at digitalmodel/docs/domains/hydrodynamics/propeller-rudder-literature.md |
| AC7 | Legal scan passes | `legal-sanity-scan.sh` | **PASS** | "RESULT: PASS — no violations found" |

**Overall: 7/7 PASS, 0 FAIL**
