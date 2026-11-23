# Plan for #2380: Execute Batch Pack 3 Tier A for external engineering software profiles

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-23
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2380
> **Review artifacts:** scripts/review/results/2026-04-23-plan-2380-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `data/document-index/online-resource-registry.yaml` (3,423 lines) — source registry with `type in [github_repo, tool]` entries and structured `notes` field per entry.
- Found: `docs/reports/llm-wiki-staged-batch-packs.md` — Batch Pack 3 design document (Section 3.3) specifying scope (153 entries), Tier A/B split, target wiki domains, owned/read-only/forbidden paths, and validation sequence.
- Found: `docs/reports/llm-wiki-external-source-priority-queue.md` — prioritizes this family as P2 (medium ROI, bounded extraction) and lists related issues.
- Gap: No Tier A promotion artifact under `docs/reports/batch-pack-3-*.md` exists yet.
- Gap: No engineering-software `entities/` stubs for the majority of tooling families (CFD, CAD, hydrodynamics meshing) in `knowledge/wikis/engineering/wiki/`.

### Standards
Not applicable — this batch promotes engineering software profiles, not standards.

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/index.md` — 22 entity pages already exist; `CadQuery`, `BEMRosetta Tool`, `OpenFOAM CFD`, `OrcaFlex Solver`, `OrcaWave Solver`, `AQWA Solver`, `LLM Wiki Tool`, `digitalmodel` are already promoted. These are EXTEND-only cases.
- `knowledge/wikis/engineering/CLAUDE.md` — frontmatter schema (title, tags, added, last_updated required; sources/domain/cross_links optional); `entities/` is the correct page family for tool profiles.
- `knowledge/wikis/marine-engineering/wiki/` — has `entities/`, `concepts/`, `comparisons/`, `visualizations/` but no `standards/`; marine-engineering entities include hydrodynamics tool profiles, so collisions possible.

### Documents consulted
- Parent epic #2390 — batch Pack 3 assigned to Wave 6 execution; pairs with #2369 (Batch Pack 2) in a parallelization bundle.
- Issue #2380 body — scope locked to Tier A only, no network scraping, no cloning, no downloads; collapse repo/docs twins into unique package roots; exclude MCP/general catalogs, archives, portals, journals, standards/regulatory, papers/tutorials, course materials; exact existing wiki matches are extend-only.
- Issue #2039 — engineering wiki ingest umbrella (upstream consumer of stubs).
- Issue #2042 — skill metadata as wiki pages (adjacent approach); deduplication guidance for tools overlapping with skills.

### Gaps identified
- No Tier A filter/classification pipeline exists; the agent must apply the issue-body filter (engineering software/packages only, collapsing repo/docs twins, excluding non-engineering families) during plan execution.
- No duplicate-detection map between registry entries and existing `knowledge/wikis/engineering/wiki/entities/*` pages.
- No carry-forward list for Tier B (needs-scraping), MCP/general catalogs, standards/regulatory entries, or papers/tutorials excluded from this wave.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-23 via `gh issue view`):
- `#2380` — OPEN — "feat(knowledge): execute Batch Pack 3 Tier A for external engineering software profiles"
- `#2390` — OPEN — epic coordinator (Work Wave 6: #2380 + #2369 parallel bundle)
- `#2364` — OPEN — Batch Pack 1 (parallel Lane B1 work; no plan file yet on disk as of 2026-04-23)
- `#2369` — OPEN — Batch Pack 2 (parallel Lane B1 work; no plan file yet on disk as of 2026-04-23)
- `#2373` — OPEN — Batch Pack 4 (this Lane B2, sibling plan file being drafted concurrently)

**File existence** (`ls -la` 2026-04-23):
- EXISTS: `data/document-index/online-resource-registry.yaml` (3,423 lines)
- EXISTS: `docs/reports/llm-wiki-staged-batch-packs.md`
- EXISTS: `docs/reports/llm-wiki-external-source-priority-queue.md`
- EXISTS: `knowledge/wikis/engineering/wiki/index.md` (77-page count)
- EXISTS: `knowledge/wikis/engineering/wiki/entities/` (22 entities, including CadQuery, OpenFOAM-CFD, OrcaFlex-Solver, OrcaWave-Solver, AQWA-Solver, BEMRosetta-Tool)
- MISSING (new — this plan creates): `docs/reports/batch-pack-3-tier-a-engineering-software-profiles.md`
- MISSING (new — this plan creates): `docs/reports/batch-pack-3-tier-a-duplicate-map.yaml`
- MISSING (new — this plan creates): `docs/reports/batch-pack-3-tier-a-carry-forward.md`

**Line excerpts** (`grep -c` and `sed -n`):
- `grep -cE "^\s*type:\s*github_repo\s*$" data/document-index/online-resource-registry.yaml` → 57
- `grep -cE "^\s*type:\s*tool\s*$" data/document-index/online-resource-registry.yaml` → 97
- Total `github_repo + tool` = 154 (matches issue body claim of 154 entries; one more than the 153 cited in the Batch Pack 3 design doc — source registry has grown by one entry since the design was authored).

**Gap proofs**:
- `ls docs/reports/batch-pack-3*` → "No such file or directory" → confirms no Tier A report exists yet.
- `ls knowledge/wikis/engineering/wiki/entities/cadquery.md` → EXISTS → confirms extend-only case for CadQuery.
- `ls knowledge/wikis/engineering/wiki/entities/gmsh.md` → does not exist → confirms net-new candidate for Gmsh.

<!-- 6 distinct sources consulted: online-resource-registry.yaml, staged-batch-packs design doc, priority-queue doc, engineering wiki CLAUDE.md + index.md, issue #2380 body, and parent epic #2390. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-23-issue-2380-batch-pack-3-tier-a-engineering-software-profiles.md |
| Tier A execution report (primary output) | docs/reports/batch-pack-3-tier-a-engineering-software-profiles.md |
| Duplicate/extend-vs-create map | docs/reports/batch-pack-3-tier-a-duplicate-map.yaml |
| Carry-forward list (excluded + Tier B) | docs/reports/batch-pack-3-tier-a-carry-forward.md |
| Wiki-ready package/profile stubs | appended sections in the Tier A report above (no separate stub files committed in this wave — see Deliverable note) |
| Plan review — Claude | scripts/review/results/2026-04-23-plan-2380-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-23-plan-2380-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-23-plan-2380-gemini.md |

---

## Deliverable

A Tier A engineering software profile report (`docs/reports/batch-pack-3-tier-a-engineering-software-profiles.md`) containing wiki-ready package/profile stubs for net-new engineering tooling families derived offline from the existing `notes` fields of `type in [github_repo, tool]` entries in `online-resource-registry.yaml`, plus a duplicate/extend-vs-create YAML map and a carry-forward list — with zero network calls, zero cloning, and no modifications to `knowledge/wikis/**` in this wave.

**Note on scope boundary:** This issue produces wiki-READY stubs as a committed artifact under `docs/reports/`; the actual page creation under `knowledge/wikis/engineering/wiki/entities/**` is out of scope for #2380 and belongs to downstream consumers (#2039 engineering wiki ingest umbrella) so that this execution wave stays reversible and low-contention.

---

## Pseudocode

```
# Step 1 — Load and filter
entries = yaml.safe_load("data/document-index/online-resource-registry.yaml")["entries"]
candidates = [e for e in entries if e.type in {"github_repo", "tool"}]
assert len(candidates) == 154  # pre-run count gate

# Step 2 — Tier A classification (offline only)
def is_tier_a(entry):
    notes = entry.get("notes", "")
    return len(notes.strip()) >= MIN_NOTES_LEN and has_capability_keywords(notes)

tier_a = [e for e in candidates if is_tier_a(e)]
tier_b_deferred = [e for e in candidates if not is_tier_a(e)]

# Step 3 — Engineering-software filter
# Exclude per issue body: MCP/general catalogs, archives, portals, journals,
# standards/regulatory, papers/tutorials/course materials.
EXCLUDE_DOMAIN_PREFIXES = {"general", "regulatory", "standards"}
EXCLUDE_NAME_TOKENS = {"awesome", "catalog", "registry", "mcp", "journal",
                      "portal", "archive", "tutorial", "course", "paper"}
def is_engineering_software(entry):
    if entry.get("domain") in EXCLUDE_DOMAIN_PREFIXES: return False
    if any(tok in entry.name.lower() for tok in EXCLUDE_NAME_TOKENS): return False
    return True

engineering_tier_a = [e for e in tier_a if is_engineering_software(e)]

# Step 4 — Collapse repo/docs twins into package roots
# Heuristic: cluster by (normalized_name, domain). The registry already shows
# paired rows like "The Well" / "The Well (github)" / "The Well (huggingface)"
# and "Netgen/NGSolve" / "Netgen/NGSolve (docs)".
def package_root(name):
    return re.sub(r"\s*\((github|docs|huggingface|pypi)\)\s*", "", name).strip()

clusters = groupby(engineering_tier_a, key=lambda e: (package_root(e.name), e.domain))
packages = [merge_cluster(rows) for _, rows in clusters]

# Step 5 — Duplicate map against existing wiki entities
existing_entities = list_files("knowledge/wikis/engineering/wiki/entities/*.md")
for pkg in packages:
    match = find_exact_slug_match(pkg, existing_entities)
    pkg.status = "extend-only" if match else "create"

# Step 6 — Emit artifacts
write_report("docs/reports/batch-pack-3-tier-a-engineering-software-profiles.md",
             packages=packages)
write_yaml("docs/reports/batch-pack-3-tier-a-duplicate-map.yaml",
           extend_only=[p for p in packages if p.status == "extend-only"],
           create=[p for p in packages if p.status == "create"])
write_report("docs/reports/batch-pack-3-tier-a-carry-forward.md",
             tier_b=tier_b_deferred,
             non_engineering_excluded=[e for e in tier_a if not is_engineering_software(e)])

# Step 7 — Post-run validation (manual gates, below)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | docs/reports/batch-pack-3-tier-a-engineering-software-profiles.md | Primary Tier A deliverable (wiki-ready stubs grouped by package root) |
| Create | docs/reports/batch-pack-3-tier-a-duplicate-map.yaml | Extend-vs-create decision map against existing `knowledge/wikis/engineering/wiki/entities/*` |
| Create | docs/reports/batch-pack-3-tier-a-carry-forward.md | Tier B deferred list + explicitly excluded non-engineering entries with rationale |
| Update | docs/plans/README.md | Add plan row for #2380 |

**Forbidden / out of scope for this wave** (per issue body and Batch Pack 3 design doc §3.3 Paths):
- `knowledge/wikis/**` — read-only in this wave; no wiki page creation
- `config/**`, `.claude/**`, `tests/**`, `scripts/**`
- network access (GitHub API, curl, gh api repos, clones, downloads)

---

## TDD Test List

This issue produces offline report artifacts; TDD is validation-gate-oriented rather than pytest-driven. Each gate below is a falsifiable pre- or post-run check run during plan execution (not auto-run in CI).

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| pre_run_registry_exists | Source registry is present | `test -f data/document-index/online-resource-registry.yaml` | exit 0 |
| pre_run_candidate_count | Filter returns expected candidate count | `grep -cE "^\s*type:\s*(github_repo\|tool)\s*$" registry.yaml` | 154 |
| post_run_yaml_parses | Duplicate map YAML is parsable | `python3 -c "import yaml; yaml.safe_load(open('docs/reports/batch-pack-3-tier-a-duplicate-map.yaml'))"` | exit 0, returns dict |
| post_run_no_wiki_writes | Wave did not modify knowledge/wikis | `git diff --name-only \| grep -c '^knowledge/wikis/'` | 0 |
| post_run_only_owned_paths | Changes stay in owned paths | `git diff --name-only \| grep -v -E '^(docs/reports/\|docs/plans/)' \| wc -l` | 0 |
| post_run_package_roots_unique | No duplicate package roots in primary output | per-row `slug` unique | no dupes |
| post_run_all_extend_pages_exist | Every `extend-only` entry references an existing wiki entity file | `test -f knowledge/wikis/engineering/wiki/entities/<slug>.md` | exit 0 for each |
| post_run_carry_forward_complete | Every excluded entry from candidate set appears in carry-forward or tier_a output | `union(extend_only, create, tier_b, excluded) == candidates` | True |
| post_run_no_network_calls | No tool used network | shell history audit | no curl/gh-api/clone commands |

---

## Acceptance Criteria

- [ ] `docs/reports/batch-pack-3-tier-a-engineering-software-profiles.md` exists and groups package profiles by package root (collapsed repo/docs/huggingface twins)
- [ ] `docs/reports/batch-pack-3-tier-a-duplicate-map.yaml` parses and enumerates every decision as `extend-only` or `create` — no ambiguous rows
- [ ] `docs/reports/batch-pack-3-tier-a-carry-forward.md` explicitly lists every excluded entry with rationale (Tier B / non-engineering / MCP or general catalog / archive / portal / journal / standards-regulatory / paper / tutorial / course)
- [ ] `union(extend-only + create + tier_b + excluded) == 154` candidate entries — 100% accounted for
- [ ] Zero files under `knowledge/wikis/**` modified by this plan's commits
- [ ] Zero network calls performed during execution (no curl/gh-api/git-clone/wget)
- [ ] Every `extend-only` row references a file that actually exists under `knowledge/wikis/engineering/wiki/entities/`
- [ ] Review artifacts posted to `scripts/review/results/2026-04-23-plan-2380-*.md`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | dispatched |
| Codex | PENDING | dispatched |
| Gemini | PENDING | dispatched |

**Overall result:** PENDING

---

## Risks and Open Questions

- **Risk:** Tier A/B classification is heuristic; a richer-than-expected `notes` field might still omit the capability data a wiki stub needs. Mitigation: the carry-forward list explicitly catches these and re-routes them to Tier B without blocking the wave.
- **Risk:** Package-root collapsing heuristic (strip `(github|docs|huggingface|pypi)` suffix + match on domain) may over-merge. Mitigation: `duplicate-map.yaml` records every collapse decision for user review.
- **Risk:** Non-engineering exclusion tokens (`awesome`, `catalog`, `mcp`, `journal`, `portal`, `archive`, `tutorial`, `course`, `paper`) may cull a legitimate engineering tool whose name happens to match. Mitigation: carry-forward.md lists every exclusion with rationale so a reviewer can restore a false positive.
- **Risk:** Because Lane B1 (#2364, #2369) and Lane B2 (#2380, #2373) touch shared files (`docs/plans/README.md`, `docs/reports/`), serialized commit phase is required. Mitigation: this plan commits only through the main session; parallel write-only pattern per `.claude/memory/` feedback `feedback_parallel_agent_write_only_pattern`.
- **Open:** Should "The Well" and related datasets (15 TB physics simulation data) be treated as engineering software (tooling) or as a dataset (out of scope)? Flagged for user during plan approval — default behavior: carry-forward to a dataset-profiles wave, not this software-profile wave.
- **Open:** Should the `MCP Official Registry` and `Awesome MCP Servers` stay excluded (as the issue body says), or be promoted to an adjacent "infrastructure" profile? Default: excluded (honors explicit issue-body list).

---

## Complexity: T2

**T2** — new reports across 3 files, offline filter + classification pipeline, non-trivial duplicate-detection logic against existing wiki entities, clear acceptance gates. Not T1 (multiple files + real logic); not T3 (no multi-repo, no new code under `src/`, no new standards).
