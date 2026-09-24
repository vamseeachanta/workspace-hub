---
name: crossprovider codex pytest-marker-addition-requires-pyproject-toml-u
description: Pytest marker addition requires pyproject.toml update under --strict-markers
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pytest, configuration-coupling, silent-failures]
---

Adding `@pytest.mark.custom_name` to test files silently fails if the marker is not declared in `pyproject.toml` when `--strict-markers` is enabled. This blocks execution and is easy to miss during implementation. Always update both test code and config together.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
