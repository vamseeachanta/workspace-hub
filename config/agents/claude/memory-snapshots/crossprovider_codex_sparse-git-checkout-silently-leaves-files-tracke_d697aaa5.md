---
name: crossprovider codex sparse-git-checkout-silently-leaves-files-tracke
description: Sparse Git checkout silently leaves files tracked despite .gitignore
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, sparse-checkout, verification]
---

Sparse-checkout mode can leave files staged/tracked that `.gitignore` claims to exclude. Explicit `git rm --sparse` or index correction required. Empirically verify with `git check-ignore` rather than assuming rules apply.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
