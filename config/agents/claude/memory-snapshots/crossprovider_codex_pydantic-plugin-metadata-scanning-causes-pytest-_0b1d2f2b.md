---
name: crossprovider codex pydantic-plugin-metadata-scanning-causes-pytest-
description: Pydantic plugin metadata scanning causes pytest collection bottleneck in shared virtualenvs
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, pydantic, performance, virtualenv]
---

When pytest collection takes multiple minutes before executing any tests, Pydantic's metadata scanning of all installed distributions is often the cause in shared .venv environments. Disabling Pydantic plugins and metadata scanning via environment flags (`PYDANTIC_CORE_SCHEMA_NO_PLUGINS=1` or equivalent) significantly reduces filesystem contention and I/O wait time.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
