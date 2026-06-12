---
name: crossprovider codex attested-evidence-blocks-formalize-plan-verifica
description: Attested evidence blocks formalize plan verification against live repo state
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [planning, review-process, verification]
---

Plan review can cite `## Attested Evidence` blocks produced at dispatch time that verify facts (file existence, issue state, commit SHA) via `gh issue view --json` and `ls -la` with flag-injection guards. Prefer attested facts over plan assertions; cite contradictions as findings.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
