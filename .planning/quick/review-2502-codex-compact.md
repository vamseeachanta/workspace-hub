You are an adversarial reviewer. Assume the plan has defects until proven otherwise. Do not praise. Do not restate the plan. Focus only on what is wrong, missing, or risky. Return APPROVE only after affirmatively verifying each correctness-critical claim. When in doubt, return MINOR or MAJOR. Each finding must cite a specific plan section or quoted claim.

Review this current draft for GitHub issue #2502. Output exactly:
## Verdict
APPROVE|MINOR|MAJOR

## Retrieval
- list what you checked

## Findings
numbered findings, or "None"

## Blockers
blocking findings only, or "None"

Key review focus:
1. Are all prior blockers resolved? Prior last blockers were: unsafe arbitrary verdict token extraction; canonical filename inconsistency between timestamped vs date-only paths; stale renderer/header scope summary; duplicate test file ownership.
2. Is the plan executable without implementation ambiguity?
3. Does it avoid changing user approval/dispatch authority?
4. Does it define enough tests and exact files?

PLAN:
```markdown
# Plan for #2502: Harden plan-review artifact metadata and stale-SHA handling

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-27 UTC / 2026-04-26 local
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2502
> **Review artifacts:** scripts/review/results/2026-04-26-plan-2502-claude.md | scripts/review/results/2026-04-26-plan-2502-codex.md | scripts/review/results/2026-04-26-plan-2502-gemini.md | scripts/review/results/2026-04-26-plan-2502-disagreement.md

---

## Resource Intelligence Summary

### Existing repo code
- `scripts/ai/continuous-planning-pipeline.py` discovers provider artifacts with `scripts/review/results/*-plan-*-*.md`, derives issue/provider from filename, and currently stores only path, empty flag, verdict, and `plan_sha256`.
- `scripts/ai/continuous-planning-pipeline.py` currently accepts the first `APPROVE|MINOR|MAJOR|UNAVAILABLE` token anywhere in an artifact. That is not safe for review artifacts that quote prompts, examples, or prose such as “No MAJOR blockers” before the true verdict.
- `scripts/ai/continuous-planning-pipeline.py` currently accepts any line exactly matching `Plan-SHA256: <64 hex>`, even if that line appears inside a fenced quote of the plan body rather than in artifact metadata.
- `scripts/review/plan-review-fanout.sh` is the canonical Step 4 plan-review fanout. It currently writes provider stdout directly to `scripts/review/results/YYYY-MM-DD-plan-NNN-<provider>.md`, overwriting same-day reruns. #2502 must replace that producer path with a collision-free timestamped form such as `YYYY-MM-DDTHHMMSSZ-plan-NNN-<provider>.md` while keeping the consumer able to classify older `YYYY-MM-DD-plan-NNN-<provider>.md` legacy artifacts.
- `scripts/review/submit-to-claude.sh`, `submit-to-codex.sh`, `submit-to-gemini.sh`, `scripts/review/render-structured-review.py`, and `scripts/review/cross-review.sh` are adjacent generic review tools, but their timestamped files do **not** match the canonical plan-review filename pattern `YYYY-MM-DDTHHMMSSZ-plan-NNN-<provider>.md`. #2502 deliberately keeps continuous-planning provider-slot ingestion limited to canonical fanout artifacts. Adjacent wrapper/cross-review outputs remain audit logs unless a future issue adds a canonical copy/export mode with the same metadata contract.
- `scripts/review/plan-review-fanout.sh` currently runs Gemini with `( cd /tmp && gemini -p "$combined" )`, which has produced trust-directory failures in current review waves. The #2502 producer fix must keep fanout’s direct raw-output capture model and set `GEMINI_CLI_TRUST_WORKSPACE=true` plus the current non-interactive trust bypass flag used by the installed CLI (`--yolo` if still valid, otherwise the CLI-documented replacement). A regression test must fail if neither env nor trust flag is present.

### Standards
| Standard | Status | Source |
|---|---|---|
| Planning workflow / review artifact convention | applicable, needs update | `docs/plans/README.md` lines 75-104 currently documents overwrite-prone `YYYY-MM-DD-plan-NNN-<agent>.md`; #2502 must update it to collision-free `YYYY-MM-DDTHHMMSSZ-plan-NNN-<agent>.md` while documenting legacy dated artifacts as readable but not newly produced |
| Harness/infra retrieval contract | applicable | `docs/plans/README.md` Step 2 requires Harness/Infra issues to consult `docs/standards/CONTROL_PLANE_CONTRACT.md`, `config/agents/` settings, and `.claude/rules/`; verified surfaces include `config/agents/provider-capabilities.yaml`, provider config/state snapshot directories, and `.claude/rules/{README.md,coding-style.md,patterns.md,calc-citation-contract.md}` |
| AI review routing policy | applicable | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` |
| Hard-stop policy | contextual only | `docs/standards/HARD-STOP-POLICY.md` applies to engineering-critical labels; #2502 is harness/workflow, so AGENTS planning gates apply but engineering hard-stop gates are not direct scope |

### Documents consulted
- Issue #2502 — requires machine-checkable fields: issue, plan path, plan commit, Plan-SHA256, provider/perspective, verdict, timestamp, and reviewed revision.
- `docs/standards/CONTROL_PLANE_CONTRACT.md`, `config/agents/provider-capabilities.yaml`, representative provider config/state snapshot directories under `config/agents/`, and `.claude/rules/README.md` plus rule files — consulted because #2502 is labeled `cat:harness` and modifies control-plane review evidence.
- `docs/standards/HARD-STOP-POLICY.md` — consulted for boundary verification; not directly applicable because #2502 lacks engineering-critical labels.
- #2489 plan/report — introduced Lane A/B review-evidence gating and made stale-vs-missing review evidence operational.
- `docs/reports/continuous-planning-pipeline.md` — current report has review-warning families: `legacy_review_no_sha`, `sha_mismatch_review`, `missing_review`, `empty_review`, `unavailable_review`, and `unknown_review`.
- First and second adversarial review waves for this plan — both returned Claude/Codex MAJOR and are incorporated here.

### Gaps identified
- No authoritative metadata contract document for plan-review artifacts.
- No canonical parser for issue/provider/path/commit/SHA/timestamp/reviewed-revision metadata.
- No deterministic selection rule when multiple candidate artifacts exist for the same issue/provider.
- No producer-side test proving fanout success and failure artifacts carry metadata while preserving raw provider output.
- Canonical fanout path reuses only the date, so same-day reruns overwrite earlier provider artifacts and defeat the audit/history requirement.
- No explicit impact report for existing legacy/stale artifacts that stricter validation will remove from Lane A/B clean evidence.

### Evidence
- Current warning counts from `docs/reports/continuous-planning-pipeline.md`: `legacy_review_no_sha: 31`, `sha_mismatch_review: 1`, `missing_review: 31`, `empty_review: 1`, `unavailable_review: 5`, `unknown_review: 5`.
- Current parser/function locations: `parse_verdict`, `parse_plan_sha`, `discover_reviews`, and `review_summary` in `scripts/ai/continuous-planning-pipeline.py`.
- Current fanout failure path is lines 109-124 in `scripts/review/plan-review-fanout.sh`.
- Current submit-wrapper/cross-review outputs use noncanonical timestamped filenames; they are audit context for #2502, not provider-slot evidence unless a future canonical export mode is added.

---

## Canonical metadata header schema

The implementation must create `docs/standards/PLAN_REVIEW_ARTIFACT_CONTRACT.md` and use the following exact header grammar there and in tests. The header starts at byte 0 of the file and ends at the first blank line. Metadata lines after the first blank line are review-body prose and must not be used for trust decisions.

```text
Review-Artifact-Version: 1
Review-Artifact-Role: provider-review
Issue: <decimal issue number>
Plan-Path: docs/plans/YYYY-MM-DD-issue-NNN-slug.md
Plan-Commit: <40 hex git commit SHA for clean committed plan bytes, or WORKTREE:<64 lowercase plan_sha256> for explicitly local draft artifacts>
Plan-SHA256: <64 lowercase hex content hash of the reviewed plan file>
Reviewed-Revision: <same value as Plan-Commit unless reviewing an immutable external revision>
Provider: claude|codex|gemini
Perspective: claude|codex|gemini
Verdict: APPROVE|MINOR|MAJOR|UNAVAILABLE
Reviewed-At-UTC: YYYY-MM-DDTHH:MM:SSZ
```

Rules:
- `Plan-SHA256` is authoritative only in this header before the first blank line. `Plan-SHA256` lines in fenced code blocks, quotes, or later prose are ignored.
- `Issue`, `Plan-Path`, `Provider`, `Perspective`, `Plan-SHA256`, and `Plan-Commit`/`Reviewed-Revision` must bind to the currently evaluated plan. A mismatch makes the artifact `untrusted_review_metadata`. For the default provider slots, `Perspective` must exactly equal `Provider`; specialized review perspectives are out of scope for #2502 and cannot satisfy provider slots.
- For local draft review waves where the plan is not committed yet, `Plan-Commit` and `Reviewed-Revision` may use the explicit `WORKTREE:<plan_sha256>` sentinel. Implementation must document that those artifacts are valid for draft review, but the continuous planning pipeline must classify them as `draft_bound_review` and **not clean Lane A/B evidence**. They must be regenerated after the plan is committed before an issue is surfaced as approval-ready or execution-ready.
- Producers may emit a git SHA in `Plan-Commit` only when `git show <sha>:<plan_path>` exists and its SHA256 equals the reviewed worktree bytes. If the plan path is untracked or dirty relative to `HEAD`, the producer must emit `WORKTREE:<plan_sha256>` instead of falsely binding worktree-only bytes to `HEAD`.
- Draft/local plans may be reviewed before they exist on `origin/main`; draft-bound artifacts are diagnostics only. Promotion to `status:plan-review` remains the existing manual governance workflow, and #2502 does not add a label-enforcement hook. Operators must regenerate commit-bound artifacts after the plan commit before treating review evidence as approval-ready.
- `Verdict` is required in the header. If `Verdict` is missing, the artifact is `metadata_incomplete`; the parser must not recover trust from a body `## Verdict` section. Body verdict sections may still be rendered for humans, but they are not machine authority.
- Plan-review contract verdicts are exactly `APPROVE|MINOR|MAJOR|UNAVAILABLE`. A raw/header `REJECT` in an ingested canonical artifact is `metadata_incomplete` or `untrusted_review_metadata` rather than clean evidence. Renderer `REJECT` normalization is out of scope because generic submit-wrapper/cross-review artifacts are not provider-slot evidence in #2502.
- `Review-Artifact-Role: disagreement` or any artifact whose filename provider segment is not one of the configured providers remains synthesis-only and never satisfies a provider slot.
- If `Plan-SHA256` is missing entirely, status is `legacy_review_no_sha`. The existing `--allow-legacy-review-artifacts` flag must no longer make legacy artifacts clean Lane A/B evidence; at most it may downgrade legacy findings to diagnostics in non-dispatch reports. Lane A/B readiness always requires metadata-bound current artifacts.
- If `Plan-SHA256` is present but another required field is missing, status is `metadata_incomplete`.
- If duplicate metadata keys appear in the header and values differ, status is `untrusted_review_metadata`.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-27-issue-2502-plan-review-artifact-metadata-stale-sha.md` |
| Contract doc | `docs/standards/PLAN_REVIEW_ARTIFACT_CONTRACT.md` |
| Pipeline consumer | `scripts/ai/continuous-planning-pipeline.py` |
| Canonical plan-review producer | `scripts/review/plan-review-fanout.sh` |
| Adjacent review wrappers | `scripts/review/render-structured-review.py`, `scripts/review/submit-to-*.sh`, `scripts/review/cross-review.sh` — explicitly audit-only/out-of-ingestion for #2502 unless their output is exported to the canonical filename pattern by future work |
| Tests | `tests/analysis/test_continuous_planning_pipeline.py` and `tests/review/test_plan_review_fanout.py` |
| Plan index | `docs/plans/README.md` |

---

## Deliverable

A documented, test-backed provider review artifact contract plus parser/producer hardening so the #2489 continuous planning pipeline can distinguish current clean provider evidence from stale, untrusted, missing, empty, disagreement-only, legacy/no-SHA, unavailable, and unknown artifacts without changing user-approval or implementation-dispatch authority.

---

## Pseudocode

```
function parse_metadata_header(text):
    header = text before first blank line
    parse KEY: value lines only from header
    if duplicate key with different value: return untrusted_review_metadata
    return metadata

function parse_review_artifact(path, current_plan_path, current_plan_sha, current_plan_commit, expected_issue, expected_provider):
    text = read artifact
    if text empty: return empty_review
    if filename/provider not in required providers: ignore for provider slot
    metadata = parse_metadata_header(text)
    if metadata.Plan-SHA256 missing: return legacy_review_no_sha
    require Review-Artifact-Version == "1" and Review-Artifact-Role == "provider-review"
    if required field other than Plan-SHA256 missing: return metadata_incomplete
    if metadata.Issue != expected_issue: return untrusted_review_metadata
    if metadata.Provider != expected_provider: return untrusted_review_metadata
    if metadata.Plan-Path != current_plan_path: return untrusted_review_metadata
    if metadata.Plan-SHA256 != current_plan_sha: return sha_mismatch_review
    if metadata.Plan-Commit and Reviewed-Revision are both git SHAs:
        require both equal the evaluated plan commit/revision
        require git blob at Plan-Commit:Plan-Path exists and sha256(blob bytes) == metadata.Plan-SHA256
    else if values use WORKTREE sentinel:
        require WORKTREE:<current_plan_sha>
        return draft_bound_review (valid for draft diagnostics, non-clean for Lane A/B)
    else: return untrusted_review_metadata
    verdict = metadata.Verdict
    if verdict == UNAVAILABLE: return unavailable_review
    if verdict == MAJOR: return major_review
    return clean review evidence

function discover_reviews(root, providers):
    collect only canonical candidate files matching YYYY-MM-DDTHHMMSSZ-plan-<issue>-<provider>.md plus legacy YYYY-MM-DD-plan-<issue>-<provider>.md for diagnostics/backward compatibility
    ignore timestamped cross-review/submit-wrapper files such as <timestamp>-<source>-plan-<provider>.md unless a future issue explicitly adds canonical export/copy support
    parse each candidate with current plan binding
    deterministic selection:
        1. group all current artifacts for the same issue/provider before choosing any winner
        2. if multiple current artifacts for same issue/provider have different verdict/status/SHA/commit bindings, block with multiple_review_artifacts
        3. if multiple current artifacts are semantically identical, select the artifact with latest valid Reviewed-At-UTC, then lexicographically latest path as a stable tie-breaker, and report duplicate_current_review as an audit warning
        4. only after conflict checks, prefer the current clean metadata-bound artifact
        5. otherwise retain the newest parsed blocker status for diagnostics
    ignore disagreement/synthesis artifacts before provider-slot accounting

function produce_plan_review_artifact(provider, raw_output_or_unavailable):
    before launching providers, read plan file once into immutable snapshot bytes
    compute plan path, issue, plan SHA256, UTC timestamp from that same snapshot
    extract provider verdict only from a dedicated raw verdict field/section: either a line `Verdict: <value>` at the start of provider output or the first non-empty line after an exact `## Verdict` heading
    never scan arbitrary prose, quoted prompts, fenced blocks, or the first standalone token elsewhere in output
    map raw `REJECT` to metadata `MAJOR`; if a successful provider output has no parseable dedicated verdict, emit conservative metadata `MAJOR` with a body note `verdict_parse_failed`; use `UNAVAILABLE` only for provider command failure/unavailable paths
    write the snapshot to a temp file and feed every provider from that snapshot (Claude path, Codex/Gemini inline body)
    if git show HEAD:<plan_path> exists and sha256(git blob bytes) == sha256(snapshot bytes):
        revision = git rev-parse HEAD
    else:
        revision = "WORKTREE:" + plan_sha256
    write canonical metadata header with Plan-Commit=revision and Reviewed-Revision=revision
    write blank line
    append raw provider output unchanged, or explicit UNAVAILABLE body with failure reason

```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/standards/PLAN_REVIEW_ARTIFACT_CONTRACT.md` | Authoritative schema, examples, draft-vs-commit binding rules, synthesis/disagreement non-provider rule |
| Modify | `scripts/ai/continuous-planning-pipeline.py` | Add header parser, metadata validation, explicit verdict parsing, deterministic multi-artifact selection, warning taxonomy, and impact reporting |
| Modify | `scripts/review/plan-review-fanout.sh` | Write collision-free `YYYY-MM-DDTHHMMSSZ-plan-NNN-<provider>.md` artifacts, prepend metadata for successful provider stdout and failure artifacts, preserve raw output, and fix Gemini trust/invocation failure path |
| Modify | `tests/analysis/test_continuous_planning_pipeline.py` | Parser/discovery/selection/report tests, including metadata, stale/untrusted cases, canonical timestamped names, legacy flag diagnostics-only behavior, version/role validation, commit blob validation, conflict-before-clean selection, and impact reporting |
| Create | `tests/review/test_plan_review_fanout.py` | Producer tests for collision-free fanout paths, immutable snapshot bytes, metadata header emission, raw-output preservation, Gemini trust invocation, and REJECT/no-verdict mapping |
| Modify | `docs/plans/README.md` | Link Step 4 to the new contract |

---

## TDD Test List

| Test name | What it verifies |
|---|---|
| `test_review_artifact_requires_current_plan_sha` | stale SHA blocks clean review with `sha_mismatch_review` |
| `test_review_artifact_missing_sha_is_legacy_not_current` | no SHA returns `legacy_review_no_sha` |
| `test_review_artifact_missing_non_sha_field_is_metadata_incomplete` | SHA present but timestamp/revision/etc. missing returns `metadata_incomplete` |
| `test_review_artifact_requires_version_and_provider_role` | missing/wrong `Review-Artifact-Version` or `Review-Artifact-Role` cannot become clean evidence |
| `test_review_artifact_wrong_issue_provider_or_path_is_untrusted` | issue/provider/path mismatches return `untrusted_review_metadata` |
| `test_malformed_reviewed_at_timestamp_is_metadata_incomplete` | timestamp must match `YYYY-MM-DDTHH:MM:SSZ` and invalid strings do not pass |
| `test_abbreviated_plan_commit_sha_is_untrusted` | 7-39 hex commit abbreviations are rejected in artifacts even if wrappers accept abbreviated input |
| `test_review_artifact_wrong_plan_commit_or_reviewed_revision_is_untrusted` | stale/fabricated commit or reviewed revision cannot pass with current SHA |
| `test_commit_bound_artifact_blob_must_hash_to_plan_sha` | commit-bound artifact is rejected when `git show Plan-Commit:Plan-Path` does not match `Plan-SHA256`, even if the dirty worktree bytes do |
| `test_worktree_sentinel_binds_to_current_plan_hash` | local draft artifacts are accepted only as `draft_bound_review` and never as clean Lane A/B evidence |
| `test_producer_uses_worktree_sentinel_for_dirty_or_untracked_plan` | producer must not bind dirty/untracked plan bytes to `HEAD` |
| `test_duplicate_conflicting_metadata_key_is_untrusted` | duplicate conflicting header keys block trust |
| `test_header_must_start_at_byte_zero` | metadata appearing after a preamble/comment/blank line is ignored and cannot establish trust |
| `test_quoted_plan_sha_inside_body_is_ignored` | body/fenced SHA does not satisfy metadata |
| `test_missing_header_verdict_is_metadata_incomplete` | header `Verdict` is required; body `## Verdict` cannot recover machine trust |
| `test_reject_header_is_invalid_for_plan_review_contract` | canonical artifact header `Verdict: REJECT` is not clean evidence and is classified invalid/incomplete |
| `test_fanout_maps_raw_reject_to_header_major` | producer maps raw provider `REJECT` from a dedicated verdict section/field to metadata `MAJOR` rather than emitting invalid header `REJECT` |
| `test_fanout_does_not_extract_verdict_from_quoted_or_arbitrary_prose` | producer ignores verdict-looking tokens outside a dedicated verdict section/field |
| `test_fanout_success_without_parseable_verdict_is_conservative_major` | successful provider output with no explicit verdict becomes metadata `MAJOR` plus diagnostic body note, not clean/unknown evidence |
| `test_perspective_must_match_provider_for_default_slots` | `Provider: claude` with `Perspective: security` is untrusted for the Claude provider slot |
| `test_explicit_header_verdict_ignores_body_prose` | header verdict is machine authority even if the body contains “No MAJOR blockers” prose |
| `test_disagreement_artifact_not_counted_as_provider` | disagreement/synthesis files do not satisfy provider slots |
| `test_empty_unavailable_unknown_major_artifacts_block_clean_review` | all non-clean statuses block Lane A/B clean evidence |
| `test_multiple_current_provider_artifacts_with_conflict_blocks` | duplicate current artifacts for same issue/provider with conflicting verdicts/statuses produce `multiple_review_artifacts` before any clean artifact can be selected |
| `test_identical_current_provider_duplicates_are_stable_newest_with_warning` | semantically identical duplicates pick latest valid timestamp/path and emit `duplicate_current_review` audit warning |
| `test_current_clean_artifact_wins_over_older_stale_artifact` | deterministic selection prefers the metadata-bound current artifact when no conflict exists |
| `test_report_explains_stale_vs_missing_vs_untrusted_evidence` | machine JSON and Markdown distinguish failure families and include an impact list |
| `test_fanout_success_and_unavailable_artifacts_emit_full_metadata_and_raw_body` | fanout success/failure artifacts include all metadata and preserve raw output/failure reason |
| `test_fanout_uses_collision_free_timestamped_artifact_paths` | same-day reruns create distinct timestamped artifacts instead of overwriting date-only paths |
| `test_fanout_hashes_exact_snapshot_bytes_sent_to_all_providers` | one immutable plan snapshot is used for Plan-SHA256 and provider input even if the worktree file changes during fanout |
| `test_noncanonical_cross_review_artifacts_do_not_satisfy_provider_slots` | timestamped submit-wrapper/cross-review names are ignored for Lane A/B evidence even when they contain review-like prose |
| `test_allow_legacy_review_artifacts_is_diagnostics_only` | the legacy flag cannot place an issue in Lane A/B without current metadata-bound artifacts |
| `test_gemini_fanout_invocation_sets_exact_trust_env_and_flag` | producer test prevents the observed trust-directory failure from recurring by checking `GEMINI_CLI_TRUST_WORKSPACE=true` and the current supported non-interactive trust flag |

---

## Acceptance Criteria

- [ ] Contract doc defines exact metadata grammar, required fields, examples, duplicate handling, draft `WORKTREE:<sha>` sentinel, collision-free timestamped artifact paths, and synthesis/disagreement non-provider rule.
- [ ] Parser ignores body/fenced metadata, requires the header to start at byte 0, validates all required fields/formats, rejects malformed timestamps and abbreviated commit SHAs, and returns deterministic statuses for stale, untrusted, incomplete, legacy, draft-bound, empty, unavailable, unknown, MAJOR, multiple-artifact, duplicate-current, and clean evidence.
- [ ] Parser validates `Review-Artifact-Version`, `Review-Artifact-Role`, `plan_commit`, `reviewed_revision`, and the git blob at `Plan-Commit:Plan-Path`, not only `Plan-SHA256`.
- [ ] Producer emits a git SHA only when the reviewed plan bytes match that commit’s blob; dirty/untracked plan bytes must use `WORKTREE:<plan_sha256>` and tests prove the fallback.
- [ ] Commit-bound approval readiness remains a workflow responsibility, not a new #2502 label-enforcement hook: draft-bound review artifacts are visible diagnostics but never clean Lane A/B evidence.
- [ ] Deterministic multi-artifact selection is implemented and covered by tests; conflict detection runs before selecting any clean artifact.
- [ ] Fanout producer writes collision-free timestamped artifacts, never overwrites same-day review waves, extracts a metadata verdict conservatively (`REJECT`→`MAJOR`, no parseable verdict→`MAJOR`, command failure→`UNAVAILABLE`), writes metadata for successful and failed providers, preserves raw provider output/failure reason after the blank line, and fixes Gemini by setting direct fanout trust/sandbox flags or by separately capturing and appending raw Gemini stdout/stderr if any wrapper is used.
- [ ] Fanout producer reads the plan once into an immutable snapshot and uses those exact bytes for metadata hashing and every provider prompt/input.
- [ ] Noncanonical submit-wrapper/cross-review artifacts are explicitly ignored for provider-slot evidence unless future work exports them to canonical collision-free `YYYY-MM-DDTHHMMSSZ-plan-NNN-<provider>.md` paths with the same metadata contract.
- [ ] The legacy allowance flag is diagnostics-only and cannot cause Lane A/B clean readiness without current metadata-bound artifacts.
- [ ] Raw-output preservation is explicit for the in-scope producer: fanout preserves raw provider stdout/stderr immediately after the blank line.
- [ ] `docs/plans/README.md` Step 4 links to the contract.
- [ ] Continuous planning JSON/Markdown includes an impact section listing affected issue numbers/status families before/after strict validation, so the current ~42 legacy/stale/unavailable/unknown review artifacts are visible rather than silently changing queue semantics.
- [ ] Validation commands pass: targeted pytest for pipeline and review producer tests, `uv run python -m py_compile` for changed Python files, and one sample `scripts/ai/continuous-planning-pipeline.py` run with warning/impact counts asserted.
- [ ] No local approval-marker semantics, no user-approval authority, and no implementation-dispatch policy are changed.

---

## Operational Impact / Rollout

- Expected immediate impact is reporting/classification only: legacy/stale/untrusted review artifacts may stop counting as clean Lane A/B evidence.
- The implementation must surface a concrete impact list by issue number and warning family in the generated JSON/Markdown report before any downstream automation uses the stricter result for dispatch.
- Historical artifacts must remain on disk for audit; the fanout producer must stop overwriting same-day artifacts, and the parser classifies legacy date-only artifacts rather than deleting or rewriting them.
- If review evidence for an otherwise approval-ready issue becomes non-clean solely because of legacy metadata, the correct action is to regenerate provider review artifacts, not to infer user approval or implementation authority.

---

## Adversarial Review Summary

| Wave | Provider | Verdict | Result |
|---|---|---|---|
| r1 | Claude | MAJOR | Fixed renderer scope ambiguity, prompt-vs-wrapper metadata conflation, UNAVAILABLE stub omission, quoted SHA gap, weak validation, and open validator decision. |
| r1 | Codex | MAJOR | Fixed missing tests for metadata fields/mismatch cases, arbitrary verdict parsing, narrow producer tests, README link omission, and classification-change ambiguity. |
| r1 | Gemini | UNAVAILABLE | Trust-directory failure recorded; not substantive. |
| r2 | Claude | MAJOR | Fixed production-path assumption by including renderer/submit-wrapper capability, defined exact header schema, added Gemini trust fix, corrected failure-output wording, split legacy vs incomplete metadata, removed no-op prompt row, avoided redundant synthesis status, and added impact rollout. |
| r2 | Codex | MAJOR | Added stale/wrong plan commit and reviewed revision validation, deterministic multiple-artifact selection, mandatory producer tests, raw-output preservation tests, and local-plan canonical-state handling. |
| r2 | Gemini | UNAVAILABLE | Same trust-directory failure; producer fix now explicitly addresses this. |

| r3-patch | Pending | Pending | Added harness/infra retrieval surfaces, made `WORKTREE:<64hex>` grammar exact, required commit-vs-worktree byte verification before emitting git SHA, added dirty/untracked producer tests, and added draft/local review artifact transition criteria before `status:plan-review`. |
| r3 | Codex | MAJOR | Fixed r3 findings by making draft-bound artifacts non-clean for Lane A/B, requiring full 40-hex commit SHAs, correcting control-plane path and harness retrieval evidence, defining `Perspective` validation semantics, and adding byte-zero header test coverage. |

| r4 | Codex | MAJOR | Fixed r4 findings by separating draft-bound diagnostics from clean Lane A/B evidence, removing any implied new label-enforcement hook, adding malformed timestamp and abbreviated-SHA tests, and defining same-verdict duplicate selection/warnings. |

| r5 | Codex | MAJOR | Historical patch wave; later superseded by r7 scope decision to keep renderer/submit-wrapper/cross-review outputs audit-only for #2502. |
| r6 | Codex | MAJOR | Historical patch wave; later superseded by r7 scope decision to remove generic wrapper/cross-review producer redesign from #2502 and focus on canonical fanout artifacts. |
| r7 | Codex | MAJOR | Fixed r7 findings by making `--allow-legacy-review-artifacts` diagnostics-only, limiting provider-slot discovery to canonical fanout filenames, removing generic wrapper/cross-review metadata from #2502 scope, and correcting HARD-STOP-POLICY applicability. |
| r8 | Codex | MAJOR | Fixed r8 findings by requiring collision-free timestamped fanout paths, validating version/role fields, and requiring consumer-side git blob hash validation for commit-bound artifacts. |
| r9 | Codex | MAJOR | Fixed r9 findings by moving conflict detection before clean selection, defining producer verdict extraction/REJECT/no-verdict mapping, and naming exact test files `tests/analysis/test_continuous_planning_pipeline.py` plus `tests/review/test_plan_review_fanout.py`. |
| r10 | Codex | MAJOR | Fixed r10 findings by removing arbitrary first-token verdict extraction, consistently using collision-free timestamped canonical paths, marking r5/r6 wrapper/renderer notes as superseded, and consolidating duplicate test-file ownership rows. |

**Current state:** draft only; not approval-ready until a fresh review wave finds no MAJOR blockers.

---

## Risks and Open Questions

- **Risk:** strict validation may temporarily reduce Lane A/B counts by reclassifying legacy artifacts. Mitigation: explicit impact report and artifact preservation.
- **Risk:** adjacent submit-wrapper/cross-review artifacts could be mistaken for provider-slot evidence. Mitigation: #2502 keeps discovery limited to canonical fanout filenames and adds tests proving timestamped generic review outputs are audit-only.
- **Risk:** local draft artifacts use a `WORKTREE:<sha>` sentinel. Mitigation: commit-bound approval evidence still requires regenerated artifacts after the plan is committed.
- **Decision:** no standalone validator CLI in #2502. Keep reusable validation in parser/helper code consumed by the continuous pipeline and producer tests; file a follow-up only if multiple consumers appear.

---

## Complexity: T2

**T2** — bounded workflow/harness hardening across one reporting script, one canonical fanout producer, docs, and tests. It remains T2 because it is read-only for issue state, does not change approval markers or dispatch authority, excludes generic wrapper/cross-review producer redesign, and includes an impact report rather than mutating historical review artifacts.

```
