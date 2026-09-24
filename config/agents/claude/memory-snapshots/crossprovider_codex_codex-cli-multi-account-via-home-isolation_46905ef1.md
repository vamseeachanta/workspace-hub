---
name: crossprovider codex codex-cli-multi-account-via-home-isolation
description: Codex CLI multi-account via HOME isolation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [codex-cli, auth, multi-account, workspace-setup]
---

Codex CLI stores auth in $HOME/.codex/auth.json, so multiple accounts on one machine require separate HOME directories. Initialize with HOME=~/codex-1 codex login, HOME=~/codex-2 codex login, then invoke as HOME=~/codex-N codex to select account.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
