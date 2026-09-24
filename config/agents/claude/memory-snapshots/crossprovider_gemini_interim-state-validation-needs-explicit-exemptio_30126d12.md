---
name: crossprovider gemini interim-state-validation-needs-explicit-exemptio
description: Interim state validation needs explicit exemptions in validation logic
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [queue-validation, state-machines, interim-states]
---

Queue validation checks must explicitly allow interim states like `status: coordinating` to exist in intermediate folders. Add exemption logic like `not (status == "coordinating" and expected_folder_status == "working")` to prevent false-positive validation errors during state transitions.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
