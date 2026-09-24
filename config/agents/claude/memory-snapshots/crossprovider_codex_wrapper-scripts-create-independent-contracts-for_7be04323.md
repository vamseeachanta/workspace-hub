---
name: crossprovider codex wrapper-scripts-create-independent-contracts-for
description: Wrapper scripts create independent contracts; forwarding is not transparent
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [wrapper-patterns, contract-mismatch]
---

Forwarding flags/args from a wrapper script to a wrapped script does not guarantee the wrapper satisfies the caller's requirements. The wrapped script's output semantics may differ from what the caller needs. Explicitly verify wrapper contract against caller requirements before assuming semantic equivalence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
