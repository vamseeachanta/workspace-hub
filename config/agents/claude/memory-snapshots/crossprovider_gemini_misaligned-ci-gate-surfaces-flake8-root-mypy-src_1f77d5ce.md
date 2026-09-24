---
name: crossprovider gemini misaligned-ci-gate-surfaces-flake8-root-mypy-src
description: Misaligned CI gate surfaces (flake8 root, mypy src/) create asymmetric failures
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [ci-gates, surface-alignment, workflow-design]
---

When linting and type-checking gates scan different directory trees, failures cluster differently by platform/target; auxiliary broken files in root-level directories block one gate without visible impact on the other. #2459 shows flake8 failing on linux/macos due to root-level `.agent-os/modules/prompt_enhancement.py` syntax errors, while mypy fails windows-only due to src/-scoped errors. Symmetric gate targets prevent this masking and keep CI failures traceable.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
