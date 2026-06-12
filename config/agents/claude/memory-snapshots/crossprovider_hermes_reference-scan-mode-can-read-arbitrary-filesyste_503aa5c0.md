---
name: crossprovider hermes reference-scan-mode-can-read-arbitrary-filesyste
description: Reference-scan mode can read arbitrary filesystem trees
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [safety, checker-design, path-validation]
---

Checker mode `--reference-scan-root <path>` accepts any path and reads all text files under it via `rglob`. If run manually with an operator-supplied path outside the repo, it can inspect unintended directories. Require repo-scoped paths or environment validation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
