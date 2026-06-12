---
name: crossprovider hermes engineering-report-scope-caveats-must-be-in-all-
description: Engineering report scope caveats must be in all artifact types, not just markdown
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [engineering-reports, scope-boundaries, artifact-consistency, compliance]
---

For parametric engineering reports (yaw-moment, performance, etc.), critical scope caveats like 'not an incident reconstruction' and 'no class compliance conclusion' must be embedded consistently in HTML metadata, JSON provenance fields, and machine-readable manifests—not just in prose markdown. Inconsistent placement means downstream consumers and regulatory audits get incomplete safety boundaries.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
