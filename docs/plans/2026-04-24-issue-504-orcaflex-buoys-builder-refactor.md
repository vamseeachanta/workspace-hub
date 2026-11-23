# Plan for #504: OrcaFlex buoys builder refactor — split 610-line mega-builder into focused builders

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/digitalmodel/issues/504
> **Review artifacts:** scripts/review/results/2026-04-24-plan-504-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/buoys_builder.py` — single 610-line `BuoysBuilder(BaseBuilder)` class combining 4 responsibilities (rollers, tugs, BM, end/mid-pipe buoys) registered as `@BuilderRegistry.register("08_buoys.yml", order=80)` at line 45.
- Found: sibling builders in same package (`environment_builder.py`, `vessel_builder.py`, `winch_builder.py`) each implement a single-purpose `BaseBuilder` subclass with its own `should_generate()` and `@BuilderRegistry.register(output_file, order=N)` — these establish the DELTA pattern (one builder → one concern).
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/registry.py` — `BuilderRegistry._registry` dict is keyed by `output_file` (line 24). A second `@register("08_buoys.yml", ...)` silently overwrites the first. **This is the HARD BLOCKER surfaced by the Explorer.**
- Found: `builders/__init__.py` (lines 16, 40) and `modular_generator/__init__.py` (line 26) — both re-export `BuoysBuilder` by name; `builders/__init__.py` includes it in `__all__`. Removing the symbol is a public-API break.
- Found: `builders/lines_builder.py` line 44 consumes `end_buoy_name` from `BuilderContext` — cross-builder dependency must survive split.
- Found: `builders/context.py` lines 38-44 — typed `BuilderContext` fields (`buoy_names_6d`, `buoy_names_3d`, `all_buoy_names`, `end_buoy_name`, `bm_buoy_name`, `roller_buoy_names`) are written today by a single `build()`; after split each builder owns its subset, and `all_buoy_names` needs an aggregator or a computed property.
- Gap: no existing test coverage for `_build_tugs`, `_build_buoyancy_module`, `_build_end_buoy`, or `_build_mid_pipe_marker` as unit tests — only indirect coverage via integration (`test_slay_builders.py`).

### Standards

Not applicable — pure internal refactor, no external engineering standard governs Python module decomposition. Internal convention (sibling-builder SRP + `order=` multiples of 10) is observed.

### LLM Wiki pages consulted

No relevant wiki pages — `knowledge/wikis/` has no entries for "buoy", "roller", "tug", or "buoyancy module" in this ecosystem. This refactor does not require wiki updates.

### Documents consulted

- Issue #504 body (`/tmp/orca-batch-2026-04-24/issue-504.json`) — specifies split into `tug_builder.py`, `roller_builder.py`, `buoyancy_builder.py`, `end_buoy_builder.py`; does NOT resolve registry-key collision.
- Pod Explorer intel (`/tmp/orca-batch-2026-04-24/intel-504.md`) — identified registry `_registry` dict collision, static-method test-site breakage (`BuoysBuilder.get_support_geometry` called at `test_buoys_builder.py` lines 171/190/203/216), cross-builder context consumer in `lines_builder.py`, and uncovered tug/BM/end-buoy/mid-pipe code paths.
- `digitalmodel/docs/domains/orcaflex/SECTION_FIDELITY_ANALYSIS.md` — architecture reference cited by issue body.
- `docs/plans/` prior art — grep of `docs/plans/**` for `BuoysBuilder`, `modular_generator`, `BuilderRegistry` returned zero matches. First refactor plan for this subsystem.

### Gaps identified

- `BuilderRegistry` has no "multiple builders → same output file" convention. Must be resolved (see TRADEOFF block).
- No unit tests for tug/BM/end-buoy/mid-pipe method groups — must be backfilled BEFORE the split to establish a TDD safety net.
- No published rule on where `DEFAULT_WIREFRAME_VERTICES`/`DEFAULT_WIREFRAME_EDGES` shared constants belong after the split — a shared `_buoy_geometry.py` helper is the least-divergent option.

### Evidence (embedded verification)

**Issue statuses** (from `/tmp/orca-batch-2026-04-24/issue-504.json`):
- `#504` — OPEN — "OrcaFlex buoys builder refactor: split 611-line mega-builder into focused builders"

**File existence** (from Explorer intel, verified 2026-04-24):
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/buoys_builder.py` (610 lines)
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/registry.py`
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/context.py`
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/__init__.py`
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/__init__.py`
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/lines_builder.py`
- EXISTS: `digitalmodel/tests/solvers/orcaflex/modular_generator/builders/test_buoys_builder.py`
- EXISTS: `digitalmodel/tests/solvers/orcaflex/modular_generator/test_slay_builders.py`
- EXISTS: `digitalmodel/tests/solvers/orcaflex/modular_generator/test_builder_context.py`
- EXISTS: `digitalmodel/tests/output/test_cli_base/08_buoys.yml`, `_08_buoys_data.yml`
- MISSING (new — this plan creates): `tug_builder.py`, `roller_builder.py`, `buoyancy_builder.py`, `end_buoy_builder.py`, `_buoy_geometry.py` (helpers)
- MISSING (new — this plan creates): matching `test_tug_builder.py`, `test_roller_builder.py`, `test_buoyancy_builder.py`, `test_end_buoy_builder.py`

**Line excerpts** (from Explorer intel — planner reproduces without re-running commands):

`buoys_builder.py` structural map:
```
Line  45: @BuilderRegistry.register("08_buoys.yml", order=80)
Lines 46-610: class BuoysBuilder(BaseBuilder)
  58-65:  should_generate(self)
  67-126: build(self)                             # orchestrator + 6x _register_entity calls
 128-214: _build_roller(self, pipeline_name)      # legacy single-roller path
 216-286: _build_roller_arrangement(self, pipeline_name, arrangement)
 288-365: get_support_geometry(station, roller_type)  @staticmethod
 367-452: _build_tugs(self, pipeline_name)
 454-520: _build_buoyancy_module(self, pipeline_name)
 522-582: _build_end_buoy(self)
 584-610: _build_mid_pipe_marker(self, pipeline_name)  # ONLY 3DBuoy producer
```

`builders/registry.py` line 24 (per Explorer): `_registry` dict keyed by `output_file` — second `register("08_buoys.yml", ...)` silently overwrites first.

**Gap proofs** (from Explorer intel):
- `grep docs/plans/** for BuoysBuilder|modular_generator|BuilderRegistry` → no matches → first plan for this subsystem.
- Current test suite in `test_buoys_builder.py` (220 lines) covers `should_generate`, `RollerArrangement`, `SupportGeometry` only — no `TestTugs`, `TestBuoyancyModule`, `TestEndBuoy`, or `TestMidPipeMarker` classes exist.

Source count: 4 (issue body + Explorer intel + sibling-builder convention + registry.py) — exceeds minimum 3.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-24-issue-504-orcaflex-buoys-builder-refactor.md |
| Implementation — shared geometry helpers | digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/_buoy_geometry.py |
| Implementation — tug | digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/tug_builder.py |
| Implementation — roller | digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/roller_builder.py |
| Implementation — BM | digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/buoyancy_builder.py |
| Implementation — end buoy (+ mid-pipe marker) | digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/end_buoy_builder.py |
| Orchestrator shim (IF approach B chosen) | digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/buoys_builder.py (rewritten) |
| Registry extension (IF approach A chosen) | digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/registry.py |
| Tests — tug | digitalmodel/tests/solvers/orcaflex/modular_generator/builders/test_tug_builder.py |
| Tests — roller (migrated) | digitalmodel/tests/solvers/orcaflex/modular_generator/builders/test_roller_builder.py |
| Tests — BM | digitalmodel/tests/solvers/orcaflex/modular_generator/builders/test_buoyancy_builder.py |
| Tests — end buoy + mid-pipe | digitalmodel/tests/solvers/orcaflex/modular_generator/builders/test_end_buoy_builder.py |
| Existing tests (updated) | digitalmodel/tests/solvers/orcaflex/modular_generator/builders/test_buoys_builder.py, test_slay_builders.py, test_builder_context.py |
| Output fixtures (byte-diff check) | digitalmodel/tests/output/test_cli_base/08_buoys.yml, _08_buoys_data.yml |
| Plan review — Claude | scripts/review/results/2026-04-24-plan-504-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-24-plan-504-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-24-plan-504-gemini.md |

---

## Deliverable

Four focused SRP builders (`tug_builder.py`, `roller_builder.py`, `buoyancy_builder.py`, `end_buoy_builder.py`) plus a shared `_buoy_geometry.py` constants helper, with no change to the emitted `08_buoys.yml` content or ordering and no regression in the existing orcaflex modular_generator test suite.

---

## Pseudocode

```
# Shared helpers module (_buoy_geometry.py)
DEFAULT_WIREFRAME_VERTICES = [ (x,y,z) * 8 cube corners ]     # copied verbatim from lines 18-27
DEFAULT_WIREFRAME_EDGES    = [ (i,j) * 12 edges ]             # copied verbatim from lines 29-42

# roller_builder.py
@BuilderRegistry.register(<slot>, order=80)     # slot depends on approach A/B
class RollerBuilder(BaseBuilder):
    def should_generate(self):
        return self.spec.is_floating() or (
            self.spec.is_slay() and self.spec.get_effective_rollers() is not None
        )
    def build(self):
        # If arrangement present → loop stations, call get_support_geometry per station
        # Else → legacy 4-support-position path
        # _register_entity("roller_buoy_names", [...])
    @staticmethod
    def get_support_geometry(station, roller_type):
        # V_ROLLER / FLAT / CRADLE branches — body copied verbatim from lines 288-365

# tug_builder.py
@BuilderRegistry.register(<slot>, order=81)
class TugBuilder(BaseBuilder):
    def should_generate(self):
        return self.spec.equipment.tugs is not None and self.spec.is_floating()
    def build(self):
        # positions tugs at first_position + i*spacing; BulkModulus=Infinity preserved

# buoyancy_builder.py
@BuilderRegistry.register(<slot>, order=82)
class BuoyancyBuilder(BaseBuilder):
    def should_generate(self):
        return self.spec.equipment.buoyancy_modules is not None
    def build(self):
        # bespoke smaller-box wireframe (lines 509-518) preserved inline
        # BulkModulus=Infinity preserved

# end_buoy_builder.py
@BuilderRegistry.register(<slot>, order=83)
class EndBuoyBuilder(BaseBuilder):
    def should_generate(self):
        return self.spec.is_floating()  # end-buoy + mid-pipe marker both gated on floating
    def build(self):
        self._build_end_buoy()            # 6D, free, at pipeline_length estimate
        self._build_mid_pipe_marker()     # ONLY 3DBuoy producer; writes buoy_names_3d

# Orchestration wiring (approach-dependent — see TRADEOFF)
```

---

## Files to Change

> Two variants below — selected by the TRADEOFF decision. Common rows listed once.

### Common (both approaches)

| Action | Path | Reason |
|---|---|---|
| Create | `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/_buoy_geometry.py` | Shared wireframe vertex/edge constants extracted from lines 18-42 of current file — single source of truth, avoids divergence across 4 new builders |
| Create | `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/tug_builder.py` | New SRP builder — lines 367-452 of current file |
| Create | `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/roller_builder.py` | New SRP builder — lines 128-365 of current file (includes `get_support_geometry` as `@staticmethod`) |
| Create | `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/buoyancy_builder.py` | New SRP builder — lines 454-520 of current file |
| Create | `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/end_buoy_builder.py` | New SRP builder — lines 522-610 of current file (end buoy + mid-pipe marker together; marker stays here because it's the only 3DBuoy producer and shares the "floating-only" gate) |
| Create | `digitalmodel/tests/solvers/orcaflex/modular_generator/builders/test_tug_builder.py` | Backfill — tugs are NOT unit-tested today |
| Create | `digitalmodel/tests/solvers/orcaflex/modular_generator/builders/test_roller_builder.py` | Migrated from `test_buoys_builder.py::TestBuoysBuilderRollerArrangement` + `TestSupportGeometry`; call-sites `BuoysBuilder.get_support_geometry` → `RollerBuilder.get_support_geometry` |
| Create | `digitalmodel/tests/solvers/orcaflex/modular_generator/builders/test_buoyancy_builder.py` | Backfill — BM NOT unit-tested today |
| Create | `digitalmodel/tests/solvers/orcaflex/modular_generator/builders/test_end_buoy_builder.py` | Backfill — end buoy + mid-pipe marker NOT unit-tested today |
| Modify | `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/__init__.py` | Import + `__all__` extend with 4 new classes; `BuoysBuilder` symbol disposition depends on approach |
| Modify | `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/__init__.py` (line 26) | Re-export the 4 new classes; `BuoysBuilder` disposition depends on approach |
| Modify | `digitalmodel/tests/solvers/orcaflex/modular_generator/builders/test_buoys_builder.py` | Retain `TestBuoysBuilderShouldGenerate` (covers overall gating if shim remains); remove moved classes |
| Verify (no change expected) | `digitalmodel/tests/solvers/orcaflex/modular_generator/test_slay_builders.py` | Imports `BuoysBuilder` at line 15 — must continue to resolve to either (B) shim or (A) orchestrator name |
| Verify (no change expected) | `digitalmodel/tests/solvers/orcaflex/modular_generator/test_builder_context.py` (line 55) | Simulates `BuoysBuilder` context writes — verify still passes after split |
| Verify (byte-identical) | `digitalmodel/tests/output/test_cli_base/08_buoys.yml`, `_08_buoys_data.yml` | Golden-file diff MUST be empty after refactor |
| Update | `docs/plans/README.md` | Add this plan to index |

### Approach A — distinct registry slots (`08a_rollers.yml`, `08b_tugs.yml`, `08c_bm.yml`, `08d_end_buoys.yml`)

| Action | Path | Reason |
|---|---|---|
| Modify | `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/registry.py` | Extend registry convention to allow compound `output_file` keys (e.g., strip suffix letter when emitting), OR allow N builders per key with explicit ordering — this is a CONVENTION CHANGE and impacts every downstream writer. Add tests for the registry convention itself. |
| Modify | include-file manifest (wherever `08_buoys.yml` is referenced by the OrcaFlex model assembler) | Four new include entries replace one — grep `"08_buoys"` across digitalmodel before committing |
| Delete | `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/buoys_builder.py` | Mega-builder removed; symbol dropped from `__all__` (BREAKING — call out in release notes) OR leave a deprecation re-export shim raising `DeprecationWarning` |
| Modify | golden-file test fixtures | `08_buoys.yml` split into four fixtures OR assembler composes them at test time — must preserve byte-stable merged output |

### Approach B — `BuoysOrchestrator` shim under single registry slot

| Action | Path | Reason |
|---|---|---|
| Rewrite | `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/buoys_builder.py` | Replace 610-line class with a ~60-line `BuoysBuilder(BaseBuilder)` that registers `@BuilderRegistry.register("08_buoys.yml", order=80)`, composes `RollerBuilder`, `TugBuilder`, `BuoyancyBuilder`, `EndBuoyBuilder` as private instances, delegates `should_generate()` as `any(child.should_generate() for child in children)`, and calls each child's `build()` in fixed order (rollers → tugs → BM → end-buoy → mid-pipe) to preserve output-list ordering. Aggregates `all_buoy_names` itself after children run. Preserves the `BuoysBuilder.get_support_geometry` re-export as a `@staticmethod` forwarding to `RollerBuilder.get_support_geometry` to keep existing test call sites green (lines 171/190/203/216 of `test_buoys_builder.py`). |
| No change | `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/registry.py` | Single registry key preserved; no convention change |
| No change | include-file manifest | `08_buoys.yml` key unchanged |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_roller_builder_single_station | `RollerBuilder.build()` produces one 6DBuoy per station | slay spec with 1-station arrangement | `6DBuoys` list length 1; name matches convention |
| test_roller_builder_multi_station_naming | Multi-station name disambiguation preserved | 3-station arrangement | 3 distinct names, monotonically numbered |
| test_roller_builder_legacy_rollers_path | Legacy `rollers` (no arrangement) still works | slay spec with `rollers=4`, no arrangement | 4 roller buoys at hardcoded support_positions |
| test_roller_builder_registers_roller_buoy_names_context | Context field written correctly | floating spec | `context.roller_buoy_names` contains the emitted names |
| test_roller_builder_should_generate_floating | Gate: floating always generates | floating spec | `should_generate() is True` |
| test_roller_builder_should_generate_slay_with_arrangement | Gate: slay + arrangement generates | slay spec with arrangement | `should_generate() is True` |
| test_roller_builder_should_generate_slay_without_arrangement | Gate: slay without arrangement skips | slay spec, `rollers=None`, `arrangement=None` | `should_generate() is False` |
| test_support_geometry_v_roller | V-ROLLER math preserved byte-identical to legacy | station + `RollerType.V_ROLLER` | tuple matches pre-refactor output |
| test_support_geometry_flat | FLAT math preserved | station + `RollerType.FLAT` | tuple matches pre-refactor |
| test_support_geometry_cradle | CRADLE math preserved | station + `RollerType.CRADLE` | tuple matches pre-refactor |
| test_support_geometry_height_offset | height_offset applied correctly | station with non-zero height_offset | tuple shifted by offset |
| test_tug_builder_nominal_two_tugs | Positions at first_position + i*spacing | `tugs=2`, first_position=X, spacing=Y | 2 buoys at X, X+Y |
| test_tug_builder_preserves_bulk_modulus_infinity | `"BulkModulus": "Infinity"` stays on each tug entry | `tugs=1` | buoy dict contains `BulkModulus=="Infinity"` |
| test_tug_builder_should_generate_floating_only | Tugs only on floating | slay spec | `should_generate() is False` |
| test_buoyancy_module_nominal | BM connected inline to pipeline | floating spec with 1 BM | `6DBuoys` has 1 BM entry at expected arc position |
| test_buoyancy_module_uses_bespoke_wireframe | BM wireframe is the smaller bespoke box, NOT `DEFAULT_WIREFRAME_VERTICES` | spec with BM | vertex list matches lines 509-518 of current code (not shared default) |
| test_buoyancy_module_preserves_bulk_modulus_infinity | BM has `BulkModulus=="Infinity"` | spec with BM | buoy dict contains `BulkModulus=="Infinity"` |
| test_end_buoy_nominal | Free 6D buoy at pipeline end | floating spec, pipeline_length=L | buoy at approx (L, 0, 0) |
| test_end_buoy_no_bulk_modulus | End buoy does NOT include `BulkModulus` field | floating spec | key absent (matches current behavior) |
| test_mid_pipe_marker_is_3d_buoy | Mid-pipe marker is the ONLY 3DBuoy producer | floating spec | `3DBuoys` list non-empty; writes `context.buoy_names_3d` |
| test_end_buoy_builder_registers_end_buoy_name | `context.end_buoy_name` set for downstream `lines_builder.py` consumer | floating spec | `context.end_buoy_name` is the emitted name |
| test_lines_builder_consumes_end_buoy_name_unchanged | Integration: `lines_builder.py` line 44 still sees `end_buoy_name` | run both builders in order | lines builder sees non-None `end_buoy_name` |
| test_golden_08_buoys_yml_byte_identical | Full refactor preserves emitted YAML | CLI base fixture inputs | `08_buoys.yml` and `_08_buoys_data.yml` byte-identical to pre-refactor |
| test_output_ordering_preserved | 6DBuoys order: rollers → tugs → BM → end_buoy (unchanged) | floating spec with all 4 | positional indices match pre-refactor |
| test_buoys_builder_compatibility_shim (approach B) OR test_buoys_builder_removed (approach A) | Public symbol disposition verified | `from ...builders import BuoysBuilder` | approach B: resolves to orchestrator; approach A: raises `ImportError` OR `DeprecationWarning` |
| test_get_support_geometry_backcompat_shim (approach B) | Existing call `BuoysBuilder.get_support_geometry(...)` still works | same args as 4 tests in current `test_buoys_builder.py` (lines 171/190/203/216) | identical return value |
| test_registry_allows_multiple_slots_per_output (approach A only) | Registry convention change is correct | register 4 builders under `08a/08b/08c/08d` | all 4 retained; emission order preserved by `order=` values |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest digitalmodel/tests/solvers/orcaflex/modular_generator/builders/ -v`
- [ ] No regression: `uv run pytest digitalmodel/tests/solvers/orcaflex/ -v`
- [ ] Full-suite smoke: `uv run pytest digitalmodel/tests/ -x`
- [ ] Golden-file diff empty: `diff digitalmodel/tests/output/test_cli_base/08_buoys.yml <freshly-regenerated>.yml` → no output; same for `_08_buoys_data.yml`
- [ ] Output-ordering check: emitted `6DBuoys` list in test_cli_base still reads rollers → tugs → BM → end_buoy
- [ ] Cross-builder context preserved: `lines_builder.py` reads non-None `end_buoy_name` in integration run
- [ ] `grep -rn "BuoysBuilder\|get_support_geometry" digitalmodel/` → every hit either uses the new API or goes through the chosen shim (no orphan references)
- [ ] Registry convention (approach A only): `uv run pytest digitalmodel/tests/.../test_registry*.py` passes
- [ ] Public-symbol disposition documented in CHANGELOG or release notes (approach A) or compat shim validated (approach B)
- [ ] Review artifacts posted to scripts/review/results/2026-04-24-plan-504-{claude,codex,gemini}.md
- [ ] Plan status advanced via GSD: `draft` → `adversarial-reviewed` → `plan-review` → user approves → `plan-approved`

---

## Adversarial Review Summary

<!-- Filled in after Step 4 completes. Do not post to GitHub until this section is populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | APPROVE / MINOR / MAJOR | _pending_ |
| Codex | APPROVE / MINOR / MAJOR | _pending_ |
| Gemini | APPROVE / MINOR / MAJOR | _pending_ |

**Overall result:** _pending_

Revisions made based on review:
- _pending_

---

## Risks and Open Questions

### `[TRADEOFF FOR USER]` — Registry collision resolution (MANDATORY DECISION)

**Context:** `BuilderRegistry._registry` (in `builders/registry.py` line 24) is a dict keyed by `output_file`. If the four new builders each `@register("08_buoys.yml", ...)`, the second registration silently overwrites the first — only one builder runs. Splitting the mega-builder **requires** resolving this collision explicitly.

**Approach A — distinct registry slots per sub-builder**
- Each new builder registers under a unique key: `08a_rollers.yml`, `08b_tugs.yml`, `08c_bm.yml`, `08d_end_buoys.yml` (suffix letters preserve the `order=80` batch grouping).
- PROS: pure SRP — each builder is independent, independently testable, independently enabled/disabled. Matches the DELTA pattern perfectly. No hidden orchestrator indirection.
- CONS: **registry convention change** — the include-file manifest (wherever `08_buoys.yml` is referenced by the OrcaFlex model assembler) needs four new include entries. Golden-file fixtures split or get composed at assembly time. Public-API break: `BuoysBuilder` symbol disappears (or becomes a deprecation shim). `08_buoys.yml` filename contract changes, which may surface in user-visible artifacts if the YAML filename appears in any external reference (OrcaFlex `.dat`, CI snapshots, user docs).
- Complexity cost: +1 tier inside T2 — involves `registry.py` changes, manifest updates, and fixture-split work.

**Approach B — `BuoysOrchestrator` (rename `BuoysBuilder`) delegating to 4 sub-builders under single `08_buoys.yml` slot**
- `BuoysBuilder` stays registered at `("08_buoys.yml", order=80)` but becomes a ~60-line orchestrator that composes four private sub-builder instances, delegates `should_generate()` as `any(child.should_generate())`, and invokes each `build()` in fixed order. Sub-builders (`TugBuilder`, `RollerBuilder`, `BuoyancyBuilder`, `EndBuoyBuilder`) are plain `BaseBuilder` subclasses NOT registered in `BuilderRegistry` — they're invoked only through the orchestrator.
- PROS: **zero registry-convention change**, **zero include-manifest change**, **zero golden-file split**. Public `BuoysBuilder` symbol preserved (no breakage for `test_slay_builders.py` or the two `__init__.py` exports). Legacy `BuoysBuilder.get_support_geometry(...)` test call sites stay green via a one-line `@staticmethod` forwarding shim. Preserves emitted YAML byte-for-byte trivially.
- CONS: sub-builders are not true first-class citizens of the registry — they're only reachable through the orchestrator, so an operator cannot disable "just tugs" without a code change. Slight composition indirection. The orchestrator is still a ~60-line class, not a pure elimination of the mega-builder.
- Complexity cost: base T2 — orchestrator + 4 sub-builders + shared geometry helper, no convention work.

**Planner recommendation: Approach B.**

Rationale: the issue requests an SRP refactor, NOT a public-API redesign or an include-manifest overhaul. Approach B delivers the full SRP benefit (four single-concern builder classes, each independently unit-testable) while preserving the `08_buoys.yml` output contract, the `BuoysBuilder` public symbol, and the golden fixtures. The ~60-line orchestrator is an acceptable thin composition layer, not a re-constitution of the mega-builder. Approach A delivers slightly cleaner registry semantics but imposes a cascade of downstream contract changes (manifest, fixtures, public symbol, YAML filenames) that exceed the refactor's stated scope.

**User might prefer Approach A if:**
- They anticipate future per-sub-builder enable/disable toggles (e.g., "skip tugs in this run") driven by configuration rather than code.
- They want the registry convention tightened workspace-wide (multiple builders → single output is a recurring pattern, not a one-off).
- They are willing to absorb the include-manifest and golden-fixture churn now to avoid a second refactor later.

**Decision requested from user before implementation. Default to B unless user responds with A.**

### Other risks

- **Risk (static-method test call sites):** `BuoysBuilder.get_support_geometry(...)` is called directly at `test_buoys_builder.py` lines 171/190/203/216. Approach B keeps a re-export shim — risk LOW. Approach A requires editing all four call sites — risk LOW-MEDIUM (mechanical).
- **Risk (coverage gap before refactor):** tugs, BM, end-buoy, mid-pipe marker have ZERO unit coverage today. The refactor MUST backfill these tests FIRST (TDD safety net), BEFORE the structural move. If the pre-move unit tests fail, the refactor is paused until they pass against the unmodified mega-builder. This is a load-bearing ordering constraint.
- **Risk (output-list ordering):** today's `build()` emits rollers → tugs → BM → end_buoy into `6DBuoys`. Any reader that assumes this ordering (downstream OrcaFlex parser, golden-file tests) must still see the same order. Approach B preserves trivially via orchestrator invocation order. Approach A must use `order=80.1, 80.2, 80.3, 80.4` (or equivalent) and trust the registry to sort stably.
- **Risk (`all_buoy_names` aggregation):** today set by a single `build()` after all sub-builds complete. Approach B aggregates inside the orchestrator after delegating. Approach A needs a fifth "late-pass aggregator" builder OR a `BuilderContext.all_buoy_names` computed property that unions `buoy_names_6d` + `buoy_names_3d` — either works but the choice must be explicit.
- **Risk (BM bespoke wireframe):** lines 509-518 define a smaller vertex list inline, NOT `DEFAULT_WIREFRAME_VERTICES`. Must be preserved in `buoyancy_builder.py` — do NOT DRY into the shared helper.
- **Risk (`BulkModulus` field divergence):** tug and BM include `"BulkModulus": "Infinity"`; roller and end-buoy do NOT. Any shared buoy-dict helper must preserve per-type field presence exactly. A dedicated test (`test_tug_builder_preserves_bulk_modulus_infinity`, `test_end_buoy_no_bulk_modulus`) pins this.
- **Risk (API-breakage via `__all__`):** `builders/__init__.py` publicly exports `BuoysBuilder`. Approach A breaks this unless a deprecation shim remains. Approach B preserves it natively.

### Open questions

- Should the mid-pipe marker (lines 584-610, only 3DBuoy producer) live inside `end_buoy_builder.py` or get its own `mid_pipe_marker_builder.py`? **Planner decision: inside `end_buoy_builder.py`** — both share the "floating-only" gate, both are free-standing (not connected to pipeline), and the marker is ~25 lines. A separate file is over-decomposition. Revisit if mid-pipe gains independent gating or grows >50 lines.
- Should the shared `DEFAULT_WIREFRAME_VERTICES`/`_EDGES` constants live in a new `_buoy_geometry.py`, in `BaseBuilder`, or be duplicated in each new file? **Planner decision: `_buoy_geometry.py`** — avoids divergence, keeps `BaseBuilder` lean, and the leading underscore signals "internal to this builders package".
- Does any user documentation or external manifest currently reference the filename `08_buoys.yml`? Flag for verification before approach-A decision.

---

## Complexity: T2

**T2** — internal refactor, single source file (610 lines) split into 5 new files plus test backfill, TDD-protected by an existing suite that must be extended first. Justification:
- Bounded scope (one source file, one output YAML, sibling-convention reference).
- No new feature surface; no intended behavior change.
- Three architectural decisions surfaced (registry collision, static-method location, mid-pipe marker placement) — two resolved in this plan, one (registry) escalated as `[TRADEOFF FOR USER]`.
- Four untested method groups require pre-move unit-test backfill — adds effort but is mechanical.
- Not T1: multi-file, public-API surface touch, cross-builder context coupling, and a mandatory architectural tradeoff.
- Not T3: no cross-repo effect, no external standards, no solver contract change, no data migration, no schema/YAML-contract change intended.
