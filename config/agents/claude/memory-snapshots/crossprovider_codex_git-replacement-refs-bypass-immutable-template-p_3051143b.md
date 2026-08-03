---
name: crossprovider codex git-replacement-refs-bypass-immutable-template-p
description: Git replacement refs bypass immutable template pins
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [git, security, reproducibility]
---

Git replacement refs allow substituting one commit for another without changing refs or SHA chains. This bypasses claims about using a specific template commit — manifest can reference commit A while actual content comes from replacement commit B. Verify Git replacement configuration and disable if immutability is required.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
