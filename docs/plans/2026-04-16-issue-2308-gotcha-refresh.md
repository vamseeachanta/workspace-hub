# Plan for #2308: Refresh BROKEN-metadata GOTCHA warnings in 3 skill/doc files

> **Status:** adversarial-reviewed
> **Complexity:** T1
> **Date:** 2026-04-16 (rev-2 after Claude MINOR review)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2308
> **Parent:** #1878 (closed)
> **Review artifacts:** scripts/review/results/2026-04-16-plan-2308-claude.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `.claude/skills/coordination/engineering-issue-workflow/SKILL.md:80` — paragraph beginning "CRITICAL GOTCHA: The index.jsonl (647K records) has all records showing `content_type: "unknown"` and `summary_done: false`". Says metadata is BROKEN and directs agents to use `online-resource-registry.yaml` + `standards-transfer-ledger.yaml` instead.
- Found: same file lines 209-213 — "### The Document Index Metadata Is Broken" subsection in the GOTCHAs reference list. Duplicate of line 80 content.
- Found: `.claude/skills/coordination/workflow-compliance-audit/SKILL.md:60` — audit step 3 bullet: "GOTCHA if all records show `content_type: "unknown"` and `summary_done: false`". Instructs auditor to treat as sign the index is broken.
- Found: `docs/standards/engineering-issue-workflow-skill.md:85` — mirrors the line-80 GOTCHA from engineering-issue-workflow SKILL.md (public doc version).
- Gap: No file currently documents how to query the NEW fields (`content_type` and `summary_done`) that were actually populated by #1878's enrichment.

### Standards
Not applicable — doc-only change.

### LLM Wiki pages consulted
Not applicable — doc-only change inside `.claude/skills/` and `docs/standards/`.

### Documents consulted

| Source | Finding |
|---|---|
| Issue #2308 body | Scope says: replace BROKEN language with new-field guidance. Pre-conditions stated were "≥90% non-other content_type" ✅ and "≥55% summary_done=True" ❌ (actual 16.1%). This plan corrects the second pre-condition to reality. |
| Issue #1878 closeout (#1878#issuecomment-4263745741) | Live enrichment: 100% `content_type` populated; 16.1% `summary_done=True`. Validator PASS with `--summary-done-min 0.10`. |
| #2309 | Proposes splitting `summary_done` into `summary_done` (content-quality) + `summary_file_exists` (87.8%, existence). This plan must NOT pre-emptively reference `summary_file_exists` since that field doesn't exist yet. |
| `data/document-index/index.jsonl` | First-record sample confirms both new fields present and schema stable. |

### Gaps identified

- Four prose blocks across three files tell agents the fields are broken. All four must be replaced with accurate current-state guidance.
- The GOTCHA category in `engineering-issue-workflow/SKILL.md` line 209 may be repurposed to a positive "how to query" entry, or removed if the entry now belongs in a different skill.

<!-- Source count: 5 distinct (issue body + 4 others). Contract requires ≥3. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-16-issue-2308-gotcha-refresh.md` |
| Edit 1 | `.claude/skills/coordination/engineering-issue-workflow/SKILL.md` (line ~80) |
| Edit 2 | `.claude/skills/coordination/engineering-issue-workflow/SKILL.md` (lines ~209-213) |
| Edit 3 | `.claude/skills/coordination/workflow-compliance-audit/SKILL.md` (line ~60) |
| Edit 4 | `docs/standards/engineering-issue-workflow-skill.md` (line ~85) |
| Plan review — Claude | `scripts/review/results/2026-04-16-plan-2308-claude.md` |

---

## Deliverable

Three files carrying BROKEN-metadata GOTCHA warnings are replaced with accurate guidance pointing agents at the now-populated `content_type` and `summary_done` fields, with honest framing that `summary_done=True` rate is 16.1% (not 55%+) because ~72% of records are CAD files.

---

## Pseudocode

**T1 — trivial. See "Edit specifications" below for exact replacement text.**

---

## Edit specifications

Each edit is a find-and-replace within the existing file. Keeping the replacements short preserves the surrounding structure of each GOTCHA section.

### Edit 1 — engineering-issue-workflow/SKILL.md line ~80

**Find:**
```
**CRITICAL GOTCHA:** The index.jsonl (647K records) has all records showing `content_type: "unknown"` and `summary_done: false`. The metadata was wiped or regenerated. Use `online-resource-registry.yaml` (247 entries, current) and `standards-transfer-ledger.yaml` (425 standards, 61.9% coverage) for lookups. These are reliable. The index.jsonl metadata is BROKEN.
```

**Replace with:**
```
**Index metadata usage (post #1878):** `index.jsonl` now carries `content_type` (100% populated, derived from extension) and `summary_done` (True iff a non-empty summary exists on the ace drive). Across the 649K-record corpus, `content_type` is highly discriminating but `summary_done=True` is only ~16% because ~72% of records are CAD files with no extractable text. For curated lookups still prefer `online-resource-registry.yaml` (247 entries) and `standards-transfer-ledger.yaml` (425 standards). See #1878 for enrichment provenance and #2309 for the planned `summary_file_exists` split.
```

### Edit 2 — engineering-issue-workflow/SKILL.md lines ~209-213

**Find:**
```
### The Document Index Metadata Is Broken

**What happened:** Agent searches index.jsonl for document metadata — gets `content_type: unknown` for all 647K records, `summary_done: false`. Agent assumes no data is available.

**How to handle:** Use `online-resource-registry.yaml` (247 entries, current) and `standards-transfer-ledger.yaml` (425 standards, 61.9% coverage) for lookups. These are reliable. The index.jsonl metadata was wiped/regenerated.
```

**Replace with:**
```
### Index metadata reference (post #1878)

**Current state:** `index.jsonl` carries `content_type` (100% populated) and `summary_done` (True for 16.1% of records; the 84% False is dominated by CAD files without extractable text).

**How to query:** Read records directly from `data/document-index/index.jsonl` — fields are present on every record. Validator at `scripts/data/document-index/validate-index-metadata.py` enforces coverage thresholds. For curated engineering lookups (small, domain-specific), `online-resource-registry.yaml` and `standards-transfer-ledger.yaml` remain the reliable complementary sources.
```

### Edit 3 — workflow-compliance-audit/SKILL.md line ~60

**Find:**
```
- **GOTCHA if all records show `content_type: "unknown"` and `summary_done: false`**: The index metadata has been wiped/regenerated. The summary data lives elsewhere. Use `online-resource-registry.yaml` and `standards-transfer-ledger.yaml` as reliable sources instead.
```

**Replace with:**
```
- **Verify index metadata coverage** (post #1878): `content_type` should be populated for 100% of records; `summary_done=True` for ~16% (the rest are mostly CAD files). If either coverage has regressed, run `scripts/data/document-index/validate-index-metadata.py` — exit 1 indicates a regression. `online-resource-registry.yaml` and `standards-transfer-ledger.yaml` remain useful for curated engineering lookups.
```

### Edit 4a — docs/standards/engineering-issue-workflow-skill.md line ~85

**Find:**
```
**CRITICAL GOTCHA:** The index.jsonl (647K records) has all records showing `content_type: "unknown"` and `summary_done: false`. The metadata was wiped or regenerated. Use `online-resource-registry.yaml` (247 entries, current) and `standards-transfer-ledger.yaml` (425 standards, 61.9% coverage) for lookups. These are reliable. The index.jsonl metadata is BROKEN.
```

**Replace with:**
```
**Index metadata usage (post #1878):** `index.jsonl` now carries `content_type` (100% populated, derived from extension) and `summary_done` (True for ~16% of records; 84% False is mostly CAD files with no extractable text). Read the fields directly from the index. `online-resource-registry.yaml` (247 entries) and `standards-transfer-ledger.yaml` (425 standards) remain useful for curated engineering lookups. See #1878 and #2309 for provenance and planned field split.
```

### Edit 4b — docs/standards/engineering-issue-workflow-skill.md lines ~224-228

**(New in rev-2 — found by Claude plan review: this file has a second BROKEN block mirroring SKILL.md lines 209-213.)**

**Find:**
```
### The Document Index Metadata Is Broken

**What happened:** Agent searches index.jsonl for document metadata — gets `content_type: unknown` for all 647K records, `summary_done: false`. Agent assumes no data is available.

**How to handle:** Use `online-resource-registry.yaml` (247 entries, current) and `standards-transfer-ledger.yaml` (425 standards, 61.9% coverage) for lookups. These are reliable. The index.jsonl metadata was wiped/regenerated.
```

**Replace with:**
```
### Index metadata reference (post #1878)

**Current state:** `index.jsonl` carries `content_type` (100% populated) and `summary_done` (True for ~16% of records; the 84% False is dominated by CAD files without extractable text).

**How to query:** Read records directly from `data/document-index/index.jsonl` — fields are present on every record. Validator at `scripts/data/document-index/validate-index-metadata.py` enforces coverage thresholds. For curated engineering lookups (small, domain-specific), `online-resource-registry.yaml` and `standards-transfer-ledger.yaml` remain the reliable complementary sources.
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `.claude/skills/coordination/engineering-issue-workflow/SKILL.md` | Edits 1 and 2 |
| Modify | `.claude/skills/coordination/workflow-compliance-audit/SKILL.md` | Edit 3 |
| Modify | `docs/standards/engineering-issue-workflow-skill.md` | Edits 4a and 4b (rev-2: review found second BROKEN block) |
| Update | `docs/plans/README.md` | Plan row (already added) |

No new code. No tests required — this is a doc edit, not a behavior change.

---

## TDD Test List

Not applicable for T1 docs-only changes. Verification is a grep check after the edits:

| Check | Command |
|---|---|
| No "BROKEN" remnants | `grep -rn "is BROKEN\|metadata was wiped\|metadata was regenerated" .claude/skills/ docs/standards/` → 0 hits |
| Correct references added | `grep -rn "post #1878\|#2309" .claude/skills/coordination/ docs/standards/` → ≥4 hits (one per edit) |

---

## Acceptance Criteria

- [ ] Four prose blocks replaced per the specifications above
- [ ] No `BROKEN` / `wiped` / `regenerated` language referring to the index remains in the three files
- [ ] Each updated section references #1878 for provenance and #2309 for the planned field split (so readers know the semantic is still evolving)
- [ ] No reference to `summary_file_exists` appears (that field doesn't exist yet — it's planned in #2309)
- [ ] `docs/plans/README.md` index row added
- [ ] Adversarial review (single-provider sufficient for T1) logged to `scripts/review/results/`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MINOR → addressed in rev-2 | (1) Edit 4 missed a second BROKEN block at `docs/standards/engineering-issue-workflow-skill.md:224-228`; split into 4a/4b. (2) Note on `workflow-compliance-audit` diagnostic one-liner may give false positives post-enrichment — flagged as out-of-scope follow-up. (3) Wording accurate across all four replacements; `~16%` over `16.1%` is correct. |

**Overall result (rev-1):** MINOR — one mechanical miss, fixed in rev-2.
**Overall result (rev-2):** Ready for approval.

Revisions made in rev-2:
- Split Edit 4 into 4a (line 85) and 4b (lines 224-228), applying Edit 2's replacement text to the second block
- Updated Files-to-Change row and plan Status accordingly
- Captured out-of-scope follow-up idea (update the diagnostic one-liner in `workflow-compliance-audit/SKILL.md:55-57`) in Risks/Open below

---

## Risks and Open Questions

- **Risk:** Agents reading cached/stale copies of the skill files may still see BROKEN warnings until next session. Mitigation: the repo state is the source of truth; cached copies self-refresh.
- **Risk:** The 16.1% figure will move if `summary_done` is redefined in #2309. The new text says "~16%" rather than an exact number to avoid re-editing the doc when #2309 ships.
- **Open:** Should Edit 2 (the standalone GOTCHAs section header) keep the word "GOTCHA" at all, now that the entry is positive guidance? The draft renames it "Index metadata reference" — arguably this entry now belongs under a different heading entirely. I'm keeping it inline to preserve reader navigation muscle memory, but a follow-up restructure is reasonable.
- **Out-of-scope follow-up (flagged by rev-1 Claude review):** `workflow-compliance-audit/SKILL.md:55-57` contains a `python3 -c` diagnostic one-liner that prints `summary_done, content_type` for the *first* record. Post-enrichment, the first record's `summary_done` may legitimately be False (84% of records are), so the one-liner no longer distinguishes "broken" from "normal CAD." A follow-up issue should replace it with a coverage spot-check (and switch to `uv run` per repo convention). Not in scope for #2308.

---

## Complexity: T1

Three files, four find-and-replace edits. No new code, no tests, no architecture change. Single-provider adversarial review is sufficient per the planning skill's T1 guidance.
