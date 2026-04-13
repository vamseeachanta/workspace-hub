# Plan for #2245: Prepare Summary/Classification Artifacts to Unblock Bounded ACMA Wiki Promotion

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-12
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2245
> **Parent:** https://github.com/vamseeachanta/workspace-hub/issues/2216
> **Blocked follow-on:** https://github.com/vamseeachanta/workspace-hub/issues/2227
> **Review artifacts:** scripts/review/results/2026-04-12-plan-2245-review-a.md | scripts/review/results/2026-04-12-plan-2245-review-b.md | scripts/review/results/2026-04-12-plan-2245-final.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/data/document-index/phase-b-extract.py` — Phase B extractor/summarizer can process `--source acma_codes`, but it writes summary files using a derived 16-character key and targets the configured summaries directory.
- Found: `scripts/data/document-index/phase-b-claude-worker.py` — writes richer summary JSON keyed by full `content_hash`, but its CLI source choices currently do not include `acma_codes`.
- Found: `scripts/data/document-index/phase-c-classify.py` — classifies records using available summaries and writes domain/status into planning outputs; current logic expects summary files by SHA-named JSON under the configured summaries directory.
- Found: `scripts/data/document-index/config.yaml` — `output.summaries_dir` points to `/mnt/remote/ace-linux-1/ace/data/document-index/summaries`, which is currently unavailable on this machine.
- Gap: there is no existing targeted command or script for preparing bounded summary/classification artifacts for exactly the three #2245/#2227 target documents.

### Standards
| Standard | Status | Source |
|---|---|---|
| `OCIMF-TANDEM-MOORING` | ledger-backed; index record present; summary/domain currently null | `data/document-index/standards-transfer-ledger.yaml` + `data/document-index/index.jsonl` |
| `CSA-Z276.1-20` | ledger-backed; index record present; summary/domain currently null | `data/document-index/standards-transfer-ledger.yaml` + `data/document-index/index.jsonl` |
| `CSA-Z276.18` | ledger-backed; index record present; summary/domain currently null | `data/document-index/standards-transfer-ledger.yaml` + `data/document-index/index.jsonl` |
| `CSA-Z276.2-19` | ledger-backed but explicitly out of scope for this issue | `data/document-index/standards-transfer-ledger.yaml` + #2226 plan |

### LLM Wiki pages consulted
- No existing wiki pages for the three bounded target docs.
- `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` exists and is blocked on upstream artifacts before #2227 can update it safely.

### Documents consulted
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` — #2207 requires registered doc, non-empty summary artifact, valid domain classification, and concrete provenance back-links before wiki promotion.
- `docs/plans/2026-04-12-issue-2227-ocimf-tandem-csa-z276-wiki-promotion.md` — #2227 execution is blocked pending these prerequisite artifacts.
- `docs/plans/2026-04-11-issue-2226-ocimf-csa-ledger-provenance-backfill.md` — authoritative source for the bounded target IDs and out-of-scope breadth.
- `scripts/data/document-index/config.yaml` — configured summary output path currently points to a missing remote mount on this machine.
- GitHub issue #2245 — bounded unblock scope and acceptance criteria.
- GitHub issue #2245 approval-intent comment — operator approved proceeding to this unblocker next.

### Gaps identified
- The configured summaries directory is currently unavailable on this machine (`/mnt/remote/ace-linux-1/...` missing).
- The three bounded targets have index records but `summary: null` and `domain: null`.
- Existing Phase B / Phase C tooling is not obviously set up for a bounded three-document ACMA-only unblock pass without either a targeted override or a small helper path.
- Without an explicit bounded path, running broad `--source acma_codes` processing risks touching many out-of-scope ACMA docs.

<!-- Verification: distinct sources consulted = 7+ (issue #2245, #2227 plan, #2226 plan, #2207 contract, config.yaml, phase-b-extract.py, phase-b-claude-worker.py, phase-c-classify.py, index.jsonl, ledger). -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-12-issue-2245-acma-summary-classification-unblock.md` |
| Plan review A | `scripts/review/results/2026-04-12-plan-2245-review-a.md` |
| Plan review B | `scripts/review/results/2026-04-12-plan-2245-review-b.md` |
| Review synthesis | `scripts/review/results/2026-04-12-plan-2245-final.md` |
| Likely implementation script changes | `scripts/data/document-index/phase-b-claude-worker.py`, `scripts/data/document-index/phase-c-classify.py` |
| Possible helper/runner | `scripts/data/document-index/prepare-acma-wiki-unblock.py` (new, only if needed) |
| Config/doc references | `scripts/data/document-index/config.yaml`, `data/document-index/index.jsonl`, `data/document-index/standards-transfer-ledger.yaml` |
| Bounded output artifacts | summary/classification artifacts for the three target docs, plus #2227 handoff note/comment |
| Plan index update | `docs/plans/README.md` |

---

## Deliverable

A bounded, reproducible path that produces or explicitly blocks the required summary/classification artifacts for `OCIMF-TANDEM-MOORING`, `CSA-Z276.1-20`, and `CSA-Z276.18`, with exact artifact refs that #2227 can consume without broadening scope.

---

## Scope Boundaries

### In scope now
- Confirm exact index/ledger identity for the three bounded targets.
- Produce or verify non-empty reusable summary artifacts for those targets.
- Produce or verify valid domain classification for those targets.
- Record an exact handoff chain back to #2227.
- If the configured summary path is unavailable, implement the minimum bounded workaround or else document a blocker.

### Explicitly out of scope
- Broad Phase B/Phase C processing for all `acma_codes` documents.
- Processing `CSA-Z276.2-19`, `CSA-B625-13`, `CSA-22.1-12`, or broader API breadth.
- Wiki page creation or updates (#2227 scope).
- Ledger/schema redesign.
- Broad mount/infra redesign outside what is minimally required to unblock the three bounded targets.

---

## Pseudocode

```text
identify three bounded target records in index.jsonl by ledger-backed path/title/content_hash

for each target:
    confirm ledger entry exists
    confirm index record exists
    capture canonical content_hash/path/title

check configured summaries output path:
    if available:
        use it
    else:
        implement a bounded local override/workaround or stop with explicit blocker

prepare summaries for exactly the three targets:
    prefer existing Phase B tooling with a bounded filter
    if existing tooling cannot safely bound to three targets:
        add a minimal helper path that accepts an explicit target list

prepare domain classification for exactly the three targets:
    use existing Phase C logic if possible
    otherwise apply the smallest bounded classification step necessary for these three targets

verify outputs:
    summary artifact exists and non-empty
    classification exists and is valid for wiki promotion
    exact artifact refs are documented for #2227

if any prerequisite still cannot be produced safely:
    stop and document blocker in GitHub with exact reason and next action
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/data/document-index/phase-b-claude-worker.py` | allow bounded processing of the exact three target docs if this is the smallest safe path |
| Modify | `scripts/data/document-index/phase-c-classify.py` | support bounded/local summary resolution if needed for the three targets |
| Create (only if smaller/cleaner than broad patching) | `scripts/data/document-index/prepare-acma-wiki-unblock.py` | one bounded runner for target record selection + summary/classification prep |
| Update | `docs/plans/README.md` | add canonical plan row for #2245 |
| Possibly create bounded artifact note | `docs/plans/2026-04-12-issue-2245-acma-summary-classification-unblock.md` follow-up sections / GitHub comment refs | handoff to #2227 |

---

## TDD / Verification List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| verify_target_identity_resolution | each target resolves from ledger to index record | target IDs | exact content_hash/path/title for 3 docs |
| verify_bounded_processing_only | implementation touches only the three bounded targets | target list | no extra ACMA docs processed |
| verify_summary_artifacts_exist | each target gets a non-empty summary artifact | 3 target records | 3 non-empty summary JSON artifacts |
| verify_domain_classification_present | each target gets a valid domain classification | 3 target records | valid domain values suitable for #2227 |
| verify_handoff_refs_documented | #2227 can see the exact artifact refs to consume | output note/comment | explicit refs for all 3 targets |
| verify_blocker_path_if_missing_mount | if summary path cannot be used, issue reports blocker or bounded workaround | missing mount scenario | explicit stop or bounded fallback, not silent failure |

---

## Acceptance Criteria

- [ ] each bounded target has a confirmed registry/index identity
- [ ] each bounded target has a non-empty reusable summary artifact or an explicit documented blocker
- [ ] each bounded target has a valid domain classification for wiki promotion
- [ ] handoff back to #2227 names the exact artifact refs to consume
- [ ] no out-of-scope CSA/API breadth is silently processed
- [ ] implementation uses the smallest bounded tooling change necessary

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Review A | PENDING | pending review |
| Review B | PENDING | pending review |

**Overall result:** PENDING

Revisions made based on review:
- pending

---

## Risks and Open Questions

- **Risk:** the configured summaries path is unavailable on this machine; implementation may need a bounded local override instead of the default path.
- **Risk:** broad `acma_codes` processing would violate scope discipline; the implementation must stay target-list-bounded.
- **Risk:** existing Phase B/Phase C tool contracts may not cleanly support targeted operation without a small helper or patch.
- **Open:** is the preferred fix a local summaries-dir override or a one-off bounded helper that writes the artifacts explicitly for these three docs?
- **Open:** should classification be written back into the main index directly or materialized in a separate bounded handoff artifact if index mutation is too broad?

---

## Complexity: T2

**T2** — bounded multi-file data-pipeline unblock work requiring careful reuse of existing tooling, exact target selection, and explicit anti-scope-creep controls.
