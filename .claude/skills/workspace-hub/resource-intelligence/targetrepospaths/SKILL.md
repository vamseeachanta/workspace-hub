---
name: resource-intelligence-targetrepospaths
description: "Sub-skill of resource-intelligence: target_repos\u2192Paths."
version: 1.1.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# target_repos→Paths

## target_repos→Paths


For each repo in `target_repos`, inventory these paths during mining category 4 (Existing code / scripts):

| Repo | Paths to inventory |
|------|--------------------|
| `workspace-hub` | `scripts/`, `.claude/skills/`, `.claude/docs/`, `specs/` |
| `digitalmodel` | `src/digitalmodel/`, `tests/`, `specs/wrk/` |
| `assetutilities` | `src/assetutilities/`, `tests/` |
| `worldenergydata` | `src/worldenergydata/`, `tests/` |
| `assethold` | `src/assethold/`, `tests/` |
| `ogmanufacturing` | `src/ogmanufacturing/`, `tests/` |
| `aceengineer-website` | `content/`, `src/` |
| `aceengineer-admin` | `src/` |
| any other repo | `src/`, `tests/`, `scripts/` (if they exist) |

---
