---
name: crossprovider gemini alphanumeric-version-comparison-needs-natural-so
description: Alphanumeric version comparison needs natural sort
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [parsing, version-handling, bug-prevention]
---

Version parts like CFR 250.901 cannot be parsed as int(); crashes result. Use natural/alphanumeric comparison (e.g., sort tuples of normalized parts) to handle mixed numeric and alphabetic version identifiers.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
