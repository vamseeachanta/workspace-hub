---
name: crossprovider codex afk-safety-requires-concrete-artifact-and-comman
description: AFK-safety requires concrete artifact and command contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [prompt-engineering, afk-agent, issue-259, issue-260]
---

Generated implementation prompts must include exact expected artifacts, specific test commands, and concrete gh commands, not just scope and branch. Issue #259/#260: thin prompts caused AFK agents to diverge on interpretation. Generated prompts should mirror what a human engineer would expect from explicit acceptance criteria.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
