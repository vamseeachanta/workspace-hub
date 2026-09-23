---
name: crossprovider codex published-package-deletion-requires-full-repo-se
description: Published package deletion requires full-repo search and deprecation shims
metadata:
  type: reference
  source: codex
  bridged: 2026-07-30
  tags: [deletion-safety, published-packages, import-mechanisms, public-api]
---

Symbol-name grep cannot detect string-based imports (importlib/__getattr__, pickle payloads, config-driven loading). Before deleting from published packages, search entire repo including tests, docs, packaging config, doctest, and Sphinx. Provide deprecation shims forwarding to modern equivalents to avoid breaking external consumers who rely on __all__ entries or direct module imports.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
