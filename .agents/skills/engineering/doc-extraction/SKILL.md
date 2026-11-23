---
name: doc-extraction
description: 'Classify and extract structured content from engineering documents using
  a 3-layer taxonomy: generic content types, engineering patterns, and domain sub-skills.
  Use when ingesting standards, reports, or technical manuals into structured data
  for downstream analysis. type: reference

  '
version: 1.0.0
updated: 2026-03-12
category: engineering
triggers:
- document extraction
- content classification
- extract constants
- extract equations
- extract tables
- parse engineering document
- ingest standard
- technical manual extraction
capabilities:
- content-type-classification
- engineering-pattern-extraction
- standards-reference-parsing
- unit-normalization
requires: []
tags: []
scripts_exempt: true
type: reference
---

# Doc Extraction

## When to Use

- Ingesting a new standard or code (DNV-RP, API RP, ISO, ASME)
- Extracting constants, equations, or tables from technical reports
- Building structured datasets from engineering manuals
- Populating knowledge bases from document collections
- Pre-processing documents before analysis workflow

## Related Skills

- [document-index-pipeline](../../data/document-index-pipeline/SKILL.md) — 7-phase A→G pipeline
- [doc-intelligence-promotion](../../data/doc-intelligence-promotion/SKILL.md) — Deep extraction post-processing
- [cathodic-protection](../marine-offshore/cathodic-protection/SKILL.md) — CP system design
- [viv-analysis](../marine-offshore/viv-analysis/SKILL.md) — VIV assessment for risers
- [fitness-for-service](../asset-integrity/fitness-for-service/SKILL.md) — FFS assessment
- [structural-analysis](../marine-offshore/structural-analysis/SKILL.md) — Structural checks

## References

- DNV-RP-B401: Cathodic Protection Design
- DNV-RP-C205: Environmental Conditions and Environmental Loads
- API 579-1/ASME FFS-1: Fitness-for-Service
- API RP 16Q: Design, Selection, Operation, and Maintenance of Marine Drilling Riser Systems

## Sub-Skills

- [Yield Reality (WRK-1246 Corpus Assessment)](yield-reality-wrk-1246-corpus-assessment/SKILL.md)
- [Architecture](architecture/SKILL.md)
- [1. `constants` (0% yield — not yet implemented) (+7)](1-constants-0-yield-not-yet-implemented/SKILL.md)
- [Unit Detection and Normalization (+4)](unit-detection-and-normalization/SKILL.md)
- [Extraction Workflow](extraction-workflow/SKILL.md)
- [Output Schema](output-schema/SKILL.md)
- [Domain Sub-Skills](domain-sub-skills/SKILL.md)
- [Hybrid Classification Strategy (WRK-1188 Learning)](hybrid-classification-strategy-wrk-1188-learning/SKILL.md)
