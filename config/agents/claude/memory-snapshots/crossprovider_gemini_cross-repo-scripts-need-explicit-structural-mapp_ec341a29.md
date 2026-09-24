---
name: crossprovider gemini cross-repo-scripts-need-explicit-structural-mapp
description: Cross-repo scripts need explicit structural mapping
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [multi-repo-scripting, environment-heterogeneity]
---

Tier-1 repos have varying layouts (src/ vs flat, OGManufacturing vs ogmanufacturing capitalization, different config file names). Scripts must map these explicitly via associative arrays or config files, not assume uniformity.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
