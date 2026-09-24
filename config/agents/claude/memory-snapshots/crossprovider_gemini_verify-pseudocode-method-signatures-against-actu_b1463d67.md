---
name: crossprovider gemini verify-pseudocode-method-signatures-against-actu
description: Verify pseudocode method signatures against actual codebase
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [adversarial-review, pseudocode, plan-review]
---

Plans often assume simplified method signatures (e.g., `fetch(ticker)`) that diverge from reality (e.g., `fetch(ticker, start_date, end_date, use_cache)`). Adversarial review must read the actual implementation before accepting pseudocode. Framing parameter mismatches as "1-line fixes" masks real complexity.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
