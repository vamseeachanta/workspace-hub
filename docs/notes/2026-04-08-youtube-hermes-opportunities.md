# YouTube review notes — Hermes ecosystem opportunities

Date: 2026-04-08

Reviewed videos
- https://youtu.be/u_dHaxt-8MI — Hermes + Manim skill for animated explainer videos
- https://youtu.be/Mb5N08xcxtg — Hermes + Karpathy LLM Wiki for persistent compounding knowledge
- https://youtu.be/bc4NrE0cOE0 — Auto Research / self-improving skills loop

## What matters for our repo ecosystem

### 1) LLM Wiki is the highest-value immediate fit
We already have wiki and knowledge infrastructure, but the biggest gap is systematic ingestion from:
- session logs / learnings
- engineering docs and extracted references
- repo artifacts and generated reports

This is more valuable than generic self-improvement because it compounds engineering knowledge into reusable markdown pages and can later feed GTM/publication pipelines.

Related existing issues:
- #2011 feat: cross-wiki link discovery and infrastructure
- #2022 feat: publish repo knowledge bases as aceengineer.com content
- #103 WRK-1332: Archive synthesis + knowledge backfill
- #2016 feat(gtm): client conversion pipeline

Recommended new work:
- seed/refresh an engineering wiki from high-value sources
- define schema and ingestion conventions
- add incremental ingest/lint cron
- produce an operator playbook so Claude Code can run the workflow directly

### 2) Manim should be applied to GTM and engineering explainers
We already have animation capability in the ecosystem. The best use is not generic video creation, but engineering explainers and GTM collateral:
- mooring / riser / catenary animations
- installation sequence explainers
- report companion animations
- website / outreach assets

Related existing issues:
- #1809 GTM: Create .gif screencasts of all 5 demo reports running
- #2016 feat(gtm): client conversion pipeline
- #2022 feat: publish repo knowledge bases as aceengineer.com content

Recommended new work:
- build one reusable engineering animation pipeline
- start with 2-3 flagship examples tied to demo reports
- make outputs suitable for website + outreach + README embeds

### 3) Auto-research / self-improvement is useful but not first
We already have strong self-improvement paths via session logs and repo-level learning. The immediate bottleneck is not “how to self-improve everything,” but “how to convert more repo knowledge into reusable artifacts and client-facing assets.”

So this stream should prioritize:
1. wiki compounding
2. GTM animation assets
3. only then deeper autonomous skill optimization

## Recommended execution order
1. Create and execute an issue for engineering LLM wiki ingestion + cronized maintenance
2. Create and execute an issue for Manim-based engineering explainer pipeline
3. Later, revisit self-improvement/autoresearch using session-log analysis as input rather than as the primary stream
