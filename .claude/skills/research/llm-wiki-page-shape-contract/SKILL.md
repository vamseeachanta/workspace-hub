---
name: llm-wiki-page-shape-contract
description: >-
  Enforce the page-shape contract when a repo-side document or analysis output
  gets converted into an llm-wiki page. Use when (1) running
  `scripts/knowledge/llm_wiki.py ingest`, (2) writing or rewriting a wiki page
  from docs/reports/*, docs/handoffs/*, scripts/review/results/*, or calc
  citation outputs, (3) deciding whether a page should be split into a folder of
  sub-pages, (4) reviewing wiki PRs for length / diagram / divide-and-conquer
  compliance. Codifies the Karpathy + Astro-Han + lewislulu page rules applied
  to workspace-hub's domain-wiki layout under
  /mnt/local-analysis/llm-wiki/wikis/<domain>/. Sibling to research/llm-wiki
  (which owns the CLI ops) — this skill is the quality gate every converted
  page must clear before commit.
metadata:
  category: research
  related_skills:
    - research/llm-wiki
    - research/llm-wiki-cadence-governance
    - data/doc-intelligence-promotion
    - coordination/llm-wiki-roadmap-integration
  related_issues:
    - vamseeachanta/workspace-hub#2374
    - vamseeachanta/workspace-hub#2392
    - vamseeachanta/workspace-hub#2727
  references:
    - references/page-templates.md
---

# llm-wiki page-shape contract

When a repo-side artifact (analysis output, handoff, calc result, review
finding, ingested external source) becomes a wiki page, this skill is the
binding contract on **page shape**. It sits above `research/llm-wiki` and
above `data/doc-intelligence-promotion` as the quality gate every converted
page must clear before it commits.

Pattern provenance: distills [Karpathy's gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f),
[Astro-Han/karpathy-llm-wiki](https://github.com/Astro-Han/karpathy-llm-wiki),
and [lewislulu/llm-wiki-skill](https://github.com/lewislulu/llm-wiki-skill).
Page-rule choices match lewislulu's because they are the strictest and produce
the most lintable corpus.

---

## When this skill applies

| Trigger | Apply contract? |
|---|---|
| Converting `docs/reports/<analysis>.md` → wiki | **YES** |
| Converting `docs/handoffs/*.md` → wiki | **YES** (after [#2374](https://github.com/vamseeachanta/workspace-hub/issues/2374) queue marks it `promoted`) |
| Calc-citation sidecar → wiki `standards/<code-id>.md` | **YES** |
| `scripts/review/results/*.md` → wiki | **CANDIDATE-ONLY** ([#2374](https://github.com/vamseeachanta/workspace-hub/issues/2374)); never direct-write |
| External source (article, paper, LinkedIn post) via `llm_wiki.py ingest` | **YES** |
| Editing an existing wiki page in place | **YES** (length/diagram/divide rules still apply) |
| Writing to client-private wiki ([#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746)) | **YES** — same shape contract; different boundary rules per [#2727](https://github.com/vamseeachanta/workspace-hub/issues/2727) |
| Writing to vendor-brochure / off-repo intel notes | **NO** — those are off-repo per service-provider data routing |

---

## Source-class → page-type routing

This is the canonical mapping. If a source class is not listed, default to
**candidate-only** (file in [#2374](https://github.com/vamseeachanta/workspace-hub/issues/2374) queue, don't direct-write).

| Source class | Wiki page type | Path |
|---|---|---|
| Analysis report (`docs/reports/<topic>.md`) | summary + concept update | `wikis/<domain>/summaries/<slug>.md` + ripple update on concepts |
| Calc-citation sidecar (per [`calc-citation-contract.md`](../../rules/calc-citation-contract.md)) | standards page | `wikis/<domain>/standards/<code-id>.md` (frontmatter must satisfy [#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471)) |
| Handoff (`docs/handoffs/*.md`) | concept update (rarely new page) | ripple update on existing concepts; **never** a new summary |
| Review result (`scripts/review/results/*.md`) | candidate-only | [#2374](https://github.com/vamseeachanta/workspace-hub/issues/2374) queue → reviewed → promote |
| External article/post (LinkedIn, blog, paper) | summary + concept update | `wikis/<domain>/sources/<slug>.md` + concept update (per `feedback_llm_wiki_external_post_ingest_workflow`) |
| Domain knowledge synthesis | concept page or methodology page | `wikis/<domain>/concepts/<slug>.md` or `wikis/<domain>/methodology/<slug>.md` |
| Entity (person, tool, org, paper) | entity page | `wikis/<domain>/entities/<slug>.md` |
| Large binary (model weights, PDF >10 MB, dataset) | **ref pointer**, not copy | `wikis/<domain>/sources/refs/<slug>.md` with `external_path:` frontmatter |

---

## Page-shape rules

These are exit-0 / exit-1 checks. A page that violates any of them is not
ready to commit.

### Rule 1 — Length ceiling, divide-and-conquer

| Page type | Word target | Hard ceiling |
|---|---|---|
| Concept | 400–1200 | **1200** |
| Folder-split `index.md` | 150–400 | 500 |
| Sub-page under folder-split | 400–1200 | 1200 |
| Entity | 200–500 | 700 |
| Summary | 150–400 | 500 |
| Standards page | 300–1200 | 1200 (split by topic, not section) |
| Methodology page | 400–1200 | 1200 |

**If a page would exceed 1200 words, split it. Do not write a single fat file.**

Split procedure:
1. Create `wikis/<domain>/concepts/<topic>/`
2. Write `wikis/<domain>/concepts/<topic>/index.md` (150–400 words: definition + one-line map of sub-pages)
3. Write each aspect as `wikis/<domain>/concepts/<topic>/<aspect>.md` (400–1200 words each)
4. Update `wikis/<domain>/index.md` with the indented hierarchy
5. Update inbound wikilinks from `[[<topic>]]` to `[[<topic>/<aspect>]]` where the link actually targets one aspect

**Signals you need to split (apply before hitting 1200):**
- Three or more `##` top-level sections each with `###` subsections
- You find yourself wanting to write `[[Page#Section]]` — that section deserves its own page
- Two or more distinct concepts share the page but are not explored
- Cross-cutting subsections (e.g., "Variants", "Failure modes") that recur across multiple `##` headers

### Rule 2 — Diagrams mandatory in Mermaid, formulas in KaTeX

- **Any** flow, sequence, hierarchy, or state diagram → Mermaid only. ASCII art is banned. ASCII boxes rot fast, can't be annotated, and break renderers.
- **Any** formula → KaTeX. Inline `$f(x) = \sum_i w_i x_i$` or block `$$...$$`.
- Both render in the existing wiki preview surface and in Obsidian/web viewers when contributors clone the wiki repo locally.

### Rule 3 — Wikilinks are first-class, raw links are second-class

- Internal references between wiki pages: `[[Concept A]]` (Obsidian-style)
- Internal references that target a specific aspect: `[[concepts/<topic>/<aspect>]]`
- External references: standard markdown links with provenance, never bare URLs
- Every page links **both directions**: the page references its sources AND every source page links back via the consuming page

### Rule 4 — Required frontmatter

Every page MUST carry YAML frontmatter. Minimum fields per page type are in
`references/page-templates.md`. Universal-required fields:

```yaml
---
title: <Title>
type: concept | entity | summary | standards | methodology | ref
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [<source-slug-1>, <source-slug-2>]
tags: [<tag-1>, <tag-2>]
---
```

Standards pages additionally require `code_id`, `publisher`, `revision` per
[#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471) so the
calc citation contract resolves.

### Rule 5 — Cascade updates (one source ≠ one page)

A single new source typically touches **5–15 wiki pages**, not one. After
writing the primary summary or concept page:

1. Scan same-domain pages for content the new source materially affects
2. Update every affected page's body + bump `updated:` frontmatter date
3. Update `wikis/<domain>/index.md` for every new or materially-changed page
4. Append a log entry to `wikis/<domain>/log.md` (see `log-guide` precedent from lewislulu):
   ```
   ## [YYYY-MM-DD] ingest | <primary page>
   - Updated: <cascade page 1>
   - Updated: <cascade page 2>
   ```

If you only touched one page, ask yourself why. Either (a) the source was
genuinely narrow (acceptable — note this in the log entry), or (b) you
missed ripple effects (re-scan).

### Rule 6 — Contradictions are annotated, never silently overwritten

If a new source contradicts existing wiki content:

- Do **not** silently rewrite to match the newer source
- Annotate the disagreement in-line with source attribution
- Cross-link both versions
- File an audit entry per `research/llm-wiki-audit-feedback-loop` if the contradiction needs human resolution

Reason: this is what makes the wiki defensible. A wiki that quietly drifts
toward the latest source loses provenance and trust.

### Rule 7 — Input vs output layer distinction (Karpathy three-layer pattern)

Each domain wiki maintains an explicit separation between the **input
layer** (raw, immutable source material) and the **output layer** (compiled
knowledge pages):

```
wikis/<domain>/
├── sources/             ← INPUT: immutable raw sources (read-only after ingest)
│   ├── <slug>.md            article / paper / report / handoff snapshot
│   └── refs/<slug>.md       pointer files for large binaries
├── concepts/            ← OUTPUT: compiled concept pages
├── entities/            ← OUTPUT: people / tools / orgs / papers
├── summaries/           ← OUTPUT: per-source distilled takeaways
├── standards/           ← OUTPUT: code/standard reference pages
├── methodology/         ← OUTPUT: methodology / how-to pages
├── audit/               ← feedback inbox (per research/llm-wiki-audit-feedback-loop)
├── log/                 ← per-day operation log
├── index.md             ← master catalog
└── CLAUDE.md            ← schema: scope, conventions, open questions
```

Rules:

- `sources/` pages are **immutable** once ingested. Corrections to a source's
  *interpretation* go into `summaries/`, `concepts/`, or audit files —
  never into the source page itself.
- Compiled pages (`concepts/`, `entities/`, `summaries/`, `standards/`,
  `methodology/`) reference `sources/` via wikilinks: `[[sources/<slug>]]`.
- The input/output split applies to **both public and private wikis** — same
  shape, different routing rules (see Rule 8).
- **Retrofit policy: on-touch** — existing interleaved pages in a domain
  stay as-is until a page in that domain is materially updated. When you
  touch a page, reorganize the **adjacent pages in that domain subtree**
  into the input/output split as part of the same PR. Do not batch-retrofit
  pages you are not otherwise touching; do not leave a half-split domain
  after a touch. The 14 current domains will converge to the new layout
  over time as work flows through them.
- If an existing domain is fully interleaved at touch time, the touch
  triggers a per-domain split — log the migration in `log/YYYYMMDD.md`
  with a `## [HH:MM] migrate | <domain> sources/<-->output split` entry.

### Rule 8 — Public vs private wiki abstraction gate

Before promoting a page to the **public** llm-wiki repo
(`vamseeachanta/llm-wiki`), the abstraction gate must clear. See
`research/llm-wiki-public-private-routing` for the gate logic; this rule
ties the gate into the page-shape contract.

| Target wiki | Abstraction required? |
|---|---|
| `llm-wiki-<client>` private (per [#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746)) | NO — exact client + project names + raw numbers stay |
| `llm-wiki` public | YES for client project names; CONDITIONAL exception when project name + all key data are publicly available |

Abstraction surface (public wiki only):

- **Client project names** are abstracted by default (e.g., `Project Alpha`
  not `<actual project name>`).
- **Exception**: if the project name is in the public domain (SEC filings,
  press releases, conference papers, regulator records, public reservoir
  databases) AND **all key data being cited is also publicly available**,
  the actual project name can be used. The conjunction is binding — both
  conditions or neither.
- Client identity itself is governed by `.legal-deny-list.yaml` and
  `.claude/rules/legal-compliance.md` — Rule 8 does not relax those.

A page that fails the gate is either (a) re-routed to a private wiki, or
(b) rewritten with the abstraction applied. Never silently committed.

---

## Pre-conversion checklist

Run before writing a single line of wiki content.

- [ ] Source class is in the routing table above (else: file as candidate per [#2374](https://github.com/vamseeachanta/workspace-hub/issues/2374))
- [ ] Data-layer boundary check passes ([#2727](https://github.com/vamseeachanta/workspace-hub/issues/2727)): no vendor-derivative, no client material to public wiki, no raw API dumps
- [ ] Target wiki domain is decided (engineering / marine / naval / process / drilling / geotech / trends / ...) — see `wikis/` for current domain list
- [ ] Target page type is decided (concept / entity / summary / standards / methodology)
- [ ] If standards page: code_id frontmatter triple resolved via [#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471)
- [ ] Existing page at target path checked — merge vs new-page decision made consciously
- [ ] Target wiki is correctly chosen: public `llm-wiki` vs private `llm-wiki-<client>` per Rule 8
- [ ] If public target: abstraction gate cleared per `research/llm-wiki-public-private-routing`
- [ ] Input/output layer split confirmed per Rule 7: sources land in `sources/`, compiled in `concepts/ entities/ summaries/ standards/ methodology/`
- [ ] If source is a binary doc (PDF / DOCX / XLSX / PPTX): pre-extraction estimate computed per `research/llm-wiki-source-extraction-coverage`

## Post-conversion checklist

Run before committing.

- [ ] Length under hard ceiling (else: split per Rule 1)
- [ ] All diagrams Mermaid (else: convert per Rule 2)
- [ ] All formulas KaTeX (else: convert per Rule 2)
- [ ] Frontmatter complete and dated (Rule 4)
- [ ] `wikis/<domain>/index.md` updated for every touched page (Rule 5)
- [ ] `wikis/<domain>/log.md` entry appended (Rule 5)
- [ ] Cascade-update scan run — same-domain pages reviewed for ripple effects (Rule 5)
- [ ] Contradictions annotated, not silently overwritten (Rule 6)
- [ ] Input/output split honored: this commit does not put a source under `concepts/` or vice versa (Rule 7)
- [ ] If on-touch retrofit triggered: adjacent same-domain pages reorganized into the split in this same PR (Rule 7)
- [ ] If public target: abstraction gate verdict recorded in commit message (Rule 8) — `abstraction: applied | not-needed-exception-met | not-applicable-private`
- [ ] If extracted from binary: `extraction_estimate` and `extraction_yield` frontmatter set on the summary page; lost-content inventory included if yield < estimate
- [ ] `uv run scripts/knowledge/llm_wiki.py lint --wiki <domain>` passes

---

## Hand-off back to `research/llm-wiki`

Once a page satisfies this contract:

```bash
# Pre-flight: shape check (manual + lint)
uv run scripts/knowledge/llm_wiki.py lint --wiki <domain>

# Commit: legal sanity scan auto-runs via pre-commit
git add wikis/<domain>/<page>.md wikis/<domain>/index.md wikis/<domain>/log.md
git commit -m "wiki(<domain>): <slug> — <one-line>" -- wikis/<domain>/<page>.md wikis/<domain>/index.md wikis/<domain>/log.md
```

Pathspec form `git commit -m "..." -- <files>` per
`feedback_multi_agent_commit_serialization` — protects against parallel-agent
sweep contamination.

---

## What this skill is NOT

- Not a replacement for `research/llm-wiki` — that skill owns the CLI ops (init / status / ingest / query / lint / batch-ingest)
- Not a replacement for `data/doc-intelligence-promotion` — that skill owns the L2→L3 promotion gate
- Not a replacement for [#2374](https://github.com/vamseeachanta/workspace-hub/issues/2374) — that issue defines the candidate queue from transient artifacts
- Not for off-repo intel notes, vendor brochures, or client-private working drafts (per service-provider data routing matrix)
- Not for general personal notes or daily journals

## Related must-fire rules

- `feedback_llm_wiki_concept_pages_need_public_references` — concept pages need textbooks/DOIs/manuals; LinkedIn-only fails day-one lint
- `feedback_llm_wiki_hyphen_module_path_pattern` — `scripts/data/llm-wiki/` poisons Python dotted-paths; grep for `llm-wiki\.` as P1 smell
- `feedback_html_default_artifact` — wiki pages stay Markdown (skill/rule/wiki content); HTML is for human-facing reports
- `feedback_silent_verdict_flip_defect_class` — standards pages need `section` AND `edition`, not just `code_id`
- `feedback_subagent_write_phantom` — if a subagent writes a wiki page, main session must `ls` the path before believing
