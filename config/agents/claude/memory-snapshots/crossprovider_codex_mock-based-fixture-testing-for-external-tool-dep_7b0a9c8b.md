---
name: crossprovider codex mock-based-fixture-testing-for-external-tool-dep
description: Mock-based fixture testing for external tool dependencies
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, shell-scripts, fixtures]
---

Test shell scripts that depend on external tools (uv, pip-audit, etc.) by creating minimal mktemp fixture repos and mocking tools via PATH override. Avoids full dependency installation, keeps tests fast and isolated, and eliminates flaky environmental dependencies.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
