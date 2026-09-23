# Plan for #3709 (v2): Managed-Block Classification Before Cron Cutover

> **Status:** plan-review
> **Complexity:** T3
> **Date:** 2026-07-30
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3709
> **Client:** N/A
> **Lane:** lane:claude
> **Supersedes:** `docs/plans/2026-07-30-issue-3709-managed-block-classification.md` on `plan/3709-managed-block-classification` (r2 verdict **MAJOR**, 5 major findings)
> **Review artifacts:** `scripts/review/results/2026-07-30-plan-3709-v2-verification-log.md` (author verification log, not a review); independent r2 adversarial review REQUIRED before any approval

---

## Tense convention

Every statement about **work this plan proposes** is written in future tense. The
`Evidence` and `Today's status` columns are **measurements**, written as measurements with the
command that produced them. A measurement written in the future tense is unverifiable, which is
how the v1 plan shipped three false RED claims. Measurements are not claims that any artifact this
plan will create already exists.

**Every measurement below was produced on `ace-linux-1` (`dev-primary`,
`/mnt/local-analysis/workspace-hub`) on 2026-07-30**, except where marked `[mac]`. All ten cron and
enforcement sources are byte-identical between the Mac checkout at `3fe934da9` and the ace1 checkout
at `5690613c4` (`git hash-object` compared file by file; the only delta between those commits is
eight `.claude/state/*` files).

---

## Resource Intelligence Summary

### Existing repo code

- `scripts/cron/cron_transaction.py:160-234` will become the transaction owner of a records-based
  classification pass. `_classify_nonmanaged` (`:209-217`) will be replaced; it iterates only
  `parsed["before"] + parsed["after"]`. `_rebuild_lines` (`:229-234`) will be replaced; it
  re-classifies line **strings** rather than consuming records.
- `scripts/cron/cron-audit.py:220-263` (`audit_crontab`) and `:266-294` (`build_audit_context`) will
  stop being an independent classification path. `audit_crontab` iterates
  `crontab_text.split("\n")` and never parses markers, so it has no notion of location.
- `scripts/cron/cron_apply.py:291-297` (`_load_cutover_context`) + `:157-180` (`_selection_context`)
  will stop being the second, divergent context builder.
- `scripts/cron/cron_line_model.py:130-150` (`classify_line_detail`) will gain a precedence
  reorder only. It will remain the single destructive cataloging authority; no fuzzy or
  command-only route will be added.
- `scripts/cron/cron_identity.py:186-225` (`build_ownership_context`) will become a thin wrapper
  over a new single-source context builder. `_bind_identity` (`:228-243`) will gain the missing
  preservation collision check.
- `scripts/enforcement/scheduler_mutation_attestations.py:277-291` (`_preservation_shape`) will be
  re-authored as an ordered AST predicate set. Its module is 317 lines against a 400-line ceiling.

### Standards

| Standard | Status | Source |
|---|---|---|
| Scheduler Mutation Safety | applicable | `.claude/rules/scheduler-mutation-safety.md:3-10` will continue to require registered mutators, exact/parsed destructive identity, fail-closed unknowns, exact post-write verification, rollback CAS under the declared lock, and a green enforcement checker before merge. |
| Issue Planning Mode | applicable | `.claude/skills/coordination/issue-planning-mode/SKILL.md` will continue to require reproduction before planning, TDD-first implementation after approval, independent adversarial review, and no implementation before user approval. |
| Coding style — edit safety | applicable | `.claude/rules/coding-style.md` — multi-file refactor; one file at a time, tests between files. |

### LLM Wiki pages consulted

No `llm-wiki` content will be modified. The live `llm-wiki` corpus-ingest cron line
(`config/workstations/harness-state-classes.yaml:111-120`) will be treated as preserved external
state and will be the fixture for the precedence tests.

### Documents consulted

- Issue [#3709](https://github.com/vamseeachanta/workspace-hub/issues/3709) — defines the defect and
  the four required scope items (classify every line; one shared classification path; intent report
  with acknowledgement; TDD proof on the captured ace1 crontab).
- `scripts/review/results/2026-07-30-plan-3709-claude-r2.md` on
  `origin/plan/3709-managed-block-classification` — MAJOR, 5 major findings. This plan resolves each
  one and, where the review's own prescribed remedy is unsafe, says so with the measurement that
  proves it (see Findings 2R and 5R below).
- `docs/session-handoffs/2026-07-30-handoff-cron-upkeep-chain-to-ace-linux-1.md` — records that the
  Mac cannot run the enforcement checker and cannot regenerate the cron identity inventory, and that
  `scripts/review/results/` is gitignored (`.gitignore:577`) so review artifacts must be force-staged.
- `config/scheduled-tasks/mutation-surfaces.yaml:4-35` — `scripts/cron/cron_apply.py` is a compliant
  `direct-owner` with the `reconcile-current-user-crontab` operation carrying **11** attestations
  and two exact authority branches.
- `scripts/enforcement/scheduler_mutation_contract.py:71-109` — `ATT_SOURCES` holds **37** entries;
  the module is **exactly 400 lines**, the enforced ceiling.
- `scripts/enforcement/scheduler_mutation_delegation.py:112-123` — the identity-inventory digest
  covers `cron_transaction.py`, `cron_line_model.py`, `cron_identity.py`, `cron_render.py`,
  `build-cron-identity-inventory.py` and three configs; `:96-98` requires
  `resolved_dispositions[0].source_digest` to equal `inventory["input_digest"]`. This is the
  constraint the v1 plan missed entirely.
- Issue [#3711](https://github.com/vamseeachanta/workspace-hub/issues/3711) — the inventory
  generator is host-dependent; this plan inherits it as an implementation-host constraint.
- Drive-file index: no relevant documents for `cron plan_cutover managed block scheduler mutation`
  (the drive index reported stale/unreachable roots on the prior pass; no new hits).

### Gaps identified

1. No single classification-context constructor exists. Two builders exist and are **already
   divergent** (10 vs 11 preservation fingerprints).
2. No whole-crontab, location-tagged classification record type exists.
3. No transaction-level guard blocks uncataloged **managed-block** lines before rebuild.
4. No intent/deletion report exists; nothing enumerates baseline `A` lines absent from planned `C`.
5. `_bind_identity` has no collision check against preservation fingerprints, so an exact identity
   row silently outranks a third-party preservation fingerprint.
6. `cron-audit` has no parse-error path at all — it is **already fail-open** on a duplicate-marker
   crontab whose live lines are all known.
7. No attestation proves that managed-block lines are classified before the rebuild.

### Measured evidence

**Issue status** (`gh issue view 3709`, 2026-07-30): OPEN, `bug`, `cat:harness`,
`domain:workstations`, `status:needs-plan`, `lane:codex`.

**Files (all EXIST, hashes identical Mac ↔ ace1):** `scripts/cron/cron_transaction.py`,
`cron_apply.py`, `cron_line_model.py`, `cron_identity.py`, `cron-audit.py`,
`scripts/enforcement/scheduler_mutation_attestations.py`, `scheduler_mutation_contract.py`,
`config/scheduled-tasks/mutation-surfaces.yaml`, `config/workstations/harness-state-classes.yaml`,
`config/scheduled-tasks/schedule-tasks.yaml`.

**M0 — the enforcement checker is GREEN on today's `main` on Linux.** The v1 plan's
"environment-blocked" rows were a macOS artifact, not a defect.

```
$ ssh ace-linux-1 'cd /mnt/local-analysis/workspace-hub && uv run python \
    scripts/enforcement/check-scheduler-mutation-surfaces.py; echo EXIT=$?'
EXIT=0
$ ssh ace-linux-1 '... --check-html docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html'
HTML_EXIT=0
```

All 11 attestations of `reconcile-current-user-crontab` evaluate `True`, including
`python-postwrite-preservation-multiset-v1`. `ATT_SOURCES` = 37 entries.

**M1 — the defect reproduces on the live ace1 crontab.**

```
parse:  before=11 managed=51 after=9  error=None
audit:  {'cataloged': 11, 'preserved_external': 1, 'uncataloged': 47, 'ignore': 15}
plan_cutover: abort_reason=None  uncataloged=0  new_text=72 lines
by location: before:ignore=10  before:preserved_external=1
             managed:cataloged=4  managed:uncataloged=47
             after:cataloged=7   after:ignore=2
```

The 11 cataloged lines are 7 `canonical-exact-line` + 4 `legacy-exact-line` across 9 distinct task
ids (`deckhand-api-presence-sync`, `drive-index-refresh-ace`, `drive-index-refresh-cad`,
`email-queue-attention-notify`, `email-queue-state-dry-run`, `equality-matrix-refresh`,
`notification-purge`, `session-analysis`, `session-curation`); two lines are exact duplicates.

**M2 — the two context builders are already divergent.**

```
audit  build_audit_context(...)["external_fingerprints"]        : 10 entries
apply  _load_cutover_context(...)[2]["preservation_fingerprints"]: 11 entries
equal  : False
line_identities equal : True     catalog_commands equal : True (53 == 53)
```

Provenance of the extra entry: `build_ownership_context` appends one
`{"owner": "catalog-preservation-only", ...}` row from the `deckhand-api-presence-sync` catalog
task's `installed_fingerprint`. The 10 audit entries are third-party rows
(`deckhand` ×6, `ace-linux-2` ×2, `external-private-repo` ×1, `llm-wiki` ×1). The divergence is
invisible today only because `classify_line_detail` discards its `external_fingerprints` argument
whenever `ownership_context is not None` (`cron_line_model.py:149`).

**M3 — exact identity outranks preservation, and the route is live.** Appending one
`legacy_exact_lines` variant carrying the llm-wiki corpus-ingest line to the existing
`notification-purge` row (schema-valid — `validate_state_classes` returns `[]`):

```
classify_line_detail(llm_wiki_line, ownership_context=...)  : cataloged
  reason=legacy-exact-line  catalog_task_id=notification-purge  variant_id=injected-probe
build_ownership_context(...)["identity_collisions"]          : []      <-- no guard fires
plan_cutover(...)  abort_reason=None  llm_wiki_line_in_planned_text=False   <-- deleted
```

All three existing `legacy_exact_lines` rows live under `preserved_local`, not `preserved_external`
(`config/workstations/harness-state-classes.yaml:137,152,160,168`).

**M4 — the audit is ALREADY fail-open on a parse error.** A crontab with duplicate managed markers
whose live lines are all cataloged/preserved/ignore:

```
parse_crontab(...)["error"]      : 'multiple begin markers found'
cron-audit counts                : {'cataloged': 2, 'preserved_external': 1, 'uncataloged': 0, 'ignore': 6}
cron-audit ok field / exit today : ok=True / exit 0        <-- fail-OPEN, no refactor involved
plan_cutover abort_reason        : 'multiple begin markers found'   <-- already fail-closed
```

r2's Finding 3 framed this as a regression the shared path *would introduce*. The measurement shows
the hole exists on `main` today; the shared path must close it, not merely avoid widening it.

**M5 — the intent-report gap has a fixture that does not depend on the uncataloged abort.** A
crontab of `[env line] + render_block(all 56 selected tasks) + [notification-purge legacy line ×2]`:

```
notification-purge legacy line class : cataloged
plan_cutover abort_reason            : None
plan_cutover uncataloged             : 0
"intent" in plan result              : False
absent occurrences (A minus C)       : 2  (both the cataloged legacy line)
```

On the live ace1 crontab the same computation yields 51 absent non-ignore occurrences —
**47 `uncataloged` + 4 `cataloged`** — and 52 added occurrences. (r2 reported 48+3 from an older
static capture; the live crontab measured today gives 47+4. The direction of the finding is
unchanged: a `cataloged` absence is exempt under the v1 pseudocode and would be deleted silently.)

**M6 — the classifier-branch guard is real and the raw source does not contain the literal.**

```
derive_cron_classifier_branches(records)                     : {'canonical-exact-line','legacy-exact-line'}
same, after adding ONE extra dict literal to cron_line_model : None      -> two attestations fail
"'class': 'cataloged'" present in raw cron_line_model source : False     (the match is on ast.unparse)
```

**M7 — the identity inventory can only be regenerated on ace1.**

```
$ ssh ace-linux-1 '... uv run --with pyyaml python scripts/cron/build-cron-identity-inventory.py --check'
ACE1_CHECK_EXIT=0
$ [mac] uv run --with pyyaml python scripts/cron/build-cron-identity-inventory.py --check
ERROR: stale identity inventory: .../docs/reports/issue-3475-command-identity-inventory.json
MAC_CHECK_EXIT=1
```

**M8 — module sizes.** `scheduler_mutation_contract.py` = **400** (ceiling), `attestations.py` = 317,
`cron_transaction.py` = 257, `cron-audit.py` = 379. The size test is
`tests/enforcement/test_scheduler_mutation_task3.py:274-288`: ≤400 lines per
`scripts/enforcement/scheduler_mutation*.py`, ≤50 lines per function.

**M9 — ace2.** `crontab -l | wc -l` from ace1 → **40**. The ace2 class breakdown
(`cataloged 3, preserved_external 9, uncataloged 11, ignore 18`; 3/14 by identity vs 14/14 by line
count) is **inherited from the task brief and NOT re-verified here** — driving `cron-audit` on ace2
was out of the read-only budget. It is context only; no test row depends on it.

Distinct sources consulted: issue body, r2 review artifact, session handoff, five cron modules,
three enforcement modules, two configs, the mutation-surfaces registry, and the live ace1 crontab.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-30-issue-3709-managed-block-classification-v2.md` |
| Author verification log | `scripts/review/results/2026-07-30-plan-3709-v2-verification-log.md` |
| Independent plan review (r2, required) | `scripts/review/results/2026-07-30-plan-3709-v2-<provider>-r2.md` |
| Captured ace1 crontab fixture | `tests/cron/fixtures/ace1-crontab-2026-07-30.txt` (new) |
| Context-unification tests | `tests/cron/test_cron_classification_context.py` (new) |
| Audit fail-closed tests | `tests/cron/test_cron_audit_fail_closed.py` (new) |
| Transaction tests | `tests/cron/test_cron_apply.py` |
| Preservation precedence tests | `tests/cron/test_a1_preserved.py` |
| Attestation tests | `tests/enforcement/test_scheduler_mutation_task3.py` |
| Classification context authority | `scripts/cron/cron_identity.py` |
| Classifier authority | `scripts/cron/cron_line_model.py` |
| Transaction | `scripts/cron/cron_transaction.py` |
| Audit CLI | `scripts/cron/cron-audit.py` |
| Apply wrapper | `scripts/cron/cron_apply.py` |
| Attestation implementation | `scripts/enforcement/scheduler_mutation_attestations.py` |
| Mutation surface registry | `config/scheduled-tasks/mutation-surfaces.yaml` |
| Identity inventory | `docs/reports/issue-3475-command-identity-inventory.json` |
| Generated safety report | `docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html` |
| Plan index | `docs/plans/README.md` |

---

## Deliverable

One classification context, built in one place, consumed by both `cron-audit.py` and
`plan_cutover`; a records-based transaction that will classify **every** live line — `before`,
`managed`, and `after` — before any rebuild and will abort on any uncataloged record regardless of
location; an intent report that will enumerate **every** baseline occurrence absent from the planned
crontab with **no class exempt**, blocking unless an occurrence-scoped digest acknowledges it; and a
scheduler-mutation attestation that will assert that ordering structurally rather than by verbatim
source text.

---

## Recommended Design

### D1 — Unify at the context-builder layer (resolves r2 MAJOR 2)

`cron_identity.py` will gain the single source of truth:

```
build_classification_context(catalog, registry, state_classes, machine_id,
                             *, workspace_hub=None, fail_on_collision=True) -> dict
```

returning exactly the inputs the classifier consumes:

| Key | Meaning |
|---|---|
| `machine_id`, `roles`, `selected_tasks`, `selected_task_ids` | selection, unchanged semantics |
| `line_identities` | exact canonical + legacy identity map |
| `third_party_fingerprints` | `preserved_external` + `preserved_local` fingerprint rows (10 on ace1) |
| `catalog_fingerprints` | catalog `installed_fingerprint` rows (1 on ace1) |
| `preservation_fingerprints` | `third_party_fingerprints + catalog_fingerprints`, in that order |
| `identity_collisions`, `preservation_collisions` | fail-closed diagnostics |
| `catalog_commands` | **reporting only**; the classifier will never read it |

`build_ownership_context` will become a thin wrapper that delegates to it and returns the same key
set it returns today, so existing callers and tests will not move.

Both consumers will be rewritten to **return that object verbatim**:

- `cron-audit.build_audit_context(machine_id)` → `build_classification_context(...)`. Its private
  `load_external_fingerprints()` will move inside the new builder and will no longer be a second
  classification input.
- `cron_apply._load_cutover_context(machine_id)` → `build_classification_context(...)`.
  `cron_apply.external_fingerprints(classes)` will no longer feed `plan_cutover`.

`plan_cutover` will take the **context**, not a caller-supplied closure and not the five
pass-through parameters:

```
plan_cutover(current_text, classification_context, *, acknowledged=()) -> dict
```

It will build the classifier closure internally from the context. `audit_crontab` will take the same
context. Two consumers of one object cannot disagree; that is the property the issue asks for, and
sharing a `for` loop is not it.

**Constraint discovered by measurement — `classify_line_detail`'s signature will NOT change.** r2's
prescribed remedy ("delete the dead `catalog_commands` and `external_fingerprints` parameters") is
unsafe: `derive_cron_classifier_branches` requires the verbatim unparsed token
`return _classify_preserved(line, external_fingerprints)`. Rewriting that one return to read the
fingerprints off `ownership_context` makes `derive_cron_classifier_branches` return `None`
(measured), which fails `cron-classifier-destructive-branches-v1` and
`cron-canonical-legacy-exact-authority-v1` and flips `cron_apply.py`, `setup-cron.sh` and
`new-machine-setup.sh` to `migration-required`. `catalog_commands` will therefore stay in the
signature, documented in the docstring as a dead parameter retained under attestation lock, with the
removal deferred to a follow-on issue that budgets re-authoring the branch derivation.

### D2 — Preservation precedence, correctly ordered (resolves r2 MAJOR 1)

`classify_line_detail` will classify in this order:

```
ignore  →  third-party preservation  →  exact identity  →  catalog preservation  →  uncataloged
```

**The naive "preservation before identity" reorder is wrong and this plan will not ship it.**
Measured: moving the whole `preservation_fingerprints` list ahead of identity flips the two live
`deckhand-api-presence-sync` lines in ace1's `after` section from `cataloged` to
`preserved_external`, because that list contains the task's own catalog `installed_fingerprint`. The
cutover would stop deduping them — a live behaviour regression introduced by the "fix".

Measured for the correct ordering (third-party rows only ahead of identity):

```
live-line classification parity vs today : 71 / 71 identical, 0 differences
derive_cron_classifier_branches          : {'canonical-exact-line','legacy-exact-line'}  (unchanged)
llm-wiki line with injected legacy row   : preserved_external   (today: cataloged)
```

`_bind_identity` will additionally gain a collision check: binding an exact line that matches any
**third-party** fingerprint will append a `preservation_collision` record and will raise when
`fail_on_collision`. It will deliberately exclude `catalog_fingerprints` — measured, the rendered
canonical `deckhand-api-presence-sync` line matches its own `installed_fingerprint`, so an
undiscriminated guard would raise on every fingerprinted catalog task.

Both mechanisms will ship: the ordering fixes classification, the bind-time guard fails the context
build closed so an operator sees the mistake at config-load time instead of at cutover time.

### D3 — Records-based transaction, fail-closed on parse error (resolves r2 MAJOR 3)

```
classify_crontab_lines(current_text, classify_detail) -> {"parsed", "records", "error"}
```

Records will be ordered dicts `{"location", "index", "line", "detail"}` for
`location in ('before', 'managed', 'after')`.

**On parse error it will never return `records: []`.** It will return the error plus
`fallback_records` — every raw line of `current_text` classified with `location: "unparsed"`,
`index: <line number>` — so the audit keeps reporting everything it can while failing closed.

- `plan_cutover` will abort on `classified["error"]` before any rebuild (it already does; the
  behaviour will be preserved and pinned by the attestation).
- `cron-audit.main()` will return **non-zero** and emit `ok: false` with `reason: "crontab-parse-failed"`
  and the parse error string whenever `classified["error"]` is set — **including when
  `uncataloged` is empty**, which is exactly the case that exits 0 today.

### D4 — Intent report with no exempt class (resolves r2 MAJOR 4)

```
build_cutover_intent(records, new_lines, acknowledged) -> {"absent", "added", "blocking"}
```

- `absent` will enumerate **every** occurrence in the baseline multiset that is not in the planned
  multiset — `cataloged`, `preserved_external`, `uncataloged` and `ignore` alike — carrying
  `location`, `index`, `line`, `class`, `reason`, occurrence `key`, and `acknowledged`.
- `blocking` will be every absent occurrence whose class is not `ignore` and whose `key` is not in
  `acknowledged`. **`cataloged` is not exempt.** This is the sentence the v1 pseudocode contradicted
  and the reason "silent deletion impossible by construction" was false.
- `key` = `sha256(f"{sha256(baseline_text)}\0{location}\0{index}\0{line}")`.

**Acknowledgement will be occurrence-scoped and CLI-only:** `cron_apply.py --acknowledge-absent <hex>`
(repeatable), threaded to `plan_cutover(..., acknowledged=frozenset(...))`. It will not be readable
from an environment variable, from any YAML, or from any classification outcome. A
`legacy_exact_lines` row will therefore no longer function as a non-interactive acknowledgement flag.

**Recommended over the stricter alternative.** r2 offered "(a) no acknowledgement path at all". This
plan rejects (a): ace1 cannot converge without deleting two duplicate `cataloged` occurrences and
replacing the old `repository-sync` redirect line, so (a) would make the `--replace` path that
[#3708](https://github.com/vamseeachanta/workspace-hub/issues/3708) exists to re-open permanently
unreachable. (b) with a baseline-bound, occurrence-scoped digest keeps deletion deliberate, auditable
and non-replayable (the digest is invalidated by any change to the baseline crontab).

### D5 — The attestation (resolves r2 MAJOR 5)

**Recommendation: (b) assert the property, implemented as an ordered AST predicate set — not
re-authored verbatim tokens, and not a behavioural attestation.**

*Rejected — behavioural attestation.* `evaluate_python`'s contract is
`(name, records: dict[bytes, bytes], source: bytes) -> bool`, and
`check-scheduler-mutation-surfaces.py` builds `records` from **git-index blobs**
(`read_index_records`). Executing them to observe behaviour would import arbitrary staged content
into the enforcement gate's own process with no sandbox — a code-execution surface in the one tool
whose job is to be trustworthy. Rejected on that ground alone.

*Rejected — re-authoring ten verbatim tokens.* The failure mode r2 named (an implementer relaxes the
token set so the new code trivially satisfies it) is invisible in review: a token list looks the same
whether it is strict or vacuous. A one-token diff is unreviewable.

*Recommended — ordered AST predicates.* The module already contains exactly this idiom
(`_prewrite_shape` / `_rollback_shape` / `_ordered_indices` / `_assign_call`, `attestations.py:66-127`).
An ordering predicate cannot be quietly relaxed: weakening it requires **deleting a named predicate**,
which is a visible diff. It is strictly stronger than today's shape because it asserts *sequence*
(classification before render, abort before rebuild, intent check before return) which a text match
cannot express.

**The exact replacement shape** — pinned here so the implementer cannot choose it later:

```python
def _preservation_shape(tree):
    return bool(tree) and _plan_cutover_order(tree) \
        and _classify_all_locations(tree) and _rebuild_retention(tree)
```

1. `_plan_cutover_order(tree)` = `_ordered_indices(plan_cutover.body, P)` with `P`, in this order:
   1. `_assign_call(s, "classified", "classify_crontab_lines", ["current_text", "classify_detail"])`
   2. `_guard_return(s, "classified['error']")`
   3. assignment to `uncataloged` whose value unparse contains **both** `classified['records']` and
      `r['detail']['class'] == 'uncataloged'`
   4. `_guard_return(s, "uncataloged")`
   5. `_assign_call(s, "block", "render_block", ["selected_tasks", "roles"])`
   6. `_assign_call(s, "new_lines", "_rebuild_from_records", ["classified['parsed']", "classified['records']", "block"])`
   7. `_assign_call(s, "intent", "build_cutover_intent", ["classified['records']", "new_lines", "acknowledged"])`
   8. `_guard_return(s, "intent['blocking']")`

   where `_guard_return(stmt, expr)` = `isinstance(stmt, ast.If) and ast.unparse(stmt.test) == expr
   and stmt.body and isinstance(stmt.body[-1], ast.Return)`.
2. `_classify_all_locations(tree)` = `classify_crontab_lines` contains an `ast.For` node with
   `ast.unparse(node.iter) == "('before', 'managed', 'after')"`.
3. `_rebuild_retention(tree)` = `ast.unparse(_rebuild_from_records)` contains all four of:
   `r['location'] == 'before' and r['detail']['class'] != 'cataloged'`,
   `r['location'] == 'after' and r['detail']['class'] != 'cataloged'`,
   `return before + block`, `return before + block + after`.

**Verified by execution against a throwaway prototype** (a scratch file, never written into the
repo):

```
new shape on prototype        : True
new shape on current main     : False        <-- genuinely RED today
old shape on prototype        : False        <-- the refactor DOES break today's attestation
old shape on current main     : True
```

**No new attestation name will be added.** `python-postwrite-preservation-multiset-v1` will be
updated in place, so `ATT_SOURCES` will not grow and `scheduler_mutation_contract.py` will stay at
exactly 400 lines. `attestations.py` will grow from 317 within the 400 ceiling, with every new helper
≤ 50 lines.

### D6 — Deferred, with citations

- **Lock continuity** (`cron_apply.py:352-361`): `_finish_exact` runs after the `with _flock(LOCKFILE)`
  block closes, so post-write verification is outside the declared lock, against
  `.claude/rules/scheduler-mutation-safety.md:7`. Deferred from #3709 — but it will be recorded as a
  **hard blocker on any issue that re-enables `setup-cron.sh --replace`**, not a soft follow-on.
- **Python-layer OS guard** (`cron_apply.py:366-394`): `main()` has the physical-host equality guard
  but no Windows/OS guard. Deferred.
- **`equality-report` / `equality-matrix-refresh` rendering the same script**: checked, **not a
  defect** — the two catalog rows differ in schedule (`30 4 * * 1` vs `50 */6 * * *`) and log path, so
  their rendered exact lines differ and `_bind_identity` sees no collision. Recorded here so the next
  plan does not re-derive it as a hazard.
- **`catalog_commands` removal**: deferred to a follow-on that budgets re-authoring
  `derive_cron_classifier_branches` and refreshing three surfaces (measured hazard, see D1).

---

## Pseudocode

```python
# cron_identity.py — the single source of truth
def build_classification_context(catalog, registry, state_classes, machine_id,
                                 *, workspace_hub=None, fail_on_collision=True):
    context  = build_context(machine_id, registry=registry, workspace_hub=workspace_hub)
    rendered = [render_task(t, context) for t in _selected(catalog["tasks"], roles, tokens)]
    third_party = [row for row in preserved_external + preserved_local if row.get("fingerprint")]
    catalog_fps = [{"owner": "catalog-preservation-only", "fingerprint": t["installed_fingerprint"]}
                   for t in rendered if t.get("installed_fingerprint")]
    identities, identity_collisions, preservation_collisions = {}, [], []
    for task in rendered:
        _bind_identity(identities, identity_collisions, preservation_collisions,
                       task["line"], task["id"], "canonical-exact-line", "",
                       third_party, fail_on_collision)
    _bind_legacy(...)                              # same guard for legacy variants
    return {..., "third_party_fingerprints": third_party,
            "catalog_fingerprints": catalog_fps,
            "preservation_fingerprints": third_party + catalog_fps,
            "identity_collisions": identity_collisions,
            "preservation_collisions": preservation_collisions}


def _bind_identity(identities, collisions, preservation_collisions, line, task_id,
                   source, variant_id, third_party, fail):
    hit = _first_matching_fingerprint(line, third_party)     # NEW: no catalog_fingerprints here
    if hit:
        preservation_collisions.append({"line": line, "task_id": task_id, "owner": hit["owner"]})
        if fail:
            raise ValueError(f"exact identity collides with preservation fingerprint: {task_id}")
        return
    ...existing task-id collision logic unchanged...


# cron_line_model.py — precedence only; signature unchanged (attestation-locked)
def classify_line_detail(line, catalog_commands=None, external_fingerprints=None,
                         selected_task_ids=None, catalog_fingerprints=None,
                         ownership_context=None):
    if _is_ignore_line(line):
        return {"line": line, "class": "ignore", "reason": "ignore"}
    if ownership_context is not None:
        external_fingerprints = ownership_context.get("preservation_fingerprints", [])
        third_party = [r for r in external_fingerprints
                       if r.get("owner") != "catalog-preservation-only"]
        preserved = _classify_preserved(line, third_party)
        if preserved["class"] == "preserved_external":
            return preserved                                  # third party wins over identity
        identity = ownership_context.get("line_identities", {}).get(line)
        if identity:
            return {"line": line, "class": "cataloged", "reason": identity["source"], ...}
    return _classify_preserved(line, external_fingerprints)   # token pinned by the branch guard


# cron_transaction.py
def classify_crontab_lines(current_text, classify_detail):
    parsed = parse_crontab(current_text)
    records = []
    for location in ('before', 'managed', 'after'):
        for index, line in enumerate(parsed[location]):
            records.append({"location": location, "index": index, "line": line,
                            "detail": classify_detail(line)})
    if parsed["error"]:
        records = _fallback_records(current_text, classify_detail)   # NEVER empty
    return {"parsed": parsed, "records": records, "error": parsed["error"]}


def plan_cutover(current_text, classification_context, *, acknowledged=()):
    classify_detail = _detail_classifier(classification_context)
    classified = classify_crontab_lines(current_text, classify_detail)
    if classified["error"]:
        return _abort(classified["error"], [], None)
    uncataloged = [r for r in classified["records"] if r["detail"]["class"] == "uncataloged"]
    if uncataloged:
        return _abort(f"uncataloged live cron line(s): {uncataloged}", uncataloged, None)
    block = render_block(selected_tasks, roles)
    new_lines = _rebuild_from_records(classified["parsed"], classified["records"], block)
    intent = build_cutover_intent(classified["records"], new_lines, acknowledged)
    if intent["blocking"]:
        return _abort("planned crontab would omit live line(s)", [], intent)
    return {"new_text": ..., "preserved": ..., "uncataloged": [], "intent": intent,
            "abort_reason": None}


def _rebuild_from_records(parsed, records, block):
    before = [r["line"] for r in records
              if r["location"] == "before" and r["detail"]["class"] != "cataloged"]
    if parsed["roles"] is None:
        return before + block
    after = [r["line"] for r in records
             if r["location"] == "after" and r["detail"]["class"] != "cataloged"]
    return before + block + after


def build_cutover_intent(records, new_lines, acknowledged=()):
    planned = multiset(new_lines)
    absent  = [occurrence(r) for r in records if not consume(planned, r["line"])]
    blocking = [row for row in absent
                if row["class"] != "ignore" and row["key"] not in acknowledged]
    return {"absent": absent, "added": added(records, new_lines), "blocking": blocking}


# cron-audit.py
def main(argv=None):
    context   = build_classification_context(...)          # the SAME object cron_apply gets
    classified = classify_crontab_lines(read_live_crontab(), detail_classifier(context))
    audit      = audit_from_records(classified["records"])
    if classified["error"]:
        emit(ok=False, reason="crontab-parse-failed", error=classified["error"], audit=audit)
        return 2                                            # non-zero even with 0 uncataloged
    emit(ok=not audit["uncataloged"], audit=audit)
    return 1 if audit["uncataloged"] else 0
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `tests/cron/fixtures/ace1-crontab-2026-07-30.txt` | Captured live ace1 crontab (73 lines) as a committed regression fixture. |
| Create | `tests/cron/test_cron_classification_context.py` | Rows 3, 4, 5 — one context, one construction site, no closure parameter. |
| Create | `tests/cron/test_cron_audit_fail_closed.py` | Rows 9, 10 — parse-error fail-closed. |
| Modify | `tests/cron/test_cron_apply.py` | Rows 1, 2, 11, 12, 13, 14 — managed-block abort and intent report. |
| Modify | `tests/cron/test_a1_preserved.py` | Rows 6, 7, 8 — precedence and bind-time collision. |
| Modify | `tests/enforcement/test_scheduler_mutation_task3.py` | Rows 15, 16 — new shape + seven named mutations; the four existing mutation strings are the OLD source text and must be replaced in the same commit. |
| Modify | `scripts/cron/cron_identity.py` | Add `build_classification_context`; split third-party vs catalog fingerprints; add preservation collision guard to `_bind_identity`/`_bind_legacy`; keep `build_ownership_context` as a delegating wrapper. |
| Modify | `scripts/cron/cron_line_model.py` | Precedence reorder ONLY. Signature, the single `{'class': 'cataloged'}` dict literal, and the `return _classify_preserved(line, external_fingerprints)` token are all preserved verbatim. |
| Modify | `scripts/cron/cron_transaction.py` | `classify_crontab_lines`, `_rebuild_from_records`, `build_cutover_intent`; `plan_cutover` takes the context + `acknowledged`; delete `_classify_nonmanaged` and `_rebuild_lines`. |
| Modify | `scripts/cron/cron-audit.py` | Consume the shared context and shared records; add the parse-error fail-closed exit; delete the independent classification loop and the second fingerprint load. |
| Modify | `scripts/cron/cron_apply.py` | `_load_cutover_context` returns the shared context; `--acknowledge-absent` CLI; surface `intent` in dry-run and abort payloads; stop passing `external_fingerprints`. |
| Modify | `scripts/enforcement/scheduler_mutation_attestations.py` | Re-author `_preservation_shape` as the pinned ordered predicate set; add `_guard_return` and two ≤50-line helpers. NO new attestation name. |
| Modify | `docs/reports/issue-3475-command-identity-inventory.json` | Regenerate — the digest covers `cron_transaction.py`, `cron_line_model.py`, `cron_identity.py`. **Must be regenerated on ace-linux-1** (M7). |
| Modify | `config/scheduled-tasks/mutation-surfaces.yaml` | Refresh `resolved_dispositions[0].source_digest` to the new `inventory["input_digest"]` (`scheduler_mutation_delegation.py:96-98`). No attestation list change. |
| Modify | `docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html` | Regenerate via `--render-html`; `--check-html` is a byte comparison and `input_digest` will change. |
| Modify | `docs/plans/README.md` | Add this plan to the index. |

**Not changed:** `scripts/enforcement/scheduler_mutation_contract.py` (stays at exactly 400 lines),
`config/workstations/harness-state-classes.yaml` (no new legacy rows), `scripts/cron/cron_render.py`,
`scripts/cron/setup-cron.sh`.

---

## TDD Test List

Every row states its status **on today's `main`** and the command that proves that status. Commands
marked `[ace1]` will be run from the repo root of `/mnt/local-analysis/workspace-hub` on
`ace-linux-1` with `PATH=$HOME/.local/bin:$PATH`; they are read-only in-process calls plus
`crontab -l`. `P` denotes this shared preamble:

```python
# P
import sys, importlib.util, collections, copy
from pathlib import Path
ROOT = Path("/mnt/local-analysis/workspace-hub")
sys.path.insert(0, str(ROOT/"scripts"/"cron")); sys.path.insert(0, str(ROOT/"scripts"/"enforcement"))
import cron_transaction as ct, cron_line_model as clm, cron_identity as ci, cron_apply as ca
spec = importlib.util.spec_from_file_location("cron_audit", ROOT/"scripts"/"cron"/"cron-audit.py")
audit = importlib.util.module_from_spec(spec); spec.loader.exec_module(audit)
catalog, registry, classes = ca._load(ca.CATALOG), ca._load(ca.REGISTRY), ca._load(ca.STATE_CLASSES)
selection = ca._selection_context(catalog, registry, "dev-primary")
own = ci.build_ownership_context(catalog, registry, classes, "dev-primary")
cat_cmds = ca._combine_keys(ct.catalog_command_keys(selection["selected_raw"], include_fingerprinted=False),
                            ct.catalog_command_keys(selection["selected"], include_fingerprinted=False))
def plan(text, ownership=own, cls=classes):
    return ct.plan_cutover(text, selection["selected"], selection["roles"], cat_cmds,
        ca.external_fingerprints(cls), selected_task_ids=selection["selected_task_ids"],
        catalog_fingerprints=ca.catalog_fingerprints(selection["selected_raw"]), ownership_context=ownership)
```

| # | Test name | File | What it will verify | Expected input | Expected output | Today's status on `main` + proving command |
|---|---|---|---|---|---|---|
| 1 | `test_captured_ace1_crontab_aborts_with_47_managed_uncataloged` | `tests/cron/test_cron_apply.py` | The captured ace1 crontab will abort before rebuild and enumerate all 47 uncataloged records, every one `location == "managed"`. | `tests/cron/fixtures/ace1-crontab-2026-07-30.txt` | `abort_reason` non-null; `len(uncataloged) == 47`; all `location == "managed"` | **RED.** `[ace1]` `P` + `crontab -l > /tmp/a1.txt`; `p = plan(Path('/tmp/a1.txt').read_text())` → `p["abort_reason"] is None`, `len(p["uncataloged"]) == 0`; while `collections.Counter((loc, clm.classify_line_detail(l, ownership_context=own)["class"]) for loc in ("before","managed","after") for l in clm.parse_crontab(text)[loc])` → `('managed','uncataloged'): 47`. |
| 2 | `test_managed_block_unknown_line_blocks_before_rebuild` | `tests/cron/test_cron_apply.py` | A synthetic unknown line inside the managed block will block instead of vanishing. | `env + marker_begin + "0 * * * * cd /tmp && bash unknown.sh" + rendered block + marker_end` | abort naming that exact line, `location == "managed"` | **RED.** `[ace1]` `P` + `block = ct.render_block(selection["selected"], selection["roles"]); U = "0 * * * * cd /tmp && bash unknown.sh"; t = "\n".join(["WORKSPACE_HUB=/mnt/local-analysis/workspace-hub", block[0], U, *block[1:]])+"\n"; p = plan(t)` → `clm.classify_line_detail(U, ownership_context=own)["class"] == "uncataloged"` but `p["abort_reason"] is None`, `len(p["uncataloged"]) == 0`, `U not in p["new_text"].split("\n")` (silently dropped). |
| 3 | `test_audit_and_apply_share_one_classification_context` | `tests/cron/test_cron_classification_context.py` | The two **production** entry points will return byte-equal classification inputs for one machine id. Not a shared fixture — it calls `build_audit_context` and `_load_cutover_context` themselves. | `machine_id = "dev-primary"` | every classification input equal, including the preservation set | **RED.** `[ace1]` `P` + `a = audit.build_audit_context("dev-primary"); _, _, o = ca._load_cutover_context("dev-primary")` → `len(a["external_fingerprints"]) == 10`, `len(o["preservation_fingerprints"]) == 11`, `a["external_fingerprints"] == o["preservation_fingerprints"]` → `False`. |
| 4 | `test_classification_context_has_exactly_one_construction_site` | `tests/cron/test_cron_classification_context.py` | AST scan: outside `cron_identity.py`, no module will call `build_ownership_context`, `load_external_fingerprints`, or `external_fingerprints` to build classification inputs; both consumers will return `build_classification_context(...)` directly. | `scripts/cron/*.py` | exactly one construction site | **RED.** `[ace1]` `python3 -c "from pathlib import Path; [print(p.name, p.read_text().count('build_ownership_context('), p.read_text().count('external_fingerprints(')) for p in Path('scripts/cron').glob('cron*.py')]"` → `cron-audit.py 3 2`, `cron_apply.py 1 2` — two independent construction sites today. |
| 5 | `test_plan_cutover_takes_a_context_not_a_classifier_closure` | `tests/cron/test_cron_classification_context.py` | `plan_cutover`'s signature will be `(current_text, classification_context, *, acknowledged=())` — no caller-supplied closure, no `catalog_commands`/`external_fingerprints` pass-throughs. | `inspect.signature(ct.plan_cutover)` | exactly those parameters | **RED.** `[ace1]` `python3 -c "import inspect,sys; sys.path.insert(0,'scripts/cron'); import cron_transaction as ct; print(list(inspect.signature(ct.plan_cutover).parameters))"` → `['current_text','selected_tasks','roles','catalog_commands','external_fingerprints','selected_task_ids','catalog_fingerprints','ownership_context']`. |
| 6 | `test_llm_wiki_line_in_legacy_exact_lines_stays_preserved_external` | `tests/cron/test_a1_preserved.py` | A third-party preserved line injected into `legacy_exact_lines` will classify `preserved_external`, not `cataloged`, and will survive the planned text verbatim. | `harness-state-classes.yaml` + one extra `notification-purge` legacy variant carrying the llm-wiki line | `class == "preserved_external"`; line present in planned `C` | **RED.** `[ace1]` `P` + `c2 = copy.deepcopy(classes)`; append `{"id":"probe","line":LLM}` to the `notification-purge` row under `preserved_local`; `own2 = ci.build_ownership_context(catalog, registry, c2, "dev-primary")` → `clm.classify_line_detail(LLM, ownership_context=own2)["class"] == "cataloged"` (reason `legacy-exact-line`), and `plan(text, own2, c2)` → `abort_reason is None` with `LLM not in new_text.split("\n")`. |
| 7 | `test_bind_identity_collides_on_third_party_preservation_fingerprint` | `tests/cron/test_a1_preserved.py` | Binding an exact identity to a line matching a third-party preservation fingerprint will record a `preservation_collision` and raise under `fail_on_collision=True`. | same injected state classes | `ValueError`; `preservation_collisions` non-empty | **RED.** `[ace1]` same command as row 6 → `own2["identity_collisions"] == []`, and `build_ownership_context` has no `preservation_collisions` key at all (`ci.build_ownership_context` returns 9 keys, none named that). |
| 8 | `test_catalog_installed_fingerprint_does_not_outrank_exact_identity` | `tests/cron/test_a1_preserved.py` | The `deckhand-api-presence-sync` catalog `installed_fingerprint` will **not** win over the canonical identity, so cutover keeps deduping those two live `after` lines. | ace1 fixture | both live deckhand lines classify `cataloged` | **GREEN today — regression guard, not a change-proof.** Stated explicitly because the obvious "preservation first" fix breaks it: `[ace1]` reordering the whole `preservation_fingerprints` list ahead of identity flips exactly those two lines to `preserved_external` (live parity `69/71`, 2 differences). With the third-party-only ordering of D2 the parity is `71/71`, 0 differences. |
| 9 | `test_audit_fails_closed_on_parse_error_with_zero_uncataloged` | `tests/cron/test_cron_audit_fail_closed.py` | `cron-audit` will exit non-zero with `ok: false` and `reason: "crontab-parse-failed"` on a duplicate-marker crontab even when no line is uncataloged. | duplicate managed markers; every live line cataloged/preserved/ignore | exit ≠ 0, `ok == False`, parse error named | **RED.** `[ace1]` `P` + build `t = "\n".join([env, LLM, block[0], block[1], block[-1], block[0], block[2], block[-1]])+"\n"` → `clm.parse_crontab(t)["error"] == "multiple begin markers found"`, `audit.audit_crontab(t, ...)["counts"] == {'cataloged':2,'preserved_external':1,'uncataloged':0,'ignore':6}`, `uncataloged == []` → `main()` returns **0** and prints `ok: true`. |
| 10 | `test_classify_crontab_lines_never_returns_empty_records_on_parse_error` | `tests/cron/test_cron_audit_fail_closed.py` | On a parse error the shared path will still return one classified record per raw line, tagged `location == "unparsed"`. | same duplicate-marker text | `len(records) == len(text.split("\n"))`; `error` set | **RED.** `[ace1]` `grep -rn "classify_crontab_lines" scripts/ tests/` → no matches; the function does not exist. |
| 11 | `test_absent_cataloged_occurrence_blocks_without_acknowledgement` | `tests/cron/test_cron_apply.py` | A `cataloged` occurrence present in `A` and absent from `C` will block. Own fixture — row 1's uncataloged abort does not fire on it. | `env + render_block(56 tasks) + notification-purge legacy line ×2` | abort; `intent["blocking"]` holds both occurrences with `class == "cataloged"` | **RED.** `[ace1]` `P` + `t = "\n".join([env, *block, NPURGE, NPURGE])+"\n"; p = plan(t)` → `clm.classify_line_detail(NPURGE, ownership_context=own)["class"] == "cataloged"`, `p["abort_reason"] is None`, `p["uncataloged"] == []`, `"intent" not in p`, and the `A`−`C` multiset difference is `{NPURGE: 2}`. |
| 12 | `test_intent_report_enumerates_every_absent_occurrence_including_ignore` | `tests/cron/test_cron_apply.py` | `intent["absent"]` will list every absent occurrence of every class — `ignore` and `cataloged` included — with location, index, class, reason and key. | ace1 fixture with the uncataloged abort suppressed via `acknowledged` | 51 absent occurrences: 47 `uncataloged` + 4 `cataloged` | **RED.** `[ace1]` `P` + on `crontab -l`: `plan(text)` returns no `intent` key; the multiset difference computed externally gives `{'uncataloged': 47, 'cataloged': 4}` (51 absent, 52 added) with `abort_reason is None`. |
| 13 | `test_acknowledgement_is_occurrence_scoped_and_not_config_satisfiable` | `tests/cron/test_cron_apply.py` | An acknowledgement key will only be satisfiable by the exact `sha256(baseline‖location‖index‖line)` digest passed to `plan_cutover`; no env var, no YAML key, and no `legacy_exact_lines` row will satisfy it; a key from a different baseline will not. | row-11 fixture + a stale key + `CRON_ACK=*` in env | still blocks | **RED.** `[ace1]` `grep -rn "acknowledged\|acknowledge" scripts/cron tests/cron` → no matches; `plan_cutover` has no `acknowledged` parameter (row 5 signature dump). |
| 14 | `test_ace1_duplicate_occurrences_are_reported_in_the_intent_report` | `tests/cron/test_cron_apply.py` | The two exact duplicate pairs in ace1's live crontab will each appear in `intent["absent"]` with distinct occurrence indices. | ace1 fixture | 2 duplicate lines, 2 absent occurrences attributable by index | **RED.** `[ace1]` `P` + duplicate detection on `crontab -l`: `notification-purge` line ×2 (managed idx 31 + after idx 7) and `deckhand-api-presence-sync` line ×2 (after idx 1 + after idx 8); `plan(text)` produces no intent report. |
| 15 | `test_preservation_attestation_accepts_records_based_reconstruction` | `tests/enforcement/test_scheduler_mutation_task3.py` | `python-postwrite-preservation-multiset-v1` will return `True` for a records-based `plan_cutover` that classifies all three locations, aborts before render, and checks the intent report. | `records` with `cron_transaction.py` = the new shape | `True` | **RED.** `[ace1]` evaluate `sma._preservation_shape(ast.parse(prototype))` with today's implementation → `False` (and the new predicate set against today's `cron_transaction.py` → `False`). Both directions measured. |
| 16 | `test_preservation_attestation_rejects_seven_named_mutations` | `tests/enforcement/test_scheduler_mutation_task3.py` | Each of M1–M7 below will flip the attestation to `False`. | mutated `cron_transaction.py` bytes | `False` for all seven | **RED.** `[ace1]` the four mutation strings in today's `test_preservation_attestation_proves_plan_reconstruction` (`test_scheduler_mutation_task3.py:257-268`) are the OLD double-quoted source text; none of M1–M7's anchors exists in today's `cron_transaction.py`. Measured against the prototype, all seven return `False` (M3 verified only after being restated as a statement **hoist**; an added decoy assignment does not trip `_ordered_indices`). |

**The seven named mutations for row 16** (each must flip the attestation `False`; all verified):

| Id | Mutation |
|---|---|
| M1 | `for location in ('before', 'managed', 'after'):` → `for location in ('before', 'after'):` |
| M2 | delete the `if uncataloged: return _abort(...)` guard |
| M3 | hoist `block = render_block(selected_tasks, roles)` **above** `classified = classify_crontab_lines(...)` |
| M4 | `before = [ ... 'before' ... != 'cataloged']` → `before = []` |
| M5 | `return before + block + after` → `return before + block` |
| M6 | delete the `if intent['blocking']: return _abort(...)` guard |
| M7 | delete the `if classified['error']: return _abort(...)` guard |

**Existing green gates that will be run and must stay green** (declared green — deliberately not
counted as change-proofs, because re-listing existing coverage as new TDD rows is what failed the
last three plans):

| Gate | Status today | Command |
|---|---|---|
| `test_classifier_branch_set_is_complete_and_exact` | GREEN | `[ace1] uv run pytest tests/enforcement/test_scheduler_mutation_surfaces.py -q` |
| `test_enforcement_modules_obey_size_limits_and_extract_responsibilities` | GREEN | `[ace1] uv run pytest tests/enforcement/test_scheduler_mutation_task3.py -q` |
| `test_llm_wiki_corpus_ingest_is_preserved` | GREEN | `[ace1] uv run pytest tests/cron/test_a1_preserved.py -q` |
| `plan_cutover` already aborts on a parse error | GREEN | measured: `plan(dup_marker_text)["abort_reason"] == "multiple begin markers found"` |
| whole checker + `--check-html` | GREEN (exit 0/0) | `[ace1] uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py` and `--check-html …` |

**Score: 15 of 16 new rows are genuinely RED on today's `main`; row 8 is declared GREEN as a
regression guard with the measurement showing why it is necessary.**

---

## Implementation Sequencing (mandatory — resolves r2 MINOR 8)

The enforcement gate hard-errors in the intermediate state: once `cron_transaction.py` is refactored
but `_preservation_shape` is not, `python-postwrite-preservation-multiset-v1` returns `False` →
`derive_status` returns `migration-required` for `scripts/cron/cron_apply.py`, which is a hardcoded
member of `resolved_dispositions` (`scheduler_mutation_contract.py:307`) and cannot be moved into a
`disposition_group`, so `covered != migration` fires as an **error**. TDD is preserved by splitting
along the gate boundary, not by splitting the fused pair:

1. **Commit 1 — RED tests only.** All 16 rows land in `tests/cron/*` and `tests/enforcement/*`.
   `tests/cron/*` is not a digest source, so the gate stays green while 15 rows fail.
   *Gate check:* `check-scheduler-mutation-surfaces.py` exit 0.
2. **Commit 2 — context unification.** `cron_identity.py` + `cron-audit.py` + `cron_apply.py`
   context wiring; regenerate the identity inventory **on ace1** and refresh `source_digest` and the
   HTML report in the same commit. Rows 3, 4, 9, 10 go green.
3. **Commit 3 — precedence + collision guard.** `cron_line_model.py` reorder, `_bind_identity` guard.
   Rows 6, 7 go green; row 8 stays green. Inventory + digest + HTML refresh again.
4. **Commit 4 — the fused pair.** `cron_transaction.py` records refactor **and**
   `_preservation_shape` **and** its mutation test, in one commit, never split. Rows 1, 2, 5, 11–16
   go green. Inventory + digest + HTML refresh.
5. Every commit ends with `check-scheduler-mutation-surfaces.py` and `--check-html` at exit 0
   **on ace-linux-1**, after `git add` (the checker reads the git index, not the worktree).

**Implementation host:** commits 2–4 must be authored on `ace-linux-1`. `build-cron-identity-inventory.py`
is host-dependent (#3711) — `--check` exits 0 on ace1 and 1 on macOS today (M7), so a Mac-authored
commit would publish a wrong inventory and a wrong `source_digest`.

---

## Acceptance Criteria

- [ ] The captured ace1 crontab will produce a non-zero abort enumerating exactly 47 uncataloged
      records, every one with `location == "managed"`.
- [ ] Every live line in `before`, `managed` and `after` will be classified before any rebuild.
- [ ] `cron-audit.py` and `plan_cutover` will consume the **same object** returned by
      `build_classification_context`, and an AST test will prove there is exactly one construction
      site outside `cron_identity.py`.
- [ ] `plan_cutover` will take a classification context, not a caller-supplied classifier closure.
- [ ] A line matching a third-party preservation fingerprint will classify `preserved_external` even
      when it also appears in `line_identities`, and `_bind_identity` will fail closed on that
      collision.
- [ ] Catalog `installed_fingerprint` rows will **not** outrank exact identity; the two live
      `deckhand-api-presence-sync` lines will still classify `cataloged` and still dedupe.
- [ ] `cron-audit` will exit non-zero with `ok: false` on a parse error even when zero lines are
      uncataloged; `classify_crontab_lines` will never return `records: []`.
- [ ] `intent["absent"]` will enumerate **every** absent occurrence of every class; `cataloged` will
      not be exempt; `intent["blocking"]` will be non-empty for any unacknowledged non-`ignore`
      absence.
- [ ] Acknowledgement will be occurrence-scoped, baseline-bound, and satisfiable only via
      `--acknowledge-absent` — provably not by any env var, config key, or classification outcome.
- [ ] No fuzzy or command-only cataloging route will be added; `cron_line_model.py` will keep exactly
      one `{'class': 'cataloged'}` dict literal and
      `derive_cron_classifier_branches` will keep returning
      `{'canonical-exact-line', 'legacy-exact-line'}`.
- [ ] `python-postwrite-preservation-multiset-v1` will be the pinned ordered predicate set of D5, and
      all seven named mutations M1–M7 will return `False`.
- [ ] `ATT_SOURCES` will gain no entry; `scheduler_mutation_contract.py` will stay at 400 lines;
      every function in `scheduler_mutation*.py` will stay ≤ 50 lines.
- [ ] The identity inventory and `resolved_dispositions[0].source_digest` will be regenerated **on
      ace-linux-1** and the HTML report re-rendered, in the same commit as each source change.
- [ ] `[ace1] uv run pytest tests/cron -q` and `[ace1] uv run pytest tests/enforcement -q` will pass.
- [ ] `[ace1] uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py` and
      `--check-html docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html` will both exit 0
      at every commit.
- [ ] No implementation step will run `crontab` (write), `setup-cron.sh`, `cron_apply.py --apply`,
      `daily-cleanup.sh`, `repository_sync`, or `reconcile-ecosystem.sh --apply` on any host.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Author verification (not a review) | n/a | Every RED/GREEN claim in the TDD table was produced by execution on `ace-linux-1`; raw output is in `scripts/review/results/2026-07-30-plan-3709-v2-verification-log.md`. Two of r2's own prescribed remedies were found unsafe by measurement and are replaced with justified alternatives (D1 signature lock, D2 third-party-only ordering). |
| Independent r2 | **REQUIRED — not yet run** | Must be an independent provider. Self-review is explicitly insufficient. |

**Overall result:** pending independent r2. `status:plan-approved` will not be applied by any agent.

Revisions made relative to v1 (all five MAJORs):

1. Unification moved from the classifier closure to `build_classification_context`, with the measured
   10-vs-11 divergence as the RED proof and an AST single-construction-site test.
2. Precedence fixed as *third-party* preservation ahead of exact identity — not blanket preservation,
   which was measured to break the deckhand dedup — plus a bind-time collision guard.
3. `classify_crontab_lines` never returns empty records; `cron-audit` gains a non-zero parse-error
   exit. The fail-open was measured to **already exist** on `main`.
4. `cataloged` is no longer exempt from the intent report; acknowledgement is an occurrence-scoped,
   baseline-bound CLI digest with an explicit anti-bypass test.
5. `_preservation_shape` is re-authored as a pinned ordered AST predicate set with seven named
   mutations, all verified against a throwaway prototype; the behavioural alternative is rejected on
   code-execution grounds and the reason is recorded.

Plus: the identity-inventory digest chain and the ace1-only implementation host (missed entirely by
v1), the 400-line contract ceiling, four-commit sequencing that never leaves the gate red, and an
honest 15-RED/1-GREEN test table with per-row proving commands.

---

## Risks and Open Questions

- **Risk:** deleting `catalog_commands` would break `derive_cron_classifier_branches` (measured). The
  plan keeps it and defers removal. A reviewer wanting it gone must budget the branch-derivation
  rewrite plus three surface refreshes.
- **Risk:** `build_ownership_context`'s key set is consumed by existing tests. It stays as a
  delegating wrapper; any key rename is out of scope.
- **Risk:** the intent report's multiset comparison is over raw line strings. No whitespace or
  ordering normalization will be added — normalization is exactly how an unknown line becomes
  "known".
- **Risk:** `ignore` lines are excluded from `blocking` but included in `absent`. A crontab whose env
  lines are dropped will therefore report but not block. If a reviewer wants env lines to block, that
  is a one-line change to the `blocking` predicate and should be decided before approval.
- **Risk:** the acknowledgement digest binds to the whole baseline, so any concurrent crontab change
  invalidates every key. That is intended (it is a CAS on the acknowledgement), but it means an
  operator on a churning crontab may need to re-derive keys.
- **Risk:** `docs/reports/issue-3475-command-identity-inventory.json` regeneration is host-dependent.
  If implementation drifts to a Mac, the digest chain will silently publish a wrong inventory. The
  sequencing section makes ace1 mandatory; CI cannot currently enforce it.
- **Open:** should `#3708`'s premise be restated in this issue or in a follow-up comment on #3708
  once this lands? The issue asks for re-verification; this plan does not schedule it.
- **Open:** ace2's class breakdown was not re-verified (M9). If the owner wants ace2 convergence
  covered by #3709 rather than #3708, the plan needs a second fixture and the scope grows.

---

## Complexity: T3

**T3** — the change crosses a scheduler-mutation safety contract, two consumer CLIs, the destructive
classifier, the attestation that guards the reconstruction, a digest chain with a host-dependent
generator, and a generated HTML audit. Implementation remains blocked until user approval.
