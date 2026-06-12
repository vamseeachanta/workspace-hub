---
name: crossprovider hermes nightly-learning-artifacts-are-70-untracked-crit
description: Nightly learning artifacts are 70% untracked; critical institutional knowledge lost on machine failure
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [nightly-pipeline, git-tracking-gap, knowledge-preservation]
---

comprehensive-learning-nightly.sh orchestrator produces 10+ artifact types (session analysis, corrections, patterns, readiness reports) but only ~3 are git-tracked. CRITICAL untracked: .claude/state/corrections/, .claude/state/patterns/ (behavioral learnings), .claude/state/session-analysis/. Design decision: track all artifacts or accept daily data loss.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
