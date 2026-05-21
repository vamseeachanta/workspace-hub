# Execution-Stage Adversarial Review: #2745 acma-projects freeze
> **Reviewer:** Claude (T9 cross-review, T2 complexity)
> **Date:** 2026-05-20
> **Evidence file:** `scripts/review/results/2026-05-20-execute-2745-evidence.md`
> **Plan:** `docs/plans/2026-05-20-issue-2745-acma-projects-freeze.md`
> **Live inspection performed:** Yes — all key artifacts independently verified via Bash, not trusted from evidence file

---

```
VERDICT: APPROVE_WITH_MINOR
```

---

## FINDINGS

### BLOCKERS (none)

No blockers to close. All primary freeze objectives achieved and independently verified.

---

### NON-BLOCKING OBSERVATIONS

**[MINOR — Operational Risk] Diverged local/remote HEAD not documented in reversal instructions.**
Local HEAD `a81d3c7c` and origin/main `a7727671` are genuinely diverged (same tree `8eff374d`, same parent `105c9ce8`, different SHAs from different commit paths). After `git fetch`, git reports "Your branch and 'origin/main' have diverged, and have 1 and 1 different commits each." `git pull --ff-only` fails. The STATUS-FROZEN.md Reversal section says only: `gh repo unarchive` + edit .git/config + update STATUS file. It does NOT say: `git fetch && git reset --hard origin/main` to reconcile the shadow commit before re-enabling push. A future operator following the documented reversal steps would attempt `git push` with a diverged history and get a non-fast-forward rejection. This is cosmetic in the frozen state (pushurl blocks it anyway) but is a real operator trap if reversal is ever attempted.
**Recommendation:** Add one line to the Reversal section: `git fetch origin && git reset --hard origin/main` (reconcile local shadow commit before restoring push permission).

**[MINOR — Verification Gap] T5 hook test used direct-exec, not actual `git commit` invocation.**
The plan required: `git add .test-guard-fires && git commit -m "test" 2>&1 | grep "FROZEN"`. Evidence documents: "Direct-exec verification (bypasses D-state git commit)." The hook is installed, executable, and confirmed to output the correct FROZEN error at exit 1. However, the actual git commit code path was never exercised. This matters because the hook is the last resort against accidental local commits (the GH archive covers remote). The D-state bypass was documented and reasonable given disk pressure, but the AC as written (T5 + epic #2744 acceptance "guard/checker fails on new data ingestion") is strictly not satisfied — only "hook script exists and runs correctly when invoked directly" is proven.
**Recommendation:** When disk pressure allows, run `echo '' > /tmp/test-guard && cp /tmp/test-guard /mnt/ace/acma-projects/.test-guard-fires && git -C /mnt/ace/acma-projects add .test-guard-fires && git -C /mnt/ace/acma-projects commit -m "test" 2>&1 | grep -c "FROZEN"` to close the verification gap. File a follow-up note in [#2769](https://github.com/vamseeachanta/workspace-hub/issues/2769) or the issue comment.

**[MINOR — Backup AC literal miss] Backup file-count invariant unverified; proxy accepted.**
Plan AC (r2-codex finding 3): "Backup directory file count + top-dir listing match T0.5 pre-snapshot exactly." Evidence documents: file count (`find -type f | wc -l`) hangs on ext4 D-state; verified by path-isolation argument instead. The proxy argument is sound (no freeze code path touched the backup dir; top-dir listing is identical) but the AC was written precisely because `du -sh` alone is insufficient — yet the literal binding check was still not done. The 10,729 pre-count from T0.5 is captured in `/tmp/acma-backup-precount.txt`; the post-count was never written to `/tmp/acma-backup-postcount.txt`. Path-isolation is a defensible substitute given the constraint, but it is a documented deviation from the strict AC.
**Recommendation:** Add to T10 evidence comment: "T7 backup file-count invariant DEVIATED — literal count not rerun due to ext4 D-state; post-count validation deferred to [#2769](https://github.com/vamseeachanta/workspace-hub/issues/2769) once disk pressure resolves."

**[MINOR — T8 deviation from plan AC] Legal-sanity scan killed; scope-correct grep accepted.**
Plan AC: "Legal-sanity scan runs at T8 on workspace-hub AND captures STATUS-FROZEN.md content scan; exit 0." Actual execution: `scripts/legal/legal-sanity-scan.sh` killed after 7+ minutes due to 33K-file scan on workspace-hub; replaced with targeted grep over task-touched files only. The grep correctly found no secrets, no private-key markers, and no deny-listed client names. I independently verified: STATUS-FROZEN.md does NOT contain "31522-woodfibre-lng" or any deny-listed pattern from `.legal-deny-list.yaml`. The intent of the AC is satisfied. The deviation is the method (grep vs full scan), not the outcome.
**Recommendation:** Document in T10 evidence comment. The full `legal-sanity-scan.sh` bottleneck on workspace-hub is a separate systemic issue (33K files, 7+ min runtime) — file a follow-up issue if the scan needs performance improvement for routine use.

**[MINOR — Pre-completion cleanup audit not documented in evidence.]**
Plan AC: "Pre-completion cleanup audit per coordination/pre-completion-cleanup-audit skill: CLEAN or EXPECTED only; no UNEXPECTED residue." The evidence file (T0–T8, 296 lines) contains no mention of the cleanup audit. This is a process gap — either it was run and not documented, or it was skipped. The audit is a SOUL.runtime.md hard gate ("never report all done with UNEXPECTED residue present").
**Recommendation:** Run and document the cleanup audit in the T10 evidence comment before closing #2745.

**[NON-BLOCKING — T3 Deviation Audit Trail Note] API PUT commit vs local git push creates two-author history.**
The GH commit `a7727671` was created via GitHub Contents API PUT using the noreply email (`23155845+vamseeachanta@users.noreply.github.com`). The local shadow commit `a81d3c7c` uses `achantav@gmail.com`. Both have identical tree SHA (`8eff374d`), same parent (`105c9ce8`), and same message. Blob SHA match confirmed (`8bed2d970fb3a6aa3d37bb3409d3f4a4465adadf`). The freeze intent is fully achieved — the file is on GH before archive, content is correct, and the repo is archived. The author/committer email discrepancy is cosmetically inelegant but carries no operational risk in an archived repo. Future cloners see the noreply commit as HEAD; local working copy has the orphaned shadow commit contained by pushurl=no_push.

**[NON-BLOCKING — Post-commit hook at /mnt/ace/acma-projects/.git/hooks/post-commit is dead code.]**
The post-commit hook references `$HOOK_DIR="/mnt/github/workspace-hub/scripts/ai-review"` — a path that does not exist (`/mnt/github/` is absent on this machine). The hook silently no-ops on every commit. This predates the freeze and is not a freeze defect, but future operators should be aware this hook is non-functional.

**[NON-BLOCKING — T10 not yet executed; #2745 remains open.]**
At review time, #2745 has `status:plan-approved` label and is OPEN. No T10 close-with-evidence comment has been posted. This is correct posture — the implementer has not pre-closed the issue and has reserved T10 for post-review execution. The `feedback_never_offer_to_self_label_plan_approved` gate is properly observed.

---

## AC SATISFACTION TABLE

| AC | Status | Notes |
|---|---|---|
| T0 parallel-work check | PASS | Evidence complete; SOUL.md discriminator (journal vs active) acceptable here |
| STATUS-FROZEN.md committed+pushed BEFORE archive | PASS | Commit `a7727671` at T00:16:21Z; archive confirmed after; ordering verified via T3/T6 timestamps |
| STATUS-FROZEN.md content matches plan (no backup-disposition, correct links) | PASS | Live blob SHA confirmed; content decoded and verified; "revisit criteria" correctly delegated to #2769 |
| remote.origin.pushurl = no_push | PASS | Live config confirmed: `no_push://vamseeachanta/acma-projects-frozen` |
| Fetch URL preserved | PASS | `https://github.com/vamseeachanta/acma-projects` intact |
| Pre-commit hook installed + verified | PARTIAL | Hook installed, direct-exec verified, git commit pathway not tested due to D-state |
| isArchived: true on GitHub | PASS | Live API confirmed |
| Backup file count + top-dir match pre-snapshot | PARTIAL | Top-dir match confirmed; file count unverified (D-state hang); path-isolation argument accepted |
| Legal-sanity scan T8; exit 0 | PARTIAL | Scope-correct grep substituted; no deny-list hits independently confirmed |
| T9 execution-stage adversarial review | IN PROGRESS | This document is the T9 review |
| #2746 at status:plan-approved or later | PASS | Live labels: `status:plan-approved` confirmed |
| T10 evidence comment posted on #2745 | NOT YET | Deferred to post-T9 completion |
| #2745 closed with evidence | NOT YET | Correct — awaiting this review then T10 |
| Pre-completion cleanup audit | MISSING | Not documented in evidence; must run before close |

---

## DEVIATION ASSESSMENT

**T3 API PUT substitution for `git push origin main`:** ACCEPTABLE. The end state (STATUS-FROZEN.md committed on origin/main before archive, correct content verified by blob SHA) genuinely satisfies the plan AC. The deviation creates a local shadow commit divergence which is contained by pushurl=no_push and GH archive. The reversal path omission (minor finding above) is the only residual risk.

**T5 hook direct-exec substitution for git commit test:** ACCEPTED WITH NOTE. The hook is functional; the git commit pathway test was blocked by the same ext4 D-state that blocked T3. The redundant protection layers (GH archive + pushurl=no_push) mean the hook's untested git-invocation path has low practical impact. Document and defer verification to disk-pressure-free window.

**T7 backup file-count proxy:** ACCEPTED WITH NOTE. Path-isolation argument is sound; no freeze code path could have mutated the backup directory. The deviation from the literal AC is documented.

**T8 scope-correct grep vs full legal scan:** ACCEPTED. Intent satisfied; method deviated. No deny-list exposure found independently.
