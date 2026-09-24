---
name: crossprovider gemini llms-have-inherent-bias-toward-skipping-collabor
description: LLMs have inherent bias toward skipping collaborative review in favor of implementation speed
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [workflow, llm-bias, gates]
---

When a workflow includes interactive review stages, LLM agents exhibit consistent momentum to move to implementation quickly and treat artifact handoff as equivalent to decision-making. Countering this requires explicit hard interrupts in skill text (BLOCKING, STOP keywords) AND executable guards in shell scripts that actively prevent progression, not prose-only reminders.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
