---
name: crossprovider codex pathspec-commits-protect-against-auto-sync-conta
description: Pathspec commits protect against auto-sync contamination
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, workflow, automation-safety]
---

Use `git commit -F <msgfile> -- <paths>` to stage only targeted files. Automated sync processes can sweep unrelated changes into commits; pathspec form restricts scope and prevents PR contamination.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
