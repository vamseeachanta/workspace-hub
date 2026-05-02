---
title: "Canonical Spec Semantic Equivalence Contract"
tags: [orcawave, orcaflex, semantic-proof, canonical-spec, diffractionspec, projectinputspec, equivalence, validation]
sources:
  - closed-issues
added: 2026-04-26
last_updated: 2026-04-26
---

# Canonical Spec Semantic Equivalence Contract

Defines what "semantic equivalence" means when a canonical `spec.yml` is converted to a solver-native input file (OrcaWave `.yml`/`.owd`, OrcaFlex `.yml`/`.dat`). This is the durable contract consumed by structure-family proof issues (#2455, #2456, #2457 first wave; #2472, #2473, #2474, #2475 next wave) and by the [Fixture Expansion Cookbook](../workflows/orcawave-orcaflex-fixture-expansion-cookbook.md).

## Scope

**In scope.** Deterministic, license-free proof that a canonical spec produces a native input file whose **engineering meaning** matches the spec on every dimension below. The proof can run in CI on any developer machine.

**Out of scope.** Licensed solver execution. Whether the native input file actually loads, runs, and produces physically reasonable results on a paid OrcaWave or OrcaFlex installation is a separate proof tracked under the [Licensed Solver Proof Protocol](../workflows/orcawave-orcaflex-fixture-expansion-cookbook.md#when-licensed-machine-proof-is-required) and issue #2475. Semantic equivalence is necessary but not sufficient for licensed proof.

## Why Two Proof Layers

A canonical-to-native generator can produce a YAML that the solver rejects, hangs on, or runs to a physically nonsense answer — even when every value in the file matches the spec. Conversely, a generator can produce a YAML the solver loads and runs to convergence even when a unit was silently mistranslated. Independent proofs:

| Proof layer | Question answered | Where it runs | Cost |
|---|---|---|---|
| **Semantic equivalence** | Does the native input file mean what the spec says? | Any dev machine, CI | Free |
| **Licensed load/run** | Does the solver actually load and run the file to a sensible result? | Licensed machine via [Solver Queue](../entities/solver-queue.md) | Paid seat |

Conflating the two is the failure mode this contract exists to prevent.

## Equivalence Dimensions

Every canonical-to-native conversion must preserve all nine dimensions. Each new structure-family fixture must assert each dimension explicitly.

### 1. Object Identity

Every named entity in the spec (vessel, line, body, environment block, restraint) appears in the native file with a **stable, predictable name** derived from the spec. Round-trip via the reverse parser must reproduce the spec name.

- Native `Name` fields are the contract surface — formatting, comments, and key ordering are not.
- A spec body named `FPSO_A` must not silently become `Body1` or `default` in native output.

### 2. Units

| Quantity | Canonical (`spec.yml`) | Native (OrcaWave/OrcaFlex YAML) | Conversion site |
|---|---|---|---|
| Mass | kg | te (OrcaFlex) / kg (OrcaWave) | Generator must convert and the test must assert the converted value |
| Length | m | m | Identity, but assert anyway |
| Frequency | rad/s or Hz (declared in spec) | Hz (Orcina convention) | Convert and reverse-sort if needed |
| Angle | deg | deg | Rotational RAOs are **rad/m** internal; report deg/m |
| Time | s | s | Identity |

Unit drift is the most common cross-solver disagreement (see [Solver Debugging Protocol](../workflows/solver-debugging-protocol.md)). Tests must assert numeric values, not unit-stripped tokens.

### 3. Coordinate and Body Frames

- Origin and orientation of every body frame must round-trip through the generator.
- World frame: right-handed, z-up convention is enforced; non-conforming spec values are an error, not a silent reinterpretation.
- Body-relative attachment points (line ends, fairleads, padeyes) must preserve their attached-body identity, not just their world coordinates.

### 4. Sign Conventions

- Wave heading direction: **going-to** vs **coming-from** must be declared in the spec and matched in native output. The OrcaWave/OrcaFlex pipeline uses Orcina conventions documented in [OrcaWave-to-OrcaFlex Pipeline](../workflows/orcawave-to-orcaflex-pipeline.md).
- Phase convention: **Orcina lag** is the native convention; AQWA-derived specs require explicit conversion.
- Rotation handedness: angular DOFs are right-handed; a spec that flips this must be detected and either converted or rejected.

### 5. Solver Option Mapping

Canonical option names must map deterministically to native option names. The reverse must also hold — a native option enabled in output must correspond to a spec option, never to a hidden default.

- **Worked example:** PR #528 fixed an overlap where canonical `analysis_type: full_qtf` could leave native `SolveType: Potential and source formulations`. The fix added `_effective_solve_type(spec)` in `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py` so the canonical intent promotes the native field. Tests now assert the native `SolveType` directly. New solver-option mappings must add the same kind of explicit assertion.

### 6. Frequency and Heading Domains

- The set of frequencies in native output must equal the set declared in the spec, after unit conversion. Order may differ (Orcina is descending; spec may be ascending) but the **multiset of values** must match.
- Heading set must match similarly. Periodic boundaries (0 and 360) are the same heading; tests must accept either canonical form but not silently drop one.

### 7. Native-Default Tolerances

Native solver YAML carries hundreds of fields the canonical spec does not set. Tests must distinguish three cases:

| Native field origin | How tests handle it |
|---|---|
| Set by canonical spec | Assert exact value |
| Solver default with no spec preference | Tolerate any value the solver writes (do not assert) |
| Solver default that violates spec intent | Assert by negation — field must NOT be the default that disagrees with spec |

Forgetting the third row is the trap PR #528 closed. A spec that says "full QTF" must not silently coexist with a native default that says "potential only", even though both files load.

### 8. File and Path Provenance

- Mesh / panel / source files referenced by the spec must appear in the native output with **paths that resolve from the same working directory the solver will run from**, not absolute developer-machine paths.
- The reverse parser must extract the same logical path; any rewriting (e.g., `./mesh.gdf` ↔ `mesh.gdf`) is allowed only if the round-trip is documented and tested.
- Provenance is a security and reproducibility concern: a spec must never embed an absolute path that leaks the build host (see `.claude/rules/coding-style.md` path-handling rule).

### 9. Acceptable Formatting and Default Differences

The contract is about **engineering meaning**, not text equality. The following native-output differences are explicitly allowed:

- Whitespace, indentation, key ordering inside YAML maps.
- Inline comments added by the generator.
- Numeric formatting (`1.0` vs `1.000` vs `1.00e0`) provided the parsed value is identical.
- Solver defaults emitted for fields the spec did not set.

Tests that assert byte-equal native YAML are **wrong**: they make the contract brittle and overfit to one generator formatting style. The cookbook page enumerates the assertion idioms that survive formatting churn.

## Reverse-Parser Equivalence

For every canonical-to-native generator, a reverse parser converts native YAML back to a canonical-spec dict. The composition `parse(generate(spec))` must equal `spec` modulo:

- Solver defaults the spec did not set (drop before compare).
- Numeric tolerance documented per field (default: bit-exact for integers, `math.isclose(rel_tol=1e-9)` for floats; explicit larger tolerance only when the generator legitimately quantizes).

Reverse-parser equivalence is the strongest deterministic proof short of running the solver. New fixture proofs should add a reverse-parser test wherever the parser supports the field set used.

## Anti-Patterns This Contract Rejects

- Asserting native YAML by string comparison. Brittle; defeats the point of semantic equivalence.
- Round-tripping a spec through `yaml.safe_load(yaml.safe_dump(spec))` and calling that "semantic proof".
- Reading the generator's output and confirming it matches a hard-coded fixture file the same generator produced — circular.
- Skipping the third row of the native-default table; assuming "if it loads, the meaning matched".

## Worked Examples in the Repo

| Fixture | Source | Proof file (digitalmodel) | Issue |
|---|---|---|---|
| L03 ship benchmark — full-QTF OrcaWave roundtrip | `docs/domains/orcawave/L03_ship_benchmark/spec.yml` | `tests/hydrodynamics/diffraction/test_orcawave_semantic_roundtrip.py` | #2457 |
| PLET-to-PLEM rigid jumper | `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/` (canonical spec under fixture dir) | `tests/solvers/orcaflex/modular_generator/test_jumper_plet_to_plem_semantic.py` | #2455 |
| Lazy-wave / steep-wave riser variants | `ProjectInputSpec` / `ModularModelGenerator` | `tests/solvers/orcaflex/modular_generator/test_riser_variant_semantic_proof.py` | #2456 |

PR digitalmodel#528 implements the first wave; the test runner was reported at 35 passed in 20.46s on 2026-04-23.

## Related Schemas

- Canonical OrcaWave input: [`DiffractionSpec`](https://github.com/vamseeachanta/digitalmodel/blob/main/src/digitalmodel/hydrodynamics/diffraction/input_schemas.py)
- OrcaWave generator: [`orcawave_backend.py`](https://github.com/vamseeachanta/digitalmodel/blob/main/src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py)
- OrcaWave reverse parser: [`reverse_parsers.py`](https://github.com/vamseeachanta/digitalmodel/blob/main/src/digitalmodel/hydrodynamics/diffraction/reverse_parsers.py)
- OrcaWave-to-OrcaFlex bridge: [`orcawave_to_orcaflex.py`](https://github.com/vamseeachanta/digitalmodel/blob/main/src/digitalmodel/hydrodynamics/diffraction/orcawave_to_orcaflex.py)
- Canonical OrcaFlex input: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/` (`ProjectInputSpec` and `ModularModelGenerator`)

## Downstream Consumers

This contract is binding for:

- #2472 — OrcaFlex CALM/SPM buoy semantic proof
- #2473 — OrcaFlex spread-moored FPSO / vessel+mooring semantic proof
- #2474 — OrcaWave-to-OrcaFlex RAO/hydrodynamic handoff semantic proof
- #2475 — Licensed-machine load/run proof protocol (composes with this contract; does not replace it)

Issues #2455, #2456, #2457 are the first-wave consumers and have CLOSED status.

## Cross-References

- **Related workflow**: [Fixture Expansion Cookbook](../workflows/orcawave-orcaflex-fixture-expansion-cookbook.md)
- **Related workflow**: [OrcaWave-to-OrcaFlex Pipeline](../workflows/orcawave-to-orcaflex-pipeline.md)
- **Related workflow**: [Solver Debugging Protocol](../workflows/solver-debugging-protocol.md)
- **Related entity**: [OrcaWave Solver](../entities/orcawave-solver.md)
- **Related entity**: [OrcaFlex Solver](../entities/orcaflex-solver.md)
- **Related entity**: [Diffraction Analysis System](../entities/diffraction-analysis-system.md)
- **Related entity**: [Solver Queue](../entities/solver-queue.md)
- **Related concept**: [Hydrodynamic Analysis](../concepts/hydrodynamic-analysis.md)
- **Related concept**: [Test-Driven Development](../concepts/test-driven-development.md)
- **Operator map**: [`docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`](../../../../../docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md)
- **Issue**: #2476
