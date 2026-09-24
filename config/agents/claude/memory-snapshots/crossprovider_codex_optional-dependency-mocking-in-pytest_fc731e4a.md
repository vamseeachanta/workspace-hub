---
name: crossprovider codex optional-dependency-mocking-in-pytest
description: Optional dependency mocking in pytest
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, pytest, mocking]
---

Use `pytest.importorskip('ModuleName')` for external/licensed deps (e.g., OrcFxAPI) and `monkeypatch.setitem(sys.modules, 'module_name', MagicMock())` for optional viz (e.g., matplotlib). Tests must not require network, licenses, or external mounts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
