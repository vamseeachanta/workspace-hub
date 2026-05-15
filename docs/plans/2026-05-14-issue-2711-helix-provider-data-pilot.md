# Plan for #2711: feat(provider-data): service-provider data library — Helix 15k IRS pilot

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-05-14
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2711
> **Review artifacts:** scripts/review/results/2026-05-14-plan-2711-claude.md | scripts/review/results/2026-05-14-plan-2711-codex.md | scripts/review/results/2026-05-14-plan-2711-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- EXISTS: `docs/governance/2026-05-14-service-provider-data-routing-and-bsee-ingest-design.md` — D3 decision: Helix IRS vendor brochure routes to `/mnt/ace/vendor-pdfs/helix-esg/`, NOT in any git repo. Copyright owned by vendor; not redistributable under CC-BY-4.0; #2482 deny-list applies. This decision is FINAL and load-bearing for this plan.
- EXISTS: `docs/governance/vendor-pdf-inventory.md` (2026-05-14) — IRS PDF already indexed. Local path `helix-esg/Helix_Well_Ops_IRS-7-15k_LTR_2023-11-28.pdf`. Origin URL `https://helixesg.com/downloads/Helix_Well_Ops-_IRS_7_15k-_LTR_11-28-23_FINAL.pdf`. Observed 2026-05-14. Character: vendor-brochure. No in-repo PDF entry exists or should be created.
- EXISTS: `digitalmodel/src/digitalmodel/citations/schema.py` (133 lines) — `@dataclass(frozen=True) Citation(code_id, publisher, revision, section, wiki_path, note="")`. Governs STANDARDS-derived constants only per `.claude/rules/calc-citation-contract.md` escape clause: "Do NOT apply when the constant is derived from the code itself (not a standard)." Vendor data is not a standard. This plan does NOT apply the citation contract to vendor specs; it proposes a structurally similar but distinct sibling schema `ProviderDataRecord` for vendor-spec provenance.
- EXISTS: `digitalmodel/src/digitalmodel/orcaflex/model_builder.py` — `build_scr_model(water_depth, riser_od, riser_id)`, `LineSectionProperties(outer_diameter, inner_diameter, mass_per_unit_length)`, `LineConfig`, `VesselConfig`. Water depth is the primary environment parameter throughout.
- EXISTS: `digitalmodel/src/digitalmodel/orcaflex/riser_config.py` — `SCRDesignInput(water_depth, pipe: RiserPipeProperties)`, `TTRDesignInput(water_depth, pipe)`, `RiserPipeProperties(outer_diameter, wall_thickness)`. `water_depth` in meters is the canonical OrcaFlex environment field that IRS MWD maps to.
- EXISTS: `digitalmodel/src/digitalmodel/orcaflex/environment.py` — `CurrentProfile(water_depth, surface_speed)`. Water depth field confirmed.
- GAP: `docs/provider-data/` directory does not exist anywhere in the repo.
- GAP: No `ProviderDataRecord` schema exists. The `Citation` schema targets standards; vendor data needs a parallel schema without the wiki-frontmatter resolver (no fail-closed validation against wiki pages).
- GAP: No OrcaFlex mapping documentation exists for IRS or any intervention riser system.
- GAP: No `docs/provider-data/README.md` template for adding future providers.

### Standards

Not applicable as primary scope — this issue is a provider-data library pilot, not a standards-calculation issue. The `calc-citation-contract.md` rule DOES NOT apply to vendor-derived parameters per its own explicit escape clause. `ProviderDataRecord` is architecturally inspired by `Citation` but is a separate concern.

### LLM Wiki pages consulted

No relevant wiki pages. The Helix entity page in drilling-engineering wiki does not yet exist (deferred per D4 of the routing design until sufficient public-record grounding — SEC 10-K + class records — accumulates).

### Documents consulted

- `docs/governance/2026-05-14-service-provider-data-routing-and-bsee-ingest-design.md` — D1–D5 routing matrix; D3 routes Helix IRS to private mount.
- `docs/governance/vendor-pdf-inventory.md` — IRS PDF already indexed with origin URL and inventory schema.
- `digitalmodel/src/digitalmodel/citations/schema.py` — `Citation` and `CitedValue` shapes; informs `ProviderDataRecord` design.
- `docs/standards/calc-output-citation.md` — citation contract scope confirmed; vendor data out of scope.
- `.claude/rules/calc-citation-contract.md` — "Do NOT apply when" escape clause confirmed applicable here.
- `.gitignore` lines 510–514 — only `docs/gtm/intake/received/` and `docs/gtm/intake/logos/` gitignored under `docs/`; `docs/provider-data/` path is NOT gitignored.
- Issue [#2711](https://github.com/vamseeachanta/workspace-hub/issues/2711) — scope per task prompt: parameters.yaml + orcaflex-mapping.md + ProviderDataRecord schema + library README.
- `digitalmodel/src/digitalmodel/orcaflex/model_builder.py` — OrcaFlex field names for riser modeling.
- `digitalmodel/src/digitalmodel/orcaflex/riser_config.py` — TTRDesignInput, SCRDesignInput, RiserPipeProperties field names.
- PDF brochure — Helix 15k IRS, 4 pages, read via image extraction 2026-05-14, revision date 11.17.2023. All IRS spec values embedded in Evidence below.

### Gaps identified

- `docs/provider-data/` tree does not exist anywhere in the repo — must be created from scratch.
- `ProviderDataRecord` dataclass does not exist — confirmed 0 matches in repo.
- No pytest tests for structured provider-data YAML validation.
- No orcaflex-mapping documentation for any intervention riser system.
- `docs/provider-data/README.md` template for "how to add next provider" does not exist.

### Evidence (embedded verification)

**Issue statuses** (2026-05-14; `gh issue view 2711` not independently run in this session — issue scope confirmed via task prompt):
- `#2711` — OPEN — feat(provider-data): service-provider data library — Helix 15k IRS pilot

**File existence** (Read/Grep/Glob 2026-05-14T session):
- EXISTS: `docs/governance/2026-05-14-service-provider-data-routing-and-bsee-ingest-design.md` — confirmed Read
- EXISTS: `docs/governance/vendor-pdf-inventory.md` — confirmed via Grep output
- EXISTS: `digitalmodel/src/digitalmodel/citations/schema.py` — confirmed Read, 133 lines
- EXISTS: `digitalmodel/src/digitalmodel/orcaflex/model_builder.py` — confirmed Read
- EXISTS: `digitalmodel/src/digitalmodel/orcaflex/riser_config.py` — confirmed Read
- EXISTS: `digitalmodel/src/digitalmodel/orcaflex/environment.py` — confirmed Read
- MISSING (new — this plan creates): `docs/provider-data/README.md`
- MISSING (new — this plan creates): `docs/provider-data/helix-esg/irs-15k/parameters.yaml`
- MISSING (new — this plan creates): `docs/provider-data/helix-esg/irs-15k/orcaflex-mapping.md`
- MISSING (new — this plan creates): `docs/provider-data/helix-esg/irs-15k/PROVIDER_RECORD.md`
- MISSING (new — this plan creates): `digitalmodel/src/digitalmodel/provider_data/__init__.py`
- MISSING (new — this plan creates): `digitalmodel/src/digitalmodel/provider_data/schema.py`
- MISSING (new — this plan creates): `digitalmodel/tests/provider_data/test_schema.py`
- MISSING (new — this plan creates): `digitalmodel/tests/provider_data/test_irs_15k_yaml.py`

**vendor-pdf-inventory.md IRS row** (Read 2026-05-14):
```
helix-esg/Helix_Well_Ops_IRS-7-15k_LTR_2023-11-28.pdf |
  origin: https://helixesg.com/downloads/Helix_Well_Ops-_IRS_7_15k-_LTR_11-28-23_FINAL.pdf |
  observed: 2026-05-14 | character: vendor-brochure |
  public anchor: Helix 10-K Well Intervention segment; SPE/OTC conference papers
```

**.gitignore excerpt** (Read lines 510–514, 2026-05-14):
```
docs/gtm/intake/received/
docs/gtm/intake/logos/
...
knowledge/wikis/**/raw/papers/*.pdf
wikis/**/raw/papers/*.pdf
```
`docs/provider-data/` does not match any gitignore pattern. Confirmed safe to create.

**PDF IRS specifications** (4-page brochure, image extraction 2026-05-14, revision date 11.17.2023):
```
IRS specifications:
  Bore Diameter: 6-3/8 in HH-NL production, 2-1/16 in DD-NL annulus
  Working Pressure: 15,000 psi
  Design Temperature Range: 35 F to 300 F
  Maximum Working Depth (MWD): 10,000 ft (3,048 m)
  Control System: MUX with integrated redundancy via HIPPS
  Maximum EDP Disconnect Angle: 18 degrees
  Subsea Package Weight: 242,000 lbs (280,000 lbs with optional Safety Head)
Surface flowhead specifications:
  Maximum Through Bore Diameter: 6-3/8 in production, 4-1/16 in wings
  Maximum Working Pressure (MWP): 15,000 psi
Client interface:
  Pass Through Tree Function Lines: 19x Hydraulic Control lines
    (3x 15,000 psi + 16x 5,000 psi)
  2x Electrical Control lines
  Subsea Interface: IRS 7 18-3/4 in hydraulic connector
```

**citations/schema.py Citation shape** (Read lines 40–54, 2026-05-14):
```python
@dataclass(frozen=True)
class Citation:
    code_id: str
    publisher: str
    revision: str
    section: str
    wiki_path: str
    note: str = ""
```
`ProviderDataRecord` will be structurally similar but MUST NOT import from `citations/` or inherit its resolver behavior.

**Gap proofs** (Grep 2026-05-14):
- `Grep pattern=ProviderDataRecord path=/mnt/local-analysis/workspace-hub` → 0 files → class does not exist.
- `Glob pattern=docs/provider-data/** path=/mnt/local-analysis/workspace-hub/docs` → no files found → directory does not exist.

**Reproduction proofs:** N/A — new feature; no existing failure to reproduce. Intentional skip per Step 1.5 guidance; marked here so reviewers know the skip was deliberate.

<!-- Verification: distinct sources: (1) issue #2711 body, (2) routing governance doc D3, (3) vendor-pdf-inventory.md, (4) citations/schema.py, (5) calc-citation-contract.md escape clause, (6) .gitignore lines 510-514, (7) model_builder.py OrcaFlex fields, (8) riser_config.py TTR/SCR fields, (9) environment.py water_depth field, (10) PDF brochure images 4 pages. Count: 10 — exceeds minimum 3 ✓ -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-14-issue-2711-helix-provider-data-pilot.md` |
| Provider library README | `docs/provider-data/README.md` |
| IRS parameters YAML | `docs/provider-data/helix-esg/irs-15k/parameters.yaml` |
| IRS OrcaFlex mapping | `docs/provider-data/helix-esg/irs-15k/orcaflex-mapping.md` |
| IRS provenance record | `docs/provider-data/helix-esg/irs-15k/PROVIDER_RECORD.md` |
| ProviderDataRecord schema | `digitalmodel/src/digitalmodel/provider_data/schema.py` |
| Schema unit tests | `digitalmodel/tests/provider_data/test_schema.py` |
| YAML integration tests | `digitalmodel/tests/provider_data/test_irs_15k_yaml.py` |
| Plan review — Claude | `scripts/review/results/2026-05-14-plan-2711-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-14-plan-2711-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-14-plan-2711-gemini.md` |

---

## Deliverable

A structured provider-data library pilot will exist at `docs/provider-data/helix-esg/irs-15k/` with a validated `parameters.yaml` encoding all Helix 15k IRS specifications extracted from the brochure (bore, pressure, depth, temperature, weight, control-line counts), an `orcaflex-mapping.md` mapping each spec to a specific OrcaFlex `.dat` field or justified "no direct field", a `PROVIDER_RECORD.md` with full provenance, a `ProviderDataRecord` Python dataclass at `digitalmodel/src/digitalmodel/provider_data/schema.py`, and 12 pytest tests verifying the YAML conforms to the schema and values are within expected engineering ranges — together establishing the reusable template for all future provider additions.

---

## Pseudocode

```
# digitalmodel/src/digitalmodel/provider_data/schema.py

import math
import yaml
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ProviderDataSource:
    """Provenance record for a vendor parameter file.

    Intentionally distinct from Citation (which targets wiki-backed standards).
    No wiki-resolver. No fail-closed validation against wiki frontmatter.
    Records vendor document provenance only.
    """
    vendor: str               # "Helix Energy Solutions Group"
    vendor_slug: str          # "helix-esg"
    document_name: str        # "15k Intervention Riser System LTR brochure"
    revision_date: str        # ISO date or vendor label: "2023-11-17"
    origin_url: str           # source download URL (not a local path)
    private_mount_path: str   # "/mnt/ace/vendor-pdfs/helix-esg/..."
    inventory_ref: str        # "docs/governance/vendor-pdf-inventory.md"
    retrieved_date: str       # "2026-05-14"
    sha256: str = ""          # optional; fill when PDF is at hand for drift detection
    note: str = ""

    def __post_init__(self):
        for f in ("vendor", "vendor_slug", "document_name", "origin_url",
                  "private_mount_path", "inventory_ref", "retrieved_date"):
            v = getattr(self, f)
            if not isinstance(v, str) or not v.strip():
                raise ValueError(f"ProviderDataSource.{f} must be non-empty string")


@dataclass(frozen=True)
class SpecValue:
    """A single specification value with unit."""
    value: float
    unit: str          # "psi", "m", "kg", "degF", "deg", "count" — never empty
    note: str = ""

    def __post_init__(self):
        if not self.unit.strip():
            raise ValueError("SpecValue.unit must be non-empty")


@dataclass
class ProviderDataRecord:
    """Structured provider equipment specification record.

    One record per equipment-system variant (e.g., IRS 15k).
    specifications: dict mapping spec_key -> SpecValue (or list[SpecValue]
                    for multi-value specs like bore variants)
    orcaflex_mapping: dict mapping spec_key -> human-readable OrcaFlex field description
    """
    provider: ProviderDataSource
    system_name: str
    system_slug: str
    specifications: dict  # str -> SpecValue | list[SpecValue]
    orcaflex_mapping: dict = field(default_factory=dict)

    _REQUIRED_SPECS = frozenset({
        "mwd_m", "mwp_psi", "bore_production_id_m",
        "design_temp_min_degF", "design_temp_max_degF",
        "subsea_package_weight_kg",
    })

    def validate(self) -> None:
        missing = self._REQUIRED_SPECS - set(self.specifications)
        if missing:
            raise ValueError(f"ProviderDataRecord missing required specs: {sorted(missing)}")
        for key, sv in self.specifications.items():
            items = sv if isinstance(sv, list) else [sv]
            for item in items:
                if not math.isfinite(item.value) or item.value < 0:
                    raise ValueError(
                        f"Spec {key!r} has invalid value {item.value} — must be finite non-negative"
                    )


def load_provider_yaml(yaml_path: Path) -> ProviderDataRecord:
    """Load, parse, and validate a provider parameters.yaml file.

    Raises ValueError for missing required fields or out-of-range values.
    Raises yaml.YAMLError for malformed YAML.
    """
    raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    source = ProviderDataSource(**raw["source"])
    specs = {}
    for k, v in raw["specifications"].items():
        if isinstance(v, list):
            specs[k] = [SpecValue(**i) for i in v]
        else:
            specs[k] = SpecValue(**v)
    record = ProviderDataRecord(
        provider=source,
        system_name=raw["system"]["name"],
        system_slug=raw["system"]["slug"],
        specifications=specs,
        orcaflex_mapping=raw.get("orcaflex_mapping", {}),
    )
    record.validate()
    return record
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/provider-data/README.md` | Library README — "how to add next provider" template and current library index |
| Create | `docs/provider-data/helix-esg/irs-15k/parameters.yaml` | Structured IRS specs from brochure; all values with value + unit fields |
| Create | `docs/provider-data/helix-esg/irs-15k/orcaflex-mapping.md` | Spec-key to OrcaFlex .dat field mapping table |
| Create | `docs/provider-data/helix-esg/irs-15k/PROVIDER_RECORD.md` | Human-readable provenance: vendor, origin URL, inventory ref, retrieval date |
| Create | `digitalmodel/src/digitalmodel/provider_data/__init__.py` | Package init; exports ProviderDataRecord, ProviderDataSource, SpecValue, load_provider_yaml |
| Create | `digitalmodel/src/digitalmodel/provider_data/schema.py` | ProviderDataSource, SpecValue, ProviderDataRecord dataclasses + load_provider_yaml() |
| Create | `digitalmodel/tests/provider_data/__init__.py` | Test package init (empty) |
| Create | `digitalmodel/tests/provider_data/test_schema.py` | Unit tests for ProviderDataRecord validation logic |
| Create | `digitalmodel/tests/provider_data/test_irs_15k_yaml.py` | Integration tests: load real parameters.yaml, assert required keys + value ranges |

---

## Concrete YAML Design

`docs/provider-data/helix-esg/irs-15k/parameters.yaml` will contain:

```yaml
# Helix Energy Solutions Group — 15k Intervention Riser System
# Extracted from: Helix_Well_Ops_IRS-7-15k_LTR_2023-11-28.pdf (4-page brochure, rev 11.17.2023)
# Routing: vendor-brochure per D3 decision — docs/governance/2026-05-14-service-provider-data-routing-and-bsee-ingest-design.md
# PDF location (off-repo): /mnt/ace/vendor-pdfs/helix-esg/Helix_Well_Ops_IRS-7-15k_LTR_2023-11-28.pdf
# COPYRIGHT NOTICE: All specifications are factual engineering data (17 U.S.C. 102(b)).
#   The source PDF is Helix Energy Solutions Group proprietary and is NOT in this repository.

system:
  name: "15k Intervention Riser System"
  slug: "irs-15k"
  vendor: "Helix Energy Solutions Group"
  abbreviation: "IRS"

source:
  vendor: "Helix Energy Solutions Group"
  vendor_slug: "helix-esg"
  document_name: "15k Intervention Riser System LTR brochure"
  revision_date: "2023-11-17"
  origin_url: "https://helixesg.com/downloads/Helix_Well_Ops-_IRS_7_15k-_LTR_11-28-23_FINAL.pdf"
  private_mount_path: "/mnt/ace/vendor-pdfs/helix-esg/Helix_Well_Ops_IRS-7-15k_LTR_2023-11-28.pdf"
  inventory_ref: "docs/governance/vendor-pdf-inventory.md"
  retrieved_date: "2026-05-14"
  sha256: ""  # fill when PDF is at hand for drift detection

specifications:
  # Primary ratings
  mwp_psi: { value: 15000.0, unit: "psi", note: "Maximum Working Pressure" }
  mwp_mpa: { value: 103.42, unit: "MPa", note: "MWP converted: 15000 * 0.006895" }
  mwd_ft:  { value: 10000.0, unit: "ft", note: "Maximum Working Depth" }
  mwd_m:   { value: 3048.0, unit: "m", note: "MWD converted: 10000 * 0.3048" }

  # Bore geometry
  bore_production_id_in: { value: 6.375, unit: "in", note: "Production bore — HH-NL (6-3/8 in)" }
  bore_production_id_m:  { value: 0.16193, unit: "m", note: "Production bore: 6.375 * 0.0254" }
  bore_annulus_id_in:    { value: 2.0625, unit: "in", note: "Annulus bore — DD-NL (2-1/16 in)" }
  bore_annulus_id_m:     { value: 0.05239, unit: "m", note: "Annulus bore: 2.0625 * 0.0254" }

  # Design temperature
  design_temp_min_degF: { value: 35.0, unit: "degF" }
  design_temp_min_degC: { value: 1.67, unit: "degC", note: "(35 - 32) * 5/9" }
  design_temp_max_degF: { value: 300.0, unit: "degF" }
  design_temp_max_degC: { value: 148.89, unit: "degC", note: "(300 - 32) * 5/9" }

  # Mechanical / operational
  max_edp_disconnect_angle_deg: { value: 18.0, unit: "deg" }
  subsea_package_weight_lbs: { value: 242000.0, unit: "lbs", note: "Base configuration" }
  subsea_package_weight_kg:  { value: 109771.7, unit: "kg", note: "Converted: 242000 / 2.20462" }
  subsea_package_weight_with_safety_head_lbs: { value: 280000.0, unit: "lbs" }
  subsea_package_weight_with_safety_head_kg:  { value: 127006.4, unit: "kg" }

  # Surface flowhead
  flowhead_bore_production_in: { value: 6.375, unit: "in" }
  flowhead_bore_wings_in: { value: 4.0625, unit: "in" }
  flowhead_mwp_psi: { value: 15000.0, unit: "psi" }

  # Control lines
  control_lines_hydraulic_15kpsi_count: { value: 3.0, unit: "count" }
  control_lines_hydraulic_5kpsi_count:  { value: 16.0, unit: "count" }
  control_lines_electrical_count: { value: 2.0, unit: "count" }
```

---

## OrcaFlex Mapping Design

`docs/provider-data/helix-esg/irs-15k/orcaflex-mapping.md` will contain a table mapping each IRS spec key to a specific OrcaFlex object/field with rationale. Key rows:

| IRS spec key | Value | OrcaFlex object / field | Mapping rationale |
|---|---|---|---|
| `mwd_m` | 3048.0 m | `CurrentProfile.water_depth`; `SCRDesignInput.water_depth`; `TTRDesignInput.water_depth` | Primary environment depth; drives riser length, catenary geometry, and current profile depth |
| `bore_production_id_m` | 0.1619 m | `LineSectionProperties.inner_diameter`; `RiserPipeProperties` inner diameter | IRS riser through-bore; determines wireline/CT access capability and internal fluid volume |
| `mwp_psi` | 15,000 psi (103.4 MPa) | No direct OrcaFlex field — apply as burst-check input or `EndAForce` pressure load case in post-processing | OrcaFlex models structural dynamics, not internal pressure; MWP sets wall-thickness via burst check per API RP 2RD |
| `subsea_package_weight_kg` | 109,772 kg | `Buoy6DConfig.mass` (kg) when modeled as discrete lumped mass; or contributes to `LineSectionProperties.mass_per_unit_length` | IRS lower package is a 6DOF lumped mass at bottom end; weight drives top tension sizing |
| `design_temp_min_degC` / `design_temp_max_degC` | 1.67 C / 148.89 C | No direct field — governs `RiserPipeProperties.grade` material selection | OrcaFlex uses ambient temperature for buoyancy only; design temp is a material constraint |
| `max_edp_disconnect_angle_deg` | 18 deg | Emergency disconnect load case: compute hang-off angle via `estimate_scr_hang_off_angle(water_depth, horizontal_offset)`; acceptance criterion: computed angle ≤ 18 deg | EDP must function within 18 deg; OrcaFlex time-history at vessel-offset limit provides the angle at riser top |

---

## Provider Library README Design

`docs/provider-data/README.md` will contain:

- "What this is" / "What this is NOT" boundaries
- Directory layout: `<vendor-slug>/<system-slug>/{parameters.yaml,orcaflex-mapping.md,PROVIDER_RECORD.md}`
- Numbered "how to add next provider" procedure (≥7 steps): PDF to private mount → inventory row → parameters.yaml → mapping → provenance → test → verify
- Current library table: vendor, system, slug, date added (only Helix 15k IRS at v1)

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_provider_data_source_missing_field_raises` | Missing required field raises ValueError | Omit `vendor` from ProviderDataSource kwargs | `ValueError` containing "vendor" |
| `test_spec_value_empty_unit_raises` | Empty unit string raises ValueError | `SpecValue(value=1.0, unit="")` | `ValueError` |
| `test_provider_data_record_missing_required_spec_raises` | Missing `mwd_m` raises ValueError | Record with `mwd_m` omitted | `ValueError` listing "mwd_m" |
| `test_provider_data_record_negative_value_raises` | Negative spec value raises | `mwp_psi.value = -100.0` | `ValueError` mentioning spec key |
| `test_provider_data_record_valid_nominal_passes` | Valid minimal record passes validate() | All required specs present and positive | No exception |
| `test_load_provider_yaml_irs_15k_nominal` | load_provider_yaml() succeeds on real IRS YAML | Path to `parameters.yaml` | Returns ProviderDataRecord, no exception |
| `test_irs_15k_mwd_value` | MWD spec is 3048.0 m | IRS YAML loaded | `record.specifications["mwd_m"].value == 3048.0` |
| `test_irs_15k_mwp_value` | MWP spec is 15000.0 psi | IRS YAML loaded | `record.specifications["mwp_psi"].value == 15000.0` |
| `test_irs_15k_bore_production_range` | Production bore ID within realistic IRS range | IRS YAML loaded | `0.15 <= value <= 0.17` |
| `test_irs_15k_subsea_weight_unit_consistency` | kg weight ≈ lbs / 2.20462 within 1% | IRS YAML loaded | `abs(kg - lbs / 2.20462) / kg < 0.01` |
| `test_irs_15k_temp_range_ordering` | Min temp less than max temp | IRS YAML loaded | `design_temp_min_degF.value < design_temp_max_degF.value` |
| `test_load_provider_yaml_malformed_raises` | Malformed YAML raises | YAML missing `system` key | `KeyError` or `yaml.YAMLError` |

---

## Acceptance Criteria

- [ ] `docs/provider-data/helix-esg/irs-15k/parameters.yaml` will exist; `grep mwd_m` will show `value: 3048.0`
- [ ] `docs/provider-data/helix-esg/irs-15k/orcaflex-mapping.md` will exist with a table ≥7 rows mapping IRS specs to OrcaFlex fields
- [ ] `docs/provider-data/README.md` will exist with a numbered "how to add next provider" procedure (≥7 steps) and a current library table
- [ ] `from digitalmodel.provider_data.schema import ProviderDataRecord` will succeed (no import error)
- [ ] `uv run pytest digitalmodel/tests/provider_data/ -v` will show 12 tests passing
- [ ] `uv run pytest digitalmodel/ -v` will pass with no new failures (no regression)
- [ ] `git ls-files "*.pdf"` will show no new PDF entries — no PDF committed to repo
- [ ] `docs/governance/vendor-pdf-inventory.md` will NOT be modified — IRS row already exists; `git diff` must be empty for that file
- [ ] Plan review artifacts posted to `scripts/review/results/` per T2 cross-review requirement (Codex + Gemini minimum)

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** PENDING

Revisions made based on review:
- (none yet — plan is draft)

---

## Risks and Open Questions

- **Risk (license — flag for user):** Factual engineering specifications (bore diameter, working pressure, depth rating, weight) are generally not copyrightable under US law (17 U.S.C. § 102(b) — copyright does not extend to ideas, procedures, processes, or discoveries). This plan stores only numeric values with units, not copied prose or verbatim table formatting. The source PDF stays off-repo per D3. This is standard engineering practice (spec values appear in engineering datasheets universally). However, if user requires formal legal clearance before committing `parameters.yaml`, defer this artifact until cleared and flag. Recommendation: proceed with numeric-only YAML as low-risk.
- **Risk (schema boundary — load-bearing):** `ProviderDataRecord` must NOT import from `digitalmodel.citations` or inherit the wiki-resolver. These are separate concerns. Mixing them would (a) impose fail-closed wiki-page requirements on vendor data and (b) violate the `calc-citation-contract.md` "Do NOT apply when" escape clause. Keep `provider_data/schema.py` and `citations/schema.py` in separate modules with no cross-import.
- **Risk (unit conversion accuracy):** Conversion factors embedded in YAML must be correct. Verifiable: 242000 / 2.20462 = 109771.7 kg (±0.05 kg); 10000 * 0.3048 = 3048.0 m (exact). Test `test_irs_15k_subsea_weight_unit_consistency` enforces 1% tolerance. If tolerance fails: fix the YAML value, not the test threshold.
- **Risk (OrcaFlex field drift):** Field names in `model_builder.py` and `riser_config.py` may change between OrcaFlex versions. Mapping doc references field names as of 2026-05-14 read. If OrcaFlex API version changes, update the mapping doc accordingly; tests do not depend on OrcaFlex field names.
- **Open (SHA256 checksum):** `ProviderDataSource.sha256` is an optional field (default empty string). Filling it requires the PDF to be at hand. Recommendation: compute and fill at first opportunity when PDF is accessed at `/mnt/ace/`. Does not block plan approval.
- **Open (schema location):** `provider_data/schema.py` under `digitalmodel/src/digitalmodel/` scopes it to engineering-tool consumers. If non-digitalmodel consumers (e.g., a workspace-hub script) need `load_provider_yaml`, extract to `scripts/data/` later. Defer; cross that bridge when a concrete consumer appears.
- **Open (next provider):** Q4000 vessel parameters (`helix-esg/q4000/parameters.yaml`) is the natural next entry — same vendor, second system. Defer to a follow-up issue. This pilot establishes the full pattern.

---

## Complexity: T2

**T2** — new directory tree, new YAML schema, new Python dataclass module with validation, new pytest test suite (12 tests), new OrcaFlex mapping documentation. No existing production code modified. Below T3 because: no multi-module interdependency changes, no CI gate modifications, no regulatory-critical calc surface, and rollback is purely additive (all new files, zero edits to existing code). Per `feedback_always_adversarial_review_scale_depth`, T2 requires Codex + Gemini cross-review at minimum.
