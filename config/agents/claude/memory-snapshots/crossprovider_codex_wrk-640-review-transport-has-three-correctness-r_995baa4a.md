---
name: crossprovider codex wrk-640-review-transport-has-three-correctness-r
description: WRK-640 review transport has three correctness regressions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review-transport, bash-scoping, validation-gap]
---

Bash `local` keyword used outside function in fallback path (crash on Codex NO_OUTPUT). Raw artifact preservation gap: scripts keep provider output only in temp files deleted on exit, contradicting documented behavior. False-positive validation: renderer coerces malformed JSON scalars to strings, allowing invalid output to classify VALID.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
