---
name: crossprovider codex pep-723-inline-deps-scripts-require-uv-run-not-b
description: PEP-723 inline-deps scripts require `uv run`, not bare python3
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [uv, pep-723, tooling-quirk]
---

Scripts with PEP-723 `# /// script` headers and inline dependencies (e.g., `--with pyyaml`) fail silently when invoked as `python3 script.py`; they must be run via `uv run script.py`. Bare python3 lacks the declared dependencies even if uv is installed. This quirk recurs in corpus-ingest workflows.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
