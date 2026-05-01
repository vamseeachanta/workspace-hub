# Plan for #2374: feat(knowledge): build transient-promotion candidate queue from handoffs and review artifacts

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-26
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2374
> **Review artifacts:** scripts/review/results/2026-04-29-plan-2374-claude.md | ...-codex.md | ...-gemini.md
> **Self-reference slug:** `2026-04-27-issue-2374-transient-promotion-candidate-queue`

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/knowledge/synthesize_archive.py`, `scripts/knowledge/capture-wrk-summary.sh`, `scripts/knowledge/categorize_uncategorized.py` — three upstream extractors that already operate over the WRK-archive/JSONL surface and emit structured records. The candidate-queue generator built here will reuse the same atomic-write + `flock` patterns and the `categorize_uncategorized.RULES` priority list when classifying candidate findings by category.
- Found: `scripts/knowledge/query-knowledge.sh` and `scripts/knowledge/build-knowledge-index.sh` — query-side surface that consumes `knowledge-base/*.jsonl`. The candidate ledger must live in a path that is either (a) already on the index, or (b) explicitly added so the queue is queryable from the same surface.
- Found: `scripts/knowledge/wiki-cross-links.py` and `scripts/knowledge/wiki_health_cron.py` — show that wiki-targeting helpers already exist and route by category. The `wiki_target_domain` field on each candidate will adopt the same coarse domain vocabulary (`engineering` / `marine` / `naval` / `process` / `personal` / `general`) used by these helpers, so the queue's routing column is not invented from scratch.
- Found: `scripts/cron/comprehensive-learning-nightly.sh`, `scripts/cron/harvest-workflow-tips.sh`, `scripts/cron/queue-refresh-weekly.sh` — recurring-run drivers that already produce weekly/nightly outputs in `docs/reports/`. These are the "recurring-run outputs" the issue body names as a third candidate source.
- Found: sibling wave-2 plan `docs/plans/2026-04-26-issue-2375-wrk-completions-normalize-seeds.md` — design for the normalized `knowledge/seeds/wrk-completions.yaml` seed and a derived `data/document-index/wrk-wiki-candidates.yaml` projection (path updated per the superseding #2375 plan at `docs/plans/2026-04-29-issue-2375-wrk-completions-normalize.md`; prior draft used `knowledge-base/wiki-candidates.yaml`). The wave-2 plan explicitly proposes a status vocabulary `{candidate, reviewed, promoted, rejected}` and a 0..3 scoring rubric (reusable methodology / durable category / evidence richness). **This wave-3 plan adopts that vocabulary and rubric verbatim** so the WRK-side and handoff-side queues remain merge-compatible.
- Gap: no script today scans `docs/handoffs/*.md` for promotion candidates. `grep -rl 'transient-promotion'` over the repo returns three hits (this issue's epic family + the wave-2 plan + a 2026-04-19 wiki-roadmap prompt), all prose; no extractor.
- Gap: no script today scans `scripts/review/results/*.md` for promotion candidates. The directory holds 1,107+ artifacts (1,111 entries minus a small WRK-prefixed input subset), so the extractor must be selective, not greedy.
- Gap: no script today scans `docs/reports/*.md` (150 files) for promotion candidates emitted by recurring runs. Those reports today are read by humans, never harvested.
- Gap: no `knowledge-base/promotion-candidates.yaml` ledger exists. `ls knowledge-base/` shows only `index.jsonl`, `wrk-completions.jsonl`, `wrk-completions.jsonl.lock` — confirming there is no candidate-queue artifact today.

### Standards
Not applicable. `cat:data-pipeline, cat:harness, domain:knowledge-management` — no engineering standards exercised, no calc constants emitted, so `.claude/rules/calc-citation-contract.md` does not apply. `.claude/rules/coding-style.md` (relative paths via `${REPO_ROOT}` or `git rev-parse --show-toplevel`, no hardcoded absolute paths) and `.claude/rules/patterns.md` (Level-2 script enforcement) do apply.

### LLM Wiki pages consulted
- No marine-engineering, naval-architecture, or maritime-law wiki page is consumed at queue-generation time. This queue *targets* wiki pages for a future promotion pass; it does not read them. The cross-link to existing wiki indexes happens later, at promotion time, governed by #2236 post-closure workflow.

### Documents consulted
- Issue #2374 body — defines candidate sources (handoffs, review artifacts, recurring-run outputs), required fields per candidate (source path, issue ref, finding summary, suggested durable target, status), and the explicit non-goal that this issue must NOT auto-promote.
- Parent issue #2205 (CLOSED, status:plan-approved) — operating model; transient artifacts (handoffs, session reports, review artifacts) are L2; durable targets (wiki, registries, follow-on issues) are L3/L4. This queue is the L2→L3 bridge.
- Issue #2209 (CLOSED) — durable-vs-transient boundary policy. Confirms handoffs and review artifacts are *transient*; promotion to durable requires explicit candidate selection. This queue is the operational substrate that policy assumes.
- Sibling issue #2375 (OPEN) — wave-2 partner. Sources from JSONL WRK corpus; emits `data/document-index/wrk-wiki-candidates.yaml` (path per the superseding #2375 plan; prior draft used `knowledge-base/wiki-candidates.yaml`). Wave-3 (this plan) sources from text-Markdown artifacts; emits `knowledge-base/promotion-candidates.yaml`. Both share `candidates[]` schema fields, status vocabulary, and scoring rubric shape (0..3 binary-increment) so a future merge into a unified ledger is structurally compatible with union-schema reconciliation. **Caveat:** the `DURABLE_CATEGORIES` sets are almost disjoint (#2374: 7 members including `ai-orchestration`, `ci`, `data-pipeline`, `automation`, `knowledge-management`, `documentation`; #2375: 4 members including `data`, `harness`, `standards`; overlap: only `engineering`). Scores are therefore not directly comparable across the two ledgers without re-scoring against a unified DURABLE_CATEGORIES set. Shape compatibility ≠ score comparability. **Note:** #2370 uses a structurally different 4-dimension × 0-5 weighted composite scoring system; any three-way ledger merge must normalize scores before comparison.
- Sibling issue #2370 (OPEN) — closed-issue promotion ledger for `cat:engineering*`. Same scoring philosophy (reusable methodology + stable decision value + evidence richness). This wave-3 ledger borrows the rubric.
- Issue #2236 (OPEN) — post-closure promotion workflow. The output of this queue is the *input* to that workflow. The queue does not implement promotion — it stages candidates for the workflow to act on.
- Issue #2238 (OPEN) — closed-issue citation guardrail. Each candidate must include enough provenance (source path + sha at extraction time + issue ref where present) for the guardrail to verify references downstream.
- Issue #2366 (OPEN) — strengthening scorecard. Queue size, candidate-status distribution, and time-to-promotion will be scorecard metrics.
- `docs/plans/2026-04-26-issue-2375-wrk-completions-normalize-seeds.md` — wave-2 plan; lines 219-269 define the wiki-candidate generator and its scoring rule. This plan reuses `score_candidate()` semantics (0..3 scale, reasons list) and `route_domain()` (`engineering` / `marine` / `naval` / `process` / `personal` / `general`). Note: `DURABLE_CATEGORIES` and the `route_domain` process-category set intentionally differ between #2374 and #2375 due to different source material — see Risks § "Coordination note (feed18 patch)" for details.
- `docs/plans/_template-issue-plan.md` — the canonical template; this plan follows its section order and the embedded retrieval contract.
- `.claude/skills/coordination/issue-planning-mode/SKILL.md` (v3.1.0) — the planning workflow skill. Confirms draft → adversarial review → `status:plan-review` → user approval gating; no self-approval per memory rule `feedback_never_offer_to_self_label_plan_approved.md`.
- Memory feedback `feedback_data_format_guidelines.md` — default to YAML for agent-facing structured data; JSON only for machine-consumed tool output. Candidate ledger is YAML.

### Gaps identified
- No handoffs extractor. Must build.
- No review-artifact extractor. Must build.
- No recurring-run report extractor. Must build.
- No `knowledge-base/promotion-candidates.yaml` ledger artifact. Must create.
- No reusable parser for "issue-reference + finding" extraction across heterogeneous Markdown bodies. Must build, with regex-and-heuristic strategy and a TDD fixture set drawn from the three source classes.
- No documented merge contract between this queue and the wave-2 `wrk-wiki-candidates.yaml` (at `data/document-index/wrk-wiki-candidates.yaml`). Must document in `knowledge/seeds/schema.md` (which the wave-2 plan already extends with a `type: wrk` variant).
- No append/update flow that keeps the ledger fresh as new handoffs and review artifacts land. Must build (cron-friendly entry point + idempotent re-extraction).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-27 via `gh issue view`):
- `#2374` — OPEN — feat(knowledge): build transient-promotion candidate queue from handoffs and review artifacts
- `#2205` — CLOSED, status:plan-approved — parent operating model
- `#2375` — OPEN — sibling: WRK normalize + wiki-candidate corpus
- `#2370` — OPEN — sibling: closed-issue promotion ledger
- `#2209` — CLOSED — durable-vs-transient boundary policy
- `#2236` — OPEN — post-closure promotion workflow (consumes this queue)
- `#2238` — OPEN — closed-issue citation guardrail
- `#2366` — OPEN — strengthening scorecard

**File existence** (`ls` 2026-04-27):
- EXISTS: `docs/handoffs/` — 82 files as of 2026-04-27 (counts grow daily; extractors use glob patterns, not hardcoded counts) (53 `*-handoff.md` style + 29 `session-*.md` style; verified by `ls docs/handoffs/ | wc -l`)
- EXISTS: `scripts/review/results/` — 1,111 entries as of 2026-04-27 (counts grow daily; extractor regex-filters to date-named subset) (`ls | wc -l`); date-named modern artifacts (`2026-04-25-plan-2487-*.md`, `2026-04-27-plan-2514-*.md`) coexist with timestamp-named legacy artifacts (`20260209T204919Z-*.md`)
- EXISTS: `docs/reports/` — 150 files as of 2026-04-27 (counts grow weekly; extractor uses bounded RECURRING_GLOBS) (`ls | wc -l`); recurring-run outputs include `compliance-weekly-YYYYMMDD.md`, `provider-autolabel-candidates.md`, `provider-utilization-weekly.md`, `2026-04-2X-provider-session-learning-transfer.md`
- EXISTS: `knowledge-base/index.jsonl`, `knowledge-base/wrk-completions.jsonl`, `knowledge-base/wrk-completions.jsonl.lock`
- EXISTS: `docs/plans/2026-04-26-issue-2375-wrk-completions-normalize-seeds.md` (wave-2 plan; cited above)
- EXISTS: `scripts/knowledge/synthesize_archive.py`, `scripts/knowledge/capture-wrk-summary.sh`, `scripts/knowledge/categorize_uncategorized.py`, `scripts/knowledge/wiki-cross-links.py`
- MISSING (new — this plan creates): `scripts/knowledge/build_promotion_candidates.py`
- MISSING (new — this plan creates): `scripts/knowledge/extract_handoff_findings.py`
- MISSING (new — this plan creates): `scripts/knowledge/extract_review_findings.py`
- MISSING (new — this plan creates): `scripts/knowledge/extract_recurring_findings.py`
- MISSING (new — this plan creates): `knowledge-base/promotion-candidates.yaml`
- MISSING (new — this plan creates): `docs/reports/promotion-candidates-extraction-report.md`
- MISSING (new — this plan creates): `scripts/knowledge/tests/test_extract_handoff_findings.py`
- MISSING (new — this plan creates): `scripts/knowledge/tests/test_extract_review_findings.py`
- MISSING (new — this plan creates): `scripts/knowledge/tests/test_extract_recurring_findings.py`
- MISSING (new — this plan creates): `scripts/knowledge/tests/test_build_promotion_candidates.py`

**Existing schema reuse evidence** (excerpt from wave-2 plan, lines 219-269):
The wave-2 plan defines `score_candidate(entry)` returning `(score, reasons)` with three increments — `has-patterns`, `durable-category`, `has-evidence` — and a status vocabulary `{candidate, reviewed, promoted, rejected}`. This plan adopts the same function signature, the same status set, and an analogous routing function. No re-invention.

**Handoff structure heterogeneity** (`grep -E '^#{1,3} ' docs/handoffs/session-2026-04-26-flywheel-cradle-to-grave-exit.md`):
```
# Session Handoff — Cradle-to-Grave Engineering Flywheel
## What Got Built
### Issues (aceengineer-strategy)
### Artifacts on `main`
### Memory entries written
## Locked Decisions (for future sessions)
## Open Items (blocking next-session work)
## Two Painful Pattern Discoveries (Useful for Next Session)
```
Compared with the older shape (`docs/handoffs/2026-04-22-plan-approval-ready-exit-handoff.md` — flat `## Session outcome / GitHub issue links / Latest convergence comments` headings) — confirms the extractor must tolerate heterogeneous heading shapes. Per-handoff bullet density: 41-64 list items in mature exit-handoffs vs. 16 in lighter session-summary handoffs.

**Review-artifact structure** (`grep -E '^#{1,3} ' scripts/review/results/2026-04-25-plan-2487-claude.md`):
```
# Plan Review: #2487 Inventory Readiness Spine — v6
## Verdict
## Findings
## Blocking findings
```
The "Findings" section is the candidate-rich surface. Modern review files are date-named (`2026-MM-DD-plan-NNNN-{claude,codex,gemini}.md`); the extractor must filter to that prefix to avoid swallowing the legacy `20260209T204919Z-*` cohort (which is WRK-era and out of scope for this queue).

**No prior implementation** (`grep -rl 'transient-promotion\|wiki-candidate\|promotion-candidate' docs/ scripts/ knowledge/ knowledge-base/ 2>/dev/null | grep -v '.git/'`):
```
docs/handoffs/2026-04-20-llm-wiki-strengthening-issue-discovery-exit-handoff.md
docs/plans/2026-04-19-claude-llm-wiki-roadmap-review-prompt.md
docs/plans/2026-04-26-issue-2375-wrk-completions-normalize-seeds.md
docs/reports/skill-promotion-audit.md
docs/plans/README.md
```
All five hits are prose. No script implementing a transient-promotion candidate queue exists today.

**Recurring-run outputs** (`ls docs/reports/ | grep -E 'weekly|nightly|cron|provider'`):
```
compliance-weekly-20260413.md
compliance-weekly-20260420.md
provider-autolabel-candidates.md
provider-routing-scorecard.md
provider-utilization-weekly.md
2026-04-22-provider-session-learning-transfer.md
2026-04-23-provider-session-learning-transfer.md
2026-04-24-provider-session-learning-transfer.md
```
These are the bounded recurring-run outputs the issue body refers to. The extractor will consume only this filtered subset, not the full 150-file `docs/reports/` directory, to keep noise down.

<!-- Source count: issue #2374 body + parent #2205 + boundary #2209 + sibling #2375 + sibling #2370 + #2236 + #2238 + #2366 + wave-2 plan + planning skill + memory feedback + repo file evidence = 12 distinct sources (≥3 required). -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-27-issue-2374-transient-promotion-candidate-queue.md` |
| Handoff extractor | `scripts/knowledge/extract_handoff_findings.py` |
| Review-artifact extractor | `scripts/knowledge/extract_review_findings.py` |
| Recurring-run extractor | `scripts/knowledge/extract_recurring_findings.py` |
| Queue builder (orchestrator) | `scripts/knowledge/build_promotion_candidates.py` |
| Promotion-candidate ledger (authoritative) | `knowledge-base/promotion-candidates.yaml` |
| Extraction report | `docs/reports/promotion-candidates-extraction-report.md` |
| Schema doc update | `knowledge/seeds/schema.md` |
| Tests — handoff extractor | `scripts/knowledge/tests/test_extract_handoff_findings.py` |
| Tests — review extractor | `scripts/knowledge/tests/test_extract_review_findings.py` |
| Tests — recurring extractor | `scripts/knowledge/tests/test_extract_recurring_findings.py` |
| Tests — queue builder | `scripts/knowledge/tests/test_build_promotion_candidates.py` |
| Plans index update | `docs/plans/README.md` |
| Plan review — Claude | `scripts/review/results/2026-04-29-plan-2374-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-29-plan-2374-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-29-plan-2374-gemini.md` |

---

## Deliverable

A `knowledge-base/promotion-candidates.yaml` ledger built by `scripts/knowledge/build_promotion_candidates.py` from three text-Markdown sources — `docs/handoffs/*.md`, the date-named modern subset of `scripts/review/results/*.md`, and a bounded subset of `docs/reports/*.md` (recurring-run outputs only) — where each candidate carries `source_path`, `source_kind`, `source_sha`, `issue_ref`, `finding_summary`, `wiki_target_domain`, `extend_or_create`, `score`, `reasons`, and `status` (default `candidate`); accompanied by an extraction report enumerating per-source counts, field-fill rates, and unrecoverable cases. No automatic promotion; the ledger is the input to #2236's post-closure workflow.

---

## Pseudocode

### `build_promotion_candidates.py` (orchestrator)
```
function main(args):
    repo = git_root()
    out_yaml   = repo / "knowledge-base/promotion-candidates.yaml"
    out_report = repo / "docs/reports/promotion-candidates-extraction-report.md"

    candidates = []
    stats = {"by_source_kind": Counter(), "fields_filled": Counter(),
             "unrecoverable": [], "scanned": 0, "kept": 0}

    candidates += extract_handoff_findings(repo / "docs/handoffs", stats)
    candidates += extract_review_findings(repo / "scripts/review/results", stats)
    candidates += extract_recurring_findings(repo / "docs/reports", stats)

    # Score and filter; drop score < 1 (pure noise)
    scored = []
    for c in candidates:
        c["score"], c["reasons"] = score_candidate(c)
        if c["score"] >= 1:
            c["wiki_target_domain"] = route_domain(c)
            c["extend_or_create"]   = "extend" if existing_wiki_page_for(c) else "create"
            c["status"]             = "candidate"
            scored.append(c)
            stats["kept"] += 1

    if not args.dry_run:
        atomic_write_yaml(out_yaml, {
            "schema_version": "1.0.0",
            "generated_at": utcnow_iso(),
            "candidates": sorted(scored, key=lambda c: (-c["score"], c["source_path"], c["issue_ref"] or "")),
        })
        write_extraction_report(out_report, stats)
```

### `extract_handoff_findings.py`
```
function extract_handoff_findings(handoffs_dir, stats):
    out = []
    for path in sorted(handoffs_dir.glob("*.md")):
        sha = git_blob_sha(path)
        body = read_text(path)
        sections = split_by_heading_atx(body)        # tolerate # / ## / ###; mixed shapes
        for heading, lines in sections:
            if not heading_is_finding_rich(heading): # see vocabulary table below
                continue
            for bullet in extract_bullets(lines):
                issue_refs = re.findall(r'#(\d+)\b', bullet)
                summary    = first_sentence(bullet, max_chars=240)
                if not summary:
                    stats["unrecoverable"].append({"path": str(path), "section": heading})
                    continue
                out.append({
                    "source_kind": "handoff",
                    "source_path": str(path.relative_to(repo_root())),
                    "source_sha":  sha,
                    "section":     heading,
                    "issue_ref":   issue_refs[0] if issue_refs else None,
                    "additional_refs": issue_refs[1:] or [],
                    "finding_summary": summary,
                    "patterns":  detect_patterns(bullet),  # regex hits: "lesson", "decision", "anti-pattern"
                    "evidence":  extract_quoted_paths_or_shas(bullet),  # used by score_candidate
                })
    stats["by_source_kind"]["handoff"] = len(out)
    return out

function heading_is_finding_rich(h):
    h_lc = h.lower()
    return any(kw in h_lc for kw in [
        "finding", "lesson", "decision", "discover", "open item",
        "key technical", "pattern", "outcome", "what was completed",
    ])
```

### `extract_review_findings.py`
```
function extract_review_findings(reviews_dir, stats):
    out = []
    # Filter to date-named modern artifacts only; skip legacy timestamp-prefixed files
    pattern = re.compile(r'^\d{4}-\d{2}-\d{2}-plan-\d+-(?:claude|codex|gemini|disagreement)\.md$')
    for path in sorted(reviews_dir.iterdir()):
        if not pattern.match(path.name):
            continue
        sha = git_blob_sha(path)
        body = read_text(path)
        # Extract the "Findings" section and any "HIGH"/"MAJOR"/"CRITICAL" subsections
        for heading, lines in split_by_heading_atx(body):
            if heading.lower().strip() not in ("findings", "blocking findings",
                                                "high", "critical", "major"):
                continue
            for bullet in extract_bullets(lines):
                issue_refs = re.findall(r'#(\d+)\b', bullet)
                out.append({
                    "source_kind": "review",
                    "source_path": str(path.relative_to(repo_root())),
                    "source_sha":  sha,
                    "section":     heading,
                    "issue_ref":   filename_issue_number(path.name),  # NNNN from -plan-NNNN-
                    "additional_refs": issue_refs,
                    "finding_summary": first_sentence(bullet, max_chars=240),
                    "patterns":  ["adversarial-finding"],
                    "severity":  classify_severity(heading),  # critical|high|major|minor|none
                    "evidence":  extract_quoted_paths_or_shas(bullet),
                })
    stats["by_source_kind"]["review"] = len(out)
    return out
```

### `extract_recurring_findings.py`
```
RECURRING_GLOBS = [
    "compliance-weekly-*.md",
    "provider-autolabel-candidates.md",
    "provider-routing-scorecard.md",
    "provider-utilization-weekly.md",
    "*-provider-session-learning-transfer.md",
]

function extract_recurring_findings(reports_dir, stats):
    out = []
    matched = set()
    for g in RECURRING_GLOBS:
        for path in reports_dir.glob(g):
            matched.add(path)
    for path in sorted(matched):
        sha = git_blob_sha(path)
        body = read_text(path)
        for heading, lines in split_by_heading_atx(body):
            if not heading.lower().startswith(("findings", "candidates", "actions",
                                                "recommendations")):
                continue
            for bullet in extract_bullets(lines):
                issue_refs = re.findall(r'#(\d+)\b', bullet)
                out.append({
                    "source_kind": "recurring-run",
                    "source_path": str(path.relative_to(repo_root())),
                    "source_sha":  sha,
                    "section":     heading,
                    "issue_ref":   issue_refs[0] if issue_refs else None,
                    "additional_refs": issue_refs[1:] or [],
                    "finding_summary": first_sentence(bullet, max_chars=240),
                    "patterns":  ["recurring-run"],
                    "evidence":  extract_quoted_paths_or_shas(bullet),
                })
    stats["by_source_kind"]["recurring-run"] = len(out)
    return out
```

### Shared scoring + routing (mirrors wave-2 plan)
```
DURABLE_CATEGORIES = {
    "engineering", "ai-orchestration", "ci", "data-pipeline",
    "automation", "knowledge-management", "documentation",
}

function score_candidate(c):
    score, reasons = 0, []
    if c.get("patterns"):                   # finding-rich heading or recurring-run/adversarial tag
        score += 1; reasons.append("has-patterns")
    if classify_category(c) in DURABLE_CATEGORIES:
        score += 1; reasons.append("durable-category")
    if c.get("evidence"):                   # paths/SHAs/issue refs cited inline
        score += 1; reasons.append("has-evidence")
    return score, reasons

function route_domain(c):
    cat = classify_category(c)
    if cat == "engineering":
        return route_engineering_subdomain(c)  # marine | naval | engineering | general
    if cat in ("ai-orchestration", "ci", "automation", "data-pipeline"):
        # NOTE: #2375 routes only (ai-orchestration, ci, automation) → process;
        # "data-pipeline" falls through to "general" in #2375.  This plan
        # intentionally includes "data-pipeline" → process because the handoff/
        # review-artifact source surface contains process-oriented data-pipeline
        # findings (e.g., solver-queue, batch-runner).  Any unified-ledger merge
        # must reconcile this routing divergence.
        return "process"
    if cat == "personal":
        return "personal"
    return "general"
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/knowledge/build_promotion_candidates.py` | Orchestrator: invokes the three extractors, scores + routes, atomically writes ledger + report |
| Create | `scripts/knowledge/extract_handoff_findings.py` | Heading-and-bullet extractor over `docs/handoffs/*.md` |
| Create | `scripts/knowledge/extract_review_findings.py` | Findings-section extractor over date-named `scripts/review/results/*.md` |
| Create | `scripts/knowledge/extract_recurring_findings.py` | Bounded glob extractor over recurring-run reports in `docs/reports/` |
| Create | `knowledge-base/promotion-candidates.yaml` | Authoritative ledger; durable, reviewable surface |
| Create | `docs/reports/promotion-candidates-extraction-report.md` | Per-source counts, field-fill rates, unrecoverable list |
| Create | `scripts/knowledge/tests/test_extract_handoff_findings.py` | TDD coverage for handoffs extractor |
| Create | `scripts/knowledge/tests/test_extract_review_findings.py` | TDD coverage for review extractor |
| Create | `scripts/knowledge/tests/test_extract_recurring_findings.py` | TDD coverage for recurring-run extractor |
| Create | `scripts/knowledge/tests/test_build_promotion_candidates.py` | TDD coverage for orchestrator and scoring |
| Modify | `knowledge/seeds/schema.md` | Document `promotion-candidates.yaml` schema and the merge contract with wave-2 `wrk-wiki-candidates.yaml` (at `data/document-index/wrk-wiki-candidates.yaml`) |
| Update | `docs/plans/README.md` | Add this plan to the index |

No engineering-package files (`digitalmodel/`, `assethold/`, `assetutilities/`, etc.) are touched. All work is hub-local under `scripts/knowledge/`, `knowledge-base/`, `knowledge/`, and `docs/`.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_handoff_extractor_picks_up_issue_refs_from_bullets | regex captures `#NNNN` from a bullet | bullet with "Closed `#2228` because…" | issue_ref == "2228" |
| test_handoff_extractor_handles_session_prefix_and_dated_prefix | both `2026-04-22-…-handoff.md` and `session-2026-04-26-…-exit.md` shapes load | mixed fixture dir | both file kinds yield candidates |
| test_handoff_extractor_skips_non_finding_sections | heading "GitHub issue links" yields nothing | handoff with that heading | zero candidates from that section |
| test_handoff_extractor_keeps_finding_rich_sections | headings "Lessons", "Open Items", "Key Technical Findings" are kept | fixture handoff | candidates emitted from each |
| test_handoff_extractor_records_source_sha | each candidate carries the blob sha at extraction time | any handoff | source_sha is a 40-char hex string |
| test_handoff_extractor_truncates_finding_summary | summary capped at 240 chars | bullet > 240 chars | summary length ≤ 240 + "…" sentinel |
| test_review_extractor_filters_to_date_named_artifacts | legacy `20260209T204919Z-*` files are skipped | mixed fixture dir | only `YYYY-MM-DD-plan-NNNN-{claude,codex,gemini,disagreement}.md` are scanned |
| test_review_extractor_extracts_issue_from_filename | issue number recovered from filename even when bullet lacks `#NNN` | `2026-04-25-plan-2487-claude.md` with bullet "missing context" | issue_ref == "2487" |
| test_review_extractor_classifies_severity | HIGH/CRITICAL/MAJOR sections get severity tag | review with HIGH heading | severity == "high" |
| test_review_extractor_handles_disagreement_files | `-disagreement.md` files are scanned identically | fixture | candidates emitted |
| test_recurring_extractor_globs_only_named_reports | files outside RECURRING_GLOBS are ignored | mixed `docs/reports/` fixture | only `compliance-weekly-*.md`, `provider-*` files are scanned |
| test_recurring_extractor_keeps_findings_or_actions_or_recommendations | sections matching the vocabulary are kept | recurring-run report fixture | candidates emitted from those sections |
| test_orchestrator_dedupes_by_source_path_plus_summary | identical (path, summary) pair appears once | duplicate fixture | one candidate, not two |
| test_orchestrator_drops_score_zero | candidate with score == 0 is excluded from output | low-signal fixture | not in ledger |
| test_orchestrator_default_status_candidate | every emitted candidate starts at status="candidate" | any input | status == "candidate" |
| test_orchestrator_status_vocabulary_documented_inline | YAML output documents the status set in a comment header | run | output begins with `# status: candidate|reviewed|promoted|rejected` comment |
| test_orchestrator_atomic_write_no_tmp_leftover | write goes through tempfile + os.replace | run on tmp paths | no `.tmp` files remain in target dir |
| test_orchestrator_idempotent_on_unchanged_inputs | byte-identical output on re-run when inputs unchanged | run twice | byte-equal YAML |
| test_orchestrator_sorted_by_score_then_path_then_issue | stable ordering | mixed fixture | candidates sorted by (-score, source_path, issue_ref) |
| test_orchestrator_dry_run_no_writes | --dry-run flag suppresses writes | --dry-run on tmp | no ledger or report file created |
| test_extraction_report_per_source_counts | report contains per-source-kind counts | run | report has rows for handoff/review/recurring-run |
| test_extraction_report_unrecoverable_section | unparseable bullet is recorded, not silently dropped | bad fixture | report Unrecoverable section names file + heading |
| test_route_domain_engineering_to_marine | engineering+riser routes to marine | candidate with riser pattern | wiki_target_domain == "marine" |
| test_route_domain_ci_to_process | ai-orchestration / ci routes to process | candidate with CI keyword | wiki_target_domain == "process" |
| test_score_full_three_dimensions | candidate with patterns + durable-category + evidence scores 3 | rich fixture | score == 3, all three reasons present |
| test_schema_round_trip | every emitted candidate has all required keys | run, then re-parse | required keys present on every candidate |
| test_schema_doc_documents_merge_contract | `knowledge/seeds/schema.md` mentions `wrk-wiki-candidates.yaml` (wave-2, at `data/document-index/`) and `promotion-candidates.yaml` (this plan) | static check | both files referenced |

---

## Acceptance Criteria

- [ ] `knowledge-base/promotion-candidates.yaml` exists and is valid YAML; every candidate carries `source_kind ∈ {handoff, review, recurring-run}`, `source_path`, `source_sha`, `issue_ref` (or `null`), `finding_summary` (≤ 240 chars), `wiki_target_domain`, `extend_or_create`, `score ∈ {1,2,3}`, `reasons` (non-empty list), and `status` defaulting to `candidate`.
- [ ] All three source classes are represented in the first generated ledger: at least one `handoff`-kind candidate from `docs/handoffs/*.md`, at least one `review`-kind candidate from a `2026-MM-DD-plan-NNNN-*.md` file, at least one `recurring-run`-kind candidate from a recurring report in `docs/reports/`.
- [ ] Legacy timestamp-prefixed review files (`20260209T204919Z-…`) are explicitly filtered out, verified by a test.
- [ ] `docs/reports/promotion-candidates-extraction-report.md` lists per-source-kind candidate counts, field-fill rates per field, an "Unrecoverable" section naming each (file, section) pair the extractor could not parse, and the recurring-glob list used.
- [ ] `knowledge/seeds/schema.md` documents the `promotion-candidates.yaml` schema and the merge contract with the wave-2 `wrk-wiki-candidates.yaml` (at `data/document-index/wrk-wiki-candidates.yaml`; shared `status` vocabulary `{candidate, reviewed, promoted, rejected}`, shared 0..3 binary-increment `score` rubric, shared `wiki_target_domain` vocabulary).
- [ ] No automatic promotion: the ledger is generation-only. There is no script in this issue that mutates wiki pages, opens follow-on issues, or changes candidate status from `candidate`. Verified by code review and by absence of any wiki-write or `gh issue` calls in the new scripts.
- [ ] All new tests pass: `uv run pytest scripts/knowledge/tests/test_extract_handoff_findings.py scripts/knowledge/tests/test_extract_review_findings.py scripts/knowledge/tests/test_extract_recurring_findings.py scripts/knowledge/tests/test_build_promotion_candidates.py -v`.
- [ ] No regression: `uv run pytest scripts/knowledge/tests/ -v` and `bash scripts/knowledge/tests/test-knowledge-scripts.sh` pass.
- [ ] Issue-body acceptance criterion 4 satisfied: this plan complements rather than replaces `#2236` (post-closure promotion workflow). The ledger is the *input* to that workflow; the README/plan text states this explicitly.
- [ ] Plan is positioned as a sibling, not a duplicate, of `#2375` (WRK normalize / wiki-candidates) and `#2370` (closed-issue ledger). Status vocabulary, scoring rubric, and routing vocabulary are shared and documented.
- [ ] Path-handling rule honored: every new script resolves the repo root via `git rev-parse --show-toplevel` (or `${REPO_ROOT}`); no hardcoded absolute paths. Enforced by `scripts/enforcement/check-no-abs-paths.sh` in CI.
- [ ] Review artifacts posted to `scripts/review/results/` (Claude + Codex + Gemini) before label move to `status:plan-review`. No self-approval.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (feed17) | MINOR | F1: DURABLE_CATEGORIES divergence vs #2375; F2: wrong script paths; F3: route_domain process-set divergence; F4-F7: cosmetic/stale |
| Codex | PENDING | (filled after review wave) |
| Gemini | PENDING | (filled after review wave) |

**Overall result:** PENDING (Claude MINOR addressed in feed18 patch; Codex/Gemini pending)

Revisions made based on review:
- **feed16 patch (2026-04-29):** patched 7 stale wiki-candidate path references (`knowledge-base/wiki-candidates.yaml` → `data/document-index/wrk-wiki-candidates.yaml`) per #2375 superseding plan. Added #2370 scoring-architecture difference note at line 35 and coordination note in Risks. See `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-patch-2374-feed16.md`.
- **feed18 patch (2026-04-29):** addressed all 3 MINOR findings (F1-F3) and all 4 LOW observations (F4-F7) from Claude feed17 adversarial review. See `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-patch-2374-feed18.md`.

---

## Risks and Open Questions

- **Risk — heading-shape heterogeneity in handoffs:** `docs/handoffs/` mixes flat (`## Session outcome`) and nested (`## What Got Built / ### Issues`) shapes; bullet density ranges from 16 to 64. A naive H2-only walker will under-extract from nested handoffs. Mitigation: walker accepts H1-H3, classifies each heading by keyword vocabulary (`finding`, `lesson`, `decision`, `discover`, `open item`, `pattern`, `outcome`, `what was completed`), records every unrecoverable section in the report so reviewers can extend the vocabulary.
- **Risk — review-results corpus is huge (1,111 entries) and historically heterogeneous:** the legacy `20260209T204919Z-*` cohort is WRK-era and structurally different from modern `2026-MM-DD-plan-NNNN-*` files. Greedy scanning would inflate noise. Mitigation: hard regex filter `^\d{4}-\d{2}-\d{2}-plan-\d+-(?:claude|codex|gemini|disagreement)\.md$` at extraction time; legacy cohort is explicitly out of scope and documented as such in the schema doc.
- **Risk — recurring-run subset drift:** new recurring-run reports may appear later (e.g., a future weekly cron). The extractor's `RECURRING_GLOBS` is a fixed list; it will silently miss new ones. Mitigation: add an extraction-report row "Reports in `docs/reports/` matching no glob" so reviewers can extend `RECURRING_GLOBS` over time. Out of scope for this issue: an auto-discovery scheme.
- **Risk — duplicate findings across handoff and review files:** a finding cited in a review may be re-summarized in the next session-exit handoff. Without dedup, the ledger inflates. Mitigation: dedup key is `(normalized(finding_summary[:120]), issue_ref)`; first occurrence wins; second occurrence is logged in the report's `Suppressed duplicates` section.
- **Risk — schema drift vs wave-2 `wrk-wiki-candidates.yaml`:** if this plan's schema diverges from `#2375`'s (artifact at `data/document-index/wrk-wiki-candidates.yaml`), downstream consumers must reconcile two schemas plus the wave-1 closed-issue ledger from `#2370`. Mitigation: this plan adopts wave-2's `status`, 0..3 binary-increment scoring rubric, and `wiki_target_domain` vocabulary verbatim; the schema doc names the merge contract explicitly so future drift is visible. **Note:** #2370 uses a structurally different 4-dimension × 0-5 weighted composite; any three-way merge must normalize scores.
- **Risk — `source_sha` churn:** every commit to a handoff file changes its blob sha, marking the candidate as stale even when the finding is unchanged. Mitigation: `source_sha` is informational; dedup is on summary + issue_ref, not sha; sha is used only by `#2238` citation guardrail downstream.
- **Risk — extractor regex misclassifies prose as bullets:** numbered lists, indented continuations, and code fences inside bullets can confuse a naive `^- ` walker. Mitigation: parse via a markdown-aware splitter (e.g., reuse `markdown-it-py` if already a dep, otherwise a regex set covering `^- `, `^* `, `^\d+\.\s`); record problem cases as unrecoverable rather than silently truncating.
- **Open:** Does the ledger live under `knowledge-base/` (cache convention; matches `wrk-completions.jsonl`) or under `knowledge/seeds/` (entries-schema convention)? Plan picks `knowledge-base/promotion-candidates.yaml` because the data is regenerable from the source Markdown and is a *cache* of extracted findings, not an authoritative seed. Flag for user during approval.
- **Open:** Should `existing_wiki_page_for(c)` actually scan `knowledge/wikis/*/wiki/` to set `extend_or_create` accurately, or default to `create` and let the human reviewer adjust at promotion time? Plan defaults to `create` for v1 with a TODO for a wiki-index lookup follow-on, to keep the v1 scope bounded.
- **Coordination note (feed16 patch, 2026-04-29):** six stale references to the prior-draft wiki-candidate path `knowledge-base/wiki-candidates.yaml` in this plan were updated to `data/document-index/wrk-wiki-candidates.yaml` per the superseding #2375 plan (`docs/plans/2026-04-29-issue-2375-wrk-completions-normalize.md`). The #2375 plan's Risk section already documented this coordination hazard. Lines patched: 19, 35, 51, 359, 396, 406, 438 (original numbering). Additionally, line 35 now notes the #2370 scoring-architecture difference (0..3 binary vs 4-dim × 0-5 weighted) identified by feed14/F1.
- **Coordination note (feed18 patch, 2026-04-29):** Patched 7 findings from Claude feed17 adversarial review (3 MINOR, 4 LOW). F1: downgraded "mechanical merge" claim to "structurally compatible with union-schema reconciliation" and added explicit DURABLE_CATEGORIES divergence caveat (overlap with #2375 is only `engineering`). F2: fixed 3 script paths from `scripts/operations/` → `scripts/cron/`. F3: documented intentional `data-pipeline` → `process` routing divergence vs #2375 in `route_domain` pseudocode comment. F4: removed stale `2026-04-26` self-reference slug parenthetical. F5: added "(counts as of 2026-04-27; …)" qualifiers to file-count evidence. F6: updated review artifact date prefix from `2026-04-26` to `2026-04-29`. F7: removed redundant "(final-slug = ...)" parenthetical from artifact map. Lines patched: 7, 8, 18, 35, 40, 67–69, 140, 153–155, 336 (original numbering).
- **Open:** Should the orchestrator be wired into a recurring schedule (cron / `scripts/cron/`) in this issue, or left as a manual `uv run` call until the queue stabilizes? Plan keeps it manual for v1; a follow-on issue can wire cron after one human review pass confirms the candidate quality.

---

## Complexity: T2

**T2** — four new Python scripts (one orchestrator + three extractors), four new test files, one new authoritative artifact (the YAML ledger), one new report, one schema-doc update, no engineering-package changes. Bounded scope: deterministic extraction over an existing finite Markdown corpus + a deterministic projection. No external network, no new infrastructure, no cross-repo edits, no automatic promotion. Sibling-aligned with wave-2 `#2375` and wave-1 `#2370`; merge contract documented up front.
