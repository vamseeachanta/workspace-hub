---
name: crossprovider hermes lane-e-discovery-requires-enriching-all-open-iss
description: Lane E discovery requires enriching all open issues, not just labeled ones
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [lane-classification, github-enrichment, continuous-pipeline]
---

Issues with implementation PRs/comments but no status labels will miss Lane E classification in live mode unless the enrichment step fetches PR evidence for every open issue, not just pre-filtered subsets.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
