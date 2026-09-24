---
name: crossprovider codex licensed-seat-contention-retry-via-result-json-d
description: Licensed seat contention retry via result JSON deletion
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [licensed-software, operational-knowledge, diagnostics]
---

Licensed simulation tools (OrcaWave, AQWA) signal seat contention with rc 75; resolve by deleting the result JSON to trigger retry. A frozen process heartbeat indicates running state, not stalled state. Know the tool's native signaling before diagnosing hangs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
