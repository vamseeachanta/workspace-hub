---
name: crossprovider codex pytest-with-licensed-external-dependencies
description: pytest with licensed/external dependencies
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pytest, testing-patterns, external-dependencies, mocking]
---

Use pytest.importorskip('PackageName') to gracefully skip tests when optional/licensed packages (e.g., OrcFxAPI) are missing. For optional deps like matplotlib, mock via monkeypatch.setitem(sys.modules, 'matplotlib', MagicMock()). Prevents cascading import failures during test collection.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
