# Rules
Universal constraints only. Stage-specific rules live in micro-skills (`.claude/skills/workspace-hub/stages/`).

Files:
- `coding-style.md` — edit safety, path handling, harness file size
- `patterns.md` — enforcement gradient (prose → script → hook)
- `calc-citation-contract.md` — citation emission for standards-derived constants (per [#2481](https://github.com/vamseeachanta/workspace-hub/issues/2481), [#2685](https://github.com/vamseeachanta/workspace-hub/issues/2685))
- `codes-standards-data-routing.md` — vendor-licensed codes/standards data → private `vamseeachanta/llm-wiki` (post 2026-05-20 visibility flip)
- `wiki-sibling-routing.md` — `llm-wiki` + `llm-wiki-<client>` data/knowledge/result routing contract (suffix form, one-sibling-per-client, projects-as-folders; enforced by Level-2 `scripts/enforcement/check-wiki-sibling-frontmatter.py`; per [#2778](https://github.com/vamseeachanta/workspace-hub/issues/2778))
- `goal-invocation.md` — `/goal` invocation contract; consult [#2695](https://github.com/vamseeachanta/workspace-hub/issues/2695) catalog before invoking
- `completeness-before-close.md` — test-/evidence-based completeness score (0–100%) owner-verified before `gh issue close`; Level-2 advisory script + Level-3 GH Action gate (per [#2798](https://github.com/vamseeachanta/workspace-hub/issues/2798))
- `svg-pdf-portability.md` — no `<pattern>`/`clipPath`/`<filter>`/`<mask>` in PDF-bound or logo SVG (Cairo/Evince mis-paints them); verify with `pdftocairo`, not just Chrome/Poppler; fix at the canonical asset (per the 2026-07-03 digitalmodel-logo teal-band incident)
- `verify-ci-lint-toolchain.md` — before pushing, run the repo's EXACT CI lint toolchain (same black/isort/flake8 version + config; verify the binary exists); `ruff` ≠ `black`; a format pre-commit must use `uv run` so hook versions can't drift from CI (per the 2026-07-04 worldenergydata #821/#822 lint-drift incident)
- `merge-authorization.md` — what a user "merge and continue" authorizes an agent to run: per-PR, non-sticky, unambiguous-target-only; default remains verify-green + hand the human the command (per the 2026-07-03/04 elastic self-merge incident, [#3390](https://github.com/vamseeachanta/workspace-hub/issues/3390) item 4)
- `merge-cleanup.md` — a merge is not done until its remote branch, local branch, and worktree are gone; `--merged` UNDER-reports (squash rewrites SHAs) so its silence is not evidence; never remove a worktree holding unarchived uncommitted work (per the 2026-07-30 sweep: 44 merged-but-undeleted remote branches, 17 worktrees)
- `windows-junction-restore-safety.md` — never git-restore/recursively delete a shared-skill link path without probing LinkType first; junction children belong to the link target (per the 2026-07-16 canonical-skills wipe, [#3571](https://github.com/vamseeachanta/workspace-hub/issues/3571))
- `model-routing.md` — which model/provider gets which lane (Fable 5 = orchestration/planning/forensics; Opus 4.8 = marathons + browser + automatic fallback when Fable unavailable; Codex = also marathon implementation; Sonnet/Haiku = crawl + r1 review) + quota-resilience commit cadence and start-of-task grounding (per the 2026-07-06 session audit, [#3390](https://github.com/vamseeachanta/workspace-hub/issues/3390))
