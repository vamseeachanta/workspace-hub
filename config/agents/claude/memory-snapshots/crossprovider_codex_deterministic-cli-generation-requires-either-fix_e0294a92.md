---
name: crossprovider codex deterministic-cli-generation-requires-either-fix
description: Deterministic CLI generation requires either fixed dates or required input flags
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [llm-wiki, reproducibility, deterministic-generation]
---

Implicit `date.today()` in artifact naming breaks reproducibility. Either use a fixed issue date as the default, accept a required `--generated-date` flag, or require an input artifact (like `--docs-master-catalog`) that is part of the deterministic output path. Tests must pass fixed dates to allow byte-exact reproducibility checks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
