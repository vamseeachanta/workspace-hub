---
name: crossprovider gemini bleach-dependency-as-optional-with-fail-closed-s
description: Bleach dependency as optional with fail-closed semantics
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [security, dependencies, html-sanitization]
---

Declare bleach in `pyproject.toml` under a `[project.optional-dependencies.workqueue]` extra, then invoke with `uv run --project . --extra workqueue`. In code, wrap imports with try/except ImportError and fail closed (render placeholder text or escape) when missing. This pattern decouples the sanitizer from core runtime, avoiding installation friction.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
