---
name: crossprovider hermes shell-regex-anchors-don-t-match-indented-blocks
description: Shell regex anchors don't match indented blocks
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [shell, regex, hooks, generation]
---

Pattern `^if [[ ... ]]` fails to match when the if-statement is indented inside another block. Generated hook patterns must either strip indentation during matching or insert guards with matching indentation. Indented early-exit blocks are valid shell syntax but invisible to line-start anchors.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
