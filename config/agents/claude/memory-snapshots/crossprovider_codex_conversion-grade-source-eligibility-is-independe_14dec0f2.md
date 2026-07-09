---
name: crossprovider codex conversion-grade-source-eligibility-is-independe
description: Conversion-grade source eligibility is independent of numerical correctness
metadata:
  type: reference
  source: codex
  bridged: 2026-07-07
  tags: [conversion-policy, source-hierarchy, data-quality]
---

A field-specific conversion factor is eligible only if its SOURCE CLASS meets policy (e.g., operator/regulator/assay/technical-literature) AND its derivation is direct or explicitly approved multi-source — not if the number is numerically correct. Trade-press tables (OGJ, compilations) are secondary sources, policy-ineligible even if accurate. Fail-closed semantics: absence of policy-grade evidence → keep `accepted_for_conversion=false`, not "accept tentatively." Example: Gaviota 52.7° API from OGJ is corroboration only, conversion-ineligible.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
