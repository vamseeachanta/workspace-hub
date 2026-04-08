---
title: "Knowledge-to-Website Pipeline"
tags: [gtm, website, publishing, content-pipeline, aceengineer]
sources:
  - knowledge-to-website-pipeline-doc
added: 2026-04-08
last_updated: 2026-04-08
---

# Knowledge-to-Website Pipeline

Turn repo knowledge bases into client-facing aceengineer.com content. The repo contains deep engineering knowledge that clients find valuable -- wiki pages, skills, methodology docs, and parametric demo reports.

## Pipeline Architecture

```
Source (repo) -> Normalize -> Stage -> Review -> Publish
```

### Phase 1: Wiki to Static Pages
Convert wiki markdown to styled HTML with navigation, cross-links, author attribution, call-to-action, and SEO metadata.

### Phase 2: Skills as Service Pages
Each engineering skill becomes a service description page.
729 engineering skills = 100+ potential service pages.

### Phase 3: Methodology as Marketing
Published methodology docs serve dual purpose:
1. Technical credibility
2. Client education

### Phase 4: Daily Automation
Cron-based auto-publish of new wiki pages and skills to site.

## Content Inventory

| Content Type | Quantity | Source |
|---|---|---|
| Wiki pages (marine engineering) | 19K+ | knowledge/wikis/marine-engineering/ |
| Wiki pages (naval architecture) | 45 | knowledge/wikis/naval-architecture/ |
| Engineering skills | 729 | .claude/skills/ |
| Methodology docs | 6 | docs/methodology/ |

## Cross-References

- **Related issue**: #2022 (publish repo knowledge bases)
- **Related issue**: #2016 (client conversion pipeline)
- **Related concept**: [[compound-engineering]]
- **Related entity**: [LLM Wiki Tool](../entities/llm-wiki-tool.md)
