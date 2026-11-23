#2269 draft plan is now through a real three-provider adversarial review wave.

Artifacts added
- `scripts/review/results/2026-04-15-plan-2269-claude.md`
- `scripts/review/results/2026-04-15-plan-2269-codex.md`
- `scripts/review/results/2026-04-15-plan-2269-gemini.md`

Current result
- all three providers returned MAJOR
- the plan is not approval-ready yet

Main blocker themes
1. bootstrap-path contract must be pinned (`/usr/lib/...` vs `/opt/...` probe order + failure rule)
2. wrapper-vs-runner responsibility split must be explicit
3. smoke/benchmark scope and YAML verdict schema need tighter closure
4. behavioral tests and requirement traceability need to be more explicit

I already patched the draft to absorb a first response wave, updated the local plan file/README to `plan-review`, and restored the live `status:plan-review` label now that the issue actually has a canonical plan artifact plus provider reviews.

Next step is another tightening patch wave against these MAJOR findings before this can be surfaced as approval-ready.
