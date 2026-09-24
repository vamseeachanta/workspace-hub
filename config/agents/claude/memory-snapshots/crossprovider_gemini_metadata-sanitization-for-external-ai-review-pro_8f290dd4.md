---
name: crossprovider gemini metadata-sanitization-for-external-ai-review-pro
description: Metadata sanitization for external AI review providers
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [security, privacy, data-sanitization, ai-review]
---

Review payloads sent to third-party AI providers (Codex, Gemini) for cross-review require sanitization to prevent leaking repo-private metadata, internal issues, session artifacts, or secrets.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
