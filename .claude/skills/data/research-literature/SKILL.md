---
name: research-literature
description: 'Systematize research and literature gathering for engineering categories
  — queries doc index, capability map, and standards ledger to produce structured
  research briefs for calculation implementation.

  '
version: 1.0.0
category: data
related_skills:
- doc-research-download
- work-queue-workflow
triggers:
- research literature
- gather standards
- literature review
- research brief
- find standards for
---

# Research & Literature Gathering Skill

## Overview

Use this skill when implementing calculations requires identifying applicable
standards, gathering reference literature, and mapping gaps. It queries three
existing data sources and produces a structured YAML research brief.

## Inputs

- **category**: engineering discipline (e.g. `geotechnical`, `structural`, `subsea`)
- **subcategory**: specific topic (e.g. `pile_capacity`, `fatigue`, `viv_analysis`)

## 5-Step Workflow

### Step 1 — Query the Standards Ledger

Find standards already tracked for the domain:

```bash
uv run --no-project python scripts/data/document-index/query-ledger.py \
  --domain <category> --verbose
```

Record each standard's status (`gap`, `done`, `wrk_captured`, `reference`).

### Step 2 — Query the Document Index

Search the 1M-record doc index for relevant documents:

```bash
uv run --no-project python -c "
import json
from collections import Counter
matches = []
with open('data/document-index/index.jsonl') as f:
    for line in f:
        rec = json.loads(line)
        path_lower = rec.get('path', '').lower()
        summary_lower = (rec.get('summary') or '').lower()
        if '<category>' in path_lower or '<subcategory>' in path_lower \
           or '<category>' in summary_lower or '<subcategory>' in summary_lower:
            matches.append(rec)
print(f'Found {len(matches)} documents')
by_source = Counter(r['source'] for r in matches)
for s, c in by_source.most_common():
    print(f'  {s}: {c}')
"
```

Prioritize `og_standards` and `ace_standards` sources over project files.

### Step 3 — Cross-Reference Capability Map

Identify what is implemented vs. gap in the target repo:

```bash
uv run --no-project python -c "
import yaml
with open('specs/capability-map/digitalmodel.yaml') as f:
    data = yaml.safe_load(f)
for m in data['modules']:
    if '<subcategory>' in m['module'] or '<category>' in m['module']:
        print(f\"Module: {m['module']} ({m['standards_count']} standards)\")
        for s in m.get('standards', [])[:30]:
            print(f\"  {s['status']:15s} {s['org']:8s} {s['id'][:70]}\")
"
```

Also check `assetutilities.yaml` and `worldenergydata.yaml` if the category
may span repos.

### Step 4 — Produce the Research Brief

Save as `specs/capability-map/research-briefs/<category>-<subcategory>.yaml`
using the template below.

### Step 5 — Search University & Academic Resources

University coursework and textbooks are high-value sources — they contain **worked examples
with verified answers**, ideal for TDD test assertions and calculation-report YAML examples.

1. Search the doc index for university/academic materials:
   - Keywords: course name, textbook author, university, lecture, homework, example problem
   - Sources: `ace_project`, `dde_project` (may contain archived coursework)
2. Search for relevant textbook chapters and problem sets:
   - Structural: Roark's Formulas, Shigley, Timoshenko
   - Geotechnical: Das, Coduto, API RP 2GEO worked examples
   - Hydrodynamics: DNV-RP-C205 examples, Faltinsen, Chakrabarti
   - Pipeline: Bai & Bai, Mousselli, Palmer & King
   - Financial: Hull (Options), Bodie/Kane/Marcus (Investments)
3. Archive all coursework material as **dark intelligence**:
   - Save to `knowledge/dark-intelligence/<category>/<subcategory>/`
   - These are private resources not publicly shared
   - Used to inform implementations, generate test data, validate calculations
   - Include: problem statements, known inputs/outputs, solution methodology

Add to the research brief under `university_resources` and `worked_examples`.

### Step 6 — Document Download Tasks

For each standard not yet available locally:

1. **First**: check doc index for existing copies (`og_standards`, `ace_standards`)
2. **Second**: check O&G Standards SQLite at `/mnt/ace/O&G-Standards/_inventory.db`
3. **Third**: search public sources (standard body websites, university repos, OpenCourseWare)
4. **Fourth**: search university digital libraries (MIT OCW, Stanford, TU Delft open access)
5. **Fifth**: flag as `paywalled — manual download required` if not freely available

Hand off actual downloads to the `doc-research-download` skill.

## Research Brief Template

```yaml
# research-brief-<category>-<subcategory>.yaml
category: "<category>"
subcategory: "<subcategory>"
generated: "YYYY-MM-DD"

applicable_standards:
  - id: "<STANDARD-ID>"
    title: "<full title>"
    org: "<DNV/API/ISO/etc>"
    status: "available|needs_download|paywalled"
    doc_path: "<path in index or null>"
    key_sections: ["Sec X.Y — relevant topic"]

available_documents:
  - path: "<path from index>"
    source: "<og_standards|ace_standards|etc>"
    summary: "<from Phase B if available>"
    relevance: "high|medium|low"

download_tasks:
  - standard: "<STANDARD-ID>"
    url: "<where to find it>"
    notes: "paywalled — check ace_standards first"

key_equations:
  - name: "<equation name>"
    standard: "<STANDARD-ID>"
    section: "<Sec X.Y>"
    latex: "<LaTeX if known>"
    description: "<what it computes>"

university_resources:
  - source: "<textbook/course/lecture>"
    title: "<title>"
    author: "<author or institution>"
    relevance: "high|medium|low"
    archived_at: "knowledge/dark-intelligence/<category>/<subcategory>/<filename>"
    worked_examples_count: N
    notes: "<what makes this useful>"

worked_examples:
  - source: "<STANDARD-ID or textbook>"
    section: "<Sec X.Y or Ch N>"
    description: "<example problem description>"
    inputs: {}
    expected_output: {}
    use_as_test: true  # flag for TDD test generation

implementation_target:
  repo: "<digitalmodel|worldenergydata|etc>"
  module: "<discipline>/<module>"
  existing_code: "<path if any>"
  calc_report_template: "examples/reporting/<name>.yaml"
```

## AC Checklist

- [ ] Standards ledger queried for domain
- [ ] Doc index searched with category and subcategory keywords
- [ ] Capability map cross-referenced for implementation status
- [ ] University/academic resources searched (textbooks, coursework, OCW)
- [ ] Worked examples with known answers identified for TDD tests
- [ ] Coursework materials archived in `knowledge/dark-intelligence/<category>/`
- [ ] Research brief YAML saved to `specs/capability-map/research-briefs/`
- [ ] Download tasks identified with availability status
- [ ] Brief reviewed for completeness before handing off to implementation WRK
