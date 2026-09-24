---
name: crossprovider gemini codex-sustained-major-across-multiple-review-rou
description: Codex sustained MAJOR across multiple review rounds signals genuine plan defects
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [cross-provider-review, plan-quality, governance]
---

When one provider sustains the same severity (especially MAJOR) through successive review iterations while others converge to MINOR, it reveals genuine defects that incremental patch cycles miss. #2289 shows Codex sustaining MAJOR through v1–v6 despite fixes each round, forcing deeper refinements (hook split, precedence cascade, timestamp normalization, UTC tie-break, scenario matrix expansion, approval-after-revert narrowing). Each fix addressed a Codex-sustained category. Don't assume convergence on MINOR when one provider's verdict diverges.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
