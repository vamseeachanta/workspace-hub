---
name: wiki-context
description: "Auto-query llm-wiki domains for relevant context before executing domain tasks"
version: 1.0.0
metadata:
  hermes:
    tags: [wiki, context, retrieval, knowledge]
    category: research
    related_skills: [llm-wiki, engineering-issue-workflow]
---

# Wiki Context Retrieval

Query the llm-wiki knowledge base for relevant context before executing engineering domain tasks.
Bridges the gap between wiki knowledge and agent execution per the retrieval contract (#2208).

## When This Skill Activates

- Before any engineering domain task (OrcaFlex, mooring, pipeline, structural, CFD, naval architecture)
- When an agent needs background knowledge for issue planning or execution
- When the retrieval contract (#2208) requires consulting wiki sources
- When working on issues labeled `domain:knowledge-management` or `domain:knowledge`

## Quick Usage

```bash
# Query across all domain wikis
bash scripts/knowledge/wiki-query-context.sh "mooring line failure HMPE"

# Query specific domains only
bash scripts/knowledge/wiki-query-context.sh "pipeline integrity corrosion" --domains engineering,marine-engineering

# JSON output for programmatic use
bash scripts/knowledge/wiki-query-context.sh "OrcaFlex VIV analysis" --json
```

## How to Use in Agent Workflows

### Step 1: Identify Query Keywords
Extract 3-5 keywords from the current task. Include:
- Domain terms (mooring, pipeline, structural, hydrodynamic)
- Tool names (OrcaFlex, OrcaWave, AQWA, OpenFOAM)
- Standards codes (DNV-RP-C205, API 2SK, OCIMF MEG4)

### Step 2: Run Wiki Query
```bash
bash scripts/knowledge/wiki-query-context.sh "<keywords>" --domains <relevant_domains>
```

The script queries each wiki domain via `llm_wiki.py query` and checks the cross-links
JSONL store for entity matches. Results are ranked by relevance.

### Step 3: Inject Context
Take the top 3 results and use them as background context for your task:
- Read the referenced wiki page(s) for detailed knowledge
- Note any cross-wiki links that connect to other domains
- Cite wiki pages in your output (e.g., "per wiki:engineering/concepts/pipeline-integrity")

### Step 4: Log Consultation
Record which wiki pages were consulted in your output:
```
Wiki sources consulted:
- engineering/concepts/pipeline-integrity-assessment (score: 0.85)
- marine-engineering/entities/pipeline-integrity (score: 0.72)
- cross-link: shared entities [API 579, DNV-RP-F101]
```

## Domain Wiki Map

| Domain | Wiki Path | Typical Topics |
|--------|-----------|---------------|
| engineering | `knowledge/wikis/engineering/` | Methodology, compound patterns, standards |
| marine-engineering | `knowledge/wikis/marine-engineering/` | Offshore, mooring, riser, hydrodynamics |
| naval-architecture | `knowledge/wikis/naval-architecture/` | Ship design, stability, seakeeping |
| maritime-law | `knowledge/wikis/maritime-law/` | Legal frameworks, cases, regulations |
| personal | `knowledge/wikis/personal/` | Career learnings (rarely queried by agents) |

## Cross-Links Store

The JSONL cross-link store at `knowledge/wikis/cross-links.jsonl` contains inter-wiki
relationships with typed evidence (slug-similarity, shared-tags, entity-coref,
shared-provenance, standards-chain). Use it to discover related pages across domains.

## Integration with Retrieval Contract (#2208)

The retrieval contract requires minimum 3 consulted sources per issue plan. Wiki
context counts as a consulted source. Record findings in the "Resource Intelligence
Summary" section of plans.
