---
name: crossprovider codex baseline-reproducibility-audit-in-isolated-copie
description: Baseline reproducibility audit in isolated copies
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [verification, baseline, methodology]
---

Before implementing changes, run read-only baseline passes on copies of the repo (never the working tree). This establishes determinism and side-effect surfaces without risking tracked files. Varied runtime and transient state become visible only in baseline runs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
