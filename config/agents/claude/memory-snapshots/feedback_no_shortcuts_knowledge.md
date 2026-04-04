---
name: No shortcuts on knowledge extraction
description: User strongly prefers thorough extraction-to-expert-agent pipeline over quick approximations — applies to all domain knowledge work
type: feedback
---

No shortcuts on domain knowledge work. The correct approach is: extract → validate with TDD → build calculation modules → synthesize into expert agent. Every function must be backed by a worked example from an authoritative source (textbook, standard, peer-reviewed paper).

**Why:** Quick approximations produce agents that hallucinate engineering answers. The value is in source-traced, numerically verified knowledge — not in speed. The user explicitly approved a 14-WRK roadmap spanning extraction, curation, module development, and expert agent synthesis rather than a shortcut approach.

**How to apply:** When building domain expertise (naval architecture, offshore engineering, or any technical discipline): always extract from primary sources first, create TDD fixtures from worked examples, implement calculations with tests, then create the expert skill/agent. Never skip the extraction and validation steps to get to the "agent" faster. The agent is only as good as its verified knowledge base.
