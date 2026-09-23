# Plan for #3709 (v3): Managed-Block Classification Before Cron Cutover

> **Status:** plan-review
> **Complexity:** T3
> **Date:** 2026-07-30
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3709
> **Client:** N/A
> **Lane:** lane:claude
> **Supersedes:** `docs/plans/2026-07-30-issue-3709-managed-block-classification-v2.md` on
> `plan/3709-managed-block-classification-v2` (independent Codex r2 verdict **MAJOR**, 2 major findings)
> **Blocking dependency:** [#3711](https://github.com/vamseeachanta/workspace-hub/issues/3711) must
> land before commit 2 of this plan. See FIX 2.
> **Review artifacts:** `scripts/review/results/2026-07-30-plan-3709-v3-verification-log.md` (author
> verification log, not a review); independent r2 adversarial review REQUIRED before any approval

---

## Tense convention

Every statement about **work this plan proposes** is written in future tense. The `Evidence` and
`Today's status` columns are **measurements**, written as measurements with the command that produced
them. A measurement written in the future tense is unverifiable, which is how the v1 plan shipped
three false RED claims.

**Every measurement below was produced on `ace-linux-1` (`dev-primary`,
`/mnt/local-analysis/workspace-hub`, HEAD `3fe934da9` = `origin/main`) on 2026-07-30**, except where
marked `[mac]`. Probe scripts ran from `/tmp/v3probe` on ace1 and were never written into the repo.
Raw output is in the verification log.

---

## Scope of this revision

v3 is a **targeted revision** of v2, not a re-plan. v2's design was independently reproduced and
confirmed by the Codex r2 reviewer on four points, all of which **carry forward unchanged**:

| Carried forward from v2 | Independent confirmation |
|---|---|
| Keeping the dead `catalog_commands` / `external_fingerprints` parameters in `classify_line_detail`. Deleting them makes `derive_cron_classifier_branches` return `None` and flips three surfaces to `migration-required`. | Reproduced by r2 on ace1: rewriting the preserved return to read from `ownership_context` returned `None`; one extra `{"class": "cataloged"}` literal also returned `None`. |
| **Third-party-first** ordering (not blanket preservation-first). | Reproduced by r2 for the safety half (injected llm-wiki legacy line → `preserved_external` under the refined order). The parity counts r2 could not rerun are now measured offline from the committed fixture: blanket = **69/71**, third-party-first = **71/71**. |
| `build_classification_context` as the single seam; `plan_cutover(current_text, classification_context, *, acknowledged=())`. | r2: "The v2 seam is substantially better than v1 … I did not find a separate MAJOR in the seam design itself." |
| Rejecting a behavioural attestation (the checker builds `records` from git-index blobs). | Not contested. |
| No new attestation name, so `scheduler_mutation_contract.py` stays at exactly 400 lines. | Re-measured: contract = 400 lines, `ATT_SOURCES` = 37 entries. |

Design sections **D1, D2, D3, D4 and D6 of v2 are adopted verbatim** and are not restated here except
where a measurement changed. This document rewrites **D5** (the attestation), adds **D7** (the
inventory host dependency) and **D8** (the crontab fixtures), and republishes the full TDD table
because every row's numbering and proving command changed.

---

## FIX 1 (r2 MAJOR 1) — D5 rewritten: a value-flow predicate set

### The finding, reproduced

r2 constructed an implementation that satisfies **v2's entire ordered-predicate set while being
wrong**: it classifies zero records, hides the required retention code in dead branches, returns only
the rendered managed block, and reports no blocking intent.

v2's published predicate spec was implemented literally and run against that counter-example. r2's
result reproduces exactly:

```
v2 spec on HONEST implementation : {'order': True, 'all_locations': True, 'retention': True, 'shape': True}
v2 spec on COUNTEREXAMPLE        : {'order': True, 'all_locations': True, 'retention': True, 'shape': True}
```

Every ordering predicate present; none of the behaviour. That violates
`.claude/rules/scheduler-mutation-safety.md`'s "failed source attestations must fail closed" — the
attestation can certify unsafe code. **Sequence assertions are insufficient.**

### The counter-example, written out

This is the exact shape the v3 predicate set must reject. It will be committed **verbatim** as a
permanent test fixture (row 17), so no future weakening of the predicate set can pass unnoticed:

```python
def classify_crontab_lines(current_text, classify_detail):
    parsed = parse_crontab(current_text)
    if False:
        for location in ('before', 'managed', 'after'):
            for index, line in enumerate(parsed[location]):
                records.append({'location': location, 'index': index, 'line': line,
                                'detail': classify_detail(line)})
    return {'parsed': parsed, 'records': [], 'error': None}


def _fallback_records(current_text, classify_detail):
    return []


def plan_cutover(current_text, classification_context, *, acknowledged=()):
    classify_detail = _detail_classifier(classification_context)
    selected_tasks = classification_context['selected_tasks']
    roles = classification_context['roles']
    classified = classify_crontab_lines(current_text, classify_detail)
    if classified['error']:
        return _abort(classified['error'], [], None)
    uncataloged = [r for r in classified['records'] if r['detail']['class'] == 'uncataloged']
    if uncataloged:
        return _abort(f'uncataloged live cron line(s): {uncataloged}', uncataloged, None)
    block = render_block(selected_tasks, roles)
    new_lines = _rebuild_from_records(classified['parsed'], classified['records'], block)
    intent = build_cutover_intent(classified['records'], new_lines, acknowledged)
    if intent['blocking']:
        return _abort('planned crontab would omit live line(s)', [], intent)
    return {'new_text': '\n'.join(block), 'preserved': [], 'uncataloged': [],
            'conflicts': [], 'intent': intent, 'abort_reason': None}


def _rebuild_from_records(parsed, records, block):
    before = [r['line'] for r in records
              if r['location'] == 'before' and r['detail']['class'] != 'cataloged']
    after = [r['line'] for r in records
             if r['location'] == 'after' and r['detail']['class'] != 'cataloged']
    if parsed.get('roles') is None:
        return before + block
    if False:
        return before + block + after
    return block


def build_cutover_intent(records, new_lines, acknowledged=()):
    return {'absent': [], 'added': [], 'blocking': []}
```

### D5 — the v3 predicate set

**Recommendation: assert the property as an ordered predicate set with value-flow assertions, built
on the repository's existing reachability engine.** The behavioural-attestation and verbatim-token
alternatives stay rejected for v2's reasons.

**Key structural decision — reuse `scheduler_mutation_python_flow._walk_block`.**
`scripts/enforcement/scheduler_mutation_python_flow.py:15-62` already enumerates live control-flow
paths and already eliminates `if <constant>` dead branches (`:40-42`). v2 did not use it and that is
precisely why v2's predicates were fooled by `if False:`. Every v3 path-based predicate will be
expressed over `_walk_block`, so dead-branch elimination is inherited from an engine that is already
under test rather than reimplemented.

That engine deliberately discards loop-body evidence (`:57-60`: "transaction guarantees must be
established outside ambiguous loops"). v3 will respect that invariant: the loop-body predicate below
is a **shape** claim ("if the loop runs, every iteration appends"), never a claim that the loop runs.

**`python-postwrite-preservation-multiset-v1` will be redefined as the conjunction of seven named
predicates**, all of which must hold:

```python
def preservation_shape(tree) -> bool:
    return bool(tree) and all(predicate(tree) for _name, predicate in NAMED_PREDICATES)
```

| # | Predicate | Assertion | Kind |
|---|---|---|---|
| 1 | `plan-cutover-order` | `_ordered_indices(plan_cutover.body, P)` for the eight-step `P` of v2 D5, with step 3 strengthened from a substring test to a structural one: the `uncataloged` value must be a comprehension whose **iterator unparses to exactly `classified['records']`** and whose condition contains `r['detail']['class'] == 'uncataloged'`. | ordering |
| 2 | `plan-cutover-result-flow` | Every live path of `plan_cutover` ends in a `Return`; exactly **one** distinct terminal return is a `Dict`; in it `'new_text'` → `Name('new_text')`, `'intent'` → `Name('intent')`, `'abort_reason'` → `Constant(None)`; and some live statement assigns `new_text` from an expression containing `new_lines`. | value-flow |
| 3 | `render-block-called-once` | `render_block` is called exactly once across all live paths of `plan_cutover`. | value-flow |
| 4 | `classify-populates-records` | The statement `for location in ('before', 'managed', 'after'):` lies on **every** live path of `classify_crontab_lines`; that loop contains exactly one inner `for … in enumerate(parsed[location])`; a record `append` carrying all of `'location'`, `'index'`, `'line'`, `'detail'` and a `classify_detail(` call is an **unconditional direct child** of the inner loop body; and every distinct terminal return binds `'records'` to a `Name` that is either the appended variable or `fallback_records` — never a list literal. | value-flow |
| 5 | `fallback-records-populated` | Every live path of `_fallback_records` ends in a `Return`; no terminal return is an empty list/tuple literal or a bare constant; and the live text contains `classify_detail(` and `'unparsed'`. | value-flow |
| 6 | `rebuild-retention` | In `_rebuild_from_records`, `before` and `after` are assigned comprehensions over `records` filtering `r['location'] == '…'` and `r['detail']['class'] != 'cataloged'`; every live path ends in a `Return`; and the set of distinct terminal return expressions is **exactly** `{"before + block", "before + block + after"}`; every path terminating in `before + block` passes through an `if` whose test is `parsed['roles'] is None`. | value-flow |
| 7 | `intent-derives-blocking` | In `build_cutover_intent`, `absent` is a comprehension whose iterator mentions `records`; `blocking` is a comprehension **over `absent`** whose condition contains both `!= 'ignore'` and `not in acknowledged`; every live path ends in a `Return`; and every distinct terminal return binds `'blocking'` → `Name('blocking')` and `'absent'` → `Name('absent')`. | value-flow |

The four assertions the brief demanded map onto predicates 1/4 (classified records reach the abort
decision), 4/6 (retention and classification are on live paths, not dead branches), 2/6 (the returned
value composes `before + block + after`, not `block` alone) and 7 (the intent report is derived from
the classification, not constructed empty).

**Exact-set equality in predicate 6 is the load-bearing idea.** `{unparse(r) for r in terminal
returns} == {"before + block", "before + block + after"}` cannot be satisfied by addition (any extra
live return breaks equality) nor by concealment (hiding a return in a dead branch removes it from the
set). v2's `"return before + block + after" in text` was satisfiable by both.

### Proof that the v3 set rejects the counter-example

Executed on ace1 against a prototype of the module (never written into the repo):

```
v3 predicate set on HONEST implementation : True
v3 predicate set on COUNTEREXAMPLE        : False
  per-predicate on the counter-example:
    plan-cutover-order          True     <-- v2 stopped here
    plan-cutover-result-flow    False
    render-block-called-once    True
    classify-populates-records  False
    fallback-records-populated  False
    rebuild-retention           False
    intent-derives-blocking     False
```

The counter-example is rejected on **four independent predicates**. `plan-cutover-order` — the whole
of v2's ordering evidence — still returns `True`, which is the clearest statement of why ordering
alone was never sufficient.

### The mutation battery

**Fifteen named mutations plus the counter-example**, each of which must return `False`. All sixteen
were executed against the prototype; the honest baseline returns `True`.

| Id | Mutation | v2 spec | v3 set |
|---|---|---|---|
| M1 | `for location in ('before', 'managed', 'after'):` → `('before', 'after')` | False | **False** |
| M2 | delete the `if uncataloged: return _abort(...)` guard | False | **False** |
| M3 | hoist `block = render_block(...)` above `classified = classify_crontab_lines(...)` | False | **False** |
| M3b | add a **decoy** `block0 = render_block(...)` above the classification | **True** | **False** |
| M4 | `before = [ … 'before' … ]` → `before = []` | False | **False** |
| M5 | `return before + block + after` → `return before + block` | False | **False** |
| M6 | delete the `if intent['blocking']: return _abort(...)` guard | False | **False** |
| M7 | delete the `if classified['error']: return _abort(...)` guard | False | **False** |
| M8 | dead all-locations loop, `records: []` returned *(r2)* | **True** | **False** |
| M9 | dead `return before + block + after`, live `return block` *(r2)* | **True** | **False** |
| M10 | vacuous `build_cutover_intent` returning empty literals *(r2)* | **True** | **False** |
| M11 | `_fallback_records` returns `[]` | **True** | **False** |
| M12 | success return emits `'\n'.join(block)` instead of `new_text` | **True** | **False** |
| M13 | the record append is made conditional (`if line.strip():`) inside the inner loop | **True** | **False** |
| M14 | `_rebuild_from_records(classified['parsed'], [], block)` | False | **False** |
| MX | the full r2 counter-example above | **True** | **False** |

```
v3 accepts baseline                 : True
v3 mutations NOT rejected           : none — all 16 rejected
v2 mutations NOT rejected           : M3b, M8, M9, M10, M11, M12, M13, MX  (8 of 16)
```

### Closing v2's admitted M3 hole

v2 admitted that M3 "only flips when written as a true statement hoist — an added decoy
`block0 = render_block(...)` does not trip `_ordered_indices`". **v3 closes it**, by predicate 3
(`render-block-called-once`). M3b now measures `False`.

Recorded for completeness: even before predicate 3, the decoy was *safety-inert*, because predicate 1
pins the `_rebuild_from_records` call's argument list to exactly
`(classified['parsed'], classified['records'], block)` — a decoy that is actually **used** fails
predicate 1, and a decoy that is unused changes no behaviour. Predicate 3 closes the inert case as
well, at a cost of three lines, so the hole is not left open on an argument.

### Honest statement: this class cannot be fully closed by AST shape

**No. An AST-shape attestation can never fully close this class, and v3 does not close it.**

The attestation is a syntactic predicate over source text; the property wanted — "no live crontab line
is dropped without an abort" — is a semantic property of the executed program. Any syntactic
approximation of a non-trivial semantic property must be either unsound (accepts some bad programs)
or incomplete (rejects some good ones). Enforcement here must not reject legitimate refactorings, so
the choice is forced toward unsoundness. Concretely, **three residual shapes were constructed and
measured; the v3 predicate set returns `True` for all three**:

```
R1  _detail_classifier returns {'class': 'cataloged'} for every line   -> v3 attestation = True
R2  _abort(...) returns abort_reason=None                              -> v3 attestation = True
R3  parse_crontab mis-partitions every line into 'before'              -> v3 attestation = True
```

R1 deletes every live line while every predicate passes. The predicate set pins **names, shapes and
value flow between the four named functions**; it has no view into `_detail_classifier`, `_abort`, or
`parse_crontab`. Widening it to cover those would require the attestation to model the whole module,
at which point it stops being reviewable — which was the original objection to a verbatim token list.

**Compensating controls for the residue.** The plan will not claim the attestation carries
`scheduler-mutation-safety.md`'s fail-closed clause on its own. That clause will be carried
**jointly** by the attestation and the following, each of which is a required deliverable:

1. **Behavioural tests are the actual safety proof.** Rows 1, 2, 11, 12, 14 and 20 execute
   `plan_cutover` and `build_cutover_intent` against the committed ace1 and ace2 crontab fixtures and
   assert the abort, the record count and the intent contents. R1, R2 and R3 above all fail those
   tests immediately. The attestation's narrower job is to prevent **silent structural regression** of
   code the tests already prove correct.
2. **The counter-example is a permanent fixture** (row 17). Any future edit that would re-admit MX
   turns that test red.
3. **The predicate set cannot be silently thinned** (row 18). `NAMED_PREDICATES` and the mutation
   table will be module-level tuples, and a test will assert `len(NAMED_PREDICATES) == 7` and
   `len(NAMED_MUTATIONS) == 16`. Deleting a predicate or a mutation is then a red test, not an
   invisible one-token diff.
4. **Review gate.** This plan records that the attestation is a *regression tripwire, not a proof*.
   Any future change that removes a named predicate or a named mutation will require an independent
   adversarial review, and that sentence will be carried into the module docstring.

### Module placement — a measured constraint v2 did not face

`scripts/enforcement/scheduler_mutation_attestations.py` is **317** lines against the enforced
**400**-line ceiling (`tests/enforcement/test_scheduler_mutation_task3.py:274-288`, which also caps
every function at 50 lines). The v3 predicate module measures **293 lines**; folding it into
`attestations.py` would land at roughly 593 and break the ceiling.

The predicate set will therefore ship as a new sibling module
**`scripts/enforcement/scheduler_mutation_preservation.py`**, following the existing precedent of
`scheduler_mutation_python_flow.py` (180 lines, imported by `attestations.py`).
`attestations.py` will lose `_preservation_shape` (17 lines incl. separators) and gain an import plus
a one-line dispatch, landing near 302. Import order is acyclic:
`attestations → preservation → python_flow`.

Measured, so the implementer is not surprised:

```
candidate module lines            : 293      (ceiling 400)
functions over 50 lines           : none     (largest = 26)
size test globs scheduler_mutation*.py, so the new module is covered automatically
required-module set in that test  : {report.py, delegation.py} — unchanged by an addition
```

**Surface-discovery constraint.** `discover_mutation_surfaces`
(`check-scheduler-mutation-surfaces.py:136-176`) scans every tracked `scripts/**/*.py`, and a file
matching any `PRIMITIVE_PATTERNS` entry becomes a `direct` surface, which would raise
`direct inventory mismatch` unless registered. `scheduler_mutation_attestations.py` matches two
Windows primitives today and is exempt only because it is a member of the `FORENSIC` set
(`:59-60`) with `# scheduler-mutation-forensic` sentinels on the matching lines. The candidate
module was scanned:

```
v3 predicate module   : direct_primitives=[]  alias=False  known_call=None
attestations.py (ctl) : direct_primitives=['windows-task-set', 'windows-task-unregister-register']
```

Zero matches, so **no `FORENSIC` change and no `mutation-surfaces.yaml` entry will be required**. The
plan pins the constraint: if any predicate line ever matches a `PRIMITIVE_PATTERNS` regex, the module
must be added to `FORENSIC` and carry the sentinel comment in the same commit.

`ATT_SOURCES` will gain no entry and `scheduler_mutation_contract.py` will stay at exactly 400 lines.

---

## FIX 2 (r2 MAJOR 2) — the ace1-only inventory constraint

### The finding

v2 required commits 2-4 to be authored on ace1 because `build-cron-identity-inventory.py --check`
exits 0 there and 1 on macOS (#3711), and admitted CI cannot enforce it. The failure is **silent**:
`_validate_inventory_digest` (`scheduler_mutation_delegation.py:112-123`) hashes only the eight
configured **source** files, so a Mac-authored commit can publish wrong `identities` rows carrying a
correct `input_digest`, and the enforcement checker passes it. An unenforceable process constraint
guarding a destructive path is not a control.

### Root cause, measured

The host dependence is `cron_render.workspace_hub_path` (`cron_render.py:87`):
`Path(override).expanduser().resolve()`. `build-cron-identity-inventory.py:96-100` feeds it each
Linux machine's declared `workspace_root` from `registry.yaml`. On macOS `/home` is an autofs mount
that `.resolve()` rewrites. Measured on both hosts:

```
[ace1] gpu-claw  declared=/home/undi/ws/workspace-hub
                 resolved=/home/undi/ws/workspace-hub                              faithful=True
[mac]  gpu-claw  declared=/home/undi/ws/workspace-hub
                 resolved=/System/Volumes/Data/home/undi/ws/workspace-hub          faithful=False

[ace1] all four registry Linux machines: faithful=True
[mac]  dev-primary/dev-secondary faithful=True, gpu-claw faithful=False
```

`gpu-claw` alone is poisoned, which is exactly the near-miss #3711 was filed for.

### Decision: **(a) — sequence #3711 as a hard blocking prerequisite of #3709**

Justification, in order of weight:

1. **(a) removes the constraint; (b) only guards it.** #3711's primary required remedy is to resolve
   workspace roots from `registry.yaml` as declared data rather than by touching the filesystem. Once
   that lands, the inventory is a pure function of the eight digest-source bytes, generation is
   byte-identical on every POSIX host, `--check` exits 0 on the Mac, and **the ace1-only authorship
   requirement disappears entirely**. There is nothing left to bypass. Even #3711's fallback remedy
   (fail closed when the host cannot faithfully render another machine's root) converts the silent
   failure into a loud non-zero exit, which is the property r2 asked for.
2. **(b) would be #3711's work done under #3709's number.** Every in-issue detection worth having
   lives in `build-cron-identity-inventory.py` or `cron_render.workspace_hub_path` — the two files
   #3711 is scoped to change. Implementing it here means writing code that #3711 will immediately
   rewrite, with a guaranteed conflict on a digest-source file.
3. **The strongest form of (b) is out of budget.** A genuine identity-row content assertion requires
   the enforcement checker to regenerate the inventory from **git-index bytes**, but
   `build-cron-identity-inventory.build()` reads from filesystem `Path`s. Refactoring it to consume
   parsed records is strictly larger than #3711 and would blow this plan's T3 budget.
4. **(a) is cheap.** The guard predicate is already validated by the measurement above — one
   comparison per Linux machine — so #3711 is a small issue, and sequencing it first costs little.

**This will be stated as a blocking dependency in the plan header and posted on both issues.**
Commit 1 of this plan (RED tests only) may land before #3711, because `tests/cron/*` and
`tests/enforcement/*` are not digest sources. Commits 2-4 will not begin until #3711 is merged.

### Compensating control while the dependency is open

Because sequencing is itself a process promise, one cheap in-issue tripwire will ship in commit 1, in
`tests/cron/` (not a digest source, no conflict with #3711):

`test_identity_inventory_host_can_render_every_linux_root` will assert that the host running the
tests resolves every registry Linux `workspace_root` to itself, and will name the offending machine
and cite #3711 when it does not. It is **declared GREEN on ace1** and RED on macOS by construction —
a tripwire, not a change-proof, counted as such in the TDD table (row 22).

### Residue, stated honestly

Even with #3711 merged, `_validate_inventory_digest` still validates the inventory's **inputs**, not
its **contents**. A hand-edited `identities` array carrying a correct `input_digest` still passes the
checker. That hole exists on `main` today, is not created or widened by #3709, and is **not closed by
this plan**. It will be filed as a follow-on ("enforcement checker must regenerate the identity
inventory from index bytes and compare") rather than claimed as resolved.

---

## FIX 3 — D8: committed crontab fixtures

### The gap

Rows 1, 12 and 14 of v2 proved themselves only against live ace1 state via `crontab -l`. No ace1
crontab fixture exists on `main`:

```
$ [ace1] ls tests/cron/fixtures      -> No such file or directory
$ [ace1] git ls-files | grep -i crontab
config/agents/claude/memory-snapshots/…   docs/reports/2026-04-15-issue-2292-installed-crontab-probe.md
scripts/coordination/productivity/crontab.example      scripts/cron/crontab-template.sh
```

None is an ace crontab capture. The r2 reviewer could not rerun rows 1, 12 and 14 for exactly this
reason, and neither can any future reviewer.

### Sanitisation rule

The rule is stated as a **gate with a precedence order**, because a fixture that lies about its own
classification is worse than no fixture.

1. **Classification-load-bearing bytes are preserved verbatim.** Every byte that can change
   `classify_line_detail`'s output — the whole of every non-comment cron line, and both managed-block
   markers — is copied exactly. In particular `/mnt/local-analysis/workspace-hub` is **not** rewritten:
   it is the `workspace_root` that `registry.yaml` already declares publicly, and every
   `canonical-exact-line` identity match depends on it.
2. **Redaction is permitted only where it cannot change a class.** The single permitted rewrite is
   **user home directories** → `$HOME` (regex `/home/(?!linuxbrew/)[A-Za-z0-9._-]+`), which is
   semantically identical under cron and is already the dominant style in the same crontabs. Well-known
   **system** accounts are exempt by name (`linuxbrew`) because they are not user-identifying.
3. **Secret-shaped content is a rejection, not a redaction.** A deny-scan runs for `MAILTO=`,
   `*TOKEN|SECRET|PASSWORD|API_KEY|ACCESS_KEY=`, `Bearer <token>`, `ghp_`/`github_pat_`, `sk-`/`sk-ant-`,
   `AKIA…`, `AIza…`, `xox[abprs]-`, PEM private-key headers, e-mail addresses, IPv4 literals and
   `ssh|scp|rsync user@host`. **If any pattern matches, the capture is aborted and no fixture is
   committed**, because redacting a match would alter the redacted line's class.
4. **Provenance lives in a sidecar, never in the fixture.** Rows 12 and 14 assert exact
   `(location, index)` pairs, so a header comment inside the fixture would shift every index. Host,
   machine id, capture date, line count and deny-scan result go in
   `tests/cron/fixtures/README.md`.
5. **Class-preservation is verified, not assumed.** Every fixture is classified before and after
   redaction and the full `(location, index, class)` sequence must be identical (row 21).

### Measured result of applying the rule

```
ace1: 73 lines, 15593 bytes   deny-scan matches: 0   redactions: 0
      -> committed byte-identical to `crontab -l`
ace2: 40 lines,  6850 bytes   deny-scan matches: 4   (/home/linuxbrew x1 exempt, /home/<user> x3)
      -> 3 redactions to $HOME; residual /home hits: ['/home/linuxbrew'] (exempt by rule 2)
      SANITISATION CLASS-PRESERVING: True   (40/40 identical (location, index, class))
```

The ace1 capture required **zero** redactions. The rule is therefore a gate the capture passed, not a
transformation applied — stated plainly so a reviewer does not assume the fixture was rewritten.

### Fixture classification, measured

```
ace1 (dev-primary)   73 lines   before=11 managed=51 after=9  error=None roles=control-plane
   by class       : {cataloged: 11, ignore: 12, preserved_external: 1, uncataloged: 47}
   by (loc,class) : before:ignore=10  before:preserved_external=1
                    managed:cataloged=4  managed:uncataloged=47
                    after:cataloged=7   after:ignore=2

ace2 (dev-secondary) 40 lines   before=14 managed=14 after=10 error=None roles=comms-dispatch+sim-worker
   by class       : {cataloged: 3, ignore: 15, preserved_external: 9, uncataloged: 11}
   by (loc,class) : before:ignore=10  before:preserved_external=4
                    managed:cataloged=3  managed:uncataloged=11
                    after:ignore=5      after:preserved_external=5
```

The ace1 figures reproduce v2's M1 exactly. **v2's M9 explicitly declined to verify the ace2
breakdown; v3 verifies it** — 40 lines, role `comms-dispatch+sim-worker`, 9 `preserved_external`, and
3 of 14 managed lines cataloged by identity, all confirmed. (v2's `cron-audit` figure of
`ignore: 15` for ace1 versus 12 here is the audit's own defect, not a discrepancy: `audit_crontab`
iterates `crontab_text.split("\n")` and counts the two marker lines and the trailing blank, which
have no location. That divergence is what D1 removes.)

### Rows re-pointed at the fixture

Rows 1, 12 and 14 will be re-pointed at `tests/cron/fixtures/ace1-crontab-2026-07-30.txt`. All three
today-statuses were re-measured **from the fixture file, offline, with no `crontab -l`**, and are
reproducible by any reviewer on any Linux host. Row 8's parity claim, which r2 could not rerun, is
likewise now fixture-based.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-30-issue-3709-managed-block-classification-v3.md` |
| Author verification log | `scripts/review/results/2026-07-30-plan-3709-v3-verification-log.md` |
| Superseded v2 plan | `docs/plans/2026-07-30-issue-3709-managed-block-classification-v2.md` |
| Independent r2 review being answered | `scripts/review/results/2026-07-30-plan-3709-v2-codex-r2.md` |
| Independent plan review (r2, required) | `scripts/review/results/2026-07-30-plan-3709-v3-<provider>-r2.md` |
| ace1 crontab fixture | `tests/cron/fixtures/ace1-crontab-2026-07-30.txt` (new, this branch) |
| ace2 crontab fixture | `tests/cron/fixtures/ace2-crontab-2026-07-30.txt` (new, this branch) |
| Fixture provenance sidecar | `tests/cron/fixtures/README.md` (new, this branch) |
| Attestation counter-example fixture | `tests/enforcement/fixtures/preservation_counterexample.py` (new) |
| Attestation honest-shape fixture | `tests/enforcement/fixtures/preservation_reference.py` (new) |
| Preservation predicate module | `scripts/enforcement/scheduler_mutation_preservation.py` (new) |
| Context-unification tests | `tests/cron/test_cron_classification_context.py` (new) |
| Audit fail-closed tests | `tests/cron/test_cron_audit_fail_closed.py` (new) |
| Fixture integrity + host tripwire tests | `tests/cron/test_cron_fixtures.py` (new) |
| Transaction tests | `tests/cron/test_cron_apply.py` |
| Preservation precedence tests | `tests/cron/test_a1_preserved.py` |
| Attestation tests | `tests/enforcement/test_scheduler_mutation_task3.py` |
| Classification context authority | `scripts/cron/cron_identity.py` |
| Classifier authority | `scripts/cron/cron_line_model.py` |
| Transaction | `scripts/cron/cron_transaction.py` |
| Audit CLI | `scripts/cron/cron-audit.py` |
| Apply wrapper | `scripts/cron/cron_apply.py` |
| Attestation dispatch | `scripts/enforcement/scheduler_mutation_attestations.py` |
| Reachability engine (reused) | `scripts/enforcement/scheduler_mutation_python_flow.py` |
| Mutation surface registry | `config/scheduled-tasks/mutation-surfaces.yaml` |
| Identity inventory | `docs/reports/issue-3475-command-identity-inventory.json` |
| Generated safety report | `docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html` |
| Plan index | `docs/plans/README.md` |

---

## Deliverable

One classification context, built in one place, consumed by both `cron-audit.py` and `plan_cutover`;
a records-based transaction that will classify **every** live line — `before`, `managed` and `after` —
before any rebuild and will abort on any uncataloged record regardless of location; an intent report
that will enumerate **every** baseline occurrence absent from the planned crontab with **no class
exempt**, blocking unless an occurrence-scoped digest acknowledges it; and a scheduler-mutation
attestation that will assert that reconstruction by **value flow on live paths**, not by statement
order alone — proven against a committed counter-example that today's design accepts.

---

## Files to Change

Unchanged from v2 except where marked **[v3]**.

| Action | Path | Reason |
|---|---|---|
| Create **[v3]** | `tests/cron/fixtures/ace1-crontab-2026-07-30.txt` | Sanitised ace1 capture, 73 lines. Committed on this plan branch so rows 1, 8, 12, 14 are reproducible offline. |
| Create **[v3]** | `tests/cron/fixtures/ace2-crontab-2026-07-30.txt` | Sanitised ace2 capture, 40 lines, role `comms-dispatch+sim-worker`. |
| Create **[v3]** | `tests/cron/fixtures/README.md` | Provenance + sanitisation rule + deny-scan result. Kept out of the fixtures so indices do not shift. |
| Create **[v3]** | `tests/enforcement/fixtures/preservation_reference.py` | The honest records-based shape the attestation must accept. |
| Create **[v3]** | `tests/enforcement/fixtures/preservation_counterexample.py` | The r2 counter-example, verbatim, permanent. |
| Create **[v3]** | `scripts/enforcement/scheduler_mutation_preservation.py` | The seven named predicates + `NAMED_MUTATIONS`. 293 lines measured, under the 400 ceiling; every function ≤ 50 lines. |
| Create **[v3]** | `tests/cron/test_cron_fixtures.py` | Rows 20, 21, 22 — fixture classification, sanitisation class-preservation, host-fidelity tripwire. |
| Create | `tests/cron/test_cron_classification_context.py` | Rows 3, 4, 5. |
| Create | `tests/cron/test_cron_audit_fail_closed.py` | Rows 9, 10. |
| Modify | `tests/cron/test_cron_apply.py` | Rows 1, 2, 11, 12, 13, 14. |
| Modify | `tests/cron/test_a1_preserved.py` | Rows 6, 7, 8. |
| Modify **[v3]** | `tests/enforcement/test_scheduler_mutation_task3.py` | Rows 15-19 — new shape, 16-entry mutation battery, arity guard, module size. The four existing mutation strings are the OLD source text and must be replaced in the same commit. |
| Modify | `scripts/cron/cron_identity.py` | Add `build_classification_context`; split third-party vs catalog fingerprints; preservation collision guard; keep `build_ownership_context` as a delegating wrapper. |
| Modify | `scripts/cron/cron_line_model.py` | Precedence reorder ONLY. Signature, the single `{'class': 'cataloged'}` literal and the `return _classify_preserved(line, external_fingerprints)` token preserved verbatim. |
| Modify | `scripts/cron/cron_transaction.py` | `classify_crontab_lines`, `_fallback_records`, `_rebuild_from_records`, `build_cutover_intent`; `plan_cutover` takes the context + `acknowledged`; delete `_classify_nonmanaged` and `_rebuild_lines`. |
| Modify | `scripts/cron/cron-audit.py` | Consume the shared context and shared records; parse-error fail-closed exit; delete the independent classification loop and the second fingerprint load. |
| Modify | `scripts/cron/cron_apply.py` | `_load_cutover_context` returns the shared context; `--acknowledge-absent` CLI; surface `intent`; stop passing `external_fingerprints`. |
| Modify **[v3]** | `scripts/enforcement/scheduler_mutation_attestations.py` | Delete `_preservation_shape`; import and dispatch `preservation_shape` from the new module. Net ≈ 302 lines. NO new attestation name. |
| Modify | `docs/reports/issue-3475-command-identity-inventory.json` | Regenerate — digest covers `cron_transaction.py`, `cron_line_model.py`, `cron_identity.py`. |
| Modify | `config/scheduled-tasks/mutation-surfaces.yaml` | Refresh `resolved_dispositions[0].source_digest` to the new `input_digest`. No attestation list change, no new surface row. |
| Modify | `docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html` | Regenerate via `--render-html`. |
| Modify | `docs/plans/README.md` | Index this plan; mark v2 superseded. |

**Not changed:** `scripts/enforcement/scheduler_mutation_contract.py` (stays at exactly 400 lines),
`scripts/enforcement/scheduler_mutation_python_flow.py` (imported, not modified),
`check-scheduler-mutation-surfaces.py` (`FORENSIC` needs no new member — measured),
`config/workstations/harness-state-classes.yaml`, `scripts/cron/cron_render.py` (owned by #3711),
`scripts/cron/setup-cron.sh`.

---

## TDD Test List

Every row states its status **on today's `main`** and the command that proves that status. Commands
marked `[ace1]` will be run from `/mnt/local-analysis/workspace-hub` with
`PATH=$HOME/.local/bin:$PATH`; they are read-only in-process calls. **No row requires `crontab -l`
any more** — rows 1, 8, 12 and 14 now read the committed fixture. `P` denotes v2's shared preamble
with `FIX = Path("tests/cron/fixtures/ace1-crontab-2026-07-30.txt")` and
`text = FIX.read_text()` substituted for the live capture.

| # | Test name | File | What it will verify | Expected output | Today's status on `main` + proving command |
|---|---|---|---|---|---|
| 1 | `test_ace1_fixture_aborts_with_47_managed_uncataloged` | `test_cron_apply.py` | The committed ace1 fixture will abort before rebuild and enumerate all 47 uncataloged records, every one `location == "managed"`. | `abort_reason` non-null; `len(uncataloged) == 47`; all `managed` | **RED.** `[ace1]` `P` → `plan(text)` gives `abort_reason=None`, `uncataloged=0`, `new_text=72 lines`, while the true record scan gives `uncataloged=47, all managed=True`. |
| 2 | `test_managed_block_unknown_line_blocks_before_rebuild` | `test_cron_apply.py` | A synthetic unknown line inside the managed block will block instead of vanishing. | abort naming the line, `location == "managed"` | **RED.** `[ace1]` `P` + synthetic `U`; `classify_line_detail(U, ownership_context=own)["class"] == "uncataloged"` but `plan(t)["abort_reason"] is None` and `U` is absent from `new_text`. Independently reproduced by r2. |
| 3 | `test_audit_and_apply_share_one_classification_context` | `test_cron_classification_context.py` | The two production entry points return byte-equal classification inputs. | all inputs equal | **RED.** `[ace1]` `build_audit_context("dev-primary")["external_fingerprints"]` = 10; `_load_cutover_context("dev-primary")[2]["preservation_fingerprints"]` = 11; equal → `False`. Reproduced by r2. |
| 4 | `test_classification_context_has_exactly_one_construction_site` | `test_cron_classification_context.py` | AST scan over **all** tracked cron consumers, not just the two known ones (r2 residual-risk note). | one construction site | **RED.** `[ace1]` counts over `scripts/cron/cron*.py` → `cron-audit.py 3/2`, `cron_apply.py 1/2`. Reproduced by r2. |
| 5 | `test_plan_cutover_takes_a_context_not_a_classifier_closure` | `test_cron_classification_context.py` | Signature `(current_text, classification_context, *, acknowledged=())`. | exactly those parameters | **RED.** `[ace1]` `inspect.signature(ct.plan_cutover)` → 8 positional params. Reproduced by r2. |
| 6 | `test_llm_wiki_line_in_legacy_exact_lines_stays_preserved_external` | `test_a1_preserved.py` | Third-party preserved line injected into `legacy_exact_lines` classifies `preserved_external`. | `preserved_external`; line survives planned `C` | **RED.** `[ace1]` injected variant → `cataloged` (reason `legacy-exact-line`), `abort_reason is None`, line absent from `new_text`. Reproduced by r2. |
| 7 | `test_bind_identity_collides_on_third_party_preservation_fingerprint` | `test_a1_preserved.py` | Bind-time collision recorded and raised under `fail_on_collision`. | `ValueError`; non-empty `preservation_collisions` | **RED.** `[ace1]` `identity_collisions == []` and no `preservation_collisions` key exists. Reproduced by r2. |
| 8 | `test_catalog_installed_fingerprint_does_not_outrank_exact_identity` | `test_a1_preserved.py` | The two live `deckhand-api-presence-sync` lines stay `cataloged` so cutover keeps deduping them. | both `cataloged` | **GREEN today — deliberate regression guard.** Necessary because the obvious fix breaks it. Now measured **from the fixture**, closing r2's "could not verify": blanket preservation-first = `same=69/71 diffs=2` (both deckhand lines flip to `preserved_external`); third-party-first = `same=71/71 diffs=0`. |
| 9 | `test_audit_fails_closed_on_parse_error_with_zero_uncataloged` | `test_cron_audit_fail_closed.py` | Non-zero exit and `ok: false` on a duplicate-marker crontab with zero uncataloged. | exit ≠ 0 | **RED.** `[ace1]` parse error `multiple begin markers found`, counts `{cataloged:2, preserved_external:1, uncataloged:0, ignore:6}`, `main()` returns 0 and prints `ok: true`. Reproduced by r2. |
| 10 | `test_classify_crontab_lines_never_returns_empty_records_on_parse_error` | `test_cron_audit_fail_closed.py` | One record per raw line, `location == "unparsed"`. | `len(records) == len(lines)` | **RED.** `[ace1]` `grep -rn "classify_crontab_lines" scripts/ tests/` → no matches. Reproduced by r2. |
| 11 | `test_absent_cataloged_occurrence_blocks_without_acknowledgement` | `test_cron_apply.py` | A `cataloged` occurrence present in `A` and absent from `C` blocks. | `intent["blocking"]` holds both | **RED.** `[ace1]` `abort_reason is None`, `uncataloged == []`, `"intent" not in p`, multiset difference `{NPURGE: 2}`. Reproduced by r2. |
| 12 | `test_intent_report_enumerates_every_absent_occurrence_including_ignore` | `test_cron_apply.py` | Every absent occurrence of every class, with location, index, class, reason, key. | 51 absent: 47 `uncataloged` + 4 `cataloged` | **RED, now fixture-based.** `[ace1]` on the committed fixture: `plan(text)` has no `intent` key; externally computed `absent = 51 {uncataloged: 47, cataloged: 4}`, `added = 52`, `abort_reason is None`. |
| 13 | `test_acknowledgement_is_occurrence_scoped_and_not_config_satisfiable` | `test_cron_apply.py` | Only the exact `sha256(baseline‖location‖index‖line)` digest satisfies it; no env var, YAML key or `legacy_exact_lines` row does. | still blocks | **RED.** `[ace1]` `grep -rn "acknowledged\|acknowledge" scripts/cron tests/cron` → no matches. Reproduced by r2. |
| 14 | `test_ace1_duplicate_occurrences_are_reported_with_distinct_indices` | `test_cron_apply.py` | Both duplicate pairs appear in `intent["absent"]` at distinct indices. | 2 pairs, 4 occurrences | **RED, now fixture-based.** `[ace1]` on the fixture: `notification-purge` at `(managed,31)` + `(after,7)`; `deckhand-api-presence-sync` at `(after,1)` + `(after,8)`; absent cataloged at `(after,0/4/7/8)`; no intent report exists. |
| 15 | `test_preservation_attestation_accepts_records_based_reconstruction` | `test_scheduler_mutation_task3.py` | The attestation returns `True` for `tests/enforcement/fixtures/preservation_reference.py`. | `True` | **RED.** `[ace1]` v3 predicate set on today's `cron_transaction.py` → `False` (per-predicate: only `render-block-called-once` True); shipped `_preservation_shape` on the new shape → `False`. Both directions measured. |
| 16 | `test_preservation_attestation_rejects_sixteen_named_mutations` | `test_scheduler_mutation_task3.py` | Each of M1-M14, M3b and MX flips the attestation `False`. | `False` ×16 | **RED.** `[ace1]` today's four mutation strings in `test_scheduler_mutation_task3.py:257-268` are the OLD source text and none of the new anchors exists in today's `cron_transaction.py`. Against the prototype: v3 rejects 16/16; the v2 spec rejects only 8/16. |
| 17 | `test_preservation_attestation_rejects_the_r2_counterexample` | `test_scheduler_mutation_task3.py` | The committed r2 counter-example is rejected, on named predicates. | `False`, ≥1 named predicate `False` | **RED.** `[ace1]` v2's published spec on the counter-example → `{'order': True, 'all_locations': True, 'retention': True, 'shape': True}`; v3 → `False` on 4 of 7 predicates. The fixture does not exist on `main`. |
| 18 | `test_preservation_predicate_set_cannot_be_silently_thinned` | `test_scheduler_mutation_task3.py` | `len(NAMED_PREDICATES) == 7` and `len(NAMED_MUTATIONS) == 16`, each with a unique name. | passes | **RED.** `[ace1]` `grep -rn "NAMED_PREDICATES\|NAMED_MUTATIONS" scripts/ tests/` → no matches; neither symbol exists. |
| 19 | `test_preservation_module_obeys_size_and_surface_constraints` | `test_scheduler_mutation_task3.py` | The new module is ≤400 lines, every function ≤50, and it matches no `PRIMITIVE_PATTERNS` entry (so it needs no `FORENSIC` membership). | passes | **RED.** `[ace1]` `scripts/enforcement/scheduler_mutation_preservation.py` does not exist. Prototype measured at 293 lines, largest function 26, `direct_primitives=[]`. |
| 20 | `test_ace2_fixture_classifies_as_captured` | `test_cron_fixtures.py` | The ace2 fixture reproduces its recorded breakdown for `dev-secondary`. | `before=14 managed=14 after=10`; `{cataloged:3, ignore:15, preserved_external:9, uncataloged:11}` | **RED.** `[ace1]` `ls tests/cron/fixtures` → no such directory; the fixture does not exist on `main`. Values measured on the capture. |
| 21 | `test_fixture_sanitisation_is_class_preserving_and_secret_free` | `test_cron_fixtures.py` | Each fixture passes the deny-scan, and redaction leaves the `(location, index, class)` sequence unchanged. | deny-scan 0 hits; sequences identical | **RED.** `[ace1]` fixtures absent on `main`. Measured on the captures: ace1 deny-scan 0 / 0 redactions; ace2 3 redactions, `SANITISATION CLASS-PRESERVING: True`. |
| 22 | `test_identity_inventory_host_can_render_every_linux_root` | `test_cron_fixtures.py` | The host resolves every registry Linux `workspace_root` to itself; otherwise fails naming the machine and citing #3711. | passes on Linux | **GREEN on ace1 — deliberate tripwire, not a change-proof.** Declared as such. `[ace1]` all four Linux roots `faithful=True`; `[mac]` `gpu-claw` resolves to `/System/Volumes/Data/home/undi/ws/workspace-hub`, `faithful=False`. |

**Score: 20 of 22 rows are genuinely RED on today's `main`. Rows 8 and 22 are declared GREEN as
guards, each with the measurement showing why it is necessary.** (v2: 15 RED / 1 GREEN.)

**Existing green gates that will be run and must stay green** (declared green, deliberately not
counted as change-proofs):

| Gate | Status today at `3fe934da9` | Command |
|---|---|---|
| whole enforcement checker | GREEN, exit 0 | `[ace1] uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py` |
| generated HTML report | GREEN, exit 0 | `[ace1] … --check-html docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html` |
| identity inventory freshness | GREEN, exit 0 | `[ace1] uv run --with pyyaml python scripts/cron/build-cron-identity-inventory.py --check` |
| `test_classifier_branch_set_is_complete_and_exact` | GREEN | `[ace1] uv run pytest tests/enforcement/test_scheduler_mutation_surfaces.py -q` |
| `test_enforcement_modules_obey_size_limits_and_extract_responsibilities` | GREEN | `[ace1] uv run pytest tests/enforcement/test_scheduler_mutation_task3.py -q` |
| `test_llm_wiki_corpus_ingest_is_preserved` | GREEN | `[ace1] uv run pytest tests/cron/test_a1_preserved.py -q` |
| `plan_cutover` already aborts on a parse error | GREEN | measured |

---

## Implementation Sequencing

Unchanged from v2 except for the #3711 prerequisite and the new module in commit 4.

The enforcement gate hard-errors in the intermediate state: once `cron_transaction.py` is refactored
but the attestation is not, `python-postwrite-preservation-multiset-v1` returns `False` →
`derive_status` returns `migration-required` for `scripts/cron/cron_apply.py`, a hardcoded member of
`resolved_dispositions` (`scheduler_mutation_contract.py:307`) that cannot be moved into a
`disposition_group`, so `covered != migration` fires as an **error**. TDD is preserved by splitting
along the gate boundary, not by splitting the fused pair.

0. **Prerequisite — [#3711](https://github.com/vamseeachanta/workspace-hub/issues/3711) merged.**
   Blocking for commits 2-4 only. See FIX 2.
1. **Commit 1 — RED tests and fixtures only.** All 22 rows plus
   `tests/cron/fixtures/*` and `tests/enforcement/fixtures/*`. Neither `tests/` nor the fixtures are
   digest sources, so the gate stays green while 20 rows fail. **May land before #3711.**
   *Gate check:* checker exit 0.
2. **Commit 2 — context unification.** `cron_identity.py` + `cron-audit.py` + `cron_apply.py` context
   wiring; regenerate the identity inventory and refresh `source_digest` and the HTML report in the
   same commit. Rows 3, 4, 9, 10 go green.
3. **Commit 3 — precedence + collision guard.** `cron_line_model.py` reorder, `_bind_identity` guard.
   Rows 6, 7 go green; row 8 stays green. Inventory + digest + HTML refresh.
4. **Commit 4 — the fused triple.** `cron_transaction.py` records refactor **and**
   `scheduler_mutation_preservation.py` **and** the `attestations.py` dispatch, in one commit, never
   split. Rows 1, 2, 5, 11-19 go green. Inventory + digest + HTML refresh.
5. Every commit ends with `check-scheduler-mutation-surfaces.py` and `--check-html` at exit 0, after
   `git add` (the checker reads the git index, not the worktree).

**Implementation host:** once #3711 has landed, generation is host-independent and commits 2-4 may be
authored anywhere. Until then, and as a belt regardless, row 22 fails loudly on a host that cannot
faithfully render another machine's `workspace_root`.

---

## Acceptance Criteria

- [ ] The committed ace1 fixture will produce a non-zero abort enumerating exactly 47 uncataloged
      records, every one with `location == "managed"`.
- [ ] Every live line in `before`, `managed` and `after` will be classified before any rebuild.
- [ ] `cron-audit.py` and `plan_cutover` will consume the **same object** from
      `build_classification_context`, with an AST test proving one construction site across all
      tracked cron consumers.
- [ ] `plan_cutover` will take a classification context, not a caller-supplied classifier closure.
- [ ] A line matching a third-party preservation fingerprint will classify `preserved_external` even
      when it also appears in `line_identities`, and `_bind_identity` will fail closed on that
      collision.
- [ ] Catalog `installed_fingerprint` rows will **not** outrank exact identity; the two live
      `deckhand-api-presence-sync` lines will still classify `cataloged` and still dedupe.
- [ ] `cron-audit` will exit non-zero with `ok: false` on a parse error even with zero uncataloged
      lines; `classify_crontab_lines` will never return `records: []`.
- [ ] `intent["absent"]` will enumerate **every** absent occurrence of every class; `cataloged` will
      not be exempt.
- [ ] Acknowledgement will be occurrence-scoped, baseline-bound, and satisfiable only via
      `--acknowledge-absent`.
- [ ] No fuzzy or command-only cataloging route will be added; `cron_line_model.py` will keep exactly
      one `{'class': 'cataloged'}` literal and `derive_cron_classifier_branches` will keep returning
      `{'canonical-exact-line', 'legacy-exact-line'}`.
- [ ] **`python-postwrite-preservation-multiset-v1` will return `False` for the committed r2
      counter-example and for all sixteen named mutations, and `True` for the committed reference
      shape.**
- [ ] **`NAMED_PREDICATES` will hold exactly 7 uniquely-named predicates and `NAMED_MUTATIONS`
      exactly 16, both asserted by test.**
- [ ] **`scheduler_mutation_preservation.py` will be ≤400 lines with every function ≤50 lines, will
      match no `PRIMITIVE_PATTERNS` entry, and will require no `FORENSIC` or `mutation-surfaces.yaml`
      change.**
- [ ] `ATT_SOURCES` will gain no entry; `scheduler_mutation_contract.py` will stay at 400 lines.
- [ ] **#3711 will be merged before commit 2.**
- [ ] **Both crontab fixtures will pass the deny-scan, and redaction will be proven class-preserving.**
- [ ] The identity inventory and `resolved_dispositions[0].source_digest` will be regenerated and the
      HTML report re-rendered in the same commit as each source change.
- [ ] `[ace1] uv run pytest tests/cron -q` and `[ace1] uv run pytest tests/enforcement -q` will pass.
- [ ] `check-scheduler-mutation-surfaces.py` and `--check-html` will both exit 0 at every commit.
- [ ] No implementation step will run `crontab` (write), `setup-cron.sh`, `cron_apply.py --apply`,
      `daily-cleanup.sh`, `repository_sync`, or `reconcile-ecosystem.sh --apply` on any host.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Codex r2 on **v2** | **MAJOR** | (1) the ordered AST attestation accepts a wrong implementation; (2) the ace1-only inventory constraint is unenforceable. Both are answered above; ten of v2's sixteen rows were independently reproduced RED, and v2's two contested design decisions were independently confirmed correct. |
| Author verification of **v3** (not a review) | n/a | Every RED/GREEN claim was produced by execution on `ace-linux-1`; raw output in `scripts/review/results/2026-07-30-plan-3709-v3-verification-log.md`. |
| Independent r2 on **v3** | **REQUIRED — not yet run** | Must be an independent provider. Self-review is explicitly insufficient. |

**Overall result:** pending independent r2. `status:plan-approved` will not be applied by any agent.

### v2 → v3 delta

1. **D5 rewritten.** Seven named predicates with value-flow assertions built on the existing
   `_walk_block` reachability engine, replacing three shape predicates. Proven to reject r2's exact
   counter-example (4 of 7 predicates `False` where v2 scored `True` on all three) and all sixteen
   named mutations, where v2's spec rejected only eight. v2's admitted M3 decoy hole is closed.
   The predicate set ships as `scheduler_mutation_preservation.py` because folding 293 lines into
   `attestations.py` would break the measured 400-line ceiling.
2. **Attestation limits stated honestly.** Three residual shapes were constructed and measured that
   v3 still accepts (R1/R2/R3). The plan does **not** claim the attestation carries the fail-closed
   clause alone, and names four compensating controls that carry it jointly.
3. **#3711 sequenced as a hard blocking dependency**, replacing v2's unenforceable "author on ace1"
   promise, with the root cause measured (`cron_render.py:87` `.resolve()`; `gpu-claw` poisoned on
   macOS) and a cheap in-repo tripwire while the dependency is open. The pre-existing
   inventory-content hole is recorded as an unclosed follow-on rather than claimed fixed.
4. **Crontab fixtures committed** for ace1 (73 lines, 0 redactions) and ace2 (40 lines, 3 redactions,
   proven class-preserving), with a stated sanitisation gate. Rows 1, 8, 12 and 14 no longer depend on
   `crontab -l`; r2's three "NOT RERUN" rows and the unverifiable 69/71 vs 71/71 parity claim are now
   reproducible offline. ace2's breakdown, which v2 declined to verify, is verified.
5. **Six new TDD rows** (17-22); score improves from 15 RED / 1 GREEN to 20 RED / 2 GREEN.

---

## Risks and Open Questions

- **Risk (carried):** deleting `catalog_commands` would break `derive_cron_classifier_branches`.
  Deferred; independently reproduced by r2.
- **Risk (carried):** `build_ownership_context` stays as a delegating wrapper, so a future caller
  could bypass the new context object. Row 4's AST scan covers all tracked cron consumers, per r2's
  residual-risk note.
- **Risk (carried):** the intent report's multiset comparison is over raw line strings; no
  normalization will be added.
- **Risk (carried):** `ignore` lines are excluded from `blocking` but included in `absent`. If a
  reviewer wants env lines to block, that is a one-line change to the `blocking` predicate and should
  be decided before approval.
- **Risk (carried):** the acknowledgement digest binds to the whole baseline, so any concurrent
  crontab change invalidates every key. Intended, but operationally noticeable.
- **Risk (new):** the attestation still accepts R1/R2/R3. Mitigated only by the behavioural tests and
  the arity guard. A reviewer who considers that insufficient should say so before approval — the
  alternative is a behavioural attestation, which is rejected on code-execution grounds.
- **Risk (new):** #3711 is `status:needs-plan`, so this plan's commits 2-4 are gated on an issue that
  has no plan yet. If the owner prefers not to serialise, the fallback is FIX 2 option (b) implemented
  inside `build-cron-identity-inventory.py`, accepting the conflict with #3711.
- **Risk (new):** the fixtures are point-in-time captures. They will drift from live ace1/ace2 state.
  They are regression fixtures, not a live mirror; the file names carry the capture date and the
  provenance sidecar records it.
- **Open (carried):** should #3708's premise be restated in that issue once this lands?
- **Open (resolved from v2):** ace2's breakdown is now verified. Whether ace2 convergence belongs to
  #3709 or #3708 remains an owner decision; this plan adds the ace2 fixture but schedules no ace2
  convergence work.

---

## Complexity: T3

**T3** — the change crosses a scheduler-mutation safety contract, two consumer CLIs, the destructive
classifier, the attestation that guards the reconstruction, a digest chain with a host-dependent
generator, a new enforcement module, and a generated HTML audit. Implementation remains blocked until
user approval **and** until #3711 is merged.
