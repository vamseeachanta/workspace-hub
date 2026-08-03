# Disagreement report — plan #3784 (2026-08-02)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | The plan is well-evidenced and the scope boundaries are sound, but three defects would produce a |
| codex | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

(no findings unique to this provider)

### codex

- The review target is internally inconsistent: the inline plan says `config/tmux/tmux-autosave.timer` will use “`Persistent=true` so a missed window fires after boot,” while the checked-out plan at `docs/plans/2026-08-02-issue-3784-tmux-persistence-and-ssh-autoattach.md:299` says `Persistent=true` is deliberately not set. Those are opposite designs for the most dangerous part of the rollout, so the plan artifact under approval is ambiguous.
- The revised local plan still depends on an unverified plugin marker. `docs/plans/2026-08-02-issue-3784-tmux-persistence-and-ssh-autoattach.md:260-264` says the implementation will “consult the marker resurrect/continuum actually writes.” I grepped the installed plugin code and found no durable restore-in-progress marker: `~/.tmux/plugins/tmux-resurrect/scripts/restore.sh:19-21` only uses process-local shell variables, and `~/.tmux/plugins/tmux-continuum/scripts/continuum_restore.sh:13-18` directly invokes resurrect’s restore script. A test with a synthetic “marker present” fixture would prove wrapper behavior against a marker the real plugin may never create.
- The review gate artifacts are invalid. The plan header names `scripts/review/results/2026-08-02-plan-3784-codex.md` and `...-agy.md` at `docs/plans/2026-08-02-issue-3784-tmux-persistence-and-ssh-autoattach.md:9`; `scripts/review/results/2026-08-02-plan-3784-codex.md` is 0 bytes and `scripts/review/results/2026-08-02-plan-3784-agy.md` is missing. `docs/plans/README.md:84-96` requires adversarial review artifacts from 2+ providers, with failed providers recorded as `UNAVAILABLE`, not empty or absent files.
- The plan has not reached the repository’s plan-review gate. `docs/plans/README.md:104-112` requires posting the completed plan to GitHub and applying `status:plan-review`; live `gh issue view 3784` shows `status:needs-plan`, and `git status --short` shows `docs/plans/2026-08-02-issue-3784-tmux-persistence-and-ssh-autoattach.md` is untracked. Implementation cannot start from this state.
- The plan index update is promised but absent. `docs/plans/2026-08-02-issue-3784-tmux-persistence-and-ssh-autoattach.md:306` lists `docs/plans/README.md` as an update target, but `rg "3784|tmux-persistence" docs/plans/README.md` returns no index row. That violates `docs/plans/README.md:74-80`, which requires adding the plan to the index during draft-plan creation.

