---
name: crossprovider codex configuration-catalogs-must-pin-install-commands
description: Configuration catalogs must pin install commands to match declared versions—not placeholders or 'latest'
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [catalog-management, reproducibility, automation]
---

When a catalog entry records a commit SHA or version, the install_command must actually pin to that exact artifact. Unpinned commands (even with `@<COMMIT_SHA>` placeholders) break reproducibility and violate the catalog's own pinning contract. Automate validation: every active/evaluated entry must have a fully reproducible install_command.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
