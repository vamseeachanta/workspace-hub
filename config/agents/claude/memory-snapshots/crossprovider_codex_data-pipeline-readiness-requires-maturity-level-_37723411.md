---
name: crossprovider codex data-pipeline-readiness-requires-maturity-level-
description: Data pipeline readiness requires maturity-level separation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [data-pipeline, reproducibility, publishing, versioning]
---

When auditing data for external surfaces (HuggingFace, web publication), distinguish: committed tracked artifacts (canonical, versioned, reproducible from sources), locally generated untracked outputs (ephemeral, rebuild on demand), and live external state (may diverge from repo). Being "present in checkout" is not proof of publishability. Verify that the published version reproduces deterministically from committed repo sources only, without downloading/patching live external data.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
