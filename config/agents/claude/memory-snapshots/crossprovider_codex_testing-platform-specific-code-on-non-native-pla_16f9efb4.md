---
name: crossprovider codex testing-platform-specific-code-on-non-native-pla
description: Testing platform-specific code on non-native platforms requires strict skip/fail boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [testing, platform-specific, test-semantics, ci]
---

When testing Windows-native code on Linux, skip only when the platform is absent AND the mode is optional; all Windows capability gaps in required mode must fail with an infrastructure-failure marker, not skip. Skipping too broadly masks real defects; failing on missing platform blocks unrunnable tests. The boundary between skip and fail is a contract, not a preference.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
