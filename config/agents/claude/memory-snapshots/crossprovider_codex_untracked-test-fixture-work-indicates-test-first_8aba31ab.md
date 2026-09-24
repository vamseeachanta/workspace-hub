---
name: crossprovider codex untracked-test-fixture-work-indicates-test-first
description: Untracked test/fixture work indicates test-first parallel progress
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [parallel-work, discovery, test-first, contract-drift]
---

Untracked test files (e.g., `tests/test_validate_ace_wave1_text_json.py`, `tests/fixtures/`) surfacing mid-session often indicate test-first work in flight before implementation lands. Discovery must check for these before accepting baseline state as complete. Can reveal contract drift early (e.g., `logical_target_store: private_sidecar_manifest` not in closed #65 matrix).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
