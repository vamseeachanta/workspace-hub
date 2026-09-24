---
name: crossprovider gemini no-output-vs-workflow-failure-environment-constr
description: NO_OUTPUT vs workflow failure: environment constraints are classified, not failures
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [gate-validation, machine-constraints, governance]
---

When a tool is not installed on a workstation (e.g., Codex CLI missing on ace-linux-1), this is classified as NO_OUTPUT—a known machine constraint—not a gate failure. Gate evidence documents this explicitly; production items may re-run on a different workstation if the tool is required. This prevents false negatives and distinguishes environmental limits from actual defects.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
