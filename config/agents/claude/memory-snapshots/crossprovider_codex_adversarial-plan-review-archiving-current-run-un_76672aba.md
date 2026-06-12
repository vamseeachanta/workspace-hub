---
name: crossprovider codex adversarial-plan-review-archiving-current-run-un
description: Adversarial plan review archiving: current run unversioned, prior rounds numbered
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [planning-workflow, artifact-naming, review-cycles]
---

Plan review artifacts are authored as current-dated `${TODAY}-plan-${NNNN}-{claude,codex,gemini}.md` during a rerun; before the next rerun, they are immediately archived to `${PREV_DATE}-plan-${NNNN}-{claude,codex,gemini}-r${round}.md`. Plans iterate through many review rounds (12+ observed on #2510) with MAJOR findings patched between rounds. Only the unversioned current file is the rerun target.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
