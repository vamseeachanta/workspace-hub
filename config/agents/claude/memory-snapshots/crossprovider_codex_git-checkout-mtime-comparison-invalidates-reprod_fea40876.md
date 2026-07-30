---
name: crossprovider codex git-checkout-mtime-comparison-invalidates-reprod
description: Git checkout mtime comparison invalidates reproducibility claims
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [reproducibility, build-systems, git]
---

File modification times after `git checkout` can exceed committed generated artifacts despite identical content, due to coarse timestamp resolution. Reproducibility checks using mtime (`artifact.mtime < input.mtime`) fail immediately after clean checkout, even with byte-identical builds. Use content-based digests, build provenance metadata, or explicit version/dependency pinning instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
