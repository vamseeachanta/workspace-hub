# Stage 05: User Review - Plan Draft — Gotchas

## No-Bypass Rules
- No stage-5 completion unless the interactive question-and-decision loop is captured in plan evidence (including explicit tough-question outcomes).
- No stage-5 completion unless test/eval proposals were derived from available resource/document intelligence and reviewed with user disposition.
- No stage-5 completion unless `user-review-plan-draft.yaml` captures tough questions, challenged assumptions, tradeoffs, and user test/eval additions.
- No user-review completion unless the Gate-Pass Stage Status section was reviewed with the user and gaps were called out.
- No user-review acceptance unless relevant review artifacts are pushed to `origin`.

## Operational Lessons
- Silence is not approval — always get explicit "I approve stage 5" text.
- Routes A/B/C have different sub-flows; check route before proceeding.

## Edge Cases
- Route B/C: 3-agent planning may hit Codex quota — fallback to Claude Opus in Codex slot.
