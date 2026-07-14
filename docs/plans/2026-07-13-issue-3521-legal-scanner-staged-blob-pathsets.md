# Plan for #3521: Legal Scanner Staged-Blob Pathsets

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-07-13
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3521
> **Client:** N/A
> **Lane:** lane:codex
> **Execution:** `parallel-readonly` planning/review; `single-lane` implementation in this isolated worktree
> **Review artifacts:** `scripts/review/results/2026-07-13-plan-3521-{claude,codex,gemini}.md`

---

## Resource Intelligence Summary

### Existing repo code

- `scripts/legal/legal-sanity-scan.sh:81-107,183-215,229-246` supports only
  legacy repo/all/diff/JSON modes, builds a newline-delimited path list from
  `git diff --name-only HEAD`, reopens mutable worktree files, suppresses Git and
  search errors, silently excludes files over 1 MiB, and interpolates JSON
  without binary-safe framing.
- `.legal-deny-list.yaml:102-128` supplies broad exclusions including the legal
  scanner directory. Strict staged mode will not honor those blanket exclusions;
  it will use same-blob, rule-ID-specific forensic dispositions.
- `scripts/enforcement/check-no-conflict-markers.sh:21-33,86-127` demonstrates
  staged-content sentinels and NUL path discovery, but its shell variable cannot
  preserve arbitrary blob bytes and some Git failures continue silently.
- `scripts/enforcement/check-scheduler-mutation-surfaces.py:86-119` is the
  stronger raw-byte precedent: `ls-files -z` plus `cat-file --batch-command -Z`.
- No test currently targets `legal-sanity-scan.sh`; the 21 legal tests cover
  separate PII/redaction helpers. The related legal/enforcement baseline is
  green at 47 tests.

### Standards

- `docs/standards/CONTROL_PLANE_CONTRACT.md` makes the scanner, versioned schemas,
  and non-sensitive policy durable control-plane artifacts; request/receipt
  files remain external transaction evidence.
- `.claude/rules/patterns.md` classifies this fail-closed check as Level 2 now;
  pre-commit adoption remains #3398-owned and may promote it to Level 3.
- Universal security/legal rules require no secrets, no sensitive identifiers in
  public output, input validation, and a passing legal scan. Receipt findings
  therefore expose rule IDs and byte offsets only—never patterns or snippets.

### LLM Wiki pages consulted

Not applicable. This generic public enforcement issue contains no client or
project identifiers and does not change domain knowledge.

### Documents consulted

- Issue [#3521](https://github.com/vamseeachanta/workspace-hub/issues/3521) —
  requires an explicit caller-selected repo, NUL-safe staged blob set, exact
  byte authority, deterministic edge policies, and machine-readable evidence.
- `docs/plans/2026-05-16-issue-2722-pre-commit-conflict-marker-hook.md` — prior
  reviews established same-staged-blob sentinels, NUL iteration, and the danger
  of path-wide forensic exemptions.
- `docs/plans/2026-07-11-issue-3470-scheduler-mutation-safety-contract.md` —
  precedent for raw-byte Git transport, length framing, and adversarial path
  fixtures; issue 3470 is closed.
- Issue [#3398](https://github.com/vamseeachanta/workspace-hub/issues/3398) —
  remains draft and owns tier-1 pre-commit topology. It will consume this
  scanner contract rather than implement a competing resolver.
- Issue [#3522](https://github.com/vamseeachanta/workspace-hub/issues/3522) —
  separately owns assessment/migration of sensitive rule values already tracked
  in public history. This plan will neither repeat nor expose those values.
- Drive-index query `legal scanner staged blob NUL pathset` returned no relevant
  external documents; results were unrelated engineering files. Two indexes were
  unreachable and three carried staleness warnings, recorded as coverage gaps.

### Gaps identified

- No immutable staged-request/receipt protocol or versioned schemas exist.
- No binary-safe helper reads selected index blobs by verified object ID.
- No deterministic policy exists for untracked/intent-to-add, conflicts,
  deletion, rename, symlink, gitlink, binary, large, or archive entries.
- No post-scan verifier detects index, HEAD, tool, or rule drift before commit.
- No public-safe receipt or narrow forensic mechanism exists for strict mode.
- No stable public rule-ID/private-pattern authority exists; #3522 must provide
  it before strict-mode implementation or activation.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-13T22:30-05:00):

- `#3521` — OPEN — `status:needs-plan`, `lane:codex`.
- `#3398` — OPEN — `status:needs-plan`, `lane:codex`; topology consumer.
- `#3470` — CLOSED — staged/raw-byte transport precedent.
- `#3522` — OPEN — `status:needs-plan`, `lane:codex`; exposure remediation.

**Reproduction proof** (synthetic non-sensitive rule, disposable nested repo):

```text
$ git -C repro-3521 diff --cached --raw --abbrev=40
:100644 100644 83126302079c10762b29692dc322e430472a5360 3ac14b7581bca2b7bd16a92bdb998d50637d2257 M sample.txt
$ git -C repro-3521 diff --name-only HEAD
(empty; worktree equals HEAD while the index contains the prohibited blob)
$ scripts/legal/legal-sanity-scan.sh --repo=repro-3521 --diff-only
RESULT: PASS — no violations found
```

The staged blob contained only the synthetic marker `ZZZ_FORBIDDEN_3521`; the
worktree contained `clean`. The current scanner returned 0, reproducing the issue
exactly. The fixture directory was deleted after capture.

**Baseline:** `uv run --no-project pytest -q scripts/legal/tests
tests/enforcement/test_check_no_conflict-markers.py` → `47 passed in 43.64s`.

Source count: issue body, current scanner, two enforcement precedents, three
prior/related issues, control-plane/rules docs, and drive-index query (9+).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-13-issue-3521-legal-scanner-staged-blob-pathsets.md` |
| Normative protocol | `docs/plans/evidence/2026-07-13-issue-3521-staged-scan-contract.md` |
| Compatibility wrapper | `scripts/legal/legal-sanity-scan.sh` |
| Strict scanner/helper | `scripts/legal/scan_staged_blobs.py` |
| Strict package | `scripts/legal/staged_scan/{model,git_transport,rules,receipt,cli}.py` |
| Focused tests | `scripts/legal/tests/test_staged_scan_{contract,transport,policy}.py` |
| Versioned schemas | `schemas/legal-staged-scan-{request,receipt,rule-registry,rule-map}.schema.json` |
| Non-sensitive strict policy | `config/legal-staged-scan-policy.yaml` |
| Contract documentation | `docs/standards/LEGAL_STAGED_SCAN_CONTRACT.md` |
| User documentation | `.claude/docs/legal-scanning.md` |
| Review artifacts | `scripts/review/results/2026-07-13-plan-3521-{claude,codex,gemini}.md` |
| Plan index | `docs/plans/README.md` |

---

## Deliverable

A versioned, fail-closed staged-request/receipt mode that scans immutable Git
blobs and raw paths, independently regenerates receipts, and detects scan-to-
commit drift against the resulting commit tree. Legacy modes remain explicitly
non-attesting.

---

## Interface and Data Contract

The normative protocol, exact commands, byte framing, request/delta schemas,
rule authority, edge/exit table, atomic-output rules, receipt regeneration, and
post-commit tree verification are frozen in
`docs/plans/evidence/2026-07-13-issue-3521-staged-scan-contract.md`.

V1 accepts an external NUL pathset or an explicit `all-staged` generator. Every
declared path must resolve to the staged delta; untracked/intent-to-add entries
fail closed. Receipts use opaque ordinals and a nonce-salted request commitment,
never path hashes, repository hashes, rule digests, patterns, or snippets.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/legal/legal-sanity-scan.sh` | Add strict-mode dispatch and compatibility help; no binary logic in shell. |
| Create | `scripts/legal/scan_staged_blobs.py` | Binary-safe request, scan, canonical receipt, and verifier. |
| Create | `scripts/legal/staged_scan/*.py` | Split model, Git transport, rule matching, receipt, and CLI below size limits. |
| Create | `scripts/legal/tests/test_staged_scan_*.py` | Hermetic contract/transport/policy TDD matrices. |
| Create | `schemas/legal-staged-scan-request.schema.json` | Freeze caller-to-scanner contract. |
| Create | `schemas/legal-staged-scan-receipt.schema.json` | Freeze evidence/exit contract. |
| Create | `schemas/legal-staged-scan-rule-map.schema.json` | Freeze stable public IDs to private pattern map. |
| Create | `schemas/legal-staged-scan-rule-registry.schema.json` | Freeze non-sensitive ID/target/severity/mode authority. |
| Create | `config/legal-staged-scan-policy.yaml` | Non-sensitive media, limit, sentinel, destination policy. |
| Create | `docs/standards/LEGAL_STAGED_SCAN_CONTRACT.md` | Durable attestation/threat model. |
| Modify | `.claude/docs/legal-scanning.md` | Mark legacy modes non-attesting; document exact commands. |
| Update | `docs/plans/README.md` | Index plan and review state. |

`.legal-deny-list.yaml` and pre-commit callers are out of scope. #3522 must first
land the stable non-sensitive registry/private rule map consumed here. After
#3521 merges, #3398 must be re-planned/re-reviewed against this strict CLI; no
concurrent wrapper/docs edits are permitted.

---

## TDD Test List

| Test | Verification |
|---|---|
| `test_staged_blob_wins_over_clean_worktree` | Staged prohibited/worktree clean fails and receipt OID matches index. |
| `test_clean_staged_blob_ignores_dirty_worktree` | Worktree content cannot contaminate attestation. |
| `test_raw_path_matrix_round_trips` | Space, tab, newline, leading dash, colon, non-UTF-8 paths survive via base64. |
| `test_request_set_equals_all_staged_delta` | Omission, addition, duplicate, absolute, `..`, outside-root, and stale entries fail. |
| `test_explicit_pathset_rejects_untracked` | NUL pathset entries absent/intent-to-add in index fail rather than disappear. |
| `test_identity_drift_fails_closed` | HEAD/index/tool/policy/rule mutation before or during scan returns rc3. |
| `test_git_errors_and_rules_fail_closed` | Missing blobs, Git errors, and missing/empty/malformed rules return rc2/3, never pass. |
| `test_index_edge_matrix` | Old/new mode/OID/null invariants cover add/modify/delete/type-change/rename-as-D+A. |
| `test_symlink_and_gitlink_policy` | Symlink target blob is scanned without dereference; gitlink rejects. |
| `test_media_policy_matrix` | Preflight caps precede contents; binary scans; magic-detected archive/oversize reject. |
| `test_path_rules_cover_all_entry_kinds` | Raw add/delete/symlink paths are scanned without reversible public identifiers. |
| `test_receipt_is_canonical_and_public_safe` | Same request repeats bytes; only ordinals/revision IDs/findings are public. |
| `test_forged_receipt_is_rejected` | Verify independently rescans/regenerates; forged verdict/findings/hash cannot pass. |
| `test_receipt_cannot_self_reference` | In-repo/staged request or receipt paths reject; external receipt binds request only. |
| `test_forensic_policy_is_narrow` | Exact same-line rule-ID sentinel/prefix works; wrong/adjacent/whole-file/arbitrary bypasses fail. |
| `test_rule_authority_is_immutable` | Public registry/private map IDs match; missing/duplicate/mutable/weakened sources fail. |
| `test_post_commit_tree_binding` | Parent/tree/delta match request; mutation after verify is caught on resulting commit. |
| `test_cat_file_protocol_is_strict` | Truncated/wrong/reordered/extra headers or content and boundary collisions fail. |
| `test_atomic_evidence_output` | 0700 dir/0600 files, no-follow/no-overwrite/link-publish/fsync, crash cleanup, rc4 failure. |
| `test_legacy_cli_compatibility` | Existing all/repo/diff/json/quiet modes remain callable and labeled non-attesting. |
| `test_python_size_limits` | New Python files stay ≤400 lines and functions ≤50 lines. |

Tests will create isolated Git repositories and synthetic rules at runtime; no
real client/project/person value will enter source, fixtures, logs, or receipts.

---

## Implementation Sequence

1. Add RED schema/CLI/request-set tests; confirm assertion failures, not import
   or fixture failures.
2. Implement canonical request creation and exact old/new staged-delta parsing.
3. Add RED immutable-blob/path/edge tests; implement batch `cat-file -Z` reads.
4. After #3522 merges, add RED rule/path/media/forensic tests and byte scanning.
5. Add RED receipt/TOCTOU/public-safety tests; implement rescan and commit verify.
6. Wire the shell wrapper and legacy compatibility tests.
7. Update contract/user docs and run the full acceptance sequence.
8. Run T3 adversarial code/artifact review; any later change invalidates the
   staged receipt and requires a fresh request/scan/verify cycle.

---

## Acceptance Criteria

- [ ] RED evidence is captured per task before implementation.
- [ ] #3522 is approved/merged and supplies the stable public-ID/private-map
      contract; exact commits/digests are frozen before implementation.
- [ ] `uv run --no-project pytest -q scripts/legal/tests/test_staged_scan_*.py`
      passes, including every named edge/threat fixture.
- [ ] `uv run --no-project pytest -q scripts/legal/tests
      tests/enforcement/test_check_no_conflict_markers.py` passes.
- [ ] `uv run --no-project python -m compileall -q scripts/legal` passes.
- [ ] Contract commands succeed on an exact synthetic staged set; forged receipt
      or mutation after final pre-commit verify fails rescan/post-commit rc3.
- [ ] Strict mode never opens a worktree target, follows a symlink, suppresses a
      Git/search/rule error, skips a large/binary/archive silently, or echoes a
      pattern/snippet.
- [ ] Schemas reject unknown versions, fields, invalid base64, abbreviated OIDs,
      non-canonical JSON, and request/receipt self-inclusion.
- [ ] Legacy mode compatibility tests pass and documentation calls those modes
      non-attesting.
- [ ] `bash -n scripts/legal/legal-sanity-scan.sh`, schema validation, compileall,
      focused tests, and the 47-test baseline pass with their documented codes.
- [ ] Strict `pathset → request → scan → verify → commit → verify-commit` scans
      the exact staged implementation transaction; legacy scan is compatibility
      evidence only and cannot satisfy self-scan acceptance.
- [ ] T3 code/artifact review has no MAJOR; issue receives implementation summary
      and source-consumption comment. No self-merge or self-close occurs.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude r1 | MAJOR | receipt trust, commit TOCTOU, public disclosure, rule/self-scan, framing/limits incomplete |
| Codex r1 | MAJOR | edge schema, rule/path authority, framing/exits, dependencies, modularity incomplete |
| Gemini r1 | UNAVAILABLE | noninteractive OAuth rc41 |
| r2 | pending | exact revised plan and normative protocol require review |

**Overall result:** draft; implementation is blocked pending review and explicit
user approval. No agent may apply `status:plan-approved` or create its marker.

---

## Risks and Open Questions

- **Security incident:** #3522 owns private-rule migration/history assessment;
  it is a hard dependency and this issue must not echo or expand the exposure.
- **Adoption overlap:** #3521 lands first; then #3398 is revised/re-reviewed to
  consume this CLI/schema. #3521 will not edit tier-1 pre-commit configs.
- **Git portability:** implementation will assert minimum Git support for
  `cat-file --batch-command -Z`; unsupported versions return configuration error.
- **Resource bounds:** strict policy will cap total/request/blob sizes and reject
  unsupported inputs rather than degrade to a skip.

---

## Complexity: T3

Cross-cutting public security enforcement, binary-safe Git transport, versioned
evidence schemas, TOCTOU defense, and self-scanning policy require three-provider
plan and code review.
