# Online Resource Registry Refresh Audit — 2026-05-03

> **Audit Issue:** [#2593](https://github.com/vamseeachanta/workspace-hub/issues/2593) (W2-D)
> **Audit Plan:** `docs/plans/2026-05-02-issue-2593-llm-wiki-W2D-online-resource-registry-refresh.md`
> **Snapshot Date:** 2026-05-03 (registry generated 2026-04-02T04:28:12; audit verifies state ~31 days later)
> **Scope:** `data/document-index/online-resource-registry.yaml` — schema, freshness, missing 2025-2026 high-value standards revisions, W1 cross-link verification
> **Deliverables:** this audit report + proposed-patch sidecar at `data/document-index/online-resource-registry-patch-2026-05-03.yaml` (≤20 entries) + audit-time test at `tests/audits/test_online_resource_registry_audit.py`
> **NOT modified by this audit:** the registry yaml itself.

---

## Methodology

1. **Frontmatter parity** — compare `total_entries` declared in registry frontmatter against `len(entries)` on the body.
2. **Field inventory** — collect the union of fields present across all entries; compare against the schema-gap list called out in the W2-D plan (`revision`, `superseded_by`, `code_id`, `last_verified`).
3. **Stale signal** — `last_checked` distribution; entries last checked >30 days ago are candidates for re-verification.
4. **W1 cross-reference pass** — enumerate the 11 publisher URLs the W1-A (#2586) and W1-D (#2589) plans propose; resolve each against registry entries by URL string match; classify as `present-correct`, `present-wrong-url` (URL-mismatch), or `missing`.
5. **High-value 2025-2026 revisions pass** — confirm presence/absence of the 4 candidates the W2-D plan §Resource Intel enumerated (API RP 2A-WSD R2025, DNV-ST-F101 rename, ISO 19901-7 FDIS, MARPOL Annex VI 2026 ECA) plus 5 additional candidates surfaced during this audit.
6. **Live URL spot-check** — WebFetch sample of 4 publisher URLs to detect dead/redirected/login-walled pages; classify as `200-resolves`, `200-but-page-not-found`, `redirect-to-auth`, or `error`.

All findings are point-in-time as of the snapshot date. Verification commands are recorded inline so a re-runner can reproduce.

---

## Section 1 — Schema Gap Findings

The registry has **zero** `revision`, `superseded_by`, `code_id`, and `last_verified` fields across all 248 entries.

**Verification:**
```
$ grep -E "^[[:space:]]*revision:" data/document-index/online-resource-registry.yaml | wc -l
0
```

**Field inventory** (verified 2026-05-03 via `yaml.safe_load` + union of all entry keys):
```
['domain', 'download_status', 'id', 'last_checked', 'local_backup_path',
 'name', 'notes', 'relevance_score', 'source_catalog', 'type', 'url']
```

| Field | Schema-gap status | Recommendation |
|---|---|---|
| `revision` | MISSING — zero entries set it | ADD as optional free-text per W2-D MINOR-3 (permissive regex: date-like OR `Nth Edition` OR `(R\d{4})` OR `:YYYY`) |
| `code_id` | MISSING — zero entries set it | ADD as optional, allowing standards-portal entries to link to `standards-transfer-ledger.yaml` IDs (resolves the #2471 routing decision's portability) |
| `superseded_by` | MISSING — zero entries set it | RECOMMEND-ONLY in this audit; do NOT add to patch (no consumer reads it today; would replicate the M1 split-brain pattern). Defer to a follow-up issue. |
| `last_verified` | INTENTIONALLY NOT ADDED | Per W2-D MAJOR-1 fix: reuse the existing `last_checked` field; do NOT introduce a parallel timestamp field. |

**Schema-gap impact:** entries pointing at the publisher's *current* revision look identical to entries pointing at a *retired* revision. The first-class consequence is that calc-citation-contract resolution (`.claude/rules/calc-citation-contract.md`) cannot reliably tie a registry entry to a wiki page revision string.

---

## Section 2 — Frontmatter Drift

The frontmatter declares `total_entries: 247` while the body has 248 entries (a 1-entry drift).

**Verification:**
```
$ python3 -c "import yaml; r=yaml.safe_load(open('data/document-index/online-resource-registry.yaml')); print(r['total_entries'], len(r['entries']))"
247 248
```

**Cause (likely):** an entry was appended without `scripts/data/build-online-resource-registry.py` being re-run to regenerate the frontmatter summary block.

**Fix scope:** out of scope for W2-D (the plan explicitly defers this). The registry-generation script must be re-run; this audit records the drift.

**Duplicate URL finding (NEW — beyond §Resource Intel):** the URL `https://opensees.berkeley.edu/` appears twice across the 248 entries (247 unique URLs + 1 dup). The duplicate IDs are unique, but the canonical URL is shared. Recommend dedup pass.

---

## Section 3 — Freshness / `last_checked` Distribution

96% of entries share a single regeneration date.

**Verification:**
```
$ grep -E "^[[:space:]]*last_checked:" data/document-index/online-resource-registry.yaml | sort | uniq -c
    238   last_checked: '2026-04-02'
      9   last_checked: '2026-04-16'
      1   last_checked: '2026-04-03'
```

The registry has not been per-entry re-verified since its 2026-04-02 mass regeneration. This is expected for a build-time-generated registry, but it means `last_checked` does NOT carry signal about whether the URL still resolves — which motivates the audit-time `test_url_resolves_sample` test (audit-marked, not in default pytest run).

---

## Section 4 — W1 Cross-Reference Pass (publisher URLs from W1-A / W1-D)

Eleven publisher URLs proposed by W1-A (#2586, API standards) and W1-D (#2589, naval-architecture concept pages). Each row is keyed by `code_id` and resolved against registry entries by URL string match.

| `code_id` | W1 publisher URL (canonical) | Registry status | Class |
|---|---|---|---|
| API-RP-2A-WSD | https://store.accuristech.com/standards/api-rp-2a-wsd-r2025 | absent | **MISSING** |
| API-STD-2RD | https://www.api.org/products-and-services/standards | absent (registry has the announcements landing, not 2RD-specific) | **MISSING** |
| API-RP-2SK | https://www.api.org/products-and-services/standards/important-standards-announcements/standard-2sk | present in registry as `api_org_products_and_services_standards_important_standards__839ba5` BUT URL is a 404 (live-fetched 2026-05-03 — see Section 6) | **PRESENT-WRONG-URL (DEAD)** |
| API-RP-2GEO | https://www.api.org/products-and-services/standards/important-standards-announcements/standard-2geo | absent | **MISSING** |
| API-RP-2MET | https://www.api.org/products-and-services/standards/important-standards-announcements/standard-2met | absent | **MISSING** |
| API-RP-16Q | https://www.api.org/products-and-services/standards/important-standards-announcements/standard-16q | absent | **MISSING** |
| API-RP-17B | https://www.api.org/products-and-services/standards/important-standards-announcements/standard-17b | absent | **MISSING** |
| API-RP-1111 | https://www.api.org/products-and-services/standards/important-standards-announcements/standard-1111 | absent | **MISSING** |
| ITTC-RP-7.5 | https://ittc.info/about-ittc/recommended-procedures/ | absent | **MISSING** |
| SNAME-T&R | https://www.sname.org/pubs/journals | absent | **MISSING** |
| ABS-Rules-MOU | https://ww2.eagle.org/en/rules-and-resources/rules-and-guides.html | absent | **MISSING** |

**Summary:** 10 of 11 W1-proposed URLs are absent from the registry; 1 is present at a now-dead URL. Caveat on the API-RP-2SK / API-RP-2GEO / API-RP-2MET / API-RP-16Q / API-RP-17B / API-RP-1111 announcement-portal URLs: based on Section 6 spot-check, the `important-standards-announcements/<standard>` path pattern returns 404 for at least one tested member. The *recommended* canonical URL for these patches is the publisher's standard search portal (e.g., `https://www.api.org/products-and-services/standards/whats-new`) until an authoritative per-standard page is identified, or omit the URL entirely and cite the standards-transfer-ledger ID.

---

## Section 5 — High-Value 2025-2026 Revisions Pass

The W2-D plan's §Resource Intel enumerated 4 high-value 2025-2026 revisions that the registry is missing. This audit confirms all 4 plus surfaces 5 additional candidates.

### 5.1 Plan-enumerated candidates (4)

| Standard | Status as of 2026-05-03 | Registry presence |
|---|---|---|
| API RP 2A-WSD 22nd Ed (R2025 reaffirmation) | reaffirmation effective 2025; AccurisTech-listed | absent |
| DNV-ST-F101 (renamed from DNV-OS-F101) | Edition 2021-08, Amended 2021-12 (verified live 2026-05-03 — see §6) | absent (registry has only the legacy `dnv_standards_explorer` portal pointer) |
| ISO 19901-7 (FDIS revision in progress) | publisher page returned 403 in spot-check (likely Cloudflare anti-bot) — defer to web-search citation | absent |
| MARPOL Annex VI 2026 ECA amendments | Canadian Arctic + Norwegian Sea ECA effective 2026-03-01; NE Atlantic ECA expected MEPC 84 April 2026 | absent (registry has 1 regulatory entry — IMO GISIS portal — not the Annex VI document) |

### 5.2 NEW candidates surfaced by this audit (5 — meets W2-D Acceptance Criterion ≥5)

| # | Standard / resource | Why it's high-value | Source |
|---|---|---|---|
| 5 | DNV-RP-C203 (Fatigue Design of Offshore Steel Structures) — current Edition 2021-09 | Cited by `digitalmodel/src/digitalmodel/orcaflex/` fatigue modules; no registry entry | dnv.com/energy/standards-guidelines/dnv-rp-c203 |
| 6 | DNV-OS-E301 (Position Mooring) — current Edition 2024-07 | The pilot-cited standard in `.claude/rules/calc-citation-contract.md`; the wiki page at `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` exists but the registry has no per-document entry pointing at the publisher revision | dnv.com/energy/standards-guidelines/dnv-os-e301 |
| 7 | OCIMF MEG4 (Mooring Equipment Guidelines, 4th Edition, 2018) — superseded by OCIMF MEG5 in 2025-2026 transition | OCIMF Tandem Mooring wiki page added per #2559 chain (`knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md`); registry has no OCIMF entry | ocimf.org/document-libraries |
| 8 | API RP 2T (Recommended Practice for Planning, Designing, and Constructing Tension Leg Platforms — 4th Edition, 2025 announced) | TLP design reference; cited in digitalmodel TLP modules | api.org/products-and-services/standards |
| 9 | IMO MEPC.391(81) — Guidelines on Lifecycle GHG Intensity of Marine Fuels (LCA Guidelines), adopted 2025-03 | Required for IMO Net-Zero Framework compliance taking effect 2027; registry has no IMO/MEPC entries beyond GISIS | imo.org/en/OurWork/Environment |

**Audit finding:** the 5 NEW candidates above, combined with the 4 plan-enumerated candidates, give 9 missing high-value entries. The W2-D Acceptance Criterion required either ≥10 stale (with revision-string evidence) OR ≥5 new missing-entry findings — this audit satisfies the second bound.

---

## Section 6 — Live URL Spot-Check (4 of 248 entries)

Sample-verified via WebFetch on 2026-05-03. Selection biased toward standard-portal entries (highest stakes for citation contract).

| Entry id | URL | Result | Class |
|---|---|---|---|
| `dnv_standards_explorer` | https://standards.dnv.com/explorer/ | 302 redirect to maritime.dnv.com authentication portal | **REDIRECT-TO-AUTH** (login-walled; archive-mode browsing no longer works) |
| `api_org_products_and_services_standards_important_standards__839ba5` | https://www.api.org/products-and-services/standards/important-standards-announcements/standard-2sk | 200 OK but page is API's "page not found" template | **200-BUT-PAGE-NOT-FOUND** (effectively dead) |
| (W2-D candidate URL) | https://www.dnv.com/energy/standards-guidelines/dnv-st-f101-submarine-pipeline-systems/ | 200 OK; page healthy; Edition 2021-08, Amended 2021-12 | **200-RESOLVES** |
| `api_org_products_and_services_standards_66556d` | https://www.api.org/products-and-services/standards | 200 OK; active page, title "Standards" | **200-RESOLVES** |
| (W2-D candidate URL) | https://www.iso.org/standard/59298.html | 403 Forbidden | **ERROR (likely Cloudflare anti-bot, not absent)** |

**Spot-check summary:** 2/5 endpoints return effectively dead content (1 login-walled, 1 silent 404); 2/5 are healthy; 1/5 is anti-bot blocked. The two effectively-dead surfaces are exactly the surfaces the calc-citation-contract resolver would consult — high stakes for citation defensibility.

---

## Section 7 — Cumulative Findings vs Acceptance Criteria

W2-D Acceptance Criterion #3 requires `≥10 stale entries (with revision-string evidence beyond §Resource Intel) OR ≥5 NEW missing high-value entries beyond the 4 in §Resource Intel`.

This audit surfaces:
- **5 NEW missing high-value entries** (Section 5.2 rows 5-9) — satisfies the ≥5-NEW bound.
- **2 schema-gap classes documented with field-inventory evidence** (Section 1 + Section 2 frontmatter drift + duplicate-URL finding).
- **10 of 11 W1-cross-reference URLs absent or pointing at dead endpoints** (Section 4) — directly informs the patch sidecar.
- **2 of 5 spot-checked URLs effectively dead** (Section 6) — independent stale signal.

Acceptance Criterion #3 met: ≥5 NEW missing high-value entries. The patch sidecar (`data/document-index/online-resource-registry-patch-2026-05-03.yaml`) proposes ≤20 entries drawn from this finding set.

---

## Section 8 — Recommendations (NOT applied by this audit)

The following are explicitly OUT of W2-D scope; this audit records them for the implementation issue that consumes the patch:

1. **Re-run `scripts/data/build-online-resource-registry.py`** to regenerate the frontmatter summary block (resolves the 247-vs-248 drift).
2. **Dedup `https://opensees.berkeley.edu/`** — keep one entry, archive the other.
3. **Add `code_id` field schema migration** — optional field on standards-portal entries; bridges to `standards-transfer-ledger.yaml` per the #2471 routing principle (CSA-Z276-only as sanctioned; generalization deferred per `feedback_plan_past_tense_artifact_claims.md` polarity).
4. **Add `revision` field schema migration** — optional free-text; permissive grammar.
5. **Re-verify the DNV standards-explorer landing** — login-walled now; either note the auth requirement in registry `notes` or replace the URL with the per-standard page (`dnv.com/energy/standards-guidelines/<doc-id>`).
6. **Replace the dead `api_org_products_and_services_standards_important_standards__839ba5` URL** with the active API standards landing or omit the URL entirely.
7. **`superseded_by` schema field** — defer to a separate follow-up issue with explicit consumer wiring, per W2-D MINOR risk-resolution stance.

---

## Verification Reproducibility

All Section 1-3 findings can be re-derived offline via the included audit-time test (`tests/audits/test_online_resource_registry_audit.py`):
- `test_revision_field_zero_count_today` — Section 1
- `test_frontmatter_total_entries_drift_documented` — Section 2
- `test_no_duplicate_ids` — Section 2 ID uniqueness
- `test_every_url_well_formed` — Section 6 well-formedness pre-check
- `test_proposed_patch_required_fields` — patch sidecar contract
- `test_proposed_patch_no_legacy_unflagged` — patch sidecar 5-year window
- `test_url_resolves_sample` (audit-marked, opt-in via `-m audit`) — Section 6 live network sample

Section 4-6 findings are reproduced via the WebFetch invocations recorded inline above and the `test_url_resolves_sample` opt-in test.
