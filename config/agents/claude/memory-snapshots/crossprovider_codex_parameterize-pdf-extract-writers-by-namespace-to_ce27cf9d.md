---
name: crossprovider codex parameterize-pdf-extract-writers-by-namespace-to
description: Parameterize PDF extract writers by namespace to support multiple content types
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, writer-pattern, separation-of-concerns]
---

Pass namespace (`'standards'`, `'papers'`, etc.) to writer helpers instead of hardcoding paths. Let the extractor decide routing, then writers place output under the correct namespace. This keeps the extraction logic separate from the storage policy and allows new content types without replicating writers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
