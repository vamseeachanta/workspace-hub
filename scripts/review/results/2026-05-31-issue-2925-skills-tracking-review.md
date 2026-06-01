# Adversarial Review — track 7 fleet skills swallowed by bare-dir gitignore (#2925)

- **Date:** 2026-05-31
- **Branch:** `fix/track-fleet-skills-2925`
- **Commit reviewed:** `4f03d50a7` (amended; pre-genericization was `4741cd36e`)
- **Reviewer:** Claude adversarial sub-agent (T1 — single-file/config scope), defect-hunting stance
- **Issue:** [#2925](https://github.com/vamseeachanta/workspace-hub/issues/2925)

## Scope

The commit adds two `!`-negation lines to `.gitignore` so `.claude/skills/digitalmodel/`
and `.claude/skills/memory/` (previously swallowed by bare-dir ignores `digitalmodel/`
L14 and `memory/` L298) become tracked, and adds 10 skill files (7 distinct skills)
that were untracked-local on dev-primary. Goal: propagate fleet skills that dev-primary
(404) has but dev-secondary / licensed-win-2 (396, == origin/main) lack. One skill
(`business_admin/personal-tax-filing-packet`) deliberately HELD (sensitive, `personal-*`).

## Verdict

**REQUEST-CHANGES → RESOLVED.** Gitignore mechanics verified textbook-correct; one MED
finding (machine-specific paths) and one LOW finding (path inconsistency) were both fixed
in the amended commit and re-verified.

## Findings

| # | Sev | Finding | Resolution |
|---|-----|---------|------------|
| 1 | MED | 26 lines across 6 files hardcoded `/home/vamsee` and `/mnt/local-analysis` — wrong-on-arrival for the heterogeneous fleet (esp. Windows licensed-win-2) the commit aims to propagate to. | Genericized: `/home/vamsee` → `~`; `/mnt/local-analysis` → `$WORKROOT` with a per-file convention note. Verified: zero `/home/vamsee` remain; `/mnt/local-analysis` remains only in the 2 explanatory convention notes. |
| 2 | LOW→MED | Two skills disagreed on the digitalmodel venv location (`workspace-hub/digitalmodel/.venv` vs sibling `digitalmodel/.venv`). | Reconciled against on-disk layout: `digitalmodel` and `assetutilities` are **siblings** under `/mnt/local-analysis` (verified `digitalmodel/.venv` exists; `workspace-hub/digitalmodel` does NOT). The `workspace-hub/`-nested form pointed at directories that exist on no machine — corrected to `$WORKROOT/{digitalmodel,assetutilities}`. Severity raised: it was wrong, not merely inconsistent. |

## Checks that PASSED (explicitly clean)

- **Last-match-wins placement** — negations at `.gitignore:304-305`, AFTER both `digitalmodel/` (L14) and `memory/` (L298). `git check-ignore` confirms the 7 skills resolve NOT-IGNORED.
- **Over-broad negation / drift** — `git status --porcelain` on both scoped trees is empty; on-disk set == `git ls-files` set. No binaries/junk swept in, nothing trackable left behind.
- **Collateral un-ignore** — the unrelated `memory/` data-dir ignore (L298) still fires for paths outside `.claude/skills/`; negation is anchored to `.claude/skills/memory/` only.
- **Held tax skill** — `business_admin/personal-tax-filing-packet/` is NOT in the commit and remains gitignored via `personal-*` (L277).
- **Secrets / keys / client-IDs / PII** — targeted scan of all 10 committed files: clean.

## Follow-up (out of scope for #2925)

The same nonexistent `workspace-hub/digitalmodel` nesting exists in several **already-tracked**
skills (`development/ci-test-debugging-gotchas/references/digitalmodel-worktree-test-execution-with-shared-venv.md`
— a stale copy of the skill fixed here — plus `business/gtm-parametric-demo-reports`,
`coordination/gtm-cross-review-readiness`, `data/excel-workbook-to-python-v2`). Recommend a
follow-up issue to genericize those too; not expanded into this commit to keep scope tight.
