# Author verification log — #3709 plan v4

**Not a review.** This records the commands that produced every measurement in
`docs/plans/2026-07-30-issue-3709-managed-block-classification-v4.md`, so an independent reviewer can
re-run them rather than re-derive them.

Hosts: macOS (author) and `ace-linux-1` (`dev-primary`, `/mnt/local-analysis/workspace-hub`,
HEAD `3fe934da9` = `origin/main`, Python 3.12.3). The prototype is pure `ast` and produced
byte-identical output on both.

No implementation was performed. No cron script, enforcement module, config file or crontab was
edited. `crontab -l` was NOT run for this revision — v3's committed fixtures already carry the live
capture. No `setup-cron.sh`, `cron_apply.py --apply`, `daily-cleanup.sh`, `repository_sync` or
`reconcile-ecosystem.sh --apply` on any host.

---

## 1. Baseline gates re-measured on ace1 at `3fe934da9`

```
$ ssh ace1 ... cd /mnt/local-analysis/workspace-hub
$ uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py                  -> 0
$ uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py --check-html ...  -> 0
$ uv run --with pyyaml python scripts/cron/build-cron-identity-inventory.py --check        -> 0
$ wc -l scripts/enforcement/scheduler_mutation_contract.py      -> 400   (pin holds)
$ wc -l scripts/enforcement/scheduler_mutation_attestations.py  -> 317
```

The three pytest gates (`test_scheduler_mutation_surfaces.py` 30 passed,
`test_scheduler_mutation_task3.py` 89 passed, `test_a1_preserved.py` 7 passed) were independently
re-run by the v3 r2 reviewer at the same HEAD and are carried forward.

---

## 2. Predicate matrix and mutation battery — reproduced on ace-linux-1

```
HOST=ace-linux-1 PY=Python 3.12.3
case                                         v4     v3     first failing predicate
------------------------------------------------------------------------------------------------------------
e01_nested_abort                             False  True   plan-cutover-binding-closure
e02_module_rebind                            False  True   module-binding-integrity
e03_inbody_rebind                            False  True   plan-cutover-binding-closure
e04_abort_returns_success                    False  True   abort-fails-closed
e05_continue_skip                            False  True   record-loop-bodies-exact
e06_second_success_dict                      False  True   plan-cutover-success-path-chain
e07_context_callable                         False  True   plan-cutover-terminal-return-closure
e08_decorator                                False  True   plan-cutover-binding-closure  (+1 more)
e09_intent_helper_lie                        False  True   callee-allowlist-closure  (+2 more)
e10_no_totality_guard                        False  True   classification-covers-every-line
e11_parser_marker_theft                      True   True   -
e12_marker_collusion                         False  True   marker-prefixes-are-literal
e13_managed_line_reported_ignore             True   True   -
e14_ignore_exempts_managed                   False  True   managed-absence-always-blocks
mx1_v3_counterexample                        False  False  plan-cutover-result-flow  (+11 more)
mx2_v4_delegation                            False  True   plan-cutover-terminal-return-closure  (+1 more)
r01_detail_classifier_constant               True   True   -
r03_parse_mispartitions                      True   True   -
reference                                    True   True   -

v3 textual mutation                          v4     v3     first failing predicate
------------------------------------------------------------------------------------------------------------
M1 classify only two of the three locations  False  False  classify-populates-records  (+1 more)
M2 delete the uncataloged abort guard        False  False  plan-cutover-order  (+1 more)
M3 hoist render_block above the classification False  False  render-block-called-once
M3b add an unused render_block decoy above the classification False  False  render-block-called-once  (+1 more)
M4 empty the `before` retention comprehension False  False  rebuild-retention
M5 drop `after` from the rebuilt result      False  False  rebuild-retention
M6 delete the blocking-intent abort guard    False  False  plan-cutover-order  (+1 more)
M7 delete the parse-error abort guard        False  True   plan-cutover-success-path-chain
M11 `_fallback_records` returns an empty list False  False  fallback-records-populated  (+1 more)
M12 the success return emits the block instead of new_text False  False  plan-cutover-result-flow
M13 make the record append conditional inside the inner loop False  False  classify-populates-records  (+1 more)
M14 pass an empty record list to the rebuild False  False  plan-cutover-order  (+1 more)

predicates: 19   file cases: 19   textual mutations: 12
reference per-predicate: all True
RUN_EXIT=0
```

Command: `python3 scripts/review/prototypes/3709-v4/run.py` (exit 0). The same command on macOS
produces byte-identical output.

**Reading of the `v3` column:** twelve of the fourteen rejection cases are `True` under v3's published
predicate contract. The v3 r2 reviewer constructed one of those twelve (`mx2_v4_delegation`); the
other eleven were constructed for this revision.

---

## 3. Behavioural harness — reproduced on ace-linux-1

```
case                                 v3     v4     A (orphan present)           B (clean crontab)
----------------------------------------------------------------------------------------------------------------------
e01_nested_abort                     True   False  DROPS 5/5 LIVE LINES         SUCCEEDS, no loss
e02_module_rebind                    True   False  ABORTS                       SUCCEEDS, no loss
e03_inbody_rebind                    True   False  DROPS 4/5 LIVE LINES         DROPS 4/5 LIVE LINES
e04_abort_returns_success            True   False  DROPS 5/5 LIVE LINES         SUCCEEDS, no loss
e05_continue_skip                    True   False  ABORTS                       ABORTS
e06_second_success_dict              True   False  ABORTS                       DROPS 5/5 LIVE LINES
e07_context_callable                 True   False  DROPS 4/5 LIVE LINES         DROPS 4/5 LIVE LINES
e08_decorator                        True   False  DROPS 5/5 LIVE LINES         DROPS 5/5 LIVE LINES
e09_intent_helper_lie                True   False  ABORTS                       SUCCEEDS, no loss
e10_no_totality_guard                True   False  ABORTS                       SUCCEEDS, no loss
e11_parser_marker_theft              True   True   ABORTS                       ABORTS
e12_marker_collusion                 True   False  ABORTS                       DROPS 1/5 LIVE LINES
e13_managed_line_reported_ignore     True   True   ABORTS                       SUCCEEDS, no loss
e14_ignore_exempts_managed           True   False  DROPS 1/5 LIVE LINES         SUCCEEDS, no loss
mx1_v3_counterexample                False  False  DROPS 4/5 LIVE LINES         DROPS 4/5 LIVE LINES
mx2_v4_delegation                    True   False  DROPS 5/5 LIVE LINES         DROPS 5/5 LIVE LINES
r01_detail_classifier_constant       True   True   ABORTS                       ABORTS
r03_parse_mispartitions              True   True   ABORTS                       SUCCEEDS, no loss
reference                            True   True   ABORTS                       SUCCEEDS, no loss

honest expectation:  A -> ABORTS (run-orphan-b is uncataloged)   B -> SUCCEEDS, no loss
```

Command: `python3 scripts/review/prototypes/3709-v4/behaviour.py` (exit 0).

Scenario A carries an uncataloged managed-block line, so the honest shape must ABORT. Scenario B
carries none, so the honest shape must SUCCEED losing nothing; B is where a silent drop is visible.

**The four accepted shapes are each measured non-destructive:**

| Case | v4 attestation | A | B |
|---|---|---|---|
| `r01_detail_classifier_constant` | accepts | ABORTS | ABORTS |
| `r03_parse_mispartitions` | accepts | ABORTS | no loss |
| `e11_parser_marker_theft` | accepts | ABORTS | ABORTS |
| `e13_managed_line_reported_ignore` | accepts | ABORTS | no loss |

`e12_marker_collusion` and `e14_ignore_exempts_managed` are the control cases: both are destructive
and both are **rejected** by predicates 18 and 19 respectively. Removing either predicate re-admits a
measured data-loss path.

---

## 4. Module budget

```
$ python3 - (ast section measurement over preservation_prototype.py)
shared helpers                                                  113
predicates 1-7  + local helpers                                 141
predicates 8-19 + local helpers                                 268
header / constants / allowlists / registry / evaluate()        ~119
total file                                                      641   (single-module ceiling 400)
largest function                                                 34   (function ceiling 50)
PRIMITIVE_PATTERNS direct_primitives                             []
```

Hence the two-module split specified in the plan (≈360 + ≈290).

---

## 5. FIX B evidence — host identifiers in the v3 fixtures

```
$ git show 'origin/plan/3709-managed-block-classification-v3:tests/cron/fixtures/ace1-crontab-2026-07-30.txt' | grep -n 'ace-linux'
7:# Generated: 2026-05-10T12:28:32Z for ace-linux-1

$ git show 'origin/plan/3709-managed-block-classification-v3:tests/cron/fixtures/ace2-crontab-2026-07-30.txt' | grep -n 'ace-linux'
6:# ai-tools-status: hourly AI CLI version check (local only; ace-linux-1 aggregates)
7:# harness-update: daily native harness tool update — hermes/claude/codex/gemini (ace-linux-2 slot 01:45)

$ grep -n 'hostname: ace-linux-1' config/workstations/registry.yaml
8:    hostname: ace-linux-1

$ git grep -c 'ace-linux-1' -- . | wc -l
944
```

The reviewer flagged only the ace1 occurrence; ace2 carries two more. All three are pre-existing
`ignore`-class comment lines that the capture did not add, and the identifier is public in 944 tracked
files. The plan amends rule 4 rather than rebaselining, because rebaselining would destroy the ace1
fixture's byte-equality with live `crontab -l` — the property the r2 reviewer used to verify rows 1,
8, 12 and 14.

---

## 6. Reproduction instructions for the next reviewer

```
python3 scripts/review/prototypes/3709-v4/run.py         # exit 0; predicate + mutation matrix
python3 scripts/review/prototypes/3709-v4/behaviour.py   # exit 0; data-loss measurement
python3 scripts/review/prototypes/3709-v4/make_cases.py  # regenerates every derived case; git diff must be empty
```

`run.py` exits non-zero if the reference is rejected, if any rejection case is accepted, **or if any
case in `ADMITTED_RESIDUE` stops being accepted** — so the plan's residue table cannot drift out of
date without turning the runner red.

To attack the design rather than re-read it: add a file to `cases/`, run `run.py`, and check whether
`behaviour.py` reports a drop for a case the predicate set accepted.
