---
name: crossprovider gemini ensemble-planning-with-provider-stance-matrix
description: Ensemble planning with provider/stance matrix
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [planning, multi-agent, ensemble, non-determinism]
---

To surface alternative framings and detect consensus vs. disagreement in planning, dispatch 9 concurrent agents across 3 providers (Claude, Codex, Gemini) with 3 different stances each: conservative/creative/adversarial for Claude, feasibility/architecture/testing for Codex, risks/simple/extensibility for Gemini. Synthesize outputs with confidence scores (CONSENSUS/SPLIT/SOLO) per decision point; SPLIT decisions pause and present unresolved choices to user before proceeding.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
