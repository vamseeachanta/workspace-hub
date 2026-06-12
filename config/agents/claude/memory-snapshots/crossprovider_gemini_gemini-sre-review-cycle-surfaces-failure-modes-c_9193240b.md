---
name: crossprovider gemini gemini-sre-review-cycle-surfaces-failure-modes-c
description: Gemini SRE review cycle surfaces failure modes Claude misses
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [code-review, cross-provider-review, failure-analysis]
---

After Claude drafts a plan, submit to Gemini with explicit 'robustness, failure modes, long-term maintainability' stance. Gemini SRE mindset catches: L3 parser edge cases (partial YAML, fenced code), state corruption scenarios, undocumented rate limits, nightly cron hazards. Produces a refined plan with explicit mitigations that Claude alone would miss.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
