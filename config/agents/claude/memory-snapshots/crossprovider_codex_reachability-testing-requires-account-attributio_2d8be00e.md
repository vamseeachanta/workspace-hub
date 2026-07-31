---
name: crossprovider codex reachability-testing-requires-account-attributio
description: Reachability testing requires account attribution, not just TCP
metadata:
  type: reference
  source: codex
  bridged: 2026-07-30
  tags: [reachability, dispatch, ssh-testing]
---

SSH connectivity alone doesn't prove dispatch feasibility. Use `ssh -n -o BatchMode=yes` to verify which OS account succeeds (e.g. prove the `vamsee` account authenticates), not just that port 22 is open.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
