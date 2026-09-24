---
name: crossprovider codex feature-availability-vs-enforcement-gap-in-accep
description: Feature availability vs. enforcement gap in acceptance criteria
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [acceptance-criteria, feature-enforcement, requirements-tracing]
---

Plans conflate 'we added a capability/flag' with 'it is enforced by default.' Making a gate or check opt-in (default off) does NOT satisfy a requirement to 'add a blocking gate' — acceptance tests can pass even when enforcement is disabled. Acceptance criteria must require the feature to be enforced, not just available.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
