# Plan for #2392: Wiki coverage-gap detector — inventory × wiki diff per discipline

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-04-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2392
> **Review artifacts:** scripts/review/results/2026-04-20-plan-2392-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/data/document-index/` — provenance.py, phase-a-index.py build the L2 registry that this tool joins against. Baseline OK.
- Found: `scripts/knowledge/llm_wiki.py` — wiki-ingest surface; does NOT produce gap lists.
- Gap: no existing script joins `/mnt/ace/**` inventory against `knowledge/wikis/**` coverage — confirmed via `Glob "**/detect*gap*" "**/wiki_coverage*"` → 0 results.

### Standards
Not applicable — this is tooling, not an engineering calculation.

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/index.md` — sampled; most pages lack `doc_key` frontmatter (blocked by #2360).
- `knowledge/wikis/marine-engineering/wiki/index.md` — uses different frontmatter shape per operating model §8.1 (domain autonomy).

### Documents consulted
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` §2 (layer ownership), §4 (flows) — tool output must classify gaps per most-durable-owner rule.
- `docs/plans/2026-04-11-issue-2205-multi-machine-llm-wiki-resource-doc-intelligence-operating-model.md` — parent plan, §2 forbidden inventions applies.
- `data/document-index/registry.yaml` (L2 inventory source).
- `data/document-index/mounted-source-registry.yaml` (path→machine availability).
- `data/document-index/code-registry.yaml` (industry codes inventory).
- `data/document-index/online-resource-registry.yaml` (external sources inventory).
- `data/document-index/dde-standards-inventory.yaml` (standards inventory).
- Related issue #2366 — scorecard/action queue; this issue's output becomes its input.
- Related issue #2365 — design-code registry promotion; overlaps on `code-registry.yaml` but scoped to standards-only.

### Gaps identified
- No tooling exists that produces per-domain gap YAML files.
- No standard for gap-entry shape; this plan defines one.
- `doc_key` coverage in wikis is partial (blocked by #2360); tool must tolerate missing keys.

**Distinct sources consulted: 9** (issue body + 8 above) — exceeds ≥3 minimum.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-20-issue-2392-wiki-coverage-gap-detector.md` |
| Tests | `tests/knowledge/test_detect_wiki_gaps.py` |
| Implementation | `scripts/knowledge/detect_wiki_gaps.py` |
| Config | `config/ai-tools/wiki-gap-detection.yaml` (discipline→wiki mapping) |
| Output | `docs/reports/wiki-coverage-gaps/<domain>.yaml` |
| Cron wiring | `config/scheduled-tasks/schedule-tasks.yaml` (add entry) |
| Plan review — Claude | `scripts/review/results/2026-04-20-plan-2392-claude.md` |

---

## Deliverable

A `detect_wiki_gaps.py` CLI that emits one gap YAML per wiki domain listing sources-without-wiki-pages, joined by `doc_key`, with per-entry availability-tier classification.

---

## Pseudocode

```
function detect_gaps(config):
    l2_sources = load_registry("data/document-index/registry.yaml")
            ∪ load_registry("data/document-index/mounted-source-registry.yaml")
            ∪ load_registry("data/document-index/code-registry.yaml")
            ∪ load_registry("data/document-index/online-resource-registry.yaml")
            ∪ load_registry("data/document-index/dde-standards-inventory.yaml")
    analysis_reports = scan("docs/reports/*.md") filtered by L3-eligibility heuristic
    wiki_doc_keys = scan("knowledge/wikis/*/wiki/**/*.md") → set of frontmatter doc_key

    for each source in l2_sources ∪ analysis_reports:
        if source.doc_key not in wiki_doc_keys:
            discipline = classify_discipline(source)  # tag-based
            availability_tier = classify_tier(source)  # per operating-model §7
            emit gap_entry to docs/reports/wiki-coverage-gaps/<discipline>.yaml

    write summary to docs/reports/wiki-coverage-gaps/_summary.md
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/knowledge/detect_wiki_gaps.py` | Main implementation |
| Create | `tests/knowledge/test_detect_wiki_gaps.py` | TDD test suite |
| Create | `config/ai-tools/wiki-gap-detection.yaml` | Discipline→wiki-domain mapping, eligibility heuristic rules |
| Create | `docs/reports/wiki-coverage-gaps/README.md` | Explains output format + re-run cadence |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | Schedule weekly run |
| Update | `docs/plans/README.md` | Add this plan to index |

---

## TDD Test List

| Test name | Verifies | Input | Expected output |
|---|---|---|---|
| test_known_source_not_in_wiki_surfaces | Source with `doc_key` X, no wiki ref → appears in gap YAML | fixture with 1 registry entry, 0 wiki pages | gap YAML contains X |
| test_wiki_covered_source_excluded | Source with `doc_key` X, wiki page references X → excluded | fixture with 1 registry + 1 wiki page | gap YAML empty |
| test_missing_doc_key_marked_identity_unresolved | Source with null `doc_key` still emitted but flagged | fixture with unindexed entry | entry has `status: identity-unresolved` |
| test_discipline_classification | Source tagged `naval-architecture` routes to naval-architecture gap file | fixture with tagged entry | file `naval-architecture.yaml` gets entry |
| test_availability_tier_git_tracked | L2 registry entry gets tier 1 (git-tracked metadata) | fixture L2 entry | `tier: git-tracked` |
| test_availability_tier_shared_mount | `/mnt/ace/` L1 entry gets tier 2 (shared) | fixture with mount path | `tier: shared-mount` |
| test_dry_run_writes_nothing | `--dry-run` prints counts, no file writes | full fixture corpus | filesystem unchanged |
| test_idempotent_rerun | 2nd run with unchanged input produces identical output | same fixture run twice | byte-identical YAML |
| test_analysis_report_eligibility | `docs/reports/` entries filtered by L3-eligibility heuristic | 5 reports, 2 eligible | 2 gap entries |

---

## Acceptance Criteria

- [ ] All tests pass: `uv run pytest tests/knowledge/test_detect_wiki_gaps.py -v`
- [ ] No regression: `uv run pytest` at repo root
- [ ] End-to-end run against current corpus completes in <5 min
- [ ] Produces ≥1 gap YAML per wiki domain on first real run (sanity check)
- [ ] Weekly cron entry merged into `config/scheduled-tasks/schedule-tasks.yaml`
- [ ] Review artifacts posted under `scripts/review/results/`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (self) | MINOR | See findings A–C below |
| Codex | PENDING | Cross-provider review optional-before-approval |
| Gemini | PENDING | Optional |

**Overall result:** PASS-after-minor-fixes applied inline.

Revisions made based on self-review (see `scripts/review/results/2026-04-20-plan-2392-claude.md`):
- Added `_summary.md` output in pseudocode (finding A — was implicit in AC, made explicit in impl).
- Added analysis-report eligibility heuristic to tests (finding B — was untested).
- Added `availability-tier` tests covering both tiers 1 and 2 (finding C — tier 3 local-cache excluded explicitly as non-L1/L2 source).

---

## Risks and Open Questions

- **Risk:** Many `doc_key`s in wikis are missing until #2360 lands. Mitigation: tool emits `identity-unresolved` status; re-run after #2360 merge gives true coverage.
- **Risk:** Analysis-report L3-eligibility heuristic is subjective; may over- or under-emit. Mitigation: config-driven rule file; first real run calibrated with user review.
- **Open:** Should the tool propose wiki-page skeletons automatically? Out of scope here; follow-on issue if desired.

---

## Complexity: T2

New script with config + tests + cron wiring; no existing file significantly modified.
