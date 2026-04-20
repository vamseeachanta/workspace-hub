# Plan for #2392: Wiki coverage-gap detector — v2 (post-iteration-1 cross-review)

> **Status:** plan-review (iteration 2 of 3)
> **Complexity:** T2
> **Date:** 2026-04-20 (v2)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2392
> **v1 reference:** commit `5b4c347cd` + findings at `scripts/review/results/2026-04-20-plan-2392-{claude,codex,gemini}.md`
> **Review artifacts:** populated after iteration-2 review dispatch

---

## Revision History

**v1 (2026-04-20, commit 5b4c347cd):** Claude self-review MINOR. Cross-review Codex MAJOR + Gemini MAJOR.
**Convergent v1 P1 findings now fixed in v2:**
- D1 `sha256:` namespace not enforced → **§Identity Contract** + tests (below)
- D3 AC-vs-test coverage gap → **§AC ↔ Test Map** + expanded TDD list
- D5 dependency statuses unverified → **§Dependency Matrix** with live-verified statuses
- D4 threat model missing → **§Threat Model** (below)
- D6 review metadata contradiction → header no longer cites speculative review paths; they are added only when artifacts exist
- Codex-specific: "cross-provider-optional" prose removed; repo policy restored
- Codex-specific: tier-3 local-cache exclusion now explicitly tested
- Codex-specific: scope creep removed — `docs/plans/README.md` update moved to the committing agent's side work, not part of deliverable

---

## Resource Intelligence Summary

### Existing repo code
- `scripts/data/document-index/provenance.py:82` — `merged_at` field (confirmed via Read 2026-04-20); baseline join surface.
- `scripts/data/document-index/phase-a-index.py:135-137` — legacy md5 prefix for `og_standards` (confirmed); coverage tool must tolerate.
- `scripts/knowledge/llm_wiki.py` — ingest surface (does not produce gap lists).
- Gap confirmed: `Glob "**/detect*gap*"` = 0 results.

### Standards
Not applicable.

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/index.md` — sampled; engineering CLAUDE.md declares `{title, tags, added, last_updated}` required (operating-model §8.1).
- `knowledge/wikis/marine-engineering/wiki/index.md` — uses `{domain, created, last_updated, page_count}`; different shape is blessed by §8.1.

### Documents consulted
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` §2/§3/§4/§7/§8.1 (all invoked by this plan).
- `docs/plans/2026-04-11-issue-2205-multi-machine-llm-wiki-resource-doc-intelligence-operating-model.md` — parent plan.
- `data/document-index/registry.yaml`, `mounted-source-registry.yaml`, `code-registry.yaml`, `online-resource-registry.yaml`, `dde-standards-inventory.yaml` — L2 inventory sources.

### Dependency Matrix (live-verified 2026-04-20)

| Issue | State | Relationship | Behavior if unshipped |
|---|---|---|---|
| #2205 | CLOSED (operating model) | authority | — always available |
| #2360 | OPEN status:plan-review | soft | tool tolerates missing `doc_key` via `status: identity-unresolved` classification |
| #2389 | OPEN status:plan-review | soft | tool tolerates missing `source_doc_key` by falling back to registry `doc_key` |
| #2365 | OPEN status:plan-review | overlap (design-code registry) | scope separation: #2392 emits gap list; #2365 promotes; no overlap |
| #2366 | OPEN status:plan-review | downstream consumer | no blocking |

### Gaps identified
- No existing tooling produces per-domain gap YAML.
- No standard for gap-entry shape (this plan defines it).
- `doc_key` coverage in wikis is partial (blocked by #2360); tool tolerates.

Distinct sources: **11** (exceeds ≥3 minimum).

---

## Identity Contract (§3 compliance)

All `doc_key` values read or emitted MUST conform to operating-model §3:
- Canonical: `sha256:<64-hex>`.
- Legacy `md5:<hex>` accepted for reads only (per §3 table); never written.
- Bare-hex (no prefix) rejected with clear error.
- Path-only identity forbidden — tool never synthesizes `doc_key` from path alone.

For sources lacking a known `doc_key`, tool emits `status: identity-unresolved` rather than fabricating one.

---

## Cross-Machine Tier Assignment (§7 compliance)

| Artifact | Path | Tier | Authority | Sync direction |
|---|---|---|---|---|
| L2 registries | `data/document-index/*.yaml` | 1 git-tracked | authoritative | — |
| L3 wiki pages | `knowledge/wikis/**/*.md` | 1 git-tracked | authoritative | — |
| Analysis reports (input) | `docs/reports/*.md` | 1 git-tracked | authoritative | — |
| Mounted sources (input paths only — not read by detector) | `/mnt/ace/**` via registry | 2 shared-mount | referenced | — |
| Gap YAML output | `docs/reports/wiki-coverage-gaps/*.yaml` | 1 git-tracked | authoritative | — |
| Summary output | `docs/reports/wiki-coverage-gaps/_summary.md` | 1 git-tracked | authoritative | — |

**Detector does not read `/mnt/ace/` directly** — it reads registry entries that describe mounted sources. Tier-3 local-cache is explicitly out of scope (detector never writes nor consults a local cache). Tier-3 exclusion has a test (`test_tier3_local_cache_excluded`).

---

## Threat Model

**Input surfaces:** YAML registries, markdown wiki/report files.
**Trust boundaries:** all inputs are git-tracked → committed content trusted; malformed frontmatter possible from human error.
**Mitigations:**
- Frontmatter parse errors → skip + log + emit gap entry with `status: frontmatter-parse-error`.
- YAML schema-mismatch in registry → abort with clear error (fail-closed).
- No filesystem writes outside `docs/reports/wiki-coverage-gaps/` (path allowlist check).
- Mount paths read as metadata strings only — no filesystem traversal of `/mnt/ace/`.

**Threat tests:**
- `test_malformed_frontmatter_does_not_crash`
- `test_schema_mismatch_fails_closed`
- `test_output_path_allowlist_enforced`

---

## AC ↔ Test Map

| Acceptance Criterion | Covering test(s) |
|---|---|
| All new tests pass | `pytest tests/knowledge/test_detect_wiki_gaps.py -v` (all below) |
| No regression | `pytest` at repo root (handled by CI) |
| E2E <5 min on current corpus | `test_runtime_budget_under_five_min` (fixture corpus ≥ real scale) |
| ≥1 gap YAML per domain on first run | `test_first_run_emits_per_domain_yaml` (fixture with 3 domains) |
| Weekly cron entry | `test_cron_config_parses_and_schedules_weekly` |
| Review artifacts posted | validated by reviewer's Retrieval Adequacy check; not a test but explicit reviewer-task |
| `sha256:` namespace enforced | `test_sha256_required`, `test_bare_hex_rejected`, `test_md5_read_only` |
| Tier-3 exclusion | `test_tier3_local_cache_excluded` |
| Threat model tests pass | listed under Threat Model |

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-20-issue-2392-wiki-coverage-gap-detector.md` |
| Tests | `tests/knowledge/test_detect_wiki_gaps.py` |
| Implementation | `scripts/knowledge/detect_wiki_gaps.py` |
| Config | `config/ai-tools/wiki-gap-detection.yaml` |
| Output | `docs/reports/wiki-coverage-gaps/*.yaml` + `_summary.md` |
| Cron wiring | `config/scheduled-tasks/schedule-tasks.yaml` (modify) |

Review artifact paths are intentionally omitted from header until artifacts exist.

---

## Deliverable

A `detect_wiki_gaps.py` CLI emitting per-domain gap YAML (+ summary) under `docs/reports/wiki-coverage-gaps/`, with strict `sha256:` identity handling, tier classification per operating-model §7, and fail-closed error semantics.

---

## Pseudocode

```
function detect_gaps(config):
    # Load inputs (tier-1 git-tracked only for detector consumption)
    l2_sources = load_and_validate_schema("data/document-index/registry.yaml")
               ∪ ... (other L2 yamls)
    analysis_reports = scan("docs/reports/*.md") filtered by L3-eligibility heuristic
    wiki_doc_keys = scan("knowledge/wikis/*/wiki/**/*.md") → set of sha256: doc_keys

    for each source:
        key = source.doc_key
        if key is null → identity_status = "identity-unresolved"
        elif key starts with "sha256:" → identity_status = "ok"
        elif key starts with "md5:" → identity_status = "legacy-read-only" (allowed)
        else → emit conformance warning; identity_status = "non-conforming"

        if key not in wiki_doc_keys and key is not tier-3 local-cache only:
            discipline = classify_discipline(source)
            tier = classify_tier(source)  # §7
            emit gap_entry with identity_status, tier, discipline

    write outputs atomically under path allowlist check
    write _summary.md
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/knowledge/detect_wiki_gaps.py` | Main implementation |
| Create | `tests/knowledge/test_detect_wiki_gaps.py` | TDD suite |
| Create | `config/ai-tools/wiki-gap-detection.yaml` | Discipline→wiki-domain mapping |
| Create | `docs/reports/wiki-coverage-gaps/README.md` | Output format reference |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | Weekly schedule |

---

## TDD Test List

| Test | Verifies |
|---|---|
| test_sha256_required | bare-hex input produces clear error |
| test_md5_legacy_read_only | md5: keys accepted for reads, never written |
| test_bare_hex_rejected | no-prefix input rejected with clear message |
| test_path_only_identity_forbidden | detector never synthesizes doc_key from path |
| test_known_source_not_in_wiki_surfaces | source w/ doc_key, no wiki ref → gap emitted |
| test_wiki_covered_source_excluded | source referenced by wiki → not a gap |
| test_missing_doc_key_marked_identity_unresolved | null key → `status: identity-unresolved` |
| test_discipline_classification | naval-architecture tag → routes to naval file |
| test_tier_classification_git_tracked | L2 yaml entry → tier 1 |
| test_tier_classification_shared_mount | `/mnt/ace/` source → tier 2 |
| test_tier3_local_cache_excluded | local-cache-only source → detector never considers it |
| test_dry_run_writes_nothing | `--dry-run` produces no file writes |
| test_idempotent_rerun | same input → byte-identical YAML |
| test_analysis_report_eligibility | L3-eligibility filter works correctly |
| test_runtime_budget_under_five_min | fixture corpus completes under budget |
| test_first_run_emits_per_domain_yaml | ≥1 YAML per domain in fixture |
| test_cron_config_parses_and_schedules_weekly | cron entry validates against schedule schema |
| test_malformed_frontmatter_does_not_crash | parse error → skip + log, not crash |
| test_schema_mismatch_fails_closed | bad registry → abort with clear error |
| test_output_path_allowlist_enforced | write outside allowlist → refused |

---

## Acceptance Criteria

- [ ] All 20 tests pass: `uv run pytest tests/knowledge/test_detect_wiki_gaps.py -v`
- [ ] No regression at repo root
- [ ] E2E run on current corpus completes <5 min (measured)
- [ ] Produces ≥1 gap YAML per wiki domain on first real run
- [ ] Weekly cron entry merged + validated by test
- [ ] Operating-model §3 (identity) enforced: all test_sha256_*/test_md5_*/test_bare_hex_* pass
- [ ] Operating-model §7 (tier) enforced: all test_tier_* pass
- [ ] Threat model tests pass

---

## Adversarial Review Summary

| Provider | Verdict | Key findings | Artifact |
|---|---|---|---|
| Claude v1 | MINOR | self-review, 3 fixes | `2026-04-20-plan-2392-claude.md` |
| Codex v1 | MAJOR | sha256, AC-test gap, policy, tier-3, deps, threat model, scope | `2026-04-20-plan-2392-codex.md` |
| Gemini v1 | MAJOR | sha256, unverified claims, threat, perf test | `2026-04-20-plan-2392-gemini.md` |
| Claude v2 | PENDING | — | — |
| Codex v2 | PENDING | — | — |
| Gemini v2 | PENDING | — | — |

---

## Risks and Open Questions

- **Risk:** §3 identity enforcement may surface large volumes of `identity-unresolved` entries until #2360 completes. Mitigation: counts surfaced in `_summary.md`; not a blocker.
- **Risk:** L3-eligibility heuristic is subjective. Mitigation: config-driven + first-run user calibration.
- **Open:** Should analysis-report filter include `docs/reports/weekly/*` or only top-level? Plan default: top-level only; weekly reports handled by existing #2089.

---

## Complexity: T2

New script + config + tests + cron wiring; no existing file significantly modified.
