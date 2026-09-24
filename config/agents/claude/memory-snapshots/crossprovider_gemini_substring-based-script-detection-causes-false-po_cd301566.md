---
name: crossprovider gemini substring-based-script-detection-causes-false-po
description: Substring-based script detection causes false positives
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [code-detection, regex, substring-matching]
---

Using `in` operator to detect script calls (e.g., `'test' in line`) falsely matches script stems to unrelated words ('test' in 'latest'). Use word boundaries (`\btest\b`) or full-path matching. Standard pitfall in code-detection heuristics.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
