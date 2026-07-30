---
name: crossprovider codex git-subprocess-isolation-requires-explicit-git-n
description: Git subprocess isolation requires explicit GIT_NO_REPLACE_OBJECTS restoration
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [git-security, subprocess-isolation, replacement-refs]
---

Stripping ambient Git config (GIT_CONFIG_NOSYSTEM/GLOBAL) does not prevent local `.git/config` includes or default replacement-ref handling. Subprocesses invoking Git must explicitly set GIT_NO_REPLACE_OBJECTS or validate final objects against desired SHAs, since `archive`/`ls-tree` honor replacement refs by default even when global config is cleared.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
