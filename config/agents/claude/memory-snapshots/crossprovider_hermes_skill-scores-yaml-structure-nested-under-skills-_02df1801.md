---
name: crossprovider hermes skill-scores-yaml-structure-nested-under-skills-
description: skill-scores.yaml structure: nested under skills key with hot/warm/cold/dead tiers
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [skill-management, configuration, hermes]
---

skill-scores.yaml organizes skills under a top-level `skills:` key (not flat) with tiers named `hot`, `warm`, `cold`, `dead` (not `active`). Essential for any cross-agent skill analysis or gap detection that relies on scored skill data.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
