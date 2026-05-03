---
title: "Pipeline End-Expansion and Spool Design"
tags: [pipeline, subsea, spool, end-expansion, plet, tie-in, dnv-st-f101]
added: 2026-05-03
last_updated: 2026-05-03
---

# Pipeline End-Expansion and Spool Design

## Scope

Tie-in design at pipeline ends and mid-line breaks: end-expansion budget, expansion spools, mid-line tees, PLETs/PLEMs, and sleeper interaction. Boundary discipline: this page is pipeline-side hardware; SCR-flowline tie-in topology is named as adjacency only and not the primary subject. It does NOT re-cover corroded fitness-for-service (see [[pipeline-integrity-assessment]]).

## Out of Scope

- SCR riser fatigue (lives on the riser cluster pages).
- Free-span fatigue mechanics (see [[free-span-viv-fatigue]]).

## Key Concepts

- **Effective axial force** — fully restrained pipeline carries axial load proportional to ΔT × E × A; at line ends the force decays into displacement.
- **End-expansion budget** — predicted longitudinal displacement at the cold end (PLET, jumper, spool) over the operating-condition envelope.
- **Expansion spool** — Z-spool, U-spool, or Π-spool flowline absorbs end displacement through bending; geometry sized against fatigue, hub-misalignment tolerances, and pipelay overlay.
- **Mid-line tee / wye** — branch tie-in to a parallel flowline; locally raises constraint stiffness and modifies the effective-axial-force distribution.
- **PLET / PLEM** — pipeline-end-termination structures providing ROV-operable hub interfaces for jumper installation; landed during pipelay per [[pipeline-installation-methods]].
- **Walking interaction** — repeated startup-shutdown cycles per [[pipeline-walking]] consume the end-expansion budget directionally; spool sizing must account for cumulative drift.
- **Sleeper interaction** — sleepers used for [[pipeline-lateral-buckling]] modulate axial-force feed-in into the spool.

## Standards / References

- DNV-ST-F101 (Submarine Pipeline Systems — umbrella) [[../../../engineering-standards/wiki/standards/dnv-st-f101]] — design-basis posture for tie-in design.
- DNV-RP-F110 (Global Buckling of Submarine Pipelines) — feed-in interaction. https://www.dnv.com/ <!-- TODO(W4-codify): replace external URL with [[../standards/dnv-rp-f110]] when standards page lands -->
- API RP 1111 [[../../../engineering-standards/wiki/standards/api-rp-1111]] — limit-state design context.

## Cross-References

- **Related concept**: [[pipeline-walking]] — directional consumption of spool budget.
- **Related concept**: [[pipeline-lateral-buckling]] — sleeper-spool interaction.
- **Related concept**: [[pipeline-installation-methods]] — PLET landing tolerances feed into spool sizing.
- **Related concept**: [[pipeline-integrity-assessment]] — long-term tie-in fitness implications.
