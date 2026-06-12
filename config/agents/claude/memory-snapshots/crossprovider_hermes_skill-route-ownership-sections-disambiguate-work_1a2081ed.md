---
name: crossprovider hermes skill-route-ownership-sections-disambiguate-work
description: Skill route ownership sections disambiguate workflow defaults
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [skills, routing, metadata, canonical-route]
---

Add explicit 'Route ownership' sections to canonical skills to clarify which skill is the default/canonical route for a given workflow context (e.g., workspace-hub, GitHub issue planning). Boundary skills (exception paths like generic planning or PR-centric workflows) should document when they should NOT be the default, preventing misapplication and silent routing failures.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
