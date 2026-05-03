---
title: "AWS D1.1/D1.1M — Structural Welding Code, Steel — bounded summary"
tags: ["aws", "standards", "welding", "structural", "steel", "metadata-only"]
added: 2026-05-03
last_updated: 2026-05-03
domain: engineering-standards
code_id: aws-d1-1
publisher: AWS
publisher_full: "American Welding Society"
revision: "2010"
revision_source: "/mnt/ace/O&G-Standards/AWS/AWS D1.1/AWS D1.1-D1.1M (2010) Structural Welding Code - Steel.pdf"
publisher_current_edition: "2025"
verified_on: 2026-05-03
public_url: https://pubs.aws.org/p/2264/d11d11m2025-structural-welding-code-steel
sources:
  - "/mnt/ace/O&G-Standards/AWS/AWS D1.1/AWS D1.1 (2006) - Structual Welding Code - Steel (Searchable).pdf (2006 edition; two-print variants — Scanned and Searchable)"
  - "/mnt/ace/O&G-Standards/AWS/AWS-D1-1-D1-1M-2008(1).pdf (2008 reissue print at AWS-folder root)"
  - "/mnt/ace/O&G-Standards/AWS/AWS D1.1/AWS D1.1 (2009) - Structual Welding Code - Steel (Scanned).pdf (2009 edition)"
  - "/mnt/ace/O&G-Standards/AWS/AWS D1.1/AWS D1.1-D1.1M (2010) Structural Welding Code - Steel.pdf (2010 edition; pinned canonical revision)"
extraction_policy: metadata-only
raw_copy_allowed: false
aws_doc_number: "D1.1/D1.1M"
ledger_id: AWS-D1.1
cross_references:
  - { code_id: "asme-bpvc-ix", relation: "qualifies", note: "ASME BPVC Section IX qualifies welders/procedures referenced by D1.1 contract documents" }
  - { code_id: "api-1104", relation: "companion", note: "API 1104 is the pipeline-welding companion code; D1.1 covers structural, 1104 covers transmission pipelines" }
multi_edition_note: "umbrella page covering 4 editions on disk (2006, 2008, 2009, 2010); revision pinned to newest on-disk 2010"
---

# AWS D1.1/D1.1M — Structural Welding Code, Steel

## Scope
Welding requirements for the fabrication and erection of welded steel structures. Covers welding processes, prequalified joints, qualification of procedures and personnel, fabrication and inspection, stud welding, and dynamically loaded structures. Applies to steels with minimum specified yield strength up to a code-defined ceiling and thickness above an allowable lower bound. Used as the structural-welding contractual reference for buildings, bridges, and offshore topsides.

## Why this page exists
Resolver target for digitalmodel `Citation` instances per `.claude/rules/calc-citation-contract.md`. AWS D1.1 is referenced 12 times across `digitalmodel/structural/fatigue/sn_curves.py`, `digitalmodel/structural/fatigue/__init__.py`, `digitalmodel/fatigue/sn_library.py`, and `digitalmodel/fatigue/weld_classification.py` — primarily for S-N fatigue curves and weld classifications. This page contains no clause text, formulas, or tables.

## Where to find the full text
- Raw PDFs (4 editions on disk under `/mnt/ace/O&G-Standards/AWS/`, read-only, vendor-derivative; do not copy into git per #2482):
  - 2006 edition (two-print variants, Scanned + Searchable) under `AWS D1.1/`
  - 2008 reissue at `AWS-D1-1-D1-1M-2008(1).pdf`
  - 2009 edition under `AWS D1.1/`
  - 2010 edition under `AWS D1.1/` (canonical for this page)
- Publisher catalog: https://pubs.aws.org/ (registration required for purchase/download)
- Internal callers: `digitalmodel/src/digitalmodel/structural/fatigue/sn_curves.py`, `digitalmodel/src/digitalmodel/structural/fatigue/__init__.py`, `digitalmodel/src/digitalmodel/fatigue/sn_library.py`, `digitalmodel/src/digitalmodel/fatigue/weld_classification.py`

## Edition gap discipline
On-disk newest edition is 2010. Publisher-current edition is 2025 — a 15-year gap, the widest in the engineering-standards W-series. Calc-callers MUST verify against the publisher-current edition before any compliance use; this wiki page reflects the on-disk corpus only and does not certify currency.

## Cross-references
- [[asme-bpvc-ix]] — qualifies welders and welding procedures referenced by D1.1 contract documents
- [[api-1104]] — companion pipeline-welding code (forward-pointing dangling link; W1-A or future W1-B scope)
- [Calc citation contract](../../../../../.claude/rules/calc-citation-contract.md)
