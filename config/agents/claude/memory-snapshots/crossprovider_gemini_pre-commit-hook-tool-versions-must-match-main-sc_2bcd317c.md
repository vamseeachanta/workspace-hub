---
name: crossprovider gemini pre-commit-hook-tool-versions-must-match-main-sc
description: Pre-commit hook tool versions must match main script versions
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [ci-cd, tooling, version-management, pre-commit]
---

WRK-1056: Mismatched versions between .pre-commit-config.yaml (e.g., ruff 0.x) and main script (uv tool run ruff 0.y) cause 'passed locally, failed in CI' situations. Coordinate versions explicitly or parameterize via a shared config file.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
