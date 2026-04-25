# Plan for #2227: Promote OCIMF Tandem Mooring and CSA Z276 Coverage into LLM-Wikis

> **Status:** draft (v4 — re-decouples CSA Z276 from OCIMF Tandem via formal phase split now that #2471 `wiki/standards/` sanction is plan-approved at `cb1c4a972`; addresses r3 Gemini MAJOR findings; Codex r3 UNAVAILABLE — CLI regression #2479)
> **Complexity:** T2
> **Date:** 2026-04-12 (v1) / 2026-04-21 (v2 revision) / 2026-04-23 (v3 revision) / 2026-04-24 (v4 revision)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2227
> **Parent:** https://github.com/vamseeachanta/workspace-hub/issues/2216
> **Review artifacts:** `scripts/review/results/2026-04-21-plan-2227-codex.md` (MAJOR, r1) | `scripts/review/results/2026-04-21-plan-2227-gemini.md` (APPROVE, r1) | `scripts/review/results/2026-04-23-plan-2227-claude.md` (MAJOR, r2) | `scripts/review/results/2026-04-23-plan-2227-codex.md` (UNAVAILABLE, r3 — codex-cli 0.124.0 stdin-hang #2479) | `scripts/review/results/2026-04-23-plan-2227-gemini.md` (MAJOR, r3) | `scripts/review/results/2026-04-23-plan-2227-disagreement.md`

---

## Resource Intelligence Summary

### Existing repo code
- Found: `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` — existing OCIMF MEG4 page, git-tracked (confirmed via `git ls-files`).
- Found: `knowledge/wikis/engineering/wiki/standards/` — directory exists and is git-tracked, containing `api-579-ffs.md`, `dnv-os-e301.md`, `dnv-rp-c203.md`, `dnv-rp-c205.md`, `dnv-rp-f101.md`, `dnv-rp-f105.md`, `ocimf-meg4.md`. (Reviewer note: Gemini r3 Finding 1 reported these paths absent at HEAD — that is the documented sandbox-overlay-blindness defect; verified present via `git ls-files` from the main workspace.)
- Found: `knowledge/wikis/marine-engineering/wiki/` — directory is gitignored (`.gitignore:492 /knowledge/wikis/*`; only `!/knowledge/wikis/engineering/` at line 493 and `!/knowledge/wikis/cross-links.md` at line 494 are re-included). Subdirs present: `comparisons/`, `concepts/`, `entities/`, `sources/`, `visualizations/`. NO `standards/` directory, and marine-engineering `CLAUDE.md` schema (lines 6-23) does not list `standards/` as a sanctioned `wiki/` subcategory (literal `standards/` appears only at line 11 under `raw/`).
- Found: `scripts/knowledge/llm_wiki.py` — lint command at `cmd_lint` (line 683) validates frontmatter for `entities/concepts/sources/comparisons/standards/workflows` (line 632). Supports `standards/` in frontmatter check but orphan/link checks only traverse `entities/concepts/sources/comparisons` (line 748).
- Found: `data/document-index/summaries/sha256:5e5f...json`, `...:b576...json`, `...:3aa1...json` — summary artifacts EXIST for all three target doc_keys, with `summary: ""` across all three. `text_preview` is heterogeneous: OCIMF-TANDEM (`5e5f…`) preview length 0; CSA Z276.1-20 (`b576…`) and CSA Z276.18 (`3aa1…`) each carry a 1000-char corrupted-OCR preview (first 200 chars of `b576…`: `"pyorat\npakota\nmakaamaan\nlujana\njakcanut\ntiedocca\nperaan\ncannikka\n…"`; first 200 of `3aa1…`: `"monen\nkuunnella\ncannikka\ncamoin\npyctyvat\nvaatteitaan\n…"`). Downstream: OCIMF remediation will be "extract preview content"; CSA remediation will be "fix encoding/OCR corruption".
- User decision on #2471 (2026-04-23 issue comment): `wiki/standards/` sanctioned as a first-class page type. **#2471 v3 reached `status:plan-approved` at commit `cb1c4a972` on `plan/issue-2471-standards-wiki-path-sanction`** (forward-adopt status); the codification (schema CLAUDE.md amendments + per-wiki gitignore re-include + lint path) will land via that branch. v4 forward-adopts the sanction: CSA pages will land at `knowledge/wikis/marine-engineering/wiki/standards/csa-z276-1-20.md` and `…/csa-z276-18.md` once #2471 codification merges to main, and will carry `code_id`, `publisher`, `revision` frontmatter per the contract.

### Standards
| Standard | Ledger status | doc_key (sha256) | Summary artifact | Content ready? |
|---|---|---|---|---|
| `OCIMF-TANDEM-MOORING` | done | `sha256:5e5f61e785295f0ac849399bb302cb5192ca84c108e6a57e82b8cc83b8b431af` | file exists, `summary=""` | **NO** — blocker from #2245 handoff |
| `OCIMF-MEG4-2018` | done | (existing wiki page); no new summary required | n/a for narrow historical update | partial — update only if ledger notes warrant |
| `CSA-Z276.1-20` | done | `sha256:b576ada30e9ccea727ecab10e1f2a0e435613b25147e3bbb2b3f3d2b718766fd` | file exists, `summary=""` | **NO** — blocker (Phase 2 only) |
| `CSA-Z276.18` | done | `sha256:3aa1fdc3e2c73e1f9c3bb476e5eb663a7742518462bf1abefcbe26b7efd87fd4` | file exists, `summary=""` | **NO** — blocker (Phase 2 only) |
| `CSA-Z276.2-19` | done | — | — | **OUT OF SCOPE** (routed to #2283 via #2244 triage) |

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` — current page; cross-link to tandem will be added narrowly (≤ 10 lines, see T7).
- `knowledge/wikis/engineering/wiki/index.md` — engineering standards section (`## Standards (7 pages)` at line 99) lists existing `ocimf-meg4` entry; Phase 1 will add a row for `ocimf-tandem-mooring`.
- `knowledge/wikis/engineering/wiki/log.md` — promotion log, append-only.
- `knowledge/wikis/marine-engineering/wiki/index.md` — has `## Entities | ## Concepts | ## Sources | ## Comparisons` sections; NO `## Standards` heading. Phase 2 will add the section once codification lands.
- `knowledge/wikis/marine-engineering/CLAUDE.md` — schema does NOT yet sanction `wiki/standards/`; the #2471 codification plan will amend.
- `knowledge/wikis/engineering/CLAUDE.md` — sanctions `wiki/{concepts,entities,sources,standards,workflows}/`.

### Documents consulted
- `docs/plans/2026-04-11-issue-2216-acma-codes-llm-wiki-repo-intelligence-integration.md` — parent approved plan.
- `docs/plans/2026-04-12-issue-2245-acma-summary-classification-unblock.md` — prerequisite; CLOSED 2026-04-13 with `ready_for_2227: false` handoff artifact.
- `docs/plans/2026-04-11-issue-2225-acma-codes-source-registration-and-initial-indexing.md` — CLOSED 2026-04-11 (completed).
- `docs/plans/2026-04-16-issue-2207-standards-codes-provenance-reuse-contract.md` — CLOSED; defines the reuse contract this plan consumes.
- `docs/plans/2026-04-23-issue-2471-standards-wiki-path-sanction.md` (on `plan/issue-2471-standards-wiki-path-sanction`) — Phase 2 prereq (codification of `wiki/standards/` schema + lint + gitignore re-include).
- `docs/reports/acma-wiki-unblock-2245-handoff.yaml` — authoritative per-target blocker evidence.
- `.claude/rules/calc-citation-contract.md` — mandates `code_id`/`publisher`/`revision` frontmatter on standards pages so downstream calc modules can emit Citations against them.
- Issue #2227 comment thread (2026-04-12 → 2026-04-23): #2244 triage routed broader CSA/API breadth to #2283/#2284/#2285/#2286/#2287; rollback 2026-04-21 15:07 moved label → `status:plan-review`.

### Gaps identified
- Reusable summaries for all three target doc_keys are unusable today; all three have `summary: ""`, and `text_preview` is either empty (OCIMF) or corrupted OCR (CSA x2).
- `knowledge/wikis/marine-engineering/` is gitignored — promoting CSA pages there will require the gitignore re-include landing via the #2471 codification.
- Marine-engineering `CLAUDE.md` schema does not yet list `wiki/standards/` as a sanctioned directory; the #2471 sanction is plan-approved but the codification has not yet merged.
- `llm_wiki.py lint` orphan/link checks do not traverse `standards/` — Phase 1 hardens this with explicit T13 inbound-link assertion.

<!-- Verification (v4): distinct sources consulted = 18+ (3 ledger entries + 3 summary JSON files + 3 gitignore lines + 2 wiki CLAUDE.md files + 5 prior plans + 1 handoff yaml + 5 review artifacts inc r3 triad + disagreement + 1 issue thread + 1 #2471 decision comment + calc-citation contract rule + lint source). -->

---

## Phase Split (v4 structural change)

**The CSA Z276 coverage is formally separated from the OCIMF Tandem coverage as Phase 2.** v3 nested CSA work as a sub-branch of #2227 with a `MARINE_TAXONOMY_SUB_GATE` guard; that coupled the OCIMF Tandem promotion to two unrelated remediations (CSA OCR fix AND #2471 codification). v4 lifts that coupling.

| Phase | Scope | Branch (git) | Prereqs | Status |
|---|---|---|---|---|
| **Phase 1** | OCIMF Tandem Mooring page in engineering wiki + narrow `ocimf-meg4.md` update + index/log entries + tests | `feat/issue-2227-ocimf-tandem-engineering-wiki` | OCIMF preview content (#2245 follow-up) only | Drives this issue's deliverable when content sub-gate clears |
| **Phase 2** | CSA Z276.1-20 + CSA Z276.18 pages in marine-engineering wiki at `wiki/standards/`, with `code_id`/`publisher`/`revision` frontmatter | new branch in a follow-up issue (Phase 2 split-off) | (a) #2471 codification merged to main; (b) CSA OCR remediation; (c) per-code wiki routing decision | **Deferred from #2227**; opens as new GH issue tracked from #2227 |

**Why the split:**
- v3 reviewer (Codex r1, sustained) flagged that coupling CSA to OCIMF Tandem in one branch creates a dependency between two independent prereqs — OCIMF only needs preview-content extraction, while CSA needs OCR fix + #2471 codification + per-code routing. Either side could be ready while the other remains blocked, and a coupled branch forces both to wait.
- The #2471 sanction is now plan-approved (`cb1c4a972` on `plan/issue-2471-standards-wiki-path-sanction`), so CSA has a clear codified path to land at `knowledge/wikis/marine-engineering/wiki/standards/csa-z276-1-20.md` once codification merges. There is no longer a taxonomy-decision blocker — only a sequencing blocker. Sequencing is best handled as a separate phase issue, not nested branch logic inside #2227.
- Splitting also lets Phase 1 be reviewed/approved/landed against just its own gates; Phase 2 will receive its own adversarial review against the codified `wiki/standards/` contract once #2471 merges.

#2227's deliverable is now **Phase 1 only**. Phase 2 will open as a follow-up issue at execution time (see Phase-Split Acceptance below).

---

## Deliverable

**Branch-conditional deliverable for Phase 1.** Two execution branches, scoped to the OCIMF Tandem work in the engineering wiki:

- **Branch A (CONTENT-READY):** OCIMF Tandem Mooring page lands in `knowledge/wikis/engineering/wiki/standards/` (the git-tracked, schema-sanctioned location), plus a narrowly grounded update to `ocimf-meg4.md`, index/log row, and the test file.
- **Branch B (CONTENT-BLOCKED — current state):** No wiki pages will be written. Plan execution will produce (1) a blocker comment on #2227 citing the specific OCIMF preview-content gap, (2) a follow-up issue for OCIMF preview-content extraction, and (3) a follow-up issue for the Phase 2 CSA work (Phase split). #2227 stays in `status:in-progress` (not `closed`) until OCIMF Branch A lands.

CSA pages are NOT a Branch A or Branch B deliverable for #2227 anymore — they are Phase 2 in a separate issue.

---

## Scope Boundaries

### In scope now (Branch A path, Phase 1, only if content sub-gate passes)
- Create `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` (git-tracked location). Frontmatter MUST include forward-adopted #2471 fields: `code_id: OCIMF-TANDEM-MOORING`, `publisher: OCIMF`, `revision: <as-recorded-in-ledger>` so downstream calc modules per `.claude/rules/calc-citation-contract.md` can resolve citations against this page once they need to.
- Narrowly grounded update to `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` citing tandem-mooring cross-reference from ledger notes only (≤ 10 added lines per T7).
- Append promotion entry to `knowledge/wikis/engineering/wiki/log.md`; add row to `knowledge/wikis/engineering/wiki/index.md` under `## Standards`.
- Commit `tests/knowledge/test_ocimf_tandem_promotion.py` with all listed tests, and conditional skip logic per T-skip rules (see §TDD).

### In scope now (Branch B — current state, no wiki writes)
- Post blocker comment on #2227 summarizing the content gap, citing previews: OCIMF `5e5f…` preview length 0; CSA `b576…` preview 1000 chars of corrupted OCR; CSA `3aa1…` preview 1000 chars of corrupted OCR.
- Open the **OCIMF preview-content** follow-up issue via concrete `gh issue create` invocation (see Pseudocode B1).
- Open the **Phase 2 CSA** follow-up issue via concrete `gh issue create` invocation (see Pseudocode B2). Body links to #2471 codification branch and the two CSA OCR-remediation tasks.
- Commit the `tests/knowledge/test_ocimf_tandem_promotion.py` file with the conditional-skip logic so Branch B does not ship a permanently red test suite (Gemini r3 F5).

### Explicitly out of scope (this issue)
- CSA Z276.1-20 and CSA Z276.18 page authoring (→ Phase 2, separate follow-up issue).
- CSA Z276.2-19 (→ #2283), additional OCIMF (→ #2284), API RP 2SK (→ #2285), SIGTTO (→ #2286), LR/Noble Denton (→ #2287).
- Re-parsing DRM-protected source PDFs.
- Modifying `marine-engineering/CLAUDE.md` schema or `.gitignore` (those land via #2471 codification, not here).

---

## Prerequisite Matrix

| Prereq | Current state | Blocker? | Source |
|---|---|---|---|
| #2216 (parent umbrella) | OPEN, `status:plan-review` | Non-blocking for this child | `gh issue view 2216` |
| #2225 (source registration) | CLOSED 2026-04-11, `status:plan-approved` | NOT blocking | `gh issue view 2225` |
| #2207 (reuse contract) | CLOSED, `status:plan-approved` | NOT blocking | `gh issue view 2207` |
| #2245 OCIMF preview content | CLOSED 2026-04-13, OCIMF preview length 0 in `sha256:5e5f….json` | **Phase 1 content sub-gate: BLOCKING** | `docs/reports/acma-wiki-unblock-2245-handoff.yaml`, `data/document-index/summaries/sha256:5e5f….json` |
| #2471 `wiki/standards/` page-type sanction (DECISION) | user-approved 2026-04-23; v3 plan-approved at `cb1c4a972` on `plan/issue-2471-standards-wiki-path-sanction` | **NOT BLOCKING for Phase 1** (engineering wiki already sanctions `wiki/standards/`); BLOCKING for Phase 2 | `gh issue view 2471`, branch `plan/issue-2471-standards-wiki-path-sanction` |
| #2471 codification merged to main | not yet merged | **NOT BLOCKING for Phase 1**; BLOCKING for Phase 2 | check via `git merge-base --is-ancestor plan/issue-2471-standards-wiki-path-sanction origin/main` |
| engineering wiki `wiki/standards/` already sanctioned | line 7 of `knowledge/wikis/engineering/CLAUDE.md`: `Pages: wiki/{concepts,entities,sources,standards,workflows}/` | **NOT BLOCKING** for Phase 1 | `knowledge/wikis/engineering/CLAUDE.md` |

**Classification rule (v4 simplified):** Phase 1 (OCIMF Tandem, engineering wiki) needs ONLY the content sub-gate. Today the content sub-gate fails for OCIMF (preview length 0) → Phase 1 will execute as Branch B (open follow-ups, no wiki writes). Phase 2 (CSA, marine wiki) is a separate issue and is not gated on by #2227's closure path.

---

## Pseudocode

```text
# ---------- Entry gate ----------
load handoff_yaml = yaml.load("docs/reports/acma-wiki-unblock-2245-handoff.yaml")
load summary_5e5f = json.load("data/document-index/summaries/sha256:5e5f...json")

# Phase 1 content sub-gate hinges on OCIMF only (CSA decoupled to Phase 2).
if handoff_yaml.ready_for_2227 is False
   OR summary_5e5f.summary == ""
   OR len(summary_5e5f.text_preview) == 0:
    set CONTENT_SUB_GATE = FAIL
else:
    set CONTENT_SUB_GATE = PASS

# ---------- Route ----------
if CONTENT_SUB_GATE == FAIL:
    execute Branch B
    exit
else:
    execute Branch A
    exit

# ---------- Branch A (CONTENT_SUB_GATE == PASS) ----------
create knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md:
    frontmatter:
        title: "OCIMF Tandem Mooring and Offloading Guidelines"
        tags: [ocimf, tandem, mooring, fpso]
        added: <today>
        last_updated: <today>
        sources: [doc_key=sha256:5e5f...]
        domain: marine
        # Forward-adopted from #2471 contract (calc-citation-contract.md)
        code_id: OCIMF-TANDEM-MOORING
        publisher: OCIMF
        revision: <from-ledger>
        cross_links: [ocimf-meg4]
    body: scope, provenance back-links (doc_key, source_ref, promoted_from=2227)
          content grounded strictly in OCIMF-TANDEM-MOORING ledger entry + summary artifact

modify knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md:
    preserve all existing content
    add "## Related Standards" section with bounded tandem-mooring cross-reference
    enforce ≤ 10 added lines (T7 ceiling)

append knowledge/wikis/engineering/wiki/log.md:
    one entry: "## [YYYY-MM-DD] ingest | OCIMF-TANDEM-MOORING promotion (#2227)"

modify knowledge/wikis/engineering/wiki/index.md:
    add row under "## Standards (7 pages)" for ocimf-tandem-mooring (will become 8 pages — bump heading count)

# ---------- Branch B (CONTENT_SUB_GATE == FAIL) ----------
# B1: OCIMF preview-content remediation follow-up
gh issue create \
  --title "OCIMF-TANDEM-MOORING preview content extraction (unblocks #2227 Phase 1)" \
  --body "$(cat <<'EOF'
Source: data/document-index/summaries/sha256:5e5f61e785295f0ac849399bb302cb5192ca84c108e6a57e82b8cc83b8b431af.json
Current state: text_preview length 0; summary is empty string.
Action: extract preview content via alt toolchain (ocrmypdf or manual review on a machine that can read the source).
Acceptance: summary artifact updated with non-empty `summary` and `text_preview` ≥ 200 chars; #2227 unblocked for Phase 1 Branch A.
EOF
)" \
  --label "type:remediation,parent:2216,blocks:2227"

# B2: Phase 2 CSA follow-up (formal phase split — this is the v4 decoupling)
gh issue create \
  --title "Phase 2: Promote CSA Z276.1-20 + Z276.18 into marine-engineering wiki/standards/" \
  --body "$(cat <<'EOF'
Phase split off from #2227 to decouple CSA work from OCIMF Tandem.

Targets:
- knowledge/wikis/marine-engineering/wiki/standards/csa-z276-1-20.md
- knowledge/wikis/marine-engineering/wiki/standards/csa-z276-18.md

Frontmatter contract (from #2471 + .claude/rules/calc-citation-contract.md):
- code_id, publisher, revision (REQUIRED)

Prereqs:
1. #2471 codification merged to main (schema CLAUDE.md amendment + .gitignore re-include for marine wiki/standards/ + lint path coverage). Branch: plan/issue-2471-standards-wiki-path-sanction @ cb1c4a972.
2. CSA OCR remediation: text_preview for both CSA artifacts is currently 1000-char corrupted OCR (Finnish-looking tokens). Requires alt OCR toolchain. Source artifacts:
   - data/document-index/summaries/sha256:b576ada30e9ccea727ecab10e1f2a0e435613b25147e3bbb2b3f3d2b718766fd.json
   - data/document-index/summaries/sha256:3aa1fdc3e2c73e1f9c3bb476e5eb663a7742518462bf1abefcbe26b7efd87fd4.json
3. Per-code wiki routing decision: marine-engineering vs naval-architecture (per #2471 sanction the routing is per-standard owner).

This issue does NOT block #2227 closure — #2227 closes when Phase 1 (OCIMF Tandem) lands.
EOF
)" \
  --label "type:wiki-promotion,parent:2216,split-from:2227"

# B3: blocker comment on #2227
gh issue comment 2227 --body "Phase 1 content sub-gate FAIL on $(date -I): OCIMF text_preview length 0. \
CSA work decoupled to Phase 2 follow-up. See ${B1_url} and ${B2_url}."

# ---------- Verification ----------
run uv run scripts/knowledge/llm_wiki.py lint --wiki engineering
assert exit 0 OR only warnings (no errors)
run TDD tests with branch-aware skip:
  CONTENT_SUB_GATE_PASS=<bool> uv run pytest tests/knowledge/test_ocimf_tandem_promotion.py -v
```

---

## Files to Change (branch-scoped)

### Branch A (CONTENT_SUB_GATE == PASS) — engineering wiki only, Phase 1
| Action | Path | Reason |
|---|---|---|
| Create | `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` | net-new OCIMF guideline page (git-tracked, schema-sanctioned); includes `code_id`/`publisher`/`revision` frontmatter forward-adopted from #2471 |
| Modify | `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` | narrowly grounded tandem cross-reference only, ≤ 10 added lines |
| Modify | `knowledge/wikis/engineering/wiki/index.md` | add row under `## Standards`; bump page count |
| Modify | `knowledge/wikis/engineering/wiki/log.md` | append promotion log entry |
| Create | `tests/knowledge/test_ocimf_tandem_promotion.py` | T1–T13 with branch-aware skip logic |

### Branch B (CONTENT_SUB_GATE == FAIL — current state)
| Action | Path | Reason |
|---|---|---|
| Create | `tests/knowledge/test_ocimf_tandem_promotion.py` | committed with branch-aware skip; does NOT ship red tests on Branch B (Gemini r3 F5) |
| (no wiki file changes) | — | comment-only |
| (gh CLI) | new GH issue: OCIMF preview-content remediation | Pseudocode B1 |
| (gh CLI) | new GH issue: Phase 2 CSA promotion | Pseudocode B2 |
| (gh CLI) | comment on #2227 | Pseudocode B3 |

### CSA pages — never in #2227's file list
Phase 2 owns CSA file changes in a separate branch under a separate issue. No CSA file changes will land in any branch of #2227.

---

## TDD Test List

All tests will live at `tests/knowledge/test_ocimf_tandem_promotion.py` (new file) and will run via `uv run pytest tests/knowledge/test_ocimf_tandem_promotion.py -v`. Repo-integrated lint runs via `uv run scripts/knowledge/llm_wiki.py lint --wiki engineering`.

**Branch-aware skip rule (v4, addresses Gemini r3 F5):** the test module will declare a module-level fixture that reads the runtime branch state from environment variable `CONTENT_SUB_GATE_PASS` (set by the execution wrapper from the entry-gate result; defaults to reading the artifact directly if unset). Tests T3–T13 will be decorated with `@pytest.mark.skipif(not CONTENT_SUB_GATE_PASS, reason="Branch B — wiki writes deliberately deferred")`. Tests T1–T2 (gates) and the negative test T-Bneg run unconditionally. Result: under Branch B execution the suite passes (T1 fails as expected? — see T1 spec; T1 is structured to PASS when sub-gate evaluation is correct, regardless of pass/fail outcome).

| Test ID | Test name | What it verifies | Runner | Expected outcome | Gates which branch |
|---|---|---|---|---|---|
| T1 | `test_prereq_content_sub_gate_evaluation` | Reads `acma-wiki-unblock-2245-handoff.yaml` and `summaries/sha256:5e5f….json`; asserts the `CONTENT_SUB_GATE` evaluation matches the documented rule (handoff `ready_for_2227` AND OCIMF summary non-empty AND OCIMF preview non-empty). The test checks the EVALUATION is correct, not the outcome — it always passes if the gate logic is implemented correctly, regardless of whether the result is PASS or FAIL. | pytest | always PASS (validates the gate code, not the data) | entry gate (always run) |
| T-Bneg | `test_branch_b_no_wiki_writes_when_gate_fails` | If `CONTENT_SUB_GATE` evaluates FAIL, asserts that `git diff --name-only --diff-filter=A origin/main..HEAD -- knowledge/wikis/engineering/wiki/standards/` is empty. | pytest | PASS under Branch B; skipped under Branch A | Branch B safety net |
| T3 | `test_ocimf_tandem_page_exists` | `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` exists | pytest | PASS post-Branch A; SKIPPED on Branch B | Branch A |
| T4 | `test_ocimf_tandem_frontmatter_valid` | Page has `title`, `tags`, `added`, `last_updated`, `sources`, `domain=marine` AND the v4-required forward-adopted #2471 fields `code_id`, `publisher`, `revision` (parsed via `_parse_frontmatter` helper in `scripts/knowledge/llm_wiki.py`) | pytest | PASS post-Branch A; SKIPPED on Branch B | Branch A |
| T5 | `test_ocimf_tandem_provenance_fields` | Page body contains `doc_key: sha256:5e5f...`, `source_ref` pointing to ledger entry, and `promoted_from: 2227` | pytest | PASS post-Branch A; SKIPPED on Branch B | Branch A |
| T6 | `test_ocimf_tandem_cross_reference_to_meg4` | Page contains a `[[ocimf-meg4]]` or equivalent markdown link back to the MEG4 page | pytest | PASS post-Branch A; SKIPPED on Branch B | Branch A |
| T7 | `test_ocimf_meg4_scope_narrow` | Diff of `ocimf-meg4.md` vs `origin/main` has ≤ **10 lines added** (`N_MAX_ADDED_LINES = 10` — accommodates a "## Related Standards" header + ≤ 2-item bullet list + one inbound-link sentence; exceeding this is a scope-creep signal requiring plan revision), **0 lines removed**, and every added line either (a) sits within a newly-added `## Related Standards` section, or (b) contains the literal string `OCIMF-TANDEM-MOORING` or `[[ocimf-tandem-mooring]]`. | pytest (parses `git diff --unified=0 origin/main -- knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md`) | PASS post-Branch A; SKIPPED on Branch B | Branch A |
| T8 | `test_engineering_index_has_tandem_row` | `knowledge/wikis/engineering/wiki/index.md` contains a row with `ocimf-tandem-mooring.md` under Standards section AND the heading count was bumped from 7 to 8 | pytest (regex match in Standards table) | PASS post-Branch A; SKIPPED on Branch B | Branch A |
| T9 | `test_engineering_log_has_promotion_entry` | `knowledge/wikis/engineering/wiki/log.md` contains a `## [YYYY-MM-DD] ingest | OCIMF-TANDEM-MOORING promotion (#2227)` entry | pytest | PASS post-Branch A; SKIPPED on Branch B | Branch A |
| T10 | `test_no_out_of_scope_pages` | Among **newly-ADDED files only** (use `git diff --name-only --diff-filter=A origin/main..HEAD`), there is exactly one under `knowledge/wikis/engineering/wiki/standards/` (namely `ocimf-tandem-mooring.md`) and zero anywhere under `knowledge/wikis/marine-engineering/wiki/standards/` or any other wiki's `wiki/standards/` subtree. Newly-added test files under `tests/knowledge/` are explicitly allowed. Modified (not added) files are not counted. | pytest (subprocess to `git diff --name-only --diff-filter=A origin/main..HEAD`) | PASS post-Branch A; SKIPPED on Branch B | Branch A |
| T11 | `test_llm_wiki_lint_engineering_clean` | `uv run scripts/knowledge/llm_wiki.py lint --wiki engineering` exits 0 OR only with `warning`/`info` severity | subprocess from pytest | PASS post-Branch A; SKIPPED on Branch B | Branch A |
| T12 | `test_content_has_discriminating_technical_evidence` | OCIMF-Tandem page body (excluding frontmatter + provenance block) is > 200 words AND contains at least **2 of the following discriminating evidence categories**, each independently verifiable against the source ledger entry (not the title): (a) a specific OCIMF clause/section reference matching `\b[0-9]+(?:\.[0-9]+){1,3}\b`; (b) at least one explicit numeric engineering quantity with SI/imperial unit token matching `\b\d+(\.\d+)?\s*(kN\|t\|m\|ft\|deg\|°\|kts\|knots\|MT\|bar\|kPa\|MPa)\b`; (c) a named specific mooring/hawser/fender configuration or equipment identifier (e.g., `12-point spread`, `submarine hoses`, `Yokohama fender`, `quick-release hook`, `chafe chain`) matched by a curated regex list committed in the test fixture. Title-matching terms (`tandem`, `FPSO`, `offloading`, `conventional tanker`, `berthing`) are excluded. | pytest | PASS post-Branch A — guards against title regurgitation; SKIPPED on Branch B | Branch A |
| T13 | `test_ocimf_tandem_has_inbound_link` | At least one existing engineering-wiki page contains a markdown link `[[ocimf-tandem-mooring]]` OR `](standards/ocimf-tandem-mooring.md)` OR `](/knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md)`. Hardens the "no orphan promotion" requirement that lint does not enforce for `standards/`. | pytest (recursive grep under `knowledge/wikis/engineering/wiki/`) | PASS post-Branch A; SKIPPED on Branch B | Branch A |

**TDD discipline:** Tests T1, T-Bneg, and the skip decorators on T3–T13 will be written first on the feature branch before any wiki writes. Implementation will proceed only to make T3–T13 pass under Branch A.

**Note on Gemini r3 F4 (T12 vocabulary contradicts grounding):** the v4 T12 list uses categories that the OCIMF Tandem source document (a guideline on tandem-mooring engineering practice) is independently expected to contain — clause references, engineering quantities with units, and equipment identifiers are intrinsic to the document type, not external vocabulary imposed on it. The contradiction Gemini flagged would arise only if the curated list named arbitrary terms unrelated to the source; the v4 list is structurally aligned with the source domain. If implementation finds the source artifact still cannot satisfy 2-of-3 even after preview extraction lands, that is a stronger signal of insufficient summary content (the underlying #2245 problem) than a test design flaw, and the right response is to defer landing rather than weaken the test.

---

## Acceptance Criteria

### Cross-branch
- [ ] Adversarial reviews from at least 2 providers captured for v4 (acknowledging Codex r3 was UNAVAILABLE due to codex-cli 0.124.0 stdin-hang #2479; if r4 also returns UNAVAILABLE, escalate via the cross-provider-review-payoff feedback path).
- [ ] `tests/knowledge/test_ocimf_tandem_promotion.py` committed with T1, T-Bneg, T3–T13 implemented and the `CONTENT_SUB_GATE_PASS`-aware skip decorators in place.
- [ ] Prereq matrix in this plan reflects actual `gh issue view` state at execution time (including #2471 plan-approval status).

### Branch A (CONTENT_SUB_GATE == PASS) — engineering wiki, Phase 1
- [ ] T1 passes (gate evaluation correctness).
- [ ] T-Bneg is SKIPPED (Branch A is active).
- [ ] T3–T11 all pass after implementation.
- [ ] T12 passes (discriminating-evidence content guard, not title regurgitation).
- [ ] T13 passes (at least one inbound link exists).
- [ ] `uv run scripts/knowledge/llm_wiki.py lint --wiki engineering` exits 0 or warning-only.
- [ ] Parent issue #2216 receives an implementation summary comment.
- [ ] No CSA pages created in this issue.
- [ ] Page frontmatter carries `code_id`/`publisher`/`revision` per `.claude/rules/calc-citation-contract.md`.

### Branch B (CONTENT_SUB_GATE == FAIL — current state)
- [ ] T1 passes (gate evaluation runs and reports FAIL correctly).
- [ ] T-Bneg passes (no wiki writes occurred).
- [ ] T3–T13 are SKIPPED (no permanently red tests committed — Gemini r3 F5 closed).
- [ ] Blocker comment posted on #2227 explaining the OCIMF preview-content gap with the specific previews quoted (Pseudocode B3).
- [ ] OCIMF preview-content follow-up issue opened via `gh issue create` (Pseudocode B1) with concrete title/body/labels.
- [ ] Phase 2 CSA promotion follow-up issue opened via `gh issue create` (Pseudocode B2) with concrete title/body/labels.
- [ ] No wiki files written.

### Phase-Split Acceptance (v4 new)
- [ ] #2227 retains a single deliverable (Phase 1 = OCIMF Tandem). CSA Phase 2 lives only in the follow-up issue.
- [ ] Issue #2227 closes when Phase 1 (Branch A) lands or, alternatively, when the OCIMF preview-content follow-up has propagated and a successor v5 plan executes Branch A in a follow-up #2227-Phase-1 issue (whichever the user chooses at execution time — both paths are consistent with the phase-split rule).

---

## Adversarial Review History

### v1 (2026-04-12, reviewed 2026-04-21)
- **Codex (2026-04-21):** MAJOR — internal contradiction between Scope Boundaries and Files-to-Change for CSA work; TDD contract missing; prereq matrix underspecified.
- **Gemini (2026-04-21):** APPROVE on scope.
- **Claude (2026-04-15):** needs-revision minor.
- **Governance action (2026-04-21 15:07 UTC):** Path C rollback `status:plan-approved` → `status:plan-review`.

### v2 (2026-04-21) — addressed Codex r1 MAJORs via branch-conditional design + concrete TDD list + pinned prereq matrix.

### v3 (2026-04-23) — addressed r2 Claude+Codex+Gemini findings:
- T2 path-anchored disambiguation (Claude r2 F2)
- Resource Intelligence text_preview correction (Claude r2 F1)
- T12 evidence-category rewrite (Claude r2 F5)
- T7 `N_MAX_ADDED_LINES = 10` binding (sustained from r1)
- T10 `--diff-filter=A` flag (sustained from r1)
- Gitignore line-number correction (Claude r2 F4)
- Pseudocode "load prereq matrix" operationalization (Claude r2 F8)
- #2471 codification-landed sub-check added (structural)
- Branch A unreachability framing (Claude r2 F7)
- T13 inbound-link assertion (Claude r2 F10)
- Engineering index `## Standards` section verification (Claude r2 F6)

### v4 (2026-04-24) — this revision addresses r3 findings + decouples CSA via formal phase split

**Phase split (Codex r1 sustained / handoff-prompt P1):**
1. **CSA work formally split off into Phase 2 follow-up issue.** v3 nested CSA as a sub-branch of #2227 with `MARINE_TAXONOMY_SUB_GATE`; v4 lifts the coupling. Phase 1 (this issue, OCIMF Tandem) gates ONLY on the OCIMF content sub-gate. CSA Phase 2 opens as a separate issue with its own `gh issue create` body wired in Pseudocode B2. The #2471 sanction now plan-approved at `cb1c4a972` removes the taxonomy-decision blocker that originally motivated nesting.

**Gemini r3 findings addressed:**
2. **F1 (missing source files at HEAD) — Acknowledged as documented Gemini sandbox-overlay-blindness defect, not a real defect.** Per `feedback_gemini_sandbox_overlay_blindness.md` (2026-04-23): Gemini cross-review sandbox cannot see the sparse-checkout overlay, generating ~54 false-positive file-missing claims across that batch. v4 Resource Intelligence Summary now adds an inline reviewer note pointing at the verified `git ls-files` evidence so future r-pass reviewers do not re-raise the false positive. No structural change.
3. **F2 (T10 needs `--diff-filter=A`) — already FIXED in v3**, preserved in v4.
4. **F3 (T7 undefined N) — already FIXED in v3** (`N_MAX_ADDED_LINES = 10`), preserved in v4.
5. **F4 (T12 vocabulary contradicts grounding) — addressed via category-structural alignment with source domain.** v4 adds an explicit note (under TDD §) that the evidence categories are intrinsic to the OCIMF Tandem source document type (clause references, engineering units, equipment IDs are universal in OCIMF guidelines), not externally imposed vocabulary. If 2-of-3 still fails after preview extraction, the right action is to defer rather than weaken the test.
6. **F5 (Branch B guarantees broken test suite) — FIXED via branch-aware skip.** v4 TDD section adds the `CONTENT_SUB_GATE_PASS` env-var-driven `pytest.mark.skipif` decorator pattern. Under Branch B execution T3–T13 are SKIPPED (not failed); T1 and T-Bneg pass. CI does not ship red tests.
7. **F6 (Branch B follow-up issues lack execution commands) — FIXED via Pseudocode B1, B2, B3.** v4 pseudocode now contains literal `gh issue create` invocations with full body via `cat <<'EOF'` heredoc and explicit labels, plus a `gh issue comment` for the blocker post.

**Codex r3 (UNAVAILABLE):**
8. Codex r3 returned UNAVAILABLE due to codex-cli 0.124.0 stdin-hang regression (#2479). v4 attempts r4 cross-provider review against the codex-cli 0.123.0 downgrade workaround per `feedback_codex_cli_0_124_upstream_regression.md`. If r4 codex still UNAVAILABLE, v4 will be advanced on the strength of Claude r2 + Gemini r3 + this v4 self-audit, with the gap recorded in the disagreement bucket.

**Forward-adopted contracts (v4 new):**
9. **`code_id`/`publisher`/`revision` frontmatter mandated on the OCIMF Tandem page** even though Phase 1 lands before #2471 codification merges. Rationale per `.claude/rules/calc-citation-contract.md`: forward-adopting these fields lets future calc modules emit `Citation` instances against this page without retroactive frontmatter migration. T4 enforces.

### v4 residual open questions (for v4 reviewers)
- Should #2227 close when Branch A lands, or close when Phase 1 itself ships from a successor issue (after OCIMF preview extraction unblocks)? Currently both options are listed in §Phase-Split Acceptance — user decision at execution time.
- If Codex r4 also returns UNAVAILABLE, do we proceed with single-provider-strong (Claude+Gemini) approval, or wait for codex-cli 0.123.0 downgrade rollout?

---

## Risks and Open Questions

- **Risk:** Even Phase 1 may have limited body content because the OCIMF summary artifact has `summary=""`. T12 will guard against near-empty promotion. If T12 cannot pass with extracted preview content, Phase 1 is also effectively blocked — revealing #2245 as a harder blocker than originally scoped.
- **Verified (not a risk):** engineering wiki `index.md` has a `## Standards (7 pages)` section at line 99; Branch A inserts a row and bumps the count to 8.
- **Risk (mitigated by T13):** `llm_wiki.py lint` orphan/link checks skip `standards/` — a tandem page with no inbound link would not trip lint. T13 enforces explicit inbound-link presence.
- **Risk:** Codex review channel is currently unstable (codex-cli 0.124.0 #2479). v4 will rely on Claude + Gemini for r4. If Codex remains down through v4 cycle, escalate per `feedback_codex_sustained_MAJOR_loop.md` and `feedback_cross_provider_review_payoff.md`.
- **Open:** If Phase 1 OCIMF preview content lands but T12 cannot reach 2-of-3 evidence categories, the user decision is land-as-stub-with-status-tag vs block-and-defer. v4 default: block-and-defer (stubs violate the grounding contract).

---

## Complexity: T2

**T2** — multi-file wiki/documentation promotion with bounded evidence-driven content creation, index/log updates in a single wiki domain (engineering, Phase 1 only), new test file with branch-aware skip logic, strict scope control against adjacent breadth, and explicit `gh issue create` instrumentation for the Branch B follow-up path. Phase split removes prior structural complexity rather than adding it.
