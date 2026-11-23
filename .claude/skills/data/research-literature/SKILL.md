---
name: research-literature
description: "Systematize research and literature gathering for engineering categories\
  \ \u2014 queries doc index, capability map, and standards ledger to produce structured\
  \ research briefs for calculation implementation. type: reference\n"
version: 1.0.0
category: data
related_skills:
- doc-research-download
triggers:
- research literature
- gather standards
- literature review
- research brief
- find standards for
type: reference
freedom: high
---

# Research & Literature Gathering Skill

## Overview

Use this skill when implementing calculations requires identifying applicable
standards, gathering reference literature, and mapping gaps. It queries three
existing data sources and produces a structured YAML research brief.

## Inputs

- **category**: engineering discipline (e.g. `geotechnical`, `structural`, `subsea`)
- **subcategory**: specific topic (e.g. `pile_capacity`, `fatigue`, `viv_analysis`)

## 8-Step Workflow

1. Query the Standards Ledger
2. Query the Document Index
3. Cross-Reference Capability Map
4. Produce the Research Brief
5. Search University & Academic Resources
6. Document Download Tasks
7. Deep Online Research
8. Download Script Generation

See [workflow-steps.md](references/workflow-steps.md) for detailed commands and procedures for each step.

See [templates.md](references/templates.md) for the research brief YAML template and domain-to-repo mapping.

## AC Checklist

- [ ] Standards ledger queried for domain
- [ ] Doc index searched with category and subcategory keywords
- [ ] Capability map cross-referenced for implementation status
- [ ] University/academic resources searched (textbooks, coursework, OCW)
- [ ] Worked examples with known answers identified for TDD tests
- [ ] Coursework materials archived in `knowledge/dark-intelligence/<category>/`
- [ ] Research brief YAML saved to `.planning/capability-map/research-briefs/`
- [ ] Download tasks identified with availability status
- [ ] Brief reviewed for completeness before handing off to implementation WRK
- [ ] Deep online research performed (WebSearch for free PDFs and papers)
- [ ] Download script generated via `--generate-download-script`
- [ ] Download script manually curated with discovered URLs
- [ ] Downloads validated with `file *.pdf` (no HTML/WAF responses)

## See also

- [data/dark-intel](https://github.com/vamseeachanta/data/tree/main/dark-intel) — dark intelligence archive where research materials and worked examples are stored
