---
name: crossprovider codex test-skeleton-pattern-for-coverage-uplift-select
description: Test skeleton pattern for coverage uplift: selective mocking for external dependencies
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, pytest, coverage, mocking, skeleton-tests]
---

When uplifting test coverage via skeleton tests, use `pytest.importorskip('DependencyName')` for licensed/unavailable deps (e.g., OrcFxAPI) and `monkeypatch.setitem(sys.modules, 'module', MagicMock())` for optional visualization deps (e.g., matplotlib) to avoid import-time failures and allow tests to run without external mounts or licenses.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
