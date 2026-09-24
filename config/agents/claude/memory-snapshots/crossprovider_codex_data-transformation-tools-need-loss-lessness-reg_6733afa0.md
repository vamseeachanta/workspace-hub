---
name: crossprovider codex data-transformation-tools-need-loss-lessness-reg
description: Data-transformation tools need loss-lessness regression tests
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-loss, regression-testing, chunker]
---

Wiki chunker dropped rows from variant table shapes because it assumed a single column format and didn't section-bound extraction. Fix: extract all `| [` rows inside `## Sources` section boundary, regardless of column count. Regression test must verify input row-set equals (index + chunked pages) output row-set using `diff <(git show origin/main:index.md | grep | sort -u) <(cat index.md chunks/* | grep | sort -u)`.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
