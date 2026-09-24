---
name: crossprovider codex generated-environment-files-must-not-be-committe
description: Generated environment files must not be committed
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [vcs, git, environment]
---

`.venv/pyvenv.cfg`, virtual environment configs, build outputs (`dist/`), and other generated state are machine-specific and should not land in VCS. If accidentally committed, make a hygiene commit removing them before human review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
