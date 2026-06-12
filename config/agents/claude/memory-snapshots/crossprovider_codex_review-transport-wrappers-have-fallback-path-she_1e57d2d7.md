---
name: crossprovider codex review-transport-wrappers-have-fallback-path-she
description: Review transport wrappers have fallback-path shell bugs
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [shell-bugs, review-transport, fallback-paths]
---

Codex fallback path in cross-review.sh uses `local` outside functions (runtime error) and artifact preservation doesn't match documented contract. Raw provider output deleted on exit while docs claim it's preserved; affects fallback when Claude NO_OUTPUT.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
