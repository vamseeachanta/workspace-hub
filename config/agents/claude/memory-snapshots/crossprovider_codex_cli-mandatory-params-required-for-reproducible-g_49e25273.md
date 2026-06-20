---
name: crossprovider codex cli-mandatory-params-required-for-reproducible-g
description: CLI mandatory params required for reproducible generated artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-06-19
  tags: [reproducibility, generated-artifacts]
---

If generated output (JSONL/JSON/HTML) is repo-committed, its CLI must be reproducible from repo state. Optional parameters with silent fallbacks (missing catalog → default rows) break reproducibility. Make parameters mandatory or document fallbacks in artifact metadata.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
