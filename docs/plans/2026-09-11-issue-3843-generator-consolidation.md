# Plan for #3843: add BaseFile variation models and name-keyed merge to modular_generator

> **Status:** adversarial-reviewed — rewritten after r1 and r2 both returned REJECT
> **Complexity:** T2
> **Date:** 2026-09-11
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3843
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-09-11-plan-3843-claude.md | ...-codex.md | ...-gemini.md

---

## Why this plan is not the one the issue asked for

The issue proposes consolidating four generators onto one and retiring three. The first draft of this plan did that. It was rejected by both reviewers and its central premise was disproved by execution. Every deletion-safety claim failed:

| Claim in the first draft | Established reality |
|---|---|
| Two generators have zero live consumers | Both are imported and tested; 23 tests pass across the two |
| Their consumers import paths that do not exist | `digitalmodel.agents` is a deprecation alias onto `digitalmodel.workflows.agents`; `digitalmodel.orcaflex.model_generator` resolves to the real module |
| `tests/test_orcaflex_agent.py` is a live collection error | It collects 13 tests and all pass |
| The Jinja package has no in-tree consumer | `commands/generate.py:7-8` imports it; `cli.py:25` registers the command |
| `templates/` sole reader is the deleted package | `template_library.py:9,85-103` reads it independently, with 44 tests asserting those paths |
| The 14 hybrid template sets are orphan data | They are live fixtures: `test_template_generator.py:138-146`, `test_hybrid_templates.py:47-75,184-220` |
| Porting merge and the writer makes `template_generator` deletable | It also supplies `TemplateManager`, `ModelValidator` and a CLI, re-exported at `solvers/orcaflex/__init__.py:80-95` |

The root cause of the first four was a structural read standing in for an executed one: directory absence was treated as proof of import failure, and the import was never run.

**This plan therefore does only the additive half.** It closes the capability gap that the research actually established and that survives every review, and it deletes nothing. Retirement becomes a follow-on that the capability work makes evaluable, rather than a premise assumed in advance.

---

## Resource Intelligence Summary

### Existing repo code

- Found: `solvers/orcaflex/modular_generator/` — the survivor by capability and coverage. Reachable from `orcaflex-convert` (`pyproject.toml:208`) via `format_converter/spec_to_modular.py:43`. 42 test files.
- Found: `template_generator.py:273-323` — `_merge_object_lists`, name-keyed list merge. Read in full for this plan.
- Found: `template_generator.py:380-418` — `_generate_reference`, emits `BaseFile:` plus `IncludeFile:` case files with an `os.path.relpath` fallback.
- Gap: `modular_generator` cannot emit a `BaseFile` variation model. A grep across the package returns one hit, a legacy config key at `schema/campaign.py:277`.
- Gap: `modular_generator` has no merge layer. `schema/_overrides.py` provides dotted-path overrides, which is a different operation from OrcaFlex whole-object replacement.

### Standards

Not applicable. `BaseFile` and `IncludeFile` semantics are vendor format behaviour, not standards-derived constants, so no `Citation` sidecar is required.

### LLM Wiki pages consulted

No relevant wiki pages.

### Documents consulted

- Issue #3843 and its correction comment, which withdraws the deletion premise.
- `scripts/review/results/2026-09-11-plan-3843-claude.md` — r1, 2 MAJOR.
- `scripts/review/results/2026-09-11-plan-3843-codex.md` — r2, 5 MAJOR.
- Orcina webhelp, *Variation models* — `BaseFile` clears all existing data then loads and accepts binary or text; `IncludeFile` acts incrementally and is text-only.
- `.claude/rules/reproducibility-is-not-correctness.md` — governs the comparator for the writer.

### Gaps identified

- No `BaseFile` emission in the survivor.
- No name-keyed list merge in the survivor.
- No licence-free comparator for `BaseFile` composition, since resolving one requires OrcaFlex or a local reimplementation.

### Evidence (embedded verification)

**Issue status** (verified 2026-09-11): `#3843` — OPEN.

**Gap proof**:
```
$ grep -rn "BaseFile" src/digitalmodel/solvers/orcaflex/modular_generator/
schema/campaign.py:277:   # legacy config key only
```

**Premise-disproving reproduction** — embedded per r1 finding 3 and r2 finding 6, and it is the evidence that reshaped this plan:

```
$ pytest tests/test_orcaflex_agent.py -q
13 passed in 0.92s

$ pytest tests/solvers/orcaflex/test_model_generator.py -q
10 passed in 3.32s

$ python -c "import digitalmodel.orcaflex.model_generator as m; print(m.__file__)"
...\src\digitalmodel\solvers\orcaflex\model_generator\__init__.py

$ python -c "import digitalmodel.agents.orcaflex.generators.env_files as m; print(m.__file__)"
DeprecationWarning: digitalmodel.agents is deprecated. Use digitalmodel.workflows.agents instead.
...\src\digitalmodel\workflows\agents\orcaflex\generators\env_files.py
```

- Reproduced at: 2026-09-11
- Failure mode matches the issue claim: **NO.** The issue alleged dead modules and a collection error. Both modules are live and all 23 tests pass. The plan is scoped to the corrected finding.

**Source read for the port** — `template_generator.py:292-299`, the branch the first draft's pseudocode omitted:
```
has_names = (all(isinstance(item, dict) and 'Name' in item for item in base_list if item)
             and all(isinstance(item, dict) and 'Name' in item for item in override_list if item))
if not has_names:
    return deepcopy(override_list) if override_list else deepcopy(base_list)
```

Distinct sources consulted: 5 — the issue, two review artifacts, the executed reproductions, and the source of the function being ported. Minimum 3 met.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-09-11-issue-3843-generator-consolidation.md |
| Implementation — merge | `digitalmodel/src/.../modular_generator/merge.py` |
| Implementation — BaseFile writer | `digitalmodel/src/.../modular_generator/writers/basefile.py` |
| Tests — merge | `digitalmodel/tests/solvers/orcaflex/modular_generator/test_name_keyed_merge.py` |
| Tests — writer | `digitalmodel/tests/solvers/orcaflex/modular_generator/test_basefile_writer.py` |
| Golden comparator | `digitalmodel/tests/solvers/orcaflex/modular_generator/goldens/basefile/` |
| Plan review — Claude | scripts/review/results/2026-09-11-plan-3843-claude.md |
| Plan review — Codex | scripts/review/results/2026-09-11-plan-3843-codex.md |

---

## Deliverable

`modular_generator` gains two capabilities it lacks: emission of a `BaseFile`-based variation model, and name-keyed list merge with OrcaFlex whole-object replacement semantics. Nothing is deleted.

---

## Pseudocode

```
# Ported from template_generator._merge_object_lists, read at :273-323.
# The has_names guard and the deepcopy are part of the behaviour, not incidental.
function merge_named_lists(base_list, override_list):
    has_names = every truthy item in BOTH lists is a dict carrying "Name"
    if not has_names:
        # Local convenience, NOT established vendor semantics — see Risks.
        return deepcopy(override_list) if override_list else deepcopy(base_list)

    result = []
    override_by_name = {item["Name"]: item for item in override_list if item}
    seen = set()
    for item in base_list:                       # base order preserved
        if item and "Name" in item:
            seen.add(item["Name"])
            result.append(deepcopy(override_by_name.get(item["Name"], item)))
    for item in override_list:                   # unknown names append
        if item and "Name" in item and item["Name"] not in seen:
            result.append(deepcopy(item))
    return result
```

```
function write_variation_model(base_path, overrides, out_path):
    doc = {"BaseFile": relpath(base_path, from=out_path.parent)}   # .dat or .yml both valid
    for section in _OBJECT_SECTIONS order:       # reference-before-use is mandatory
        if section in overrides: doc[section] = overrides[section]
    write_yaml(doc, out_path, Dumper=_NoAliasDumper)               # OrcFxAPI rejects anchors
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `modular_generator/merge.py` | name-keyed merge |
| Create | `modular_generator/writers/basefile.py` | variation-model emission |
| Create | two test modules and a goldens directory | TDD coverage and the comparator |
| Update | docs/plans/README.md | index |

No file is deleted. No module is renamed — six workspace-hub skills name `modular_generator`'s path, one as an executable invocation.

---

## The comparator problem, and how it is solved

r1 and r2 both found that "the variation model and the flat includefile set produce the same object set" is not a licence-free assertion. Resolving a `BaseFile` model needs OrcaFlex, and the licensed-run lane is down on both Windows hosts. A resolver written as part of this work is inside the producing system and is not a comparator.

An independent implementation exists in the tree: `template_generator._generate_reference` at `:380-418`. It is a separate codebase and it is **not** being deleted by this plan.

**Goldens are captured from it and committed**, and the ported writer is asserted against those goldens. Under `.claude/rules/reproducibility-is-not-correctness.md` the comparator class is `cross-solver` — an independent implementation — not `archived-run`. The provenance record states the producing module, the commit it was captured at, and that it is a second implementation of the same vendor-documented format rather than the vendor itself.

The residual limitation is stated rather than hidden: agreement between two in-house implementations is weaker than agreement with OrcaFlex. A licensed equivalence check is named as a follow-on and is **not** claimed here.

---

## TDD Test List

| # | Test | Asserts |
|---|---|---|
| 1 | override replaces a same-named entry wholesale | the override entry is present with no residue of the base entry |
| 2 | a base key absent from the override is gone | proves replacement, not deep merge |
| 3 | an unknown name appends at the end | base order unchanged |
| 4 | base order preserved under override | untouched entries keep position |
| 5 | a list containing an item without `Name` | falls back to wholesale list replacement, does not raise |
| 6 | an empty override with a non-`Name` base | returns the base copy |
| 7 | the result does not alias the base | mutating the result leaves the base unchanged |
| 8 | falsy entries in either list | skipped, no exception |
| 9 | writer emits `BaseFile:` plus overrides | key present, path relative to the output file |
| 10 | writer accepts a `.dat` base | emitted unchanged — `BaseFile` accepts binary |
| 11 | emitted overrides respect reference-before-use order | line types precede lines |
| 12 | no YAML anchors in output | `_NoAliasDumper` in force |
| 13 | **writer output matches the committed golden** | comparator is `template_generator`, an independent implementation |
| 14 | #3838's collision check on the writer's output | the guard is not bypassed by the new writer |

Tests 5 to 8 exist because the first draft's pseudocode would have raised `KeyError` on the input test 5 covers. Test 13 is the load-bearing assertion.

---

## Acceptance Criteria

1. `modular_generator` emits a `BaseFile`-based variation model.
2. The writer's output matches goldens captured from `template_generator._generate_reference`, with a provenance record naming the producing module, its commit, and the comparator class `cross-solver`.
3. Name-keyed merge is available, with the `has_names` fallback, deep copying and order preservation all covered.
4. Test 2 proves wholesale replacement rather than deep merge.
5. No file is deleted and no module renamed; all 23 tests across `test_orcaflex_agent.py` and `test_model_generator.py` still pass.
6. The generator suite shows no new failures against a baseline captured and committed before implementation begins.

---

## Risks

| Risk | Mitigation |
|---|---|
| The goldens encode a bug in `template_generator` rather than correct behaviour | The comparator class is recorded as `cross-solver`, not as truth. A licensed equivalence check is named as a follow-on. Agreement between two in-house implementations is stated as the limit of the evidence |
| The `has_names` fallback is not vendor behaviour | It is ported to preserve the existing contract and carries a comment saying it is a local convenience, **not** established OrcaFlex semantics. Establishing it is out of scope |
| `BaseFile` relative-path resolution differs from the source | Test 9 asserts the path is relative to the output file, matching the `os.path.relpath` behaviour at `:380-418` |
| Scope creeps back toward deletion | Deletion is explicitly out of scope. The follow-on cannot begin until the capability lands and is proven |

---

## Out of Scope

**All retirement.** No generator is deleted, no module renamed, no compatibility alias removed. The seven false premises tabulated above are why: each would have to be re-established by execution, not inference, before any deletion is planned. A follow-on issue should do that, and it becomes tractable once the capability gap is closed.

Also out of scope: `TemplateManager`, `ModelValidator` and the `template_generator` CLI; OrcFxAPI statics validation; typed builders for Constraints, Links and 3DBuoys; binary `.dat` output; RAO ingestion; unit conversion.
