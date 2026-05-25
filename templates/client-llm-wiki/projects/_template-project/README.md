# Project `<PROJECT_SHORT_NAME>` — `<CLIENT_SHORT_NAME>` engagement

Navigation aid for this project's wiki content. **No strict frontmatter required** on this file — the [`check-wiki-sibling-frontmatter.py`](../../../../../scripts/enforcement/check-wiki-sibling-frontmatter.py) enforcement script explicitly excludes `README.md` basenames from `projects/**/*.md` validation (r2-F4 fix per [#2778](https://github.com/vamseeachanta/workspace-hub/issues/2778)).

## Layout

| Subdirectory | Contents |
|---|---|
| `raw/` | Raw inputs as received from the client / sourced from `/mnt/ace/<CLIENT_RAW_ROOT>/<PROJECT_SHORT_NAME>/`. Filename-preserved. |
| `extracted/` | Cleaned / extracted intermediate artifacts (CSVs, JSON, normalized text). Derived from `raw/`. |
| `methodology/` | Client-specific methodology notes — how the calculations / extractions / analyses were performed. References generic concept pages in `vamseeachanta/llm-wiki` via wiki slug (not duplicate copies). |
| `results/` | Final client-facing calc results, reports (HTML/PDF/DOCX), evidence packs. |

## Frontmatter convention (for content pages, not this README)

Every `.md` file under this project that is content (not navigation) must carry frontmatter conforming to [`.claude/rules/wiki-sibling-routing.md`](../../../../../.claude/rules/wiki-sibling-routing.md):

```yaml
---
visibility: private-client-llm-wiki
client: <CLIENT_SHORT_NAME>
project: <PROJECT_SHORT_NAME>
---
```

When `<PROJECT_SHORT_NAME>` is added to the `projects:` list of `<CLIENT_SHORT_NAME>` in `config/client-wikis.yml` (workspace-hub), Rule E activates — staged content with a `project:` value not in the list fails the enforcement check.

## Promotion to generic `llm-wiki`

Methodology or sanitized worked examples may be promoted from this project's `methodology/` to the generic `vamseeachanta/llm-wiki` repo via the abstraction-gate skill: `research/llm-wiki-public-private-routing` (Skill D). The original here remains as the client-attributed audit-trail; the public page in `llm-wiki` is an abstracted copy, never a `git mv`.

## How this project folder was instantiated

Per the `coordination/client-llm-wiki-factory` skill Step 5b:

```bash
cp -a /mnt/local-analysis/workspace-hub/templates/client-llm-wiki/projects/_template-project/. \
      /mnt/local-analysis/llm-wiki-<CLIENT_SHORT_NAME>/projects/<PROJECT_SHORT_NAME>/
```

Then substitute the two placeholders (`<CLIENT_SHORT_NAME>`, `<PROJECT_SHORT_NAME>`) and add `<PROJECT_SHORT_NAME>` to the client's `projects:` list in `config/client-wikis.yml`.
