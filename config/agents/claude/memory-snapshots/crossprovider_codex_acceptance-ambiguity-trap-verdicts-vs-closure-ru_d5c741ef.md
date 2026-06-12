---
name: crossprovider codex acceptance-ambiguity-trap-verdicts-vs-closure-ru
description: Acceptance ambiguity trap: verdicts vs closure rules
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [acceptance-criteria, release-blocking, clarity]
---

Plans with conflicting acceptance criteria and closeout conditions silently permit false positives. Example: accepting "failure evidence captured" as completion while stating "don't close until both tests pass." Split acceptance into distinct verdicts ("evidence captured" vs "validation passed") so implementers cannot misinterpret checkboxes as closure gates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
