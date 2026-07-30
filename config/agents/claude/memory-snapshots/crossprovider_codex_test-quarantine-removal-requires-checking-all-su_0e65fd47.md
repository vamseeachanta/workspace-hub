---
name: crossprovider codex test-quarantine-removal-requires-checking-all-su
description: Test quarantine removal requires checking all suppression layers
metadata:
  type: reference
  source: codex
  bridged: 2026-07-05
  tags: [pytest, ci-configuration, test-discovery]
---

Removing explicit test quarantine (conftest.py filter) does not guarantee test discovery if pytest --ignore entries in pyproject.toml, CI job routing, or test-discovery filters still suppress it. Must verify all four layers when removing quarantine: explicit quarantine file, pytest config ignores, CI job routing, and test-discovery filters.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
