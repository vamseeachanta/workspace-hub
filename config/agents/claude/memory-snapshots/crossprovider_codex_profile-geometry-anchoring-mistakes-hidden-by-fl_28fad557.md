---
name: crossprovider codex profile-geometry-anchoring-mistakes-hidden-by-fl
description: Profile/geometry anchoring mistakes hidden by flat survey data
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [geometry-validation, domain-specific-bug, engineering-data]
---

Bottom-section profile endpoints anchored to total rod length instead of pump measured depth can hide 50+ feet of error when the survey is flat or slowly varying. The defect emerges only when using real wells with depth/length mismatches. Always verify anchor points against the correct reference frame, not just visual inspection of nominal curves.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
