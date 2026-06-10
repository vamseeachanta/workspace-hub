# Plan for #3015: harden attest-plan-claims path extraction for jsonl and template evidence

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-06-10
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3015
> **Client:** N/A
> **Review artifacts:** scripts/review/results/2026-06-10-plan-3015-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/review/attest-plan-claims.sh:25` — `ALL_PATHS` extractor regex: `` `[a-zA-Z0-9._/\-]+\.(py|md|yaml|yml|sh|json|toml)` `` — `jsonl` is absent from the alternation; this is the single root cause.
- Found: `tests/review/test_attest_plan_claims.py` — 9 test clusters, 682 lines; no test covers `.jsonl` extraction; Cluster 2 `test_extracts_backticked_paths_with_known_extensions` checks `.sh`, `.py`, `.toml`, `.md` paths only.
- Found: `tests/review/fixtures/sample_plan_with_citations.md` — 28-line fixture used by most tests; contains no backticked `.jsonl` reference.

### Standards

Not applicable — harness/CI issue.

### LLM Wiki pages consulted

No relevant wiki pages.

### Documents consulted

- `docs/plans/2026-04-20-issue-2405-cross-review-sandbox-repo-access.md` — original plan that created `attest-plan-claims.sh`; extension list `(py|md|yaml|yml|sh|json|toml)` was set there and never updated.
- Issue [#3015](https://github.com/vamseeachanta/workspace-hub/issues/3015) body — cites Codex r3 review artifact for #2975 Phase A as the source that caught the omission; names `templates/ecosystem-wiki-flywheel/run-history-record.example.jsonl` as the example missing path.
- Issue [#2975](https://github.com/vamseeachanta/workspace-hub/issues/2975) — parent context confirming `.jsonl` is a load-bearing template/run-history artifact type in the ecosystem-wiki-flywheel design.

### Gaps identified

- `jsonl` missing from `ALL_PATHS` extractor alternation on `attest-plan-claims.sh:25` (insert `|jsonl` after `json`).
- No existing test covers `.jsonl` path extraction; a new passing test does not exist to regress against.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-10T via `mcp__github__issue_read`):
- `#3015` — OPEN — "harden attest-plan-claims path extraction for jsonl and template evidence"
- `#2405` — OPEN — cross-review sandbox attestation (original plan)

**File existence** (verified 2026-06-10T):
- EXISTS: `scripts/review/attest-plan-claims.sh`
- EXISTS: `tests/review/test_attest_plan_claims.py`
- EXISTS: `tests/review/fixtures/sample_plan_with_citations.md`
- EXISTS: `docs/plans/2026-04-20-issue-2405-cross-review-sandbox-repo-access.md`

**Line excerpt** (`attest-plan-claims.sh:25` via `Read` tool):
```bash
ALL_PATHS=$(grep -oE '`[a-zA-Z0-9._/\-]+\.(py|md|yaml|yml|sh|json|toml)`' "$PLAN_FILE" \
```
`jsonl` is absent; it should appear between `json` and `toml`.

**Gap proofs**:
- `grep -n "jsonl" tests/review/test_attest_plan_claims.py` → no output → zero `.jsonl` test coverage confirmed.
- `grep -n "jsonl" tests/review/fixtures/sample_plan_with_citations.md` → no output → fixture has no `.jsonl` reference.

**Reproduction proofs**:
N/A — issue alleges a static code gap (missing extension in regex), not a runtime failure. Gap is directly verifiable from `attest-plan-claims.sh:25` without running the script.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-06-10-issue-3015-attest-jsonl-extension.md` |
| Implementation | `scripts/review/attest-plan-claims.sh` |
| Tests | `tests/review/test_attest_plan_claims.py` |
| Plan review — Claude | `scripts/review/results/2026-06-10-plan-3015-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-06-10-plan-3015-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-06-10-plan-3015-gemini.md` |

---

## Deliverable

`scripts/review/attest-plan-claims.sh` extracts backticked `.jsonl` paths and includes them in the attested file list, verified by two new TDD tests.

---

## Pseudocode

Trivial — see Files to Change. The entire change is inserting `|jsonl` into one string literal.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/review/attest-plan-claims.sh` | add `jsonl` to extension alternation on line 25 |
| Modify | `tests/review/test_attest_plan_claims.py` | add 2 new tests for `.jsonl` extraction |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_extracts_backticked_jsonl_path` | `.jsonl` backticked path appears in attested file list | inline plan text with `` `templates/run-history-record.example.jsonl` `` | `MISSING: templates/run-history-record.example.jsonl` in attestation output |
| `test_jsonl_extraction_does_not_break_existing_extensions` | `.py`, `.md`, `.yaml`, `.yml`, `.sh`, `.json`, `.toml` still extracted after adding `jsonl` | inline plan text with one backticked path per existing extension | all 7 extensions present in attestation output |

---

## Acceptance Criteria

- [ ] `scripts/review/attest-plan-claims.sh:25` regex includes `jsonl` in the extension alternation.
- [ ] `test_extracts_backticked_jsonl_path` passes (was failing before the fix).
- [ ] `test_jsonl_extraction_does_not_break_existing_extensions` passes (regression guard for all 7 prior extensions).
- [ ] All prior tests in `tests/review/test_attest_plan_claims.py` continue to pass: `uv run pytest tests/review/test_attest_plan_claims.py -v`.
- [ ] No regression in full suite: `uv run pytest tests/ -x`.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | pending | — |
| Codex | pending | — |
| Gemini | pending | — |

**Overall result:** pending

---

## Risks and Open Questions

- **Risk (low):** Regex alternation ordering — placing `jsonl` after `json` (not before) is safe because ERE alternation is greedy-left and `json` does not prefix-match `jsonl` in an extended-regex character-class context. No ordering hazard.
- **Open:** Should `ndjson` or `json5` be added at the same time? Issue body names only `jsonl` — keeping minimum scope; file a follow-on issue if other extensions are needed.

---

## Complexity: T1

Single-file regex change (`attest-plan-claims.sh:25`, four characters inserted: `|jsonl`) plus two new tests in the existing test file. No new modules, no architecture change, no new dependencies.
