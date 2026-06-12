---
name: crossprovider codex canonical-repo-registry-must-match-git-submodule
description: Canonical repo registry must match git submodule reality or diverge immediately
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [documentation, ecosystem-metadata]
---

Creating a skill/doc that claims to be the 'authoritative ecosystem reference' but omits repos from .gitmodules creates maintenance debt immediately (WRK-1098 omitted 10+ canonical submodules). Either enumerate all repos with explicit scope ('core only'), or accept that a full-authority registry must be machine-checkable against .gitmodules.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
