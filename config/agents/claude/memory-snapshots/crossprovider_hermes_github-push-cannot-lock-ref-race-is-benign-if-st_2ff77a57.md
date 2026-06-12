---
name: crossprovider hermes github-push-cannot-lock-ref-race-is-benign-if-st
description: GitHub push cannot-lock-ref race is benign if state matches
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, github, push, race-condition]
---

Push warnings about 'cannot lock ref' appear repeatedly but are benign: verify with `git fetch` and confirm local HEAD matches `origin/main`. State matching proves the push succeeded despite the transient lock warning.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
