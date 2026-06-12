---
name: crossprovider hermes missing-git-upstream-tracking-is-silently-ignore
description: Missing git upstream tracking is silently ignored
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-sync, dispatch-safety, readiness]
---

When `git rev-parse @{u}` fails (no upstream tracking), the error is silently ignored, leaving `ahead=0, behind=0`. Repos with no remote tracking are reported as synced even though `sync_policy: pull-before-work-push-after-work` requires upstream divergence checking.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
