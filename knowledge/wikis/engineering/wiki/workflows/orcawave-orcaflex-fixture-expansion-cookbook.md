---
title: "OrcaWave / OrcaFlex Fixture Expansion Cookbook"
tags: [orcawave, orcaflex, fixtures, semantic-proof, cookbook, testing, validation]
sources:
  - closed-issues
added: 2026-04-26
last_updated: 2026-04-26
---

# OrcaWave / OrcaFlex Fixture Expansion Cookbook

A repeatable procedure for adding a new structure-family semantic-proof fixture without overfitting to one generated YAML formatting style. Operationalizes the [Canonical Spec Semantic Equivalence Contract](../concepts/canonical-spec-semantic-equivalence.md) for OrcaWave/OrcaFlex.

## When To Use This Cookbook

Add a new fixture when the workspace needs deterministic semantic-proof coverage for a structure family that the existing fixtures (L03 ship, PLET-to-PLEM jumper, lazy/steep-wave riser) do not represent. Typical drivers:

- A downstream issue depends on the family (e.g., #2472 CALM/SPM buoy, #2473 spread-moored FPSO, #2474 OrcaWave-to-OrcaFlex RAO handoff).
- A standards-driven workflow needs a regression anchor.
- A reverse parser supports a new field set.

Do **not** use this cookbook to "add tests" to an already-proven fixture, to validate solver physics (that requires licensed proof per #2475), or to rewrite an existing generator.

## Step 1 — Fixture Selection Criteria

A new fixture qualifies when **all** of these hold:

| Criterion | Why |
|---|---|
| Distinct structure family from existing proofs | Each family stresses a different code path in the generator |
| Minimal: smallest spec that still exercises every disputed dimension | Big specs hide regressions in unrelated noise |
| Has a documented canonical `spec.yml` location under `digitalmodel/docs/domains/` or fixture directory | Discoverable and round-trippable |
| Reverse parser supports the field set, OR parser limitations are explicitly enumerated | Avoids silent partial coverage |
| Real engineering motivation (cited issue, PR, or ops scenario) | Filters out fixtures with no consumer |

Reject a candidate fixture if it duplicates the structural variety of an existing proof, requires fields no parser yet handles, or exists only to grow line count.

## Step 2 — Canonical Spec Fields by Solver Family

Each solver family has a minimum-required canonical-spec field set. Below is the **minimum**; specific structures will set more.

### OrcaWave (`DiffractionSpec`)

| Field group | Required | Notes |
|---|---|---|
| Body identity | yes | Stable name; one entry per modeled body |
| Mesh / panel source | yes | Path resolves from solver run dir; absolute paths rejected |
| Frequency domain | yes | Set of frequencies + unit declaration (rad/s or Hz) |
| Heading domain | yes | Set of headings in deg, going-to convention |
| Solve type | yes | `potential`, `potential_source`, `full_qtf`, `diagonal_qtf` |
| Mass/inertia matrix | yes for QTF | COG required when QTF is enabled |
| Output requests | yes | RAO, added mass, damping, QTF — must be explicit |
| Multi-body interaction | conditional | Required when more than one body |

### OrcaFlex (`ProjectInputSpec` / `ModularModelGenerator`)

| Field group | Required | Notes |
|---|---|---|
| Object identity | yes | Vessels, lines, buoys, anchors, environments |
| Line types | yes | OD, mass-per-length, EA, EI per line type used |
| Connections | yes | Each line endpoint binds to a body, free end, or anchor |
| Stage / time-step | yes | Stage durations and inner/outer time-steps |
| Environment | yes | Wave train, current, wind block — even if "still water" |
| Coordinate frame | yes | World frame z-up; body frames per body |
| Vessel type / hydrodynamic database | conditional | Required for any vessel that uses RAOs |

A spec missing any required row should fail-closed in the generator, not silently default.

## Step 3 — Native Assertion Checklist (Formatting-Robust)

Tests must assert **engineering meaning** without overfitting to one generator formatting style. Use these idioms:

### Assert by parsed value, not text

```python
import yaml
native = yaml.safe_load(generated_yaml_text)
assert native["Bodies"][0]["Name"] == "FPSO_A"
assert native["Bodies"][0]["Mass"] == pytest.approx(spec.mass_kg / 1000.0)  # kg -> te
```

Never: `assert "Name: FPSO_A" in generated_yaml_text`.

### Assert by multiset for unordered domains

```python
assert sorted(native["Frequencies"]) == sorted(spec.frequencies_hz)
assert set(native["Headings"]) == set(spec.headings_deg)
```

### Assert by negation against bad defaults

For every solver-default field where the default disagrees with spec intent (Dimension 7 of the contract), assert by negation:

```python
# spec.analysis_type == "full_qtf"
assert native["SolveType"] != "Potential and source formulations"
assert native["SolveType"] == "Full QTF calculation"
```

This is the assertion class that catches the PR #528 family of regressions.

### Assert reverse-parser equivalence where supported

```python
from digitalmodel.hydrodynamics.diffraction.reverse_parsers import parse_orcawave_native
recovered_spec = parse_orcawave_native(generated_yaml_text)
assert recovered_spec.normalized() == spec.normalized()
```

`normalized()` strips solver-default fields the spec did not set; the comparison is on engineering meaning.

### Assert for each contract dimension

The proof test for any new fixture must contain at least one assertion for each of the nine equivalence dimensions in the contract. Tests that cover only six or seven dimensions are not complete proofs — they are silent gaps.

| Dimension | Assertion idiom |
|---|---|
| Object identity | Compare `Name` fields |
| Units | `pytest.approx` after explicit conversion |
| Frames | Compare origin and orientation tuples |
| Sign conventions | Compare phase/heading enum + numeric example |
| Solver options | Assert positive AND assert negation against bad defaults |
| Frequency / heading domains | Multiset equality |
| Native-default tolerances | Negation assertions on hostile defaults |
| Path provenance | Compare path + assert non-absolute |
| Formatting / acceptable defaults | Use `yaml.safe_load`, not text compare |

## Step 4 — Avoiding Overfit Traps

The cookbook exists because past test patterns overfit to one generator's formatting. Avoid these:

- **Byte-equal native YAML.** First time the generator changes whitespace, every fixture breaks; reviewers regenerate the snapshot and lose the regression signal.
- **Snapshot files committed alongside the generator.** When the same generator both writes the snapshot and is tested against it, the test is circular. Use external evidence: spec values, reverse-parser output, hand-derived expected values.
- **Substring matches on raw YAML.** Sensitive to comments, ordering, scientific-notation formatting; misses semantic equivalents.
- **`yaml.safe_load(yaml.safe_dump(x)) == x`.** This is a YAML round-trip, not a semantic-proof. Reject in review.
- **One assertion per fixture.** If a single assertion covers the test, the fixture is too coarse to detect the dimensions the contract requires.

## Step 5 — Evidence and Review Checklist

Before submitting a new fixture proof for review, the author must attach all of the following to the issue / PR description:

- [ ] Canonical spec path and brief structural description.
- [ ] List of asserted dimensions, with one assertion line per dimension.
- [ ] Reverse-parser equivalence result (or explicit "parser does not yet support fields X, Y").
- [ ] Numeric example for each unit conversion the test exercises.
- [ ] Confirmation that no absolute paths leak into native output.
- [ ] Negation assertions for any solver default that disagrees with spec intent.
- [ ] Pytest output (collected, passed, time) on the dev machine.

The reviewer should reject the proof when any item is missing or hand-waved. The contract is fail-closed at review time, not just at runtime.

## When Licensed-Machine Proof Is Required

Semantic equivalence is sufficient when:

- The change is generator-only.
- No new solver default is being relied on.
- No physics regression is suspected.

Licensed-machine load/run proof is required when **any** of these hold:

- A new solver-option mapping is introduced (the option must actually be honored by the solver, not just written to YAML).
- The fixture exercises a path the solver could reject at parse-time (mesh format, multi-body coupling block).
- A previous regression was caught by physics, not by parse.
- The fixture is the first to use a newly added field in `DiffractionSpec` or `ProjectInputSpec`.

The licensed-proof protocol itself lives under issue #2475; route licensed runs through the [Solver Queue](../entities/solver-queue.md) per the [machine boundary](../../../../../docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md).

## Candidate Future Families

These are open candidates flagged by the 2026-04-23 closeout handoff. Each one needs its own issue before becoming a proof:

| Candidate | Solver | Issue placeholder | Why it stresses something new |
|---|---|---|---|
| CALM / SPM buoy mooring | OrcaFlex | #2472 | Single-point mooring + hawser hose + floater coupling |
| Spread-moored FPSO | OrcaFlex | #2473 | 12-line+ mooring spread + vessel-type RAOs |
| Multi-body OrcaWave (LNG carrier + FLNG) | OrcaWave | tbd | Cross-body coupling matrix, multi-body QTF |
| RAO / hydrodynamic handoff | OrcaWave -> OrcaFlex | #2474 | Cross-solver provenance + frequency/heading domain preservation |
| Semi-sub / FOWT | OrcaFlex | tbd | Multi-column geometry + viscous damping |
| Mooring-only system | OrcaFlex | tbd | Anchor identity + line/segment topology |
| Installation analysis | OrcaFlex | tbd | Staged simulation + time-varying boundary conditions |

## Worked Example: Adding a CALM Buoy Fixture (sketch)

The pattern below illustrates how the cookbook applies to a new family. It is a sketch, not committed code.

```text
1. Locate / write canonical spec at digitalmodel/docs/domains/orcaflex/calm_buoy/spec.yml
   - Single buoy, 6 chain legs, hawser to FPSO, JONSWAP environment
   - Set ALL Step 2 OrcaFlex required fields explicitly

2. Write proof at digitalmodel/tests/solvers/orcaflex/modular_generator/test_calm_buoy_semantic.py
   - Load spec, generate native YAML
   - Run all nine dimension assertions
   - Run reverse-parser equivalence
   - Add negation assertions for any field where the OrcaFlex default disagrees with intent (e.g., line statics method)

3. Attach evidence to GitHub issue #2472:
   - Spec path
   - Test output (pytest -q line count and timings)
   - List of asserted dimensions with one example each

4. If a new generator default was added, also queue a licensed run via Solver Queue and capture the result.
```

## Cross-References

- **Related concept**: [Canonical Spec Semantic Equivalence Contract](../concepts/canonical-spec-semantic-equivalence.md)
- **Related workflow**: [OrcaWave-to-OrcaFlex Pipeline](../workflows/orcawave-to-orcaflex-pipeline.md)
- **Related workflow**: [Solver Debugging Protocol](../workflows/solver-debugging-protocol.md)
- **Related entity**: [OrcaWave Solver](../entities/orcawave-solver.md)
- **Related entity**: [OrcaFlex Solver](../entities/orcaflex-solver.md)
- **Related entity**: [Solver Queue](../entities/solver-queue.md)
- **Related entity**: [Diffraction Analysis System](../entities/diffraction-analysis-system.md)
- **Related concept**: [Test-Driven Development](../concepts/test-driven-development.md)
- **Operator map**: [`docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`](../../../../../docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md)
- **Issues**: #2476, #2455, #2456, #2457, #2472, #2473, #2474, #2475
