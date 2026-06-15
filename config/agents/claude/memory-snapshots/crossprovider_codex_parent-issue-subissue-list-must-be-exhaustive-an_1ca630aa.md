---
name: crossprovider codex parent-issue-subissue-list-must-be-exhaustive-an
description: Parent-issue subissue list must be exhaustive and match the plan graph
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [planning, github-issues, graph-completeness]
---

If a plan identifies N child issues (#265-#269 = 5 issues), the parent GitHub issue's "Proposed subissues" section must list all N. If the parent lists only 4, discovery and sequencing tools will miss the 5th. Verify the parent issue body against the plan's subissue dependency graph.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
