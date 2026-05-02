# Plan: audit(data) — online-resource-registry refresh + 2025-2026 standards-revision sweep (W2-D)

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-05-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2593
> **Review artifacts:** scripts/review/results/2026-05-02-plan-W2D-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `data/document-index/online-resource-registry.yaml` — 3,423 lines, 248 entries, last regenerated 2026-04-02 per `generated:` frontmatter timestamp.
- Found: `scripts/data/build-online-resource-registry.py` — generates the registry from upstream catalogs.
- Found: `scripts/data/connect-web-resources-to-registry.py` — links web resources into the registry.
- Found: `scripts/data/generate-domain-resource-views.py` — derives per-domain views.
- Found: `scripts/document-intelligence/cross-reference-registries.py` — cross-references this registry against `standards-transfer-ledger.yaml` and `code-registry.yaml`.
- Found: `tests/data/test_build_online_resource_registry.py` — existing build-time test (the W2-D test will be a separate audit-time test, not a duplicate).
- Gap: there is NO `revision:` field on any entry (`grep -E "^[[:space:]]*revision:" … | wc -l` returns 0) — the registry currently tracks `last_checked` and `download_status` but not the publisher revision string. This is the largest schema gap.
- Gap: there is NO `superseded_by` or `superseded_or_legacy` annotation — no way to mark an entry whose revision a publisher has retired.
- Gap: there is NO `code_id` field linking standards-portal entries to `standards-transfer-ledger.yaml` / wiki `standards/<code-id>.md` — duplicates the standards-page issue called out in #2471 routing decision.

### Standards
| Standard | Status | Source |
|---|---|---|
| API RP 2A-WSD 22nd ed (R2025 reaffirmation) | gap — registry has only `api_org_products_and_services_standards*` portal entries, no per-document revision tracking | api.org publications catalog 2025 (web search) |
| DNV-ST-F101 (renamed from DNV-OS-F101) | gap — registry shows only the legacy `dnv_standards_explorer` portal pointer | dnv.com/energy/standards-guidelines/dnv-st-f101 |
| ISO 19901-7:2013 (under FDIS revision toward 2025-2026) | gap — no entry; only API RP 2SK portal pointer present, which is the legacy basis document | iso.org/standard/59298 |
| MARPOL Annex VI (Canadian Arctic + Norwegian Sea ECA effective 2026-03-01; NE Atlantic ECA expected MEPC 84 April 2026; 0.10% m/m sulphur enforcement 2027-03-01) | gap — no entry; relevant for `domain: regulatory` (registry has 1 regulatory entry today) | imo.org/en/mediacentre/meetingsummaries/pages/preview-mepc-84.aspx |

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` — recently added per #2559 chain; example of the standards-page routing #2471 sanctioned. Demonstrates that a wiki page can outlive a registry entry, so the registry must point at the standards page, not just the publisher portal.
- No relevant wiki pages exist for API RP 2A, DNV-ST-F101, ISO 19901-7, MARPOL Annex VI — these are exactly the targets W2-D's sister plans (#2586 API, #2589 naval-arch) propose to add. W2-D's job is to make sure the registry knows about them.

### Documents consulted
- `data/document-index/online-resource-registry.yaml` — 248 entries, schema fields: `id, url, name, type, domain, local_backup_path, download_status, last_checked, relevance_score, source_catalog, notes`.
- `data/document-index/standards-transfer-ledger.yaml` — referenced by `cross-reference-registries.py`; W2-D's audit will consume this to identify standards that are in the ledger but missing from the online-resource-registry.
- Issue #2540 — OPEN — "epic(llm-wiki): overnight Elements corpus planning wave after #2536" — parent epic for the W1/W2 wave.
- Issue #2586 — OPEN — "feat(llm-wiki): bounded API standards summary promotion to engineering-standards wiki (W1-A)" — proposes new API standards wiki pages; W2-D verifies each gets a registry entry.
- Issue #2587 — OPEN — "feat(llm-wiki): asset-management wiki topical scaffold + scope boundary (W1-B)".
- Issue #2588 — OPEN — "audit(llm-wiki): engineering wiki gap audit + prioritized backfill sequence (W1-C)".
- Issue #2589 — OPEN — "feat(llm-wiki): naval-architecture wiki topical expansion — 10 core concept pages (W1-D)".
- `docs/plans/2026-04-11-issue-2136-intelligence-accessibility-registry-with-machine-reachability.md` — adjacent registry plan; design pattern for "audit + small patch PR" used here.
- `docs/plans/2026-04-17-issue-2307-accessibility-registry-declaration.md` — same family.
- Recent commit `24eccfc49 fix(registry): update 8 dead URLs, archive 1 defunct resource (#2302)` — established precedent for bounded URL-fix PRs against this file.

### Gaps identified
- No publisher-revision tracking on registry entries (schema gap).
- No supersession marker; entries that point at retired revisions look identical to entries pointing at current revisions.
- No coupling between registry entries and the wiki `standards/<code-id>.md` pages that #2471 sanctioned.
- No automated audit harness verifying URLs at audit-time (build-time tests in `tests/data/` cover registry construction, not freshness of the URLs themselves).
- ≥4 high-value 2025-2026 standards revisions identified by web search are absent from the registry (API RP 2A-WSD R2025, DNV-ST-F101 rename of DNV-OS-F101, ISO 19901-7 FDIS, MARPOL Annex VI 2026 ECA amendments).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-02 via `gh issue view --json state,title`):
- `#2540` — OPEN — "epic(llm-wiki): overnight Elements corpus planning wave after #2536"
- `#2586` — OPEN — "feat(llm-wiki): bounded API standards summary promotion to engineering-standards wiki (W1-A)"
- `#2587` — OPEN — "feat(llm-wiki): asset-management wiki topical scaffold + scope boundary (W1-B)"
- `#2588` — OPEN — "audit(llm-wiki): engineering wiki gap audit + prioritized backfill sequence (W1-C)"
- `#2589` — OPEN — "feat(llm-wiki): naval-architecture wiki topical expansion — 10 core concept pages (W1-D)"

**File existence** (`ls` 2026-05-02):
- EXISTS: `data/document-index/online-resource-registry.yaml` (3,423 lines, 248 entries)
- EXISTS: `scripts/data/build-online-resource-registry.py`
- EXISTS: `scripts/document-intelligence/cross-reference-registries.py`
- EXISTS: `tests/data/test_build_online_resource_registry.py`
- MISSING (new — this plan creates): `docs/audits/2026-05-02-online-resource-registry-refresh.md`
- MISSING (new — this plan creates): `data/document-index/online-resource-registry.proposed-patch.yaml` (proposed patch sidecar, NOT the registry itself)
- MISSING (new — this plan creates): `tests/data/test_online_resource_registry.py`
- MISSING (no audits dir today): `docs/audits/` — plan will create the directory.

**Line excerpts** (`head -60 data/document-index/online-resource-registry.yaml`):
```
generated: '2026-04-02T04:28:12'
total_entries: 247
summary:
  by_type:
    tool: 97
    github_repo: 56
    data_api: 31
    paper: 31
    tutorial: 15
    standard_portal: 9
    professional_body: 4
    course_material: 3
    library: 1
  by_domain:
    naval_architecture: 40
    structural: 30
    oil_and_gas: 29
    hydrodynamics: 28
    ...
  by_download_status:
    not_started: 221
    downloaded: 17
    reference_only: 9
entries:
- id: awesome_mcp_servers
  url: https://github.com/punkpeye/awesome-mcp-servers
  ...
  last_checked: '2026-04-02'
  relevance_score: 5
```
Note frontmatter says `total_entries: 247` while `grep -c "^- id:" … = 248` — a 1-entry drift between frontmatter and body, itself an audit finding.

**Last-checked distribution** (`grep -E "^[[:space:]]*last_checked:" … | sort | uniq -c`):
```
    238   last_checked: '2026-04-02'
      9   last_checked: '2026-04-16'
      1   last_checked: '2026-04-03'
```
96% of entries share a single regeneration date — the registry has not been touched per-entry since.

**Revision-field gap proof** (`grep -c "^[[:space:]]*revision:" … = 0`): no entry tracks publisher revision.

**Recent history** (`git log --oneline data/document-index/online-resource-registry.yaml | head -4`):
```
24eccfc49 fix(registry): update 8 dead URLs, archive 1 defunct resource (#2302)
135922b96 docs: add everything-claude-code to online resource registry
bdca843ef feat(doc-intel): connect OrcaWave/OrcaFlex web resources to registry (#1580)
eee5098cc feat(doc-intel): unified online resource registry — merge 7 catalogs (#1576)
```
Last targeted edit was #2302 — the bounded-patch precedent W2-D follows.

**Web-search evidence (2025-2026 revisions)** verified 2026-05-02:
- API RP 2A-WSD 22nd Edition Reaffirmed (R2025) — accuristech / nimonik / api.org 2025 publications catalog
- DNV-ST-F101 (renamed from DNV-OS-F101) — dnv.com/energy/standards-guidelines/dnv-st-f101-submarine-pipeline-systems
- ISO 19901-7:2013 confirmed 2018, FDIS revision in progress — iso.org/standard/59298
- MARPOL Annex VI: Canadian Arctic + Norwegian Sea ECA effective 2026-03-01; NE Atlantic ECA expected MEPC 84 April 2026; 0.10% m/m sulphur enforcement 2027-03-01 — imo.org/en/mediacentre/meetingsummaries/pages/preview-mepc-84.aspx; clydeco.com 2026 MARPOL Annex VI insight

**Source count: 11 distinct sources** (registry file, 4 helper scripts, 1 existing test, 5 issues, 1 commit, 1 sister plan, 4 web-search publishers — well above the ≥3 minimum.)

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-02-issue-2593-llm-wiki-W2D-online-resource-registry-refresh.md` |
| Audit report (deliverable A) | `docs/audits/2026-05-02-online-resource-registry-refresh.md` |
| Proposed patch (deliverable B, NOT applied to registry) | `data/document-index/online-resource-registry.proposed-patch.yaml` |
| Audit-time test | `tests/data/test_online_resource_registry.py` |
| Index update | `docs/plans/README.md` |
| Plan review — Claude | `scripts/review/results/2026-05-02-plan-W2D-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-02-plan-W2D-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-02-plan-W2D-gemini.md` |

---

## Deliverable

A bounded audit report plus a proposed (not-applied) ≤20-entry patch to `online-resource-registry.yaml` that will identify stale entries (revision drift since 2026-04-02) and add the highest-value 2025-2026 standards revisions, ungated by a wholesale rewrite. The registry yaml itself will NOT be modified by this plan; the implementation issue that follows W2-D will apply the patch.

---

## Pseudocode

```
function audit_online_resource_registry():
    load registry = yaml.safe_load(online-resource-registry.yaml)
    assert registry["total_entries"] == count(registry["entries"])  # frontmatter drift check

    stale_entries = []
    missing_entries = []
    schema_gaps = []

    # 1. Stale-revision pass (publisher-canonical pages only, sample to avoid bulk scrape)
    for entry in registry["entries"] where type == "standard_portal":
        publisher_current = WebFetch(entry.url, "extract latest revision string and date")
        if entry has no `revision` field:
            schema_gaps.append((entry.id, "no revision field"))
        elif entry.revision < publisher_current.revision:
            stale_entries.append((entry.id, entry.revision, publisher_current.revision))

    # 2. Missing high-value pass (cross-reference WebSearch findings)
    high_value_2025_2026 = [
        ("API RP 2A-WSD R2025", "api.org/standards/api-rp-2a-wsd"),
        ("DNV-ST-F101 (renamed from DNV-OS-F101)", "dnv.com/.../dnv-st-f101"),
        ("ISO 19901-7 FDIS", "iso.org/standard/59298"),
        ("MARPOL Annex VI 2026 ECA amendments", "imo.org/.../mepc-84"),
        ...up to ~10 candidates...
    ]
    for candidate in high_value_2025_2026:
        if candidate.url not in [e.url for e in registry["entries"]]:
            missing_entries.append(candidate)

    # 3. W1 cross-reference pass
    for plan in [#2586, #2587, #2589]:
        for standards_page in plan.proposed_pages:
            if standards_page.publisher_url not in registry:
                missing_entries.append((standards_page, "referenced by W1 plan"))

    # 4. Schema-gap pass (single output)
    schema_gaps.append("no `revision` field on any entry")
    schema_gaps.append("no `superseded_by` field")
    schema_gaps.append("no `code_id` linkage to standards-transfer-ledger.yaml")

    write_audit_report(stale_entries, missing_entries, schema_gaps)
    write_proposed_patch(top_20(stale_entries + missing_entries))
```

The proposed-patch file is a YAML sidecar (NOT a unified diff and NOT applied) so reviewers can inspect entry-by-entry before the implementation PR consumes it.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/audits/2026-05-02-online-resource-registry-refresh.md` | audit report (deliverable A); creates `docs/audits/` dir |
| Create | `data/document-index/online-resource-registry.proposed-patch.yaml` | proposed ≤20-entry patch sidecar (deliverable B); registry yaml itself is NOT modified |
| Create | `tests/data/test_online_resource_registry.py` | audit-time tests (schema, URL resolution sample, no duplicate ids) |
| Update | `docs/plans/README.md` | add this plan to the plan index |

Explicitly NOT modified by this plan: `data/document-index/online-resource-registry.yaml`. The implementation issue that follows W2-D will consume the patch.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_registry_yaml_loads` | registry parses as YAML | `online-resource-registry.yaml` | `dict` with `entries` list |
| `test_frontmatter_total_entries_matches_body` | `total_entries` matches `len(entries)` | registry dict | assertion holds (will FAIL today; documents the 247-vs-248 drift) |
| `test_no_duplicate_ids` | every `id` is unique | registry entries | no duplicates |
| `test_every_url_well_formed` | every `url` parses as a URL | registry entries | `urllib.parse.urlparse` succeeds, scheme in `{http, https}` |
| `test_revision_field_parseable_when_present` | when `revision` is added by patch, it parses to a date or matches a known publisher pattern (e.g., `R2025`, `22nd Edition`) | proposed-patch entries | regex match against publisher-revision grammar |
| `test_url_resolves_sample` | sample of 10 entries (deterministic, seeded by hash) returns 200 OR 3xx via WebFetch at audit-time | 10 sampled entries | unverifiable URLs flagged as `flaky`, NOT `missing` (per Risks below) |
| `test_proposed_patch_has_required_fields` | every patch entry has `id`, `url`, `name`, `type`, `domain`, `revision`, `last_verified`, `code_id` (when applicable) | patch yaml | required fields present |
| `test_no_legacy_entry_older_than_5_years_without_annotation` | acceptance criterion enforcement | merged-view registry | every entry whose `revision` parses to >5 years old has `superseded_or_legacy: true` |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest tests/data/test_online_resource_registry.py -v` (excluding `test_frontmatter_total_entries_matches_body` which is allowed to fail and is documented as the rationale for fixing frontmatter in a follow-up PR).
- [ ] No regression: `uv run pytest tests/data/` passes (existing `test_build_online_resource_registry.py` continues to pass).
- [ ] Audit report at `docs/audits/2026-05-02-online-resource-registry-refresh.md` identifies **≥10 stale entries OR ≥5 missing high-value entries** (whichever bound is reached first; need not satisfy both).
- [ ] Proposed-patch file `data/document-index/online-resource-registry.proposed-patch.yaml` parses against the existing registry validators when notionally merged (validated via `scripts/data/build-online-resource-registry.py --dry-run` if that flag exists, or a temp-file merge in the test).
- [ ] No proposed-patch entry has a `revision` parseable to >5 years before 2026-05-02 without an explicit `superseded_or_legacy: true` annotation.
- [ ] `docs/plans/README.md` updated with this plan.
- [ ] Review artifacts posted to `scripts/review/results/2026-05-02-plan-W2D-{claude,codex,gemini}.md`.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | (pending) | (filled after review) |
| Codex | (pending) | (filled after review) |
| Gemini | (pending) | (filled after review) |

**Overall result:** PASS / FAIL (re-draft required) — to be filled.

Revisions made based on review:
- (none yet — initial draft)

---

## Risks and Open Questions

- **Risk:** WebFetch flakiness during audit — publisher pages return 503 or apply rate limits. **Mitigation:** cache responses to a tmp dir; entries that cannot be re-verified are flagged as `verification_status: flaky` in the audit report, NOT mislabeled as `missing`. The audit report distinguishes these classes explicitly.
- **Risk:** Revision-string format drifts across publishers (e.g., API uses `22nd Edition (R2025)`, DNV uses `2021-08`, ISO uses `:2013`). **Mitigation:** the `revision` field is free-text, and `test_revision_field_parseable_when_present` uses a permissive regex (date-like OR `Nth Edition` OR `(R\d{4})` OR `:YYYY`). Strict normalization is deferred to a follow-up.
- **Risk:** Entries used by build pipelines (`scripts/data/generate-domain-resource-views.py`, `scripts/document-intelligence/cross-reference-registries.py`) may break if reformatted. **Mitigation:** patch is a *sidecar*, not applied; the implementation issue that consumes the patch will run those scripts before/after as a regression check.
- **Risk:** The 247-vs-248 frontmatter drift may indicate a deeper construction bug. **Mitigation:** audit report records it as a finding; W2-D does not attempt to fix it (out of scope).
- **Risk:** `last_verified` is a NEW field; existing tooling does not consume it. **Mitigation:** `last_verified` is added only to patch-introduced entries; existing entries continue to use `last_checked`. A follow-up issue will harmonize the two field names.
- **Open:** Should the registry be split per-publisher (`API.yaml`, `DNV.yaml`, `ISO.yaml`, …) for review-friendliness, or kept monolithic? **Defer to user during plan-approval.** W2-D assumes monolithic for now.
- **Open:** Should `code_id` be added to standards-portal entries to link to `standards-transfer-ledger.yaml` per #2471 routing? **Defer to user.** W2-D will recommend it in the audit report but not require it in the patch.

---

## Complexity: T2

**T2** — bounded delta on a 248-entry registry, three new files (audit report, proposed-patch sidecar, audit-time test), one updated index file, no modification of the registry yaml itself, ≥3 distinct sources cited, requires multi-publisher web-search verification but no production-pipeline changes. Not T1 because there are multiple test cases and a new directory (`docs/audits/`); not T3 because there is no schema migration of existing entries, no breaking change to consumers, and the patch is bounded to ≤20 entries.
