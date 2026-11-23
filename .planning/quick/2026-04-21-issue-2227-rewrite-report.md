# Rewrite Report — Issue #2227 Plan v2

**Date:** 2026-04-21
**Plan:** `docs/plans/2026-04-12-issue-2227-ocimf-tandem-csa-z276-wiki-promotion.md`
**Trigger:** Fresh Codex review 2026-04-21 returned MAJOR with 3 blockers; governance rollback `status:plan-approved` → `status:plan-review` per Path C.

---

## What Changed (v1 → v2)

### 1. Resolved the `wiki/standards/` path contradiction (Codex MAJOR #1)

**v1 defect:** Scope Boundaries said "stop if marine-engineering conventions don't permit `wiki/standards/`", but Artifact Map, Files-to-Change, and Acceptance Criteria hard-coded success as creating files at `knowledge/wikis/marine-engineering/wiki/standards/csa-z276-{1,18}.md`. Internally contradictory.

**v2 fix:** Plan is now explicitly **branch-conditional**:
- **Branch A (content-ready):** writes ONLY to `knowledge/wikis/engineering/wiki/standards/` — confirmed git-tracked (via `git ls-files`) and schema-sanctioned (engineering `CLAUDE.md` lists `standards/` in directory structure).
- **Branch B (content-blocked — current state):** no wiki writes; post blocker comment + open follow-up issues.
- CSA pages are **explicitly deferred out of this issue** until a separate marine-wiki taxonomy + gitignore decision lands.

No deliverable is simultaneously "must exist" and "only if conventions permit" anymore.

### 2. Concretized the TDD contract (Codex MAJOR #2)

**v1 defect:** "Verification List" was conceptual (`verify_csa_pages_exist`, `verify_provenance_backlinks_present`) with no test location, runner, or harness named.

**v2 fix:** `§TDD Test List` now specifies:
- **Test file:** `tests/knowledge/test_ocimf_tandem_promotion.py` (new)
- **Runner commands:** `uv run pytest tests/knowledge/test_ocimf_tandem_promotion.py -v` + `uv run scripts/knowledge/llm_wiki.py lint --wiki engineering`
- **12 concrete tests (T1–T12):** entry gates (T1 content, T2 taxonomy), structural (T3–T10), existing-lint integration (T11), content-quality guard (T12 — guards against empty-summary regurgitation)
- Each test names its runner, assertion mechanism, expected outcome today, and which branch it gates

### 3. Pinned the prerequisite matrix (Codex MAJOR #3)

**v1 defect:** Resource Intel said `FAIL for execution readiness` but plan still framed body as implementation-ready without pinning concrete artifact paths.

**v2 fix:** `§Prerequisite Matrix` now lists:
- Current `gh issue view` state of #2216 (OPEN plan-review), #2225 (CLOSED 2026-04-11), #2207 (CLOSED), #2245 (CLOSED 2026-04-13)
- Per-target sha256 doc_keys and exact summary artifact paths
- Explicit blocker/non-blocker classification per row
- Two named sub-gates (CONTENT + MARINE_TAXONOMY) with which issue they block

### 4. Additional v2 findings baked in

- `.gitignore:491` ignores `/knowledge/wikis/*` with only `engineering/` exempted (line 492) — confirmed marine-engineering wiki is not durable without a gitignore amendment
- `knowledge/wikis/marine-engineering/CLAUDE.md` schema (lines 8-23) does NOT list `standards/` as a sanctioned category — confirmed taxonomy gap
- Summary JSON files DO exist for all three sha256 doc_keys, but with `summary: ""` and `text_preview: ""` — the reuse-contract schema is satisfied, but content is empty (per #2245 handoff)
- `scripts/knowledge/llm_wiki.py lint` frontmatter check traverses `standards/` (line 632) but orphan/link checks do not (line 748) — soft cross-link enforcement
- Plan header `Status:` updated from `draft` → `plan-review (v2)`; review-artifacts line updated to cite 2026-04-21 artifacts

---

## Claude v2 Verdict: MINOR

Full artifact: `scripts/review/results/2026-04-21-plan-2227-claude-rev-2.md`

**Codex v1 MAJORs all resolved.** Residual MINOR issues:

1. **T12 content-quality gate may be unsatisfiable under current blocker** — summary artifacts have empty `summary:` field, so even the sanctioned engineering-wiki OCIMF Tandem page cannot ground a >200-word body. T12 should be promoted from post-condition to an entry sub-gate (same level as T1).
2. **Engineering `index.md` `## Standards` section existence unchecked** — plan admits this gap but does not add a pre-write check to TDD or Files-to-Change.
3. **"Current branch: B" not made explicit** — as of 2026-04-21, every prereq-matrix row is blocking, so Branch B is the only reachable path today. Plan should state this live state up-front for batch agents.
4. **T2 uses unfalsifiable "or equivalent"** — either enumerate acceptable gitignore patterns or drop T2 (since no CSA work happens in this issue regardless).
5. **History entry for Claude 2026-04-15 understates severity** — prior comment recorded MAJOR with sharper blockers, not "needs-revision minor".

None rise to MAJOR. The plan is approval-ready contingent on a short follow-up revision addressing those MINORs, or user can accept MINORs and approve as-is.

---

## New Risks (introduced or newly surfaced in v2)

1. **Branch B is likely the true current deliverable, not Branch A.** With T1 failing for all three targets today, execution of this plan lands zero wiki pages and two follow-up issues. The plan's structure obscures that reality. Batch-agent risk: an agent that reads §Deliverable without tracing into §Prerequisite Matrix could believe Branch A is the live path.

2. **T12 reveals a deeper blocker than v1 acknowledged.** v1 treated "summary artifacts missing" as a binary gate (schema present / not present). v2 explicitly introduces content-quality testing (T12) which, under current state, would block even the engineering-wiki Tandem page. This makes #2245 a harder prerequisite than the parent #2216 tree originally scoped — a re-extraction workstream is effectively required, not optional.

3. **Marine-wiki taxonomy decision is now a carved-out child issue** that does not yet exist. Risk: decision drifts as metadata-only sweep (#2260) progresses and the two trees evolve inconsistent conventions.

4. **Engineering wiki may accrete marine-domain standards** (CSA LNG content) if the taxonomy follow-up chooses "put everything in engineering" as the expedient answer. That would distort engineering wiki's stated focus ("engineering methodology") per its own `CLAUDE.md`.

5. **Plan's branch-conditional structure is novel in this repo.** Existing batch-agent contracts assume a single linear plan. If agents cannot parse "run Branch B today, reserve Branch A for re-execution without re-approval", the plan may need an additional per-branch approval protocol clarification.

---

## Artifacts Produced This Session

- `docs/plans/2026-04-12-issue-2227-ocimf-tandem-csa-z276-wiki-promotion.md` — v2 plan (rewritten in place, history preserved in §Adversarial Review History)
- `scripts/review/results/2026-04-21-plan-2227-claude-rev-2.md` — Claude v2 self-review (MINOR verdict)
- `.planning/quick/2026-04-21-issue-2227-rewrite-report.md` — this report

## NOT Done This Session (per constraints)

- No commits, no pushes
- No Codex/Gemini dispatch (main session only)
- No `status:plan-approved` application (user-only)
- No wiki content changes (plan-only revision)

## Next Steps (user decision)

1. **Address Claude v2 MINORs** then dispatch fresh Codex + Gemini reviews
2. **Accept MINORs as-is** and apply `status:plan-approved` with Branch B execution expected
3. **Reframe as Branch B-only plan for today** (drop Branch A into a separate future-scope issue) — cleanest separation, but breaks narrative continuity with the existing issue body
