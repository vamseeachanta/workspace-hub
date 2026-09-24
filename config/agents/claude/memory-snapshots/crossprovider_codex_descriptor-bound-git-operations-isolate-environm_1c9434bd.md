---
name: crossprovider codex descriptor-bound-git-operations-isolate-environm
description: Descriptor-bound Git operations isolate environment
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-security, descriptor-safety, environment-isolation]
---

When executing Git operations on untrusted clones, bind descriptors via explicit pass operations, restrict child process inheritance via `pass_fds`, and drop ambient environment variables (Git identity, askpass, loader). This prevents environment contamination or credential leakage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
