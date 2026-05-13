---
name: project-domain-knowledge-sweep
description: Multi-source domain research → coverage map → implementation issues workflow. Replaces LinkedIn-only extraction with academic + standards + industry + marketing parallel sweep. Domain 1 (Hydrodynamics) launched 2026-05-12.
metadata: 
  node_type: memory
  type: project
  originSessionId: 37c4fd1d-3784-4903-a5ea-5fe997dd7044
---

# Domain Knowledge Sweep workflow

Parent feature: [#2667](https://github.com/vamseeachanta/workspace-hub/issues/2667).

## Architecture

```
PARENT FEATURE (#2667)
└── DOMAIN PARENT (e.g., #2668 Hydrodynamics)
    ├── R1 Standards inventory (DNV/API/ISO/ABS catalog)
    ├── R2 Academic sources (textbooks, papers, DOIs)
    ├── R3 Industry practice (OMAE/ISOPE, vendor docs)
    ├── R4 Marketing/LinkedIn surface (NOT primary technical source)
    ├── R5 Code coverage audit (digitalmodel STRONG/PARTIAL/GAP)
    └── R6 Synthesis → coverage map + gap implementation subissues
```

## Why this exists

- LinkedIn-only sourcing fails day-one lint per `feedback_llm_wiki_concept_pages_need_public_references`
- Single-source extraction was the original `field-dev-code-recon` skill pattern; this generalizes it
- 3 AI accounts on standby — parallelize research streams across them
- llm-wiki strategic role demands comprehensive coverage (`project_llm_wiki_strategic_role`)

## How to apply

1. **New domain target?** Spawn a Domain Parent issue (template = #2668)
2. **Account distribution:** Account 1 (synthesis + code), Account 2 (standards + academic), Account 3 (industry + LinkedIn marketing)
3. **R4 LinkedIn is marketing surface only** — no technical content imported from social posts
4. **Citations:** all gap subissues must conform to `.claude/rules/calc-citation-contract.md`
5. **Wiki ingestion:** R6 produces an llm-wiki checklist; concepts must cite primary (non-LinkedIn) sources

## Domain queue (priority order)

1. Offshore Hydrodynamics — [#2668](https://github.com/vamseeachanta/workspace-hub/issues/2668) (LAUNCHED 2026-05-12)
2. Mooring Design (queued)
3. Subsea Pipelines (queued)
4. VIV / Riser Dynamics (queued)
5. CCS / CO2 Transport (queued)

## Related memory

- [[project_llm_wiki_external_post_ingest_workflow]] — single-source extraction (predecessor pattern)
- [[feedback_llm_wiki_concept_pages_need_public_references]] — root cause for shift
- [[project_llm_wiki_strategic_role]] — why coverage gaps are first-class defects
- [[project_nightly_researchers]] — existing parallel research infrastructure to leverage
