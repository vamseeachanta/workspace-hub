# Project `<PROJECT_SHORT_NAME>` — `<CLIENT_SHORT_NAME>` engagement

Navigation aid for this project's wiki content. **No strict frontmatter required** on this file — the [`check-wiki-sibling-frontmatter.py`](../../../../../scripts/enforcement/check-wiki-sibling-frontmatter.py) enforcement script explicitly excludes `README.md` basenames from `projects/**/*.md` validation (r2-F4 fix per [#2778](https://github.com/vamseeachanta/workspace-hub/issues/2778)).

## Layout

| Subdirectory | Contents |
|---|---|
| `raw/` (optional, post-bootstrap) | Local navigation placeholder only. Raw inputs remain in authorized external storage; the directory and its contents are not part of the initial scaffold. |
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

## How this project folder is instantiated

Project folders are a post-bootstrap operation. Use repository-local tooling to
copy this skeleton, resolve `<PROJECT_SHORT_NAME>`, and register that project in
the authoritative private registry. Do not create or copy raw-source content as
part of project-folder instantiation.
