---
name: crossprovider gemini sys-meta-path-redirection-for-transparent-import
description: sys.meta_path redirection for transparent import compatibility
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [imports, backward-compat, deprecation]
---

Use importlib.abc.MetaPathFinder + RedirectLoader on sys.meta_path to transparently redirect old import paths to new ones, emitting DeprecationWarning once per session via a _warned set. Enables module splits without breaking existing callers.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
