---
name: crossprovider hermes stale-artifact-and-duplicate-issue-accumulation-
description: Stale artifact and duplicate issue accumulation exceeds manual triage capacity
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [automation, repo-hygiene, stale-artifacts, batch-detection]
---

Once a repo accumulates stale issues, closed-but-unmarked work, and duplicate copies (e.g., session-corpus-audit module duplicated in two locations, issues marked OPEN that are completed), one-off cleanup passes fall behind within weeks. Need scheduled detector + machine-readable disposition rules (auto-close, auto-merge-dupe, auto-label) rather than re-running manual audits.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
