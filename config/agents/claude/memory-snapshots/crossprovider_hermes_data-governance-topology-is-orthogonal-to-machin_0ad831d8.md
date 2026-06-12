---
name: crossprovider hermes data-governance-topology-is-orthogonal-to-machin
description: Data-governance topology is orthogonal to machine repo placement
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-governance, repo-placement, dependency-mapping]
---

`/mnt/ace/*` data buckets, `/mnt/local-analysis/<repo>` Git checkouts, and private wikis at `/mnt/ace/<client>-wiki` define a separate topology. A repo's machine placement depends on data-access requirements (e.g., worldenergydata needs /mnt/ace access) in addition to workload; don't conflate the two.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
