---
name: crossprovider codex human-gates-run-in-session-because-human-decisio
description: Human gates run in-session because human decision context is fresh input, not task
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [human-in-loop, gate-design, session-boundaries]
---

Gates 5→6, 7→8, 17→18 are intentionally run in the current human session, not spawned as Task agents. This preserves the interactive review loop — the human's approval is new context, not just data review. Task agents cannot replace this gate because they inherit prior session context and lose the human's fresh judgment.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
