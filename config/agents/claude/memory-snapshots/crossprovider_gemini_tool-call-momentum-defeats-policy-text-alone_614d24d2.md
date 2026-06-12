---
name: crossprovider gemini tool-call-momentum-defeats-policy-text-alone
description: Tool-call momentum defeats policy text alone
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [agent-behavior, workflow-design]
---

LLMs optimizing for end-to-end task completion chain tool calls past stage boundaries despite skill prose saying "stop here." Interactive stops require either executable gate blocks or explicit `ask_user` calls with clear question framing per dimension (scope, criteria, risks).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
