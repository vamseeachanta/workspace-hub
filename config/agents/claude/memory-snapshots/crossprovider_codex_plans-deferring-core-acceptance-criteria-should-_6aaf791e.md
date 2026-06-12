---
name: crossprovider codex plans-deferring-core-acceptance-criteria-should-
description: Plans deferring core acceptance criteria should block acceptance or decouple scopes explicitly
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [planning, acceptance-criteria, scope]
---

Plans #608 and #609 defer their primary deliverable (mesh QA gates, auxiliary mesh handling) to upstream issues, then include acceptance tests that claim success while the core issue requirement remains unmet. Either block plan acceptance until dependencies land, or explicitly split scope into 'deferred' vs 'implementable' and test only the latter.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
