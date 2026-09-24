---
name: crossprovider codex openai-responses-api-vs-images-api-model-placeme
description: OpenAI Responses API vs Images API model placement
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [openai, api, image-generation, error-handling]
---

OpenAI's image generation model gpt-image-2 belongs in the Images API model parameter, not in the Responses API tools object. Passing it in tools returns a 400 error citing param: tools as the problem location.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
