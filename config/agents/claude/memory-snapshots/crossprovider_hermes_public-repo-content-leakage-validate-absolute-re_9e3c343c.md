---
name: crossprovider hermes public-repo-content-leakage-validate-absolute-re
description: Public-repo content leakage: validate absolute + relative paths + internal references
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [public-repo, content-leakage, boundary-validation]
---

Public-repo validators must catch not just absolute paths (e.g., `/mnt/`) but relative workspace paths, private-corpus indicators (e.g., `per /raw/`, `per /private/`), and internal instruction leakage (e.g., `per CLAUDE.md schema`). Example: llm-wiki #77 validator only caught absolute paths, missed `per maritime-law/CLAUDE.md` schema reference. **Why:** relative and schema-reference leakage violates public/private boundary and exposes internal workflows. **How to apply:** add `_is_public_safe_content` check for pattern list: `/raw`, `/private`, `/mnt`, `CLAUDE.md`, `.claude/`, workspace paths; reject edges with unresolved internal references.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
