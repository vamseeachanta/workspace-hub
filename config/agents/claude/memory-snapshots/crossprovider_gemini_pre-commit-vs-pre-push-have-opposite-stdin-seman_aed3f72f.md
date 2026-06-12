---
name: crossprovider gemini pre-commit-vs-pre-push-have-opposite-stdin-seman
description: Pre-commit vs pre-push have opposite stdin semantics
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [git-hooks, pre-commit]
---

pre-commit does NOT pipe stdin; uses `PRE_COMMIT=1` env var + file filtering. pre-push receives stdin with refs. Can't use same git-diff logic in both. Detect environment via `PRE_COMMIT` env var to branch behavior.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
