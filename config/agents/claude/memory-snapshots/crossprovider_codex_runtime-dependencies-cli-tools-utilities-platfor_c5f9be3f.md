---
name: crossprovider codex runtime-dependencies-cli-tools-utilities-platfor
description: Runtime dependencies (CLI tools, utilities, platform assumptions) must be explicitly declared, not assumed
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dependencies, shell-scripts, plan-review, executability]
---

Shell scripts in plans often use sha256sum, grep, sed, awk, readlink, gh, git without declaring them as dependencies. Missing CLI availability crashes the plan at runtime. Dependencies section must list required tools, platform expectations, and fail behavior when tools are unavailable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
