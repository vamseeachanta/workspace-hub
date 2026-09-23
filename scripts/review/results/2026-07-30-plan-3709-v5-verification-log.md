# Author verification log — #3709 plan v5

**Not a review.** Raw output for every measurement in
`docs/plans/2026-07-30-issue-3709-managed-block-classification-v5.md`.

Hosts: macOS (`/Users/.../workspace-hub`, plan branch working copy) and `ace-linux-1`
(`dev-primary`, `/mnt/local-analysis/workspace-hub`, HEAD `05da65cc6` = `origin/main`, Python 3.12.3).
Date: 2026-07-30.

No destructive command was run. `crontab -l` (read-only) was used once, to re-verify fixture
byte-equality. No `crontab <file>`, `setup-cron.sh`, `cron_apply.py`, `daily-cleanup.sh`,
`repository_sync`, or `reconcile-ecosystem.sh --apply` on any host.

---

## 1. ace1 host state

```
HEAD: 05da65cc6  branch: main
origin/main: 05da65cc6
python: Python 3.12.3
  400 scripts/enforcement/scheduler_mutation_contract.py
  257 scripts/cron/cron_transaction.py
  677 tests/enforcement/test_scheduler_mutation_task3.py
1a5e5573d00d17c4a820a831549fb92a2dad100b5fbab5572afcefadd57c84c1  (git cat-file blob :scripts/cron/setup-cron.sh)
=== CHECKER ===
checker exit=0
html_exit=0
inv_exit=0
```

## 2. ace1 fixture byte-equality (read-only)

```
$ ssh ace1 "crontab -l | sha256sum; crontab -l | wc -l"
45cc7dc366ff5ecb61525323fc0f2afda668782aaf323f819ae70cf67c8a9551  -
73
```

Identical to the committed `tests/cron/fixtures/ace1-crontab-2026-07-30.txt`
(sha256 `45cc7dc366ff5ecb61525323fc0f2afda668782aaf323f819ae70cf67c8a9551`, 73 lines).

## 3. ace1 pytest baseline — `main` is NOT green

```
=== pytest tests/enforcement ===
FAILED tests/enforcement/test_check_skill_index_coherence.py::test_real_repo_passes
FAILED tests/enforcement/test_soul_auto_load.py::test_drift_script_returns_zero_in_clean_state
2 failed, 417 passed in 396.05s (0:06:36)
=== pytest tests/cron ===
284 passed in 25.94s
=== pytest tests/enforcement/test_scheduler_mutation_task3.py ===
89 passed in 14.94s
=== pytest scripts/cron/tests/test_validate_schedule.py ===
FAILED scripts/cron/tests/test_validate_schedule.py::test_windows_tasks_have_windows_scheduler
1 failed, 53 passed in 8.07s
```

Corrections to the brief's stated baseline: `tests/cron/test_cron_runtime.py` **passes** (it is inside
the fully green `tests/cron` run), and `test_validate_schedule.py` lives under `scripts/cron/tests/`,
outside both suites.

## 4. Cross-host reproduction of the prototype

```
macOS   run.py            sha256 90d9c4f10f7af955084eed83a719b5b6119eeee1ab68375169e6fe33179a0b23
ace1    run.py            sha256 90d9c4f10f7af955084eed83a719b5b6119eeee1ab68375169e6fe33179a0b23
macOS   behaviour.py --check  sha256 d5368d2c4826d0da7fb564ef30642aca52aa50e12a8c86ed81a5fdc1dee61620
ace1    behaviour.py --check  sha256 d5368d2c4826d0da7fb564ef30642aca52aa50e12a8c86ed81a5fdc1dee61620
run_exit=0   beh_exit=0   (both hosts)
```

Invocation:
`PYTHONPATH=<repo>/scripts/enforcement python3 scripts/review/prototypes/3709-v5/run.py`

---

## 5. `run.py` — the demoted 19-predicate set over 23 cases + 12 mutations

```
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
z07_r01_intent_blocking_cleared              True   True   -
z08_no_guard_plus_marker_theft               False  True   classification-covers-every-line
z09_no_guard_plus_mispartition               False  True   classification-covers-every-line
z10_new_text_dedupes                         True   True   -

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

predicates: 19   file cases: 23   textual mutations: 12
reference per-predicate: all True
```

---

## 6. `behaviour.py --check` — the PRIMARY control over four scenarios

```
case                               v3     v4     A                       B                       C                       D                     
----------------------------------------------------------------------------------------------------------------------------------------------------
e01_nested_abort                   True   False  DROPS 5/5 LIVE LINES    SUCCEEDS, no loss       DROPS 5/5 LIVE LINES    SUCCEEDS, no loss     
e02_module_rebind                  True   False  ABORTS                  SUCCEEDS, no loss       DROPS 1/5 LIVE LINES    SUCCEEDS, no loss     
e03_inbody_rebind                  True   False  DROPS 4/5 LIVE LINES    DROPS 4/5 LIVE LINES    DROPS 4/5 LIVE LINES    DROPS 4/5 LIVE LINES  
e04_abort_returns_success          True   False  DROPS 5/5 LIVE LINES    SUCCEEDS, no loss       DROPS 5/5 LIVE LINES    SUCCEEDS, no loss     
e05_continue_skip                  True   False  ABORTS                  ABORTS                  ABORTS                  SUCCEEDS, no loss     
e06_second_success_dict            True   False  ABORTS                  DROPS 5/5 LIVE LINES    DROPS 5/5 LIVE LINES    DROPS 5/5 LIVE LINES  
e07_context_callable               True   False  DROPS 4/5 LIVE LINES    DROPS 4/5 LIVE LINES    DROPS 4/5 LIVE LINES    DROPS 4/5 LIVE LINES  
e08_decorator                      True   False  DROPS 5/5 LIVE LINES    DROPS 5/5 LIVE LINES    DROPS 5/5 LIVE LINES    DROPS 5/5 LIVE LINES  
e09_intent_helper_lie              True   False  ABORTS                  SUCCEEDS, no loss       DROPS 1/5 LIVE LINES    SUCCEEDS, no loss     
e10_no_totality_guard              True   False  ABORTS                  SUCCEEDS, no loss       ABORTS                  SUCCEEDS, no loss     
e11_parser_marker_theft            True   True   ABORTS                  ABORTS                  ABORTS                  ABORTS                
e12_marker_collusion               True   False  ABORTS                  DROPS 1/5 LIVE LINES    ABORTS                  DROPS 2/5 LIVE LINES  
e13_managed_line_reported_ignore   True   True   ABORTS                  SUCCEEDS, no loss       SUCCEEDS, no loss       SUCCEEDS, no loss     
e14_ignore_exempts_managed         True   False  DROPS 1/5 LIVE LINES    SUCCEEDS, no loss       SUCCEEDS, no loss       SUCCEEDS, no loss     
mx1_v3_counterexample              False  False  DROPS 4/5 LIVE LINES    DROPS 4/5 LIVE LINES    DROPS 4/5 LIVE LINES    DROPS 4/5 LIVE LINES  
mx2_v4_delegation                  True   False  DROPS 5/5 LIVE LINES    DROPS 5/5 LIVE LINES    DROPS 5/5 LIVE LINES    DROPS 5/5 LIVE LINES  
r01_detail_classifier_constant     True   True   ABORTS                  ABORTS                  ABORTS                  ABORTS                
r03_parse_mispartitions            True   True   ABORTS                  SUCCEEDS, no loss       ABORTS                  SUCCEEDS, no loss     
reference                          True   True   ABORTS                  SUCCEEDS, no loss       ABORTS                  SUCCEEDS, no loss     
z07_r01_intent_blocking_cleared    True   True   DROPS 4/5 LIVE LINES    DROPS 4/5 LIVE LINES    DROPS 4/5 LIVE LINES    DROPS 4/5 LIVE LINES  
z08_no_guard_plus_marker_theft     True   False  ABORTS                  DROPS 1/5 LIVE LINES    ABORTS                  DROPS 2/5 LIVE LINES  
z09_no_guard_plus_mispartition     True   False  ABORTS                  SUCCEEDS, no loss       ABORTS                  SUCCEEDS, no loss     
z10_new_text_dedupes               True   True   ABORTS                  SUCCEEDS, no loss       ABORTS                  DROPS 1/5 LIVE LINES  

v3 textual mutation                v3     v4     A                       B                       C                       D                     
----------------------------------------------------------------------------------------------------------------------------------------------------
M1                                 False  False  ABORTS                  ABORTS                  ABORTS                  ABORTS                
M2                                 False  False  ABORTS                  SUCCEEDS, no loss       ABORTS                  SUCCEEDS, no loss     
M3                                 False  False  ABORTS                  SUCCEEDS, no loss       ABORTS                  SUCCEEDS, no loss     
M3b                                False  False  ABORTS                  SUCCEEDS, no loss       ABORTS                  SUCCEEDS, no loss     
M4                                 False  False  ABORTS                  ABORTS                  ABORTS                  ABORTS                
M5                                 False  False  ABORTS                  ABORTS                  ABORTS                  ABORTS                
M6                                 False  False  ABORTS                  SUCCEEDS, no loss       DROPS 1/5 LIVE LINES    SUCCEEDS, no loss     
M7                                 True   False  ABORTS                  SUCCEEDS, no loss       ABORTS                  SUCCEEDS, no loss     
M11                                False  False  ABORTS                  SUCCEEDS, no loss       ABORTS                  SUCCEEDS, no loss     
M12                                False  False  ABORTS                  DROPS 4/5 LIVE LINES    ABORTS                  DROPS 4/5 LIVE LINES  
M13                                False  False  ABORTS                  SUCCEEDS, no loss       ABORTS                  SUCCEEDS, no loss     
M14                                False  False  ABORTS                  ABORTS                  ABORTS                  ABORTS                

honest expectation:  A ABORTS   B no loss   C ABORTS   D no loss
predicate-ACCEPTED and DESTRUCTIVE: ['z07_r01_intent_blocking_cleared', 'z10_new_text_dedupes']
```

---

## 7. Per-predicate sole-rejection evidence (FIX 3)

```
#   predicate                                rejects  SOLE rejecter of  (* = destructive)
1   plan-cutover-order                       3        -
2   plan-cutover-result-flow                 2        M12*
3   render-block-called-once                 2        M3
4   classify-populates-records               3        -
5   fallback-records-populated               2        -
6   rebuild-retention                        3        M4, M5
7   intent-derives-blocking                  1        -
8   plan-cutover-terminal-return-closure     2        e07_context_callable*
9   plan-cutover-success-path-chain          6        e06_second_success_dict*, M7
10  plan-cutover-binding-closure             5        e01_nested_abort*, e03_inbody_rebind*
11  module-binding-integrity                 2        e02_module_rebind*
12  abort-fails-closed                       1        e04_abort_returns_success*
13  callee-allowlist-closure                 2        -
14  record-loop-bodies-exact                 5        e05_continue_skip
15  absent-record-is-literal                 2        -
16  missing-occurrences-shape                1        -
17  classification-covers-every-line         4        e10_no_totality_guard, z08_no_guard_plus_marker_theft*, z09_no_guard_plus_mispartition
18  marker-prefixes-are-literal              2        e12_marker_collusion*
19  managed-absence-always-blocks            2        e14_ignore_exempts_managed*

total shapes: 35  destructive in >=1 scenario: 17
predicate-ACCEPTED and DESTRUCTIVE: ['z07_r01_intent_blocking_cleared', 'z10_new_text_dedupes']
```

## 8. Candidate reduced predicate sets — measured coverage

```
all 19                                         accepted=6   accepted&DESTRUCTIVE=['z07_r01_intent_blocking_cleared', 'z10_new_text_dedupes']
DROP 1,4,5,7,15,16  (13 kept)  <- recommended  accepted=6   accepted&DESTRUCTIVE=['z07_r01_intent_blocking_cleared', 'z10_new_text_dedupes']
DROP 1,2,4,5,7,13,15,16 (11 kept)              accepted=8   accepted&DESTRUCTIVE=['e09_intent_helper_lie', 'z07_r01_intent_blocking_cleared', 'z10_new_text_dedupes', 'M12']
closure + guards only (8 kept)                 accepted=15  accepted&DESTRUCTIVE=['e12_marker_collusion', 'z07_r01_intent_blocking_cleared', 'z10_new_text_dedupes', 'M12']
guards only 17,18,19 (3 kept)                  accepted=28  accepted&DESTRUCTIVE=['e01_nested_abort', 'e02_module_rebind', 'e03_inbody_rebind', 'e04_abort_returns_success', 'e06_second_success_dict', 'e07_context_callable', 'e08_decorator', 'e09_intent_helper_lie', 'mx2_v4_delegation', 'z07_r01_intent_blocking_cleared', 'z10_new_text_dedupes', 'M6', 'M12']
```

## 9. Module-budget projection for the 13-predicate set

```
v4 19-predicate prototype : 640 lines  (max function span 34, ceiling 50)
v5 13-predicate projection: 517 lines  (six predicate bodies = 101 lines, plus registry rows,
                                        separators and the prototype-only v3 scaffolding)
still > the enforced 400-line ceiling -> the two-module split is retained
```

## 10. #3518 state — measured, not assumed

```
$ git merge-base --is-ancestor 1c3d7f683 origin/main && echo YES
YES        (1c3d7f683 'fix(enforcement): attest setup wrapper os gate', 2026-07-13)
$ gh pr view 3517 --json state,mergedAt
state=MERGED merged=2026-07-14T10:48:04Z
$ git cat-file blob :scripts/cron/setup-cron.sh | sha256sum
1a5e5573d00d17c4a820a831549fb92a2dad100b5fbab5572afcefadd57c84c1
   == WRAPPER_SHA256[SETUP] in scripts/enforcement/scheduler_mutation_wrapper_attestations.py:24
$ [ace1] uv run pytest tests/enforcement/test_scheduler_mutation_task3.py -q
89 passed
```

## 11. Required-check gap — measured

```
$ gh api repos/vamseeachanta/workspace-hub/rulesets --jq '.[] | "\(.id) \(.name)"'
17369764 protect-main branch active
$ gh api repos/vamseeachanta/workspace-hub/rulesets/17369764 --jq '.rules[].type'
deletion
non_fast_forward
$ gh api repos/vamseeachanta/workspace-hub/branches/main/protection
{"message":"Branch not protected","status":"404"}

=> no required_status_checks rule exists; NO CI check is merge-blocking today,
   including the existing 'Scheduler Mutation Surface Guard'.
```
