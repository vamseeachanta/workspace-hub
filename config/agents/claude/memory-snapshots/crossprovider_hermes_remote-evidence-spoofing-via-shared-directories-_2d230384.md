---
name: crossprovider hermes remote-evidence-spoofing-via-shared-directories-
description: Remote evidence spoofing via shared directories requires cryptographic authentication
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [security, hermes, remote-execution, trust-boundary]
---

Hermes issue #2720: `collect_readiness()` accepts JSON evidence from shared `--evidence-dir/<host>.json` as authoritative if fields (`host_id`, `hostname`, `producer`, booleans, timestamp) self-match, with no signature/binding/protected transport. Any writer to the share can forge clean pass evidence and trigger dispatch. Control-plane gates on shared/untrusted directories must use signed artifacts, SSH-verified execution, or equivalent attested collection paths bound to host/worktree/registry revision.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
