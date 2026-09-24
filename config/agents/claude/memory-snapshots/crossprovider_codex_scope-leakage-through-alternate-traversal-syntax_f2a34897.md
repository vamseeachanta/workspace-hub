---
name: crossprovider codex scope-leakage-through-alternate-traversal-syntax
description: Scope leakage through alternate traversal syntax
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, security, scope]
---

Denying specific commands (find, du, wc -l) does not prevent equivalent traversal via language builtins (Python rglob(), grep -R, os.walk()) or unrestricted operators (full jq, bash expansions). When enforcing scope boundaries, audit all data-access methods in the target execution environment, not just CLI tools.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
