---
name: crossprovider codex public-safety-boundaries-need-explicit-allowlist
description: Public-safety boundaries need explicit allowlisting, not negative patterns
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [public-safety, allowlisting, firewall]
---

Rejecting known unsafe patterns (dotfiles, 'raw' folder, scaffolding files) leaves gaps when new unsafe cases emerge. Instead, explicitly enumerate allowed wiki directories and content kinds, reject everything outside that set. This prevents accidental inclusion of agent config files, CLAUDE.md, or private scaffolding even if they exist in committed tree.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
