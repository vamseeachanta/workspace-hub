---
name: dark-intelligence-workflow
description: "Extract calculation methodology from legacy Excel/files into clean,\
  \ client-free dark intelligence archive \u2014 the canonical path for porting legacy\
  \ calculations to public repos while avoiding legal/IP issues.\n"
type: reference
version: 1.0.0
category: data
related_skills:
- research-literature
- calculation-report
tags:
- excel
- legacy-extraction
- engineering-calculations
- ip-compliance
- methodology-archive
triggers:
- dark intelligence
- extract from excel
- port legacy calculation
- archive calculation
- extract methodology
---

# Dark Intelligence Workflow

## Overview

Use this skill when porting engineering calculations from legacy Excel spreadsheets
(or other legacy formats) into clean, client-free implementations in the 4 public
repos. The workflow extracts only generic methodology — equations, input/output
schemas, worked examples — and strips all client/project identifiers before archival.

## Sub-Skills

- [Inputs](inputs/SKILL.md)
- [Step 1 — Identify (+4)](step-1-identify/SKILL.md)
- [Step 6 — Implement (+1)](step-6-implement/SKILL.md)
- [Integration Points](integration-points/SKILL.md)
- [AC Checklist](ac-checklist/SKILL.md)

## Ecosystem Audit & Promotion Planning

Use this workflow when you need to assess the full dark intelligence landscape
across the ecosystem and plan promotion work into GitHub issues.

### 3-Parallel-Subagent Audit Pattern

Run 3 subagents simultaneously to cover the full surface:

1. **Excel Inventory Subagent** — scan for:
   - Actual .xlsx/.xls files on disk and in repo
   - Dark intelligence extraction outputs (knowledge/dark-intelligence/)
   - Excel-processing scripts (scripts/data/doc_intelligence/)
   - Catalog/index entries referencing Excel (data/document-index/, docs/CONTENT_INDEX.md)
   - Planning docs (.planning/algorithm-extraction.md, heavy-batch-prompts.md)

2. **Conversion Infrastructure Subagent** — map:
   - Skills: dark-intelligence-workflow, xlsx-to-python, doc-extraction, doc-intelligence-promotion
   - Pipeline scripts: parsers, formula_to_python, chain builder, pattern detector, module assembler
   - POC outputs: xlsx-poc/ (v1 formula extraction), xlsx-poc-v2/ (pattern + code gen)
   - digitalmodel Excel utilities (legacy/ scripts, excel_utilities.py modules)
   - Schema & validation (config/schemas/dark-intelligence-archive.yaml)

3. **Domain Coverage Subagent** — assess:
   - Module registries (solver registry, design code registry, skill graph index)
   - Standards transfer ledger (data/document-index/standards-transfer-ledger.yaml)
   - Domain file counts in digitalmodel/src/digitalmodel/ (30 domains, 1,362 files)
   - Function counts and standards-mapped vs unmapped (docs/vision/CALCULATIONS-VISION.md)
   - Test coverage baselines (config/testing/coverage-baseline.yaml)

### Gap Matrix Output

Cross-reference the 3 subagent outputs into a promotion map:

```
EXCEL SOURCE          → EXTRACTION STATE   → CODE COVERAGE    → STANDARDS STATUS
/mnt/ace/*.xls (3.6K)   6 extracted          1,362 files        29/425 done
CONTENT_INDEX (419)      0 extracted          7,355 functions    235 gaps
Standards DB             cataloged            2.95% test cov     93 materials gaps
```

### Issue Generation Pattern

Structure GitHub issues as:
- 1 epic with child issue cross-references
- Phase 1: Wire existing extractions (quick wins — extracted but not promoted)
- Phase 2: Batch extraction (high-value unprocessed Excel files)
- Phase 3: Systematic gap closure (by domain, largest gaps first)
- Phase 4: Infrastructure (test coverage uplift, feedback loop, registry rebuild)

Labels: `dark-intelligence`, `domain:code-promotion`, `domain:extraction-pipeline`,
`cat:engineering-calculations`

### Key Reference Files
- Assessment output: docs/document-intelligence/dark-intelligence-excel-assessment.md
- Standards ledger: data/document-index/standards-transfer-ledger.yaml
- Domain coverage: docs/document-intelligence/domain-coverage.md
- Calculations vision: docs/vision/CALCULATIONS-VISION.md
- Pipeline scripts: scripts/data/doc_intelligence/
- Dark intel archives: knowledge/dark-intelligence/
- Algorithm plan: .planning/algorithm-extraction.md
