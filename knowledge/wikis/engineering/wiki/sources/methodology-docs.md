---
title: "Methodology Docs Collection"
tags: [source, methodology, compound-engineering, enforcement]
sources:
  - docs/methodology/
added: 2026-04-08
last_updated: 2026-04-08
---

# Methodology Docs Collection

Source summary of `docs/methodology/` — six documents capturing the ACE Engineer operational methodology, derived from real operational experience rather than theoretical frameworks.

## Overview

| Property | Value |
|----------|-------|
| Directory | `docs/methodology/` |
| Documents | 6 |
| Origin | Distilled from actual workspace-hub operational patterns |
| Nature | Descriptive (what emerged), not prescriptive (what was planned) |

## Documents

| File | Topic | Key Insight |
|------|-------|-------------|
| `compound-engineering.md` | The compound flywheel | Work produces tools, tools produce better work — the self-reinforcing loop |
| `enforcement-over-instruction.md` | Gates vs guidelines | Technical enforcement (hooks, scripts) beats prose instructions every time |
| `orchestrator-worker.md` | Agent separation | Coordinator + isolated workers outperforms one monolithic agent |
| `multi-agent-parity.md` | Shared knowledge base | All agents sharing one knowledge base eliminates redundant discovery |
| `compliance-dashboard.md` | Visibility into enforcement | Dashboard tracking which rules are enforced at which level |
| `knowledge-to-website-pipeline.md` | Knowledge surfacing | Pipeline from internal knowledge → public-facing website content |

## Methodology Lineage

These documents were not designed upfront. They emerged from patterns observed during real engineering work:

```
Real engineering sessions (2025-Q2 onward)
    → Patterns noticed across sessions
        → Patterns documented in docs/methodology/
            → Concept pages created in engineering wiki
                → Cross-referenced and interlinked
```

## Wiki Concept Pages Generated

Each methodology document generated a corresponding concept page:

| Methodology Doc | Wiki Concept Page |
|----------------|-------------------|
| `compound-engineering.md` | [Compound Engineering](../concepts/compound-engineering.md) |
| `enforcement-over-instruction.md` | [Enforcement Over Instruction](../concepts/enforcement-over-instruction.md) |
| `orchestrator-worker.md` | [Orchestrator-Worker Separation](../concepts/orchestrator-worker-separation.md) |
| `multi-agent-parity.md` | [Multi-Agent Parity](../concepts/multi-agent-parity.md) |
| `compliance-dashboard.md` | [Compliance Dashboard](../concepts/compliance-dashboard.md) |
| `knowledge-to-website-pipeline.md` | [Knowledge to Website Pipeline](../concepts/knowledge-to-website-pipeline.md) |

## Cross-References

- **Related source**: [Career Learnings Seed](../sources/career-learnings-seed.md)
- **Related source**: [Dark Intelligence Extractions](../sources/dark-intelligence-extractions.md)
- **Related concept**: [Compound Engineering](../concepts/compound-engineering.md)
- **Related concept**: [Enforcement Over Instruction](../concepts/enforcement-over-instruction.md)
