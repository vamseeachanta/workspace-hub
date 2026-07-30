---
name: crossprovider codex externalize-normalized-and-curated-data-to-versi
description: Externalize normalized and curated data to versioned storage for source independence
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [architecture, dependencies, reproducibility]
---

Store outputs in external versioned storage rather than depending on connector services or live APIs. This enables reproducible runs, avoids coupling to external services, and keeps the codebase independent of data-access layer changes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
