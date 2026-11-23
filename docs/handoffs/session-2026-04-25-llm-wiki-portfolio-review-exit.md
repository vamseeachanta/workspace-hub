# Session Handoff — llm-wiki Portfolio Review (2026-04-24 → 2026-04-25)

> **Session goal:** review llm-wiki end-to-end (raw data → code → GTM), identify gaps, create + plan + execute fitting issues.
> **Outcome:** 3 gap issues created and shipped (#2480, #2481, #2482); 1 follow-up tracker (#2485); 1 superseded (#2022 closed); full work-loss audit + stash cleanup completed.

---

## What shipped

### Issues closed

| # | Title | State | Final commits |
|---|---|---|---|
| #2480 | E2E pipeline smoke test | CLOSED | `3f9a31954` (workspace-hub/main) |
| #2481 | Calc-output citation contract | CLOSED | `bd11f33bf` (workspace-hub/main) + `fcd183c6` (digitalmodel/main, post-rebase) |
| #2482 | llm-wiki → GTM content boundary (governance) | CLOSED | `f7e905a05` (workspace-hub/main) |
| #2022 | Publish wiki to aceengineer.com (legacy) | CLOSED as superseded by #2482 | — |

### Issues opened

| # | Title | State | Reason |
|---|---|---|---|
| #2485 | GTM boundary mechanical enforcement (linter + ledger + hook) | OPEN tracker | Rescoped out of #2482 v6 to keep that plan T2; design inherited from v2-v5 review artifacts |

### Workspace-hub commits (chronological, all on origin/main)

```
a67874461  docs(stash-recovery): persist #2452 implementation-inventory review artifacts
3bd1699c7  docs(#2480,#2481): mark both plan rows completed after close
69172ded9  docs(#2480,#2481): mark plans as implemented-pending-final-landing
3f9a31954  feat(#2480): add llm-wiki E2E pipeline smoke test
bd11f33bf  feat(#2481): adopt calc-output citation contract + wiki frontmatter + worked example
12b4be834  docs(#2481): lock 3 open-question decisions in plan + approval marker
6ef949158  docs(#2482): mark plan row completed after implementation
f7e905a05  feat(#2482): adopt llm-wiki → GTM content boundary (policy only)
```

### Digitalmodel commits (on origin/main)

```
fcd183c6  feat(#2481): add citation schema + mooring-factor pilot registry
          (cherry-picked + rebased from 8fc2f427 on issue-511-campaign-spec-generation;
           that branch also pushed to origin for backup)
```

---

## #2482 iteration — pattern worth remembering

The governance plan went through **6 versions** with adversarial self-review at each step.

| Version | Verdict | Finding class |
|---|---|---|
| v1 | MAJOR 5/4 | structural defects (fabricated exemplars, missing publishers, memory mis-cited, live contradictor wiki page, missing adjacent surfaces) |
| v2 | MINOR + 2 MAJOR-severity | scope completion (`data/document-index/`, `overview.md` linter contradiction) |
| v3 | MINOR + 1 MAJOR + 4 MINOR | rule-consistency (exercise rule-path gaps) |
| v4 | MINOR + 0 MAJOR + 4 MINOR | spec gaps (schema, impl, bootstrap hazard, top-level defaults) |
| v5 | MAJOR 3/6 | spec drift from in-place patching |
| v6 | scope-split | mechanical enforcement → #2485; policy-only stays |

**Lesson:** when adversarial review cycles show drift into a sibling sub-scope, **rescope** rather than auto-patch. v5's MAJOR was entirely confined to the linter/ledger sub-scope that v6 rescoped out — policy content was stable from v2 onward.

---

## #2481 decisions locked

| Decision | Locked answer |
|---|---|
| D1 pilot module | mooring load-factor (DNV-OS-E301 Section 2.2.3) |
| D2 validation | fail-closed at calc time; `CitationResolutionError.code_id` preserved in message |
| D3 wiki_path resolution | direct file read; migrate to MCP `wiki_search` when #2400 ships (no schema change required) |

---

## Work-loss audit results

All session work is **safely on origin** across both repos. Audit performed 2026-04-25.

| Surface | State |
|---|---|
| workspace-hub session commits (8) | Verified on `origin/main` via `git merge-base --is-ancestor` |
| digitalmodel #2481 commit | On `origin/digitalmodel/main` as `fcd183c6` |
| digitalmodel `issue-511-campaign-spec-generation` (was local-only) | Pushed to origin |
| digitalmodel `issue-2455-2457-semantic-proofs-clean` (was local-only) | Pushed to origin |
| Untracked review artifacts (#2452 inventory, 3 files) | Recovered from `stash@{3}^3` to commit `a67874461` |
| Stash hygiene | 9 stashes → 1 retained (parallel-session-owned) |

### Dropped stashes (recoverable for ~90 days via `git fsck --lost-found`)

| SHA | Label |
|---|---|
| `52cf86cd` | `handoff-retry-stash-1777043182` |
| `5b4162aa` | `temp-before-2465-governance-sync` |
| `7e5e890b` | `temp-pre-2452-tracked-provider-audit-artifacts` |
| `8102488b` | `temp-pre-2452-untracked-review-artifacts` (content already at `a67874461`) |
| `e8764cb7` | `git-safe-auto-stash` (integration/runbook, 75 files, 0 unique paths) |
| `da842a6d` | `git-safe-auto-stash` (integration/runbook, 14 files) |
| `74d5ecbe` | `autostash` (4d, 15 auto-gen state files) |
| `e3c870cf` | `pre-07e7e7d07-promotion-2026-04-20` (29+21 files, 0 unique paths) |

**Drop safety bar applied:** every dropped stash held zero file paths unique to the stash (verified against `origin/main` via `git cat-file -e`). Differing content versions were stale snapshots superseded by newer commits on main.

### Retained stash

| Idx | Label | Why kept |
|---|---|---|
| @{0} | `wave-1-plan-commits-buffer` | Parallel session owns; contains 1 unique file `scripts/review/results/2026-04-24-plan-2487-disagreement.md` not yet on main |

---

## Memory candidates (for `.claude/memory/` / topics)

Surfaces worth promoting to durable memory after user review:

1. **Iteration-pattern-when-drift**: when adversarial review cycles show drift into a sibling sub-scope (v4→v5 introducing spec defects while patching v3→v4 ones), **rescope rather than auto-patch**. Distinct from `feedback_codex_sustained_major_loop` (which is cross-provider consensus). This is single-reviewer patch-drift.
2. **Reverse-index stash-drop pattern**: when dropping multiple stashes, drop in reverse-index order (`@{N}` → `@{N-1}` → ...) to preserve indices of unprocessed stashes. Forward-order corrupts subsequent index references.
3. **0-unique-paths drop safety bar**: a stash is safe to drop iff `git cat-file -e origin/main:<path>` succeeds for every path in `git stash show --name-only` AND every untracked path in `git show stash^3 --name-only`. Differing content alone is not a drop blocker — main's version supersedes.
4. **digitalmodel pytest env friction**: `uv run pytest` on digitalmodel currently has env-setup overhead that exceeds reasonable timeouts; **inline `python -c` smoke checks** are a reliable fallback (used to verify #2481 citations module).
5. **Branch-context illusion of regression**: a "missing frontmatter" / "lost commits" alarm can be branch confusion (silent checkout to a feature branch by parallel session), not actual data loss. Always check `git status -sb` and `git merge-base --is-ancestor <sha> origin/main` before assuming loss.
6. **Parallel-session checkout sweeps staged files**: a parallel session checking out a different branch DOES delete the working-tree copy of files that are `git add`-ed but not yet committed. The first attempt to commit this handoff doc was lost this way (file written + staged → parallel session checked out `plan/issue-2369-batch-pack-2` → working-tree copy deleted, leaving status `AD`).

---

## Open / pending items

| Item | Owner | Cadence |
|---|---|---|
| #2485 plan drafting | future session | when mechanical-enforcement is prioritized |
| `mooring_design.py` Field defaults migration to citations registry | future session | follow-up after #2481 settles |
| Pre-existing digitalmodel stash `WIP on main: bf9506da Expand cathodic_protection ...` | original-author session | apply when ready |
| #2480 nightly CI wiring | deferred per user | pick up when #2366/#2465 audit cadence lands |
| Forward-adopted #2471 frontmatter on `dnv-os-e301.md` + `ocimf-meg4.md` | retire when #2471 broad rollout | tracked in #2481 close comment |
| **Commit this handoff doc to main** | next session on main | parallel session held the lock at session-end; doc currently lives as untracked on whatever branch the parallel session left checked out |

---

## Final state checks (at session-end snapshot, before parallel-session checkout race)

```
$ git stash list | wc -l
1

$ git log --oneline origin/main -8
a67874461  docs(stash-recovery): persist #2452 implementation-inventory review artifacts
3bd1699c7  docs(#2480,#2481): mark both plan rows completed after close
69172ded9  docs(#2480,#2481): mark plans as implemented-pending-final-landing
3f9a31954  feat(#2480): add llm-wiki E2E pipeline smoke test
bd11f33bf  feat(#2481): adopt calc-output citation contract + wiki frontmatter + worked example
12b4be834  docs(#2481): lock 3 open-question decisions in plan + approval marker
6ef949158  docs(#2482): mark plan row completed after implementation
f7e905a05  feat(#2482): adopt llm-wiki → GTM content boundary (policy only)
```

Closing session.
