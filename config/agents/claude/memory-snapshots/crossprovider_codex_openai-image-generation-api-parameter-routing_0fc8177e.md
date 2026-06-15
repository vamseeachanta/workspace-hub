---
name: crossprovider codex openai-image-generation-api-parameter-routing
description: OpenAI image generation API parameter routing
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [openai-api, provider-quirk, parameter-placement]
---

Image model names (e.g., `gpt-image-2`) go directly in `openai.images.generate({model: '...'})`, not in the Responses API `tools` array. Passing the model to `tools: [{type: 'image_generation', model: ...}]` produces a 400 `invalid_value` error on the `tools` param. Route by API entry point, not handler type.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
