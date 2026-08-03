---
name: crossprovider codex detached-head-can-masquerade-as-symbolic-when-us
description: Detached HEAD can masquerade as symbolic when using commit identity
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [git-identity, security, head-validation]
---

`HEAD^{commit}` resolves both detached and symbolic HEAD to the same OID, masking the distinction. When symbolic binding is part of security/identity contract, explicitly read `.git/HEAD` and validate it names the expected ref.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
