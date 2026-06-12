---
name: crossprovider codex lazy-import-and-sys-modules-tests-fail-when-test
description: Lazy-import and sys.modules tests fail when test order changes; require subprocess isolation
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, test-brittleness, lazy-loading]
---

Plans proposing lazy-import tests (e.g., 'test that importing module does not import pandas.market_calendars') are fragile because sys.modules is process-global. If any other test imports the module first, the test falsely passes. These tests must use subprocess.Popen or explicit sys.modules cleanup to be reliable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
