# Plan for #2506: Validate Lane E Implementation Handoff Readiness

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-27
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2506
> **Review artifacts (planned):** scripts/review/results/2026-04-27-plan-2506-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- `scripts/ai/continuous-planning-pipeline.py` — already defines `HANDOFF_FIELDS` (13 lower-cased tokens) at lines 33-47, and `pr_handoff_state()` at lines 295-312 returning `("review-ready", [])` if all tokens are present anywhere in the PR body, else `("open-pr", ["lane_e_handoff_missing"])`.
- `tests/analysis/test_continuous_planning_pipeline.py` — `test_open_pr_with_complete_handoff_is_lane_e_review_ready` (line 196) and `test_live_issue_list_enriches_unlabeled_issues_for_lane_e` (line 241) cover the happy path and live enrichment, but no fixture covers: missing-risk, missing-tests, incidental body-mention, stale-branch, or conflicting-dispatch evidence.
- PR association in current code is permissive: `pr_handoff_state()` accepts the first entry of `closedByPullRequestsReferences` and concatenates issue comments into the matching PR body. There is no precedence check for: (a) explicit `closes #N`/`fixes #N` keywords, (b) branch naming containing the issue slug/number, (c) labels, vs. (d) incidental body mentions — current behavior conflates these.
- `gh_issue_list()` (line 570) enriches every open issue with `comments,closedByPullRequestsReferences`. The current pipeline therefore already has the data it needs to validate handoff fields per PR — the gap is the validator, not the data layer.
- Token matching is substring-based (`field not in body`). `"issue"` will collide with the word "issue" appearing anywhere in the body; `"risks"` will match the literal token "risks:" but also any prose containing "risks"; conflicting-dispatch evidence is not parsed at all.

### Documents consulted
- Parent #2489 plan: `docs/plans/2026-04-26-issue-2489-continuous-planning-pipeline.md` — defines Lane E mandatory handoff fields (lines 108, 178-179, 201) and PR association precedence rule (line 106): "explicit execution/start/completion comment URL > branch name containing issue slug/number > PR title closing the issue > direct issue-closing keyword; incidental body-only references are weak evidence and must not alone classify Lane E". #2506 is the implementation of this contract.
- Issue body #2506 — required handoff fields list (13 items), 6-fixture matrix, `open-pr` vs `review-ready` classifier output, and review-capacity-cap acceptance criterion.
- Sibling #2502 (plan-review artifact metadata) — defines machine-checkable metadata contract for review artifacts; complementary surface, not overlapping.
- Sibling #2503 (canonical approval-request comments) — Lane A surface; #2503 explicitly preserves `closedByPullRequestsReferences`/Lane E PR enrichment per its r14 acceptance (verified in `docs/plans/2026-04-27-issue-2503-canonical-approval-request-comments.md` lines 15, 111, 146, 164). #2506 must therefore remain compatible with the GraphQL comment-window structure #2503 introduces.
- Sibling #2504 (dispatch-ledger trust contract) — defines lease lifecycle. #2506 consumes ledger rows to detect "conflicting dispatch evidence" but does not write or arbitrate ledger rows.
- Sibling #2505 (golden-output morning packet) — defines markdown sections and Top-actions ordering. Lane E review-ready/open-pr distinction feeds into #2505's "merge-ready Lane E" priority bucket. #2506 produces the data; #2505 renders it.
- `docs/standards/HARD-STOP-POLICY.md` — implementation-review must occur before merge; the `implementation-review status` handoff field must distinguish `pending`, `passed`, `failed`.
- `docs/plans/_template-issue-plan.md` — required plan sections.
- `docs/plans/README.md` — index conventions; entry already exists for #2489 at line 319.
- `.claude/skills/coordination/issue-planning-mode/SKILL.md` — verified workflow: draft → adversarial review → status:plan-review → user approval → implementation.

### Standards
| Standard | Status | Source |
|---|---|---|
| Planning workflow / Lane E definition | applicable | `docs/plans/2026-04-26-issue-2489-continuous-planning-pipeline.md` lines 104-108 |
| HARD-STOP-POLICY | contextual only | `docs/standards/HARD-STOP-POLICY.md` — applies to engineering-critical surfaces; #2506 is workflow validation, so the implementation-review field name must align but the policy itself is not modified |
| Calc citation contract | not applicable | `.claude/rules/calc-citation-contract.md` — no engineering-derived constants in this plan |

### LLM Wiki pages consulted
- No relevant wiki pages — this is workflow harness work.

### Gaps identified
- No PR-association precedence validator exists. `pr_handoff_state()` does not distinguish explicit issue-closing references (`closesByPullRequestsReferences` is a strong signal) from incidental body mentions of `#NNN`.
- No structured handoff-field parser exists. Token-substring matching produces false positives (the word "risks" anywhere in a body satisfies the `risks` field).
- No fixture corpus covers the 6 cases enumerated in the issue body: complete, missing-risk, missing-tests, incidental-reference-only, stale-branch, conflicting-dispatch-evidence.
- No primary-blocker reasoning — `pr_handoff_state()` returns a single `lane_e_handoff_missing` warning regardless of whether one or all 13 fields are missing.
- No `evidence_strength` classification (strong | weak | incidental) on PR association.
- No stale-branch detection. A merged or abandoned branch with stale handoff evidence currently classifies the same as a live PR.
- No conflicting-dispatch detection at the Lane E layer. Currently if a dispatch row says `running` and a PR is open, lane resolution falls into Lane E (PR check runs first at classifier line 356-361 before the dispatch check at line 362), but no warning surfaces the conflict.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-27 via `gh issue view`):
- `#2506` — OPEN — feat(ai-orchestration): validate Lane E implementation handoff readiness
- `#2489` — CLOSED, status:plan-approved — feat(ai-orchestration): continuous planning pipeline for AFK issue throughput
- `#2502` — OPEN — feat(ai-orchestration): harden plan-review artifact metadata and stale-SHA handling
- `#2503` — OPEN — feat(ai-orchestration): standardize canonical approval-request comments for plan-review issues
- `#2504` — OPEN — feat(ai-orchestration): define dispatch-ledger trust contract and lease lifecycle writer
- `#2505` — OPEN — feat(ai-orchestration): add golden-output contract for morning approval and QA packet

**File existence** (verified 2026-04-27 via `ls`):
- EXISTS: `scripts/ai/continuous-planning-pipeline.py` (638 lines)
- EXISTS: `tests/analysis/test_continuous_planning_pipeline.py`
- EXISTS: `config/ai-tools/continuous-planning-pipeline.json` (15057 lines, current snapshot)
- EXISTS: `docs/reports/continuous-planning-pipeline.md`
- EXISTS: `docs/plans/2026-04-26-issue-2489-continuous-planning-pipeline.md`
- EXISTS: `docs/plans/_template-issue-plan.md`
- EXISTS: `docs/plans/README.md`
- EXISTS sibling: `docs/plans/2026-04-27-issue-2502-plan-review-artifact-metadata-stale-sha.md`
- EXISTS sibling: `docs/plans/2026-04-27-issue-2503-canonical-approval-request-comments.md`
- MISSING (this plan creates): `tests/analysis/fixtures/lane_e_handoff/` fixture directory
- MISSING (this plan creates): `docs/standards/LANE_E_HANDOFF_CONTRACT.md` (or merge into existing CONTROL_PLANE_CONTRACT.md — see Open Questions)

**Line excerpts** (verified):
- `scripts/ai/continuous-planning-pipeline.py:33-47` defines `HANDOFF_FIELDS` tuple of 13 lower-case tokens.
- `scripts/ai/continuous-planning-pipeline.py:295-312` defines `pr_handoff_state()`: returns `("review-ready", [])` only if every token in `HANDOFF_FIELDS` appears as a substring in `pr.body.lower()`.

**Gap proofs**:
- `grep -n -i "evidence_strength\|incidental\|precedence" scripts/ai/continuous-planning-pipeline.py` → returns nothing → confirms no precedence validator exists.
- `ls tests/analysis/fixtures/lane_e_handoff/ 2>&1` → "No such file or directory" → confirms fixture corpus does not exist.
- `grep -l -i "lane e\|implementation handoff" docs/standards/` → empty → confirms no standards-level handoff contract document exists yet.

Distinct sources consulted: issue #2506 body, parent plan #2489, sibling plan #2503, existing pipeline implementation, existing test file, planning skill SKILL.md, planning template — 7 sources, exceeds the ≥3 requirement.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-27-issue-2506-lane-e-handoff-validator.md` |
| Tests | `tests/analysis/test_continuous_planning_pipeline.py` (extended) |
| Fixture corpus | `tests/analysis/fixtures/lane_e_handoff/{complete,missing-risk,missing-tests,incidental-ref,stale-branch,conflicting-dispatch}.json` |
| Implementation | `scripts/ai/continuous-planning-pipeline.py` (extended `pr_handoff_state` and add `pr_association_evidence`) |
| Contract doc | `docs/standards/LANE_E_HANDOFF_CONTRACT.md` (new) |
| Plan review — Claude | scripts/review/results/2026-04-27-plan-2506-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-27-plan-2506-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-27-plan-2506-gemini.md |
| Index update | `docs/plans/README.md` (new row) |

---

## Deliverable

A Lane E handoff validator that (a) classifies PR-to-issue association evidence into `strong | weak | incidental` using explicit precedence (issue-closing reference > branch name > PR title closes > body mention), (b) parses the 13 mandatory handoff fields from PR body using structured key:value extraction (not substring matching), (c) emits `open-pr` vs `review-ready` substates with a primary-blocker reason naming the first missing field, (d) detects stale-branch and conflicting-dispatch states as additional blockers, and (e) ships a 6-fixture test corpus exercising the matrix in the issue body. Validator remains read-only — it does not merge, close, or write labels.

---

## Pseudocode

```text
HANDOFF_FIELD_SCHEMA = {
    "issue":                 r"^\s*issue\s*:\s*#?(\d+)\s*$",
    "pr_branch":             r"^\s*PR/branch\s*:\s*(\S+)\s*$",
    "dispatch_id":           r"^\s*dispatch\s*id\s*:\s*(\S+)\s*$",
    "plan_sha":              r"^\s*plan\s*SHA\s*:\s*(\S+)\s*$",
    "approval_marker":       r"^\s*approval\s*marker\s*:\s*(\S+)\s*$",
    "changed_files":         r"^\s*changed\s*files\s*:\s*(.+)$",
    "tests_ci":              r"^\s*tests/CI\s*:\s*(.+)$",
    "artifacts":             r"^\s*artifacts\s*:\s*(.+)$",
    "risks":                 r"^\s*risks\s*:\s*(.+)$",
    "implementation_review": r"^\s*implementation-review\s*status\s*:\s*(pending|passed|failed)\s*$",
    "recommended_action":    r"^\s*recommended\s*human\s*action\s*:\s*(.+)$",
    "review_effort":         r"^\s*review\s*effort\s*:\s*(low|medium|high)\s*$",
    "priority_reason":       r"^\s*priority\s*reason\s*:\s*(.+)$",
}

def pr_association_evidence(issue, pr) -> dict:
    # Returns {strength: "strong"|"weak"|"incidental"|"none", source: "<reason>"}
    if pr_closes_issue_keyword(pr, issue.number):       # "closes #N", "fixes #N" in PR body
        return {"strength": "strong", "source": "closing_keyword"}
    if branch_name_matches(pr.head.ref, issue.number):  # branch contains "<NNN>" or slug
        return {"strength": "strong", "source": "branch_name"}
    if pr_title_closes_issue(pr.title, issue.number):
        return {"strength": "strong", "source": "pr_title"}
    if pr_label_links_issue(pr.labels, issue.number):
        return {"strength": "weak", "source": "label"}
    if incidental_body_mention(pr.body, issue.number):
        return {"strength": "incidental", "source": "body_mention"}
    return {"strength": "none", "source": None}

def parse_handoff_fields(pr_body: str) -> dict:
    # Line-anchored regex per HANDOFF_FIELD_SCHEMA. NOT substring matching.
    # Returns {field_name: value | None}
    parsed = {}
    for line in pr_body.splitlines():
        for name, pattern in HANDOFF_FIELD_SCHEMA.items():
            m = re.match(pattern, line, re.IGNORECASE)
            if m:
                parsed[name] = m.group(1).strip()
    return {name: parsed.get(name) for name in HANDOFF_FIELD_SCHEMA}

def detect_stale_branch(pr, now_utc, ttl_days=14) -> bool:
    # Stale = PR.updated_at older than ttl AND PR not in DRAFT|MERGED state
    if pr.state == "MERGED":
        return False
    return (now_utc - pr.updated_at).days > ttl_days

def detect_conflicting_dispatch(issue_number, dispatch_rows) -> str | None:
    # Returns conflict description if a non-terminal dispatch row exists with
    # a different dispatch_id from the one declared in PR body's "dispatch id" field
    row = dispatch_rows.get(issue_number)
    if not row:
        return None
    if row.get("state") in NON_TERMINAL_DISPATCH_STATES:
        return f"dispatch_{row['dispatch_id']}_in_state_{row['state']}_while_pr_open"
    return None

def pr_handoff_state(issue, dispatch_rows, now_utc) -> tuple[str, list[str], dict]:
    pr = resolve_pr(issue)  # uses closedByPullRequestsReferences first
    if not pr:
        return None, [], {}
    evidence = pr_association_evidence(issue, pr)
    if evidence["strength"] in {"none", "incidental"}:
        # incidental body-mention does NOT classify as Lane E
        return None, ["lane_e_pr_association_weak"], {"evidence": evidence}
    parsed = parse_handoff_fields(pr.body)
    missing = [name for name, value in parsed.items() if value is None]
    warnings = []
    if missing:
        warnings.append("lane_e_handoff_missing")
    if detect_stale_branch(pr, now_utc):
        warnings.append("lane_e_stale_branch")
    conflict = detect_conflicting_dispatch(issue.number, dispatch_rows)
    if conflict:
        warnings.append(f"lane_e_dispatch_conflict:{conflict}")
    if evidence["strength"] == "weak":
        warnings.append("lane_e_pr_association_weak")
    state = "review-ready" if not missing and "lane_e_stale_branch" not in warnings else "open-pr"
    primary_blocker = (
        f"missing_field:{missing[0]}" if missing
        else "stale_branch" if "lane_e_stale_branch" in warnings
        else "dispatch_conflict" if conflict
        else None
    )
    return state, warnings, {"evidence": evidence, "parsed": parsed, "primary_blocker": primary_blocker}
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/ai/continuous-planning-pipeline.py` | Replace substring `HANDOFF_FIELDS` matcher with line-anchored regex parser; add `pr_association_evidence()`, `detect_stale_branch()`, `detect_conflicting_dispatch()`; surface primary blocker in evidence dict |
| Modify | `tests/analysis/test_continuous_planning_pipeline.py` | Add 6 fixture-driven tests + edge-case unit tests for each helper |
| Create | `tests/analysis/fixtures/lane_e_handoff/complete.json` | Issue + PR with all 13 fields and strong association |
| Create | `tests/analysis/fixtures/lane_e_handoff/missing-risk.json` | Same as complete but `risks:` line removed |
| Create | `tests/analysis/fixtures/lane_e_handoff/missing-tests.json` | Same as complete but `tests/CI:` line removed |
| Create | `tests/analysis/fixtures/lane_e_handoff/incidental-ref.json` | PR body mentions `#NNN` only in prose; no closing keyword/branch/title link |
| Create | `tests/analysis/fixtures/lane_e_handoff/stale-branch.json` | PR with all fields but `updated_at` >14 days old, state=OPEN |
| Create | `tests/analysis/fixtures/lane_e_handoff/conflicting-dispatch.json` | PR + dispatch ledger row with different `dispatch_id` in `running` state |
| Create | `docs/standards/LANE_E_HANDOFF_CONTRACT.md` | Authoritative schema + association-precedence + stale/conflict rules; referenced by SKILL.md and #2505 packet renderer |
| Update | `docs/plans/README.md` | Add #2506 row |

Out of scope (delegated):
- #2502 review-artifact metadata — separate plan.
- #2503 approval-comment GraphQL parser — must remain compatible (verify by re-running `test_live_issue_list_enriches_unlabeled_issues_for_lane_e` after change).
- #2504 dispatch-ledger writer/lease — #2506 reads ledger rows; does not write.
- #2505 morning packet rendering — #2506 supplies `primary_blocker`/`substate`; #2505 lays it out.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_handoff_complete_fixture_is_review_ready` | Happy path | `lane_e_handoff/complete.json` | lane=E, substate=review-ready, warnings=[] |
| `test_handoff_missing_risk_blocks_review_ready` | Single-field gap surfaces | `lane_e_handoff/missing-risk.json` | substate=open-pr, primary_blocker="missing_field:risks" |
| `test_handoff_missing_tests_blocks_review_ready` | Tests/CI required | `lane_e_handoff/missing-tests.json` | substate=open-pr, primary_blocker="missing_field:tests_ci" |
| `test_incidental_pr_body_mention_not_lane_e` | Body-only `#NNN` mention does not promote | `lane_e_handoff/incidental-ref.json` | lane != E, warning=lane_e_pr_association_weak |
| `test_stale_branch_blocks_review_ready_even_when_complete` | Stale PR cannot be review-ready | `lane_e_handoff/stale-branch.json` | substate=open-pr, warning=lane_e_stale_branch |
| `test_conflicting_dispatch_evidence_surfaces_warning` | Open PR while ledger row says `running` (different dispatch_id) | `lane_e_handoff/conflicting-dispatch.json` | lane=E, warning includes lane_e_dispatch_conflict |
| `test_pr_association_precedence_closing_keyword_wins` | `closes #N` is strong | PR body with `closes #N` only | strength=strong, source=closing_keyword |
| `test_pr_association_precedence_branch_name_strong` | Branch with issue number is strong absent closing keyword | branch=`feature/issue-2506-x` | strength=strong, source=branch_name |
| `test_pr_association_precedence_label_is_weak` | Label-only link is weak | PR labels include `issue-2506` only | strength=weak |
| `test_handoff_field_parser_rejects_substring_match_for_risks` | Token "risks" in prose paragraph does not satisfy `risks:` field | PR body says "this carries risks" without `risks:` line | parsed.risks is None |
| `test_handoff_field_parser_accepts_case_insensitive_keys` | `Risks:` and `risks:` both parse | PR body with `Risks: low` | parsed.risks="low" |
| `test_implementation_review_status_must_be_enum` | Free-text fails enum check | PR body with `implementation-review status: maybe` | parsed.implementation_review is None |
| `test_review_effort_must_be_enum` | Free-text fails enum check | PR body with `review effort: medium-ish` | parsed.review_effort is None |
| `test_existing_handoff_pr_test_still_passes_under_regex_parser` | Regression: `test_open_pr_with_complete_handoff_is_lane_e_review_ready` continues to pass | existing fixture | review-ready as before |
| `test_live_enrichment_test_still_passes` | Regression: GraphQL `closedByPullRequestsReferences` enrichment from #2503 unaffected | existing fixture | unchanged behavior |
| `test_primary_blocker_picks_first_missing_field_in_schema_order` | Deterministic single-blocker reporting | PR missing 3 fields | primary_blocker names the first per HANDOFF_FIELD_SCHEMA dict order |
| `test_lane_e_review_capacity_cap_unchanged` | Saturation logic in `compute_buffer_health` still triggers at 5 | 5 review-ready Lane E items | buffer_health.lane_e.status=saturated |

---

## Acceptance Criteria

- [ ] `pr_handoff_state()` rejects substring-only handoff matches (e.g., the word "risks" in prose).
- [ ] PR association precedence implemented and tested: closing_keyword > branch_name > pr_title > label > body_mention.
- [ ] Incidental body-only `#NNN` mention classifies as `lane_e_pr_association_weak` and does NOT place the issue in Lane E.
- [ ] All 6 fixtures from issue #2506 body exist under `tests/analysis/fixtures/lane_e_handoff/` and are exercised by named tests.
- [ ] `open-pr` vs `review-ready` substate emitted with `primary_blocker` field naming the first missing handoff field, or `stale_branch`, or `dispatch_conflict`.
- [ ] `implementation-review status` parser enforces the `pending|passed|failed` enum; `review effort` parser enforces `low|medium|high`.
- [ ] `docs/standards/LANE_E_HANDOFF_CONTRACT.md` exists and documents schema, precedence, stale/conflict semantics.
- [ ] `docs/plans/README.md` contains a row for #2506.
- [ ] Tests pass: `uv run pytest tests/analysis/test_continuous_planning_pipeline.py -v`.
- [ ] No regression: existing #2489 tests `test_open_pr_with_complete_handoff_is_lane_e_review_ready` and `test_live_issue_list_enriches_unlabeled_issues_for_lane_e` still pass unchanged.
- [ ] Validator does not write GitHub state, merge PRs, or create dispatch leases (read-only contract from #2489 preserved).
- [ ] Adversarial plan review artifacts exist for the current plan SHA before moving #2506 to `status:plan-review`.

---

## Adversarial Review Summary

<!-- Filled in after plan-review wave completes. Status: PENDING. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** PENDING (adversarial review wave not yet run).

---

## Risks and Open Questions

- **Risk:** PR bodies in the wild use varied formatting (markdown bold, table rows, indented code blocks). Line-anchored regex with `re.IGNORECASE` and stripping leading whitespace handles most cases, but bold-prefixed keys like `**Risks:** low` need a small tolerance pattern. Mitigate by including a tolerance pattern (`^\s*\**\s*risks\s*\**\s*:\s*(.+)$`) and a fixture proving it.
- **Risk:** Switching from substring to regex parsing will change Lane E classification on existing live PRs. Migration risk: PRs that were marked `review-ready` under substring logic may flip to `open-pr` under stricter parsing. Mitigate by running the new validator against a snapshot of current `config/ai-tools/continuous-planning-pipeline.json` Lane E entries before merge and reporting deltas in the implementation PR.
- **Risk:** Stale-branch TTL of 14 days is a guess. If overnight cycles legitimately leave a PR open longer (e.g. waiting for sibling-issue resolution), legitimate work flips to `open-pr`. Mitigate by making TTL configurable via `--lane-e-stale-days` and defaulting conservatively to 21 days.
- **Risk:** `closedByPullRequestsReferences` is a GitHub-managed field, but PRs that don't explicitly close issues won't appear there. Then `pr_association_evidence` sees no PR. Mitigate by also checking branches via `gh pr list --search "in:title,body #NNN"` only when no `closedByPullRequestsReferences` row exists, and rate-limit the fallback.
- **Risk:** Field-name collision — issue body says "issue:" and many PRs reference the issue elsewhere. Line-anchored regex on `^\s*issue\s*:\s*#?(\d+)\s*$` mitigates this.
- **Risk:** Overlap with #2504 (dispatch-ledger writer). #2506 only **reads** dispatch ledger rows for the conflicting-dispatch fixture; does not arbitrate ledger trust. Boundary holds as long as #2506 reads the ledger format defined by #2504 once that lands. Until #2504 lands, #2506 reads the optional ledger schema as defined in `docs/plans/2026-04-26-issue-2489-continuous-planning-pipeline.md` line 142.
- **Open:** Should `LANE_E_HANDOFF_CONTRACT.md` be a new standalone standards file, or an appendix to `CONTROL_PLANE_CONTRACT.md`? Recommend standalone for searchability; flag for user during approval.
- **Open:** Should `lane_e_pr_association_weak` (label-only) downgrade to non-Lane-E classification, or stay in Lane E with a warning? Recommend stay-in-Lane-E-with-warning so the PR doesn't disappear; flag for user.
- **Open:** TTL default for stale-branch — 14 vs 21 days. Flag for user.

---

## Complexity: T2

**T2** — modification of an existing module with new helpers, fixture corpus addition, one new standards doc, full TDD coverage, and explicit regression coverage of two existing tests. No new top-level module, no schema migration of persisted JSON beyond additive evidence fields.
