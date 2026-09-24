---
name: crossprovider gemini never-execute-commands-extracted-from-memory-or-
description: Never execute commands extracted from memory or text
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [security, memory-systems, acl, code-execution]
---

Memory governance systems (and any text-parsing tools) must never parse and execute commands found in untrusted text, even as opt-in features. This creates ACE vulnerabilities. Replace with static analysis (e.g., checking if a referenced script exists) or remove entirely.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
