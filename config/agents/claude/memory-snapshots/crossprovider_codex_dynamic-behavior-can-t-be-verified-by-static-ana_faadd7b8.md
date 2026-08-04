---
name: crossprovider codex dynamic-behavior-can-t-be-verified-by-static-ana
description: Dynamic behavior can't be verified by static analysis across platforms
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [windows, cross-platform, testing, acceptance]
---

Windows argument forwarding via `%*`, path canonicalization across native/Git-Bash/UNC forms, and metacharacter handling cannot be verified by inspecting `.cmd` source. These require actual testing on Windows using a native argv-capture tool, not textual analysis. Same applies to locale-dependent behavior, quote preservation, and trailing-backslash handling.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
