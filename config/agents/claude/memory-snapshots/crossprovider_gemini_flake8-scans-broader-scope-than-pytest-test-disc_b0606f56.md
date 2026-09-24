---
name: crossprovider gemini flake8-scans-broader-scope-than-pytest-test-disc
description: Flake8 scans broader scope than pytest test discovery
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [ci-cd, lint, test-scope]
---

Running `flake8 .` in CI scans tooling paths (`.agent-os/`, `scripts/`, `modules/`) that are outside `tests/` and the importable package, creating false gates on syntax errors unrelated to test execution. Scope flake8 to match pytest's authoritative test paths.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
