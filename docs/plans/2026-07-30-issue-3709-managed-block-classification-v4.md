# Plan for #3709 (v4): Managed-Block Classification Before Cron Cutover

> **Status:** plan-review
> **Complexity:** T3
> **Date:** 2026-07-30
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3709
> **Client:** N/A
> **Lane:** lane:claude
> **Supersedes:** `docs/plans/2026-07-30-issue-3709-managed-block-classification-v3.md` on
> `plan/3709-managed-block-classification-v3` (independent Codex r2 verdict **MAJOR**: 1 major,
> 1 minor, 1 process gap)
> **Blocking dependency:** [#3711](https://github.com/vamseeachanta/workspace-hub/issues/3711) must
> land before commit 2 of this plan. Unchanged from v3 FIX 2; a plan for #3711 is being drafted in
> parallel. This plan does not attempt to remove the dependency.
> **Review artifacts:** `scripts/review/results/2026-07-30-plan-3709-v3-codex-r2.md` (the review this
> revision answers); `scripts/review/results/2026-07-30-plan-3709-v4-verification-log.md` (author
> verification log, not a review); independent r2 adversarial review REQUIRED before any approval
> **Executable prototype (new in v4):** `scripts/review/prototypes/3709-v4/` — every number in this
> document is produced by `run.py` and `behaviour.py` in that directory. See FIX C.

---

## Tense convention

Every statement about **work this plan proposes** is written in future tense. The `Evidence` and
`Today's status` columns are **measurements**, written as measurements with the command that produced
them.

Measurements new in v4 were produced on **macOS** and re-produced byte-identically on
**`ace-linux-1`** (`dev-primary`, `/mnt/local-analysis/workspace-hub`, HEAD `3fe934da9` =
`origin/main`, Python 3.12.3) on 2026-07-30. The prototype is pure `ast` and is host-independent;
both runs are in the verification log. Measurements carried forward from v3 keep their original
`[ace1]` provenance.

---

## Scope of this revision

v4 is a **narrow delta** on v3. The r2 reviewer independently verified and confirmed the following,
all of which **carry forward unchanged and are not relitigated here**:

| Confirmed by independent r2 on v3 | Status in v4 |
|---|---|
| v3's predicate set rejects the v2 counter-example | Carried forward; re-measured as case `mx1_v3_counterexample` |
| The ace1 fixture is byte-equal to live ace1 (73 lines, SHA `45cc7dc…`) | Carried forward unchanged |
| ace2's sanitised fixture is class-preserving (40/40 identical `(location, index, class)`) | Carried forward unchanged |
| Baseline gates green on ace1: checker, HTML checker, inventory `--check`, three pytest gates | Re-measured green at `3fe934da9`; see the gates table |
| v2 decisions that survived: retained dead `catalog_commands` / `external_fingerprints`, third-party-first ordering, `build_classification_context` as the single seam, behavioural attestation rejected, `scheduler_mutation_contract.py` at exactly 400 lines | Carried forward unchanged |
| The new sibling module `scheduler_mutation_preservation.py` (zero `PRIMITIVE_PATTERNS` triggers) | Carried forward, **but the measured size changes** — see FIX A §Module budget |
| #3711 sequenced as a hard blocking prerequisite of commits 2-4 | Carried forward unchanged |

**v3 design sections D1-D4 and D6-D8 are adopted verbatim.** This document rewrites **D5** again
(FIX A), amends **D8's sanitisation rule 4** (FIX B), adds **D9** (the committed prototype, FIX C),
and republishes only the TDD rows that change.

---

## FIX A (r2 MAJOR) — D5 rewritten again: closing the delegation route

### The finding, reproduced

The reviewer built a wrong implementation satisfying **all seven** v3 predicates: a non-constant early
return from `plan_cutover` calls an **uninspected helper** that returns only the managed block with an
empty intent report, while the compliant classification / rebuild / intent pipeline remains later in
the function. v3's predicates inspect `plan_cutover`'s own body but never ask what its callees do, so
every predicate still sees what it expects.

The counter-example is committed verbatim as
`scripts/review/prototypes/3709-v4/cases/mx2_v4_delegation.py`. Re-implementing v3's published
predicate contract and running it against that file reproduces the reviewer's result exactly:

```
mx2_v4_delegation   v3 predicate set = True     (all seven True)
                    v4 predicate set = False
                      plan-cutover-terminal-return-closure  False
                      callee-allowlist-closure              False
```

Behaviourally, on the harness's synthetic crontab, that module **drops 5 of 5 live lines while
reporting `abort_reason: None`**. This violates `scheduler-mutation-safety.md`'s "failed source
attestations must fail closed": the attestation certifies a destructive implementation.

### D5 — the v4 predicate set: 7 carried forward + 12 new

`python-postwrite-preservation-multiset-v1` will be redefined as the conjunction of **nineteen** named
predicates. Predicates 1-7 are v3's, unchanged in wording and in effect. Predicates 8-19 are the v4
delta. All nineteen will be expressed over the repository's existing reachability engine
`scheduler_mutation_python_flow._walk_block`, exactly as v3 established.

The delta answers the reviewer's three suggested directions **jointly**, because each alone is
defeatable:

| Reviewer's direction | v4 predicate that carries it | Why it is insufficient alone |
|---|---|---|
| no live `Return` before the classification/abort sequence | 9 `plan-cutover-success-path-chain` | an early return that is *after* the sequence and returns a second success dict still bypasses it (case E06) |
| the delegated helper set is closed and inspected | 13 `callee-allowlist-closure`, 12 `abort-fails-closed`, 16 `missing-occurrences-shape` | a nested `def` (E01), a module-level rebind (E02), an in-body rebind (E03) or a decorator (E08) all keep the allowlist intact while changing what the names resolve to |
| terminal return set equality over the inter-procedural result | 8 `plan-cutover-terminal-return-closure` | a `Call` terminal return is not a `Dict`, so v3's "exactly one terminal Dict" is satisfied by an arbitrary delegated return (this IS the reviewer's counter-example) |

| # | Predicate | Assertion | Answers |
|---|---|---|---|
| 1-7 | *(v3, verbatim)* | `plan-cutover-order`, `plan-cutover-result-flow`, `render-block-called-once`, `classify-populates-records`, `fallback-records-populated`, `rebuild-retention`, `intent-derives-blocking` | v2's counter-example |
| 8 | `plan-cutover-terminal-return-closure` | Every live path of `plan_cutover` ends in a `Return`, and every terminal return expression is **either** a `Call` whose `func` is `Name('_abort')` **or** the single success `Dict`; the set of distinct terminal `Dict`s has size exactly 1. Nothing else may terminate the function. | MX2, E06, E07 |
| 9 | `plan-cutover-success-path-chain` | Every live path terminating in the success `Dict` traverses, **in order on that path**, the nine-step value chain `classified = classify_crontab_lines(...)` → `if classified['error']:` → the `uncataloged` comprehension → `if uncataloged:` → `block = render_block(...)` → `new_lines = _rebuild_from_records(...)` → an assignment to `new_text` mentioning `new_lines` → `intent = build_cutover_intent(...)` → `if intent['blocking']:`. v3 asserted this order over the function **body**; v4 asserts it over **every success path**. | E06, M7 |
| 10 | `plan-cutover-binding-closure` | The set of names assigned anywhere in `plan_cutover` is **exactly** the nine `{classify_detail, selected_tasks, roles, classified, uncataloged, block, new_lines, new_text, intent}`; `plan_cutover` contains no nested `FunctionDef` / `AsyncFunctionDef` / `ClassDef` / `Lambda`; it carries no decorator; and its signature is exactly `(current_text, classification_context, *, acknowledged=())`. | E01, E03, E08 |
| 11 | `module-binding-integrity` | No module-level statement may rebind a name defined by a `def` in the same module. Imports **may** bind an allowlisted name (that is how `render_block` and `parse_crontab` arrive) unless a top-level `def` of the same name also exists. No inspected function is decorated; none is defined twice. | E02, E08 |
| 12 | `abort-fails-closed` | `_abort` joins the inspected set. Every live path ends in a `Return`; every terminal return is a `Dict` binding `'new_text'` → `Constant(None)` and `'abort_reason'` → the `Name` of `_abort`'s first parameter. No abort may report `abort_reason=None`. | E04 (**closes v3 residue R2**) |
| 13 | `callee-allowlist-closure` | For each of the seven inspected functions, the set of `ast.Name` callees is **exactly** a pinned allowlist (builtins exempted). Introducing any new helper into the safety path is a red test, not an invisible diff. | MX2, E09 |
| 14 | `record-loop-bodies-exact` | In `classify_crontab_lines` the outer location loop's body is exactly the inner `enumerate` loop, whose body is exactly the record `append`; no `continue` / `break` / `if` / `try` / `while` appears inside either. Same shape constraint on `_fallback_records`. | E05, M13 |
| 15 | `absent-record-is-literal` | In `build_cutover_intent`, `absent`'s element expression is a `Dict` **literal** binding `'class'` → `r['detail']['class']`, `'line'` → `r['line']`, `'location'` → `r['location']`, `'index'` → `r['index']`, and the comprehension carries no filter. The absence record may not be manufactured by a helper. | E09 |
| 16 | `missing-occurrences-shape` | `_missing_occurrences` joins the inspected set: exactly one loop, over `records`, whose body is exactly one `if remaining[record['line']] > 0:` with an `else` of exactly `missing.append(record)`; `remaining = Counter(new_lines)`; every terminal return is `missing`. | E09 |
| 17 | `classification-covers-every-line` | `classify_crontab_lines` will carry a **totality guard**: `expected` is a comprehension over `current_text.splitlines()` filtered by `not line.startswith(MARKER_PREFIXES)`, and `if sorted(r['line'] for r in records) != sorted(expected):` returns a non-null `error`. The guard lies on every live path that returns `error: None`. | E10, E11, and it neutralises v3 residue R3's line-dropping form |
| 18 | `marker-prefixes-are-literal` | `MARKER_PREFIXES` is a module-level assignment whose value is exactly `('# >>> workspace-hub managed', '# <<< workspace-hub managed')`. Predicate 17's exclusion set may not be a function call or a mutable constant. | E12 |
| 19 | `managed-absence-always-blocks` | `blocking`'s condition contains `a['class'] != 'ignore' or a['location'] == 'managed'`. A managed-block line the new block does not reproduce **always** blocks, because managed records are unconditionally dropped by the rebuild and the intent report is their only protection. | E13, E14 |

**Predicates 8, 10, 11 and 13 are the closure group** — they are what make "the helper set is closed"
a real claim rather than a naming convention. Together they say: `plan_cutover` may end only in an
`_abort` call or the one success dict; it may bind only nine names; it may call only six functions; and
none of those six may be swapped out at module scope, in the body, by nesting, or by decoration.

**Predicate 17 is the load-bearing new safety idea.** Predicates 1-16 pin *shape*; predicate 17 makes
the implementation **check itself at runtime** that classification covered every live line, and pins
that check structurally. That is what converts a whole class of parser defects from "silent data loss"
into "fail closed", including a residue v3 admitted it could not close.

### Proof: the counter-example is rejected, and so are twenty-five other shapes

`python3 scripts/review/prototypes/3709-v4/run.py` — exit 0, reproduced identically on ace1:

```
case                                         v4     v3     first failing predicate
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

M1  classify only two of the three locations              False  False
M2  delete the uncataloged abort guard                    False  False
M3  hoist render_block above the classification           False  False
M3b add an unused render_block decoy                      False  False
M4  empty the `before` retention comprehension            False  False
M5  drop `after` from the rebuilt result                  False  False
M6  delete the blocking-intent abort guard                False  False
M7  delete the parse-error abort guard                    False  True
M11 `_fallback_records` returns an empty list             False  False
M12 the success return emits the block instead of new_text False False
M13 make the record append conditional                    False  False
M14 pass an empty record list to the rebuild              False  False

predicates: 19   file cases: 19   textual mutations: 12
reference per-predicate: all True
```

**The `v3` column is the point of the table.** Twelve of the fourteen rejection cases are `True` under
v3's published contract — that is, v3 would have certified all of them. The reviewer found one of
those twelve; this plan found the other eleven.

v3's M8, M9 and M10 are shape mutations rather than token edits; they are embodied verbatim in
`mx1_v3_counterexample.py`, which is a rejection case in its own right, so v3's sixteen-mutation
battery is carried forward in full.

### The fifth evasion, and the sixth: what I built and what happened

The brief required an honest attempt to defeat my own predicate set rather than declaring victory.
Six were constructed after the reviewer's. Four were closed by adding a predicate; **two were not
closable by shape alone and forced a change to the implementation the plan specifies**:

| Attempt | Shape | Outcome |
|---|---|---|
| E01 / E02 / E03 / E08 | four different ways to make a pinned name resolve to something else (nested def, module rebind, in-body rebind, decorator) | **Closed** by predicates 10 and 11 |
| E05 | `if line.startswith('#'): continue` before the record append — v3's "unconditional direct child of the inner loop body" is satisfied by it | **Closed** by predicate 14 |
| E09 | the intent report's element expression *and* its membership test delegated to uninspected helpers | **Closed** by predicates 13, 15, 16 |
| E11 | the parser reports live lines as block markers, so they vanish from both sides of a `parsed['markers']`-based reconciliation | **Not closable by predicate.** Forced predicate 17's expected set to be derived from a module constant instead of from the parser. Measured non-destructive under that form. |
| E12 | the parser steals a line **and** the marker constant names that same line, so it is missing from both sides even of the constant-derived guard | **Not closable by predicate alone.** Forced `MARKER_PREFIXES` to be a pinned literal (predicate 18). Before predicate 18 it dropped 1 of 5 live lines while the attestation returned `True`. |
| E13 | the classifier reports live **managed-block** lines as class `ignore`; managed records are always dropped by the rebuild, and `blocking` deliberately exempts `ignore` | **Not an attestation gap — a design defect.** No predicate over the four v3 functions can see it. Closed by changing `blocking` to `a['class'] != 'ignore' or a['location'] == 'managed'`, pinned by predicate 19. Before that change it dropped 1 of 5 live lines with `abort_reason: None`. |

E13 is the most important of the six. It is the same defect #3709 was filed for — a managed-block line
that vanishes instead of blocking — reachable through the classifier rather than through
`plan_cutover`. **v3's design would have shipped it**, because v3's intent report exempts class
`ignore` unconditionally and v3 recorded that exemption as an open question rather than a hazard. v4
resolves the open question in the safe direction and pins the resolution.

**After six attempts I could not construct a shape that the v4 predicate set accepts and that is
destructive on the behavioural harness.** That is a measurement, not a proof. An AST-shape attestation
is a syntactic approximation of a semantic property and must be unsound somewhere; the honest claim is
that the four shapes it still accepts were each executed and none of them loses a line.

### The residue, with a named covering test for each

v3 offered "four compensating controls", which the reviewer judged too diffuse. v4 states the residue
as an enumerated list, each entry with its measured behaviour and **one named test**:

| # | Shape the attestation still accepts | Measured behaviour | Named covering test |
|---|---|---|---|
| RES-1 | `r01_detail_classifier_constant` — `_detail_classifier` returns `{'class': 'cataloged'}` for every line (v3 residue R1) | **ABORTS** in both scenarios. Every line is dropped by the rebuild, every drop becomes an `absent` record of class `cataloged`, and predicate 19's `blocking` rule fires. Not a data-loss path. | row 1 `test_ace1_fixture_aborts_with_47_managed_uncataloged` — the fixture's `{cataloged: 11, ignore: 12, preserved_external: 1, uncataloged: 47}` breakdown is impossible under a constant classifier |
| RES-2 | `r03_parse_mispartitions` — the parser puts every line in `before` (v3 residue R3) | **ABORTS** in scenario A, **no loss** in scenario B. Predicate 17's totality guard sees every line, and the rebuild retains every non-cataloged record; the output shape is wrong, no line is lost. | row 20 `test_ace2_fixture_classifies_as_captured` — pins `before=14 managed=14 after=10`, which a mis-partition cannot reproduce |
| RES-3 | `e11_parser_marker_theft` — the parser reports live lines as block markers | **ABORTS** in both scenarios: the constant-derived expected set still contains the stolen line, so the totality guard fires. | row 20 `test_ace2_fixture_classifies_as_captured` — the stolen line changes the location counts |
| RES-4 | `e13_managed_line_reported_ignore` — the classifier reports managed cron lines as class `ignore` | **ABORTS** in scenario A and loses nothing in scenario B, **because of predicate 19**. Without predicate 19 it drops a live line silently (case `e14_ignore_exempts_managed`, which the attestation rejects). | row 2 `test_managed_block_unknown_line_blocks_before_rebuild` — a managed line with no catalog match must block regardless of what class it is given |

v3's residue R2 (`_abort` returns `abort_reason=None`) is **closed**, not residual: predicate 12
rejects it, and the behavioural harness confirms it was a 5-of-5 data-loss path.

Two of v3's three residues therefore survive as shapes the attestation accepts, but **neither is a
data-loss path any more** — RES-1 is caught by the pinned intent chain and RES-2 by the pinned totality
guard. That is a stronger statement than v3's, and it is measured rather than argued.

### The cost, stated plainly

Nineteen predicates over seven functions is close to a transcription of the destructive core. Any
legitimate refactor of those seven functions will require editing a named predicate. **That is the
intended behaviour for a destructive path** — it converts a refactor into a review trigger — but it is
a real cost and a reviewer should weigh it. The alternatives remain rejected for v2's and v3's
reasons: a behavioural attestation would execute code inside the enforcement checker, and a verbatim
token list is not reviewable.

### Module budget — a measured constraint that changed

v3 measured its predicate module at 293 lines against the enforced 400-line ceiling
(`tests/enforcement/test_scheduler_mutation_task3.py:274-288`, which also caps every function at 50).
The v4 prototype measures **641 lines**, so a single module will **not** fit. Measured section sizes:

```
shared helpers (paths, terminals, dict items, comprehensions)   113
predicates 1-7  + their local helpers                           141
predicates 8-19 + their local helpers                           268
header, constants, allowlists, registry, evaluate()              ~119
largest function                                                  34   (ceiling 50)
```

The predicate set will therefore ship as **two** sibling modules:

| Module | Contents | Projected lines |
|---|---|---|
| `scripts/enforcement/scheduler_mutation_preservation.py` | shared helpers, predicates 1-7, `NAMED_PREDICATES`, `NAMED_MUTATIONS`, `preservation_shape` | ≈ 360 |
| `scripts/enforcement/scheduler_mutation_preservation_closure.py` | predicates 8-19 and their local helpers | ≈ 290 |

Import order stays acyclic: `attestations → preservation → preservation_closure → python_flow`.
`attestations.py` will still lose `_preservation_shape` and gain an import plus a one-line dispatch,
landing near 302 of 400. The prototype's own `PRIMITIVE_PATTERNS` scan measured
`direct_primitives=[]` for the whole 641 lines, so **neither module will need `FORENSIC` membership
or a `mutation-surfaces.yaml` entry** — v3's constraint holds across the split, and the plan keeps
v3's pin: if any predicate line ever matches a `PRIMITIVE_PATTERNS` regex, that module must be added
to `FORENSIC` with the sentinel comment in the same commit.

`ATT_SOURCES` will gain no entry and `scheduler_mutation_contract.py` will stay at exactly 400 lines
(re-measured at `3fe934da9`: 400).

### Consequential changes to the implementation D5 specifies

Three of the new predicates pin code that v3's design did not contain. The implementation will
therefore also:

1. add `MARKER_PREFIXES` as a module-level literal in `cron_transaction.py`;
2. add the totality guard to `classify_crontab_lines` (predicate 17) — a parse that does not account
   for every line of `current_text` will return an `error` and abort, instead of silently planning
   over a partial record set;
3. change `build_cutover_intent`'s `blocking` rule so a **managed-block** absence blocks even when its
   class is `ignore` (predicate 19), resolving v3's open question in the fail-closed direction;
4. extract `_missing_occurrences` (predicate 16) so the multiset comparison is a pinned shape rather
   than an inline helper call.

---

## FIX B (r2 MINOR) — D8 sanitisation rule 4, amended

### The finding

v3's rule 4 says provenance "lives in a sidecar, never in the fixture", and
`tests/cron/fixtures/README.md` repeats it, while the committed ace1 fixture contains
`# Generated: 2026-05-10T12:28:32Z for ace-linux-1` at line 7. Measured on the v3 branch, the ace2
fixture carries two more:

```
ace1 line 7 : # Generated: 2026-05-10T12:28:32Z for ace-linux-1
ace2 line 6 : # ai-tools-status: … (local only; ace-linux-1 aggregates)
ace2 line 7 : # harness-update: … (ace-linux-2 slot 01:45)
```

All three are pre-existing `ignore`-class comment lines that the capture did not add.

### Decision: **amend the rule; do not rebaseline the fixtures**

Reasons, in order of weight:

1. **Rebaselining destroys the fixture's strongest verification property.** The ace1 fixture is
   byte-equal to live `crontab -l` with zero redactions, and the r2 reviewer used exactly that
   property to confirm rows 1, 8, 12 and 14. Editing a comment to satisfy a wording choice would
   break the one thing a future reviewer can check independently with a single command.
2. **These are not provenance the fixture process added.** They are content of the captured machine's
   own crontab. Rule 1 already says classification-load-bearing bytes are copied exactly; rule 3
   already says redacting a matched line would alter that line's class. Rule 4 was written about the
   *header the capture process would otherwise prepend*, and it over-reached.
3. **The identifiers are not sensitive.** `ace-linux-1` appears in `config/workstations/registry.yaml`
   and in **944** tracked files in this repo. Nothing is disclosed by their presence in a fixture.
4. **Index stability.** Rows 12 and 14 assert exact `(location, index)` pairs. Rebaselining is a
   deliberate index shift for no safety gain.

**Rule 4 will be restated as:**

> **Provenance added by the capture process lives in a sidecar, never in the fixture.** Host, machine
> id, capture date, line count and deny-scan result go in `tests/cron/fixtures/README.md`, because a
> header comment inside a fixture would shift every asserted index. **Content already present in the
> captured crontab is preserved verbatim under rule 1, including host identifiers inside `ignore`-class
> comment lines.** Redacting such a line is forbidden, not merely unnecessary: it would edit a line
> whose class is asserted, and it would break the byte-equality that makes a zero-redaction capture
> independently verifiable. The deny-scan of rule 3 remains the boundary for anything sensitive; host
> names are not in it, and are public in `config/workstations/registry.yaml`.

`tests/cron/fixtures/README.md` will carry the amended wording and will enumerate the three
pre-existing host-identifier lines by fixture and line number, so the artifact and the rule agree and
a reviewer's "does any host identifier survive?" check has a documented answer instead of a
contradiction. Row 21's test will assert the enumeration matches the fixtures.

---

## FIX C (r2 process) — D9: the prototype is committed

The reviewer could not run v3's predicate prototype because v3 committed only the plan and a
verification log. Re-implementing the published contract meant testing the reviewer's reading of the
plan rather than the plan's design — and that reading turned out to be faithful, but there was no way
to know that in advance.

**The v4 prototype is committed on this branch**, under `scripts/review/prototypes/3709-v4/`, so the
next review executes the same artifact:

| File | Purpose |
|---|---|
| `preservation_prototype.py` | the nineteen named predicates (641 lines; the shipping split is specified above) |
| `cases/reference.py` | the honest shape the attestation must accept — hand-written, the source of truth for every derived case |
| `cases/mx1_v3_counterexample.py` | v2's counter-example, verbatim, hand-written |
| `cases/mx2_v4_delegation.py` | **the v3-r2 reviewer's delegation counter-example, verbatim** |
| `cases/e01…e14`, `cases/r01`, `cases/r03` | sixteen further shapes; each file's docstring states what it attacks |
| `mutations.py` | v3's textual mutation battery, re-expressed against the v4 reference |
| `make_cases.py` | regenerates every derived case as a minimal delta on `reference.py`, so a reviewer diffs rather than re-reads |
| `run.py` | the predicate matrix; **exit 0 iff** the reference is accepted, every rejection case is rejected, and every case in `ADMITTED_RESIDUE` is still accepted |
| `behaviour.py` | executes each case against two synthetic crontabs and reports data loss |

`run.py` fails if an admitted-residue case starts being rejected, so the residue table cannot silently
drift out of date either.

**This directory is a review artifact, not an implementation.** It is not imported by any enforcement
module, and `scripts/enforcement/scheduler_mutation_preservation*.py` will not be created before
#3709 is approved and #3711 has landed. When the implementation lands, the prototype's predicate
bodies will move into the two enforcement modules and the `cases/` tree will move to
`tests/enforcement/fixtures/`; the prototype directory will then be deleted in the same commit.

---

## Artifact Map — delta from v3

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-30-issue-3709-managed-block-classification-v4.md` |
| Author verification log | `scripts/review/results/2026-07-30-plan-3709-v4-verification-log.md` |
| Superseded v3 plan | `docs/plans/2026-07-30-issue-3709-managed-block-classification-v3.md` |
| Independent r2 review being answered | `scripts/review/results/2026-07-30-plan-3709-v3-codex-r2.md` |
| Independent plan review (r2, required) | `scripts/review/results/2026-07-30-plan-3709-v4-<provider>-r2.md` |
| **Executable predicate prototype** | `scripts/review/prototypes/3709-v4/` (new, this branch) |
| Preservation predicate module | `scripts/enforcement/scheduler_mutation_preservation.py` (new, ≈360 lines) |
| Preservation closure module | `scripts/enforcement/scheduler_mutation_preservation_closure.py` (new, ≈290 lines) |

All other rows of v3's artifact map carry forward unchanged.

---

## Files to Change — delta from v3

| Action | Path | Change from v3 |
|---|---|---|
| Create **[v4]** | `scripts/enforcement/scheduler_mutation_preservation_closure.py` | New second module; predicates 8-19 do not fit under the 400-line ceiling alongside 1-7 |
| Modify **[v4]** | `scripts/enforcement/scheduler_mutation_preservation.py` | Was 293 lines / 7 predicates in v3; now ≈360 lines, hosting predicates 1-7 plus `NAMED_PREDICATES` (19) and `NAMED_MUTATIONS` (26) |
| Modify **[v4]** | `scripts/cron/cron_transaction.py` | v3's refactor **plus**: `MARKER_PREFIXES` literal; the totality guard in `classify_crontab_lines`; `_missing_occurrences` extracted; `blocking` made location-aware |
| Modify **[v4]** | `tests/enforcement/test_scheduler_mutation_task3.py` | Rows 15-19 plus new rows 23-26; the mutation battery grows from 16 to 26 named rejection cases and gains a 4-entry admitted-residue table |
| Create **[v4]** | `tests/enforcement/fixtures/` | Sixteen case files instead of v3's two, migrated from the prototype's `cases/` |
| Modify **[v4]** | `tests/cron/fixtures/README.md` | Amended sanitisation rule 4 + the enumeration of pre-existing host-identifier lines |
| Modify **[v4]** | `tests/cron/test_cron_fixtures.py` | Row 21 additionally asserts the host-identifier enumeration matches the fixtures |
| Modify **[v4]** | `tests/cron/test_cron_apply.py` | Adds rows 25 and 26 |
| Delete **[v4]** | `scripts/review/prototypes/3709-v4/` | Removed in commit 4, once its contents have moved into the enforcement modules and `tests/enforcement/fixtures/` |

Every other row of v3's Files-to-Change table carries forward unchanged, including the four
`Not changed` pins (`scheduler_mutation_contract.py` at 400 lines, `python_flow.py` imported not
modified, no `FORENSIC` member, `cron_render.py` owned by #3711).

---

## TDD Test List — delta from v3

v3's 22 rows carry forward. Rows 16, 18 and 19 change their expected values; rows 23-26 are new. Every
row still states its status on today's `main` with the command that proves it.

| # | Test name | File | What it will verify | Expected output | Today's status on `main` + proving command |
|---|---|---|---|---|---|
| 16 **[revised]** | `test_preservation_attestation_rejects_twenty_six_named_mutations` | `test_scheduler_mutation_task3.py` | Each of the 14 case files and 12 textual mutations flips the attestation `False`. | `False` ×26 | **RED.** `[ace1]` today's four mutation strings at `test_scheduler_mutation_task3.py:257-268` are the OLD source text and none of the new anchors exists in today's `cron_transaction.py`. Against the committed prototype: v4 rejects 26/26; v3's contract rejects only 14/26. |
| 18 **[revised]** | `test_preservation_predicate_set_cannot_be_silently_thinned` | `test_scheduler_mutation_task3.py` | `len(NAMED_PREDICATES) == 19`, `len(NAMED_MUTATIONS) == 26`, `len(ADMITTED_RESIDUE) == 4`, each uniquely named. | passes | **RED.** `[ace1]` `grep -rn "NAMED_PREDICATES\|NAMED_MUTATIONS\|ADMITTED_RESIDUE" scripts/ tests/` → no matches. |
| 19 **[revised]** | `test_preservation_modules_obey_size_and_surface_constraints` | `test_scheduler_mutation_task3.py` | **Both** new modules are ≤400 lines, every function ≤50, and neither matches a `PRIMITIVE_PATTERNS` entry. | passes | **RED.** `[ace1]` neither module exists. Prototype measured: 641 total, largest function 34, `direct_primitives=[]`; split projects to ≈360 + ≈290. |
| 23 **[new]** | `test_preservation_attestation_rejects_the_v3_delegation_counterexample` | `test_scheduler_mutation_task3.py` | The r2 reviewer's early-return-to-an-uninspected-helper shape is rejected, on **named** predicates. | `False`; `plan-cutover-terminal-return-closure` and `callee-allowlist-closure` both `False` | **RED.** `[mac+ace1]` v3's published contract on `cases/mx2_v4_delegation.py` → all seven `True`; v4 → `False` on 2 of 19. The fixture does not exist on `main`. |
| 24 **[new]** | `test_plan_cutover_may_only_return_an_abort_or_the_success_dict` | `test_scheduler_mutation_task3.py` | Predicate 8 in isolation: a terminal `Call` that is not `_abort`, and a second success `Dict`, are both rejected. | `False` ×2 | **RED.** `[mac+ace1]` `cases/e07_context_callable.py` and `cases/e06_second_success_dict.py` are both accepted by v3's contract; neither fixture nor predicate exists on `main`. |
| 25 **[new]** | `test_absent_managed_line_blocks_even_when_classified_ignore` | `test_cron_apply.py` | A managed-block line the new block does not reproduce blocks even when `classify_line_detail` returns `ignore`. | `intent["blocking"]` holds it; `abort_reason` non-null | **RED.** `[ace1]` `plan_cutover` has no `intent` key at all today (row 11), so no class-conditional blocking rule exists to test. Behavioural harness: without the rule, this shape drops 1 of 5 live lines with `abort_reason: None`. |
| 26 **[new]** | `test_classification_that_misses_a_live_line_fails_closed` | `test_cron_apply.py` | A parse that does not account for every line of `current_text` returns `error` and aborts rather than planning over a partial record set. | `abort_reason` names the coverage failure | **RED.** `[ace1]` `classify_crontab_lines` does not exist on `main` (row 10), so there is no coverage guard to defeat; today `plan_cutover` plans over `before`+`after` only, which is #3709. |

**Score: 24 of 26 rows are genuinely RED on today's `main`. Rows 8 and 22 remain the two declared
GREEN guards, each with the measurement showing why it is necessary.** (v3: 20 RED / 2 GREEN of 22;
v2: 15 RED / 1 GREEN of 16.)

**Existing green gates that will be run and must stay green** — re-measured at `3fe934da9` on ace1,
unchanged from v3:

| Gate | Status today | Command |
|---|---|---|
| whole enforcement checker | GREEN, exit 0 | `[ace1] uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py` |
| generated HTML report | GREEN, exit 0 | `[ace1] … --check-html docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html` |
| identity inventory freshness | GREEN, exit 0 | `[ace1] uv run --with pyyaml python scripts/cron/build-cron-identity-inventory.py --check` |
| `test_classifier_branch_set_is_complete_and_exact` | GREEN, 30 passed | `[ace1] uv run pytest tests/enforcement/test_scheduler_mutation_surfaces.py -q` |
| `test_enforcement_modules_obey_size_limits…` | GREEN, 89 passed | `[ace1] uv run pytest tests/enforcement/test_scheduler_mutation_task3.py -q` |
| `test_llm_wiki_corpus_ingest_is_preserved` | GREEN, 7 passed | `[ace1] uv run pytest tests/cron/test_a1_preserved.py -q` |

**Local macOS note, carried from the r2 review:** `tests/enforcement/test_scheduler_mutation_surfaces.py`
fails on macOS on the non-UTF-8 filename fixture with `OSError: [Errno 92] Illegal byte sequence`, and
passes on ace1. The v4 prototype itself is pure `ast` and runs identically on both.

---

## Implementation Sequencing — delta from v3

Unchanged from v3 except that commit 4 now lands **two** enforcement modules and deletes the
prototype directory.

0. **Prerequisite — [#3711](https://github.com/vamseeachanta/workspace-hub/issues/3711) merged.**
   Blocking for commits 2-4 only. Unchanged from v3 FIX 2. #3711 is `OPEN` at `status:needs-plan`
   as of this writing; a plan for it is being drafted in parallel.
1. **Commit 1 — RED tests and fixtures only.** All 26 rows plus `tests/cron/fixtures/*` and
   `tests/enforcement/fixtures/*`. Neither `tests/` nor the fixtures are digest sources, so the gate
   stays green while 24 rows fail. **May land before #3711.** *Gate check:* checker exit 0.
2. **Commit 2 — context unification.** Unchanged from v3. Rows 3, 4, 9, 10 go green.
3. **Commit 3 — precedence + collision guard.** Unchanged from v3. Rows 6, 7 go green; row 8 stays green.
4. **Commit 4 — the fused quadruple.** `cron_transaction.py` records refactor **and**
   `scheduler_mutation_preservation.py` **and** `scheduler_mutation_preservation_closure.py` **and**
   the `attestations.py` dispatch, in one commit, never split — because the enforcement gate hard-errors
   in the intermediate state (`derive_status` → `migration-required` for `scripts/cron/cron_apply.py`,
   a hardcoded `resolved_dispositions` member at `scheduler_mutation_contract.py:307` that cannot be
   moved into a `disposition_group`). Rows 1, 2, 5, 11-19 and 23-26 go green. The prototype directory
   is deleted in this commit. Inventory + digest + HTML refresh.
5. Every commit ends with `check-scheduler-mutation-surfaces.py` and `--check-html` at exit 0, after
   `git add` (the checker reads the git index, not the worktree).

---

## Acceptance Criteria — delta from v3

v3's criteria carry forward. These are added or revised:

- [ ] **`python-postwrite-preservation-multiset-v1` will return `False` for the v3-r2 delegation
      counter-example and for all 26 named rejection cases, and `True` for the committed reference
      shape.**
- [ ] **Every terminal return of `plan_cutover` will be either an `_abort(...)` call or the single
      success dict, and every path to that dict will traverse the full classification → abort-guard →
      rebuild → intent → blocking-guard chain.**
- [ ] **The callee set, the assigned-name set and the module bindings of the inspected functions will
      be closed: no nested def, no decorator, no module-level or in-body rebinding of a pinned name.**
- [ ] **`_abort` will never report `abort_reason=None`.**
- [ ] **`classify_crontab_lines` will fail closed when its records do not account for every line of
      `current_text`, measured against a module-level `MARKER_PREFIXES` literal.**
- [ ] **An absent `managed`-location occurrence will block regardless of its class, including
      `ignore`.**
- [ ] **`NAMED_PREDICATES` will hold exactly 19 uniquely-named predicates, `NAMED_MUTATIONS` exactly
      26, and `ADMITTED_RESIDUE` exactly 4, all asserted by test.**
- [ ] **Both preservation modules will be ≤400 lines with every function ≤50 lines, will match no
      `PRIMITIVE_PATTERNS` entry, and will require no `FORENSIC` or `mutation-surfaces.yaml` change.**
- [ ] **The fixture sanitisation rule and the committed fixtures will agree: rule 4 will permit
      pre-existing host identifiers in `ignore`-class lines, and the README will enumerate the three
      that exist.**
- [ ] **`scripts/review/prototypes/3709-v4/` will be deleted in commit 4, its predicates having moved
      into the enforcement modules and its cases into `tests/enforcement/fixtures/`.**
- [ ] **#3711 will be merged before commit 2.** (unchanged)
- [ ] No implementation step will run `crontab` (write), `setup-cron.sh`, `cron_apply.py --apply`,
      `daily-cleanup.sh`, `repository_sync`, or `reconcile-ecosystem.sh --apply` on any host.
      (unchanged)

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Codex r2 on **v2** | **MAJOR** | (1) ordered AST attestation accepts a wrong implementation; (2) unenforceable ace1-only inventory constraint. Both answered in v3. |
| Codex r2 on **v3** | **MAJOR** | (1) the value-flow predicates still allow a non-abort early return that delegates to an uninspected helper; (2) fixture sanitisation rule contradicts the ace1 fixture; (3) the prototype was not committed, so the reviewer had to reimplement the contract. All three answered above. Everything else in v3 was independently verified and carries forward. |
| Author verification of **v4** (not a review) | n/a | Every claim above is produced by `scripts/review/prototypes/3709-v4/run.py` and `behaviour.py`, run on macOS and re-run byte-identically on `ace-linux-1`. Raw output in the verification log. |
| Independent r2 on **v4** | **REQUIRED — not yet run** | Must be an independent provider. The prototype is committed specifically so this review executes the same artifact. |

**Overall result:** pending independent r2. `status:plan-approved` will not be applied by any agent.

### v3 → v4 delta

1. **D5 rewritten again: 12 new predicates close the delegation route.** The reviewer's counter-example
   is committed verbatim and measured `False` on two named predicates where v3 scored `True` on all
   seven. The closure group (8, 10, 11, 13) makes "the helper set is closed" a checked claim rather
   than a naming convention.
2. **Six further evasions were constructed by the author.** Four were closed by predicate. Two were
   not closable by shape and forced changes to the implementation the plan specifies: the totality
   guard's expected set must come from a module literal (E11/E12), and a managed-block absence must
   block even when classified `ignore` (E13). E13 is #3709's own defect reachable through the
   classifier, and **v3's design would have shipped it**.
3. **The residue is four enumerated shapes, each with one named covering test**, replacing v3's four
   diffuse compensating controls. v3's residue R2 is closed outright; R1 and R3 survive as accepted
   shapes but are measured **non-destructive** under the v4 reference shape.
4. **A behavioural harness was added** so "accepted by the attestation" and "loses live lines" are
   separate, measured columns rather than an argument.
5. **The module budget changed:** 641 prototype lines will not fit one 400-line module, so the
   predicate set ships as two siblings (≈360 + ≈290), both still free of `PRIMITIVE_PATTERNS` matches.
6. **Sanitisation rule 4 amended, fixtures untouched** — rebaselining would destroy the ace1 fixture's
   byte-equality with live `crontab -l`, which is the property the r2 reviewer used to verify it.
7. **The prototype is committed**, so the next review runs the same artifact instead of its own
   reading of the contract.
8. **Four new TDD rows and three revised**; score improves from 20 RED / 2 GREEN of 22 to
   24 RED / 2 GREEN of 26.

---

## Risks and Open Questions

- **Risk (carried):** deleting `catalog_commands` would break `derive_cron_classifier_branches`.
  Deferred; independently reproduced by two reviewers.
- **Risk (carried):** `build_ownership_context` stays as a delegating wrapper, so a future caller could
  bypass the new context object. Row 4's AST scan covers all tracked cron consumers.
- **Risk (carried):** the intent report's multiset comparison is over raw line strings; no
  normalization will be added.
- **Risk (carried):** the acknowledgement digest binds to the whole baseline, so any concurrent crontab
  change invalidates every key. Intended, but operationally noticeable.
- **Risk (carried):** #3711 is `status:needs-plan`, so commits 2-4 are gated on an issue that has no
  merged plan yet.
- **Risk (carried):** the fixtures are point-in-time captures and will drift from live ace1/ace2 state.
- **Risk (new):** nineteen predicates over seven functions make the destructive core
  refactor-hostile by design. Any legitimate refactor becomes a review trigger. A reviewer who thinks
  the ratio is wrong should say so before approval; the reduction available is to drop predicates 15,
  16 and 17, which costs the closure of E09, E10 and E11 and re-opens RES-2 as a data-loss path.
- **Risk (new):** the residue is four *measured* shapes, not a proof of exhaustiveness. Six author
  attempts and one reviewer attempt found nothing further, which bounds confidence, not correctness.
- **Risk (new):** predicate 19 changes observable behaviour — a managed-block comment or env line that
  the regenerated block does not reproduce will now block a cutover that v3's design would have
  allowed. This is deliberate (it is the E13 fix) but it will make the first real cutover noisier.
  The escape hatch is the existing occurrence-scoped `--acknowledge-absent`, not a class exemption.
- **Open (resolved from v3):** "should `ignore` lines block?" — v3 left this to the reviewer. v4
  resolves it: `ignore` absences in `before`/`after` do not block (the rebuild retains them anyway);
  `ignore` absences in `managed` **do** block (the rebuild always drops them). Measured as case E13.
- **Open (carried):** should #3708's premise be restated in that issue once this lands?
- **Open (carried):** whether ace2 convergence belongs to #3709 or #3708 remains an owner decision.

---

## Complexity: T3

**T3** — unchanged. The change crosses a scheduler-mutation safety contract, two consumer CLIs, the
destructive classifier, the attestation that guards the reconstruction, a digest chain with a
host-dependent generator, **two** new enforcement modules, and a generated HTML audit. Implementation
remains blocked until user approval **and** until #3711 is merged.
