---
name: crossprovider codex hook-ci-enforcement-boundary-must-be-explicit-in
description: Hook/CI enforcement boundary must be explicit in plans
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [enforcement, planning, ci-integration]
---

Plans creating enforcement contracts must clearly state whether validation is manual-only, hook-only, or both. Ambiguity like 'optional' or 'to be decided in implementation' creates drift and blocks CI rollout. If manual-only, file a follow-up hook/CI issue; if hook/CI, include concrete integration test + installation path.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
