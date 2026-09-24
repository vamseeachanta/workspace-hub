---
name: crossprovider gemini environment-variable-fallbacks-enable-hermetic-t
description: Environment variable fallbacks enable hermetic test fixtures
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [testing, configuration, fixtures]
---

Library functions should accept optional parameters (e.g., queue_root) with defaults to os.environ.get() fallbacks. Tests can override configuration by setting env vars or passing parameters without modifying global state. Enables hermetic mktemp -d fixtures for parallelizable integration tests.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
