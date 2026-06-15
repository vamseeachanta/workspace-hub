---
name: crossprovider codex read-only-audits-clarify-state-but-don-t-resolve
description: Read-only audits clarify state but don't resolve it
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [review-workflow, gating, closeout]
---

A review pass that reports (not edits) dirty state is useful for final gating decisions, but cleanup still requires a separate action. Reviewers must explicitly call out which dirty items block merge vs. are acceptable residue.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
