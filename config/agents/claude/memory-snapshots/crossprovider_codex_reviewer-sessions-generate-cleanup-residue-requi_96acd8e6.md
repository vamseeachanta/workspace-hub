---
name: crossprovider codex reviewer-sessions-generate-cleanup-residue-requi
description: Reviewer sessions generate cleanup residue requiring audits
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [session-cleanup, verification, operational-hygiene]
---

Even read-only code-review sessions can create unexpected artifacts (.venv, __pycache__, .git locks) when they execute build commands or import modules. Pre-completion cleanup audits must scan for and remove these, distinguishing expected target edits from generated artifacts. Document the expected vs unexpected residue explicitly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
