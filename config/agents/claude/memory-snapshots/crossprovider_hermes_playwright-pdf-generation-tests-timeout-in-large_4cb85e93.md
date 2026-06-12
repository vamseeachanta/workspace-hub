---
name: crossprovider hermes playwright-pdf-generation-tests-timeout-in-large
description: Playwright PDF generation tests timeout in large repos without explicit pytest timeout
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [pytest, playwright, pdf-generation, large-repo, digitalmodel]
---

Tests with Playwright PDF fixture timeout >30s in workspace-hub (19K+ files) due to heavy imports during report HTML→PDF generation. Mitigate with `uv run pytest -k test_name -s --timeout=60` or mark PDF test as optional if Playwright unavailable.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
