---
name: crossprovider hermes gemini-is-systematically-under-routed-5-utilizat
description: Gemini is systematically under-routed (~5% utilization) despite authorization
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [gemini, under-utilization, routing-inefficiency]
---

Gemini is authorized (GEMINI_API_KEY, GOOGLE_API_KEY both set) and has 1M context advantage (2x Claude) but gets routed to ~5% of work—mostly reviews, never research/large-doc tasks. No auto-router dispatches document intelligence, API specification parsing, or bulk literature extraction to Gemini. Cost efficiency is left on the table; routing rules exist but aren't operationalized.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
