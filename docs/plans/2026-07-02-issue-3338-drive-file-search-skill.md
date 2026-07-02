# Plan for #3338: Skill: drive-file-search — context-aware related-file surfacing from work context

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-07-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3338
> **Client:** N/A
> **Project:** (none — repo-internal skill / harness infrastructure)
> **Lane:** lane:claude   <!-- matches the issue's lane:claude label; prose/skill authoring per epic #3333 provider routing -->
> **Review artifacts:** scripts/review/results/2026-07-02-plan-3338-claude.md | scripts/review/results/2026-07-02-plan-3338-codex.md | scripts/review/results/2026-07-02-plan-3338-gemini.md

---

## Resource Intelligence Summary

<!-- Issue class: Harness/Infrastructure (skill authoring). Consulted: issue body, epic body,
     sibling plan #3335 (CLI contract), existing skill tree + skill-lint tooling, domain map,
     nudge hook, PR #3341, live mount state. -->

### Existing repo code
- Found: `.claude/skills/data/ecosystem-data-sources/SKILL.md` — the DOMAIN-CATALOG-level sibling this skill complements at FILE level. Frontmatter shape to mirror: `name`, `description` (long, trigger-rich, quoted), `version`, `category: data`, `related_skills` (list), `triggers` (list of literal phrases), `type: reference`, `freedom: high`. Its "Governance (never violate)" section is the in-repo de-identification precedent: ACE_SHARE holds client data — "never reproduce raw content or client names in any repo; surface it as metadata only", bounded reads only, de-id stays on `lane:claude` (lines 71–77).
- Found: `.claude/hooks/ecosystem-domain-map.json` — 3,576-byte generated map (`_generated_from: llm-wiki/data/domain-database-index.yml`) with 12 domain entries (`riser`, `mooring`, `pipeline-subsea`, `structural-ffs`, `naval-arch-hydro`, `metocean`, `materials-standards`, `production-reservoir`, `geotech`, `asset-financial`, `drilling-well`, `cad-simulation`), each carrying `keywords[]`, `has_ace_share_precedent`, `repo_home`. This is the keyword source the skill's context-extraction step reuses — no new keyword list is authored.
- Found: `.claude/hooks/ecosystem-data-nudge.sh` — UserPromptSubmit hook that already consumes the same map (prompt keyword → one-line nudge, once-per-session, fail-open). #3339 extends this pattern to nudge THIS skill; this plan only has to keep trigger phrases compatible, not build the hook.
- Found: skill-lint / skill-index tooling exists (design-constraint question (2) answered YES):
  - `scripts/skills/validate_skills_frontmatter.py` (+ runner `scripts/skills/validate-skills.sh`) — validates every `SKILL.md` under a root: frontmatter delimiters, YAML parses to a mapping, `name` and `description` are non-empty strings; exit 1 on violations.
  - `scripts/skills/generate_skills_index.py` — rebuilds `.claude/skills-index.yaml` from the committed tree; inclusion requires canonical location `.claude/skills/<category>/<skill>/SKILL.md` + `name:` + `description:`. NOTE: `.claude/skills-index.yaml` is currently absent/untracked in this checkout (evidence below) — regeneration is a PR-time option, not a blocker.
  - `scripts/skills/audit-word-count.py` — flags oversized SKILL.md bodies; keep the skill compact and push detail to `references/`.
  - `scripts/curation/audit_skill_currency.py` — grades index/tree drift at family granularity; adding one new family under `.claude/skills/data/` is the normal, supported case.
- Found: `tests/skills/` — existing pytest convention for structural tests of PROSE skills (e.g., `tests/skills/test_doc_extraction_skill.py` asserts SKILL.md existence, required sections, line-count ceiling). The TDD list below follows this precedent.
- Gap: `.claude/skills/data/drive-file-search/` does not exist (gap proof below). No skill anywhere queries the drive indexes from work context.

### Standards
Not applicable — skill-authoring/harness issue; no engineering standard governs it.

| Standard | Status | Source |
|---|---|---|
| — | not applicable | `data/document-index/standards-transfer-ledger.yaml` not relevant to skill authoring |

### LLM Wiki pages consulted
No relevant wiki pages — harness infrastructure, not domain engineering knowledge. (The domain pointers the skill surfaces are read live from `llm-wiki/data/domain-database-index.yml` via the ecosystem-data-sources skill, per its "Quick lookup" section — deliberately not duplicated here.)

### Documents consulted
- Issue #3338 body — scope items 1–5 (SKILL.md + triggers, context-extraction procedure, CLI `--json` invocation + top-N presentation, guardrails, cross-provider prose); acceptance: real-work invocation returns relevant `/mnt/ace` + `/mnt/dde` files without the user naming either drive; works when only one drive is reachable.
- Epic #3333 body — Layer 2 of the architecture; sibling boundaries: #3335 supplies the CLI + registry (`lane:codex`), #3339 supplies the proactive nudge, #3340 supplies the usage playbook/metrics. Suggested order puts #3338 AFTER #3335.
- Sibling plan `docs/plans/2026-07-02-issue-3335-drive-index-query-cli.md` (on branch `origin/feat/plans-drive-index-3334-3335`, adversarial-reviewed) — defines the exact contract this skill consumes:
  - Invocation: `uv run python scripts/data/drive-index-search/search.py "<query>" --domain X --drive Y --limit N --json [--registry <path>]`.
  - `--json` envelope: `{query, generated_at, indexes_queried[], coverage_gaps[{id,path,reason}], results[{canonical_path, raw_path, source_index, adapter, score, rank_basis, meta{...}}]}`.
  - Exit codes: `0` = success INCLUDING partial results / empty results / empty selection; `2` = registry error OR selected>0 but zero indexes reachable.
  - Degradation: unreachable index → stderr warning + `coverage_gaps` entry + partial results, exit 0 — this is exactly the "works when only one drive is reachable" path.
  - Fixtures: `tests/data/drive_index_search/fixtures/` incl. `test-registry.yml` — the scripted smoke in this plan reuses them.
  - Open question flagged TO #3338: "result `meta` passthrough fields ... #3338 (skill) should confirm which fields it needs before v1 freeze" — answered in this plan (Pseudocode step 4: the skill requires only the top-level result fields; `meta` is optional garnish).
- PR #3341 (OPEN, not merged) — adds `scripts/setup/canonical-drive-links.sh` + `docs/standards/canonical-drive-references.md`; neither file exists on this branch yet (evidence below). The skill's unreachable-drive guidance must cite the script path AND the PR, since a session may run before merge.
- User-memory precedent (ecosystem Pages epic, `feedback` entries): "public repo ≠ safe to publish — every issue has exclude-list + leak-grep guard". workspace-hub is public; plans and issues quoting drive file names must pass the same de-id posture. In-repo anchor: the ecosystem-data-sources governance section cited above; enforcement precedent: `.claude/rules/wiki-sibling-routing.md` cross-client-leakage rules.

### Gaps identified
- No `.claude/skills/data/drive-file-search/` skill — SKILL.md, references file, and mock envelope fixture all built from scratch.
- No mock `--json` envelope exists anywhere — must be authored (hand-built to the #3335 schema) so the procedure is dry-runnable before #3335 lands.
- No structural test for this skill — `tests/skills/test_drive_file_search_skill.py` built from scratch (pattern exists, instance does not).
- The #3335 CLI itself does not exist yet (`scripts/data/drive-index-search/` missing) — hard dependency for the live path; pre/post split defined in TDD section.
- `--domain` vocabulary mismatch risk: the domain map uses ids like `mooring`/`riser`; the #3335 registry example uses `domains: [engineering, marine, drilling, cad, standards]`. The skill must not assume the map ids are valid `--domain` values (resolution in Pseudocode step 2; risk logged).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-02T10:53:50Z via `gh issue view` / `gh pr view`):
- `#3338` — OPEN — "Skill: drive-file-search — context-aware related-file surfacing from work context" (labels: cat:skills, enhancement, lane:claude, priority:high, status:needs-plan)
- `#3333` — OPEN — "EPIC: Context-aware drive-file search — skill + unified query layer over /mnt/ace + /mnt/dde file indexes"
- `#3334` — OPEN — "Drive-index: build full dde-drive SQLite FTS index + unfreeze master index dde coverage"
- `#3339` — OPEN — "Proactive invocation: drive-file nudge via UserPromptSubmit hook (extends #801 pattern)"
- `#3340` — OPEN — "Drive-file-search usage playbook: planning Resource-Intel integration, metrics, long-term unified-index decision"
- PR `#3341` — OPEN — "feat(setup): dde-drive NFS mount + canonical drive-reference convention"

**File existence** (`ls -la --time-style=long-iso`, 2026-07-02T10:53–10:57Z, worktree `feat/plans-drive-search-3338-3339`):
- EXISTS: `.claude/skills/data/ecosystem-data-sources/SKILL.md` (4,636 B), `.claude/hooks/ecosystem-domain-map.json` (3,576 B), `.claude/hooks/ecosystem-data-nudge.sh`, `scripts/skills/validate_skills_frontmatter.py` (2,780 B), `scripts/skills/validate-skills.sh`, `scripts/skills/generate_skills_index.py` (5,454 B), `scripts/skills/audit-word-count.py`, `tests/skills/` (pytest dir with skill structural tests)
- MISSING (new — this plan creates): `.claude/skills/data/drive-file-search/SKILL.md`, `.claude/skills/data/drive-file-search/references/context-extraction.md`, `.claude/skills/data/drive-file-search/references/mock-envelope.json`, `tests/skills/test_drive_file_search_skill.py`
- MISSING (dependency — created by other work, cited not built here): `scripts/data/drive-index-search/` + `config/drive-index-registry.yml` (#3335), `scripts/setup/canonical-drive-links.sh` + `docs/standards/canonical-drive-references.md` (PR #3341), `.claude/skills-index.yaml` (generator exists; index file not in this tree — `git ls-files` returns nothing for it)

**Line excerpts** (2026-07-02T10:54Z):
```
$ sed -n '1,22p' .claude/skills/data/ecosystem-data-sources/SKILL.md   (frontmatter, abridged)
---
name: ecosystem-data-sources
description: "Proactively surface what DATA the ecosystem already has for an engineering domain ..."
version: 1.0.0
category: data
related_skills: [research-literature, worldenergydata-source-readiness]
triggers: [do we have data for, where do we get data, ...]
type: reference
freedom: high
---

$ grep -A 10 '"mooring"' .claude/hooks/ecosystem-domain-map.json
    "mooring": {
      "has_ace_share_precedent": true,
      "keywords": ["mooring", "station-keeping", "station keeping", "catenary", "anchor", "mooring line"],
      "repo_home": "digitalmodel" },

$ sed -n '60,64p' scripts/skills/validate_skills_frontmatter.py
    for field in ("name", "description"):
        error = _validate_string_field(data, field, path)
```

**Gap proofs** (2026-07-02T10:53–10:57Z):
- `ls .claude/skills/data/drive-file-search` → "No such file or directory" → skill does not exist.
- `ls scripts/setup/canonical-drive-links.sh docs/standards/canonical-drive-references.md` → both "No such file or directory" → PR #3341 not merged into this branch.
- `ls /mnt/dde` → "No such file or directory"; `ls /mnt/ace` → mounts listing (`0_mrv`, `2H`, ...) → LIVE demonstration of the "only one drive reachable" acceptance condition on this box today.
- `ls docs/plans/ | grep -E '3338|3339'` → no matches → no prior plan for this issue on this branch.

**Reproduction proofs**: N/A — skill-authoring issue; no runtime failure alleged. The closest analog (CLI-not-yet-built) is covered by the gap proofs above and the DEPENDS split in the TDD list.

<!-- Source count: issue #3338 body, epic #3333 body, sibling plan #3335 (branch), PR #3341,
     ecosystem-data-sources SKILL.md, ecosystem-domain-map.json, ecosystem-data-nudge.sh,
     validate_skills_frontmatter.py(+.sh), generate_skills_index.py, audit-word-count.py,
     tests/skills/ precedent, live mount probes = 12 distinct sources ≥ 3 required. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-07-02-issue-3338-drive-file-search-skill.md |
| Skill (main deliverable) | .claude/skills/data/drive-file-search/SKILL.md |
| Context-extraction procedure (detail) | .claude/skills/data/drive-file-search/references/context-extraction.md |
| Mock `--json` envelope fixture | .claude/skills/data/drive-file-search/references/mock-envelope.json |
| Tests | tests/skills/test_drive_file_search_skill.py |
| Plan review — Claude | scripts/review/results/2026-07-02-plan-3338-claude.md |
| Plan review — Codex | scripts/review/results/2026-07-02-plan-3338-codex.md |
| Plan review — Gemini | scripts/review/results/2026-07-02-plan-3338-gemini.md |
| Wiki updates | none (no domain knowledge added) |
| Docs updates | docs/plans/README.md index row (at implementation/PR time — intentionally not edited in this authoring pass) |

---

## Deliverable

A `.claude/skills/data/drive-file-search/` skill (SKILL.md + references) that any agent runtime (Claude, Codex, Gemini) can follow to extract query terms from the current work context, invoke the #3335 unified drive-index CLI once with `--json`, and present ranked, de-identification-safe, freshness-caveated related files from `/mnt/ace` + `/mnt/dde` — with structural tests and a mock-envelope dry-run that work before #3335 lands.

---

## Pseudocode

The skill is PROSE + one CLI command. "Pseudocode" here is the procedure the SKILL.md body encodes, written so a non-Claude runtime (Codex/Gemini) can execute it with only `bash`, `gh`, and `python`. No Claude-specific tools appear anywhere in the procedure.

### SKILL.md frontmatter (design checkpoint — mirrors ecosystem-data-sources shape, passes validate_skills_frontmatter.py and generate_skills_index.py inclusion rules)

```yaml
---
name: drive-file-search
description: "Surface SPECIFIC FILES on the shared drives (/mnt/ace, /mnt/dde) relevant
  to the current task — the FILE-level complement to ecosystem-data-sources (which answers
  at the domain-catalog level). Extracts query terms from the active work context (repo,
  issue title/labels, engineering-domain keywords, artifact-type hints), runs the unified
  drive-index CLI once, and presents ranked canonical paths with freshness caveats.
  Use when someone asks about similar past work, prior projects, or whether files/examples/
  precedent exist, when a task in an engineering domain would benefit from past deliverables
  (a mooring calc → past mooring xlsx/py; a CAD task → past dwg/ipt/step; a standards question
  → the standards PDF inventory), or when anyone says to search the drives."
version: 1.0.0
category: data
related_skills:
- ecosystem-data-sources
triggers:
- similar past work
- do we have files for
- do we have examples of
- do we have precedent for
- search the drives
- prior project
- past project files
- have we done this before
type: reference
freedom: high
---
```

Trigger-design note (issue scope item 1 + co-occurrence guidance): the literal `triggers` list carries the four phrasings named in the issue; the `description` carries the domain+artifact co-occurrence guidance ("mooring calc → past mooring xlsx/py", etc.) so description-matching runtimes fire on domain work even without a literal trigger phrase. The literal triggers are disjoint from ecosystem-data-sources' triggers ("do we have data for", "data sources for") — FILE-level asks vs DATA/domain-level asks — so both the #3339 nudge and skill routers can discriminate.

Size note (review F1): the description as drafted (~120 words) consumes a large slice of the audit budget — `scripts/skills/audit-word-count.py::classify` flags >200 lines → WARNING and >500 words → OVER_BUDGET. The description MUST be tightened at implementation (keep the co-occurrence guidance, cut the prose) so the whole SKILL.md stays within ≤200 lines AND ≤500 words; the size pytest below pins these audit thresholds, not the looser doc-extraction 400-line ceiling.

### Step 1 — Extract work context (references/context-extraction.md carries the full procedure)

```
function extract_context():
    # (a) repo + issue — all commands fail-soft: on error, drop that signal and continue
    repo   = basename(git rev-parse --show-toplevel)          # "" if not a git repo
    issue  = if an issue number is known in-session:
                 gh issue view N --json title,labels
                 terms_issue = significant words of title (strip stopwords, numbers-only tokens)
                 labels like cat:*/domain hints noted
    # (b) engineering domain — reuse the generated map, never a hand-copied list
    map    = read .claude/hooks/ecosystem-domain-map.json     # 12 domains, keywords[]
    domain = first domain whose keywords[] match the task description / issue title
             (word-boundary, case-insensitive — same matching posture as ecosystem-data-nudge.sh)
    # (c) artifact-type hints — task type → file-type expectation, folded into presentation
    hints  = calcs/analysis → [xlsx, py, csv] | CAD/geometry → [dwg, ipt, step, sldprt, iges]
             | standards/code question → [pdf] | simulation → [dat, sim, yml, owr]
    return (repo, terms_issue, domain, domain_keywords, hints)
```

### Step 2 — Assemble the query (2–5 terms, one CLI call)

```
function build_query(context):
    terms = dedupe(top domain keyword(s) that actually matched + 1–3 significant issue-title words)
    # --domain vocabulary guard: map ids (mooring, riser, ...) are NOT guaranteed to be
    # registry `domains:` values (registry example uses engineering/marine/cad/standards).
    if config/drive-index-registry.yml exists AND domain appears in any entry's domains: list:
        domain_flag = "--domain <domain>"
    else:
        domain_flag = ""                      # fold the domain word into the query terms instead
    return (" ".join(terms), domain_flag)
```

Guard note (review F6): folding the domain word into the query terms is the SAFE DEFAULT — per #3335 (post-review), an entry with `domains:` absent matches ALL queries, and an unknown `--domain` yields an EMPTY selection with exit 0 (not an error), so the guard only prevents a silent-empty result, and a grep-level "appears in any entry's domains: list" check can false-positive on comments or other keys; treat the guard as best-effort and prefer folding whenever in doubt.

### Step 3 — Invoke the CLI (the ONE command; #3335 contract)

```
uv run python scripts/data/drive-index-search/search.py "<terms>" [--domain <d>] --json --limit 20
```

```
function run_and_branch():
    exit 0  → parse the JSON envelope (stdout); proceed to Step 4
              (0 covers partial results and empty results — check coverage_gaps either way)
    exit 2  → registry error OR zero reachable indexes:
              tell the user which drives/indexes are down (stderr + envelope if any),
              point to scripts/setup/canonical-drive-links.sh (canonical mount fixer)
              and PR #3341 (if the script is absent — convention not yet merged);
              offer the domain-catalog fallback: ecosystem-data-sources skill
    CLI missing (file not found) → #3335 not yet implemented: say so explicitly,
              cite issue #3335, fall back to ecosystem-data-sources; do NOT improvise
              ad-hoc drive crawls (governance: bounded reads only)
```

### Step 4 — Present top-N (envelope fields the skill REQUIRES — answers #3335's open question)

```
function present(envelope, hints, limit=10 shown of 20 fetched):
    required per result: canonical_path, source_index, score, rank_basis
    optional garnish:    meta.* (mtime/size/format when present), raw_path (never shown, de-id aid)
    for each of top N results:
        line 1: canonical_path                       # always /mnt/<drive>/... form
        line 2: why-relevant — which query terms matched, rank_basis, whether the
                extension matches an artifact-type hint (boost presentation order of
                hint-matching extensions WITHIN equal-score groups; never re-rank across scores)
        line 3: source: <source_index> + freshness caveat from the registry entry's
                freshness/built_at (e.g., "master_document_index — frozen 2026-04-17;
                dde results may be stale")
    if envelope.coverage_gaps non-empty:
        state plainly what was NOT searched: "index <id> not searched (<reason>) —
        results exclude <drive>; to restore: scripts/setup/canonical-drive-links.sh (PR #3341)"
        # <reason> is OPAQUE FREE TEXT quoted VERBATIM from coverage_gaps — #3335
        # defines no reason enum; never pattern-match or paraphrase it (review F4)
    then offer next actions (exactly these, per issue scope item 3 + #3340 hand-off):
        1. open/read a listed file (bounded read of that file only)
        2. record chosen paths as a "Documents consulted" entry in the active plan's
           Resource Intelligence section (the #3340 playbook formalizes this loop)
        3. refine terms and re-run (one more CLI call, not a loop)
```

### Step 5 — Guardrails (verbatim section in SKILL.md)

```
- READ-ONLY on drives: this skill NEVER writes to /mnt/ace or /mnt/dde; the CLI opens
  indexes mode=ro (per #3335). Opening a surfaced file is a bounded read of that file.
- De-identification (public-repo rule): workspace-hub issues and docs/plans/ are PUBLIC.
  Drive file names/paths frequently embed client names and project identifiers.
  Before quoting any surfaced path into an issue, plan, PR, or commit message:
    * scan the path for client-identifying tokens (company names, project codes, personnel);
    * if found, refer to it as metadata only ("a past <domain> deliverable on /mnt/ace,
      path recorded locally") or redact the identifying segment;
    * same posture as ecosystem-data-sources governance (ACE_SHARE = client data,
      metadata-only surfacing) and the ecosystem-pages leak-grep/exclude-list precedent.
  Showing full paths to the LOCAL user in-session is fine; PERSISTING them into public
  artifacts is the gated act. De-id judgment stays on lane:claude — flag, don't delegate.
- Unreachable drive: normal, expected state (dde is unmounted on this box today) —
  present partial results + the coverage_gaps caveat; never mount, never sudo.
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | .claude/skills/data/drive-file-search/SKILL.md | the skill: frontmatter + compact body (context extraction summary, the one CLI command, presentation rules, guardrails, related skills) — kept under word-count audit thresholds by pushing detail to references/ |
| Create | .claude/skills/data/drive-file-search/references/context-extraction.md | full context-extraction procedure (Step 1–2 detail), the artifact-type hint table, and the WORKED MOCK WALKTHROUGH: a mooring-calc context run end-to-end against references/mock-envelope.json with the exact expected presentation output (this is TDD test 1's checked example) |
| Create | .claude/skills/data/drive-file-search/references/mock-envelope.json | hand-built fixture conforming exactly to the #3335 `--json` schema: 5 results across ≥2 `source_index` values (mixed rank_basis fts_bm25/token_match), 1 `coverage_gaps` entry for a dde index whose `reason` is treated as OPAQUE FREE TEXT (#3335 defines no reason enum — no value assertion anywhere; review F4) — exercises partial-results presentation and the freshness caveat; all paths fictional/de-identified |
| Create | tests/skills/test_drive_file_search_skill.py | structural pytest (pattern: tests/skills/test_doc_extraction_skill.py): frontmatter fields, trigger phrases, guardrail section presence, mock-envelope schema conformance, a `skipif`-gated scripted smoke against the #3335 fixture registry, AND the shared cross-artifact trigger-alignment test with #3339 (skip-guarded until both this SKILL.md and `.claude/hooks/drive-file-map.json` land; single shared test file for both plans — review F2) |
| Update | docs/plans/README.md | add this plan to the index (at implementation/PR time — NOT edited in this plan-authoring pass) |

No existing file is modified. `.claude/skills-index.yaml` regeneration (`scripts/skills/generate_skills_index.py`) is optional at PR time and only if the index file exists on main by then (it is absent in this tree — evidence above).

---

## TDD Test List

Skills are prose — "tests" here are (1) a checked worked example, (2) the existing skill-lint tooling (found — cited in Resource Intelligence), (3) structural pytest + a scripted CLI smoke. Split by dependency:

**Pre-#3335 (runnable at this PR):**

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| mock-envelope walkthrough (documented, in references/context-extraction.md) | the whole procedure is followable by a non-Claude runtime: mooring-calc context → terms → parse mock envelope → presentation with why-relevant lines, source+freshness caveats, coverage_gaps warning, 3 next actions | references/mock-envelope.json + the worked context ("digitalmodel mooring fatigue calc, issue title 'Mooring line fatigue screening'") | the exact presentation block printed in the reference doc; reviewer can replay it step-by-step |
| skill-lint: `bash scripts/skills/validate-skills.sh .claude/skills/data/drive-file-search` | frontmatter delimiters, YAML mapping, non-empty `name`/`description` | new SKILL.md | "Skill validation passed (1 files).", exit 0 |
| test_frontmatter_contract (pytest) | frontmatter has name=drive-file-search, category=data, type=reference, `related_skills` contains `ecosystem-data-sources`, `triggers` contains "similar past work", "search the drives", "prior project", and a "do we have … for" phrasing | SKILL.md parsed with yaml | all assertions pass |
| test_triggers_disjoint_from_ecosystem_data_sources (pytest) | FILE-level vs DOMAIN-level routing stays discriminable | both skills' `triggers` lists | zero literal overlap |
| test_body_contains_contract_anchors (pytest) | body cites the ONE CLI command (`scripts/data/drive-index-search/search.py`), `--json`, exit-code 2 branch, `coverage_gaps`, `canonical-drive-links.sh`, and a De-identification/read-only guardrails section | SKILL.md body text | all anchors present |
| test_mock_envelope_schema (pytest) | fixture conforms to the #3335 envelope: top-level keys `query, generated_at, indexes_queried, coverage_gaps, results`; every result has `canonical_path, raw_path, source_index, adapter, score, rank_basis, meta`; every canonical_path starts `/mnt/` with no `/mnt/remote/` alias | references/mock-envelope.json | json loads; all key/shape assertions pass |
| test_skill_size_within_audit_limits (pytest) | SKILL.md stays within `scripts/skills/audit-word-count.py`'s OWN thresholds (>200 lines → WARNING, >500 words → OVER_BUDGET) — not the looser doc-extraction 400-line ceiling (review F1) | SKILL.md | ≤ 200 lines AND ≤ 500 words |
| test_domain_map_consumed_not_copied (pytest) | skill reads `.claude/hooks/ecosystem-domain-map.json`; no hand-copied keyword list drifting from the generated map — MECHANICAL assertions (review F3) | SKILL.md body text | literal path string `ecosystem-domain-map.json` IS present in the skill body; specific map keywords (e.g. `station-keeping`, `catenary`) are ABSENT from the body |
| test_hook_skill_trigger_alignment (pytest, skipif-gated until BOTH this SKILL.md and `.claude/hooks/drive-file-map.json` (#3339) exist) | cross-artifact routing (review F2): hook↔skill trigger sets stay reconciled | this SKILL.md `triggers:` + #3339's `drive-file-map.json` | every canonical skill trigger phrase ("similar past work", "search the drives", …) fires the hook's Tier-1 matcher; DATA-level phrasings ("do we have data for X") do NOT route to this FILE-level skill (match neither the skill's triggers nor the hook's tiers) |

**Post-#3335 (DEPENDS — `skipif not Path("scripts/data/drive-index-search/search.py").exists()`):**

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_scripted_smoke_fixture_registry (pytest, skipif-gated) | the live invocation shape works against #3335's own fixtures — no live drives touched | `uv run python scripts/data/drive-index-search/search.py "riser" --registry tests/data/drive_index_search/fixtures/test-registry.yml --json --limit 5` via subprocess | exit 0; stdout parses as JSON; envelope keys match test_mock_envelope_schema's schema (single source of truth for both assertions) |
| test_scripted_smoke_exit2_branch (pytest, skipif-gated) | the skill's exit-2 guidance matches reality | same CLI with `--registry <path-to-nonexistent.yml>` | exit 2 (registry error), confirming the SKILL.md branch text |
| live acceptance (manual, issue-level — not pytest) | issue acceptance: during a real digitalmodel mooring calc, skill surfaces relevant `/mnt/ace` (+ `/mnt/dde` once #3334/#3341 land) files without the user naming either drive; partial-results path exercised while dde is unmounted | real session on ace-linux-1 | top-N with canonical paths + dde coverage_gap caveat |

---

## Acceptance Criteria

- [ ] `.claude/skills/data/drive-file-search/SKILL.md` exists at the canonical `<category>/<skill>/SKILL.md` location with the frontmatter specified above (name, description, version, category, related_skills=[ecosystem-data-sources], triggers incl. the four issue phrasings, type, freedom)
- [ ] `bash scripts/skills/validate-skills.sh .claude/skills/data/drive-file-search` exits 0 — OR, if uv resolution fails (uv is broken for several repos on this box; the runner execs `uv run`), the fallback path `python3 scripts/skills/validate_skills_frontmatter.py .claude/skills/data/drive-file-search` exits 0 (the validator itself needs only pyyaml; review F5)
- [ ] All pre-#3335 tests pass: `uv run pytest tests/skills/test_drive_file_search_skill.py -v` (post-#3335 tests SKIP cleanly while the CLI is absent, PASS once it lands — re-run recorded on the implementing PR of whichever merges second)
- [ ] Cross-provider followability: the SKILL.md body contains no Claude-only tool references — every action is prose + `gh`/`git`/`uv run python`/file reads (spot-check: grep body for tool-invocation syntax finds only the one CLI command); scope item 5 satisfied
- [ ] The mock walkthrough in references/context-extraction.md is complete: context → terms → command → parsed envelope → presentation, including the coverage_gaps caveat and the three next actions
- [ ] Guardrails section present verbatim-in-substance: read-only drives; de-identification rule for quoting paths into public artifacts (metadata-only fallback); unreachable-drive guidance naming `scripts/setup/canonical-drive-links.sh` + PR #3341
- [ ] No regression: `uv run pytest tests/skills/ -v` passes (or matches pre-change baseline recorded at branch time)
- [ ] Docs: plan indexed in docs/plans/README.md at PR time
- [ ] Review artifacts posted to scripts/review/results/ (3 providers)
- [ ] DEFERRED (tracked, not blocking this PR): live acceptance run per issue body once #3335 (CLI) — and for dde coverage #3334 + #3341 — are merged; result posted to #3338 before close

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | **MINOR** | Size test contradicted the audit tool's own thresholds (F1); hook↔skill trigger alignment with #3339 was ungoverned (F2); map-copy test unfalsifiable as specified (F3); mock pinned a `reason` value #3335 never promises (F4); validate-skills.sh transitively needs uv (F5); `--domain` guard is best-effort only (F6). Evidence hygiene verified good (F7). Full artifact: scripts/review/results/2026-07-02-plan-3338-claude.md |
| Codex | PENDING — dispatch deferred (codex runtime CPU-constrained on this host; see epic #3333 routing note) | — |
| Gemini | PENDING — dispatch deferred (codex runtime CPU-constrained on this host; see epic #3333 routing note) | — |

**Overall result:** PASS after revisions (Claude r1)

Revisions made based on review:
- **F1** → TDD `test_skill_size_within_audit_limits` re-pinned to the audit's own thresholds (≤200 lines AND ≤500 words); frontmatter size note added requiring the ~120-word description be tightened at implementation.
- **F2** → new `test_hook_skill_trigger_alignment` (skip-guarded until both #3338 skill and #3339 map land) added to TDD list + Files to Change: every canonical skill trigger must fire #3339's hook matcher; DATA-level phrasings must not route to this FILE-level skill; trigger-collision risk updated.
- **F3** → `test_domain_map_consumed_not_copied` made mechanical: literal path `ecosystem-domain-map.json` present in the body AND specific map keywords (`station-keeping`, `catenary`) absent.
- **F4** → mock fixture + Step 4 presentation treat `coverage_gaps[].reason` as opaque free text quoted verbatim (no enum assertion); reason-vocabulary question flagged upstream to #3335 in Risks.
- **F5** → acceptance criteria gained the `python3 scripts/skills/validate_skills_frontmatter.py` fallback beside validate-skills.sh (uv broken for several repos on this box).
- **F6** → Step 2 guard note added (fold-into-query-terms is the safe default; `domains:` absent ⇒ match-all; unknown `--domain` ⇒ empty selection exit 0; grep-level checks can false-positive); the "adopt the domain-map's 12 ids in the registry" ask marked BLOCKING before #3335 v1 freeze.

---

## Risks and Open Questions

- **Risk — hard dependency on #3335:** the CLI does not exist (gap proof above); only its PLAN exists, adversarial-reviewed on a sibling branch. If #3335's implementation drifts from its plan (flag names, envelope keys, exit codes), this skill's body and mock fixture drift with it. Mitigation: the pytest schema assertions + scripted smoke against #3335's fixture registry turn drift into a test failure, not a silent lie; implementation step 1 is `gh issue view 3335` + re-read the merged contract.
- **Risk — `--domain` vocabulary mismatch (identified, unresolved upstream):** ecosystem-domain-map ids (`mooring`, `riser`, ...) vs #3335 registry example `domains:` values (`engineering`, `marine`, `cad`, ...). Mitigated in-skill (Step 2 guard: only pass `--domain` if the value appears in the registry; else fold into query terms — the safe default, since the guard is best-effort per review F6). **BLOCKING ask to #3335 before its v1 freeze:** adopt the domain-map's 12 ids as the registry `domains:` vocabulary — this lets the skill pass `--domain` unconditionally and eliminates the guard entirely; raise on the issue now, not at implementation.
- **Risk — trigger collision/overlap with ecosystem-data-sources and the #3339 nudge:** phrasing like "do we have files for" sits near "do we have data for". Mitigated: literal-trigger disjointness vs ecosystem-data-sources is pinned by a test; hook↔skill alignment with #3339 is now pinned by the skip-guarded `test_hook_skill_trigger_alignment` (review F2) — every canonical skill trigger must fire #3339's matcher, and DATA-level phrasings must route to neither this skill nor the FILE-level nudge (they belong to #801/ecosystem-data-sources).
- **Flag to #3335 (review F4):** `coverage_gaps[].reason` has no defined vocabulary/enum — raise on #3335 alongside the `meta` passthrough question this plan already answers; until then all consumers (this skill's presentation, the mock fixture, tests) treat it as opaque free text quoted verbatim.
- **Risk — de-identification is judgment, not mechanics:** a path like `/mnt/ace/2H/<client>/...` leaking into a public plan is one careless paste away. The skill makes the rule explicit and local (flag at presentation time, metadata-only fallback), but enforcement stays human/lane:claude; #3340's playbook should add the leak-grep check to the Resource-Intel recording loop.
- **Risk — freshness caveats depend on registry metadata:** the caveat line reads `freshness/built_at` from `config/drive-index-registry.yml` (a #3335 artifact). If an entry lacks freshness metadata, the skill must degrade to "freshness unknown" rather than invent a date.
- **Open:** should SKILL.md also carry a `capabilities`/`tools` frontmatter block (knowledge-pipeline style) in addition to the ecosystem-data-sources style? Current decision: NO — mirror ecosystem-data-sources exactly (`type: reference`, `freedom: high`); validator requires only name+description. Flag for user if skill routers need more.
- **Open:** `.claude/skills-index.yaml` is absent in this tree though the generator and the currency audit both reference it — regenerate at PR time or leave to the index's own remediation? Default: leave; adding one skill must not take ownership of a 224-entry index rebuild.
- **Open:** fetched `--limit 20` / shown top-10 are initial guesses; #3340's metrics should tune them.

---

## Complexity: T2

**T2** — one new skill family (SKILL.md + 2 reference files) + one structural test module; no code changes to existing paths, but the deliverable encodes a cross-provider procedure against a not-yet-implemented CLI contract, requires a schema-pinned mock fixture, de-identification guardrails, and a pre/post-dependency test split — beyond T1 prose, well short of T3.
