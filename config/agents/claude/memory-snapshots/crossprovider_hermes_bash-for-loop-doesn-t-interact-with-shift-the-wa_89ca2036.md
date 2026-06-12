---
name: crossprovider hermes bash-for-loop-doesn-t-interact-with-shift-the-wa
description: Bash for-loop doesn't interact with shift the way you'd expect
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [bash, gotcha, argument-parsing, shell-scripting]
---

When using `for i in "$@"`, the loop has already expanded all positional arguments before executing the body. A `shift` inside the loop doesn't affect the loop iteration — it only affects $@ for later code outside the loop. Use explicit iteration over an array instead if you need shift to work.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
