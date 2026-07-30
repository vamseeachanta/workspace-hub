---
name: crossprovider codex post-push-state-mutations-cannot-be-verified-pre
description: Post-push state mutations cannot be verified pre-push
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [security, verification, lifecycle]
---

Verifying a repository is PRIVATE before pushing does not prevent an admin from changing visibility to PUBLIC after the push. Any post-push lifecycle mutations (registry updates, archive promotion) require re-verification immediately after push, not pre-push attestation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
