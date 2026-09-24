---
name: crossprovider codex pep-723-direct-invocation-does-not-populate-sys-
description: PEP 723 direct invocation does not populate sys.path with repo root
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tooling, python, packaging]
---

`uv run script.py` does not place the repository root on `sys.path`, breaking sibling-package imports (e.g., `import manufacturing_evidence`). Workaround: explicit path injection or package-entry-point installation. Test with `uv run scripts/manufacturing_evidence_ledger.py --help` to detect the issue early.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
