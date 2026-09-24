---
name: crossprovider gemini code-fence-stripping-pattern-for-gate-validation
description: Code fence stripping pattern for gate validation
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [regex, gate-logic, markdown]
---

Use `r"```[^\n]*\n.*?```"` with `re.DOTALL` to strip markdown code blocks before pattern matching in gates. Prevents false positives from code examples containing gate keywords or WRK references.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
