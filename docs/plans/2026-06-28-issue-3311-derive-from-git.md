# Plan for #3311: Auto-derive the lean reference payload from git footprint

> **Status:** plan-approved (approach approved by user in-window 2026-06-28: git range since a base)
> **Complexity:** T1
> **Date:** 2026-06-28
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3311
> **Client:** N/A · **Lane:** lane:claude
> **Refines/feeds:** #3306 (lean renderer), #2110 (session-close emit side)

## Resource Intelligence
- Found: `scripts/workflow/build_session_review.py` (#3306) — renders a lean page from a `refs` payload. This issue adds the *deriver* that builds that payload from git so the page is no longer hand-authored.
- Found: squash-merge convention `subject (#NNN)` (every recent `main` commit) → reliable PR-number source, network-free.
- Found canonical doc homes (path→type): `docs/plans/`, `docs/session-handoffs/`, `docs/governance/*-decision.md`, `docs/reports/` (per #3306).
- Gap: no derivation; payloads are written by hand (as this stream's pages were).

## Implementation (TDD) — DONE in this PR
1. Pure `derive_refs(commit_messages, changed_files)`: PRs ← `(#NNN)` subject; issues ← other `#NNN`; changed docs → typed refs by path prefix; session-pages/manifest/index excluded; governance only `*-decision.md` counts. *(7 unit tests)*
2. `derive_payload_from_git(base, repo_root, …)`: thin wrapper gathering `git log --format=%B` + `git diff --name-only <base>...HEAD`, builds the v2 payload (slug←branch, date←today).
3. CLI: `--from-git --since <ref> [--slug/--title/--headline] [--emit-payload <path>]`. Default base = `merge-base(HEAD, origin/main)`. `--emit-payload` writes the derived payload for curation (the auto-draft path); else renders directly through the existing sanitize→render→manifest path.

## Acceptance criteria
- `--from-git --since <ref>` yields a lean page whose refs match the range's PRs/issues/changed-docs. ✓ (dogfooded on this branch)
- Derivation pure + unit-tested (PR/issue split, dedup, path→type, exclusions). ✓
- Sanitized-public gate unchanged. ✓

## Out of scope (follow-on)
- Stop/SessionEnd **hook** that runs `--from-git` automatically at session end (#2110 hook slice).
- gh-based issue↔PR re-classification (the `(#NNN)` heuristic is network-free and sufficient).
