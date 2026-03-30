---
name: repo-structure-tier-classification-determines-which-rules-apply
description: 'Sub-skill of repo-structure: Tier Classification (Determines Which Rules
  Apply).'
version: 1.4.0
category: workspace
type: reference
scripts_exempt: true
---

# Tier Classification (Determines Which Rules Apply)

## Tier Classification (Determines Which Rules Apply)


| Tier | Repos | Rules |
|------|-------|-------|
| **Python package** | assetutilities, digitalmodel, worldenergydata, assethold, pdf-large-reader | Full src/ layout — ALL rules below apply |
| **Admin/tooling** | aceengineer-admin, aceengineer-website, pyproject-starter | src/ layout applies to Python; website = content/ not src/ |
| **Client/portfolio** | frontierdeepwater, doris, saipem, acma-projects | EXEMPT — follow client conventions; indexing not API surface |

Client/portfolio repos must NOT be refactored to the Python layout. Do not open WRK items
for structural changes in those repos.

---
