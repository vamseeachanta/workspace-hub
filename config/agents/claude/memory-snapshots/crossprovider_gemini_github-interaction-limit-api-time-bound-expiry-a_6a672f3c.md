---
name: crossprovider gemini github-interaction-limit-api-time-bound-expiry-a
description: GitHub interaction-limit API: time-bound expiry and private-repo 405 response
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [github-api, security-automation, api-quirk]
---

GitHub's interaction-limit API enforces expiry dates (e.g., `six_months`) with no permanent setting. Private repos return HTTP 405 when attempting to set limits — renewal automation only applies to public repos. Limits must be actively renewed before expiry.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
