`★ Insight ─────────────────────────────────────`
Two of the defects below trace directly to must-fire rules in this operator's own contract rather than generic review heuristics: the untracked-file gap echoes a documented incident (`feedback_untracked_is_transient_commit_plans_immediately` — auto-sync deleted a reviewed plan's evidence because it was untracked), and the deckhand#582 gap is the exact scenario the **Discovery-first on stale `plan-approved`** rule exists to prevent. Adversarial review earns its keep by checking a plan against the reviewer's *own* prior failure modes, not just internal consistency.
`─────────────────────────────────────────────────`

## Verdict: **MAJOR**

Not APPROVE. Three defects tie directly to this operator's hard gates and one documented incident class; none are hypothetical.

---

## Precise defects

**1. MAJOR — 4 untracked files on the Deckhand feature branch have no protection clause**
Evidence 4: branch `5cc919f` is "one ahead 41 behind upstream, **4 untracked files**." Plan §A only protects "existing benchmark edits and the agent's local-only commit" — the one *ahead* commit, not the untracked files. This org has a standing incident (`feedback_untracked_is_transient_commit_plans_immediately`) where auto-sync deleted untracked, reviewed-and-approved artifacts because nothing named them as preserve-on-touch. §A's "isolated producer checkout" language addresses *where new work happens*, not whether the 4 untracked files on the existing checkout survive any sync/reset touching that host during Phase A discovery. **Fix:** name the untracked files (or a hash manifest of them) explicitly in the preserve/backup step, and add an acceptance test that they still exist byte-identical after Phase A completes.

**2. MAJOR — deckhand#582 staleness inspection is dropped between evidence and §C**
Evidence 5 explicitly flags: "[deckhand#]582 dispatch plan-approved but inspect stale implementation before work." That is a direct instance of this operator's own **Discovery-first on stale `plan-approved`** must-fire rule. Plan §C ("Dispatch and arbitration — Deckhand") goes straight into envelope/schema/hash-binding design without any step that inventories #582's current implementation against what was plan-approved. If #582's implementation already covers part of the envelope-binding work described in §C, building it again is wasted motion; if it diverges from what was approved, building atop it silently inherits the divergence. **Fix:** insert an explicit discovery step at the top of §C — read #582's current code state, diff against its approved plan, and report drift — before any envelope/schema work begins.

**3. MAJOR — PR2081 has zero GH reviews and self-merge is prohibited, but nothing in the plan gates dependent work on it clearing review**
Evidence 1: PR2081 is OPEN DRAFT, 30 checks green, **no GH reviews**, "own-PR self-merge prohibited by repo memory." digitalmodel §B and workspace-hub §D both build directly on files this PR touches (`orcaflex_run_batch.py`, `orcaflex_parallel_analysis.py`, `run_contract.py` per the Artifact Map). The plan's Acceptance section requires "T3 adversarial review and legal scan" for *this plan's* code stage but never states that PR2081 — the foundation §B/§D build on — must independently pass adversarial review and be merged by a non-self actor first. Without that gate, §B work can start against code that later gets rejected or substantially revised in review. **Fix:** add PR2081 review-and-merge (by an actor other than the authoring agent) as an explicit precondition to starting §B implementation, not just an assumption.

**4. MINOR — issue citations outside the attested evidence bundle are unverifiable from here**
Resource Intelligence cites digitalmodel [#1554](https://github.com/vamseeachanta/digitalmodel/issues/1554), [#1564](https://github.com/vamseeachanta/digitalmodel/issues/1564), [#2051](https://github.com/vamseeachanta/digitalmodel/issues/2051), and Deckhand [#572](https://github.com/vamseeachanta/deckhand/issues/572). None appear in the attested evidence block (which confirms 588, 1943, 550, 568, 569, 570, 581, 582, 564, 543 only). I have no tool access to confirm these exist or carry the scope claimed. Not necessarily wrong — but unattested claims should not silently graduate into an approved plan's dependency list. **Fix:** attest these four via the same evidence-capture pass used for the rest, or mark them "operator-asserted, unverified in this review cycle" in the plan.

**5. MINOR — `max_wall_seconds` named as missing in evidence but not bound to a test**
Evidence 3: current policy "lacks `host_aliases`, `solver_root`, `max_wall_seconds`." §A and the TDD table bind `host_aliases` and `solver_root` to an explicit preflight-fail test; `max_wall_seconds` is only implicitly covered by the general "bounded timeout" language and the timeout/cancellation test row. **Fix:** add `max_wall_seconds` to the same preflight-fail test row as the other two missing policy fields, or state explicitly why timeout enforcement doesn't need a policy-field precondition test.

**6. MINOR — acceptance-bar wording risks the smoke/batch conflation §C explicitly warns against**
§C states "a generic operational smoke will not satisfy the signed-riser canary" — good, scoped correctly. But the top-level Acceptance section's completion bar says "successful native local and primary-Linux remote runs" without repeating that qualifier. As written, a smoke-only pass could be argued to satisfy that clause. **Fix:** qualify as "successful native local and primary-Linux remote **batch execution-contract** runs (§6 criteria), not smoke-only."

**7. Verification checklist item (not a defect) — cited artifacts outside the evidence bundle**
`docs/reports/2026-09-09-orcaflex-execution-evidence.md` and `docs/reports/2026-09-09-orcaflex-fea-strategy.html` are referenced as backing but weren't part of what I was given to review. Confirm they exist and match before treating the plan as fully evidenced.

---

## Proposed next-stage checklist (future tense, minimal)

1. The operator will hash and back up the 4 untracked files on Deckhand branch `5cc919f` before any sync/checkout touches that host. **Accept:** manifest of file paths + SHA256 recorded privately; files verified byte-identical post-Phase-A.
2. The operator will diff deckhand#582's current implementation against its approved plan and record drift, before §C envelope work starts. **Accept:** written drift report (even if "no drift") exists prior to first §C commit.
3. PR2081 will receive adversarial review from an actor other than its author and be merged before §B/§D digitalmodel work begins. **Accept:** PR2081 merged, review artifact linked in this plan.
4. The four unattested issue numbers (digitalmodel #1554/#1564/#2051, deckhand #572) will be confirmed to exist and to carry the scope claimed, or removed/re-marked. **Accept:** each either linked with a live-fetch confirmation or struck from Resource Intelligence.
5. `max_wall_seconds` will be added to the same preflight-fail test as `host_aliases`/`solver_root`. **Accept:** TDD table row updated; test exists (RED before implementation).
6. Acceptance-bar wording will be tightened to explicitly require §6-criteria batch runs, not smoke-only, for completion. **Accept:** revised sentence in Acceptance and approval boundaries.

---

## Can proceed now vs. needs owner decision

**Can proceed now (read-only / isolated, no scope decision required):**
- §A operator inventory (tasks, PID, pending jobs, local overrides, revisions, aliases, env deps) — read-only.
- Untracked-file backup/hashing (defect #1 fix) — protective, non-destructive.
- deckhand#582 drift inspection (defect #2 fix) — read-only discovery.
- Requesting adversarial review on PR2081 (defect #3 fix) — review dispatch, not a merge.
- §D live private machine registry enumeration / reachability measurement — read-only.
- TDD RED-test authoring in an isolated branch/worktree (not touching the live running task).

**Needs owner decision before proceeding:**
- Neutral private scope (repository/owner/access/pinned revision) — evidence 6 says explicitly unresolved and must be recorded before live enqueue.
- Task cutover from the current Running/Password-context task to a new pinned deployment — evidence 7: "task cutover decision cannot be inferred."
- policy.yml change to allow smoke/batch workflows (currently strengthpost/OrcaWave/AQWA only) — security-relevant allowlist expansion.
- First live-lane dispatch of the smoke test (deckhand#588 confirms this has "explicitly never been done") — first-of-kind live action.
- PR2081 merge itself (someone other than the authoring agent must merge; not a Claude action).

No self-approval, no merge, no live dispatch performed or recommended as executed in this review — all of the above are named as pending, not initiated.
