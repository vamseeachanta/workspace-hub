---
name: crossprovider gemini uv-as-hard-dependency-fail-clearly-on-absence-no
description: uv as hard dependency: fail clearly on absence, no fallback chains
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [dependencies, python, uv]
---

If uv is a declared workspace tool, make it non-optional in scripts. Remove python3/python fallback detection chains. If uv isn't installed, fail with install instruction rather than silently falling back to system Python.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
