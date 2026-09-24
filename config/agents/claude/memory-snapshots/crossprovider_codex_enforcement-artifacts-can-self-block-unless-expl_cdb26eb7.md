---
name: crossprovider codex enforcement-artifacts-can-self-block-unless-expl
description: Enforcement artifacts can self-block unless explicitly excluded
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [enforcement, testing, security]
---

Enforcement scripts, validators, and legal scan rules can block their own templates, test fixtures, and plan artifacts unless explicitly excluded via per-line sentinels or scoped fixture allowlists. Blanket exempts for fixture directories are backdoors and should not be used instead of sentinel-level exclusions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
