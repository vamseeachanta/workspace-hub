# Research & Literature — Detailed Workflow Steps

## Step 1 — Query the Standards Ledger

Find standards already tracked for the domain:

```bash
uv run --no-project python scripts/data/document-index/query-ledger.py \
  --domain <category> --verbose
```

Record each standard's status (`gap`, `done`, `wrk_captured`, `reference`).

## Step 2 — Query the Document Index

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

## Step 3 — Cross-Reference Capability Map

Identify what is implemented vs. gap in the target repo:

```bash
uv run --no-project python -c "
import yaml
with open('.planning/capability-map/digitalmodel.yaml') as f:
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

## Step 4 — Produce the Research Brief

Save as `.planning/capability-map/research-briefs/<category>-<subcategory>.yaml`
using the research brief template (see [templates.md](templates.md)).

## Step 5 — Search University & Academic Resources

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

## Step 6 — Document Download Tasks

For each standard not yet available locally:

1. **First**: check doc index for existing copies (`og_standards`, `ace_standards`)
2. **Second**: check O&G Standards SQLite at `/mnt/ace/O&G-Standards/_inventory.db`
3. **Third**: search public sources (standard body websites, university repos, OpenCourseWare)
4. **Fourth**: search university digital libraries (MIT OCW, Stanford, TU Delft open access)
5. **Fifth**: flag as `paywalled — manual download required` if not freely available

Hand off actual downloads to the `doc-research-download` skill.

## Step 7 — Deep Online Research

Use WebSearch to find freely available PDFs, papers, and technical references
for standards identified as `needs_download` or `paywalled`:

```bash
# Generate research brief from existing data sources first
uv run --no-project python scripts/data/research-literature/research-domain.py \
  --category <category> --repo <repo>
```

Then use WebSearch/WebFetch to find:
- Free PDFs from standard body websites (DNV Veracity, API publications)
- Open-access papers from OnePetro, ISOPE, OTC archives
- University lecture notes and textbook chapters
- Technical guidance documents from BOEM, BSEE, HSE UK

Update the research brief with discovered URLs and availability status.

## Step 8 — Download Script Generation

Generate a curl/wget-based download script for the domain:

```bash
uv run --no-project python scripts/data/research-literature/research-domain.py \
  --category <category> --repo <repo> --generate-download-script
```

This creates `download-literature.sh` at the domain's `/mnt/ace/` literature path.
The script sources `scripts/lib/download-helpers.sh` and supports `--dry-run`.

After generation, manually curate the script:
1. Add discovered URLs from Step 7
2. Set proper filenames: `<author>-<year>-<short-title>.pdf`
3. Run `--dry-run` to verify
4. Execute and validate with `file *.pdf` (reject HTML/WAF responses)
