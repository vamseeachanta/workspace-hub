# Plan for #2227: Promote OCIMF Tandem Mooring and CSA Z276 Coverage into LLM-Wikis

> **Status:** draft (v5 — locks #2227 closure path to a single revision-bound criterion per `feedback_issue_2460_approval_binding.md`; rewires Pseudocode B1/B2/B3 to capture URLs and fail-fast; addresses r4 Claude MAJOR + r4 Gemini APPROVE-with-suggestions)
> **Complexity:** T2
> **Date:** 2026-04-12 (v1) / 2026-04-21 (v2) / 2026-04-23 (v3) / 2026-04-24 (v4) / 2026-04-25 (v5)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2227
> **Parent:** https://github.com/vamseeachanta/workspace-hub/issues/2216
> **Review artifacts:** `scripts/review/results/2026-04-21-plan-2227-codex.md` (MAJOR, r1) | `scripts/review/results/2026-04-21-plan-2227-gemini.md` (APPROVE, r1) | `scripts/review/results/2026-04-23-plan-2227-claude.md` (MAJOR, r2) | `scripts/review/results/2026-04-23-plan-2227-codex.md` (UNAVAILABLE, r3 — codex-cli 0.124.0 stdin-hang #2479) | `scripts/review/results/2026-04-23-plan-2227-gemini.md` (MAJOR, r3) | `scripts/review/results/20260425T034020Z-plan-2227-v4.md-plan-claude.md` (MAJOR, r4) | `scripts/review/results/20260425T034236Z-plan-2227-v4.md-plan-gemini.md` (APPROVE, r4) | `scripts/review/results/2026-04-23-plan-2227-disagreement.md`

---

## Resource Intelligence Summary

### Existing repo code
- Found: `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` — existing OCIMF MEG4 page, git-tracked (confirmed via `git ls-files`).
- Found: `knowledge/wikis/engineering/wiki/standards/` — directory exists and is git-tracked, containing `api-579-ffs.md`, `dnv-os-e301.md`, `dnv-rp-c203.md`, `dnv-rp-c205.md`, `dnv-rp-f101.md`, `dnv-rp-f105.md`, `ocimf-meg4.md`. (Reviewer note: Gemini r3 Finding 1 reported these paths absent at HEAD — that is the documented sandbox-overlay-blindness defect; verified present via `git ls-files` from the main workspace.)
- Found: `knowledge/wikis/marine-engineering/wiki/` — directory is gitignored (`.gitignore:492 /knowledge/wikis/*`; only `!/knowledge/wikis/engineering/` at line 493 and `!/knowledge/wikis/cross-links.md` at line 494 are re-included). Subdirs present: `comparisons/`, `concepts/`, `entities/`, `sources/`, `visualizations/`. NO `standards/` directory, and marine-engineering `CLAUDE.md` schema (lines 6-23) does not list `standards/` as a sanctioned `wiki/` subcategory (literal `standards/` appears only at line 11 under `raw/`).
- Found: `scripts/knowledge/llm_wiki.py` — lint command at `cmd_lint` (line 683) validates frontmatter for `entities/concepts/sources/comparisons/standards/workflows` (line 632). Supports `standards/` in frontmatter check but orphan/link checks only traverse `entities/concepts/sources/comparisons` (line 748).
- Found: `data/document-index/summaries/sha256:5e5f...json`, `...:b576...json`, `...:3aa1...json` — summary artifacts EXIST for all three target doc_keys, with `summary: ""` across all three. `text_preview` is heterogeneous: OCIMF-TANDEM (`5e5f…`) preview length 0; CSA Z276.1-20 (`b576…`) and CSA Z276.18 (`3aa1…`) each carry a 1000-char corrupted-OCR preview (first 200 chars of `b576…`: `"pyorat\npakota\nmakaamaan\nlujana\njakcanut\ntiedocca\nperaan\ncannikka\n…"`; first 200 of `3aa1…`: `"monen\nkuunnella\ncannikka\ncamoin\npyctyvat\nvaatteitaan\n…"`). Downstream: OCIMF remediation will be "extract preview content"; CSA remediation will be "fix encoding/OCR corruption".
- User decision on #2471 (2026-04-23 issue comment): `wiki/standards/` sanctioned as a first-class page type. **#2471 v3 reached `status:plan-approved` at commit `cb1c4a972` on `plan/issue-2471-standards-wiki-path-sanction`** (forward-adopt status); the codification (schema CLAUDE.md amendments + per-wiki gitignore re-include + lint path) will land via that branch. v5 forward-adopts the sanction: CSA pages will land at `knowledge/wikis/marine-engineering/wiki/standards/csa-z276-1-20.md` and `…/csa-z276-18.md` once #2471 codification merges to main, and will carry `code_id`, `publisher`, `revision` frontmatter per the contract.

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
- `feedback_issue_2460_approval_binding.md` — approval markers must be revision-bound (SHA + review artifact paths + storage surface), not mutable file-path refs; v5 closure path is locked per this rule.
- Issue #2227 comment thread (2026-04-12 → 2026-04-23): #2244 triage routed broader CSA/API breadth to #2283/#2284/#2285/#2286/#2287; rollback 2026-04-21 15:07 moved label → `status:plan-review`.

### Gaps identified
- Reusable summaries for all three target doc_keys are unusable today; all three have `summary: ""`, and `text_preview` is either empty (OCIMF) or corrupted OCR (CSA x2).
- `knowledge/wikis/marine-engineering/` is gitignored — promoting CSA pages there will require the gitignore re-include landing via the #2471 codification.
- Marine-engineering `CLAUDE.md` schema does not yet list `wiki/standards/` as a sanctioned directory; the #2471 sanction is plan-approved but the codification has not yet merged.
- `llm_wiki.py lint` orphan/link checks do not traverse `standards/` — Phase 1 hardens this with explicit T13 inbound-link assertion.

<!-- Verification (v5): distinct sources consulted = 19+ (3 ledger entries + 3 summary JSON files + 3 gitignore lines + 2 wiki CLAUDE.md files + 5 prior plans + 1 handoff yaml + 7 review artifacts inc r3 triad + r4 pair + disagreement + 1 issue thread + 1 #2471 decision comment + calc-citation contract rule + #2460 approval-binding rule + lint source). -->

---

## Phase Split (locked in v4, preserved in v5)

**The CSA Z276 coverage is formally separated from the OCIMF Tandem coverage as Phase 2.** v3 nested CSA work as a sub-branch of #2227 with a `MARINE_TAXONOMY_SUB_GATE` guard; that coupled the OCIMF Tandem promotion to two unrelated remediations (CSA OCR fix AND #2471 codification). v4 lifted that coupling and v5 preserves it.

| Phase | Scope | Branch (git) | Prereqs | Status |
|---|---|---|---|---|
| **Phase 1** | OCIMF Tandem Mooring page in engineering wiki + narrow `ocimf-meg4.md` update + index/log entries + tests | `feat/issue-2227-ocimf-tandem-engineering-wiki` | OCIMF preview content (#2245 follow-up) only | Drives this issue's deliverable when content sub-gate clears |
| **Phase 2** | CSA Z276.1-20 + CSA Z276.18 pages in marine-engineering wiki at `wiki/standards/`, with `code_id`/`publisher`/`revision` frontmatter | new branch in a follow-up issue (Phase 2 split-off) | (a) #2471 codification merged to main; (b) CSA OCR remediation; (c) per-code wiki routing decision | **Deferred from #2227**; opens as new GH issue tracked from #2227 |

#2227's deliverable is **Phase 1 only**. Phase 2 will open as a follow-up issue at execution time (see Pseudocode B2 and §Phase-Split Acceptance).

---

## Deliverable

**Branch-conditional deliverable for Phase 1.** Two execution branches, scoped to the OCIMF Tandem work in the engineering wiki:

- **Branch A (CONTENT-READY):** OCIMF Tandem Mooring page lands in `knowledge/wikis/engineering/wiki/standards/` (the git-tracked, schema-sanctioned location), plus a narrowly grounded update to `ocimf-meg4.md`, index/log row, and the test file.
- **Branch B (CONTENT-BLOCKED — current state):** No wiki pages will be written. Plan execution will produce (1) a blocker comment on #2227 citing the specific OCIMF preview-content gap, (2) a follow-up issue for OCIMF preview-content extraction, and (3) a follow-up issue for the Phase 2 CSA work (Phase split). #2227 stays in `status:in-progress` (not `closed`) until OCIMF Branch A lands in a successor #2227-Phase-1 execution.

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
- Open the **OCIMF preview-content** follow-up issue via concrete `gh issue create` invocation with URL capture (see Pseudocode B1).
- Open the **Phase 2 CSA** follow-up issue via concrete `gh issue create` invocation with URL capture (see Pseudocode B2). Body links to #2471 codification branch and the two CSA OCR-remediation tasks.
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

**Classification rule (preserved from v4):** Phase 1 (OCIMF Tandem, engineering wiki) needs ONLY the content sub-gate. Today the content sub-gate fails for OCIMF (preview length 0) → Phase 1 will execute as Branch B (open follow-ups, no wiki writes). Phase 2 (CSA, marine wiki) is a separate issue and is not gated on by #2227's closure path.

---

## Pseudocode

```bash
# ---------- Entry gate ----------
load handoff_yaml = yaml.load("docs/reports/acma-wiki-unblock-2245-handoff.yaml")
load summary_5e5f = json.load("data/document-index/summaries/sha256:5e5f...json")

# Defensive assertion (Claude r4 P3 — KeyError vs documented FAIL ambiguity).
# `ready_for_2227` MUST exist in handoff_yaml. If absent, fail loud — do not coerce to FAIL silently.
assert "ready_for_2227" in handoff_yaml, \
    f"FATAL: handoff_yaml missing ready_for_2227 key — cannot evaluate CONTENT_SUB_GATE; " \
    f"fix docs/reports/acma-wiki-unblock-2245-handoff.yaml schema before re-running"
assert "summary" in summary_5e5f and "text_preview" in summary_5e5f, \
    "FATAL: summary_5e5f missing summary or text_preview keys — cannot evaluate CONTENT_SUB_GATE"

# Phase 1 content sub-gate hinges on OCIMF only (CSA decoupled to Phase 2).
if handoff_yaml["ready_for_2227"] is False \
   OR summary_5e5f["summary"] == "" \
   OR len(summary_5e5f["text_preview"]) == 0:
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
        # Forward-adopted from #2471 contract (calc-citation-contract.md).
        # T4 asserts presence + non-emptiness, NOT exact field names — accommodates
        # potential field-rename in #2471 codification (Claude r4 P2).
        code_id: OCIMF-TANDEM-MOORING
        publisher: OCIMF
        revision: <from-ledger>
        cross_links: [ocimf-meg4]
    body: scope, provenance back-links (doc_key, source_ref, promoted_from=2227)
          content grounded strictly in OCIMF-TANDEM-MOORING ledger entry + summary artifact

modify knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md:
    preserve all existing content
    add "## Related Standards" section with bounded tandem-mooring cross-reference
    enforce ≤ 10 added lines (T7 ceiling); every non-blank, non-heading added line
    within the section MUST contain `OCIMF-TANDEM-MOORING` or `[[ocimf-tandem-mooring]]`

append knowledge/wikis/engineering/wiki/log.md:
    one entry: "## [YYYY-MM-DD] ingest | OCIMF-TANDEM-MOORING promotion (#2227)"

modify knowledge/wikis/engineering/wiki/index.md:
    add row under "## Standards (7 pages)" for ocimf-tandem-mooring (will become 8 pages — bump heading count)

# ---------- Branch B (CONTENT_SUB_GATE == FAIL) ----------
# Pre-flight smoke (Claude r4 P3 suggestion — guards against codex-cli-style CLI regressions):
gh auth status >/dev/null || { echo "FATAL: gh not authenticated"; exit 2; }
gh issue create --help >/dev/null || { echo "FATAL: gh issue create unavailable"; exit 2; }

# Idempotency pre-checks (Claude r4 P2 — protect against retry loops + isolated-clone-dispatch races):
B1_TITLE="OCIMF-TANDEM-MOORING preview content extraction (unblocks #2227 Phase 1)"
B2_TITLE="Phase 2: Promote CSA Z276.1-20 + Z276.18 into marine-engineering wiki/standards/"

B1_existing=$(gh issue list --state open --search "\"${B1_TITLE}\" in:title" --json number,url -q '.[0].url // ""')
B2_existing=$(gh issue list --state open --search "\"${B2_TITLE}\" in:title" --json number,url -q '.[0].url // ""')

# B1: OCIMF preview-content remediation follow-up (capture URL via --json url -q .url)
if [ -n "$B1_existing" ]; then
    B1_url="$B1_existing"
    echo "B1 already exists, reusing: $B1_url"
else
    B1_url=$(gh issue create \
      --title "$B1_TITLE" \
      --body "$(cat <<'EOF'
Source: data/document-index/summaries/sha256:5e5f61e785295f0ac849399bb302cb5192ca84c108e6a57e82b8cc83b8b431af.json
Current state: text_preview length 0; summary is empty string.
Action: extract preview content via alt toolchain (ocrmypdf or manual review on a machine that can read the source).
Acceptance: summary artifact updated with non-empty `summary` and `text_preview` >= 200 chars; #2227 unblocked for Phase 1 Branch A.
EOF
)" \
      --label "type:remediation,parent:2216,blocks:2227" \
      --json url -q .url) || { echo "FATAL: B1 gh issue create failed"; exit 3; }
fi

# B2: Phase 2 CSA follow-up (capture URL; abort B3 if either B1 or B2 failed above)
if [ -n "$B2_existing" ]; then
    B2_url="$B2_existing"
    echo "B2 already exists, reusing: $B2_url"
else
    B2_url=$(gh issue create \
      --title "$B2_TITLE" \
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

This issue does NOT block #2227 closure — see #2227 v5 plan §Phase-Split Acceptance for the locked closure path.
EOF
)" \
      --label "type:wiki-promotion,parent:2216,split-from:2227" \
      --json url -q .url) || { echo "FATAL: B2 gh issue create failed"; exit 3; }
fi

# Atomicity check: only run B3 if both URLs are populated (idempotency-safe even on retry).
[ -n "$B1_url" ] && [ -n "$B2_url" ] || { echo "FATAL: missing B1_url or B2_url; aborting B3"; exit 4; }

# B3: blocker comment on #2227 — references captured URLs from B1/B2.
# Also marks the OCIMF preview-content follow-up ($B1_url) as the explicit "unblocks #2227" link
# that the locked closure path (§Phase-Split Acceptance) refers to.
gh issue comment 2227 --body "Phase 1 content sub-gate FAIL on $(date -I): OCIMF text_preview length 0. \
CSA work decoupled to Phase 2 follow-up. \
OCIMF preview-content remediation (this is the explicit \"unblocks #2227\" follow-up): ${B1_url}. \
Phase 2 CSA follow-up (does NOT block #2227 closure): ${B2_url}. \
#2227 remains status:in-progress until a successor execution lands Branch A."

# ---------- Verification ----------
run uv run scripts/knowledge/llm_wiki.py lint --wiki engineering
assert exit 0 OR only warnings (no errors)
run TDD tests with branch-aware skip:
  CONTENT_SUB_GATE_PASS=<bool> uv run pytest tests/knowledge/test_ocimf_tandem_promotion.py -v
```

**Pseudocode notes:**
- B1/B2 use `--json url -q .url` to capture the created issue URL into shell variables (Claude r4 P1 fix — v4 had bare `gh issue create` invocations that never bound `${B1_url}`/`${B2_url}`).
- The `if [ -n "$B*_existing" ]` guards short-circuit duplicate creation when retry loops or parallel-session races re-enter Branch B (Claude r4 P2 fix per `feedback_isolated_clone_dispatch_race.md`).
- B3 runs only after both B1 and B2 succeed (atomic gate via the `[ -n "$B1_url" ] && [ -n "$B2_url" ]` check). If B1 or B2 fails (transient gh API error, auth lapse, etc.), the wrapper exits with non-zero status and the operator manually reconciles before re-running — there is no half-posted state because B3 is the only step that touches #2227's comment thread.
- Pre-flight `gh auth status` + `gh issue create --help` smoke checks catch CLI regressions (per `feedback_codex_cli_0_124_upstream_regression.md` precedent) before any state-changing call.

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
| (gh CLI) | new GH issue: OCIMF preview-content remediation (idempotent on retry) | Pseudocode B1 |
| (gh CLI) | new GH issue: Phase 2 CSA promotion (idempotent on retry) | Pseudocode B2 |
| (gh CLI) | comment on #2227 with both captured URLs | Pseudocode B3 |

### CSA pages — never in #2227's file list
Phase 2 owns CSA file changes in a separate branch under a separate issue. No CSA file changes will land in any branch of #2227.

---

## TDD Test List

All tests will live at `tests/knowledge/test_ocimf_tandem_promotion.py` (new file) and will run via `uv run pytest tests/knowledge/test_ocimf_tandem_promotion.py -v`. Repo-integrated lint runs via `uv run scripts/knowledge/llm_wiki.py lint --wiki engineering`.

**T1 always-PASS contract (rewritten in v5 per Claude r4 P2):** T1 verifies that the `CONTENT_SUB_GATE` evaluation logic correctly applies the documented rule (handoff `ready_for_2227` AND OCIMF summary non-empty AND OCIMF preview non-empty) to the current artifacts. **T1 PASSES whenever the gate logic is implemented correctly, irrespective of the resulting boolean** — under Branch B execution T1 still passes because the test asserts evaluation correctness, not gate outcome. Tests T3–T13 use branch-aware skip via `@pytest.mark.skipif(not CONTENT_SUB_GATE_PASS, reason="Branch B — wiki writes deliberately deferred")`. T-Bneg runs unconditionally and asserts no wiki writes occurred under Branch B.

**`CONTENT_SUB_GATE_PASS` resolution (Claude r4 P3):** the test module reads the runtime value from environment variable `CONTENT_SUB_GATE_PASS` (set by the execution wrapper from the entry-gate result). If unset, the module falls back to evaluating the gate directly from the artifacts at `docs/reports/acma-wiki-unblock-2245-handoff.yaml` and `data/document-index/summaries/sha256:5e5f….json`. **In CI environments where these artifacts may be absent (shallow clones, sparse checkouts):** the fallback raises `pytest.skip("CONTENT_SUB_GATE artifacts unavailable — set CONTENT_SUB_GATE_PASS env var explicitly")` for the entire module rather than silently treating absence as PASS or FAIL. The execution wrapper is responsible for setting the env var explicitly in CI; the fallback is for local-developer convenience only.

| Test ID | Test name | What it verifies | Runner | Expected outcome | Gates which branch |
|---|---|---|---|---|---|
| T1 | `test_prereq_content_sub_gate_evaluation` | Reads `acma-wiki-unblock-2245-handoff.yaml` and `summaries/sha256:5e5f….json`; asserts that the gate-evaluation function correctly returns FAIL when any of the three conditions hold (`ready_for_2227` False OR summary empty OR text_preview empty) and PASS otherwise. The test exercises evaluation logic with both real artifacts AND synthetic fixtures, and PASSES whenever the evaluation function is correct, regardless of the live artifact's actual outcome. | pytest | always PASS (validates the gate code, not the data) | entry gate (always run) |
| T-Bneg | `test_branch_b_no_wiki_writes_when_gate_fails` | If `CONTENT_SUB_GATE` evaluates FAIL, asserts that `git diff --name-only --diff-filter=A $(git merge-base origin/main HEAD)..HEAD -- knowledge/wikis/engineering/wiki/standards/` is empty (merge-base pinned per Claude r4 P3). | pytest | PASS under Branch B; skipped under Branch A | Branch B safety net |
| T3 | `test_ocimf_tandem_page_exists` | `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` exists | pytest | PASS post-Branch A; SKIPPED on Branch B | Branch A |
| T4 | `test_ocimf_tandem_frontmatter_valid` | Page has `title`, `tags`, `added`, `last_updated`, `sources`, `domain=marine` AND **the v5-required forward-adopted #2471 contract fields are present and non-empty**. v5 asserts presence-and-non-emptiness rather than exact-field-name match: the test enumerates `["code_id", "publisher", "revision"]` as the v5 expected names BUT also accepts a documented rename map (e.g., `"revision" -> "code_revision"`) loaded from `tests/knowledge/_fixtures/citation_field_aliases.yaml`. If #2471 codification merges with a renamed field, the alias map is updated in a follow-up PR (≤ 5 lines) and existing pages need no migration. | pytest | PASS post-Branch A; SKIPPED on Branch B | Branch A |
| T5 | `test_ocimf_tandem_provenance_fields` | Page body contains `doc_key: sha256:5e5f...`, `source_ref` pointing to ledger entry, and `promoted_from: 2227` | pytest | PASS post-Branch A; SKIPPED on Branch B | Branch A |
| T6 | `test_ocimf_tandem_cross_reference_to_meg4` | Page contains a `[[ocimf-meg4]]` or equivalent markdown link back to the MEG4 page | pytest | PASS post-Branch A; SKIPPED on Branch B | Branch A |
| T7 | `test_ocimf_meg4_scope_narrow` | Diff of `ocimf-meg4.md` vs `$(git merge-base origin/main HEAD)` (pinned per Claude r4 P3) has ≤ **10 lines added** (`N_MAX_ADDED_LINES = 10`), **0 lines removed**, AND every added line either (a) is the literal section header `## Related Standards` (allowed at most once), or (b) contains the literal string `OCIMF-TANDEM-MOORING` or `[[ocimf-tandem-mooring]]`. (v5 tightening per Claude r4 P3: blank lines, sub-bullets, or commentary inside the section all must reference the tandem target — no permissive "sits within the section" allowance.) | pytest (parses `git diff --unified=0 $(git merge-base origin/main HEAD) -- knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md`) | PASS post-Branch A; SKIPPED on Branch B | Branch A |
| T8 | `test_engineering_index_has_tandem_row` | `knowledge/wikis/engineering/wiki/index.md` contains a row with `ocimf-tandem-mooring.md` under Standards section AND the heading count was bumped from 7 to 8 | pytest (regex match in Standards table) | PASS post-Branch A; SKIPPED on Branch B | Branch A |
| T9 | `test_engineering_log_has_promotion_entry` | `knowledge/wikis/engineering/wiki/log.md` contains a `## [YYYY-MM-DD] ingest | OCIMF-TANDEM-MOORING promotion (#2227)` entry | pytest | PASS post-Branch A; SKIPPED on Branch B | Branch A |
| T10 | `test_no_out_of_scope_pages` | Among **newly-ADDED files only** (use `git diff --name-only --diff-filter=A $(git merge-base origin/main HEAD)..HEAD` — merge-base pinned per Claude r4 P3), there is exactly one under `knowledge/wikis/engineering/wiki/standards/` (namely `ocimf-tandem-mooring.md`) and zero anywhere under `knowledge/wikis/marine-engineering/wiki/standards/` or any other wiki's `wiki/standards/` subtree. Newly-added test files under `tests/knowledge/` are explicitly allowed. Modified (not added) files are not counted. | pytest (subprocess to `git diff --name-only --diff-filter=A`) | PASS post-Branch A; SKIPPED on Branch B | Branch A |
| T11 | `test_llm_wiki_lint_engineering_clean` | `uv run scripts/knowledge/llm_wiki.py lint --wiki engineering` exits 0 OR only with `warning`/`info` severity | subprocess from pytest | PASS post-Branch A; SKIPPED on Branch B | Branch A |
| T12 | `test_content_has_discriminating_technical_evidence` | OCIMF-Tandem page body (excluding frontmatter + provenance block) is > 200 words AND contains at least **2 of the following discriminating evidence categories**, each independently verifiable against the source ledger entry (not the title): (a) a specific OCIMF clause/section reference matching `\b[0-9]+(?:\.[0-9]+){1,3}\b`; (b) at least one explicit numeric engineering quantity with SI/imperial unit token matching `\b\d+(\.\d+)?\s*(kN\|t\|m\|ft\|deg\|°\|kts\|knots\|MT\|bar\|kPa\|MPa)\b`; (c) a named specific mooring/hawser/fender configuration or equipment identifier (e.g., `12-point spread`, `submarine hoses`, `Yokohama fender`, `quick-release hook`, `chafe chain`) matched by a curated regex list committed in the test fixture. Title-matching terms (`tandem`, `FPSO`, `offloading`, `conventional tanker`, `berthing`) are excluded. | pytest | PASS post-Branch A — guards against title regurgitation; SKIPPED on Branch B | Branch A |
| T13 | `test_ocimf_tandem_has_inbound_link` | At least one existing engineering-wiki page contains a markdown link `[[ocimf-tandem-mooring]]` OR `](standards/ocimf-tandem-mooring.md)` OR `](/knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md)`. Hardens the "no orphan promotion" requirement that lint does not enforce for `standards/`. | pytest (recursive grep under `knowledge/wikis/engineering/wiki/`) | PASS post-Branch A; SKIPPED on Branch B | Branch A |

**TDD discipline:** Tests T1, T-Bneg, and the skip decorators on T3–T13 will be written first on the feature branch before any wiki writes. Implementation will proceed only to make T3–T13 pass under Branch A.

**Note on Gemini r3 F4 / Gemini r4 T12 suggestion (manual override path):** the v5 T12 list uses categories that the OCIMF Tandem source document is independently expected to contain — clause references, engineering quantities with units, and equipment identifiers are intrinsic to the document type. If implementation finds the source artifact still cannot satisfy 2-of-3 even after preview extraction lands, that is a stronger signal of insufficient summary content (the underlying #2245 problem) than a test design flaw. The v5 default response is **block-and-defer** (per the Risks section): land no page rather than weaken the test. There is no auto-override; any operator override must land via a documented v6 plan revision, not a runtime flag.

**T12 quantitative satisfiability threshold (Claude r4 question):** T12 is declared unsatisfiable when **all three** of the following hold against extracted preview content: (a) preview length < 600 chars (insufficient signal density), (b) zero clause references match the regex, AND (c) zero numeric quantities match the units regex. In that case the operator invokes block-and-defer; #2227 remains in `status:in-progress` and a comment cites the unsatisfiability. The 600-char threshold is a heuristic floor — below it, no statistically meaningful evidence-category coverage is achievable.

---

## Acceptance Criteria

### Cross-branch
- [ ] Adversarial reviews from at least 2 providers captured for v5. **Codex-r5 unavailability policy (locked in v5, deterministic per Claude r4 P3):** if Codex r5 returns UNAVAILABLE for any reason (codex-cli stdin-hang #2479, sandbox shell exec block, sustained-MAJOR loop, etc.), v5 advances on the strength of Claude r5 + Gemini r5 + this v5 self-audit, with the gap recorded in the disagreement bucket. No runtime decision is required at plan-approval time.
- [ ] `tests/knowledge/test_ocimf_tandem_promotion.py` committed with T1, T-Bneg, T3–T13 implemented and the `CONTENT_SUB_GATE_PASS`-aware skip decorators in place.
- [ ] Prereq matrix in this plan reflects actual `gh issue view` state at execution time (including #2471 plan-approval status).

### Branch A (CONTENT_SUB_GATE == PASS) — engineering wiki, Phase 1
- [ ] T1 passes (gate evaluation correctness — always-PASS by design).
- [ ] T-Bneg is SKIPPED (Branch A is active).
- [ ] T3–T11 all pass after implementation.
- [ ] T12 passes (discriminating-evidence content guard, not title regurgitation).
- [ ] T13 passes (at least one inbound link exists).
- [ ] `uv run scripts/knowledge/llm_wiki.py lint --wiki engineering` exits 0 or warning-only.
- [ ] Parent issue #2216 receives an implementation summary comment.
- [ ] No CSA pages created in this issue.
- [ ] Page frontmatter carries `code_id`/`publisher`/`revision` (or documented #2471 alias) per `.claude/rules/calc-citation-contract.md`.

### Branch B (CONTENT_SUB_GATE == FAIL — current state)
- [ ] T1 passes (gate evaluation correctness — always-PASS by design; PASS does NOT mean the live gate result is PASS).
- [ ] T-Bneg passes (no wiki writes occurred).
- [ ] T3–T13 are SKIPPED (no permanently red tests committed — Gemini r3 F5 closed).
- [ ] Pre-flight smoke (`gh auth status`, `gh issue create --help`) passes before any state-changing call.
- [ ] Idempotency pre-checks (`gh issue list --state open --search`) execute before B1 and B2; if a duplicate-titled open issue exists, its URL is reused instead of creating a new one.
- [ ] Blocker comment posted on #2227 explaining the OCIMF preview-content gap with the specific previews quoted AND containing both `${B1_url}` and `${B2_url}` substituted (Pseudocode B3).
- [ ] OCIMF preview-content follow-up issue opened (or reused) via `gh issue create … --json url -q .url` with URL captured into `B1_url`.
- [ ] Phase 2 CSA promotion follow-up issue opened (or reused) via `gh issue create … --json url -q .url` with URL captured into `B2_url`.
- [ ] No wiki files written.

### Phase-Split Acceptance (LOCKED in v5 — single closure path per `feedback_issue_2460_approval_binding.md`)

**Closure path commitment (Claude r4 P1, locked):** v5 commits to ONE closure path; the v4 disjunction ("user decision at execution time") is removed.

- [ ] #2227 retains a single deliverable (Phase 1 = OCIMF Tandem). CSA Phase 2 lives only in the follow-up issue.
- [ ] **#2227 closes IF AND ONLY IF Branch A lands on `origin/main` (i.e., commit containing `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` is merged to main).** If Branch B executes today (the current expected path), #2227 stays in `status:in-progress`. The OCIMF preview-content follow-up issue (B1) explicitly contains the string "unblocks #2227" in its body so the closure event remains tied to this issue, not to a successor issue.
- [ ] Closure binding is **revision-bound** per `feedback_issue_2460_approval_binding.md`:
  - **Plan SHA:** the commit on `plan/issue-2227-ocimf-tandem-csa-z276-wiki-promotion` containing this v5 plan file at path `docs/plans/2026-04-12-issue-2227-ocimf-tandem-csa-z276-wiki-promotion.md`.
  - **Review artifacts (per-provider verdicts):** `scripts/review/results/20260425T034020Z-plan-2227-v4.md-plan-claude.md` (MAJOR, r4 — addressed in v5) | `scripts/review/results/20260425T034236Z-plan-2227-v4.md-plan-gemini.md` (APPROVE, r4) | r5 cross-review artifacts to be appended at v5 review pass with paths matching the `scripts/review/results/<timestamp>-plan-2227-v5.md-plan-<provider>.md` glob.
  - **Approval-storage surface:** the `status:plan-approved` label on issue #2227, plus a comment on #2227 quoting the exact plan-file commit SHA + review-artifact paths at the moment of approval.
  - **Revision cleanup protocol:** if a v6 revision lands, the `status:plan-approved` label MUST be removed before v6 review begins; a stale-approved state must not persist silently.

**Why this single path is the right one:** locking closure to "Branch A lands on main" means the plan-approved commit fixes exactly what closes #2227. The alternative ("close on successor issue execution") would untie closure from this issue's revision, re-introducing exactly the file-path-only mutability hazard #2460 documented. The OCIMF follow-up (B1) carries the explicit "unblocks #2227" linkage so when the preview content is extracted and a successor wave executes Branch A, the close event still fires from this #2227 plan, not from a new issue's plan.

---

## Adversarial Review History

### v1 (2026-04-12, reviewed 2026-04-21)
- **Codex (2026-04-21):** MAJOR — internal contradiction between Scope Boundaries and Files-to-Change for CSA work; TDD contract missing; prereq matrix underspecified.
- **Gemini (2026-04-21):** APPROVE on scope.
- **Claude (2026-04-15):** needs-revision minor.
- **Governance action (2026-04-21 15:07 UTC):** Path C rollback `status:plan-approved` → `status:plan-review`.

### v2 (2026-04-21) — addressed Codex r1 MAJORs via branch-conditional design + concrete TDD list + pinned prereq matrix.

### v3 (2026-04-23) — addressed r2 Claude+Codex+Gemini findings (full list preserved in v4).

### v4 (2026-04-24) — formal phase split + Pseudocode B1/B2/B3 + branch-aware skip + forward-adopted #2471 frontmatter.

### v5 (2026-04-25) — addresses r4 Claude MAJOR + r4 Gemini APPROVE-with-suggestions

**Claude r4 P1 (MAJOR — closure path unbound at approval time):**
1. **Locked #2227 closure to a single revision-bound criterion.** v4 §Phase-Split Acceptance left closure as "user decision at execution time" (Branch A lands OR successor v5 plan executes Branch A in a follow-up issue). Per `feedback_issue_2460_approval_binding.md`, deferring to runtime choice means the plan-approved commit doesn't actually fix what closes #2227. v5 commits to: **#2227 closes IF AND ONLY IF Branch A lands on `origin/main`**; the OCIMF preview-content follow-up (B1) carries explicit "unblocks #2227" linkage so closure remains tied to this issue's revision. Approval marker now binds plan SHA + review artifact paths + storage surface + cleanup protocol — all four bindings per the rule.

**Claude r4 P1 (MAJOR — Pseudocode B3 placeholder URLs):**
2. **B1/B2 now capture URLs via `--json url -q .url` and B3 substitutes the captured `${B1_url}`/`${B2_url}` into the comment body.** v4 had bare `gh issue create` invocations that wrote URLs to stdout but never bound them to shell variables, so B3's `${B1_url}` would have substituted as empty. v5 also adds an atomicity gate: B3 only runs if both `B1_url` and `B2_url` are non-empty; if either B1 or B2 fails, the wrapper exits non-zero before any state-changing comment is posted to #2227. (No half-posted state.)

**Claude r4 P2 (idempotency for B1/B2 retry/parallel-session safety):**
3. **Added `gh issue list --state open --search "<title> in:title"` pre-checks before each `gh issue create`.** If an open follow-up with the same canonical title exists, B1/B2 reuse its URL instead of creating a duplicate. Protects against retry loops (per `feedback_retry_loop_reset_hazard.md`) and parallel-session dispatch (per `feedback_isolated_clone_dispatch_race.md`).

**Claude r4 P2 (#2471 frontmatter migration tolerance):**
4. **T4 now accepts a documented rename map** (`tests/knowledge/_fixtures/citation_field_aliases.yaml`) so the OCIMF Tandem page survives any field rename in #2471's final form. T4 asserts presence-and-non-emptiness, not exact-field-name match. Migration path: a 5-line PR to update the alias map is sufficient; no page-content migration is required.

**Claude r4 P2 (T1 always-PASS contract clarity):**
5. **Rewrote T1's TDD prose with one declarative sentence at the top of §TDD:** "T1 verifies that the `CONTENT_SUB_GATE` evaluation logic correctly applies the documented rule to the current artifacts; T1 PASSES whenever the logic is implemented correctly, irrespective of the resulting boolean." Removed the parenthetical "T1 fails as expected? — see T1 spec" from v4. Acceptance-criteria entries for T1 also clarify that PASS does not imply the live gate result is PASS.

**Claude r4 P3 (T7 tightening):**
6. **T7 (a)-clause tightened.** v4 allowed any blank line, sub-bullet, or commentary inside the new "## Related Standards" section to satisfy the diff guard. v5 requires every non-blank, non-heading added line within the section to contain the tandem-page reference; the section header itself is allowed at most once.

**Claude r4 P3 (merge-base pinning for T7 / T10 / T-Bneg):**
7. **Pinned all `git diff` operations to `$(git merge-base origin/main HEAD)`** instead of bare `origin/main..HEAD`. Insulates from worktree / auto-sync / merge-race hazards (per `feedback_merge_race_silent_revert.md` and `feedback_autosync_silent_pusher.md`).

**Claude r4 P3 (Codex-r5 UNAVAILABLE policy made deterministic):**
8. **Cross-branch acceptance criterion locks the policy in plan-text:** if Codex r5 returns UNAVAILABLE, v5 advances on Claude+Gemini+self-audit with the gap recorded in disagreement.md. No runtime decision required.

**Claude r4 P3 (defensive `KeyError` assertion in pseudocode):**
9. **Added explicit `assert "ready_for_2227" in handoff_yaml` and `assert "summary"/"text_preview" in summary_5e5f`** at the top of the entry gate. Missing keys now fail loud with a path to the schema-fix action; no silent KeyError or coercion to FAIL.

**Claude r4 P3 (pre-flight `gh` smoke):**
10. **Added `gh auth status` + `gh issue create --help` smoke checks** before any state-changing call in Branch B. Catches CLI regressions before they corrupt #2227's comment thread.

**Claude r4 P3 (CI artifact-availability fallback):**
11. **Documented `CONTENT_SUB_GATE_PASS` resolution behavior** for CI environments where the data artifacts may not be present (shallow clones, sparse checkouts). The fallback raises `pytest.skip(...)` for the whole module rather than silently treating absence as PASS or FAIL; the wrapper is responsible for setting the env var explicitly.

**Claude r4 question (T12 quantitative unsatisfiability threshold):**
12. **Added a concrete threshold to §TDD:** T12 is declared unsatisfiable when preview length < 600 chars AND zero clause-reference matches AND zero unit-quantity matches. Below that floor the operator invokes block-and-defer.

**Gemini r4 (APPROVE):**
13. Gemini r4 returned APPROVE with two suggestions: (a) define the trigger for closing #2227 — addressed by the locked closure path above; (b) consider a manual override path for T12 — explicitly declined per the block-and-defer default in §Risks; any override must land via a v6 plan revision, not a runtime flag.

**Forward-adopted contracts (preserved from v4):**
14. `code_id`/`publisher`/`revision` frontmatter mandated on the OCIMF Tandem page (or documented alias from #2471). T4 enforces.

### v5 residual open questions (for v5 reviewers)
- None at structural level. T12's quantitative threshold (600 chars) is a heuristic and may need calibration after the OCIMF preview content actually lands; the v5 plan documents this as a known calibration point rather than an open structural question.

---

## Risks and Open Questions

- **Risk:** Even Phase 1 may have limited body content because the OCIMF summary artifact has `summary=""`. T12 will guard against near-empty promotion. If T12 cannot pass with extracted preview content (per the 600-char/zero-match threshold), Phase 1 is also effectively blocked — revealing #2245 as a harder blocker than originally scoped.
- **Verified (not a risk):** engineering wiki `index.md` has a `## Standards (7 pages)` section at line 99; Branch A inserts a row and bumps the count to 8.
- **Risk (mitigated by T13):** `llm_wiki.py lint` orphan/link checks skip `standards/` — a tandem page with no inbound link would not trip lint. T13 enforces explicit inbound-link presence.
- **Risk:** Codex review channel is unstable (codex-cli 0.124.0 #2479). v5 cross-branch acceptance now deterministically advances on Claude+Gemini+self-audit if Codex r5 returns UNAVAILABLE — no runtime decision needed.
- **Risk (mitigated):** parallel-session dispatch race or retry-loop re-entry into Branch B could create duplicate follow-up issues. v5 idempotency pre-checks (`gh issue list --state open --search`) handle this.
- **Risk (mitigated):** transient `gh issue create` failure between B1 success and B2 attempt would have left v4 in a half-posted state. v5 atomicity gate aborts B3 if either B1 or B2 fails; the operator manually reconciles before re-running.
- **Open (calibration):** T12's 600-char threshold and the curated-equipment regex list are domain heuristics. They will be calibrated against the actual extracted OCIMF preview content; if mis-calibrated, the test fixture (`tests/knowledge/_fixtures/`) is updated in the v5 implementation pass without requiring a v6 plan revision (because the structural guard is the 2-of-3-categories rule, not the specific values).
- **Open (block-and-defer default):** If Phase 1 OCIMF preview content lands but T12 cannot reach 2-of-3 evidence categories, v5 default is **block-and-defer** (no land-as-stub-with-status-tag escape). Stubs violate the grounding contract; any override requires a v6 plan revision.

---

## Complexity: T2

**T2** — multi-file wiki/documentation promotion with bounded evidence-driven content creation, index/log updates in a single wiki domain (engineering, Phase 1 only), new test file with branch-aware skip logic, strict scope control against adjacent breadth, and explicit `gh issue create` instrumentation for the Branch B follow-up path with URL capture, idempotency guards, and atomicity gates. Closure path is revision-bound per `feedback_issue_2460_approval_binding.md`. v5 hardens the Branch B execution wrapper but does not expand scope beyond Phase 1 OCIMF Tandem.
