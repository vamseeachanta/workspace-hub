---
name: crossprovider codex pr-keyword-refs-does-not-auto-close-issues-close
description: PR keyword 'Refs' does not auto-close issues; 'Closes' does
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [github, pr-workflow, issue-management]
---

When a PR uses 'Refs #NNNN' instead of 'Closes #NNNN', the issue remains open after merge and requires manual closure. This is a procedural trap that leaves stale-open children and epics until someone explicitly closes them.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
