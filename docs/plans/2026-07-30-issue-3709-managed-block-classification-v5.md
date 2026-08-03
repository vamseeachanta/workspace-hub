# Plan for #3709 (v5): Managed-Block Classification Before Cron Cutover

> **Status:** plan-review
> **Complexity:** T3
> **Date:** 2026-07-30
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3709
> **Client:** N/A
> **Lane:** lane:claude
> **Supersedes:** `docs/plans/2026-07-30-issue-3709-managed-block-classification-v4.md` on
> `plan/3709-managed-block-classification-v4` (independent Codex r2 verdict **MAJOR**: 1 major —
> a seventh accepted-and-destructive evasion, `z07_r01_intent_blocking_cleared`)
> **Blocking dependency:** [#3711](https://github.com/vamseeachanta/workspace-hub/issues/3711) must
> land before commit 2. Unchanged since v3. #3711 is now `status:plan-review` (it was `needs-plan`
> when v4 was written). This plan does not attempt to remove the dependency.
> **Review artifacts:** `scripts/review/results/2026-07-30-plan-3709-v4-codex-r2.md` (the review this
> revision answers); `scripts/review/results/2026-07-30-plan-3709-v5-verification-log.md` (author
> verification log, not a review); independent r2 adversarial review REQUIRED before any approval
> **Executable prototype:** `scripts/review/prototypes/3709-v5/` — every number in this document is
> produced by `run.py` and `behaviour.py` in that directory. `3709-v4/` is retained unmodified so a
> reviewer can diff the two.
> **Owner-approval items raised, not taken:** (1) a `.claude/rules/scheduler-mutation-safety.md`
> amendment (FIX 2); (2) adding a `required_status_checks` rule to the `protect-main` ruleset
> (D10 §R2). Neither is performed by this plan or by any agent.

---

## Tense convention

Every statement about **work this plan proposes** is written in future tense. `Evidence` and
`Today's status` columns are **measurements**, written as measurements with the command that produced
them.

Measurements new in v5 were produced on **macOS** and re-produced on **`ace-linux-1`**
(`dev-primary`, `/mnt/local-analysis/workspace-hub`, HEAD `05da65cc6` = `origin/main`, Python 3.12.3)
on 2026-07-30. The prototype's two outputs are **byte-identical across the two hosts**
(`run.py` → `90d9c4f10f7af955084eed83a719b5b6119eeee1ab68375169e6fe33179a0b23`,
`behaviour.py --check` → `d5368d2c4826d0da7fb564ef30642aca52aa50e12a8c86ed81a5fdc1dee61620`).
Measurements carried forward from v3/v4 keep their original provenance.

Note that v4 measured against `3fe934da9`; `origin/main` has since advanced to `05da65cc6`. Every
carried-forward gate has been re-measured at the newer HEAD and is reported below.

---

## Why v5 exists, and what kind of change it is

v5 is **not** another predicate round. Five rounds of AST-predicate hardening have produced
**thirteen** distinct evasions of a static attestation, and this revision adds a fourteenth. Round
five's was found by the harness that v4 itself committed:

```
z07_r01_intent_blocking_cleared   19 predicates: PASS   behaviour.py: DROPS 4/5 LIVE LINES
```

The pattern is now unambiguous and it is structural, not a matter of insufficient care:

- The **AST predicates detect by shape**. A shape predicate must *anticipate* the attack. Each round
  anticipates the previous round's attack and is defeated by the next one. Thirteen data points.
- The **behavioural harness detects by outcome**. It needs no advance knowledge of the shape. It
  found z07 in the same run in which the predicates certified it.

The owner has decided the control model must be restructured: **the behavioural harness becomes the
primary control, and the AST predicates are demoted to defence-in-depth.** This document specifies
that restructure (D10), answers the v4 review's MAJOR finding under the new model (FIX 1), settles
the governance consequence (FIX 2), right-sizes the demoted predicate set on measured evidence
(FIX 3), and resolves the #3518 collision (FIX 4).

---

## Scope of this revision — what carries forward untouched

The following are confirmed-good and are **not relitigated**:

| Carried forward | Provenance |
|---|---|
| v4's E13 finding: a managed line reported class `ignore` is always dropped by the rebuild; predicate 19 is directionally correct | v4 review §3, independently confirmed |
| v3 residue **R2 closed** (`_abort` reporting `abort_reason=None`; a 5-of-5 data-loss path v3 accepted) | v4 review §4 |
| **Fix B** — amend sanitisation rule 4, do **not** rebaseline the fixtures; rebaselining destroys the ace1 fixture's byte-equality | v4 review §7 |
| The committed-prototype practice | v4 FIX C, v4 review §1 |
| Third-party-first ordering; retained dead `catalog_commands` / `external_fingerprints` params; `build_classification_context` as the single seam | v2, re-confirmed twice |
| `scheduler_mutation_contract.py` at exactly **400** lines, with no new `ATT_SOURCES` entry | re-measured at `05da65cc6`: 400 |
| The ace1 fixture is byte-equal to live `crontab -l` | **re-verified today**: `ssh ace1 'crontab -l' \| sha256sum` → `45cc7dc366ff5ecb61525323fc0f2afda668782aaf323f819ae70cf67c8a9551`, identical to the committed fixture, 73 lines |
| #3711 blocking commits 2-4 | unchanged |
| **The v3 rejection of a behavioural *attestation*** | see D10 §"The critical distinction" — this rejection stands and v5 depends on it |

v3 design sections D1-D4 and D6-D8 remain adopted verbatim. v5 adds **D10** (the control-model
restructure), replaces **D5** with a right-sized secondary predicate set (FIX 3), and republishes the
TDD rows that change.

---

## D10 — the control model

### The critical distinction: this is not the behavioural attestation v3 rejected

v3 rejected making `python-postwrite-preservation-multiset-v1` **behavioural**, and that rejection is
correct and must be preserved. The reason is mechanical, not stylistic:
`check-scheduler-mutation-surfaces.py` builds its `records` dictionary from **git-index blobs**
(`check-scheduler-mutation-surfaces.py:115`, `records[path] = blob`, populated from `git ls-files -z`
plus `git cat-file --batch`). An attestation that *executed* those records would execute **staged,
unreviewed code inside the enforcement gate** — a new arbitrary-code-execution surface in exactly the
component whose job is to be trustworthy. That is not what v5 proposes.

| | v3's rejected behavioural **attestation** | v5's behavioural **test** |
|---|---|---|
| What runs | the **staged git-index blob** | the **committed module**, imported normally |
| Who runs it | `check-scheduler-mutation-surfaces.py`, inside the enforcement gate | `pytest`, in CI and locally |
| New code-execution surface in the gate | **yes** — this is why v3 rejected it | **none** — the gate still only parses |
| Trust boundary | executes content that has not yet been reviewed or merged | executes content that is already in the tree under review |
| Failure mode if the executed code is hostile | the gate is compromised | a test process is compromised, exactly as for any other test in the repo |

v5's enforcement-side change is **parse-only** in both directions. The checker gains the ability to
*read* one more indexed blob and assert its shape; it never executes anything.

### R1 — Primary control: a required behavioural preservation test

**Artifact:** `tests/cron/test_cutover_preservation.py` (new).

It imports the **committed** `scripts/cron/cron_transaction.plan_cutover` and asserts one invariant
over a scenario corpus:

> **The preservation invariant.** For every scenario, the returned plan either **fails closed**
> (`abort_reason` is non-null **and** `new_text` is `None`), or its `new_text` reproduces **every live
> input line with at least the multiplicity the input carried it**.

Three properties of that invariant are load-bearing:

1. **It is stated over outcomes, not shapes.** It has no knowledge of `intent`, `_abort`, callee
   allowlists, or any other internal. A novel evasion therefore requires **no new predicate** to be
   caught — which is the entire point of the restructure.
2. **It is a multiset comparison, not a membership test.** v4's harness used membership; §FIX 1b
   below exhibits a fourteenth evasion (`z10_new_text_dedupes`) that all nineteen v4 predicates
   accept **and** v4's own harness scores "SUCCEEDS, no loss", because it destroys one of two
   identical live occurrences. The ace1 fixture has two such duplicate pairs, so this is a live
   property of the target host, not a hypothetical.
3. **An abort must be a real abort.** `abort_reason` non-null *with* a non-null `new_text` is scored
   as a failure, closing the "report an abort and write anyway" shape.

**Scenario corpus** (each scenario is a crontab text; the honest shape's required outcome is fixed):

| Scenario | Content | Honest outcome |
|---|---|---|
| A | uncataloged orphan inside the managed block | **ABORT** (this is #3709's defect, reproduced) |
| B | clean crontab, nothing uncataloged | **SUCCEED, no loss** |
| C | a **cataloged** line duplicated across `managed` and `after` | **ABORT** (the rebuild can only emit one copy) |
| D | a **preserved_external** line duplicated across `before` and `after` | **SUCCEED, no loss** (the rebuild retains both) |
| ace1 | `tests/cron/fixtures/ace1-crontab-2026-07-30.txt`, 73 lines, byte-equal to live | **ABORT** — 47 managed uncataloged |
| ace2 | `tests/cron/fixtures/ace2-crontab-2026-07-30.txt`, 40 lines | **ABORT** — 11 uncataloged |

C and D exist because of the ace1 fixture's recorded duplicates (`notification-purge` at
`(managed,31)` and `(after,7)`; `deckhand-api-presence-sync` at `(after,1)` and `(after,8)`). They
are the scenarios that give the multiset form its teeth.

**Why the corpus needs a second layer.** A single invariant asserted over six scenarios could be
vacuous — an invariant that always returns `True` would pass. So the suite also carries a
**mutation test of the invariant itself**: the 23 committed shape files move from the prototype's
`cases/` to `tests/cron/fixtures/preservation_shapes/`, and one test executes each of them through
the same invariant and asserts its **recorded four-scenario verdict tuple**. If the invariant is ever
weakened, 17 of the 23 shapes stop reading as destructive and the test goes red.

**Safety boundary of that second layer.** The shape files are committed, reviewed, import nothing,
perform no I/O, and are executed against stub collaborators supplied by the harness — never against a
real crontab, never by the enforcement checker. A guard assertion in the same suite will require every
shape file to contain no `import` outside the pinned allowlist (`collections`, `cron_line_model`,
`cron_parse`, `cron_render`) and no call to `open`, `subprocess`, `os`, or `eval`, so a hostile
fixture cannot be smuggled in behind a plausible name.

### R2 — How the primary control is made required

Three layers, because the first two are not sufficient and one of them is not an agent action.

**Layer 1 — a CI job that always runs.** A new job `cron-cutover-preservation` will be added to
`.github/workflows/enforcement-gate.yml`. That workflow is chosen deliberately: it fires on every
`pull_request` to `main` with **no `paths:` filter**, so unlike the `skills-validation.yml` pattern
there is no path-based skip hole. The job will run
`uv run pytest tests/cron/test_cutover_preservation.py -q`.

**Layer 2 — the required-check rule. This is an owner action and it is not currently in place.**

> **Measured today.** `gh api repos/vamseeachanta/workspace-hub/rulesets/17369764 --jq '.rules[].type'`
> returns exactly `deletion` and `non_fast_forward`. There is **no** `required_status_checks` rule.
> `gh api repos/vamseeachanta/workspace-hub/branches/main/protection` returns **404 Branch not
> protected**. **No CI check is merge-blocking on this repository today — including the existing
> `Scheduler Mutation Surface Guard`.**

This is a pre-existing gap that v4 and its review both assumed away. Making the primary control
genuinely required means adding a `required_status_checks` rule to the `protect-main` ruleset with
contexts `Cron Cutover Preservation` **and** `Scheduler Mutation Surface Guard`. That is a repository
settings change requiring owner authority; this plan raises it and will not perform it. Until it is
done, layer 1 makes the failure **visible** on every PR but not **blocking**, and layer 3 is what
carries the fail-closed weight.

**Layer 3 — a parse-only presence-and-integrity predicate inside the existing attestation.**

A CI job can be deleted; a test can be emptied. Layer 3 closes that, without any new execution
surface and without touching the 400-line contract:

- `python-postwrite-preservation-multiset-v1` gains one further conjunct,
  `behavioural-test-present-and-pinned`.
- It reads `records[b"tests/cron/test_cutover_preservation.py"]` — the checker's dispatch already
  hands the **full** `records` dict to every Python attestation
  (`scheduler_mutation_attestations.evaluate_python(name, records, source)`), and
  `_evaluate_cron_attestation` already uses that capability
  (`derive_cron_classifier_branches(records)`). **No `ATT_SOURCES` entry is added and
  `scheduler_mutation_contract.py` stays at exactly 400 lines.**
- It `ast.parse`s the blob — it does **not** execute it — and asserts: the named test functions
  exist; the P1 test is parametrised over the full scenario list; the invariant helper's body is the
  pinned multiset comparison and not a constant `True`; and the shape-corpus expectation table has
  the pinned number of entries.

Deleting the test, emptying it, or replacing the invariant with something vacuous therefore makes
`check-scheduler-mutation-surfaces.py` exit non-zero, which is the command
`.claude/rules/scheduler-mutation-safety.md` already requires before merging scheduler changes.

### R3 — Secondary control: the AST predicates, explicitly demoted

The predicate set stays in the enforcement checker. Its documented status changes from *the
fail-closed guarantee* to *a cheap, execution-free early signal*:

- **What it still buys.** It fires at `git add` time with no test run, and it rejects **latent**
  shape damage that the scenario corpus cannot yet make destructive — see FIX 3, where two of the
  three shapes that need a *second* fault to destroy data are rejected by a single predicate.
- **What it no longer claims.** It is no longer asserted to be sound with respect to "this
  implementation cannot lose a live line". Fourteen counter-examples say it is not, and the honest
  reading of five rounds is that a shape approximation of a semantic property never will be.
- **What follows for reviewers.** A predicate failing is a hard stop. A predicate *passing* is now
  explicitly **not** evidence of preservation safety; only the primary control is.

---

## FIX 1 (v4-r2 MAJOR) — the z07 evasion, and why no predicate change is proposed

### The finding, reproduced against the committed artifact

`z07_r01_intent_blocking_cleared` starts from the admitted residue `r01_detail_classifier_constant`
and inserts **one statement** between the intent assignment and the pinned blocking guard:

```python
    intent = build_cutover_intent(classified['records'], new_lines, acknowledged)
    intent['blocking'] = []
    if intent['blocking']:
        return _abort('planned crontab would omit live line(s)', [], intent)
```

Committed as `scripts/review/prototypes/3709-v5/cases/z07_r01_intent_blocking_cleared.py`.

**The demoted predicate set accepts it** (`run.py`, exit 0 with z07 declared as residue; the
undeclared-evasion form of the same run prints
`FAIL: z07_r01_intent_blocking_cleared ACCEPTED (undeclared evasion)`):

```
case                                         v4     v3     first failing predicate
z07_r01_intent_blocking_cleared              True   True   -
```

**The primary control catches it, in all four scenarios** (`behaviour.py --check`, byte-identical on
macOS and ace1):

```
case                               v3     v4     A                       B                       C                       D
z07_r01_intent_blocking_cleared    True   True   DROPS 4/5 LIVE LINES    DROPS 4/5 LIVE LINES    DROPS 4/5 LIVE LINES    DROPS 4/5 LIVE LINES
reference                          True   True   ABORTS                  SUCCEEDS, no loss       ABORTS                  SUCCEEDS, no loss
```

### No predicate change is proposed for z07, and why that is now acceptable

v4's reviewer prescribed strengthening D5 so that every path from the intent assignment to the
success return proves the same unmodified `intent["blocking"]` is tested. **This plan declines that
prescription.** The reasons are stated plainly so a reviewer can disagree with them explicitly:

1. **It is the sixth iteration of a strategy with a thirteen-for-thirteen failure record.** Every
   previous round closed the named shape and was defeated by the next. Adding predicate 20 to forbid
   subscript writes to `intent` on success paths closes z07 and says nothing about the next one.
   §FIX 1b below is the demonstration: a fourteenth evasion, constructed while writing this plan,
   which the prescribed z07 fix does not touch.
2. **It is redundant against the control that now carries the guarantee.** z07 is destructive in
   4 of 4 scenarios. The primary control fails on it immediately.
3. **It has a real cost.** "No subscript or attribute write to `intent` on any success path" is
   another transcription of the destructive core into the predicate set, deepening the
   refactor-hostility that v4 already listed as a risk — in exchange for zero measured coverage,
   given the primary control.

Under the restructure the correct disposition of z07 is: **admitted residue of the secondary control,
covered by a named test of the primary control.** It is registered in the prototype's
`ADMITTED_RESIDUE` map against row **P5**, so `run.py` will fail if the predicate set ever starts
rejecting it and the plan silently goes stale.

## FIX 1b (new in v5) — a fourteenth evasion, and why the primary control had to change

While specifying the invariant, one further shape was constructed:
`scripts/review/prototypes/3709-v5/cases/z10_new_text_dedupes.py`. It renders `new_text` from a
de-duplicated copy of `new_lines` while still building the intent report from the **full**
`new_lines`, so `blocking` is empty and the pinned guard is satisfied:

```python
    new_text = '\n'.join(dict.fromkeys(new_lines))
```

Measured:

| Control | Verdict on `z10_new_text_dedupes` |
|---|---|
| v3's seven predicates | `True` |
| v4's nineteen predicates | `True` (predicate 9 asks only that the `new_text` assignment **mention** `new_lines`) |
| **v4's behavioural harness (membership-based)**, scenario D | **`SUCCEEDS, no loss`** — wrong |
| **v5's invariant (multiset)**, scenario D | **`DROPS 1/5 LIVE LINES`** |

This matters more than z07 does, because it is a defect in **the control being promoted**. v4's
harness could not see a duplicate occurrence being destroyed, and the ace1 fixture carries two
duplicate pairs. v5's invariant is a multiset comparison and the corpus gains scenarios C and D
specifically to exercise it. Like z07, z10 is admitted residue of the secondary control, covered by
row **P6**.

The honest summary line for the whole exercise: **fourteen evasions of the shape attestation, of
which the outcome invariant catches fourteen.**

---

## FIX 2 (governance) — the fail-closed clause

### The clause, and what it does and does not say

`.claude/rules/scheduler-mutation-safety.md:8`:

> Unsupported indirection, unknown authority, incomplete operations, or **failed source attestations
> fail closed.**

Read precisely, this is a **necessary** condition — *attestation fails ⇒ block* — and it is **still
satisfied verbatim after demotion.** Demoting the predicate set does not change what happens when it
returns `False`: `derive_status` still yields a non-compliant status, the checker still exits
non-zero, and no cutover proceeds. The retained predicates continue to fail closed exactly as before.

What the clause does **not** say is that a *passing* attestation is sufficient. The v4 review called
Finding 1 a violation of this clause; strictly it is not a violation of the clause as written, it is
an **unstated sufficiency assumption** that the rule never carried and that fourteen counter-examples
have now refuted. The rule is silent about the property that actually matters, which is why the plan
proposes to say it.

### What "fails closed" means for a failed behavioural **test**, honestly

| Layer | What a failure blocks | Strength today |
|---|---|---|
| CI job `cron-cutover-preservation` | **merge**, once the ruleset carries the required check | **visible but not blocking today** — the `protect-main` ruleset has no `required_status_checks` rule (measured above) |
| `behavioural-test-present-and-pinned` conjunct | the **enforcement gate** — deleting or neutering the test makes `check-scheduler-mutation-surfaces.py` exit 1 | blocking wherever that command is run, which the rule already mandates before merging |
| The runtime guards inside `plan_cutover` (parse-error abort, uncataloged abort, totality guard, blocking guard) | the **apply** | this is the only apply-time fail-closed, and it is unchanged by this restructure |

The limitation must be stated rather than papered over: **a failing test blocks a merge, not an
apply.** Nothing in the test can stop someone running `cron_apply.py --apply` from an unmerged
working tree. Apply-time safety comes solely from the runtime guards inside the module, which is
precisely why FIX 3 keeps the two predicates that pin those guards structurally.

### Proposed rule amendment — **owner approval required; not taken by this plan**

This plan makes **no edit** to `.claude/rules/`. It proposes the following bullet be added after the
existing fail-closed clause, and flags it as a change requiring owner approval in its own right:

> - A source attestation is a **necessary but not sufficient** control. Every destructive
>   reconstruction path must additionally carry a **behavioural preservation test** that imports the
>   committed module, executes it against committed fixtures, and fails when a live line is lost
>   without an accompanying fail-closed abort. That test runs in CI and locally, **never inside the
>   enforcement checker**; the checker may only verify, without execution, that the test is present
>   and structurally intact. A failed source attestation fails closed as before; a **passed** source
>   attestation is not evidence of preservation safety.

If the owner declines the amendment, the fallback is that the restructure ships with the rule
unchanged and the plan's own acceptance criteria carry the obligation — weaker, because the rule is
what the next plan in this domain will read.

---

## FIX 3 — right-sizing the demoted predicate set

### The measurement the recommendation rests on

Nineteen predicates over seven functions was justified when they were the primary control. The
question now is different: **for each predicate, is there a shape it uniquely rejects that the
primary control would not catch?**

`scripts/review/prototypes/3709-v5/` measures this over 35 shapes (23 case files + 12 textual
mutations), 17 of which are destructive in at least one of the four scenarios:

| # | Predicate | Rejects | Sole rejecter of (`*` = destructive) |
|---|---|---|---|
| 1 | `plan-cutover-order` | 3 | — |
| 2 | `plan-cutover-result-flow` | 2 | M12\* |
| 3 | `render-block-called-once` | 2 | M3 |
| 4 | `classify-populates-records` | 3 | — |
| 5 | `fallback-records-populated` | 2 | — |
| 6 | `rebuild-retention` | 3 | M4, M5 |
| 7 | `intent-derives-blocking` | 1 | — |
| 8 | `plan-cutover-terminal-return-closure` | 2 | e07\* |
| 9 | `plan-cutover-success-path-chain` | 6 | e06\*, M7 |
| 10 | `plan-cutover-binding-closure` | 5 | e01\*, e03\* |
| 11 | `module-binding-integrity` | 2 | e02\* |
| 12 | `abort-fails-closed` | 1 | e04\* |
| 13 | `callee-allowlist-closure` | 2 | — |
| 14 | `record-loop-bodies-exact` | 5 | e05 |
| 15 | `absent-record-is-literal` | 2 | — |
| 16 | `missing-occurrences-shape` | 1 | — |
| 17 | `classification-covers-every-line` | 4 | e10, **z08\***, z09 |
| 18 | `marker-prefixes-are-literal` | 2 | e12\* |
| 19 | `managed-absence-always-blocks` | 2 | e14\* |

Two facts fall out:

1. **Every shape marked `*` is destructive, and the primary control catches all of them.** No
   predicate is load-bearing for safety any more. The only shapes the predicate set accepts *and*
   that are destructive are z07 and z10 — and those are accepted by all nineteen, so no predicate
   is buying safety there either.
2. **Seven predicates — 1, 4, 5, 7, 13, 15, 16 — are the sole rejecter of nothing.** Every shape they
   reject is rejected by at least one other predicate.

### The composition argument for keeping any predicates at all

The tempting conclusion — "the primary control catches everything destructive, so delete the
predicates" — is wrong, and v5 measured why. Two new composed cases were built:

| Case | Construction | Predicates | Primary control |
|---|---|---|---|
| `z08_no_guard_plus_marker_theft` | E10 (totality guard removed) **∘** E11 (parser reports a live line as a marker) | rejected by 17 alone | **DROPS 1/5 (B), 2/5 (D)** |
| `z09_no_guard_plus_mispartition` | E10 **∘** R03 (parser mispartitions) | rejected by 17 alone | non-destructive on this corpus |

Neither component is destructive alone: E10 is safe in all four scenarios, E11 aborts in all four.
**Composed, they destroy live lines.** A reviewer who right-sized purely on "what does the behavioural
corpus flag today" would delete predicate 17 and reopen the route the moment a second, independent
change lands. That is the whole defence-in-depth case, and it is a measurement rather than an appeal
to caution.

### Recommendation: **thirteen predicates — drop 1, 4, 5, 7, 15, 16**

Measured coverage of candidate sets over the 35 shapes:

```
all 19                              accepted=6   accepted&DESTRUCTIVE=[z07, z10]
DROP 1,4,5,7,15,16  (13 kept)       accepted=6   accepted&DESTRUCTIVE=[z07, z10]      <- recommended
DROP 1,2,4,5,7,13,15,16 (11 kept)   accepted=8   accepted&DESTRUCTIVE=[e09*, z07, z10, M12*]
closure + guards only (8 kept)      accepted=15  accepted&DESTRUCTIVE=[e12*, z07, z10, M12*]
guards only 17,18,19 (3 kept)       accepted=28  accepted&DESTRUCTIVE=[13 shapes]
```

**The 13-predicate set has identical coverage to all nineteen**, accepts the same six shapes, and
still accepts the reference. Going to eleven costs `e09_intent_helper_lie` and `M12`, both
destructive — so thirteen is the floor, not an arbitrary trim.

The v4 review's specific caution — "15/16/17 do real work against E09/E10/E11, dropping them reopens
a line-loss route" — is answered rather than ignored. E09 is rejected by **three** predicates
(13, 15, 16); with 15 and 16 dropped, **13 still rejects it**, which is why the 13-set's measured
coverage is unchanged and the 11-set's (which also drops 13) is not. **17 is retained**, and z08 is
the case that proves it must be.

### What each retained predicate buys now

| # | Predicate | What it buys under the restructure |
|---|---|---|
| 2 | `plan-cutover-result-flow` | Sole rejecter of M12 (success return emits the block instead of `new_text`) — a destructive, single-token edit caught before a test runs |
| 3 | `render-block-called-once` | Sole rejecter of M3/M3b; keeps the block a single rendered object so the intent report and the written text cannot diverge |
| 6 | `rebuild-retention` | Sole rejecter of M4/M5; pins the two retention comprehensions, which are the only reason non-cataloged `before`/`after` lines survive at all |
| 8 | `plan-cutover-terminal-return-closure` | Sole rejecter of e07 (a terminal `Call` that is not `_abort`); the anchor of the closure group — without it the delegated-return family (mx2) re-opens |
| 9 | `plan-cutover-success-path-chain` | Widest reach (6 shapes); sole rejecter of e06 and M7; the only predicate that constrains **per-path** rather than per-body order |
| 10 | `plan-cutover-binding-closure` | Sole rejecter of e01 and e03; closes nested-def and in-body rebinding, which are how a pinned name is made to resolve elsewhere |
| 11 | `module-binding-integrity` | Sole rejecter of e02; the module-scope half of the same closure — a rebind here defeats 10 |
| 12 | `abort-fails-closed` | Sole rejecter of e04. Closes v3 residue R2 (a measured 5-of-5 data-loss path). Also the only structural guarantee that an abort really is one |
| 13 | `callee-allowlist-closure` | Retained specifically because it is what still rejects e09 once 15/16 go; makes "a new helper in the safety path" a red test rather than an invisible diff |
| 14 | `record-loop-bodies-exact` | Sole rejecter of e05 (`continue` before the record append). Latent, not destructive today — exactly the class the primary corpus cannot exhibit |
| 17 | `classification-covers-every-line` | Pins a **runtime** fail-closed guard, so it is one of the two predicates that protect **apply-time** safety, not merge-time. Sole rejecter of e10, z08, z09; z08 is the measured composition that makes it non-negotiable |
| 18 | `marker-prefixes-are-literal` | Sole rejecter of e12. Predicate 17's expected set is derived from this constant; a callable or mutable constant defeats 17 silently |
| 19 | `managed-absence-always-blocks` | Sole rejecter of e14. Pins the **other** runtime guard, and it is the direct fix for #3709's own defect reached through the classifier (E13) |

### Dropped, with the reason

| # | Predicate | Why it goes |
|---|---|---|
| 1 | `plan-cutover-order` | Strictly subsumed by 9, which asserts the same ordering per-path rather than per-body |
| 4 | `classify-populates-records` | Sole rejecter of nothing; every shape it rejects is also rejected by 14 or 17 |
| 5 | `fallback-records-populated` | Sole rejecter of nothing; the fallback path is only reachable on a parse error, which 9's chain already forces to abort |
| 7 | `intent-derives-blocking` | Sole rejecter of nothing; subsumed by 19, which pins the same expression with a stronger condition |
| 15 | `absent-record-is-literal` | Sole rejecter of nothing; e09 is still rejected by 13 |
| 16 | `missing-occurrences-shape` | Sole rejecter of nothing; e09 is still rejected by 13. This is the largest single saving (23 lines) |

### Budget consequence — measured

Mechanically stripping the six dropped predicates, their registry rows and the prototype-only v3
comparison scaffolding from the committed prototype:

```
v4 19-predicate prototype : 640 lines
v5 13-predicate projection: 517 lines   (max function span 34, ceiling 50)
```

517 is still above the enforced 400-line ceiling
(`tests/enforcement/test_scheduler_mutation_task3.py:284`), so **v4's two-module split is retained**,
with both modules smaller:

| Module | Contents | Projected |
|---|---|---|
| `scripts/enforcement/scheduler_mutation_preservation.py` | shared helpers, predicates 2/3/6/8/9, `NAMED_PREDICATES`, `NAMED_MUTATIONS`, `ADMITTED_RESIDUE`, `preservation_shape` | ≈ 300 |
| `scripts/enforcement/scheduler_mutation_preservation_closure.py` | predicates 10-14, 17-19, the `behavioural-test-present-and-pinned` conjunct and their local helpers | ≈ 220 |

Import order stays acyclic (`attestations → preservation → preservation_closure → python_flow`), the
prototype's `PRIMITIVE_PATTERNS` scan still measures `direct_primitives=[]`, so neither module needs
`FORENSIC` membership or a `mutation-surfaces.yaml` entry, and `scheduler_mutation_contract.py` stays
at exactly 400 lines with no `ATT_SOURCES` change. v3's pin is retained: if any predicate line ever
matches a `PRIMITIVE_PATTERNS` regex, that module joins `FORENSIC` with the sentinel comment in the
same commit.

---

## FIX 4 — the #3518 collision

### Measured finding: **#3518's implementation is already on `origin/main`**

The v4 review recorded #3518 as `status:plan-approved` **and unimplemented**, colliding with #3709 in
`tests/enforcement/test_scheduler_mutation_task3.py`. That is no longer accurate, and the correction
changes the answer:

| Check | Command | Result |
|---|---|---|
| #3518's named implementation commit is on main | `git merge-base --is-ancestor 1c3d7f683 origin/main` | **yes** — `1c3d7f683 fix(enforcement): attest setup wrapper os gate`, 2026-07-13 |
| Its delivery PR | `gh pr view 3517` | **MERGED** 2026-07-14 |
| Its plan's key acceptance criterion — the pin equals the staged blob | `git cat-file blob :scripts/cron/setup-cron.sh \| sha256sum` vs `WRAPPER_SHA256[SETUP]` | both `1a5e5573d00d17c4a820a831549fb92a2dad100b5fbab5572afcefadd57c84c1` — **satisfied** |
| Its named tests exist on main | `grep -n test_setup_self_pinned_baseline_accepts_registry_os_gate tests/enforcement/test_scheduler_mutation_task3.py` | line 361; `test_setup_wrapper_pin_matches_exact_staged_blob` at line 501 |
| The shared suite is green | `[ace1] uv run pytest tests/enforcement/test_scheduler_mutation_task3.py -q` | **89 passed** |
| The enforcement gate is green | `[ace1] uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py` | exit 0 |

The issue is still `OPEN` at `status:plan-approved` because it carries `gate:completeness`, and the
completeness record has not been produced and owner-verified — not because work remains.

The `origin/plan/3518-scheduler-wrapper-attestation` branch is stale by ~1,600 files against current
`main` and should not be used to judge #3518's state.

### Landing order

1. **#3518 first — as a closeout, not an implementation.** No code needs to land. The owner path is
   the completeness gate: produce the record, apply `status:completeness-verified`, close. Nothing in
   #3709 depends on that closeout, and nothing in it touches `test_scheduler_mutation_task3.py`.
2. **#3711 next** — unchanged hard blocking prerequisite for #3709 commits 2-4; currently
   `status:plan-review`.
3. **#3709 last.** With #3518 landed, #3709 is the **sole future writer** of
   `test_scheduler_mutation_task3.py`, and the collision the v4 review projected does not occur.

**What the second lander must rework, if #3518 is nonetheless re-implemented from its stale plan
branch** (the residual risk, because `status:plan-approved` invites a batch agent to pick it up):

- It must **rebase onto current `main`, not merge its plan branch.** The branch predates ~1,600 files
  of divergence; merging it would revert unrelated work.
- It must not re-apply the pin refresh — `WRAPPER_SHA256[SETUP]` already equals the staged blob;
  re-applying a stale constant would make `test_setup_wrapper_pin_matches_exact_staged_blob` red.
- If it lands after #3709 commit 1, it must merge (not overwrite) the #3709 rows added to
  `test_scheduler_mutation_task3.py` and re-run the full task-3 suite plus
  `check-scheduler-mutation-surfaces.py`.
- Either way, #3709's future dispatch change in `scheduler_mutation_attestations.py` must preserve
  the existing wrapper-attestation dispatch, which `check-scheduler-mutation-surfaces.py:55-59`
  imports separately as `evaluate_wrapper_attestation`.

**Recommended action on #3518 now:** post the correction on the issue (the collision notice comment
of 2026-07-30 is based on the stale reading) and route it to the completeness/close path. This plan
does not change #3518's labels.

---

## Artifact Map — delta from v4

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-30-issue-3709-managed-block-classification-v5.md` |
| Author verification log | `scripts/review/results/2026-07-30-plan-3709-v5-verification-log.md` |
| Superseded v4 plan | `docs/plans/2026-07-30-issue-3709-managed-block-classification-v4.md` |
| Independent r2 review being answered | `scripts/review/results/2026-07-30-plan-3709-v4-codex-r2.md` |
| Independent plan review (r2, required) | `scripts/review/results/2026-07-30-plan-3709-v5-<provider>-r2.md` |
| **Executable prototype (v5)** | `scripts/review/prototypes/3709-v5/` (23 cases, `run.py`, `behaviour.py`, `mutations.py`, `make_cases.py`, `preservation_prototype.py`) |
| v4 prototype, retained for diffing | `scripts/review/prototypes/3709-v4/` |
| **Primary control** | `tests/cron/test_cutover_preservation.py` (new) |
| **Primary control fixtures** | `tests/cron/fixtures/preservation_shapes/` (new; the 23 shape files) |
| **Primary control CI job** | `.github/workflows/enforcement-gate.yml` job `cron-cutover-preservation` |
| Secondary control | `scripts/enforcement/scheduler_mutation_preservation.py` (≈300), `…_preservation_closure.py` (≈220) |

---

## Files to Change — delta from v4

| Action | Path | Change from v4 |
|---|---|---|
| Create **[v5]** | `tests/cron/test_cutover_preservation.py` | **The primary control.** Rows P1-P8 |
| Create **[v5]** | `tests/cron/fixtures/preservation_shapes/` | 23 shape files migrated from the prototype's `cases/`, plus the pinned expectation table |
| Modify **[v5]** | `.github/workflows/enforcement-gate.yml` | New job `cron-cutover-preservation`; chosen because this workflow has no `paths:` filter |
| Modify **[v5]** | `scripts/enforcement/scheduler_mutation_preservation.py` | 13 predicates, not 19; hosts 2/3/6/8/9 + registries; ≈300 lines |
| Modify **[v5]** | `scripts/enforcement/scheduler_mutation_preservation_closure.py` | Predicates 10-14, 17-19 + `behavioural-test-present-and-pinned`; ≈220 lines |
| Modify **[v5]** | `scripts/cron/cron_transaction.py` | v4's changes stand (`MARKER_PREFIXES`, totality guard, location-aware `blocking`); `_missing_occurrences` is **still extracted** — predicate 16 is dropped but the helper remains, because the intent report's multiset accounting is what makes duplicates visible |
| Modify **[v5]** | `tests/enforcement/test_scheduler_mutation_task3.py` | Secondary-control rows only: `NAMED_PREDICATES == 13`, `NAMED_MUTATIONS == 26`, `ADMITTED_RESIDUE == 6`, both module sizes |
| Delete **[v5]** | `scripts/review/prototypes/3709-v4/`, `scripts/review/prototypes/3709-v5/` | Both removed in commit 4 |
| Not changed | `scheduler_mutation_contract.py` (400 lines, no `ATT_SOURCES` entry), `python_flow.py`, `FORENSIC`, `mutation-surfaces.yaml`, `setup-cron.sh`, `scheduler_mutation_wrapper_attestations.py` | The layer-3 conjunct reads `records` directly, so no contract change is needed |

Every other row of v3/v4's Files-to-Change table carries forward unchanged.

---

## TDD Test List

### Baseline: `main` is **not** green on ace1 — the criterion is "no new failures"

Re-measured on ace1 at `05da65cc6` (2026-07-30):

| Suite | Result | Pre-existing failures |
|---|---|---|
| `tests/enforcement` | **2 failed, 417 passed** (396 s) | `test_check_skill_index_coherence.py::test_real_repo_passes`, `test_soul_auto_load.py::test_drift_script_returns_zero_in_clean_state` |
| `tests/cron` | **284 passed, 0 failed** | none |
| `tests/enforcement/test_scheduler_mutation_task3.py` | **89 passed** | none |
| `scripts/cron/tests/test_validate_schedule.py` | **1 failed, 53 passed** | `test_windows_tasks_have_windows_scheduler` |

Two corrections to the brief's stated baseline, both measured: `tests/cron/test_cron_runtime.py`
**passes** today (it is inside the fully green `tests/cron` run), and `test_validate_schedule.py`
lives under `scripts/cron/tests/`, not `tests/`, so it is outside both suites above.

**Acceptance is therefore "no new failures", not "suites pass":** `tests/enforcement` must end at
exactly the same 2 named failures, `tests/cron` must stay at 0, and
`scripts/cron/tests/test_validate_schedule.py` must stay at exactly 1 named failure.

### Primary-control rows (the load-bearing ones)

| # | Test name | File | What it will verify | Expected | Today's status on `main` + proving command |
|---|---|---|---|---|---|
| **P1** | `test_plan_cutover_never_loses_a_live_line_without_aborting` | `tests/cron/test_cutover_preservation.py` | The invariant, parametrised over all six scenarios (A, B, C, D, ace1, ace2), against the committed `plan_cutover`. | 6 passes | **RED.** `[ace1] uv run python -c "import ast,sys; src=open('scripts/cron/cron_transaction.py').read(); print('plan_cutover' in src, 'intent' in src)"` → `plan_cutover` exists but has **no `intent` key at all** and no records model; on the ace1 fixture it plans over `before`+`after` only, which **is** #3709. |
| **P2** | `test_preservation_invariant_discriminates_over_the_shape_corpus` | same | Executes all 23 committed shape files and asserts each one's pinned four-scenario verdict tuple, so the invariant cannot be weakened into vacuity. | 23 tuples match; 17 read destructive | **RED.** `[mac+ace1]` the fixture directory does not exist on `main`. Against the committed prototype: `behaviour.py --check` exits 0 with the table reproduced byte-identically on both hosts (`d5368d2c…`). |
| **P3** | `test_absent_managed_line_blocks_even_when_classified_ignore` | same | **E13/E14 residue.** A managed-block line the new block does not reproduce blocks even when `classify_line_detail` returns `ignore`. | `intent['blocking']` holds it; `abort_reason` non-null | **RED.** `[ace1]` no `intent` key exists on `main`. Prototype: `e14_ignore_exempts_managed` drops 1/5 in scenario A without the rule; `e13_managed_line_reported_ignore` aborts in A with it. |
| **P4** | `test_classification_that_misses_a_live_line_fails_closed` | same | **E10/E11/R03 residue.** A parse not accounting for every line of `current_text` returns `error` and aborts. Includes the **composed** `z08` shape. | `abort_reason` names the coverage failure | **RED.** `[ace1]` `classify_crontab_lines` does not exist on `main`. Prototype: `z08_no_guard_plus_marker_theft` drops 1/5 (B) and 2/5 (D) without the guard. |
| **P5** | `test_intent_blocking_cannot_be_emptied_before_the_guard` | same | **The z07 residue, by outcome.** Asserts the committed module on scenario A both blocks and refuses to emit `new_text`. Named after the evasion so a future z07-shaped edit names its own regression. | abort, `new_text is None` | **RED.** `[mac+ace1]` `cases/z07_r01_intent_blocking_cleared.py` is accepted by all 19 predicates and drops 4/5 live lines in all four scenarios. No such test exists on `main`. |
| **P6** | `test_duplicate_live_occurrence_is_preserved_or_blocks` | same | **The z10 residue.** Scenarios C and D plus the ace1 fixture's two duplicate pairs; multiset, not membership. | C aborts, D loses nothing | **RED.** `[mac+ace1]` `cases/z10_new_text_dedupes.py` is accepted by all 19 predicates **and by v4's membership harness**; v5's multiset invariant scores it `DROPS 1/5` on D. |
| **P7** | `test_ace1_fixture_aborts_with_47_managed_uncataloged` | `tests/cron/test_cron_fixtures.py` | **The R01 residue.** Pins `{cataloged: 11, ignore: 12, preserved_external: 1, uncataloged: 47}` — impossible under a constant classifier. | breakdown matches, cutover aborts | **RED.** `[ace1]` `tests/cron/fixtures/` does not exist on `main` (`git ls-files tests/cron/fixtures` → empty); it exists only on the plan branches. Fixture byte-equality re-verified today: `45cc7dc3…`. |
| **P8** | `test_ace2_fixture_classifies_as_captured` | `tests/cron/test_cron_fixtures.py` | **The R03/E11 residue.** Pins `before=14 managed=14 after=10`, which a mis-partition or a marker theft cannot reproduce. | counts match | **RED.** `[ace1]` same — no fixture directory on `main`. |
| **P9** | `test_preservation_shape_fixtures_are_inert` | `tests/cron/test_cutover_preservation.py` | The shape corpus imports only the pinned allowlist and calls no `open`/`subprocess`/`os`/`eval`. | 23 pass | **RED.** `[mac+ace1]` the fixture directory does not exist on `main`. |

### Secondary-control rows (revised from v4)

| # | Test name | File | What it will verify | Expected | Today's status on `main` + proving command |
|---|---|---|---|---|---|
| 16 **[revised]** | `test_preservation_attestation_rejects_twenty_six_named_mutations` | `test_scheduler_mutation_task3.py` | The 13-predicate set rejects the same 26 named cases the 19-predicate set did. | `False` ×26 | **RED.** `[mac+ace1]` `run.py` with the reduced registry: 13 predicates accept exactly the same six shapes as 19 and still accept the reference. Today's four mutation strings at `test_scheduler_mutation_task3.py:257-268` are the OLD source text. |
| 18 **[revised]** | `test_preservation_predicate_set_cannot_be_silently_thinned` | `test_scheduler_mutation_task3.py` | `len(NAMED_PREDICATES) == 13`, `len(NAMED_MUTATIONS) == 26`, `len(ADMITTED_RESIDUE) == 6`, each uniquely named. | passes | **RED.** `[ace1] grep -rn "NAMED_PREDICATES\|NAMED_MUTATIONS\|ADMITTED_RESIDUE" scripts/ tests/` → no matches. |
| 19 **[revised]** | `test_preservation_modules_obey_size_and_surface_constraints` | `test_scheduler_mutation_task3.py` | Both modules ≤400 lines, every function ≤50, neither matches a `PRIMITIVE_PATTERNS` entry. | passes | **RED.** `[mac+ace1]` neither module exists. Measured projection: 517 total for 13 predicates, largest function 34, `direct_primitives=[]`; split ≈300 + ≈220. |
| 23 **[revised]** | `test_preservation_attestation_rejects_the_v3_delegation_counterexample` | `test_scheduler_mutation_task3.py` | The delegation shape stays rejected under the reduced set, on **named** predicates. | `False`; `plan-cutover-terminal-return-closure` and `callee-allowlist-closure` both `False` | **RED.** `[mac+ace1]` v3's contract on `cases/mx2_v4_delegation.py` → all seven `True`; the 13-predicate set → `False` on 2. |
| 24 | `test_plan_cutover_may_only_return_an_abort_or_the_success_dict` | `test_scheduler_mutation_task3.py` | Predicate 8 in isolation. | `False` ×2 | **RED.** unchanged from v4. |
| **S1 [new]** | `test_behavioural_preservation_test_is_present_and_pinned` | `test_scheduler_mutation_task3.py` | Layer 3: deleting `tests/cron/test_cutover_preservation.py`, removing a named test, or replacing the invariant body with a constant makes the attestation `False` — **by parse, never by execution**. | `False` ×4 mutants | **RED.** `[ace1]` neither the test file nor the conjunct exists on `main`. |
| **S2 [new]** | `test_enforcement_checker_never_executes_indexed_blobs` | `test_scheduler_mutation_task3.py` | Regression guard for the v3 rejection: no `exec`, `eval`, `compile`, `importlib`, `runpy` or `subprocess` reachable from `evaluate_attestation`. | passes | **GREEN today** and must stay green — this is a declared guard, not a RED row. `[ace1] uv run pytest tests/enforcement/test_scheduler_mutation_task3.py -q` → 89 passed. |

**Score: 15 of 17 rows RED on today's `main`; 2 declared GREEN guards** (S2 and v4's row 8).

### Existing green gates that must stay green — re-measured at `05da65cc6` on ace1

| Gate | Status today | Command |
|---|---|---|
| whole enforcement checker | GREEN, exit 0 | `[ace1] uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py` |
| generated HTML report | GREEN, exit 0 | `[ace1] … --check-html docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html` |
| identity inventory freshness | GREEN, exit 0 | `[ace1] uv run --with pyyaml python scripts/cron/build-cron-identity-inventory.py --check` |
| task-3 enforcement suite | GREEN, 89 passed | `[ace1] uv run pytest tests/enforcement/test_scheduler_mutation_task3.py -q` |
| whole cron suite | GREEN, 284 passed | `[ace1] uv run pytest tests/cron -q` |

**Local macOS note, carried forward:** `tests/enforcement/test_scheduler_mutation_surfaces.py` fails
on macOS on the non-UTF-8 filename fixture (`OSError: [Errno 92] Illegal byte sequence`) and passes on
ace1. The prototype is pure `ast` plus stubbed execution and produces byte-identical output on both.

---

## Implementation Sequencing — delta from v4

0. **Prerequisite — [#3711](https://github.com/vamseeachanta/workspace-hub/issues/3711) merged.**
   Blocking for commits 2-4 only. Now `status:plan-review`.
1. **Commit 1 — the primary control, RED.** `tests/cron/test_cutover_preservation.py`,
   `tests/cron/fixtures/` (crontab fixtures **and** the 23 shape files), the
   `cron-cutover-preservation` CI job, and the secondary-control RED rows. Neither `tests/` nor
   `.github/workflows/` is a digest source, so the gate stays green while the rows fail. **May land
   before #3711.** *Gate check:* checker exit 0; `tests/cron` shows exactly the new failures and no
   others.
2. **Commit 2 — context unification.** Unchanged from v3.
3. **Commit 3 — precedence + collision guard.** Unchanged from v3.
4. **Commit 4 — the fused quadruple.** `cron_transaction.py` records refactor **and** both
   preservation modules **and** the `attestations.py` dispatch, in one commit, never split — the gate
   hard-errors in the intermediate state (`derive_status` → `migration-required` for
   `scripts/cron/cron_apply.py`, a hardcoded `resolved_dispositions` member at
   `scheduler_mutation_contract.py:307` that cannot move into a `disposition_group`). Rows P1-P9 and
   16/18/19/23/24/S1 go green. **Both prototype directories are deleted in this commit.** Inventory +
   digest + HTML refresh.
5. Every commit ends with `check-scheduler-mutation-surfaces.py` and `--check-html` at exit 0, after
   `git add` (the checker reads the git index, not the worktree).

---

## Acceptance Criteria — delta from v4

- [ ] **The primary control will be `tests/cron/test_cutover_preservation.py`, and it will assert the
      multiset preservation invariant against the committed `plan_cutover` over all six scenarios.**
- [ ] **A shape that loses a live line without a fail-closed abort will make that suite red, with no
      predicate change required — demonstrated by z07 and z10, both of which the 13-predicate set
      accepts.**
- [ ] **The invariant will be proven non-vacuous** by the 23-shape corpus test: 17 of 23 shapes will
      read destructive on at least one scenario and each shape's four-scenario tuple will be pinned.
- [ ] **The primary control will run in `.github/workflows/enforcement-gate.yml`**, a workflow with no
      `paths:` filter, on every PR to `main`.
- [ ] **Deleting or neutering the primary control will fail the enforcement gate**, via a parse-only
      `behavioural-test-present-and-pinned` conjunct that reads the indexed blob and **never executes
      it** — with no `ATT_SOURCES` entry and `scheduler_mutation_contract.py` still at exactly 400.
- [ ] **No new code-execution surface will be added to `check-scheduler-mutation-surfaces.py`**,
      asserted by row S2.
- [ ] **`NAMED_PREDICATES` will hold exactly 13 uniquely-named predicates**, with measured coverage
      identical to the 19-predicate set over the 35-shape corpus, and `ADMITTED_RESIDUE` exactly 6.
- [ ] **Both preservation modules will be ≤400 lines with every function ≤50 lines**, will match no
      `PRIMITIVE_PATTERNS` entry, and will require no `FORENSIC` or `mutation-surfaces.yaml` change.
- [ ] **The fixture sanitisation rule and the committed fixtures will agree** (v4's Fix B, unchanged),
      and the ace1 fixture will remain byte-equal to live `crontab -l`.
- [ ] **No new test failures on ace1:** `tests/enforcement` ends at exactly its 2 pre-existing named
      failures, `tests/cron` at 0 beyond the intentionally-RED new rows, and
      `scripts/cron/tests/test_validate_schedule.py` at exactly its 1 pre-existing named failure.
- [ ] **Both prototype directories will be deleted in commit 4.**
- [ ] **#3711 will be merged before commit 2.**
- [ ] **Owner decisions will be recorded before commit 4:** the `.claude/rules/` amendment (FIX 2) and
      the `required_status_checks` ruleset rule (D10 §R2). Neither will be applied by an agent.
- [ ] No implementation step will run `crontab` (write), `setup-cron.sh`, `cron_apply.py --apply`,
      `daily-cleanup.sh`, `repository_sync`, or `reconcile-ecosystem.sh --apply` on any host.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Codex r2 on **v2** | **MAJOR** | ordered AST attestation accepts a wrong implementation; unenforceable ace1-only inventory constraint. Answered in v3. |
| Codex r2 on **v3** | **MAJOR** | value-flow predicates allow a delegated early return; fixture sanitisation rule contradicts the fixture; prototype not committed. Answered in v4. |
| Codex r2 on **v4** | **MAJOR** | a seventh accepted-and-destructive evasion (`z07_r01_intent_blocking_cleared`) built on the committed harness. Answered here — **by restructuring the control model rather than by adding predicate 20.** |
| Author verification of **v5** (not a review) | n/a | Every number above is produced by `scripts/review/prototypes/3709-v5/`, run on macOS and re-run on `ace-linux-1` with byte-identical output. |
| Independent r2 on **v5** | **REQUIRED — not yet run** | Must be an independent provider, and should attack the **primary** control: find a shape that loses a live line while `preservation_holds` returns `True` on all six scenarios. |

**Overall result:** pending independent r2. `status:plan-approved` will not be applied by any agent.

### v4 → v5 delta

1. **The control model is restructured.** The behavioural test is the primary control; the AST
   predicates are demoted to defence-in-depth, and the plan says so in the acceptance criteria rather
   than in prose.
2. **v3's rejection of a behavioural *attestation* is preserved and is the reason the design is
   shaped this way.** The test imports the **committed** module under pytest; the enforcement gate
   still only parses, and row S2 makes that a standing regression guard.
3. **z07 is answered without a new predicate**, and the plan argues the case rather than asserting
   it: the primary control catches it in 4 of 4 scenarios, and a sixth predicate round has a
   thirteen-for-thirteen failure record.
4. **A fourteenth evasion (`z10_new_text_dedupes`) was found — in the control being promoted.** v4's
   membership-based harness scores it safe; the invariant is now a multiset comparison and the corpus
   gains two duplicate-line scenarios drawn from the ace1 fixture's own duplicate pairs.
5. **The predicate set is right-sized 19 → 13 on measured evidence**, with identical coverage over 35
   shapes, and each retained predicate has a stated purchase. Two new composed cases (z08, z09) prove
   the composition argument that stops the trim from going further.
6. **The fail-closed clause is analysed rather than asserted**, and the rule amendment is proposed as
   an owner decision, not slipped in.
7. **#3518 is measured, not assumed:** its implementation is already on `origin/main`
   (`1c3d7f683`, PR #3517 merged 2026-07-14), so the projected collision does not occur; the residual
   risk is a batch agent re-implementing it from a 1,600-file-stale plan branch.
8. **A pre-existing governance gap is surfaced:** the `protect-main` ruleset has **no required status
   checks at all**, so no CI check on this repository is merge-blocking today.

---

## Risks and Open Questions

- **Risk (new, material):** the primary control's power is bounded by its **scenario corpus**, not by
  its logic. A shape that loses a line only under a crontab layout absent from all six scenarios
  passes. This replaces "the predicate set must anticipate the shape" with "the corpus must exhibit
  the layout" — a weaker obligation, but a real one. Mitigation: the ace1 and ace2 fixtures are real
  captures, and C/D were added the moment the fixtures' duplicate property was noticed.
- **Risk (new):** the shape corpus is **executed** by pytest. It is committed, reviewed, import- and
  call-restricted by row P9, and never touched by the enforcement checker — but it is a code path that
  runs untrusted-by-construction files, and a reviewer should confirm the allowlist is tight enough.
- **Risk (new):** layer 2 is not in place. Until the owner adds `required_status_checks`, a red
  primary control is visible but not merge-blocking, and layer 3 catches only deletion/neutering, not
  a genuine failure.
- **Risk (new):** a failing behavioural test blocks a **merge**, never an **apply**. Apply-time safety
  rests entirely on the runtime guards inside `plan_cutover`, which is why predicates 17 and 19 are
  retained.
- **Risk (carried, reduced):** thirteen predicates over seven functions still make the destructive core
  refactor-hostile. Reduced from nineteen at zero measured coverage cost; going to eleven costs e09
  and M12, both destructive.
- **Risk (carried):** deleting `catalog_commands` would break `derive_cron_classifier_branches`.
- **Risk (carried):** `build_ownership_context` stays a delegating wrapper.
- **Risk (carried):** the intent report's multiset comparison is over raw line strings; no
  normalization will be added. v5 makes the **invariant** a multiset too, so the two now agree.
- **Risk (carried):** the acknowledgement digest binds to the whole baseline.
- **Risk (carried):** the fixtures are point-in-time captures and will drift from live state. ace1
  byte-equality re-verified 2026-07-30.
- **Risk (carried):** predicate 19 makes the first real cutover noisier; the escape hatch is
  occurrence-scoped `--acknowledge-absent`, not a class exemption.
- **Open (new):** should the `behavioural-test-present-and-pinned` conjunct live inside
  `python-postwrite-preservation-multiset-v1`, or become its own registered attestation? The former
  needs no `ATT_SOURCES` entry and keeps the contract at 400; the latter reports more legibly in the
  HTML audit but costs the 400-line pin. This plan chooses the former and flags the trade-off.
- **Open (new):** should #3518 be closed via the completeness gate now, given its implementation is on
  `main`? Owner decision; this plan does not change its labels.
- **Open (carried):** should #3708's premise be restated once this lands? Whether ace2 convergence
  belongs to #3709 or #3708 remains an owner decision.

---

## Complexity: T3

**T3** — unchanged. The change crosses a scheduler-mutation safety contract, two consumer CLIs, the
destructive classifier, the attestation that guards the reconstruction, a digest chain with a
host-dependent generator, two new enforcement modules, a new CI job, a proposed rule amendment, a
proposed repository-settings change, and a generated HTML audit. Implementation remains blocked until
user approval **and** until #3711 is merged.
