---
name: crossprovider hermes hermes-external-dirs-needs-patching-to-exclude-a
description: Hermes external_dirs needs patching to exclude archived skill dirs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [harness, skills, system-prompt, architecture]
---

Pointing Hermes external_dirs at workspace-hub's 2,734 skills without filtering archives/internal/runtime/core meant 2,166 non-active skills bloated the system prompt. Patched Hermes skill_utils.py EXCLUDED_SKILL_DIRS to skip underscore-prefixed directories; patch is auto-applied by harness-update.sh via config/agents/hermes/patches/. This is a harness limitation worth knowing.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
