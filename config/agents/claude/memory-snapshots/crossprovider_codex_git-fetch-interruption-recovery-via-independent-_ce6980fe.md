---
name: crossprovider codex git-fetch-interruption-recovery-via-independent-
description: Git fetch interruption recovery via independent verification
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [git, network-resilience, remote-sync]
---

When `git fetch` is terminated mid-operation, do not retry the failing transport layer. Instead, verify base state independently via `git ls-remote origin main` or GitHub API. If the cached `origin/main` ref matches the live remote, it is safe to proceed without retry.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
