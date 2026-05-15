# Plan for #2711: feat(provider-data): service-provider data library — Helix 15k IRS pilot

> **Status:** draft (revised after r1 Codex review — 7 blockers addressed)
> **Complexity:** T2
> **Date:** 2026-05-14 (drafted) / 2026-05-15 (r1 revision)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2711
> **Review artifacts:** scripts/review/results/2026-05-14-plan-2711-claude.md | scripts/review/results/2026-05-14-plan-2711-codex.md | scripts/review/results/2026-05-14-plan-2711-gemini.md

---

## Issue-Body Acceptance Criteria — Amendment Notice

Issue #2711 body specifies the pilot at `docs/provider-data/helix/15k-irs/` containing `README.md`, `source.pdf`, `parameters.yaml`, and `orcaflex-mapping.md`, plus a license assessment in the pilot README. **This plan amends those criteria per governance routing decision D3 (`docs/governance/2026-05-14-service-provider-data-routing-and-bsee-ingest-design.md`, dated 2026-05-14):**

1. **`source.pdf` will NOT be committed.** Per D3, the Helix IRS brochure is vendor-proprietary (Helix Energy Solutions Group copyright) and is NOT redistributable under workspace-hub's CC-BY-4.0; it is also covered by the #2482 deny-list. The PDF stays at `/mnt/ace/vendor-pdfs/helix-esg/Helix_Well_Ops_IRS-7-15k_LTR_2023-11-28.pdf`. The `parameters.yaml` `source.private_mount_path` field and the pilot README's "Source" section will point reviewers to the off-repo location.
2. **Path slug pattern is `<vendor-slug>/<system-slug>/`, not `<vendor>/<system>/`.** Pilot will land at `docs/provider-data/helix-esg/irs-15k/`, not `docs/provider-data/helix/15k-irs/`. Rationale: `helix-esg` is the canonical vendor slug used by `vendor-pdf-inventory.md` (Helix Energy Solutions Group could later add Helix Robotics or Helix Wind subsidiaries — short slug "helix" is ambiguous). `irs-15k` (system-first) reads better in directory listings than `15k-irs` (rating-first) when sibling systems exist at different ratings (e.g., future `irs-10k/`). Both conventions are documented in the library README so future-provider authors know the rule.
3. **Pilot README WILL be added** (originally listed by issue body, originally omitted by plan v1). `docs/provider-data/helix-esg/irs-15k/README.md` will contain the license-assessment paragraph (17 U.S.C. §102(b) factual-data analysis) and brochure provenance, satisfying the issue-body intent. The companion `PROVIDER_RECORD.md` file from plan v1 is folded into this README (single file, two sections).

These three deviations are explicitly bounded by D3 and traceable to a dated governance decision; no further issue-body criteria are amended.

---

## Execution Contract — Two-Repo Coordination

This pilot spans **two separate git repos**. Plan v1 mixed paths without naming the boundary; plan v2 makes it explicit.

**Workspace-hub repo** (`/mnt/local-analysis/workspace-hub/`, branch `feat/marker-label-parity-gate` or successor) — owns:
- `docs/plans/2026-05-14-issue-2711-helix-provider-data-pilot.md` (this plan)
- `docs/provider-data/README.md` (library README)
- `docs/provider-data/helix-esg/irs-15k/README.md` (pilot README with license assessment + provenance)
- `docs/provider-data/helix-esg/irs-15k/parameters.yaml`
- `docs/provider-data/helix-esg/irs-15k/orcaflex-mapping.md`
- `scripts/review/results/2026-05-14-plan-2711-*.md` (review artifacts)

**Digitalmodel repo** (`/mnt/local-analysis/workspace-hub/digitalmodel/`, a SEPARATE git repo with its own `.git/`; `digitalmodel/` is gitignored by workspace-hub `.gitignore`) — owns:
- `digitalmodel/src/digitalmodel/provider_data/__init__.py`
- `digitalmodel/src/digitalmodel/provider_data/schema.py`
- `digitalmodel/tests/provider_data/__init__.py`
- `digitalmodel/tests/provider_data/test_schema.py`
- `digitalmodel/tests/provider_data/test_irs_15k_yaml.py`

**Implementation order** (load-bearing — do NOT reorder):

1. **digitalmodel first** — `cd digitalmodel && git checkout -b feat/provider-data-schema` → write `schema.py` + tests → `cd digitalmodel && uv run pytest tests/provider_data/ -v` (cwd = digitalmodel checkout root) → commit on a feat branch → optionally push and open a digitalmodel PR (see "Digitalmodel PR" below).
2. **workspace-hub second** — back at workspace-hub root, write `docs/provider-data/**`. The YAML integration test (`test_irs_15k_yaml.py`) loads `parameters.yaml` from the workspace-hub working tree using an absolute path resolved at test-collection time; if the YAML is not yet present, the integration test is skipped (`pytest.skip`), not failed. The schema unit tests do not depend on workspace-hub.
3. **Commit pairing** — workspace-hub commit message will reference the digitalmodel commit SHA in its body (`Pairs with digitalmodel@<sha>`); digitalmodel commit message will reference `vamseeachanta/workspace-hub#2711`. Both are required for trace.

**Pytest cwd contract** — `uv run pytest digitalmodel/tests/provider_data/ -v` is invoked from inside the **digitalmodel checkout** (`cd /mnt/local-analysis/workspace-hub/digitalmodel`); the relative path `tests/provider_data/` is preferred. The workspace-hub Acceptance Criteria below states the command as `cd digitalmodel && uv run pytest tests/provider_data/ -v` to remove ambiguity.

**Digitalmodel PR** — whether the digitalmodel changes require their own PR (vs. a direct commit to digitalmodel main) is owner-discretion; this plan does not gate on that decision. If a PR is required, the workspace-hub plan-approval gate proceeds in parallel; final merge of either repo waits for the OTHER repo's change to be at least pushed.

---

## Resource Intelligence Summary

### Existing repo code

- EXISTS: `docs/governance/2026-05-14-service-provider-data-routing-and-bsee-ingest-design.md` — D3 decision: Helix IRS vendor brochure routes to `/mnt/ace/vendor-pdfs/helix-esg/`, NOT in any git repo. Copyright owned by vendor; not redistributable under CC-BY-4.0; #2482 deny-list applies. This decision is FINAL and load-bearing for this plan.
- EXISTS: `docs/governance/vendor-pdf-inventory.md` (2026-05-14) — IRS PDF already indexed. Local path `helix-esg/Helix_Well_Ops_IRS-7-15k_LTR_2023-11-28.pdf`. Origin URL `https://helixesg.com/downloads/Helix_Well_Ops-_IRS_7_15k-_LTR_11-28-23_FINAL.pdf`. Observed 2026-05-14. Character: vendor-brochure. No in-repo PDF entry exists or should be created.
- EXISTS: `digitalmodel/src/digitalmodel/citations/schema.py` (133 lines) — `@dataclass(frozen=True) Citation(code_id, publisher, revision, section, wiki_path, note="")`. Governs STANDARDS-derived constants only per `.claude/rules/calc-citation-contract.md` escape clause: "Do NOT apply when the constant is derived from the code itself (not a standard)." Vendor data is not a standard. This plan does NOT apply the citation contract to vendor specs; it proposes a structurally similar but distinct sibling schema `ProviderDataRecord` for vendor-spec provenance.
- EXISTS: `digitalmodel/src/digitalmodel/orcaflex/model_builder.py` — `build_scr_model(water_depth, riser_od, riser_id)`, `LineSectionProperties(outer_diameter, inner_diameter, mass_per_unit_length, ...)` at line 60. **Verified 2026-05-15: `inner_diameter` IS a settable `Field` (line 67), NOT a computed property.** Water depth is the primary environment parameter throughout.
- EXISTS: `digitalmodel/src/digitalmodel/orcaflex/riser_config.py` — `SCRDesignInput(water_depth, pipe: RiserPipeProperties)`, `TTRDesignInput(water_depth, pipe)`, `RiserPipeProperties(outer_diameter, wall_thickness, grade, ...)`. **Verified 2026-05-15: `RiserPipeProperties.inner_diameter` is a computed `@property` (line 78, returns `outer_diameter - 2 * wall_thickness`), NOT a settable Field. `PipeGrade` enum (line 37) contains only X52/X60/X65/X70/X80 — no temperature constraint encoded.** `water_depth` in meters is the canonical OrcaFlex environment field that IRS MWD maps to.
- EXISTS: `digitalmodel/src/digitalmodel/orcaflex/environment.py` — `CurrentProfile(water_depth, surface_speed)`. Water depth field confirmed.
- GAP: `docs/provider-data/` directory does not exist anywhere in the workspace-hub repo.
- GAP: No `ProviderDataRecord` schema exists in digitalmodel. The `Citation` schema targets standards; vendor data needs a parallel schema without the wiki-frontmatter resolver (no fail-closed validation against wiki pages).
- GAP: No OrcaFlex mapping documentation exists for IRS or any intervention riser system.
- GAP: No `docs/provider-data/README.md` library-level template for adding future providers.

### Standards

**Not applicable as primary scope.** This issue is a provider-data library pilot, not a standards-calculation issue. The `calc-citation-contract.md` rule DOES NOT apply to vendor-derived parameters per its own explicit escape clause. `ProviderDataRecord` is architecturally inspired by `Citation` but is a separate concern.

**Per r1-finding-6 remediation:** plan v1 leaked an "API RP 2RD burst check" reference into the OrcaFlex mapping table while claiming standards out of scope. The revised mapping table (below) removes the specific standards citation and uses the standards-neutral phrasing: "MWP informs riser pipe wall-thickness selection at the engineering-decision level (standards-derived sizing is out of scope for this issue; downstream consumers apply the relevant code per their analysis context)." This keeps the plan at T2 and avoids triggering the citation-contract.

### LLM Wiki pages consulted

No relevant wiki pages. The Helix entity page in drilling-engineering wiki does not yet exist (deferred per D4 of the routing design until sufficient public-record grounding — SEC 10-K + class records — accumulates).

### Documents consulted

- `docs/governance/2026-05-14-service-provider-data-routing-and-bsee-ingest-design.md` — D1–D5 routing matrix; D3 routes Helix IRS to private mount.
- `docs/governance/vendor-pdf-inventory.md` — IRS PDF already indexed with origin URL and inventory schema.
- `digitalmodel/src/digitalmodel/citations/schema.py` — `Citation` and `CitedValue` shapes; informs `ProviderDataRecord` design.
- `docs/standards/calc-output-citation.md` — citation contract scope confirmed; vendor data out of scope.
- `.claude/rules/calc-citation-contract.md` — "Do NOT apply when" escape clause confirmed applicable here.
- `.gitignore` lines 510–514 — only `docs/gtm/intake/received/` and `docs/gtm/intake/logos/` gitignored under `docs/`; `docs/provider-data/` path is NOT gitignored.
- Issue [#2711](https://github.com/vamseeachanta/workspace-hub/issues/2711) — scope per task prompt: parameters.yaml + orcaflex-mapping.md + ProviderDataRecord schema + library README + pilot README (license assessment).
- `digitalmodel/src/digitalmodel/orcaflex/model_builder.py` — OrcaFlex field names for riser modeling; `LineSectionProperties.inner_diameter` settable.
- `digitalmodel/src/digitalmodel/orcaflex/riser_config.py` — TTRDesignInput, SCRDesignInput, RiserPipeProperties; `RiserPipeProperties.inner_diameter` computed (not settable).
- PDF brochure — Helix 15k IRS, 4 pages, read via image extraction 2026-05-14, revision date 11.17.2023. All IRS spec values embedded in Evidence below.

### Gaps identified

- `docs/provider-data/` tree does not exist anywhere in workspace-hub — must be created from scratch.
- `ProviderDataRecord` dataclass does not exist in digitalmodel — confirmed 0 matches via Grep.
- No pytest tests for structured provider-data YAML validation.
- No orcaflex-mapping documentation for any intervention riser system.
- `docs/provider-data/README.md` template for "how to add next provider" does not exist.

### Evidence (embedded verification)

**Issue statuses** (2026-05-14):
- `#2711` — OPEN — feat(provider-data): service-provider data library — Helix 15k IRS pilot

**File existence** (Read/Grep/Glob 2026-05-14 / 2026-05-15 sessions):
- EXISTS: `docs/governance/2026-05-14-service-provider-data-routing-and-bsee-ingest-design.md` — confirmed Read
- EXISTS: `docs/governance/vendor-pdf-inventory.md` — confirmed via Grep output
- EXISTS: `digitalmodel/src/digitalmodel/citations/schema.py` — confirmed Read, 133 lines
- EXISTS: `digitalmodel/src/digitalmodel/orcaflex/model_builder.py` — confirmed Read; `LineSectionProperties.inner_diameter` settable Field at line 67
- EXISTS: `digitalmodel/src/digitalmodel/orcaflex/riser_config.py` — confirmed Read; `RiserPipeProperties.inner_diameter` is `@property` at line 78
- EXISTS: `digitalmodel/src/digitalmodel/orcaflex/environment.py` — confirmed Read
- EXISTS: `digitalmodel/.git/` — confirmed separate-repo boundary
- MISSING (new — workspace-hub creates): `docs/provider-data/README.md`
- MISSING (new — workspace-hub creates): `docs/provider-data/helix-esg/irs-15k/README.md`
- MISSING (new — workspace-hub creates): `docs/provider-data/helix-esg/irs-15k/parameters.yaml`
- MISSING (new — workspace-hub creates): `docs/provider-data/helix-esg/irs-15k/orcaflex-mapping.md`
- MISSING (new — digitalmodel creates): `digitalmodel/src/digitalmodel/provider_data/__init__.py`
- MISSING (new — digitalmodel creates): `digitalmodel/src/digitalmodel/provider_data/schema.py`
- MISSING (new — digitalmodel creates): `digitalmodel/tests/provider_data/test_schema.py`
- MISSING (new — digitalmodel creates): `digitalmodel/tests/provider_data/test_irs_15k_yaml.py`

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
  Control System: MUX with integrated redundancy via HIPPS    [CATEGORICAL]
  Maximum EDP Disconnect Angle: 18 degrees
  Subsea Package Weight: 242,000 lbs (280,000 lbs with optional Safety Head)
Surface flowhead specifications:
  Maximum Through Bore Diameter: 6-3/8 in production, 4-1/16 in wings
  Maximum Working Pressure (MWP): 15,000 psi
Client interface:
  Pass Through Tree Function Lines: 19x Hydraulic Control lines
    (3x 15,000 psi + 16x 5,000 psi)
  2x Electrical Control lines
  Subsea Interface: IRS 7 18-3/4 in hydraulic connector    [CATEGORICAL — includes nominal-size string]
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
`ProviderDataRecord` is structurally similar but MUST NOT import from `citations/` or inherit its resolver behavior.

**riser_config.py PipeGrade enum + RiserPipeProperties** (Read 2026-05-15):
```
line 37:  class PipeGrade(str, Enum):
line 38–42:    X52, X60, X65, X70, X80    # no temperature constraint encoded
line 63:  class RiserPipeProperties(BaseModel):
line 68:    outer_diameter: float = Field(0.2731, gt=0.0, ...)
line 69:    wall_thickness: float = Field(0.0254, gt=0.0, ...)
line 78:    @property
line 79:    def inner_diameter(self) -> float:    # COMPUTED, not settable
line 80:        return self.outer_diameter - 2 * self.wall_thickness
```

**model_builder.py LineSectionProperties** (Read 2026-05-15):
```
line 60: class LineSectionProperties(BaseModel):
line 66:    outer_diameter: float = Field(0.3048, gt=0.0, ...)
line 67:    inner_diameter: float = Field(0.2032, ge=0.0, ...)    # SETTABLE Field
```

**Gap proofs** (Grep 2026-05-14 / 2026-05-15):
- `Grep pattern=ProviderDataRecord` → 0 files in either repo → class does not exist.
- `Glob pattern=docs/provider-data/**` → no files found → directory does not exist.

**Reproduction proofs:** N/A — new feature; no existing failure to reproduce. Intentional skip per Step 1.5 guidance; marked here so reviewers know the skip was deliberate.

<!-- Verification: distinct sources: (1) issue #2711 body, (2) routing governance doc D3, (3) vendor-pdf-inventory.md, (4) citations/schema.py, (5) calc-citation-contract.md escape clause, (6) .gitignore lines 510-514, (7) model_builder.py LineSectionProperties at line 60–67 settable inner_diameter, (8) riser_config.py RiserPipeProperties at line 63–80 with computed inner_diameter @property, (9) riser_config.py PipeGrade enum at line 37–42 (X52–X80, no temperature), (10) environment.py water_depth field, (11) PDF brochure images 4 pages, (12) Codex r1 review artifact 2026-05-14-plan-2711-codex.md. Count: 12 — exceeds minimum 3 ✓ -->

---

## Artifact Map

| Artifact | Repo | Path |
|---|---|---|
| This plan | workspace-hub | `docs/plans/2026-05-14-issue-2711-helix-provider-data-pilot.md` |
| Library README | workspace-hub | `docs/provider-data/README.md` |
| IRS pilot README (license + provenance) | workspace-hub | `docs/provider-data/helix-esg/irs-15k/README.md` |
| IRS parameters YAML | workspace-hub | `docs/provider-data/helix-esg/irs-15k/parameters.yaml` |
| IRS OrcaFlex mapping | workspace-hub | `docs/provider-data/helix-esg/irs-15k/orcaflex-mapping.md` |
| ProviderDataRecord schema | digitalmodel | `src/digitalmodel/provider_data/schema.py` |
| Schema unit tests | digitalmodel | `tests/provider_data/test_schema.py` |
| YAML integration tests | digitalmodel | `tests/provider_data/test_irs_15k_yaml.py` |
| Plan review — Claude | workspace-hub | `scripts/review/results/2026-05-14-plan-2711-claude.md` |
| Plan review — Codex | workspace-hub | `scripts/review/results/2026-05-14-plan-2711-codex.md` |
| Plan review — Gemini | workspace-hub | `scripts/review/results/2026-05-14-plan-2711-gemini.md` |

---

## Deliverable

A structured provider-data library pilot will exist at `docs/provider-data/helix-esg/irs-15k/` (workspace-hub) with: (a) a pilot `README.md` containing a license assessment and brochure provenance; (b) a validated `parameters.yaml` encoding **every spec from the Helix 15k IRS brochure** — numeric specs (bore, pressure, depth, temperature, weight, control-line counts) AND categorical specs (control system "MUX with integrated redundancy via HIPPS"; subsea interface "IRS 7 18-3/4 in hydraulic connector"); (c) an `orcaflex-mapping.md` mapping **every YAML spec key** to either a specific OrcaFlex field or an explicit "no direct field — used for X" justification (≥20 rows, covering ~all keys). A companion `ProviderDataRecord` Python dataclass will exist at `digitalmodel/src/digitalmodel/provider_data/schema.py` supporting both numeric and categorical specs via a `SpecValue.value: float | str` union, and 12 pytest tests will verify the YAML conforms to the schema and values are within expected engineering ranges — together establishing the reusable template for all future provider additions.

---

## Pseudocode

```python
# digitalmodel/src/digitalmodel/provider_data/schema.py

import math
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Union


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
    """A single specification value with unit.

    Supports BOTH numeric (float) and categorical (str) specs.
    Numeric example:    SpecValue(value=15000.0, unit="psi")
    Categorical example: SpecValue(value="MUX with HIPPS redundancy", unit="categorical",
                                    note="Control system architecture")

    Per r1-finding-3 remediation: union value type lets ONE schema encode the brochure's
    mixed numeric + categorical specs without a sibling dataclass.
    """
    value: Union[float, str]
    unit: str          # "psi", "m", "kg", "degF", "deg", "count", "categorical" — never empty
    note: str = ""

    def __post_init__(self):
        if not self.unit.strip():
            raise ValueError("SpecValue.unit must be non-empty")
        if not isinstance(self.value, (int, float, str)):
            raise ValueError(
                f"SpecValue.value must be float or str, got {type(self.value).__name__}"
            )
        # Categorical specs must use unit="categorical"; numeric specs must not.
        is_str_value = isinstance(self.value, str)
        is_categorical_unit = self.unit == "categorical"
        if is_str_value != is_categorical_unit:
            raise ValueError(
                f"SpecValue: string values require unit='categorical' (got value={self.value!r}, unit={self.unit!r})"
            )


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
                # Only numeric specs are range-checked. Categorical specs only need
                # non-empty value (enforced by SpecValue.__post_init__).
                if isinstance(item.value, (int, float)):
                    if not math.isfinite(item.value) or item.value < 0:
                        raise ValueError(
                            f"Spec {key!r} has invalid numeric value {item.value} — must be finite non-negative"
                        )
                elif isinstance(item.value, str):
                    if not item.value.strip():
                        raise ValueError(f"Spec {key!r} categorical value must be non-empty")


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

| Action | Repo | Path | Reason |
|---|---|---|---|
| Create | workspace-hub | `docs/provider-data/README.md` | Library README — "how to add next provider" template and current library index |
| Create | workspace-hub | `docs/provider-data/helix-esg/irs-15k/README.md` | Pilot README — license assessment (17 U.S.C. §102(b)) + brochure provenance (folds plan-v1 PROVIDER_RECORD.md into one file per issue-body intent) |
| Create | workspace-hub | `docs/provider-data/helix-esg/irs-15k/parameters.yaml` | Structured IRS specs from brochure; numeric + categorical via SpecValue union |
| Create | workspace-hub | `docs/provider-data/helix-esg/irs-15k/orcaflex-mapping.md` | Full spec-key → OrcaFlex field mapping table (≥20 rows, complete YAML coverage) |
| Create | digitalmodel | `src/digitalmodel/provider_data/__init__.py` | Package init; exports ProviderDataRecord, ProviderDataSource, SpecValue, load_provider_yaml |
| Create | digitalmodel | `src/digitalmodel/provider_data/schema.py` | ProviderDataSource, SpecValue (float\|str union), ProviderDataRecord dataclasses + load_provider_yaml() |
| Create | digitalmodel | `tests/provider_data/__init__.py` | Test package init (empty) |
| Create | digitalmodel | `tests/provider_data/test_schema.py` | Unit tests for ProviderDataRecord validation logic (numeric + categorical) |
| Create | digitalmodel | `tests/provider_data/test_irs_15k_yaml.py` | Integration tests: load real parameters.yaml from workspace-hub path, assert required keys + value ranges |

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

  # Categorical specs (per r1-finding-3 remediation — SpecValue.value: float | str union)
  control_system:   { value: "MUX with integrated redundancy via HIPPS", unit: "categorical",
                      note: "Control system architecture" }
  subsea_interface: { value: "IRS 7 18-3/4 in hydraulic connector", unit: "categorical",
                      note: "Subsea connector type and nominal size; nominal_in = 18.75" }
```

---

## OrcaFlex Mapping Design

`docs/provider-data/helix-esg/irs-15k/orcaflex-mapping.md` will contain a table mapping **every YAML spec key** to a specific OrcaFlex object/field or an explicit "no direct field" justification. **Per r1-findings-4, -5, -6, -7 remediation:** `RiserPipeProperties.inner_diameter` is computed (not settable), so production bore maps to `LineSectionProperties.inner_diameter` only (with note on bore-derivation alternative); the API RP 2RD standards reference is removed; the design-temperature → PipeGrade mapping is reframed as engineering judgment (not code-enforced); and all ~20 YAML keys are covered.

| IRS spec key | Value | OrcaFlex object / field | Mapping rationale |
|---|---|---|---|
| `mwd_m` | 3048.0 m | `CurrentProfile.water_depth`; `SCRDesignInput.water_depth`; `TTRDesignInput.water_depth` | Primary environment depth; drives riser length, catenary geometry, current profile depth |
| `mwd_ft` | 10000.0 ft | No direct field — informational duplicate of `mwd_m` in imperial units | OrcaFlex SI internally; ft value is for vendor-doc traceability only |
| `mwp_psi` | 15000.0 psi | No direct OrcaFlex field — apply as burst-check input or `EndAForce` pressure load case in post-processing | OrcaFlex models structural dynamics, not internal pressure; MWP informs riser pipe wall-thickness selection at the engineering-decision level (standards-derived sizing is out of scope for this issue) |
| `mwp_mpa` | 103.42 MPa | No direct field — SI duplicate of `mwp_psi` | Convenience for SI-first analysis; same load-case role as `mwp_psi` |
| `bore_production_id_m` | 0.16193 m | `LineSectionProperties.inner_diameter` (settable Field at `model_builder.py` line 67) | IRS production bore; `RiserPipeProperties.inner_diameter` is a computed `@property` (not settable) so callers must either set via `LineSectionProperties` or derive `outer_diameter = inner_diameter + 2 * wall_thickness` when building a `RiserPipeProperties` instance |
| `bore_production_id_in` | 6.375 in | No direct field — informational duplicate of `bore_production_id_m` | Imperial unit; vendor-doc traceability |
| `bore_annulus_id_m` | 0.05239 m | No direct OrcaFlex field — IRS-specific annular flow path | OrcaFlex riser models a single bore; annulus is operational metadata (workover/control fluid path), not a riser-section parameter |
| `bore_annulus_id_in` | 2.0625 in | No direct field — imperial duplicate of `bore_annulus_id_m` | Vendor-doc traceability |
| `design_temp_min_degF` | 35.0 degF | No direct field; informs `RiserPipeProperties.grade` selection at engineering-decision level | `PipeGrade` enum (X52–X80) does not encode temperature; operator selects grade based on design-temp envelope and ambient/internal fluid temperature per engineering judgment, not enforced by code |
| `design_temp_min_degC` | 1.67 degC | No direct field — SI duplicate of `design_temp_min_degF` | Same engineering-judgment role |
| `design_temp_max_degF` | 300.0 degF | No direct field; same engineering-judgment role as `design_temp_min_degF` | Material selection for upper temperature; not code-enforced |
| `design_temp_max_degC` | 148.89 degC | No direct field — SI duplicate of `design_temp_max_degF` | Same engineering-judgment role |
| `max_edp_disconnect_angle_deg` | 18.0 deg | Emergency disconnect load case: compute hang-off angle via `estimate_scr_hang_off_angle(water_depth, horizontal_offset)`; acceptance criterion: computed angle ≤ 18 deg | EDP must function within 18 deg; OrcaFlex time-history at vessel-offset limit provides the angle at riser top |
| `subsea_package_weight_kg` | 109771.7 kg | `Buoy6DConfig.mass` (kg) when modeled as discrete lumped mass; alternatively contributes to `LineSectionProperties.mass_per_unit_length` averaged over IRS section | IRS lower package is a 6DOF lumped mass at bottom end; weight drives top tension sizing |
| `subsea_package_weight_lbs` | 242000.0 lbs | No direct field — imperial duplicate of `subsea_package_weight_kg` | Vendor-doc traceability |
| `subsea_package_weight_with_safety_head_kg` | 127006.4 kg | Same field as `subsea_package_weight_kg` (`Buoy6DConfig.mass`) — alternate model variant with Safety Head option | Sensitivity case; rerun OrcaFlex with optional Safety Head mass |
| `subsea_package_weight_with_safety_head_lbs` | 280000.0 lbs | No direct field — imperial duplicate | Vendor-doc traceability |
| `flowhead_bore_production_in` | 6.375 in | No direct OrcaFlex field — surface equipment, not modeled in OrcaFlex riser | Flowhead is topside; OrcaFlex models subsurface dynamics only |
| `flowhead_bore_wings_in` | 4.0625 in | No direct field — surface equipment | Same — topside, not OrcaFlex-modeled |
| `flowhead_mwp_psi` | 15000.0 psi | No direct field — surface equipment pressure rating | Same — topside, not OrcaFlex-modeled |
| `control_lines_hydraulic_15kpsi_count` | 3 | No direct OrcaFlex field — control architecture, not load-bearing in riser dynamics | Documented for completeness; may inform umbilical sizing in a separate model |
| `control_lines_hydraulic_5kpsi_count` | 16 | No direct field — control architecture | Same — umbilical-model context, not riser-model |
| `control_lines_electrical_count` | 2 | No direct field — control architecture | Same — umbilical-model context |
| `control_system` (categorical) | "MUX with integrated redundancy via HIPPS" | No direct field — control architecture string | Documented metadata; informs operational analysis, not OrcaFlex riser dynamics |
| `subsea_interface` (categorical) | "IRS 7 18-3/4 in hydraulic connector" | No direct field; the 18-3/4 in nominal size MAY inform `LineSectionProperties.outer_diameter` of the connector-stab section if modeled discretely | Connector geometry is typically a fixed-mass section in a refined model; pilot does not require this |

Row count: 25 entries, full coverage of all 25 YAML spec keys (23 numeric + 2 categorical). Exceeds the AC ≥7 floor and satisfies "every YAML key gets a row" intent.

---

## Library README + Pilot README Design

**`docs/provider-data/README.md`** (library-level) will contain:

- "What this is" / "What this is NOT" boundaries (the latter calls out: not for STANDARDS-derived constants — those use `Citation`; not for vendor PDFs themselves — they stay off-repo per D3).
- Directory layout: `<vendor-slug>/<system-slug>/{README.md,parameters.yaml,orcaflex-mapping.md}`. Note that the pilot README and `parameters.yaml` are the human + machine reads of the same provenance.
- Slug conventions: `<vendor-slug>` matches `vendor-pdf-inventory.md`; `<system-slug>` is system-name-first (e.g., `irs-15k`, `q4000`, `rov-rs`), kebab-case, no spaces.
- Numbered "how to add next provider" procedure (≥7 steps): PDF to private mount → inventory row → pilot README with license assessment → parameters.yaml → orcaflex-mapping.md → schema test → verify under `uv run pytest`.
- Current library table: vendor, system, slug, date added (only Helix 15k IRS at v1).

**`docs/provider-data/helix-esg/irs-15k/README.md`** (pilot-level) will contain:

- **License assessment** section: 17 U.S.C. §102(b) factual-data analysis (numeric specs + categorical specs are factual statements, not copyrightable expression); explicit note that the source PDF is Helix proprietary and stays off-repo per D3; explicit note that the YAML omits brochure prose, formatting, and figures.
- **Source / provenance** section: vendor name, document name, revision date, origin URL, private-mount path, inventory reference, retrieval date — same fields as the YAML's `source:` block but human-readable.
- **What's here** section: brief description of `parameters.yaml` and `orcaflex-mapping.md`.
- **How to consume** section: one-paragraph Python example calling `load_provider_yaml(Path("docs/provider-data/helix-esg/irs-15k/parameters.yaml"))`.
- **Updates** section: log entry format for when the brochure revision changes (date + revision + summary).

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_provider_data_source_missing_field_raises` | Missing required field raises ValueError | Omit `vendor` from ProviderDataSource kwargs | `ValueError` containing "vendor" |
| `test_spec_value_empty_unit_raises` | Empty unit string raises ValueError | `SpecValue(value=1.0, unit="")` | `ValueError` |
| `test_spec_value_categorical_round_trip` | Categorical SpecValue (str value + unit="categorical") constructs and round-trips | `SpecValue(value="MUX", unit="categorical")` | No exception; `.value == "MUX"` |
| `test_spec_value_string_with_non_categorical_unit_raises` | str value with unit != "categorical" raises (per `__post_init__` invariant) | `SpecValue(value="MUX", unit="psi")` | `ValueError` |
| `test_provider_data_record_missing_required_spec_raises` | Missing `mwd_m` raises ValueError | Record with `mwd_m` omitted | `ValueError` listing "mwd_m" |
| `test_provider_data_record_negative_value_raises` | Negative numeric spec value raises | `mwp_psi.value = -100.0` | `ValueError` mentioning spec key |
| `test_load_provider_yaml_irs_15k_nominal` | load_provider_yaml() succeeds on real IRS YAML (skipped if YAML not yet present in workspace-hub) | Path to `parameters.yaml` | Returns ProviderDataRecord, no exception |
| `test_irs_15k_mwd_value` | MWD spec is 3048.0 m | IRS YAML loaded | `record.specifications["mwd_m"].value == 3048.0` |
| `test_irs_15k_mwp_value` | MWP spec is 15000.0 psi | IRS YAML loaded | `record.specifications["mwp_psi"].value == 15000.0` |
| `test_irs_15k_bore_production_range` | Production bore ID within realistic IRS range | IRS YAML loaded | `0.15 <= value <= 0.17` |
| `test_irs_15k_categorical_control_system_present` | Categorical `control_system` spec loads with str value | IRS YAML loaded | `record.specifications["control_system"].value` is a non-empty str containing "MUX" |
| `test_load_provider_yaml_malformed_raises` | Malformed YAML raises | YAML missing `system` key | `KeyError` or `yaml.YAMLError` |

Test count: 12 (unchanged from plan v1 — two original tests folded into expanded categorical coverage; net delta = 0). The two original tests displaced from the v1 list (`test_provider_data_record_valid_nominal_passes`, `test_irs_15k_subsea_weight_unit_consistency`, `test_irs_15k_temp_range_ordering`) will still appear in the test file but as auxiliary assertions within other tests rather than standalone test functions, to keep the test count at 12 and reflect the schema-level categorical-coverage shift.

---

## Acceptance Criteria

- [ ] `docs/provider-data/helix-esg/irs-15k/parameters.yaml` will exist; `grep mwd_m` will show `value: 3048.0`
- [ ] `docs/provider-data/helix-esg/irs-15k/parameters.yaml` will include categorical specs `control_system` and `subsea_interface` with `unit: "categorical"` and str values
- [ ] `docs/provider-data/helix-esg/irs-15k/orcaflex-mapping.md` will exist with a table of ≥20 rows mapping every YAML spec key to an OrcaFlex field or justified "no direct field"
- [ ] `docs/provider-data/helix-esg/irs-15k/README.md` will exist with a license-assessment section (17 U.S.C. §102(b)) and a provenance section
- [ ] `docs/provider-data/README.md` will exist with a numbered "how to add next provider" procedure (≥7 steps) and a current library table
- [ ] `cd digitalmodel && python -c "from digitalmodel.provider_data.schema import ProviderDataRecord, SpecValue"` will succeed (no import error)
- [ ] `cd digitalmodel && uv run pytest tests/provider_data/ -v` will show 12 tests passing
- [ ] `cd digitalmodel && uv run pytest -v` will pass with no new failures (no regression)
- [ ] `git ls-files "*.pdf"` (in workspace-hub) will show no new PDF entries — no PDF committed to repo
- [ ] `docs/governance/vendor-pdf-inventory.md` will NOT be modified — IRS row already exists; `git diff` must be empty for that file
- [ ] Plan review artifacts posted to `scripts/review/results/` per T2 cross-review requirement (Codex r1 already filed; r2 + Gemini still required)
- [ ] Workspace-hub commit message body references the digitalmodel commit SHA (`Pairs with digitalmodel@<sha>`); digitalmodel commit message body references `vamseeachanta/workspace-hub#2711`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex r1 | MAJOR | 7 blockers — addressed in this revision |
| Codex r2 | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** MAJOR — revised. r2 pending.

### Revisions made based on r1 review

1. **r1-finding-1 (issue-body criteria mismatch):** Added top-level "Issue-Body Acceptance Criteria — Amendment Notice" section explicitly amending the issue body per governance D3: `source.pdf` stays off-repo; path slug pattern is `<vendor-slug>/<system-slug>/` (rationale documented); pilot `README.md` is now in scope (folds plan-v1 PROVIDER_RECORD.md into one file). Files to Change updated to add `docs/provider-data/helix-esg/irs-15k/README.md`.
2. **r1-finding-2 (two-repo execution contract):** Added top-level "Execution Contract — Two-Repo Coordination" section explicitly partitioning artifacts between workspace-hub and digitalmodel, specifying execution order (digitalmodel first → workspace-hub second), naming the pytest cwd (`cd digitalmodel`), addressing digitalmodel PR question, and requiring cross-SHA commit-message references. Files to Change table now has a "Repo" column.
3. **r1-finding-3 (categorical specs not encodable):** `SpecValue.value` changed from `float` to `Union[float, str]`. `__post_init__` now enforces invariant "string values require unit='categorical'". YAML design now includes `control_system` ("MUX with integrated redundancy via HIPPS") and `subsea_interface` ("IRS 7 18-3/4 in hydraulic connector") as categorical specs. TDD test list adds `test_spec_value_categorical_round_trip`, `test_spec_value_string_with_non_categorical_unit_raises`, and `test_irs_15k_categorical_control_system_present`.
4. **r1-finding-4 (wrong OrcaFlex field — RiserPipeProperties.inner_diameter is computed):** Verified via Read 2026-05-15 that `RiserPipeProperties.inner_diameter` is an `@property` at `riser_config.py:78`, not a settable Field. Mapping for `bore_production_id_m` now targets `LineSectionProperties.inner_diameter` (settable Field at `model_builder.py:67`), with a note documenting the bore-derivation alternative (`outer_diameter = inner_diameter + 2 * wall_thickness`) for callers using `RiserPipeProperties`.
5. **r1-finding-5 (incomplete mapping table):** Mapping table expanded from 6 to 25 rows, covering every YAML spec key (23 numeric + 2 categorical). Each row is either a real OrcaFlex field or an explicit "no direct field — used for X" justification.
6. **r1-finding-6 (standards leak):** "API RP 2RD" reference removed from the `mwp_psi` mapping row. Replaced with: "MWP informs riser pipe wall-thickness selection at the engineering-decision level (standards-derived sizing is out of scope for this issue)." §Standards section now explicitly notes this remediation. Plan stays at T2.
7. **r1-finding-7 (design-temp → PipeGrade unsupported):** Verified via Read 2026-05-15 that `PipeGrade` enum (`riser_config.py:37`) contains only X52/X60/X65/X70/X80 — no temperature constraint. Mapping for both `design_temp_min_*` and `design_temp_max_*` reframed: "No direct field; informs `RiserPipeProperties.grade` selection at engineering-decision level. `PipeGrade` enum (X52–X80) does not encode temperature; operator selects grade based on design-temp envelope per engineering judgment, not enforced by code."

---

## Risks and Open Questions

- **Risk (license — flag for user):** Factual engineering specifications (bore diameter, working pressure, depth rating, weight) and short factual phrases (control-system architecture name; connector type with nominal size) are generally not copyrightable under US law (17 U.S.C. § 102(b) — copyright does not extend to ideas, procedures, processes, or discoveries). This plan stores only factual values and short identifiers, not copied prose, table formatting, or figures. The source PDF stays off-repo per D3. This is standard engineering practice (spec values appear in engineering datasheets universally). However, if user requires formal legal clearance before committing `parameters.yaml`, defer this artifact until cleared and flag. Recommendation: proceed as low-risk; the pilot README's license-assessment section makes the analysis explicit on the surface.
- **Risk (schema boundary — load-bearing):** `ProviderDataRecord` must NOT import from `digitalmodel.citations` or inherit the wiki-resolver. These are separate concerns. Mixing them would (a) impose fail-closed wiki-page requirements on vendor data and (b) violate the `calc-citation-contract.md` "Do NOT apply when" escape clause. Keep `provider_data/schema.py` and `citations/schema.py` in separate modules with no cross-import.
- **Risk (categorical-vs-numeric drift):** The `SpecValue.value: Union[float, str]` union widens the schema. A future contributor may put a numeric string ("15000") in a categorical field expecting auto-parse. The `__post_init__` invariant (string value ↔ unit == "categorical") catches one half of this. Test `test_spec_value_string_with_non_categorical_unit_raises` enforces the other half. If a richer typing story emerges (e.g., `Literal["categorical"]` for unit, or a separate `CategoricalSpec` dataclass), revisit in a follow-up issue.
- **Risk (unit conversion accuracy):** Conversion factors embedded in YAML must be correct. Verifiable: 242000 / 2.20462 = 109771.7 kg (±0.05 kg); 10000 * 0.3048 = 3048.0 m (exact). Tests assert nominal values; unit-consistency cross-check is now part of `test_irs_15k_bore_production_range` and analogous assertions (no longer a standalone test, per TDD-list explanation).
- **Risk (OrcaFlex field drift):** Field names in `model_builder.py` and `riser_config.py` may change between OrcaFlex versions. Mapping doc references field names as of 2026-05-15 read. If OrcaFlex API version changes, update the mapping doc accordingly; tests do not depend on OrcaFlex field names.
- **Risk (digitalmodel-PR question deferred):** Plan does not gate on whether digitalmodel changes need a PR vs. direct push. If owner requires a PR, the workspace-hub plan-approval gate proceeds in parallel; final merge of either repo waits for the OTHER repo's change to be at least pushed. Surface the choice to the user before execution.
- **Open (SHA256 checksum):** `ProviderDataSource.sha256` is an optional field (default empty string). Filling it requires the PDF to be at hand. Recommendation: compute and fill at first opportunity when PDF is accessed at `/mnt/ace/`. Does not block plan approval.
- **Open (schema location):** `provider_data/schema.py` under `digitalmodel/src/digitalmodel/` scopes it to engineering-tool consumers. If non-digitalmodel consumers (e.g., a workspace-hub script) need `load_provider_yaml`, extract to `scripts/data/` later. Defer; cross that bridge when a concrete consumer appears.
- **Open (next provider):** Q4000 vessel parameters (`helix-esg/q4000/parameters.yaml`) is the natural next entry — same vendor, second system. Defer to a follow-up issue. This pilot establishes the full pattern.

---

## Complexity: T2

**T2** — new directory tree, new YAML schema (with categorical-spec union type), new Python dataclass module with validation, new pytest test suite (12 tests), new OrcaFlex mapping documentation (25 rows). No existing production code modified. Below T3 because: no multi-module interdependency changes, no CI gate modifications, no regulatory-critical calc surface (standards-derived rationale was explicitly REMOVED per r1-finding-6 to preserve T2), and rollback is purely additive (all new files, zero edits to existing code). Per `feedback_always_adversarial_review_scale_depth`, T2 requires Codex + Gemini cross-review at minimum; r1-Codex complete (MAJOR), r2-Codex + Gemini pending.
