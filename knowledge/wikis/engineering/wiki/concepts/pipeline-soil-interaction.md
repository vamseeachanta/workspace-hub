---
title: "Pipeline Soil Interaction"
tags: [pipeline, subsea, soil-interaction, embedment, berm, dnv-rp-f114, axial-resistance]
added: 2026-05-03
last_updated: 2026-05-03
---

# Pipeline Soil Interaction

## Scope

Models for axial, lateral, and vertical pipe-soil resistance at the as-laid pipeline–seabed interface. This page covers embedment, berm formation, and history-dependent resistance, providing the soil-side input for stability and buckling design. It does NOT cover free-span fatigue mechanics (see [[free-span-viv-fatigue]]) or onshore buried-pipeline geotechnics in detail.

## Key Concepts

- **As-laid embedment** — pipeline self-weight, dynamic-lay penetration, and soil shear strength set the initial penetration; embedment is the lever for both vertical and lateral resistance.
- **Axial resistance** — friction-dominated for sand, undrained-shear-strength-dominated for clay; driven by [[pipeline-walking]] and [[pipeline-end-expansion-spool-design]] envelope sizing.
- **Lateral resistance** — passive-soil-resistance plus berm formation as the pipeline ploughs sideways; controls [[pipeline-on-bottom-stability]] and [[pipeline-lateral-buckling]] mode wavelength.
- **Berm formation** — soil pushed in front of a laterally-displacing pipeline accumulates as a berm, increasing resistance until breakout.
- **Embedment-history dependence** — cyclic lateral motion progressively increases embedment; design-bound upper and lower envelopes capture brake-then-breakout behaviour.
- **Uplift resistance** — for trenched/buried lines, vertical pull-out resistance from cover soil drives [[pipeline-upheaval-buckling]] design.

## Standards / References

- DNV-RP-F114 (Pipe-Soil Interaction for Submarine Pipelines) — primary methodology. https://www.dnv.com/ <!-- TODO(W4-codify): replace external URL with [[../standards/dnv-rp-f114]] when standards page lands -->
- DNV-RP-F109 [[../../../engineering-standards/wiki/standards/dnv-rp-f109]] — on-bottom stability consumer of the soil-resistance models.
- DNV-RP-F110 (Global Buckling of Submarine Pipelines) — soil-resistance basis for lateral buckling. https://www.dnv.com/ <!-- TODO(W4-codify): replace external URL with [[../standards/dnv-rp-f110]] when standards page lands -->

## Cross-References

- **Related concept**: [[pipeline-on-bottom-stability]] — lateral resistance is the stability denominator.
- **Related concept**: [[pipeline-lateral-buckling]] — lateral resistance controls wavelength.
- **Related concept**: [[pipeline-upheaval-buckling]] — uplift resistance from cover soil.
- **Related concept**: [[pipeline-walking]] — axial resistance governs walking rate.
- **Cross-wiki (marine-engineering)**: [Pipeline Integrity Assessment](../../../marine-engineering/wiki/entities/pipeline-integrity.md) -- similar slugs (70%); similar titles (59%); shared tags: pipeline; shared keywords: concept, cross-references, key, pipeline, related; shared entities: DNV
