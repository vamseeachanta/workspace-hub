# Content Pipeline: Repo Knowledge to aceengineer.com

> End-to-end pipeline for converting internal engineering knowledge into client-facing website content.

## Overview

The workspace-hub repository contains deep engineering knowledge across multiple domains. This pipeline transforms that knowledge into publication-ready content for aceengineer.com, driving SEO, demonstrating capability, and generating leads.

## Content Sources

| Source | Location | Page Count | Content Type |
|--------|----------|------------|--------------|
| Engineering wiki | `knowledge/wikis/engineering/wiki/` | 75 | Methodology, tools, standards |
| Marine engineering wiki | `knowledge/wikis/marine-engineering/wiki/` | 19,170 | Offshore engineering, CP, mooring |
| Naval architecture wiki | `knowledge/wikis/naval-architecture/wiki/` | 45 | Ship design, hydrostatics, stability |
| Maritime law wiki | `knowledge/wikis/maritime-law/wiki/` | 20 | Cases, conventions, liability |
| Methodology docs | `docs/methodology/published/` | 4 | Compound engineering, enforcement |
| Engineering skills | `.claude/skills/` | 690+ | OrcaFlex, FEA, standards, CFD |

## Pipeline Architecture

```
Source (wiki markdown)
    |
    v
Transform (wiki-to-website.py)
    - Strip internal references (issue numbers, file paths, cross-wiki links)
    - Add SEO metadata (title, description, keywords, canonical URL)
    - Add call-to-action sections
    - Generate navigation structure
    |
    v
Stage (docs/content-pipeline/output/)
    - Website-ready markdown with YAML frontmatter
    - One file per page, organized by domain
    |
    v
Review (manual or automated)
    - Technical accuracy check
    - Brand voice consistency
    - CTA placement
    |
    v
Publish (aceengineer.com)
    - Static site generator (Hugo/MkDocs) or direct HTML
    - Deploy to hosting
```

## Transform Rules

The conversion script (`scripts/content/wiki-to-website.py`) applies these transformations:

1. **Strip internal references**: Remove `#NNNN` issue numbers, relative file paths, internal cross-wiki links
2. **Remove internal metadata**: Strip `sources:` entries that reference internal seed files
3. **Preserve technical depth**: Keep all tables, equations, code blocks, and parameter values
4. **Add SEO frontmatter**: Generate title, description, keywords, and canonical URL
5. **Add CTA sections**: Append call-to-action linking to contact page
6. **Clean cross-references**: Convert internal wiki links to public-facing section links or remove them
7. **Add author attribution**: Credit ACE Engineer as the content author

## Directory Structure

```
docs/content-pipeline/
    README.md                    # This file
    content-calendar.md          # Publication priority and schedule
    output/                      # Generated website-ready pages
        engineering/             # Engineering methodology pages
        marine/                  # Marine/offshore engineering pages
        standards/               # Standards reference pages
        services/                # Service description pages (from skills)
```

## Usage

Generate all website-ready pages:

```bash
uv run scripts/content/wiki-to-website.py
```

Generate pages for a specific domain:

```bash
uv run scripts/content/wiki-to-website.py --domain engineering
uv run scripts/content/wiki-to-website.py --domain marine
uv run scripts/content/wiki-to-website.py --domain standards
```

Generate a single page:

```bash
uv run scripts/content/wiki-to-website.py --page knowledge/wikis/engineering/wiki/concepts/cathodic-protection-design.md
```

## Current State

- **32 pages generated** across engineering concepts, standards, tool references, and incident analyses
- **0 internal references** remaining in output (issue numbers, file paths, cross-wiki links stripped)
- **SEO frontmatter** on every page: title, description, keywords, canonical URL, author
- **CTA block** appended to every page linking to aceengineer.com/contact
- See `content-calendar.md` for publication priority and schedule (5 waves, weeks 1-5)

## Related

- Issue #2022 -- knowledge-to-website content pipeline
- Issue #2030 -- methodology docs published (completed)
- `docs/methodology/published/` -- already-published methodology pages
- `docs/methodology/knowledge-to-website-pipeline.md` -- earlier pipeline design doc
