# ACE Engineering — Ecosystem Vision

> **North Star**: An AI agent receives a client brief, selects the appropriate physics solver,
> generates all inputs, runs the simulation, extracts and interprets results, and delivers a
> validated engineering report — without a human initiating any intermediate step.

*This document is the shared north star for all repositories in this ecosystem.
Every WRK item should be scored against it before priority is assigned.*

---

## Where We Are: Current Repository Missions

Each repository's mission, and its position on the autonomy ladder (see Section 3):

| Repository | Mission | Autonomy Level |
|------------|---------|---------------|
| **digitalmodel** | Single source of truth for offshore and subsea engineering analysis across the full asset lifecycle — fatigue, hydrodynamics, riser/mooring, metocean, vessel systems — via ASCII-first configuration that generates analytical models, CAD, animations, and documentation | L2–L3 |
| **assetutilities** | Reusable automation utilities and six shared sub-agents (workflow, file, visualisation, auth, git, agent-templates) deployed across all repos as a common automation layer | L2–L3 |
| **worldenergydata** | Global energy market data aggregation, analysis, and interactive reporting from public sources (BSEE, EIA, IEA) with standardised energy units and attribution | L2 |
| **assethold** | Daily multi-signal stock recommendations (RSI, SMA, insider filings, portfolio weight) for long-term holdings, with interactive Plotly dashboards and Fidelity integration | L2–L3 |
| **aceengineer-website** | Professional company presence and engineering portfolio at www.aceengineer.com | L1–L2 |
| **workspace-hub** | Central orchestration hub: WRK queue management, AI agent coordination, session management, nightly learning pipeline, and cross-repo synchronisation | L3 |

The ecosystem is operating at **Level 2–3 overall** — automated pipelines exist, AI agents
assist, and the nightly learning pipeline is predictive. The gap to Level 4 is real and
closable within 12–18 months given the existing agent infrastructure.

---

## The 6-Level Autonomy Framework

Adapted from Zvi Feuer's framework (analogous to SAE autonomous vehicle levels, applied to
engineering production systems):

| Level | Label | Defining characteristic | Our current analogy |
|-------|-------|------------------------|---------------------|
| 0 | Manual | Human labour with manual tools | Pre-WRK era |
| 1 | Assisted | Program-specific automation | Individual scripts, no orchestration |
| 2 | Automated | Continuous activity; human monitors | CI/CD, test pipelines, submodule sync |
| 3 | Predictive | AI handles maintenance; operator ready | WRK queue + nightly comprehensive-learning |
| 4 | Autonomous | System self-programmes; humans optimise | **Target**: agents triage and execute WRK items |
| 5 | Engineering as a Service | Self-optimising ecosystem; human as Orchestrator | **North star**: AI delivers engineering outcomes on demand |

### The Trust Chasm

The hardest transition is **L3 → L4**. It is not primarily a technology gap. It is a
governance, validation, and trust gap: the moment a human can be "disengaged but ready"
requires confidence in the system's judgement at every step.

Our existing trust architecture — the plan gate, cross-review (Claude + Codex + Gemini),
WRK archival trail, acceptance criteria enforcement, and the "never archive until user
confirms" rule — is the foundation for crossing this chasm. The work is to formalise it,
extend it to agent-initiated actions, and make its audit trail legible to any stakeholder.

### The Operating Pattern: Sense → Plan → Act

The loop that Level 4 and 5 systems run continuously:

```
SENSE  — ingest live signals: CI results, sensor data, client data feeds, market data
PLAN   — AI agents simulate "what-if" against the current model; select best action
ACT    — execute: run solver, commit code, update model, generate report, alert human
```

Today this loop runs partially and manually. The vision is for it to run continuously and
autonomously, with humans setting policy and handling exceptions.

---

## Capability Gap Analysis

The gaps between current state and Level 4 autonomous operation:

| Capability | Current state | Gap | WRK candidates |
|------------|--------------|-----|----------------|
| **Agent-initiated simulation** | Human initiates every solver run via WRK item | Agents auto-schedule routine analyses from signals (schedule, data change, client trigger) | new WRK |
| **Multi-physics orchestration chain** | One solver per WRK item; handoffs are manual | Autonomous pipeline: Gmsh → OpenFOAM → OrcaFlex with validated handoffs | WRK-372 (partial) |
| **Sense-Plan-Act loop** | CI signals only; no live asset or sensor data | Live sensor/SCADA feeds → digital model → autonomous re-run on deviation | new WRK |
| **Surrogate models** | Full physics runs only; expensive design-space exploration | Train AI surrogate on existing run library; query model for fast parametrics | new WRK |
| **Autonomous report generation** | Human must review and approve every output | AI drafts, cross-reviews, and delivers validated engineering report; human spot-checks | new WRK |
| **Self-healing workflows** | Manual debugging when a solver or pipeline fails | Error signals → diagnostic agent → fix → re-run; escalate only if stuck | WRK-304 (partial) |
| **Trust architecture formalisation** | Plan gate + WRK trail exist but are not documented as a governance model | Write and publish the governance model: approval logic, audit format, rollback rules | new WRK |

---

## 3-Horizon Roadmap

### Horizon 1 — Close the L3 Gaps, Establish L4 Foundations (Now – 6 months)

- **AI interface skills** for all P1/P2 engineering tools complete (WRK-372): OrcaFlex
  failure diagnosis, OpenFOAM, Blender, ParaView, FreeCAD — so agents can drive every
  solver without human translation
- **Multi-physics workflow chains** documented and testable: Gmsh → OpenFOAM → OrcaFlex
  as a validated, agent-executable pipeline
- **Live signal ingestion** wired into comprehensive-learning (WRK-306): AI readiness
  checks, tool-call summaries, context-reset events — richer predictive data
- **Stop-hook cleanup** (WRK-304): sub-5s execution, analysis deferred to nightly pipeline
- **Trust architecture** written up: one document defining approval logic, audit format,
  and escalation rules for agent-executed actions

### Horizon 2 — Achieve Level 4: Autonomous Execution on Routine Analyses (6–18 months)

- **Agent-initiated simulation**: at least one workflow class (e.g. routine fatigue check,
  monthly energy data refresh) runs on schedule without a human WRK item
- **Surrogate model layer** for digitalmodel: train on existing OrcaFlex run library;
  expose a fast parametric query interface for design-space exploration
- **Autonomous report drafting**: AI produces a full engineering report draft from solver
  outputs; cross-review confirms; human reviews final, not intermediate steps
- **Digital twin pilot**: one active client asset connected to a live data feed;
  the Sense-Plan-Act loop runs in near-real-time for that asset
- **Engineering as a Service pilot**: one end-to-end workflow (brief → simulation → report)
  delivered without human initiation of any intermediate step

### Horizon 3 — Level 5: Engineering as a Service (18+ months)

- **Self-optimising skill library**: agents propose and execute improvements to their own
  skills based on session-quality signals from the comprehensive-learning pipeline
- **Multi-agent market**: specialised agents bid on sub-tasks within a workflow; the
  orchestrator selects based on cost, speed, and past accuracy
- **External Engineering as a Service**: AI-orchestrated workflows exposed as a service
  offering via aceengineer-website — clients submit briefs, receive validated deliverables

---

## The WRK Scoring Rubric

Before assigning priority to any new WRK item, score it against these four questions:

1. **Does it close a named gap** in the capability table above?
2. **Does it move a repo up the autonomy ladder** — from L2 to L3, or L3 to L4?
3. **Does it tighten the Sense → Plan → Act loop** — richer signals, better planning, faster execution?
4. **Does it reduce time-to-first-autonomous-result** for at least one workflow?

Items scoring **3–4** are elevated priority regardless of original complexity estimate.
Items scoring **0–1** are deprioritised unless they have a clear external dependency reason.

---

## Industry Benchmark

The closest operational reference point is the Siemens Electronics Factory in Nanjing,
recognised by the World Economic Forum as a Lighthouse Factory at Level 4 autonomy.
Outcomes versus 2022 baseline: lead times −78%, time-to-market −33%, productivity +14%,
field failures −46%, carbon emissions −28%.

The Siemens–NVIDIA partnership (announced CES 2026) is building the world's first fully
AI-driven, adaptive manufacturing site in Erlangen targeting Level 5 — the "Industrial AI
Operating System" running the Sense-Plan-Act loop at factory scale.

For computational engineering, the equivalent benchmark is **Ansys Engineering Copilot**
(2025 R2), embedded in every major solver. The gap it does not close — and where this
ecosystem operates — is *cross-solver, cross-discipline workflow orchestration*. Ansys
helps engineers inside one tool; the opportunity is autonomous orchestration *across* tools.

---

*Sources: Zvi Feuer — "Beyond Automation" (LinkedIn, 2024–2025); Deloitte Technology
Predictions 2026; IDC AI-Driven Manufacturing 2025; Siemens CES 2026 press releases;
Ansys 2025 R2 release notes; WEF Lighthouse Factory programme.*

*Last updated: 2026-02-24 | WRK-373 | Maintained in workspace-hub/docs/vision/*
