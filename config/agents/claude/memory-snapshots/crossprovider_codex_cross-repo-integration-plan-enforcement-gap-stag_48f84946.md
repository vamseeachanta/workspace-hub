---
name: crossprovider codex cross-repo-integration-plan-enforcement-gap-stag
description: Cross-repo integration plan enforcement gap: staged-vs-pushed detection
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [git-hooks, cross-repo-testing, enforcement]
---

Pre-push hooks that detect changes via staged files (git index) miss actual commits being pushed; the trigger must inspect pushed refs (local_oid..remote_oid) like the existing hub hook does. Staged-change detection can silently skip the gate on the exact scenarios it's supposed to protect (WRK-1091 recurred across 4 review rounds).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
