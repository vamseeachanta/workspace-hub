---
name: crossprovider gemini gemini-hallucinates-module-imports-when-apis-don
description: Gemini hallucinates module imports when APIs don't exist
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [gemini-quirk, hallucination-pattern, python-execution]
---

When Python modules don't exist (e.g., `google_search.gsd_list_workspaces()`), Gemini invents plausible imports rather than reporting unavailability. Suggests resolution errors occur post-parse, at module-call layer, not in static validation.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
