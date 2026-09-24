---
name: crossprovider gemini ecosystem-ci-templates-are-manual-discovered-fir
description: Ecosystem CI templates are manual-discovered; first author becomes canonical reference
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [template-discovery, ecosystem-hygiene, reuse]
---

Before authoring a new CI workflow (markdown-lint, link-check, etc.), grep ecosystem siblings (`digitalmodel/.github/workflows/`, `assethold/.github/workflows/`) for existing templates. #2443 discovered no markdown-lint or lychee workflow exists across workspace-hub ecosystem, forcing this plan to author the first canonical pair. First implementation becomes the reference for cross-repo reuse.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
