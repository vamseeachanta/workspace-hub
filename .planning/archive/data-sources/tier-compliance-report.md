# Data Residence Tier Compliance Report

> WRK-253 | Audit date: 2026-02-24 | Policy: docs/DATA_RESIDENCE_POLICY.md (ADR-004)

## Scope

Post-WRK-200 audit of worldenergydata and digitalmodel. First-time Tier 3 classification
of assethold. Machine-readable output at `config/data-residence-compliance.yaml`.

---

## Result: All Three Repos Compliant — 0 Violations

| Repo | Declared Tier | Violations | Review Items | Status |
|------|--------------|-----------|--------------|--------|
| worldenergydata | Tier 1 — Collection Data | 0 | 1 (low) | Compliant |
| digitalmodel | Tier 2 — Engineering Reference Data | 0 | 0 | Compliant |
| assethold | Tier 3 — Project/Portfolio Data | 0 | 1 (low) | Compliant |

---

## worldenergydata (Tier 1)

WRK-200 naming cleanup did not alter tier boundaries. All data directories retain correct
Tier 1 classification.

**Gitignore compliance:** Large regenerable raw data is correctly excluded.

| Data Domain | Committed | Gitignored | Compliant |
|-------------|-----------|-----------|-----------|
| BSEE current CSVs | Yes (<10MB) | zip/, bin/ | Yes |
| HSE (OSHA, EPA TRI) raw | No | Yes | Yes |
| Marine safety raw | No | Yes (+ DB) | Yes |
| Pipeline safety (PHMSA) | Small XLS | Extracted bulk | Yes |
| LNG terminals curated | Yes | cache/ | Yes |
| SODIR | No | Yes | Yes |
| Vessel fleet (curated) | Yes | — | Yes |
| Vessel hull models | Yes (OBJ) | — | Yes |
| Wind turbine DB | Yes (ZIP) | — | Yes |
| Metocean | No | Yes | Yes |
| Data catalog | Yes (<10MB) | — | Yes |

**Review item:** `data/marine_safety/` (top-level) appears alongside
`data/modules/marine_safety/`. Low-severity — recommend consolidation in a future
WRK item to remove the ambiguous path.

**WRK-200 impact:** Nil for tier classification. The naming cleanup removed orphan dirs,
fixed legacy paths, and deprecated stale docs — none of these touched the `data/` tree.

---

## digitalmodel (Tier 2)

Both data directories are unchanged since WRK-097 and correctly hold Tier 2 content.

| Path | Content | Standard Origin | Compliant |
|------|---------|----------------|-----------|
| `data/fatigue/sn_curves.yaml` | 37 SN curves | DNV-RP-C203, API-RP-2A, BS-7608, AWS-D1.1 | Yes |
| `data/hull_library/panels/primitives/` | Validation GDF/CSF panels | Analytical / DNV validation | Yes |
| `data/hull_library/panels/semi_subs/` | ISSC TLP reference models | ISSC benchmark | Yes |
| `data/hull_library/catalog/hull_panel_catalog.yaml` | Panel index | Generated catalog | Yes |

**Cross-repo dependency check:** `config/data_sources.yaml` correctly declares
worldenergydata hull models and metocean as read-only Tier 1 dependencies. No data
has been copied between repos.

**WRK-200 impact:** Nil. The `data/` directory was not in scope for WRK-200 and remains
unchanged. The deferred consolidation of `outputs/`, `results/`, `reports/` does not
affect tier classification (these are regenerable analysis outputs, not data-residence items).

---

## assethold (Tier 3 — first classification)

Assethold holds personal investment portfolio and real estate analysis data. It does not
collect public raw data at scale and does not contain engineering standards. Tier 3 is
the correct classification.

| Data Domain | Path | Git | Compliant |
|------------|------|-----|-----------|
| Stock price cache | `data/stocks/cache/` | Gitignored | Yes |
| Real estate listing | `data/loopnet/` | Committed (1 CSV) | Review |
| Portfolio analysis outputs | `data/processed/`, `data/results/` | Gitignored | Yes |
| Brokerage exports (raw) | `data/raw/` | Gitignored | Yes |
| Strategy config | `config/daily_strategy.yaml` | Committed | Yes |
| Watchlist config | `config/stocks/watchlist.yml` | Committed | Yes |
| Scenario configs | `src/.../multifamily_*.yaml` | Committed | Yes |

**Review item:** `data/loopnet/2025-06-29_loopnet.csv` — a point-in-time real estate
scrape committed to git. File is below the 10MB size threshold. If the scraper can
reproduce this snapshot, it should be gitignored. If it is a unique snapshot with no
regeneration path, the committed approach is acceptable under the policy size exception.

---

## Tier Boundary Integrity

The critical Tier 1/Tier 2 boundary (vessel hull geometry) remains intact post-WRK-200:

- **worldenergydata** holds `data/modules/vessel_hull_models/` — CAD export OBJ files
  and marine component geometry. Origin: Rhino CAD exports and OrcaWave. Tier 1.
- **digitalmodel** holds `data/hull_library/panels/` — analytical validation GDF panels
  (unit box, cylinder, spheroid, ISSC TLP). Origin: engineering benchmarks. Tier 2.

These are distinct datasets serving distinct purposes. No boundary crossing detected.

---

## Agent Query Reference

Agents querying tier classification should use `config/data-residence-compliance.yaml`.

```
worldenergydata  -> tier_1  (all data/ paths)
digitalmodel     -> tier_2  (all data/ paths)
assethold        -> tier_3  (all data/ paths)

Cross-repo access:
  digitalmodel reads worldenergydata paths via config/data_sources.yaml (read-only)
  No other cross-repo data access declared
```

---

## Follow-on Actions

| Action | Priority | Suggested WRK |
|--------|----------|--------------|
| Consolidate `worldenergydata/data/marine_safety/` into `data/modules/marine_safety/` | Low | New item |
| Determine if assethold LoopNet CSV should be gitignored | Low | New item |
| Extend tier classification to `aceengineer-admin`, `saipem`, `doris` | Medium | New item |
