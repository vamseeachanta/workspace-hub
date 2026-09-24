---
name: crossprovider codex issue-text-evidence-can-be-stale-against-live-co
description: Issue text evidence can be stale against live code; verify claims before implementing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [issues, code-review, verification]
---

Issue descriptions documenting code defects may not match current implementation. In this session, the claimed defect (exclusive day counting losing one day per WAR week) was refuted by live code already implementing `+1` for positive intervals. Verify issue claims against the actual code before accepting them as true.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
