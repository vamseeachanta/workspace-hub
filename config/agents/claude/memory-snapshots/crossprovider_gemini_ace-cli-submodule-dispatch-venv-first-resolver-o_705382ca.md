---
name: crossprovider gemini ace-cli-submodule-dispatch-venv-first-resolver-o
description: Ace CLI submodule dispatch: venv-first resolver order
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [multi-repo-orchestration, cli-architecture, subprocess]
---

Resolve tools in order: (1) .venv/bin/<command>, (2) repo/<command> script, (3) python -m <module>. Orchestrates heterogeneous submodule tools (pip-installed vs. plain scripts) without unified packaging. Check file existence before subprocess.run for actionable error messages.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
