# Plan for #2510: Python layout/CAD automation demo for chip/package geometries

> **Status:** plan-review — r7 MAJOR findings patched; r8 adversarial review pending
> **Complexity:** T2
> **Date:** 2026-04-26
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2510
> **Review artifacts (r1 archive):** scripts/review/results/2026-04-26-plan-2510-claude-r1.md | scripts/review/results/2026-04-26-plan-2510-codex-r1.md | scripts/review/results/2026-04-26-plan-2510-gemini-r1.md
> **Review artifacts (r2 archive):** scripts/review/results/2026-04-26-plan-2510-claude-r2.md | scripts/review/results/2026-04-26-plan-2510-codex-r2.md | scripts/review/results/2026-04-26-plan-2510-gemini-r2.md
> **Review artifacts (r3 archive):** scripts/review/results/2026-04-26-plan-2510-claude-r3.md | scripts/review/results/2026-04-26-plan-2510-codex-r3.md | scripts/review/results/2026-04-26-plan-2510-gemini-r3.md
> **Review artifacts (r4 archive):** scripts/review/results/2026-04-26-plan-2510-claude-r4.md | scripts/review/results/2026-04-26-plan-2510-codex-r4.md | scripts/review/results/2026-04-26-plan-2510-gemini-r4.md
> **Review artifacts (r5 archive):** scripts/review/results/2026-04-26-plan-2510-claude-r5.md | scripts/review/results/2026-04-26-plan-2510-codex-r5.md | scripts/review/results/2026-04-26-plan-2510-gemini-r5.md
> **Review artifacts (r6 archive):** scripts/review/results/2026-04-26-plan-2510-claude-r6.md | scripts/review/results/2026-04-26-plan-2510-codex-r6.md | scripts/review/results/2026-04-26-plan-2510-gemini-r6.md
> **Review artifacts (r7 current/canonical):** scripts/review/results/2026-04-26-plan-2510-claude.md | scripts/review/results/2026-04-26-plan-2510-codex.md | scripts/review/results/2026-04-26-plan-2510-gemini.md
> **Review artifacts (r7 archive after run):** scripts/review/results/2026-04-26-plan-2510-claude-r6.md | scripts/review/results/2026-04-26-plan-2510-codex-r6.md | scripts/review/results/2026-04-26-plan-2510-gemini-r6.md

---

## Resource Intelligence Summary

### Existing repo code

- `gh issue view 2510` confirms the live issue is OPEN and asks for a Python-first layout/CAD automation example using KLayout scripting and/or GDSFactory, deterministic exports, metadata extraction, tests, and documentation.
- Search for `gdsfactory|klayout|gdstk|gdspy|GDS|OASIS` in `*.py` returned no existing Python semiconductor layout implementation in the repo. This issue must create the implementation from scratch.
- `scripts/semiconductor/package_fem_benchmark.py` now exists from #2511 and establishes the semiconductor lane convention for scripts under `scripts/semiconductor/`, tests under `tests/semiconductor/`, and generated artifacts under `data/semiconductor/`. #2511 writes its report under `docs/reports/`; #2510 intentionally keeps the generated report inside `data/semiconductor/layout_cad_demo/` to keep manifest paths deterministic and co-located for this layout-demo issue.
- `tests/semiconductor/test_package_fem_benchmark.py` provides a nearby pattern for deterministic artifact contracts, CLI tests, SHA256 manifests, SVG/report checks, and guardrails against overclaiming compliance.

### Standards

| Standard / registry | Status | Source |
|---|---|---|
| GDSII / OASIS layout exchange | Open-tool practice anchor, not a locally licensed standard | Issue #2510 requires a real `.gds` artifact generated through open Python tooling. OASIS may be mentioned as context only; no `GDS-like`, JSON-only, placeholder, or fake layout artifact can satisfy closeout. |
| JEDEC / IPC semiconductor packaging standards | Restricted / not locally ingested | #2508 and #2511 guardrails apply: use terminology only; do not claim compliance or signoff. |
| `data/design-codes/code-registry.yaml` | Exists but offshore/mechanical oriented | Not a source for chip-layout rules; cite only as checked/non-applicable for this CAD/layout demo. |

### LLM Wiki pages consulted

- Search for semiconductor/ASIC/OpenROAD/OpenLane/GDSFactory/KLayout in local knowledge/wiki surfaces found no reusable semiconductor layout wiki page. #2510 should create a report/demo rather than pretending a local knowledge base already exists.

### Documents consulted

- `docs/roadmaps/chip-design-cad-fem-career-roadmap.md` — defines the chip-design CAD/FEM career lane and includes a layout/CAD automation demo step; it does not itself map issue numbers.
- `docs/plans/2026-04-26-issue-2508-semiconductor-cad-fem-knowledge-base.md` — identifies KLayout and GDSFactory as relevant open-source practice anchors and links #2510 as a downstream implementation issue.
- `docs/reports/semiconductor-cad-fem-knowledge-base.md` — maps layout/CAD automation roles to Python, KLayout/GDSFactory, and geometry metadata; deterministic checked-in portfolio artifacts are an implementation pattern inherited from #2511, not quoted wording from this report.
- `docs/plans/2026-04-27-issue-2511-semiconductor-package-fem-benchmark.md` and its landed implementation — establishes generated-artifact/report/test patterns for the same semiconductor lane.
- External docs checked 2026-04-26: GDSFactory docs (`https://gdsfactory.github.io/gdsfactory/`, title `GDSFactory 9.40.2`; execution pins `gdsfactory==9.40.2`), KLayout docs (`https://www.klayout.de/doc.html`), KLayout Python API (`https://www.klayout.de/doc/programming/python.html`), gdstk docs (`https://heitzmann.github.io/gdstk/`), and GDSFactory GitHub (`https://github.com/gdsfactory/gdsfactory`). These are reachability/tool-surface checks, not compliance sources.

### Engineering retrieval bundle checked

Because #2510 carries `cat:engineering`, the engineering retrieval bundle from `docs/plans/README.md` was checked:

- `data/document-index/standards-transfer-ledger.yaml`: 436 standards-ledger entries, largely offshore/API/DNV/mechanical; no semiconductor layout/Pdk/GDS design-rule standard source found for #2510. Non-applicable except as evidence that local standards inventory does not supply chip-layout signoff rules.
- `data/design-codes/code-registry.yaml`: offshore/mechanical design-code registry; no chip-layout DRC/LVS/GDS rule deck authority.
- `data/document-index/online-resource-registry.yaml`: 247 online resources; CAD domain exists but registry is not a semiconductor PDK/GDSFactory authority for this issue. External GDSFactory/KLayout docs remain the relevant open-tool anchors.
- `docs/document-intelligence/data-intelligence-map.md`: confirms the standards ledger, online registry, and intelligence entry points; no semiconductor-layout-specific local corpus path identified.
- Local wiki/knowledge search for semiconductor/ASIC/OpenROAD/OpenLane/GDSFactory/KLayout found no reusable semiconductor layout wiki page; #2510 must create a bounded demo and report rather than claim local signoff knowledge.

### Gaps identified

- No `scripts/semiconductor/layout_cad_demo.py` exists.
- No `tests/semiconductor/test_layout_cad_demo.py` exists.
- No generated chip/package layout artifacts exist under `data/semiconductor/layout_cad_demo/`.
- No metadata extraction report exists for a deterministic chip/package geometry layout demo.
- Local Python environment currently lacks `gdsfactory`, `klayout`, `gdstk`, and `gdspy`; this plan therefore requires the execution step to install or invoke an open layout dependency explicitly, with `gdsfactory` as the primary target. A pure-Python fallback is not sufficient to close #2510 because the issue explicitly asks to use KLayout scripting and/or GDSFactory and to export/import GDS/OASIS where practical.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-26T22:28:55-05:00 via `gh issue view`):
- `#2510` — OPEN — `feat(cad): build Python layout/CAD automation demo for chip/package geometries`
- `#2508` — CLOSED — research/job taxonomy foundation is complete.
- `#2511` — CLOSED — FEM benchmark foundation is complete.

**File/tool checks:**

```text
find docs/plans -maxdepth 1 -type f -iname '*2510*' -> docs/plans/2026-04-26-issue-2510-python-layout-cad-automation-demo.md exists locally and must be pushed to main before each approval-routing review for traceability
Python package availability probe:
gdsfactory False
klayout False
gdstk False
gdspy False
```

**Repository search proof:**

```text
search_files('gdsfactory|klayout|pya\.|gdspy|gdstk|OASIS|GDS', file_glob='*.py') -> no relevant Python layout implementation matches
```


**GDSFactory API probe (2026-04-26):**

```text
uv run --python 3.11 --with gdsfactory==9.40.2 --with kfactory==2.4.7 --with klayout==0.30.8 --with numpy==2.4.4 --with shapely==2.1.2 python - <<'PY'
import inspect, gdsfactory as gf
from gdsfactory.read import import_gds
from kfactory.utilities import save_layout_options
opts = save_layout_options()
print(gf.__version__)                              # 9.40.2
print(inspect.signature(gf.Component.write_gds))   # (self, gdspath=None, gdsdir=None, save_options: kdb.SaveLayoutOptions | None = None, ...)
print(getattr(opts, "gds2_write_timestamps", None)) # False
PY
```

Finding: use `from gdsfactory.read import import_gds`; write deterministic GDS with `save_layout_options()` / `gds2_write_timestamps=False` passed to `Component.write_gds(save_options=...)`.

**External anchor proof:**

```text
GDSFactory docs|https://gdsfactory.github.io/gdsfactory/|status=200|title=GDSFactory 9.40.2 — GDSFactory
KLayout docs|https://www.klayout.de/doc.html|status=200|title=KLayout Layout Viewer And Editor
KLayout Python API|https://www.klayout.de/doc/programming/python.html|status=200|title=KLayout Layout Viewer And Editor
gdstk docs|https://heitzmann.github.io/gdstk/|status=200|title=Gdstk Documentation — gdstk 1.0.0 documentation
```

Source count: issue body, roadmap, #2508 plan/report, #2511 implementation, external open-tool docs, local package probe.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-26-issue-2510-python-layout-cad-automation-demo.md` |
| Plan index | `docs/plans/README.md` |
| Implementation CLI/module | `scripts/semiconductor/layout_cad_demo.py` |
| TDD tests | `tests/semiconductor/test_layout_cad_demo.py` |
| Generated artifact directory | `data/semiconductor/layout_cad_demo/` |
| Metadata JSON | `data/semiconductor/layout_cad_demo/layout_metadata.json` |
| Geometry table | `data/semiconductor/layout_cad_demo/geometry_summary.csv` |
| Human-inspectable SVG | `data/semiconductor/layout_cad_demo/layout_preview.svg` |
| GDS exchange artifact | `data/semiconductor/layout_cad_demo/chip_package_demo.gds` |
| GDS read-back metadata | `data/semiconductor/layout_cad_demo/gds_readback_metadata.json` |
| Manifest | `data/semiconductor/layout_cad_demo/artifact_manifest.sha256` |
| Portfolio report | `data/semiconductor/layout_cad_demo/semiconductor-layout-cad-automation-demo.md` |
| Plan reviews | `scripts/review/results/2026-04-26-plan-2510-{claude,codex,gemini}.md` |

---

## Deliverable

A reproducible Python layout/CAD automation demo that generates a deterministic chip/package geometry layout, exports human-inspectable artifacts and metadata, validates geometry invariants with tests, and explains relevance to chip-design/package CAD roles without requiring proprietary tools.

---

## Scope Boundaries

In scope:
- Parameterized geometry for a simple package/interposer-style layout: die, substrate/interposer outline, bump/pad array, routing/keepout markers, and named layers.
- Deterministic artifact generation from a CLI.
- Metadata extraction: layers, polygons/rectangles, bounding boxes, area totals, ports/pads, net labels where represented, geometry invariants, and artifact hashes.
- SVG preview and JSON/CSV metadata always generated.
- Real GDS exchange artifact generated with an open Python layout tool. Primary path: GDSFactory (`gdsfactory`) creates the parameterized component and writes `chip_package_demo.gds`. KLayout scripting may be used as a secondary/import validation path if available.
- Import/read-back of the generated GDS using the pinned GDSFactory 9.40.2 API `from gdsfactory.read import import_gds` to verify bounding boxes/layer counts/invariants after round-trip. No alternate reader is allowed inside #2510 without plan revision.
- If `gdsfactory` cannot be installed or invoked in the execution environment, implementation must stop and post a blocker/future-dependency issue rather than silently closing with a pure JSON fallback.

Out of scope:
- OpenROAD/OpenLane RTL-to-GDS flow (#2509 owns that).
- FEM/thermal solver work (#2511 owns that).
- Foundry PDK-specific design rules, DRC/LVS signoff, JEDEC/IPC compliance, or production tapeout claims.
- Installing proprietary EDA tools.

---

## CLI and Dependency Contract

- Main command shape intentionally mirrors the #2511 argv convention. #2510 may reuse or adapt #2511 `_relative_link` / `manifest_hashes` helpers if the resulting manifest entries remain relative to the manifest parent and validate from the artifact directory.
  - `--output <dir>` required.
  - `--report <path>` required and must resolve under `--output`; otherwise the CLI must exit with a clear error before writing partial artifacts.
  - optional geometry parameters may be added only with deterministic defaults.
- Validation commands must use pinned transient dependency invocation `uv run --python 3.11 --with gdsfactory==9.40.2 --with kfactory==2.4.7 --with klayout==0.30.8 --with numpy==2.4.4 --with shapely==2.1.2 ...` so the required GDSFactory/kfactory/KLayout dependency surface is explicit, version-bounded, and does not change repo-wide dependencies.
- `scripts/semiconductor/layout_cad_demo.py` must expose a lazy import helper named `_load_gdsfactory()` for TDD monkeypatching. It may import GDSFactory lazily inside writer/import functions, but when generation is requested and GDSFactory is unavailable it must fail loudly with a dependency message that includes the exact `uv run --python 3.11 --with gdsfactory==9.40.2 --with kfactory==2.4.7 --with klayout==0.30.8 --with numpy==2.4.4 --with shapely==2.1.2 ...` invocation.
- No pure-Python fake `.gds` or JSON fallback can satisfy closeout.

---

## GDS Round-Trip Contract

The import/read-back test must compare only fields that are expected to survive GDS round-trip:

- Read-back must use GDSFactory 9.40.2 with primary API `from gdsfactory.read import import_gds`; if that import path is unavailable in the pinned version, implementation must stop and revise the plan rather than guessing a new API surface.
- `cell_name` equals the deterministic top component name.
- Layer identity is keyed by `(layer, datatype)` tuples, not human display names.
- Bounding boxes are compared in micrometers with absolute tolerance `1e-3` µm.
- Imported geometry must be flattened before counting. For this bounded demo geometry, compare geometry-derived expected counts per required layer (substrate, die, bump/pad, route/keepout) against read-back counts using exact equality only for layers generated as simple axis-aligned rectangles; if a layer uses non-rectangular/reader-fracturable geometry, the implementation must encode a layer-specific bounded range and document it in `gds_readback_metadata.json`. Exact label/port round-trip is not required because plain GDS labels/ports can be lossy across readers.
- Read-back metadata must state the reader package and version.

---

## Pseudocode

```text
function build_layout_spec(parameters):
    validate die/substrate dimensions, pad pitch/count, layer names, units
    compute substrate outline, die rectangle, bump array, route/keepout rectangles, and port labels
    return serializable layout model with units and provenance

function generate_geometry(spec):
    create deterministic ordered shapes by layer and name
    compute bounding boxes, areas, centroids, and net/pad labels
    assert die is inside substrate and pads are inside die/substrate envelope
    return geometry records and metadata summary

function write_svg(geometry, output_path):
    map layers to deterministic colors/styles
    emit SVG with viewBox from substrate bounding box
    include labels for die, substrate, bump array, and selected ports

function write_exchange_artifact(geometry, output_dir):
    require an open layout writer, primary: gdsfactory
    create a GDSFactory Component from deterministic rectangles/polygons/layers/labels
    write chip_package_demo.gds
    record writer package/version in metadata

function import_exchange_artifact(gds_path):
    read chip_package_demo.gds back through the pinned API `from gdsfactory.read import import_gds`
    extract read-back cell name, layer/polygon counts, bbox, and labels/ports where available
    compare read-back invariants against generated geometry metadata
    write gds_readback_metadata.json

function write_metadata(geometry, artifacts):
    write layout_metadata.json with parameters, layers, bboxes, counts, invariants, writer mode
    write geometry_summary.csv with deterministic row order and LF endings

function render_report(metadata, artifacts):
    summarize relevance to semiconductor layout/package CAD roles
    embed SVG preview via correct relative path
    state limitations: no PDK DRC/LVS/signoff, no JEDEC/IPC compliance
    cite open-tool anchors checked during planning

function write_manifest_after_report(artifacts, report_path):
    after report and all generated artifacts are written, compute SHA256 manifest entries relative to the manifest directory
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/semiconductor/layout_cad_demo.py` | Main deterministic layout generation / metadata extraction CLI |
| Create | `tests/semiconductor/test_layout_cad_demo.py` | TDD tests for geometry invariants, determinism, CLI behavior, metadata/report guardrails |
| Create | `data/semiconductor/layout_cad_demo/` | Checked-in deterministic demo artifacts for portfolio review |
| Create | `data/semiconductor/layout_cad_demo/semiconductor-layout-cad-automation-demo.md` | Portfolio/explanation report |
| Update | `docs/plans/README.md` | Add/update only the #2510 plan row; do not mutate sibling issue rows in this issue |
| Update | `scripts/review/results/2026-04-26-plan-2510-{claude,codex,gemini}.md` and `-rN.md` archives | Preserve canonical and archived adversarial plan-review evidence for the #2510 approval gate. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_default_spec_has_chip_package_layout_layers_and_units` | spec contains substrate, die, bump/pad, route/keepout layers with SI/um units and provenance | default spec | named layers, dimensions, role mapping |
| `test_geometry_invariants_for_die_pads_and_substrate` | die is inside substrate; all bumps/pads are inside die/substrate bounds; counts/pitch deterministic | default geometry | invariant booleans true, expected counts/bboxes |
| `test_metadata_extracts_layers_bboxes_ports_and_counts` | JSON metadata captures layers, polygons/rectangles, bbox, area, pads/ports/nets | generated geometry | deterministic metadata keys and numeric values |
| `test_gds_export_import_roundtrip_preserves_core_invariants` | real GDS export/import exists and read-back metadata preserves layer counts and bbox invariants | generated `chip_package_demo.gds` | `gds_readback_metadata.json` with bbox tolerance, contract-matched per-layer counts (exact for generated simple rectangles; documented bounded ranges only for intentionally fracturable geometry), and reader object `reader: {"package": "gdsfactory", "version": actual_imported_version}` where the version is asserted against the pinned runtime |
| `test_cli_regenerates_artifacts_manifest_and_report` | CLI writes SVG, CSV, JSON, real `.gds`, read-back JSON, manifest, and report | temp output/report paths | files exist, manifest validates, report links resolve via `Path(report.parent / svg_link).exists()` |
| `test_outputs_are_deterministic_across_runs` | repeat runs produce identical deterministic artifact hashes under the pinned GDS timestamp policy | two temp dirs | equal content hashes for manifest-covered artifacts and byte-identical `artifact_manifest.sha256` text |
| `test_missing_open_layout_dependency_blocks_rather_than_fakes_gds` | missing GDSFactory/open reader is treated as execution blocker, not a passing fake artifact | monkeypatch the lazy import helper to raise `ModuleNotFoundError` | clear RuntimeError/blocker message that includes the pinned `uv run --python 3.11 --with ...` invocation; no fake `.gds` produced |
| `test_csv_manifest_and_report_use_lf_line_endings` | cross-platform determinism for CSV/manifest/report text artifacts | generated CSV/manifest/report bytes | no `\r` bytes; explicit `\n` line endings |
| `test_report_has_role_relevance_and_no_signoff_overclaims` | portfolio report maps demo to chip/package CAD roles and avoids compliance/tapeout claims | generated report | contains role relevance; excludes `JEDEC compliant`, `DRC clean`, `tapeout-ready` |

---

## Acceptance Criteria

- [ ] TDD RED is captured before implementation using `uv run --python 3.11 --with gdsfactory==9.40.2 --with kfactory==2.4.7 --with klayout==0.30.8 --with numpy==2.4.4 --with shapely==2.1.2 pytest tests/semiconductor/test_layout_cad_demo.py -q`.
- [ ] Final targeted tests pass: `uv run --python 3.11 --with gdsfactory==9.40.2 --with kfactory==2.4.7 --with klayout==0.30.8 --with numpy==2.4.4 --with shapely==2.1.2 pytest tests/semiconductor/test_layout_cad_demo.py -q`.
- [ ] CLI can regenerate deterministic artifacts locally without proprietary tools using transient dependency invocation: `uv run --python 3.11 --with gdsfactory==9.40.2 --with kfactory==2.4.7 --with klayout==0.30.8 --with numpy==2.4.4 --with shapely==2.1.2 python scripts/semiconductor/layout_cad_demo.py --output data/semiconductor/layout_cad_demo --report data/semiconductor/layout_cad_demo/semiconductor-layout-cad-automation-demo.md`.
- [ ] Generated artifacts include metadata JSON, geometry CSV, SVG preview, real `.gds` exchange artifact, GDS read-back metadata JSON, report, and SHA256 manifest.
- [ ] Manifest validates from the artifact directory with `cd data/semiconductor/layout_cad_demo && sha256sum -c artifact_manifest.sha256`; manifest entries are relative to the manifest file parent, including report paths such as `semiconductor-layout-cad-automation-demo.md`. This supports both canonical repo output dirs and pytest temp output dirs without absolute paths.
- [ ] GDS export/import round-trip check passes and the report states the writer/reader package versions.
- [ ] Report explains relevance to chip design, package/interposer CAD automation, and job-skill development.
- [ ] Report and metadata explicitly avoid PDK DRC/LVS, JEDEC/IPC, or tapeout/signoff claims.
- [ ] Implementation cross-review is explicit and non-circular: Claude, Codex, and Gemini are requested. A valid review artifact is a non-empty Markdown file at the expected provider path containing `## Verdict`, `## Retrieval`, `## Findings`, and `## Blockers`, with verdict in `APPROVE|MINOR|MAJOR|UNAVAILABLE`. Empty files, stderr-only runs, missing headings, or parser failures count as `UNAVAILABLE`. Closeout requires no unresolved MAJOR from any valid provider review; if a provider is UNAVAILABLE after a documented retry, closeout may proceed only with two valid APPROVE/MINOR reviews plus a repo-tracked unavailable artifact and a GitHub note calling out degraded provenance.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude r1-r4 | MAJOR | Earlier waves hardened review-state hygiene, real GDS/read-back, CLI/dependency contract, deterministic GDS timestamp handling, and review-artifact validity. |
| Codex r1-r4 | MAJOR | Earlier waves hardened canonical traceability, dependency pinning, manifest/determinism policy, import/read-back contract, and stale evidence. |
| Gemini r1-r4 | UNAVAILABLE/MAJOR | Earlier runs included CLI unavailability and sandbox-overlay false positives; accepted substantive findings on stale citations, pseudocode ordering, and artifact routing only. |
| Claude r5 | MAJOR | Required manifest path policy for temp dirs, transitive dependency pinning, two-run GDS byte probe, tighter polygon bounds, report LF/link tests, and named lazy import helper. |
| Codex r5 | MAJOR | Required engineering retrieval bundle, state reconciliation between plan/header/index/label, and removal of remaining fake-layout fallback ambiguity. |
| Gemini r5 | MAJOR | Required manifest-after-report pseudocode ordering and current r5 artifact routing; import-path/default-timestamp claims were checked against the successful local probe. |
| Claude r6 | MAJOR | Required embedded two-run byte probe, full dependency pinning, stale SHA removal, exact polygon count/readback key shape, manifest/report path restrictions, manifest equality test, minority-report rule, and review artifacts in Files to Change. |
| Codex r6 | MAJOR | Required pushed-state/provenance reconciliation, r5 archive availability on main, single manifest path policy, issue-comment synchronization, and round-trip bound justification. |
| Gemini r6 | UNAVAILABLE | CLI failed before provider could read the plan; no substantive signal. |
| Claude r7 | MAJOR | Required non-empty canonical artifacts, polygon-count consistency, Files-to-Change row, reuse/justify #2511 manifest helpers, report-under-output CLI guard, dependency-error assertion, and Gemini availability policy. |
| Codex r7 | MAJOR | Required polygon-count consistency, report-location deviation from #2511 convention, single current/canonical artifact label, and review artifact files row. |
| Gemini r7 | MAJOR | Findings 1-7 were false positives caused by sandbox overlay reading a different worktree; no substantive patch applied from Gemini r7. |

**Overall result:** r7 returned MAJOR; this revision addresses the substantive r7 blockers and is queued for r8 adversarial review before any approval request.

Revisions made based on reviews so far:
- Required real open-tool GDS generation/read-back rather than pure JSON fallback; removed remaining fake-layout acceptance ambiguity.
- Added GDS import/read-back artifact and regression test.
- Clarified missing open layout dependency is a blocker, not an acceptable passing implementation.
- Added deterministic output contract, probed zero-timestamp GDS write policy, two-run GDS byte-diff validation, and manifest-relative path policy that works for repo and temp dirs.
- Added engineering retrieval bundle findings for standards ledger, code registry, online registry, and document-intelligence map.
- Added explicit CLI shape: `--output` and `--report`, validated through pinned `uv run --python 3.11 --with gdsfactory==9.40.2 --with kfactory==2.4.7 --with klayout==0.30.8 --with numpy==2.4.4 --with shapely==2.1.2 ...`.
- Added pinned `from gdsfactory.read import import_gds` import path consistently across scope, round-trip contract, and pseudocode.
- Added round-trip comparison field/tolerance/layer-key, single flatten-count policy, and bounded polygon-count acceptance.
- Corrected roadmap/report citations so they do not claim issue-number mapping or exact phrases not present in those files.
- Defined review artifact validity and current/archive routing before approval.
- Replaced circular implementation-review AC with an explicit provider/verdict closeout policy.

---

## Review Routing and Traceability Policy

- The canonical plan and README row must be committed and pushed before the final approval request so GitHub/Codex reviewers can retrieve the artifact from `main`.
- Until that push exists, review prompts must carry the full plan inline; reviewers must not be asked to rely on a GitHub path that still returns 404.
- `status:plan-review` may be applied only with a GitHub comment that explicitly says the current plan is under adversarial review and not user-approval-ready if any MAJOR remains. The final approval request is posted only after the latest valid reviews are APPROVE/MINOR.
- #2511 is used as an implementation-convention source because issue #2511 is closed and its implementation files exist on `main`; stale #2511 planning-index/header statuses are known drift and are not used as authority for #2510.

---

## Pre-Approval Review Artifact Checklist

Before asking for user approval:

- Latest current review outputs land in unsuffixed canonical paths: `scripts/review/results/2026-04-26-plan-2510-{claude,codex,gemini}.md`; immediately after each run, archive them to the corresponding `-rN.md` paths before rerunning.
- Each successful wave is archived immediately to suffixed snapshots (`-r4.md`, `-r5.md`, etc.) before another rerun can overwrite canonical paths.
- Canonical unsuffixed files must not be 0 bytes after the review command completes; transient 0-byte placeholders created by the fanout runner during an active run are not approval evidence and must be replaced by provider output or a non-empty `UNAVAILABLE` artifact before committing or requesting approval.
- The plan summary must cite the latest valid canonical artifacts and the latest archived snapshots.

---

## Determinism Contract

Execution must make deterministic artifacts falsifiable:

- Sort all layers, geometry records, labels/ports, file-list manifest entries, and JSON keys.
- Use LF line endings for CSV/manifest/report-generated tables.
- Do not serialize wall-clock timestamps into checked-in metadata, SVG, CSV, GDS read-back JSON, or manifest-covered files.
- Use explicit stable color/style maps for SVG; do not depend on Python hash iteration order.
- Manifest entries must be relative to the manifest file parent directory, not absolute and not repo-root-only. Canonical validation is `cd data/semiconductor/layout_cad_demo && sha256sum -c artifact_manifest.sha256`; for pytest temp dirs, the same relative-to-manifest rule applies and the report must be inside the output directory for deterministic manifest paths unless a future plan introduces an explicit `--manifest-root`.

- Execution must include a two-run byte-diff probe for `chip_package_demo.gds`: generate the same default design into two temp dirs using the pinned dependency set and assert equal SHA256 for the `.gds` before accepting the deterministic manifest.
- GDS bytes must be deterministic using the probed `gdsfactory==9.40.2` / kfactory path: construct/passthrough `kfactory.utilities.save_layout_options()` where `gds2_write_timestamps=False`, then pass it as `save_options` to `Component.write_gds(...)`. This zeroes GDSII timestamp fields rather than writing wall-clock time. If regenerated `.gds` hashes still differ, #2510 must stop as blocked and create/record a follow-up rather than closing with a manifest that fails regeneration.

---

## Risks and Open Questions

- **Risk:** Local environment currently lacks GDSFactory/KLayout/gdstk/gdspy. Plan mitigates by making the open dependency explicit during execution (`uv run --python 3.11 --with gdsfactory==9.40.2 --with kfactory==2.4.7 --with klayout==0.30.8 --with numpy==2.4.4 --with shapely==2.1.2 ...` or a repo dependency addition) and by treating dependency failure as a blocker rather than a successful fallback.
- **Risk:** GDSFactory APIs can change across versions. Execution must capture the exact package version in metadata/report and keep the implementation surface narrow: create component, add deterministic shapes/labels, write GDS, import/read back invariants.
- **Risk:** Geometry demo may overclaim chip-design readiness. Report must state it is a portfolio CAD automation example, not PDK-qualified layout, DRC/LVS, or tapeout evidence.
- **Decision:** Use transient pinned dependency invocation (`uv run --python 3.11 --with gdsfactory==9.40.2 --with kfactory==2.4.7 --with klayout==0.30.8 --with numpy==2.4.4 --with shapely==2.1.2 ...`) for #2510 tests and CLI validation. Do not edit repo dependency manifests for this bounded portfolio demo unless execution proves transient invocation is infeasible. First-run dependency resolution cost is accepted for this single bounded issue; execution should run the full test suite once per validation stage, not spawn repeated per-test `uv run --with` processes.

---

## Complexity: T2

**T2** — new script/module, generated artifacts, tests, and report; bounded single-issue implementation with no proprietary runtime requirement and no multi-repo integration.
