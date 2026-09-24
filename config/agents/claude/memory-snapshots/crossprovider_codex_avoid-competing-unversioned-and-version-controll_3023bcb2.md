---
name: crossprovider codex avoid-competing-unversioned-and-version-controll
description: Avoid competing unversioned and version-controlled hook mechanisms
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [hooks, version-control, deployment-consistency]
---

Parallel hook paths (unversioned `.git/hooks/pre-push` + version-controlled `scripts/hooks/pre-push.sh`) cause deployment drift, duplicate logic, and non-reproducible installs. Pick one canonical path (usually the version-controlled one) and define an installer that wires it. Unversioned hooks are never consistent across team checkouts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
