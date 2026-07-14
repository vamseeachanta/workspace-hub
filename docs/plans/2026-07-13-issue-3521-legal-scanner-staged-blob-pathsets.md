# Plan for #3521: Legal Scanner Staged-Blob Pathsets

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-07-13
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3521
> **Client:** N/A
> **Lane:** lane:codex
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
| Compatibility wrapper | `scripts/legal/legal-sanity-scan.sh` |
| Strict scanner/helper | `scripts/legal/scan_staged_blobs.py` |
| Focused tests | `scripts/legal/tests/test_scan_staged_blobs.py` |
| Request/receipt schemas | `schemas/legal-staged-scan-{request,receipt}.schema.json` |
| Non-sensitive strict policy | `config/legal-staged-scan-policy.yaml` |
| Contract documentation | `docs/standards/LEGAL_STAGED_SCAN_CONTRACT.md` |
| User documentation | `.claude/docs/legal-scanning.md` |
| Review artifacts | `scripts/review/results/2026-07-13-plan-3521-{claude,codex,gemini}.md` |
| Plan index | `docs/plans/README.md` |

---

## Deliverable

A versioned, fail-closed staged-request/receipt mode that scans immutable Git
index blobs for one explicit repository, preserves arbitrary path bytes, detects
TOCTOU, emits public-safe deterministic evidence, and leaves legacy modes
available but explicitly non-attesting.

---

## Interface and Data Contract

```bash
evidence_dir="${TMPDIR:-/tmp}/legal-stage-${USER}"
mkdir -p "$evidence_dir"
uv run --no-project python scripts/legal/scan_staged_blobs.py request \
  --repo-root . --scope all-staged --destination private \
  --out "$evidence_dir/request.json"
scripts/legal/legal-sanity-scan.sh --repo-root=. \
  --staged-request="$evidence_dir/request.json" \
  --receipt="$evidence_dir/receipt.json"
uv run --no-project python scripts/legal/scan_staged_blobs.py verify \
  --repo-root . --request "$evidence_dir/request.json" \
  --receipt "$evidence_dir/receipt.json"
```

- `--repo-root`, `--staged-request`, and `--receipt` form one mutually exclusive
  strict mode. Existing `--repo`, `--all`, `--diff-only`, `--json`, and `--quiet`
  retain compatible non-attesting behavior.
- `request` is the only request generator. V1 supports `scope=all-staged`; its
  entry set must equal `git diff-index --cached --raw -z --no-renames HEAD --`.
  Callers stage only the intended transaction before generating the request.
- Request and receipt must be regular files outside the selected repo and staged
  set. The receipt does not hash itself; the caller hashes it after atomic close.
- Exit codes: 0 clean, 1 prohibited finding, 2 usage/configuration, 3 integrity,
  unsupported transport/media, or TOCTOU. Once request validation begins, every
  exit produces an atomic failure/success receipt.

Request schema v1 binds schema/tool/policy/rule digests, normalized repository
identity hash, expected HEAD, Git object format, destination, scope, logical
index digest, selected-set digest, and entries containing `path_b64`, status,
mode, stage, full Git OID, and expected blob size/SHA-256 where applicable.

Receipt schema v1 binds the request digest, start/end HEAD and logical-index
digests, start/end tool/policy/rule digests, per-entry path identity, status,
mode, OID, blob SHA-256, size, media class, disposition, rule-ID/offset findings,
suppressions, overall verdict, and exit classification. It never includes rule
patterns or matched snippets. Public destination receipts replace reversible
paths with SHA-256 path IDs; private receipts may include `path_b64`.

---

## Pseudocode

```text
request(repo_root, scope, destination, out):
    canonicalize repo without following a caller path outside its Git root
    require clean index stages and scope == all-staged
    read HEAD/object format and full index with NUL-safe Git plumbing
    derive no-rename staged delta; reject intent-to-add and untracked requests
    emit canonical JSON request atomically outside repo

scan(request, receipt):
    validate schemas, repo identity, paths, HEAD, index, tool/policy/rule digests
    open cat-file --batch-command -Z and read every regular/symlink blob by OID
    apply byte-safe rules and same-blob forensic dispositions
    reject unsupported mode/media; never follow symlinks or recurse gitlinks
    re-read all identities; drift changes verdict to integrity failure
    atomically write deterministic receipt without patterns/snippets/self-hash

verify(repo, request, receipt):
    validate both schemas and request digest
    recompute current HEAD/index/tool/policy/rule identities
    require exact entry set, modes, stages, OIDs, and successful receipt verdict
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/legal/legal-sanity-scan.sh` | Add strict-mode dispatch and compatibility help; no binary logic in shell. |
| Create | `scripts/legal/scan_staged_blobs.py` | Binary-safe request, scan, canonical receipt, and verifier. |
| Create | `scripts/legal/tests/test_scan_staged_blobs.py` | Hermetic TDD matrix. |
| Create | `schemas/legal-staged-scan-request.schema.json` | Freeze caller-to-scanner contract. |
| Create | `schemas/legal-staged-scan-receipt.schema.json` | Freeze evidence/exit contract. |
| Create | `config/legal-staged-scan-policy.yaml` | Non-sensitive media, limit, sentinel, destination policy. |
| Create | `docs/standards/LEGAL_STAGED_SCAN_CONTRACT.md` | Durable attestation/threat model. |
| Modify | `.claude/docs/legal-scanning.md` | Mark legacy modes non-attesting; document exact commands. |
| Update | `docs/plans/README.md` | Index plan and review state. |

`.legal-deny-list.yaml` and pre-commit callers are out of scope: strict mode will
parse rule definitions but ignore its blanket target exclusions. #3522 owns
sensitive-value migration; #3398 owns tier-1 hook adoption after this merges.

---

## TDD Test List

| Test | Verification |
|---|---|
| `test_staged_blob_wins_over_clean_worktree` | Staged prohibited/worktree clean fails and receipt OID matches index. |
| `test_clean_staged_blob_ignores_dirty_worktree` | Worktree content cannot contaminate attestation. |
| `test_raw_path_matrix_round_trips` | Space, tab, newline, leading dash, colon, non-UTF-8 paths survive via base64. |
| `test_request_set_equals_all_staged_delta` | Omission, addition, duplicate, absolute, `..`, outside-root, and stale entries fail. |
| `test_identity_drift_fails_closed` | HEAD/index/tool/policy/rule mutation before or during scan returns rc3. |
| `test_git_errors_and_rules_fail_closed` | Missing blobs, Git errors, and missing/empty/malformed rules return rc2/3, never pass. |
| `test_index_edge_matrix` | Add/modify/delete/type-change/rename-as-delete-add are deterministic; conflicts/intent-to-add reject. |
| `test_symlink_and_gitlink_policy` | Symlink target blob is scanned without dereference; gitlink rejects. |
| `test_media_policy_matrix` | Binary bytes scan case-sensitive rules; undecodable case-insensitive, archive, oversize, and unknown policy reject explicitly. |
| `test_receipt_is_canonical_and_public_safe` | Repeated bytes match; JSON validates; public receipt has no pattern/snippet/reversible path. |
| `test_receipt_cannot_self_reference` | In-repo/staged request or receipt paths reject; external receipt binds request only. |
| `test_forensic_policy_is_narrow` | Same-blob rule-ID line sentinel works only under approved prefixes; blanket/arbitrary exemptions fail. |
| `test_rule_source_structural_disposition` | Exact parsed pattern fields in rule-source files avoid self-block; other content remains scanned. |
| `test_private_destination_never_bypasses` | Destination changes disclosure only, never finding verdict. |
| `test_legacy_cli_compatibility` | Existing all/repo/diff/json/quiet modes remain callable and labeled non-attesting. |
| `test_python_size_limits` | New Python files stay ≤400 lines and functions ≤50 lines. |

Tests will create isolated Git repositories and synthetic rules at runtime; no
real client/project/person value will enter source, fixtures, logs, or receipts.

---

## Implementation Sequence

1. Add RED schema/CLI/request-set tests; confirm assertion failures, not import
   or fixture failures.
2. Implement canonical request creation and exact staged-delta/index parsing.
3. Add RED immutable-blob/path/edge tests; implement batch `cat-file -Z` reads.
4. Add RED rule/media/forensic tests; implement fail-closed byte scanning.
5. Add RED receipt/TOCTOU/public-safety tests; implement atomic receipt/verify.
6. Wire the shell wrapper and legacy compatibility tests.
7. Update contract/user docs and run the full acceptance sequence.
8. Run T3 adversarial code/artifact review; any later change invalidates the
   staged receipt and requires a fresh request/scan/verify cycle.

---

## Acceptance Criteria

- [ ] RED evidence is captured per task before implementation.
- [ ] `uv run --no-project pytest -q scripts/legal/tests/test_scan_staged_blobs.py`
      passes, including every named edge/threat fixture.
- [ ] `uv run --no-project pytest -q scripts/legal/tests
      tests/enforcement/test_check_no_conflict_markers.py` passes.
- [ ] `uv run --no-project python -m compileall -q scripts/legal` passes.
- [ ] Request, scan, and verify commands above succeed on an exact synthetic
      staged set; mutation after scan makes verify return rc3.
- [ ] Strict mode never opens a worktree target, follows a symlink, suppresses a
      Git/search/rule error, skips a large/binary/archive silently, or echoes a
      pattern/snippet.
- [ ] Schemas reject unknown versions, fields, invalid base64, abbreviated OIDs,
      non-canonical JSON, and request/receipt self-inclusion.
- [ ] Legacy mode compatibility tests pass and documentation calls those modes
      non-attesting.
- [ ] `scripts/legal/legal-sanity-scan.sh --diff-only` and all repository
      enforcement checks pass on the exact staged implementation set.
- [ ] T3 code/artifact review has no MAJOR; issue receives implementation summary
      and source-consumption comment. No self-merge or self-close occurs.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | pending | fresh exact-revision review required |
| Codex | pending | fresh exact-revision review required |
| Gemini | pending | fresh exact-revision review or documented unavailability |

**Overall result:** draft; implementation is blocked pending review and explicit
user approval. No agent may apply `status:plan-approved` or create its marker.

---

## Risks and Open Questions

- **Security incident:** #3522 owns private-rule migration/history assessment;
  this issue must not echo or expand the exposure.
- **Adoption overlap:** #3398 must consume this CLI/schema and remain separately
  approved; #3521 will not edit tier-1 pre-commit configs.
- **Git portability:** implementation will assert minimum Git support for
  `cat-file --batch-command -Z`; unsupported versions return configuration error.
- **Resource bounds:** strict policy will cap total/request/blob sizes and reject
  unsupported inputs rather than degrade to a skip.

---

## Complexity: T3

Cross-cutting public security enforcement, binary-safe Git transport, versioned
evidence schemas, TOCTOU defense, and self-scanning policy require three-provider
plan and code review.
