---
name: crossprovider codex two-pass-gating-for-severity-split-policies
description: Two-pass gating for severity-split policies
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gating, testing, shell-scripts]
---

When different severities need different policies (e.g., LOW warns, MEDIUM/HIGH blocks), split into explicit passes: Pass 1 non-blocking (collects all findings), Pass 2 gating (filtered by severity). Mixing policies in one invocation with flags leads to silent misconfigurations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
