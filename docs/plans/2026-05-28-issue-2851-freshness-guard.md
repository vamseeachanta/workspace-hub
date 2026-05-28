# Plan for #2851: collect-equality freshness guard (prevent false divergences from stale checkouts)

> **Status:** adversarial-reviewed (Claude r1 MAJOR→fixed; Codex r2 pending)
> **Complexity:** T2
> **Date:** 2026-05-28
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2851
> **Client:** N/A
> **Review artifacts:** scripts/review/results/2026-05-28-plan-2851-{claude,codex}.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/readiness/collect-equality.sh` (merged #2801, `7cc51cc2f`, **unchanged since** — verified `git log 7cc51cc2f..origin/main`). Emits the 8-dim report; NO checkout-provenance fields.
- Found: `scripts/readiness/build-equality-matrix.py` — `verdict_for()` precedence + `load_reports()`. NO stale-checkout handling.
- Found: `tests/readiness/test_collect_equality.py` + `test_build_equality_matrix.py` (39 tests) — extend here.
- Gap: no `checkout_sha`/`dirty`/`behind_main` in the report; matrix cannot tell a fresh report from a stale one.

### Standards / Wiki
Not applicable — harness/ops.

### Documents consulted
- #2801 (parent) + its 2026-05-27 investigation comments — the empirical root cause (below).
- `.gitignore:180 !.claude/state/equality-*.yaml` — reports are git-tracked (transport).

### Gaps identified
- Collector records no checkout provenance → a stale/dirty tree's report is silently comparable to a fresh one.
- Matrix has no `STALE-CHECKOUT` state → contaminated reports produce false `EQUAL`/`DIVERGES`/`NO-MAJORITY`.

### Evidence (reproduction — this is the load-bearing artifact)
Verified live 2026-05-27 on ace-linux-1 (working tree 85 commits behind `origin/main`):
```
$ grep -rqi 'HTML.*default|default.*HTML' .claude/rules ; echo $?   # stale tree
1   # NO match -> b3=other
$ git grep -qi 'HTML.*default|default.*HTML' origin/main -- .claude/rules ; echo $?
0   # match -> b3=html
$ git rev-list --count HEAD..origin/main
85
```
→ dev-primary's committed report (b3=`other`, skills=407) was generated from a stale tree; dev-secondary (fresh main) got b3=`html`, skills=396. The "divergences" were **measurement artifacts**, not machine inequality. `crontab`-derived dims (scheduler) are branch-independent → those findings stand.

<!-- sources: #2851 body, #2801 + investigation comments, collect-equality.sh, build-equality-matrix.py, .gitignore, live repro = 6 -->

---

## Artifact Map
| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-05-28-issue-2851-freshness-guard.md |
| Collector (modify) | scripts/readiness/collect-equality.sh |
| Matrix (modify) | scripts/readiness/build-equality-matrix.py |
| Tests | tests/readiness/test_collect_equality.py, test_build_equality_matrix.py |
| Reviews | scripts/review/results/2026-05-28-plan-2851-{claude,codex}.md |

## Deliverable
The collector stamps checkout provenance (`checkout_sha`, `dirty`, `behind_main`) on every report, and the matrix renders `STALE-CHECKOUT` for any contaminated report — excluding it from peer comparison so a stale tree can never manufacture a false divergence. dev-primary's report is regenerated from a clean, current `main`.

## Pseudocode
```
# collect-equality.sh — add a provenance block (computed at collection time, BEFORE write)
checkout_sha = git -C "$WS" rev-parse --short HEAD            (or "unknown")
# dirty = tracked changes to MEASUREMENT-RELEVANT paths only (not unrelated untracked scratch):
dirty = [ -n "$(git -C "$WS" status --porcelain -- .claude scripts config 2>/dev/null)" ]  -> true|false
# behind_main = best-effort vs the LOCAL origin/main ref (no network fetch in the collector):
behind_main = git -C "$WS" rev-list --count HEAD..origin/main   (or "unknown" if ref absent)
emit under dimensions-sibling key:  provenance: {checkout_sha, dirty, behind_main}
# A1: hash EXCLUDES checkout_sha ONLY (pure churn — changes every commit/pull). It INCLUDES
#     dirty + behind_main, because those are freshness STATE: a clean->dirty or current->behind
#     transition (even with unchanged measured dims) MUST force a rewrite, else the committed
#     report keeps a stale dirty:false/behind:0 and the matrix is fooled again (the bug we fix).

# build-equality-matrix.py
def is_stale(report): p=report.provenance; return p.dirty is True or (p.behind_main not in (0,"0")) 
# in verdict_for precedence, ABOVE the COLD/UNIFORM split, BELOW unreachable/missing:
if report present but is_stale(report) -> "STALE-CHECKOUT"   (all dims for that machine)
# stale machines are EXCLUDED from the uniform peer value list (can't create false NO-MAJORITY/DIVERGES)
```

## Files to Change
| Action | Path | Reason |
|---|---|---|
| Modify | scripts/readiness/collect-equality.sh | add `provenance` block; exclude it from canonical hash |
| Modify | scripts/readiness/build-equality-matrix.py | `is_stale()` + `STALE-CHECKOUT` precedence + exclude stale from uniform comparison |
| Modify | tests/readiness/test_collect_equality.py | provenance fields + dirty-flag tests |
| Modify | tests/readiness/test_build_equality_matrix.py | STALE-CHECKOUT verdict + exclusion-from-peer tests |
| Update | docs/plans/README.md | index row |

## TDD Test List
| Test | Verifies | Expected |
|---|---|---|
| test_collect_emits_provenance | report has provenance.{checkout_sha,dirty,behind_main} | keys present |
| test_collect_dirty_true_on_modified_tracked | modify a tracked measurement path → dirty true | `dirty: true` |
| test_collect_dirty_false_on_clean | clean fixture repo → dirty false | `dirty: false` |
| test_collect_sha_excluded_from_hash | checkout_sha change ALONE → no rewrite (A1) | 2nd run skips |
| test_collect_dirty_change_forces_rewrite | clean→dirty with same measured dims → DOES rewrite (A1) | rewrite happens |
| test_collect_dirty_no_self_trigger | collector's own output doesn't make dirty true (captured pre-write) (A3) | `dirty: false` on clean tree |
| test_matrix_stale_checkout_verdict | dirty or behind>0 report → STALE-CHECKOUT for that machine's cells | `STALE-CHECKOUT` |
| test_matrix_stale_excluded_from_uniform | stale peer excluded → fresh machine's uniform dim is PENDING, not a false NO-MAJORITY (A2) | `PENDING` |
| test_matrix_fresh_unaffected | clean reports grade normally | EQUAL/CONFORMS as before |

## Acceptance Criteria
- [ ] Collector emits `provenance` (sha/dirty/behind_main); excluded from idempotency hash
- [ ] Matrix renders `STALE-CHECKOUT` and excludes stale reports from peer comparison
- [ ] `uv run pytest tests/readiness/` green
- [ ] dev-primary report regenerated from a clean current `main`; skills/b3 no longer diverge from dev-secondary
- [ ] Review artifacts posted

## Adversarial Review Summary
| Provider | Verdict | Findings |
|---|---|---|
| Claude (r1) | MAJOR → fixed | A1 hash must include dirty+behind_main (exclude sha only); A2 stale-exclusion test → PENDING not EQUAL; A3 dirty self-trigger test |
| Codex (r2) | PENDING | requires plan pushed |

**Overall:** r1 fixes applied; awaiting Codex r2 (T2). Not approval-ready until r2 clears.

## Risks and Open Questions
- **Risk:** `dirty` over the whole repo would false-flag on unrelated untracked scratch → scope to measurement-relevant paths (`.claude scripts config`). Reviewers: verify this scope is neither too broad (false stale) nor too narrow (misses a measured path).
- **Risk:** `behind_main` needs a recent fetch; the collector must NOT fetch (network/side-effect). v1 reads the local `origin/main` ref best-effort → `unknown` if absent. The scheduled job runs after repo-sync's pull, so the ref is fresh there. Document the caveat.
- **Open:** should `behind_main: "unknown"` (no local ref) be treated as STALE (fail-closed) or fresh? Recommend **STALE** (fail-closed — can't prove freshness). Flag for approval.
- **Implementation note:** must be implemented from a clean current `main` checkout (worktree), not the current stale local tree.

## Complexity: T2
Two files + tests, focused harness fix; T2 ⇒ Claude + Codex review.
