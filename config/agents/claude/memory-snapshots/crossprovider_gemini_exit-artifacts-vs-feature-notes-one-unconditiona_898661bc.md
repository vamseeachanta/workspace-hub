---
name: crossprovider gemini exit-artifacts-vs-feature-notes-one-unconditiona
description: Exit artifacts vs feature notes: one unconditional, one informational
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [yaml, workflow, stages]
---

exit_stage.py treats exit_artifacts as unconditional—adding feature-specific artifacts fails non-feature WRKs. Use feature_notes: block instead for conditional/informational items. Prevents false negatives during stage transitions.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
