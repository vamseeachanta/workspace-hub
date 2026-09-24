---
name: crossprovider codex scoped-pathspec-commits-prevent-unrelated-sweep-
description: Scoped pathspec commits prevent unrelated sweep contamination
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-discipline, tdd, multi-agent, index-safety]
---

Use explicit `git commit -- <pathspec>` for each verified TDD checkpoint rather than broad staging to prevent unrelated changes from being swept into commits when multiple sessions, hooks, or agents interact with the same repository. This maintains clean residue and precise authorship when execution is distributed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
