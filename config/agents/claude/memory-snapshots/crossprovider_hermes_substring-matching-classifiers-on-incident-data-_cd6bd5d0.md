---
name: crossprovider hermes substring-matching-classifiers-on-incident-data-
description: Substring-matching classifiers on incident data produce false positives
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [classification, incident-data, data-quality]
---

Broad substring patterns (e.g., 'weather', 'sank', 'overboard') match unrelated rows—'sank' caught fire/grounding outcomes, 'overboard' matched generic mooring ops. Use explicit pathway groups instead.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
