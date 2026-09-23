# Verification log — plan #3709 v2 (author, NOT a review)

This file is the raw evidence behind every RED/GREEN claim in
`docs/plans/2026-07-30-issue-3709-managed-block-classification-v2.md`. It is **not** an adversarial
review; an independent r2 review is still required. It exists so a reviewer can diff the plan's
claims against actual output instead of re-deriving them.

- Host: `ace-linux-1` (`dev-primary`), repo `/mnt/local-analysis/workspace-hub`, HEAD `5690613c4`,
  `origin/main` = `3fe934da9`, worktree clean, git 2.43.0.
- Mac checkout: `/Users/krishna/Developer/ws/workspace-hub`, `main` = `3fe934da9`.
- All ten cron/enforcement sources byte-identical between the two (`git hash-object`); the only
  delta between `5690613c4` and `3fe934da9` is eight `.claude/state/*` files.
- Scope: read-only. `crontab -l` only; no `crontab` write, no `setup-cron.sh`, no
  `cron_apply.py --apply`, no `daily-cleanup.sh`, no `reconcile-ecosystem.sh --apply`. Probe scripts
  ran from `/tmp` on ace1 and were never written into the repo.

---

## 1. Enforcement checker on Linux — GREEN

```
$ uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py ; echo EXIT=$?
EXIT=0
$ uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py \
      --check-html docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html ; echo HTML_EXIT=$?
HTML_EXIT=0
```

Per-attestation, for `scripts/cron/cron_apply.py` / `reconcile-current-user-crontab` (11 entries):

```
python-physical-host-equality-guard-v1        True
python-lock-scope-v1                          True
python-baseline-snapshot-v1                   True
python-backup-baseline-v1                     True
python-prewrite-cas-v1                        True
python-postwrite-preservation-multiset-v1     True
python-postwrite-exact-state-v1               True
python-rollback-after-cas-v1                  True
python-rollback-exact-baseline-v1             True
cron-canonical-legacy-exact-authority-v1      True
crontab-current-user-target-v1                True
ATT_SOURCES total: 37     _preservation_shape(current cron_transaction.py): True
```

Any test row asserting the checker fails today is false.

---

## 2. Live ace1 crontab — the defect

```
parse:  before=11  managed=51  after=9  error=None
audit:  {'cataloged': 11, 'preserved_external': 1, 'uncataloged': 47, 'ignore': 15}   machine=dev-primary
plan_cutover: abort_reason=None  uncataloged=0  preserved=13  new_text=72 lines
              selected_tasks=56  conflicts=0
by location:  before:ignore=10  before:preserved_external=1
              managed:cataloged=4  managed:uncataloged=47
              after:cataloged=7   after:ignore=2
cataloged sources: canonical-exact-line=7  legacy-exact-line=4
cataloged task ids (9): deckhand-api-presence-sync, drive-index-refresh-ace,
  drive-index-refresh-cad, email-queue-attention-notify, email-queue-state-dry-run,
  equality-matrix-refresh, notification-purge, session-analysis, session-curation
duplicate live non-ignore lines:
  x2  30 4 * * * cd /mnt/local-analysis/workspace-hub && find logs/notifications/ ... -delete ...
        (managed index 31, after index 7)
  x2  0 5 * * 0 ... catalog_delta.py ... deckhand-api-presence-sync ...
        (after index 1, after index 8)
```

Note the duplicate placement precisely: the `notification-purge` pair straddles the block
(one copy in `managed`, one in `after`); the `deckhand-api-presence-sync` pair is **both copies in
`after`**.

Intent analysis on the same text:

```
absent occurrences (A minus C): 51 total, all non-ignore
  by class: {'uncataloged': 47, 'cataloged': 4}
added occurrences: 52
absent cataloged occurrences (x1 each):
  30 4 * * * cd /mnt/local-analysis/workspace-hub && find logs/notifications/ ... -delete ...
  47 */6 * * * ... bash scripts/curation/curate-session-memory.sh ...
  0 5 * * 0 ... catalog_delta.py ...
  50 */6 * * * ... bash scripts/readiness/equality-matrix-cron.sh ...
```

(r2 reported 48 uncataloged + 3 cataloged from an older static capture; the live crontab measured
today gives 47 + 4. The finding direction is unchanged.)

---

## 3. Context-builder divergence — MAJOR 2

```
audit  build_audit_context("dev-primary")["external_fingerprints"]   : 10
apply  _load_cutover_context("dev-primary")[2]["preservation_fingerprints"] : 11
equal                                                                 : False
line_identities equal                                                 : True
catalog_commands                                                      : 53 == 53
```

Provenance:

```
ownership preservation_fingerprints owners:
  ace-linux-2 x2, catalog-preservation-only x1, deckhand x6,
  external-private-repo x1, llm-wiki x1                       -> 11
audit  load_external_fingerprints() owners:
  ace-linux-2 x2, deckhand x6, external-private-repo x1, llm-wiki x1 -> 10
third_party = 10   catalog_preservation_only = 1
```

The single extra row is the `deckhand-api-presence-sync` catalog `installed_fingerprint`, appended
by `build_ownership_context` (`cron_identity.py:217-220`).

---

## 4. Preservation precedence — MAJOR 1

Injecting the llm-wiki corpus-ingest line as an extra `legacy_exact_lines` variant on the existing
`notification-purge` row (which lives under `preserved_local`, not `preserved_external`):

```
validate_state_classes(mutated, task_ids)      : []            <- schema-valid
classify_line_detail(LLM, ownership_context)   : cataloged
  reason=legacy-exact-line  catalog_task_id=notification-purge  variant_id=injected-probe
build_ownership_context(...)["identity_collisions"] : []       <- no guard fires
plan_cutover(...)  abort_reason=None   LLM in planned text: False   <- deleted, no abort
```

Baseline (no injection): `preserved_external`, and the line survives the planned text.

### 4a. The naive "preservation first" fix is WRONG

Reordering the entire `preservation_fingerprints` list ahead of exact identity:

```
derive_cron_classifier_branches : {'canonical-exact-line','legacy-exact-line'}   (still fine)
live-line parity vs today       : same=69  diff=2
  after  cataloged -> preserved_external   0 5 * * 0 ... catalog_delta.py ...
  after  cataloged -> preserved_external   0 5 * * 0 ... catalog_delta.py ...
```

Both live `deckhand-api-presence-sync` lines stop being catalog-owned, so cutover stops deduping
them. Cause: the catalog task's own `installed_fingerprint` is in that list, and it matches both the
live lines and the rendered canonical line:

```
catalog-preservation-only fingerprint hits on live lines : 2 (both 'after', both currently cataloged)
canonical rendered lines matching a catalog fingerprint  : ['deckhand-api-presence-sync']
```

### 4b. The third-party-only ordering is correct

Preserving only rows whose `owner != "catalog-preservation-only"` ahead of identity:

```
derive_cron_classifier_branches            : {'canonical-exact-line','legacy-exact-line'}
cron-classifier-destructive-branches-v1    : True
cron-canonical-legacy-exact-authority-v1   : True
live-line parity vs today                  : same=71  diff=[]
injected llm-wiki line under refined order : preserved_external   (today: cataloged)
```

### 4c. r2's "delete the dead parameters" remedy would break the branch guard

```
rewrite `return _classify_preserved(line, external_fingerprints)` to read the fingerprints off
ownership_context instead:
  derive_cron_classifier_branches(records) -> None
```

`None` fails `cron-classifier-destructive-branches-v1` and
`cron-canonical-legacy-exact-authority-v1` and flips three surfaces to `migration-required`. The
plan therefore keeps `classify_line_detail`'s signature.

### 4d. Extra `{'class': 'cataloged'}` dict literal — reproduced

```
derive_cron_classifier_branches(current)                       : {'canonical-exact-line','legacy-exact-line'}
same after adding ONE unrelated dict literal to cron_line_model : None
"'class': 'cataloged'" in RAW cron_line_model source            : False   (match is on ast.unparse)
```

---

## 5. Parse-error fail-open — MAJOR 3, already live on `main`

Crontab with duplicate managed markers whose live lines are all cataloged/preserved/ignore:

```
parse_crontab(...)["error"]   : 'multiple begin markers found'
cron-audit counts             : {'cataloged': 2, 'preserved_external': 1, 'uncataloged': 0, 'ignore': 6}
cron-audit uncataloged        : 0
cron-audit exit today         : 0        <- FAIL-OPEN, no refactor involved
cron-audit ok field today     : True
plan_cutover abort_reason     : 'multiple begin markers found'   <- already fail-closed
```

With uncataloged lines present the audit does exit 1 (48 uncataloged on a duplicated ace1 block), so
the hole is specifically "parse error AND everything known".

---

## 6. Intent-report fixture independent of the uncataloged abort — MAJOR 4

`[env line] + render_block(56 selected tasks) + notification-purge legacy line x2`:

```
notification-purge legacy line class : cataloged
plan_cutover abort_reason            : None
plan_cutover uncataloged             : 0
"intent" in plan result              : False
absent occurrences (A minus C)       : {NPURGE: 2}   total 2
```

Row 1's abort does not fire on this fixture, so it is a genuine independent proof that a `cataloged`
absence is silently accepted today.

---

## 7. Attestation — MAJOR 5

`_preservation_shape` today is ten verbatim tokens over `plan_cutover` + `_classify_nonmanaged` +
`_rebuild_lines` (`attestations.py:277-291`) — exactly the three functions a managed-block fix must
rewrite. The candidate replacement is the ordered AST predicate set specified in the plan (D5).
Evaluated against a throwaway prototype in `/tmp` (never written into the repo):

```
new shape on prototype        : True
new shape on current main     : False
old shape on prototype        : False
old shape on current main     : True
```

Named mutations against the prototype:

```
M1 drop 'managed' from the location tuple                : False
M2 remove the uncataloged abort                          : False
M3 hoist `block = render_block(...)` above classification: False
M4 drop the 'before' retention comprehension             : False
M5 `return before + block + after` -> `return before + block` : False
M6 remove the intent blocking check                      : False
M7 remove the parse-error abort                          : False
```

M3 caveat recorded honestly: an earlier formulation that merely **added** a decoy
`block0 = render_block(...)` above the classification did **not** trip `_ordered_indices` (it
returned `True`), because the predicate binds to the target name `block`. Only the true statement
hoist flips it. The plan's M3 is the hoist.

Module sizes (the 400-line ceiling and the 50-line-per-function rule are enforced by
`tests/enforcement/test_scheduler_mutation_task3.py:274-288`):

```
scripts/enforcement/scheduler_mutation_contract.py     400   <- at the ceiling; no ATT_SOURCES addition possible
scripts/enforcement/scheduler_mutation_attestations.py 317
scripts/cron/cron_transaction.py                       257
scripts/cron/cron-audit.py                             379
```

The four mutation strings in today's `test_preservation_attestation_proves_plan_reconstruction`
(`test_scheduler_mutation_task3.py:257-268`) are raw double-quoted source of the old functions and
must be replaced in the same commit as the source refactor.

---

## 8. Digest chain and implementation host (missed entirely by v1)

`scheduler_mutation_delegation.py:112-123` hashes `schedule-tasks.yaml`, `registry.yaml`,
`harness-state-classes.yaml`, `build-cron-identity-inventory.py`, `cron_render.py`,
**`cron_transaction.py`**, **`cron_line_model.py`**, **`cron_identity.py`** into
`inventory["input_digest"]`, and `:96-98` requires
`resolved_dispositions[0].source_digest` (`mutation-surfaces.yaml:273`) to equal it. Any edit to the
three cron modules this plan touches therefore requires regenerating
`docs/reports/issue-3475-command-identity-inventory.json` and refreshing `source_digest` in the same
commit — and re-rendering the HTML report, because `--check-html` is a byte comparison and
`input_digest` changes.

```
$ [ace1] uv run --with pyyaml python scripts/cron/build-cron-identity-inventory.py --check
ACE1_CHECK_EXIT=0
$ [mac]  uv run --with pyyaml python scripts/cron/build-cron-identity-inventory.py --check
ERROR: stale identity inventory: .../docs/reports/issue-3475-command-identity-inventory.json
MAC_CHECK_EXIT=1
```

The generator is host-dependent (#3711). Commits 2–4 of the sequencing plan must be authored on
ace-linux-1.

---

## 9. Remaining RED proofs

```
unknown line inside the managed block:
  classify_line_detail(...)               : uncataloged
  plan_cutover abort_reason               : None
  plan_cutover uncataloged                : 0
  line present in planned text            : False        <- silently dropped

construction sites today (occurrences per file):
  cron-audit.py : build_ownership_context( x3 , load_external_fingerprints( x2 , external_fingerprints( x2
  cron_apply.py : build_ownership_context( x1 , load_external_fingerprints( x0 , external_fingerprints( x2

APIs that do not exist anywhere in scripts/ or tests/:
  classify_crontab_lines, build_cutover_intent, _rebuild_from_records,
  build_classification_context, acknowledged, absent_lines      -> all zero hits

plan_cutover signature today:
  ['current_text','selected_tasks','roles','catalog_commands','external_fingerprints',
   'selected_task_ids','catalog_fingerprints','ownership_context']
```

---

## 10. Could not verify

- **ace2 class breakdown.** `crontab -l | wc -l` from ace1 → **40**, re-verified. The
  `cataloged 3 / preserved_external 9 / uncataloged 11 / ignore 18` split and the "3/14 by identity"
  framing are inherited from the task brief and were NOT re-derived here; driving `cron-audit`
  against ace2's checkout was outside the read-only budget. No test row depends on it.
- **The prototype is a proof artifact, not an implementation.** It shows the predicate set is
  satisfiable and the mutations are detected. It does not prove the real refactor will preserve every
  behaviour of `plan_cutover` — that is what the 16 test rows are for.
- **CI cannot currently enforce the ace1-only implementation host.** The constraint is documented in
  the plan's sequencing section and is otherwise unguarded.
