---
name: crossprovider codex partial-input-correction-semantics-missing-one-i
description: Partial-input correction semantics: missing one input doesn't suppress independent terms
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [calculation-design, partial-inputs, null-semantics]
---

When a calculation has multiple independent components (e.g., Patterson slippage and FVF), missing one input should only suppress the output that requires it. Missing FVF should not suppress Patterson slippage; they require disjoint inputs. Use separate validation for each term, not all-or-nothing checks. Test partial input cases explicitly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
