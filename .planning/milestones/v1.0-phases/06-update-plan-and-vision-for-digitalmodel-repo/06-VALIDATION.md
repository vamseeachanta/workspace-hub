---
phase: 6
slug: update-plan-and-vision-for-digitalmodel-repo
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-26
---

# Phase 6 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.4+ (configured in pyproject.toml) |
| **Config file** | `digitalmodel/pyproject.toml` [tool.pytest.ini_options] |
| **Quick run command** | `cd digitalmodel && python -m pytest tests/ -x --tb=short -q` |
| **Full suite command** | `cd digitalmodel && python -m pytest tests/ --tb=short` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Visual review of changed documentation files
- **After every plan wave:** Cross-reference ROADMAP.md tiers against module-registry.yaml maturity levels
- **Before `/gsd:verify-work`:** All 4 deliverable files updated and committed
- **Max feedback latency:** N/A — documentation phase, manual review

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| P6-01 | 01 | 1 | Audit current state | manual-only | `grep -c "Current State" digitalmodel/docs/vision/CALCULATIONS-VISION.md` | N/A | ⬜ pending |
| P6-02 | 01 | 1 | Tier-based roadmap | manual-only | `grep -c "Tier 1" digitalmodel/ROADMAP.md` | N/A | ⬜ pending |
| P6-03 | 01 | 1 | OrcaFlex + CP as Tier 1 | manual-only | `grep -c "OrcaFlex\|Cathodic Protection" digitalmodel/ROADMAP.md` | N/A | ⬜ pending |
| P6-04 | 02 | 1 | Tech debt documented | manual-only | `grep -c "Tech Debt" digitalmodel/ROADMAP.md` | N/A | ⬜ pending |
| P6-05 | 02 | 1 | README updated | manual-only | N/A — human review | N/A | ⬜ pending |
| P6-06 | 02 | 1 | module-registry maturity | manual-only | N/A — human review against module state | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. This phase produces documentation (markdown and YAML), not code. No test infrastructure needed.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| CALCULATIONS-VISION.md reflects current state | P6-01 | Document accuracy requires human judgment | Compare vision doc assertions against module-registry.yaml and test status |
| ROADMAP.md uses tier prioritization | P6-02 | Structural review | Verify Tier 1/2/3 structure, no calendar dates, re-tiering guidance |
| Tier 1 lists OrcaFlex + CP | P6-03 | Content correctness | Verify both modules present with current/target/gaps sections |
| Tech debt triaged | P6-04 | Triage quality requires judgment | Verify items categorized by blocking/DX/aspirational |
| README concise and updated | P6-05 | Quality/length judgment | Verify <200 lines, vision section refreshed, links to docs |
| module-registry maturity current | P6-06 | Maturity assessment requires judgment | Cross-check maturity levels against actual module test coverage |
| Doc-intelligence connections | P6-07 | Integration accuracy | Verify roadmap references doc-intelligence as upstream data pipeline |

---

## Validation Sign-Off

- [ ] All tasks have manual verification instructions
- [ ] All 4 deliverable files (ROADMAP.md, CALCULATIONS-VISION.md, README.md, module-registry.yaml) updated
- [ ] Roadmap tiers align with user decisions D-01 through D-05
- [ ] Doc-intelligence pipeline referenced as input data source
- [ ] GTM alignment with aceengineer.com noted for Tier 1/2 modules
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
