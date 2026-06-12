---
name: crossprovider hermes sourcing-repo-tracked-files-before-approval-crea
description: Sourcing repo-tracked files before approval creates trivial gate bypass
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [security, hooks, approval-gates]
---

If an approval gate sources a file like `scripts/enforcement/enforcement-env.sh` from the repo before approving implementation, agents can edit it to set `DISABLE_ENFORCEMENT=1` and bypass the gate. Source only from trusted out-of-repo locations.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
