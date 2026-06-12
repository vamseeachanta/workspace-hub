---
name: crossprovider gemini pre-completion-qa-gate-invokes-domain-sme-skills
description: Pre-completion QA gate invokes domain SME skills for independent verification
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [qa, completion-gate, sme-verification]
---

Before marking WRK complete: (1) classify output type (rao-diffraction, mooring-analysis, mesh, data-pipeline, code), (2) invoke matching SME skill (orcaflex-specialist, mooring-analysis, etc.) as subagent, (3) run data-quality checks (NaN/Inf, schema, unit consistency), (4) generate HTML verdict report. Mandatory gate.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
