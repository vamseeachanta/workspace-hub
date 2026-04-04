---
name: Overnight multi-terminal batch runs
description: User dispatches 5 parallel Claude Code terminals overnight with pre-planned prompts — recurring pattern since 2026-04-01
type: project
---

User runs overnight batch sessions with 5 parallel terminals, each with a pre-planned prompt targeting different workstreams. Prompts are committed as docs beforehand (e.g., `docs(plans): 5 overnight terminal prompts for YYYY-MM-DD night batch run`).

**Pattern observed:** 2026-04-01, 2026-04-02, 2026-04-03 (3 consecutive nights).

**Typical workstreams across terminals:**
- Solver queue operations (OrcaFlex test uplift)
- Architecture scanners (#1626, #1627, #1629, #1634)
- Doc-intel processing (#1613, #1621, #1622)
- Quality/analysis tooling (#1573)
- GTM/job market scanning (#1671)

**Why:** Maximizes overnight compute — each terminal runs autonomously on an independent workstream.

**How to apply:** When user asks for overnight planning or "what to run tonight," expect 5 terminal slots. Each prompt should be self-contained (no cross-terminal dependencies). Session handoff docs are committed next morning.
