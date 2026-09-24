---
name: crossprovider gemini linter-scope-asymmetry-creates-hidden-gate-surfa
description: Linter scope asymmetry creates hidden gate surface
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [ci-gates, linting, asymmetry]
---

CI gates with inconsistent scan scopes (e.g., `flake8 .` scanning repo root vs `mypy src/` scanning package only) create a hidden gate surface where failures appear/disappear based on auxiliary files outside the package boundary. Auxiliary scripts in `.agent-os/` or `scripts/` can break linting while the package stays clean. Gate scopes must align or document their intentional boundaries.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
