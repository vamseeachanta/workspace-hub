# Plan for #3709: Managed-Block Classification Before Cron Cutover

> **Status:** plan-review
> **Complexity:** T3
> **Date:** 2026-07-30
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3709
> **Client:** N/A
> **Lane:** lane:codex
> **Review artifacts:** scripts/review/results/2026-07-30-plan-3709-codex-r1.md

---

## Resource Intelligence Summary

### Existing repo code

- `scripts/cron/cron_transaction.py:160-235` will be the transaction owner. It will currently classify only `parsed["before"] + parsed["after"]` in `_classify_nonmanaged`, then `_rebuild_lines` will replace the managed block without classifying its live lines.
- `scripts/cron/cron-audit.py:220-263` will already classify every line in the input stream, but it will own a separate loop from the transaction. The implementation will remove this audit/transaction divergence by moving the whole-crontab classification pass into one shared pure function.
- `scripts/cron/cron_line_model.py:130-167` will remain the single destructive classification authority. The implementation will not add fuzzy or command-only cataloging routes.
- `scripts/cron/cron_identity.py:186-225` will continue to bind selected task ownership through canonical exact lines and legacy exact lines.
- `scripts/cron/cron_apply.py:320-363` will remain the I/O wrapper. If the transaction result schema will gain an intent/deletion report, `run_cutover` will surface it on dry-run and abort responses without mutating scheduler state during tests.

### Standards

| Standard | Status | Source |
|---|---|---|
| Scheduler Mutation Safety | applicable | `.claude/rules/scheduler-mutation-safety.md:3-10` will require registered mutators, exact/parsed destructive identity, fail-closed unknowns, exact post-write verification, rollback CAS under the declared lock, and enforcement checker runs before merge. |
| Issue Planning Mode | applicable | `.claude/skills/coordination/issue-planning-mode/SKILL.md` will require reproduction before planning, TDD-first implementation after approval, adversarial review, and no implementation before user approval. |

### LLM Wiki pages consulted

- No `llm-wiki` content will be modified. The live `llm-wiki` corpus-ingest cron line will be treated as preserved external state through `config/workstations/harness-state-classes.yaml:111-120`.

### Documents consulted

- Issue #3709 will define the real defect: managed-block live lines will currently vanish from `plan_cutover` without classification.
- Issue #3708 will supply the superseded "no safe re-apply path" framing; this plan will explicitly avoid repeating its assumption that audit behavior protects the transaction.
- `scripts/review/results/2026-07-30-plan-3708-claude-r2.md` from `origin/plan/3708-crontab-reapply-path` will provide the MAJOR finding that `plan_cutover` will not classify managed-block lines and will silently drop equality/repository-sync drift.
- `scripts/review/results/2026-07-30-plan-3707-claude-r2.md` from `origin/plan/3707-cron-upkeep-clockwork` will provide the safety backdrop: re-opening cron apply paths will amplify destructive-path defects, fail-open probes, and red-on-day-one tests.
- `config/scheduled-tasks/mutation-surfaces.yaml:4-35` will declare `cron_apply.py` as a compliant direct scheduler mutator with exact canonical and legacy authority branches.
- `scripts/enforcement/scheduler_mutation_attestations.py:130-150` will impose the closed AST shape for exactly one `{'class': 'cataloged'}` dict literal in `cron_line_model.py`; this plan will preserve that single cataloging site.
- `scripts/enforcement/scheduler_mutation_contract.py:71-109,155-199,302-315` will impose closed `ATT_SOURCES`, digest source union, and resolved-disposition membership. Any attestation contract change will therefore update the checker, contract, tests, registry digest, and generated HTML report together.
- Drive-file search will return no relevant documents for `cron plan_cutover managed block scheduler mutation`; it will also report stale/unreachable indexes for `/mnt/ace`, `/mnt/dde`, O&G standards, CAD readability, and the master document index.

### Gaps identified

- No shared "classify every live crontab line with location metadata" function will exist today for audit and transaction to consume.
- No transaction-level guard will block uncataloged managed-block lines before `_rebuild_lines` replaces the block.
- No deletion/intent report will enumerate baseline `A` lines absent from planned `C`, so silent deletion will remain possible by construction.
- No precedence test will prove preserved external lines win before any future non-exact identity branch.
- No scheduler-mutation attestation will prove managed-block lines are included in the preservation/fail-closed reconstruction guarantee.

### Evidence

**Issue statuses** (verified 2026-07-30T00:57Z via `gh issue view`):
- `#3709` will be OPEN, titled `bug(cron): plan_cutover silently drops managed-block lines instead of blocking on them — audit and apply path disagree`, with `status:needs-plan`.
- `#3708` will be OPEN, titled `bug(cron): no safe crontab re-apply path — audit fail-closed on 47 uncataloged lines and setup-cron --replace disabled`, with `status:needs-plan` and `lane:codex`.

**File existence** (`ls` / `rg --files` 2026-07-30T00:57Z):
- EXISTS: `scripts/cron/cron_transaction.py`
- EXISTS: `scripts/cron/cron_apply.py`
- EXISTS: `scripts/cron/cron_line_model.py`
- EXISTS: `scripts/cron/cron_identity.py`
- EXISTS: `scripts/cron/cron-audit.py`
- EXISTS: `scripts/cron/cron_render.py`
- EXISTS: `scripts/enforcement/scheduler_mutation_attestations.py`
- EXISTS: `scripts/enforcement/scheduler_mutation_contract.py`
- EXISTS: `config/scheduled-tasks/mutation-surfaces.yaml`
- EXISTS: `config/workstations/harness-state-classes.yaml`
- EXISTS: `.claude/rules/scheduler-mutation-safety.md`
- EXISTS: captured ace1 crontab plus audit JSON at `/private/tmp/claude-501/-Users-krishna-Developer-ws/37e3e642-de6b-4825-b67e-872f62f6b3b9/scratchpad/ace1-cron.txt`

**Line excerpts**:

```text
$ nl -ba scripts/cron/cron_transaction.py | sed -n '181,235p'
181     classify = _line_classifier(...)
185     preserved, uncataloged = _classify_nonmanaged(parsed, classify)
195     new_lines = _rebuild_lines(parsed, render_block(selected_tasks, roles), classify)
209 def _classify_nonmanaged(parsed, classify):
211     for line in list(parsed["before"]) + list(parsed["after"]):
229 def _rebuild_lines(parsed, block, classify):
230     before = [line for line in parsed["before"] if classify(line) != "cataloged"]
233     after = [line for line in parsed["after"] if classify(line) != "cataloged"]
```

```text
$ nl -ba scripts/cron/cron-audit.py | sed -n '220,263p'
220 def audit_crontab(...)
237     for line in crontab_text.split("\n"):
239         detail = classify_line(...)
259     return {
260         "lines": results,
261         "counts": counts,
262         "uncataloged": [r["line"] for r in results if r["class"] == "uncataloged"],
```

```text
$ nl -ba scripts/enforcement/scheduler_mutation_attestations.py | sed -n '130,150p'
130 def derive_cron_classifier_branches(records: dict[bytes, bytes]) -> set[str] | None:
143     cataloged_returns = sum(
144         "'class': 'cataloged'" in ast.unparse(node)
148     if not all(token in text for token in required) or cataloged_returns != 1:
149         return None
150     return {"canonical-exact-line", "legacy-exact-line"}
```

**Reproduction proofs** (verify-against-repo-state):

```text
$ uv run python - <<'PY'
<read captured file, use lines 2-74 as the real crontab segment, build dev-primary selection/ownership, call cron_transaction.plan_cutover, then classify the same text through cron_line_model.classify_line_detail>
PY
parsed before=11 managed=51 after=9 error=None
selected_tasks=56 conflicts=0
plan_abort_reason=None
plan_uncataloged_count=0
audit_counts={'cataloged': 11, 'preserved_external': 1, 'uncataloged': 47, 'ignore': 15}
audit_uncataloged_count=47
uncataloged_inside_managed=47
collect_equality_survives=False
old_repo_sync_line_count 1
new_repo_sync_line_count 0
new_repo_sync_line= 0 */4 * * * mkdir -p /mnt/local-analysis/workspace-hub/logs && PATH=$HOME/.local/bin:$PATH; cd /mnt/local-analysis/workspace-hub && bash scripts/cron-repository-sync.sh
llm_wiki_corpus_ingest_count=1
```

- Reproduced at: 2026-07-30T00:57Z.
- Failure mode observed will match the issue claim: YES. `plan_cutover` will report clean, while the shared classifier will find 47 uncataloged managed-block lines, and the planned output will drop the equality body plus the old repository-sync redirect.

**Related test baseline**:

```text
$ uv run pytest tests/cron/test_cron_apply.py tests/cron/test_a1_preserved.py -q
......................................                                   [100%]
38 passed in 1.48s
```

```text
$ uv run pytest tests/enforcement/test_scheduler_mutation_surfaces.py tests/enforcement/test_scheduler_mutation_hardening.py -q
FAILED ... GitTransportError: Git cat-file --batch-command -Z support is required
51 failed, 25 passed in 3.79s
```

The enforcement failure will be an environment/tooling limit on this macOS checkout, not semantic evidence about #3709. The implementation will require a capable Linux/Git run before merge.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-30-issue-3709-managed-block-classification.md` |
| Cron transaction tests | `tests/cron/test_cron_apply.py` |
| Cron identity/classification tests | `tests/cron/test_cron_identity_task2.py` |
| Ace1 preservation regression tests | `tests/cron/test_a1_preserved.py` |
| Scheduler mutation enforcement tests | `tests/enforcement/test_scheduler_mutation_surfaces.py` |
| Scheduler mutation hardening tests | `tests/enforcement/test_scheduler_mutation_hardening.py` |
| Scheduler mutation task3 tests | `tests/enforcement/test_scheduler_mutation_task3.py` |
| Shared classification implementation | `scripts/cron/cron_transaction.py` |
| Audit CLI consumer | `scripts/cron/cron-audit.py` |
| Apply wrapper consumer | `scripts/cron/cron_apply.py` |
| Classifier authority | `scripts/cron/cron_line_model.py` |
| Exact identity authority | `scripts/cron/cron_identity.py` |
| Scheduler attestation implementation | `scripts/enforcement/scheduler_mutation_attestations.py` |
| Scheduler contract implementation | `scripts/enforcement/scheduler_mutation_contract.py` |
| Mutation surface registry | `config/scheduled-tasks/mutation-surfaces.yaml` |
| Generated mutation safety report | `docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html` |
| Plan review | `scripts/review/results/2026-07-30-plan-3709-codex-r1.md` |

---

## Deliverable

The cron audit and transaction paths will share one whole-crontab classification and intent-report pipeline that will classify every live line, block uncataloged managed-block lines, and enumerate every baseline line that would be absent from the planned crontab.

---

## Recommended Design

The implementation will add one pure classification artifact in `cron_transaction.py`, for example `classify_crontab_lines(current_text, classifier)`, returning ordered records:

```python
{
    "line": line,
    "location": "before" | "managed" | "after",
    "index": zero_based_index_within_location,
    "detail": classify_line_detail(...),
}
```

`cron-audit.py` will call this artifact for reporting. `plan_cutover` will call the same artifact before any rebuild and will abort if any non-ignore record has `class == "uncataloged"`, regardless of location. `_rebuild_lines` will consume the same records rather than reclassifying line strings.

The implementation will add a second pure artifact, for example `build_cutover_intent(parsed, classified_records, planned_lines)`, that will compute baseline `A` minus planned `C` with line, location, occurrence index, classification class, reason, and planned disposition. Any absent line without a catalog-owned exact identity and explicit acknowledgment token will block. The default path will not acknowledge anything automatically. This will make silent deletion impossible by construction.

The design will keep one destructive cataloging site: `cron_line_model.classify_line_detail` will retain the only `{'class': 'cataloged'}` return. New code will move loops and disposition reporting around that classifier; it will not add new ways to return cataloged. Preservation fingerprints will be checked before any future non-exact identity branch, and this issue will add a precedence test even though no fuzzy branch will be introduced.

---

## Pseudocode

```python
def classify_crontab_lines(current_text, classify_detail):
    parsed = parse_crontab(current_text)
    if parsed["error"]:
        return {"parsed": parsed, "records": [], "error": parsed["error"]}
    records = []
    for location in ("before", "managed", "after"):
        for index, line in enumerate(parsed[location]):
            detail = classify_detail(line)
            records.append({"location": location, "index": index, "line": line, "detail": detail})
    return {"parsed": parsed, "records": records, "error": None}

def plan_cutover(...):
    classified = classify_crontab_lines(current_text, classify_detail)
    if classified["error"]:
        return abort(classified["error"])
    uncataloged = [r for r in classified["records"] if r["detail"]["class"] == "uncataloged"]
    if uncataloged:
        return abort_with_records("uncataloged live cron line(s)", uncataloged)
    block = render_block(selected_tasks, roles)
    new_lines = rebuild_from_classification(classified["parsed"], classified["records"], block)
    intent = build_cutover_intent(classified["records"], new_lines)
    if intent["unacknowledged_absent_lines"]:
        return abort_with_intent("planned crontab would omit live line(s)", intent)
    return planned(new_text, intent)

def rebuild_from_classification(parsed, records, block):
    keep_before = non_cataloged_lines(records, location="before")
    keep_after = non_cataloged_lines(records, location="after")
    if parsed["roles"] is None:
        return keep_before + block
    return keep_before + block + keep_after

def build_cutover_intent(records, new_lines):
    compare multisets of original non-ignore live lines against planned lines
    classify absent occurrences by exact catalog identity, preserved_external, uncataloged, ignore
    require an explicit acknowledgment for every absent preserved_external or unknown line
    return ordered report with absent, retained, rendered, and blocked fields
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `tests/cron/test_cron_apply.py` | Add RED transaction regressions for captured ace1 managed-block uncataloged abort, managed-block unknown-line abort, intent report blocking absent lines, repository-sync redirect deletion report, continuous lock decision if handled here, and Windows guard if handled here. |
| Modify | `tests/cron/test_cron_identity_task2.py` | Add shared-classification parity and preservation-precedence tests that prove audit and transaction consume the same record-producing path. |
| Modify | `tests/cron/test_a1_preserved.py` | Add captured llm-wiki corpus-ingest verbatim survival and precedence regression with the real preserved_external fingerprint. |
| Modify | `tests/enforcement/test_scheduler_mutation_surfaces.py` | Add or update checker coverage if the transaction attestation will gain a managed-block classification guarantee. |
| Modify | `tests/enforcement/test_scheduler_mutation_hardening.py` | Add fail-closed tests for any attempted extra cataloged return site or unregistered attestation/source mode. |
| Modify | `tests/enforcement/test_scheduler_mutation_task3.py` | Update `python-postwrite-preservation-multiset-v1` proof so source mutations that omit managed-block classification will fail. |
| Modify | `scripts/cron/cron_transaction.py` | Implement shared whole-crontab classification records, managed-block fail-closed aborts, classification-driven rebuild, and diff/intent reporting. |
| Modify | `scripts/cron/cron-audit.py` | Replace the independent audit classification loop with the shared whole-crontab classification artifact. |
| Modify | `scripts/cron/cron_apply.py` | Surface intent/deletion reports in dry-run and abort output. Lock continuity and Python-layer Windows OS guard will be explicitly deferred from this issue. |
| Modify | `scripts/cron/cron_line_model.py` | Preserve the single cataloged return site and add preservation-before-future-non-exact precedence if classifier order will be adjusted. |
| Modify | `scripts/cron/cron_identity.py` | Only adjust exact identity context if the shared classification record will need additional exact-identity metadata; no fuzzy command-only authority will be added. |
| Modify | `scripts/enforcement/scheduler_mutation_attestations.py` | Update the preservation/reconstruction attestation to require managed-block classification before rebuild while preserving exactly one cataloged return in `cron_line_model.py`. |
| Modify | `scripts/enforcement/scheduler_mutation_contract.py` | Update `ATT_SOURCES` or digest sources only if the implementation adds/renames attestations; keep the closed source contract explicit. |
| Modify | `config/scheduled-tasks/mutation-surfaces.yaml` | Refresh the `source_digest` and any attestation list if governed source changes alter the compliance proof. |
| Modify | `docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html` | Regenerate after governed scheduler mutation sources or digest inputs change. |
| Modify | `docs/plans/README.md` | Add this plan to the index. |

---

## TDD Test List

Every row below will be RED on today's `main` unless noted as an environment-blocked enforcement proof. Rows that were already green in existing suites will be excluded from the change-proof set.

| Test name | What it will verify | Expected input | Expected output | Today's main status and proof command |
|---|---|---|---|---|
| `test_captured_ace1_managed_block_uncataloged_lines_abort_with_47_records` | The captured ace1 crontab will abort before rebuild and enumerate all 47 uncataloged managed-block lines. | Lines 2-74 of captured ace1 file. | `status == "abort"` or `abort_reason` non-null; `len(uncataloged) == 47`; every record will have `location == "managed"`. | FAIL today. Proof: the reproduction command above will print `plan_abort_reason=None`, `plan_uncataloged_count=0`, `audit_uncataloged_count=47`, `uncataloged_inside_managed=47`. |
| `test_managed_block_unknown_line_blocks_before_rebuild` | A synthetic unknown cron line inside the managed block will block instead of vanishing. | Managed block containing `0 * * * * cd /tmp && bash unknown.sh`. | Abort with that exact line and `location == "managed"`. | FAIL today. Proof command `uv run python - <<'PY' ... plan_cutover(\"WORKSPACE_HUB=/repo\\n# >>> ...\\n0 * * * * cd /tmp && bash unknown.sh\\n# <<< ...\\n\", selected_tasks=[], ...) ... PY` printed `abort_reason= None`, `uncataloged_count= 0`, `unknown_survives= False`. |
| `test_shared_classification_records_are_used_by_audit_and_transaction` | Audit and transaction will consume the same ordered records, not independent classifiers over the same input. | Mixed before/managed/after crontab fixture. | Audit JSON `lines` and transaction preflight records will match by line, location, class, reason, and task id. | FAIL today. Proof: `rg -n "classify_crontab_lines|build_cutover_intent|absent_lines|unacknowledged_absent" scripts/cron tests/cron scripts/enforcement tests/enforcement` returned no matches, so the shared record-producing path will not exist yet. |
| `test_intent_report_blocks_unacknowledged_absent_live_line` | Any baseline line present in `A` and absent from planned `C` will be enumerated and block without explicit acknowledgement. | Cataloged plus preserved plus unknown occurrences where rebuild would omit one live line. | Abort with `intent.absent_lines` containing the missing occurrence, class, reason, and location. | FAIL today. Proof: captured reproduction will show `collect_equality_survives=False` while `plan_abort_reason=None`. |
| `test_repository_sync_wrapper_redirect_deletion_is_reported_and_blocked` | The old repository-sync line with `>> .../logs/quality/cron-wrapper.log` will not be silently replaced by the rendered no-redirect line. | Captured ace1 crontab. | Abort/intent report will include old repository-sync line and planned replacement line. | FAIL today. Proof: precise survival command will print `old_repo_sync_line_count 1`, `new_repo_sync_line_count 0`, and the new repository-sync line without redirect. |
| `test_equality_collect_body_deletion_is_reported_and_blocked` | The obsolete equality-report body using `collect-equality.sh && build-equality-matrix.py` will not silently disappear. | Captured ace1 crontab. | Abort/intent report will include the equality line before any planned output may be accepted. | FAIL today. Proof: reproduction command will print `collect_equality_survives=False` and `plan_abort_reason=None`. |
| `test_preserved_external_llm_wiki_wins_before_any_catalog_identity` | The llm-wiki corpus-ingest line will survive verbatim, and preservation will have precedence over any future non-exact catalog match. | Preserved llm-wiki line plus a deliberately colliding catalog-command token in test fixture. | Classification will be `preserved_external`; planned text will retain the line byte-for-byte. | FAIL for the precedence variant today. Proof: `uv run pytest tests/cron/test_a1_preserved.py::test_llm_wiki_corpus_ingest_is_preserved -q` printed `1 passed`, which will prove only the existing non-colliding case; the planned colliding-precedence case will be new RED coverage. |
| `test_no_additional_cataloged_return_sites_are_introduced` | The implementation will preserve exactly one `{'class': 'cataloged'}` dict literal in `cron_line_model.py`. | AST over changed `cron_line_model.py`. | `derive_cron_classifier_branches(records)` will not return `None`; branch set will remain exact unless intentionally updated with matching registry changes. | FAIL if implemented incorrectly; environment-blocked suite today. Proof of trap: `uv run pytest tests/enforcement/test_scheduler_mutation_surfaces.py::test_classifier_branch_set_is_complete_and_exact -q` will currently fail on this Mac at `Git cat-file --batch-command -Z support is required`; on capable Git it will guard the branch set. |
| `test_preservation_attestation_requires_managed_block_classification` | Scheduler mutation attestation will reject a transaction that classifies only before/after lines. | Mutated `cron_transaction.py` records that remove managed-block record traversal. | `evaluate_attestation("python-postwrite-preservation-multiset-v1", ...) is False`. | Environment-blocked on this Mac; semantic gap will remain. Proof: `uv run pytest tests/enforcement/test_scheduler_mutation_task3.py::test_preservation_attestation_proves_plan_reconstruction -q` failed at `Git cat-file --batch-command -Z support is required`, and the existing test body will only mutate before/after preservation, not managed-block traversal. |

Deferred trap tests will not be part of this issue: lock continuity (`cron_apply.py:352-361`) and Python-layer Windows OS guard (`cron_apply.py:366-394`) will be documented as follow-on defects unless the owner expands #3709 before approval.

---

## Acceptance Criteria

- [ ] The captured ace1 crontab segment will produce a non-zero abort that enumerates exactly 47 uncataloged managed-block lines.
- [ ] Every live line in `before`, `managed`, and `after` will be classified before any rebuild will occur.
- [ ] `cron-audit.py` and `plan_cutover` will consume the same shared classification records for the same input.
- [ ] Any line in baseline `A` and absent from planned `C` will appear in an intent report and will require explicit acknowledgement before apply can proceed.
- [ ] The equality `collect-equality.sh && build-equality-matrix.py` body will be blocked/reported rather than silently dropped.
- [ ] The old repository-sync `cron-wrapper.log` redirect line will be blocked/reported rather than silently rewritten.
- [ ] The llm-wiki corpus-ingest line will survive verbatim and preservation precedence will be tested ahead of any future non-exact identity route.
- [ ] No fuzzy command-only cataloging will be added for `notification-purge` or any other task in this issue.
- [ ] The plan will enumerate every way the change could convert unknown into known: exact canonical identity, exact legacy identity, preservation fingerprint, ignore-line parsing, intent acknowledgement, and any renderer/context normalization. Every conversion path will have a fail-closed test or will remain out of scope.
- [ ] Scheduler mutation attestations will still pass on a capable Git/Linux environment, including `uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py` and `uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py --check-html docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html`.
- [ ] `uv run pytest tests/cron/test_cron_apply.py tests/cron/test_cron_identity_task2.py tests/cron/test_a1_preserved.py -q` will pass.
- [ ] `uv run pytest tests/enforcement/test_scheduler_mutation_surfaces.py tests/enforcement/test_scheduler_mutation_hardening.py tests/enforcement/test_scheduler_mutation_task3.py -q` will pass on a host whose Git supports `cat-file --batch-command -Z`.
- [ ] No implementation will run `crontab`, `setup-cron.sh`, `cron_apply.py --apply`, SSH, or any scheduler-mutating command during tests or plan execution.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Codex | MINOR | Self-review will intentionally remain non-APPROVE and will flag residual scope decisions for intent acknowledgement, lock continuity, Windows guard, and enforcement proof on a capable Git host. |

**Overall result:** R1 MINOR only; independent r2 review will remain required before any owner approval.

Revisions made based on review:
- Self-review will be written to `scripts/review/results/2026-07-30-plan-3709-codex-r1.md`. Independent r2 review will still be required before owner approval.

---

## Risks and Open Questions

- **Risk:** The implementation could accidentally add a second `cataloged` return site and break `derive_cron_classifier_branches`; the plan will require preserving one cataloged return or updating all attestation/registry/report surfaces together.
- **Risk:** Moving audit to a shared transaction helper could accidentally drop rich audit detail; the parity test will compare line, location, class, reason, task id, and variant id.
- **Risk:** Intent acknowledgement could become a bypass if it is a broad flag. The implementation will require line-specific acknowledgement keyed by baseline digest and exact line occurrence, or it will keep acknowledgement out of this issue.
- **Risk:** `ignore` classification could convert too much state into safe-to-drop known state. The implementation will keep ignore semantics limited to blank/comment/env lines and will include env-line handling in the intent report so live `WORKSPACE_HUB=` context cannot be silently reinterpreted.
- **Risk:** Exact canonical rendering could convert an unknown drift line into known if renderer context changes. The implementation will keep cataloged authority exact, selected-task-scoped, and machine-context-bound through `build_ownership_context`.
- **Risk:** Legacy exact lines could convert unknown into known if broad rows are added to `harness-state-classes.yaml`. This issue will not add new legacy rows; any future legacy promotion will require exact line text plus tests.
- **Risk:** Preservation fingerprints are intentionally broader than exact identity. They will only preserve verbatim and will never authorize deletion or catalog absorption.
- **Risk:** Lock continuity (`cron_apply.py:352-361`) and Python-layer Windows OS guard (`cron_apply.py:366-394`) will remain adjacent known defects. This plan will defer them from #3709 because the #3709 defect will be the pure pre-rebuild classification/intent path; follow-on issues will be required before any plan re-enables live `setup-cron.sh --replace`.
- **Open:** The implementation owner will decide whether line-specific intent acknowledgement will be included in #3709 or whether #3709 will always abort on any absent non-cataloged live line and leave acknowledgement for a later apply-mode issue.

---

## Complexity: T3

**T3** — this issue will alter a scheduler mutation safety contract across transaction planning, audit reporting, attestation logic, generated reports, and high-risk fail-closed tests. Implementation will remain blocked until user approval.
