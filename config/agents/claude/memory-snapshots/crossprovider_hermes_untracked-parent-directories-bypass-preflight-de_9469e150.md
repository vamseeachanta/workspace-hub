---
name: crossprovider hermes untracked-parent-directories-bypass-preflight-de
description: Untracked parent directories bypass preflight detection
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-safety, file-detection, validation-gap]
---

Preflight dirty-file checks scanning for specific paths (e.g., `.codex/skills`) miss untracked parent directories reported by git as `?? .codex/`. Must explicitly check git porcelain output for parent-level untracked entries when validating path-based ownership.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
