---
name: crossprovider codex review-artifact-naming-contract-mismatch-breaks-
description: Review artifact naming contract mismatch breaks discovery
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [artifact-naming, scanner-contract, discovery]
---

Plans list artifacts as `plan-63-claude.md` (simple), but scanners expect `2026-06-29-plan-63-r1-claude.md` (rounded with date/round prefix). This mismatch causes scanners to miss artifacts. Plan artifact names must match the scanner's glob/regex contract (e.g., scripts/ace_public_surface_review.py:214).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
