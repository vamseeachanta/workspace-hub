---
name: crossprovider gemini system-level-package-installs-must-preserve-down
description: System-level package installs must preserve downstream command contracts
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [ci-health, uv, install-patterns, tool-coupling]
---

When transitioning to `uv pip install --system` instead of `uv sync`, verify that downstream tools (pytest, mypy, flake8) in the workflow don't depend on `uv run` wrapping. If they run bare commands, they expect system-installed tools; switching the install pattern breaks the contract.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
