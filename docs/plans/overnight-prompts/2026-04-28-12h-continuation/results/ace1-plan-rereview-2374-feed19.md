# Feed19 Result — Cold-Context Re-Review for #2374 Plan

> **Classification:** COMPLETED_WITH_RESULT
> **Machine:** ace-linux-1
> **Provider:** Claude Opus 4.6 (Feed19 — bounded adversarial re-review)
> **Date:** 2026-04-29
> **Feed chain:** feed13 (draft #2375) → feed14 (review #2375) → feed15 (patch #2375) → feed16 (patch #2374) → feed17 (review #2374) → feed18 (patch #2374) → **feed19 (re-review #2374)**

---

## Part 1: Feed17 Finding Resolution Verification

| # | Severity | Finding | Feed18 Disposition | Feed19 Verified | Notes |
|---|----------|---------|-------------------|-----------------|-------|
| F1 | MINOR | DURABLE_CATEGORIES diverges from #2375 | RESOLVED — caveated | **VERIFIED** | Line 35 now reads "structurally compatible with union-schema reconciliation" with explicit disjoint-set caveat. Correct and complete. |
| F2 | MINOR | Wrong script paths (`scripts/operations/` → `scripts/cron/`) | RESOLVED — corrected | **VERIFIED** | All three scripts (`comprehensive-learning-nightly.sh`, `harvest-workflow-tips.sh`, `queue-refresh-weekly.sh`) confirmed at `scripts/cron/` via live `ls`. No remaining `scripts/operations/` in active plan text (only appears in feed18 changelog at line 451 — appropriate as historical reference). |
| F3 | MINOR | `route_domain` process-set divergence vs #2375 | RESOLVED — documented | **VERIFIED** | Lines 337-342 carry inline comment explaining intentional `data-pipeline` → `process` routing with merge-reconciliation note. Clear and proportionate. |
| F4 | LOW | Stale self-reference slug parenthetical | RESOLVED — removed | **VERIFIED** | `grep 'final-slug'` returns only line 451 (changelog context). Active plan text clean. |
| F5 | LOW | File counts stale | RESOLVED — qualified | **VERIFIED** | Lines 67-69 now carry "(counts as of 2026-04-27; counts grow daily/weekly; extractors use glob patterns, not hardcoded counts)" qualifiers. Current live counts: handoffs=88, reviews=1196, reports=154 — drift is expected and the qualifiers adequately communicate that counts are snapshots. |
| F6 | LOW | Review artifact date prefix | RESOLVED — corrected | **VERIFIED** | Line 7 header and lines 153-155 artifact map all use `2026-04-29` prefix. Consistent. |
| F7 | LOW | Artifact map redundant parenthetical | RESOLVED — removed | **VERIFIED** | No remaining `final-slug` in artifact map section. |

**Summary: All 7 feed17 findings (3 MINOR, 4 LOW) are verified resolved. No regressions introduced.**

---

## Part 2: Fresh Adversarial Pass

### Methodology

Cold-context re-review of `docs/plans/2026-04-27-issue-2374-transient-promotion-candidate-queue.md` (459 lines, post-feed18 patch). Assessed against:
- Plan template contract (`docs/plans/_template-issue-plan.md`)
- Planning workflow README (`docs/plans/README.md`)
- Live repo state (2026-04-29)
- Sibling plan #2375 (`docs/plans/2026-04-29-issue-2375-wrk-completions-normalize.md`)
- Memory rules (adversarial stance, no self-approval, data format guidelines)

### Findings

#### N1 (LOW): `classify_category()` and `route_engineering_subdomain()` undefined in pseudocode

The pseudocode references `classify_category(c)` (lines 326, 333) and `route_engineering_subdomain(c)` (line 335) but neither function is defined or stubbed in the plan. The #2375 sibling plan defines `route_engineering_subdomain()` (with a `SUBDOMAIN_MAP` at line 308-314) but #2374 does not replicate or cross-reference this.

This is LOW rather than MINOR because:
- The plan is pseudocode (design checkpoint), not implementation spec
- Both functions have obvious signatures
- An implementer can derive `classify_category` from the `categorize_uncategorized.RULES` pattern already cited in resource intel (line 15)
- The `route_engineering_subdomain` definition exists in the #2375 plan and is reusable

**Suggested remediation (optional):** Add a 2-line stub comment: `# classify_category: reuses RULES from categorize_uncategorized.py; route_engineering_subdomain: mirrors #2375 plan lines 308-326`.

#### N2 (LOW): Dedup key inconsistency between Risks section and TDD test

- **Risks section (line 444):** dedup key is `(normalized(finding_summary[:120]), issue_ref)` — first occurrence wins
- **TDD test (line 388):** `test_orchestrator_dedupes_by_source_path_plus_summary` — dedup by `source_path + summary`
- **Pseudocode (lines 167-199):** No dedup step shown in the orchestrator main loop at all

Three representations of dedup, all slightly different. The Risks section key (`summary[:120] + issue_ref`) is the most defensible for cross-source dedup (same finding in a handoff and a review), while the test key (`source_path + summary`) can only dedup within a single source — it would miss cross-source duplicates, which is the scenario the Risk explicitly describes.

**Severity: LOW** — this is a design ambiguity the implementer must resolve, and the TDD test can be adjusted during implementation. But the inconsistency could cause a reviewer to question which contract is authoritative.

**Suggested remediation:** Align the TDD test name and description with the Risks dedup key: `test_orchestrator_dedupes_by_normalized_summary_plus_issue_ref`. Add a one-line comment in the pseudocode main loop: `# dedup: see Risks § "duplicate findings" for key definition`.

#### N3 (LOW): `existing_wiki_page_for(c)` called in pseudocode but Open Question says default to `create`

Line 188 of the pseudocode calls `existing_wiki_page_for(c)` to conditionally set `extend_or_create`. But the Open Question at line 449 says "Plan defaults to `create` for v1 with a TODO for a wiki-index lookup follow-on." These two statements contradict: the pseudocode shows a lookup, the open question says no lookup.

**Severity: LOW** — the Open Question is the authoritative design intent (deferred lookup). The pseudocode overspecifies.

**Suggested remediation:** Replace line 188 pseudocode with:
```
c["extend_or_create"]   = "create"  # v1: default create; wiki-index lookup deferred (see Open Questions)
```

#### N4 (INFO): `schema.md` does not yet document the merge contract

The plan's acceptance criterion (line 412) and Files to Change (line 365) both state that `knowledge/seeds/schema.md` will be modified to document the promotion-candidates schema and the merge contract with `wrk-wiki-candidates.yaml`. Verified: the current `schema.md` (82 lines) covers only the resource-catalog schema (`textbooks[]`, `online_portals[]`, `pending_manual[]`). It does not mention `promotion-candidates.yaml` or `wrk-wiki-candidates.yaml`.

This is expected — the plan correctly identifies this as a file to create/modify. But note: neither the #2374 nor #2375 plan specifies *where* in `schema.md` the new section goes, and the existing document is narrowly scoped to "doc-research WRK" seeds. The implementer will need to either (a) add a new top-level section to schema.md, or (b) create a separate schema doc for candidate/promotion artifacts. This is a minor ambiguity, not a defect.

**Severity: INFO** — no remediation needed; just flagging for implementer awareness.

#### N5 (INFO): `wrk-wiki-candidates.yaml` does not yet exist at `data/document-index/`

Verified: `ls data/document-index/wrk-wiki-candidates.yaml` returns "No such file or directory". This is expected — #2375 creates it. But the #2374 plan references this path in the merge contract (lines 35, 51, 365, 412, 445). If #2375 changes the path again during its own implementation, the #2374 plan's references go stale.

**Severity: INFO** — inherent coordination risk between sibling plans. The feed16 coordination note already documented this hazard class. No additional remediation needed; the implementer of #2374 should verify the #2375 output path at implementation time.

#### N6 (INFO): Score threshold divergence with #2375 undocumented in plan body

Feed17 review (line 89-92 of feed17 result) noted that #2374 keeps candidates at score ≥ 1 while #2375 keeps score ≥ 2. Feed18's residual risk table flagged this as LOW. However, neither the plan's Risks section nor the merge-contract documentation at line 35 mention this threshold divergence.

The divergence is appropriate (#2374's noisier Markdown sources justify a lower threshold) but should be documented alongside the DURABLE_CATEGORIES caveat so the merge contract is complete.

**Severity: INFO** — feed18 residual risk already flags this; upgrading to LOW would be reasonable but the information does exist in the review chain. Not blocking.

**Suggested remediation (optional):** Add one sentence to the line 35 caveat: "Score threshold also diverges: #2374 keeps ≥1 (noisier source material), #2375 keeps ≥2."

---

### Cross-Plan Boundary Assessment (#2374 vs #2375)

| Dimension | #2374 | #2375 | Boundary clear? |
|-----------|-------|-------|-----------------|
| Source material | Markdown (handoffs, reviews, reports) | JSONL WRK corpus | **Yes** — disjoint source surfaces |
| Output artifact | `knowledge-base/promotion-candidates.yaml` | `data/document-index/wrk-wiki-candidates.yaml` | **Yes** — different paths, different directories |
| Schema | Shared status vocab, shared 0..3 rubric, shared domain vocab | Same | **Yes** — documented at line 35 with feed18 caveats |
| Scoring threshold | ≥ 1 | ≥ 2 | **Underdocumented** (N6) |
| DURABLE_CATEGORIES | 7 members | 4 members (overlap: `engineering`) | **Documented** (feed18/F1 caveat) |
| route_domain process set | includes `data-pipeline` | excludes `data-pipeline` | **Documented** (feed18/F3 comment) |
| Merge path | Union-schema reconciliation (documented as future work) | Same | **Yes** |

**Boundary verdict:** Clear and well-documented after feed18 patches. The one remaining gap (threshold divergence, N6) is INFO-level.

---

### Acceptance Criteria Assessment

| AC# | Criterion (abbreviated) | Testable? | Notes |
|-----|------------------------|-----------|-------|
| 1 | YAML exists with all required fields | Yes | Field list is explicit and exhaustive |
| 2 | All three source classes represented | Yes | Minimum-one-per-kind requirement |
| 3 | Legacy timestamp files filtered out | Yes | Test `test_review_extractor_filters_to_date_named_artifacts` covers this |
| 4 | Extraction report with per-source counts | Yes | Report format described in pseudocode |
| 5 | schema.md documents merge contract | Yes | Static check on file content |
| 6 | No automatic promotion | Yes | Code-review + absence of `gh issue`/wiki-write calls |
| 7 | All new tests pass | Yes | Explicit pytest command given |
| 8 | No regression | Yes | Full test suite + integration test command given |
| 9 | Complements #2236 | Yes | Explicit prose statement in plan + absence of promotion logic |
| 10 | Sibling positioning | Yes | Shared vocabulary documented |
| 11 | Path-handling rule | Yes | Enforcement script referenced |
| 12 | Review artifacts before plan-review | Yes | Process gate |

**AC verdict:** All 12 acceptance criteria are testable and well-specified. No gaps.

---

### TDD Shape Assessment

26 tests listed across 4 test files. Coverage:
- **Handoff extractor (6 tests):** issue-ref extraction, file shape tolerance, section filtering (both include and exclude), sha recording, summary truncation. Adequate.
- **Review extractor (4 tests):** date-name filtering, filename issue extraction, severity classification, disagreement files. Adequate.
- **Recurring extractor (2 tests):** glob filtering, section vocabulary. Adequate.
- **Orchestrator/scoring (14 tests):** dedup, score thresholds, status default, status vocabulary documentation, atomic write, idempotency, sort order, dry-run, report contents, routing, scoring dimensions, schema round-trip, schema doc check. Thorough.

**TDD shape verdict:** Good coverage. The dedup test (N2) has an inconsistent key definition vs. Risks, but the test intent is correct. No missing critical test dimensions.

---

### Rollback Assessment

The plan creates new artifacts only — no existing files are modified except `knowledge/seeds/schema.md` (new section added) and `docs/plans/README.md` (index row added). Rollback is straightforward:
1. Delete the 4 new scripts + 4 new test files + 1 new YAML ledger + 1 new report
2. Revert the schema.md section addition
3. Revert the README.md index row

No schema migrations, no database changes, no infrastructure modifications. **Rollback risk: negligible.**

---

## Part 3: Classification

### Verdict: `APPROVE_FOR_CROSS_REVIEW`

**Rationale:**
- All 7 feed17 findings verified resolved
- Fresh adversarial pass found 3 LOW findings (N1-N3) and 3 INFO observations (N4-N6)
- No MAJOR or MINOR findings
- LOW findings are design ambiguities an implementer can resolve during TDD without plan revision
- Plan is structurally sound, evidence-rich (12 distinct sources, all cited with specifics), well-bounded vs siblings, and follows the template contract
- Acceptance criteria are exhaustive and testable
- TDD coverage is thorough (26 tests across 4 files)
- Rollback is trivial
- No blocking dependencies on unfinished sibling work

The plan is ready for Codex/Gemini cross-review. The 3 LOW findings (N1-N3) can optionally be patched before or after cross-review — they are unlikely to trigger MINOR/MAJOR from external reviewers because they are internal consistency nits, not structural defects.

---

## Part 4: Suggested Edit Hunks (Optional, Not Applied)

### N2 fix — Dedup key alignment

**Location:** Line 388 (TDD Test List table)

Old:
```
| test_orchestrator_dedupes_by_source_path_plus_summary | identical (path, summary) pair appears once | duplicate fixture | one candidate, not two |
```

New:
```
| test_orchestrator_dedupes_by_normalized_summary_plus_issue_ref | identical (normalized summary[:120], issue_ref) pair across sources yields one candidate | cross-source duplicate fixture (handoff + review citing same finding) | one candidate, not two; second logged in report Suppressed Duplicates |
```

### N3 fix — existing_wiki_page_for pseudocode vs Open Question

**Location:** Line 188 (Pseudocode § orchestrator)

Old:
```
            c["extend_or_create"]   = "extend" if existing_wiki_page_for(c) else "create"
```

New:
```
            c["extend_or_create"]   = "create"  # v1: default; wiki-index lookup deferred (see Open Questions)
```

### N6 fix — Score threshold in merge contract

**Location:** Line 35, after "Shape compatibility ≠ score comparability."

Add:
```
Score threshold also diverges: this plan keeps candidates at score ≥ 1 (appropriate for noisier freeform-Markdown sources), while #2375 keeps ≥ 2 (appropriate for structured JSONL). Any unified ledger view must apply a common threshold or normalize.
```

---

## Part 5: Next Safe Follow-Up Lane

1. **Dispatch Codex/Gemini cross-review** of the post-feed18 plan:
   ```bash
   bash scripts/review/plan-review-fanout.sh docs/plans/2026-04-27-issue-2374-transient-promotion-candidate-queue.md
   ```
   This is the next gate before `status:plan-review`.

2. **(Optional) Feed20 micro-patch** for N2/N3/N6 — 3 targeted edits, all LOW. Can be done before or after cross-review. Not blocking.

3. **Do NOT implement** until:
   - Cross-review verdicts from Codex + Gemini are in
   - Plan status is moved to `status:plan-review`
   - User approval moves it to `status:plan-approved`

---

## Boundary Compliance Statement

- Did NOT mutate GitHub: no `gh issue comment`, labels, PRs, closes, merges, or pushes
- Did NOT create or edit `.planning/plan-approved/*` markers
- Did NOT implement code or launch tests
- Did NOT overwrite other lanes' result files
- Wrote exactly one file: this result at `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-rereview-2374-feed19.md`
- Plan status remains `draft` — not marked approved
- All reads were read-only; no repo state mutation

---

## Lane Classification

**`APPROVE_FOR_CROSS_REVIEW`** — plan is ready for multi-provider adversarial review dispatch.
