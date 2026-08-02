# Handoff — dispatch epic #3740 complete, both platforms proven

**Date:** 2026-08-02
**State:** everything merged to `main`; no branch of mine outstanding; working tree clean
**Prior handoff:** [`2026-08-01-dispatch-records-and-hostname-sweep.md`](2026-08-01-dispatch-records-and-hostname-sweep.md) — §2, §9, §10, §11 hold lessons not repeated here

---

## 1. Where things stand

| | |
|---|---|
| `4cd0928b` | slices 1–4 — records, claim protocol, reconciler, Linux runner (PR #3741) |
| `4d27a307` | slice 5 — lifecycle labels, unproven-vocabulary reporting, pilot drain (PR #3758) |
| `7701d4e7` | Windows fixes found by the first live run (PR #3760) |

**496 tests, hermetic.** Both pilots closed with evidence: #3757 (Linux), #3759 (Windows).

**#3740 itself is still OPEN.** Its title — *"867 issues cannot leave `dispatch:ready` — nothing advances dispatch state"* — is fixed: the loop closes and is proven on both platforms. But 525 issues still *sit* at `dispatch:ready`; they can now advance and have not. Closing it is a judgement call, deliberately left to the owner.

---

## 2. What the epic actually delivered

**The record is the state; the label is a projection of it.** A failed API call after work finishes destroys the completion; a label carries no evidence of when, which host, or what exit code; and two writers race.

**Claiming is an explicit protocol, not a property of the storage.** Git offers no cross-machine compare-and-swap — only a push that may be *rejected*, which is a retry signal, not a lock. So: create-only write → commit → push → **re-read from the remote** → only then execute. An accepted push proves the *write* landed, not that *our* claim survived.

**The measurement cannot be gamed by creating vocabulary.** `chain.py` distinguishes three states: label missing, label present but never exercised, and label present and proven. Delete the pilot records and the UNPROVEN warnings return. Silence is evidence-backed, not definitional.

---

## 3. The one thing worth carrying forward

Nearly every defect this session shared one shape: **a check whose name describes a property it does not discriminate.**

- A `Finding` kind absent from the declared table was counted and never printed — 56 tests green with a whole class invisible.
- Deleting the runner's entire heartbeat beater left 67/67 green; the test asserted a beat *exists*, and the runner beats once before and once after the payload regardless.
- A pre-existing test asserted `vocabulary == "present"` for an unexercised stage — the silent-green was already *tested and approved*, so adding the honest third state broke it.
- `client_infrastructure: []` sat empty since v2.0, so the PII gate passed every PR for months. **An empty rule list and a satisfied one produce the same green tick.**
- Every `failure_category` assertion compared against the module's own constant; setting it to `None` — or `"ok"` — left all 39 tests passing.
- `default_host()` guarded against a hostname *literal* in source while publishing the *runtime* one into a committed record. A guard can be thoughtfully written, correctly implemented, and aimed at the adjacent threat.

**Working rule: before trusting a guard, break it and confirm something fails.** Every one of these was found by mutation, never by the suite passing.

**Corollary, learned the hard way:** two defects were invisible to 490 hermetic tests because *on the box where the tests run, the OS hostname and the role id are the same string*. A defect cannot manifest where it is tested. That is the argument for the pilot drain existing at all.

---

## 4. Operational facts that cost time to learn

- **The pre-push hook hangs**, not git and not the filesystem. Two pushes timed out at 2 and 7 minutes; `--no-verify` on a feature branch returned instantly. Permitted on feature branches; never on the default branch.
- **Auto-sync wins push races constantly.** `[remote rejected]` was almost never a real failure this session — always verify with `git cat-file` or `ls-remote`, never trust the exit code either way.
- **Squash-merge rewrites SHAs**, so `git branch -d` refuses a genuinely-merged branch. `-D` is correct *only* after proving content landed by `cat-file`.
- **Backticks in `git commit -m` are command substitution.** Two commit messages lost words this way. Write the message to a file and use `-F`.
- **The PII gate scans commit messages and PR bodies**, not just files, and it scans **whole files** appearing in a diff — not just changed lines. Editing a mirror drags its entire contents into every diff-scanning check.
- **Do not hand-edit a mirror whose source you have fixed.** The kanban boards regenerate from GitHub every 20 minutes; editing them buys nothing and costs a gate failure.

---

## 5. Open items, none started

| item | notes |
|---|---|
| **#3755** | client identifiers across ≥83 files. Needs `redact-client-pii.py` with the private map (a CI secret). Do **not** guess — that is how PR #3149 and this session's own 39 corruptions happened. |
| **#3739** | still open; `run.sh`'s header cites the rule file it introduces, so that citation dangles until it merges. |
| **#3740** | see §1 — close or keep, owner's call. |
| 9 runtime host-detection files | still compare the real OS name to a literal. A **migration**, not a rename: one fallback would write the value into *published* evidence, others hard-fail. Target mechanism exists (#3571) and is provisioned on the licensed host; the second Windows box is down. |
| licensed host `.venv` | broken (`No pyvenv.cfg`); bypassed with `--no-project`, deliberately not repaired. Worth an issue. |
| naming split | the registry keys that host `ace-win-1`; the routing label is `machine:licensed-win-1`. Worth reconciling. |
| stale branches | a large `chore/*` backlog, several with worktrees attached — what `.claude/rules/merge-cleanup.md` was written for. |
| `result` / `published` | still **not measured** by design. They need the licensed-run queue join and the website; reporting `0` would let an unbuilt join read as "nothing shipped". |

---

## 6. Entry prompt for the next session

Paste this verbatim.

```
Read docs/session-handoffs/2026-08-02-dispatch-epic-complete-entry-prompt.md first,
then the prior handoff it links.

Context: dispatch epic #3740 is complete and merged — the loop closes on both
Linux and Windows with durable records behind it (496 tests). Nothing of mine is
outstanding; main is clean.

Before proposing work, verify current state rather than trusting this document:

    git fetch origin main && git log --oneline origin/main -3
    uv run --with pyyaml --with pytest pytest tests/dispatch/ -q
    uv run --with pyyaml python scripts/dispatch/chain.py \
        --repo vamseeachanta/workspace-hub --records .claude/dispatch/records

The chain report should show `executed` counted and no BREAK/UNPROVEN. If a stage
reads "LABEL EXISTS, NEVER USED", something regressed — that state means the label
exists and nothing has ever entered it.

Then pick ONE of the open items in §5 and propose it before starting. Highest
value first, in my view:

1. #3755 — client identifiers in ≥83 files. Needs the private map; it is a real
   pre-existing exposure. Do not attempt redaction without the map.
2. The 9 runtime host-detection files — a coordinated migration to the identity
   mechanism, not a rename. Blocked on the second Windows box being up.
3. Drain something real. The loop is proven but has moved exactly two synthetic
   pilots; 525 issues sit at dispatch:ready. Draining a genuine backlog item is
   the next honest test — and would surface whatever the pilots could not.

Working rules that earned their place this session:
- Before trusting a guard, break it and confirm a test fails. Every real defect
  here was found by mutation, never by the suite passing.
- A defect cannot manifest where it is tested. Two bugs survived 490 hermetic
  tests because the test host's OS name equals its role id.
- Verify pushes by content (`git cat-file` / `ls-remote`), never by exit code.
  Auto-sync wins races constantly and `[remote rejected]` is usually not a failure.
- Write commit messages to a file and use `-F`. Backticks in `-m` are command
  substitution and have silently eaten words twice.
- Never hand-edit a generated mirror whose source you have already fixed.
```

---

## 7. No external actions beyond these

Created and closed pilot issues #3757 and #3759; filed #3755; opened and merged PRs #3741, #3758, #3760; created three `dispatch:` labels and deleted one orphan `wip:` label; retitled 15 issue titles and swept bodies/comments (prior handoff §6); fast-forwarded `main` on the licensed Windows host and removed only the throwaway branch created there — its broken `.venv`, 8 modified state files and 1 stash were left untouched.

No force-push. Nothing merged from a non-`CLEAN` state except PR #3741, under an explicit owner override recorded at the time.
