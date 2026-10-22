"""Text-only dictionary tests; no OpenFOAM bootstrap or executable is used.

Legacy golden values are transcribed from run-analysis.sh at the base revision,
section '# fvSolution'. They pin existing text, not engineering acceptance limits.
"""
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts" / "openfoam-analysis"
sys.path.insert(0, str(SCRIPTS))


def load_module(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Source: unchanged base writer, '# fvSolution', linear-solver entries.
HEADER = """FoamFile { version 2.0; format ascii; class dictionary; object fvSolution; }
solvers {
  p { solver GAMG; tolerance 1e-06; relTol 0.1; smoother GaussSeidel; }
  pFinal { solver GAMG; tolerance 1e-06; relTol 0; smoother GaussSeidel; }
  U { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-05; relTol 0.1; }
  UFinal { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-05; relTol 0; }
}
"""


@pytest.mark.parametrize("application,tail", [
    ("simpleFoam", ('SIMPLE { nNonOrthogonalCorrectors 0; consistent no; }\n'
     'relaxationFactors {\n  fields { p 0.3; }\n  equations {\n  U 0.7;\n  }\n}\n')),
    ("icoFoam", 'PISO { nCorrectors 2; nNonOrthogonalCorrectors 0; pRefCell 0; pRefValue 0; }\n'),
])
def test_golden(tmp_path, application, tail):
    """Base text; SIMPLE pressure is moved to fields and plain mode is explicit."""
    target = tmp_path / "fvSolution"
    load_module("fvsolution").write_fvsolution(target, {"application": application, "consistent": False})
    assert target.read_text() == HEADER + tail


def test_simplec_pressure_defect(tmp_path):
    """User Guide 6.3.2: SIMPLEC needs no pressure relaxation."""
    target = tmp_path / "fvSolution"
    load_module("fvsolution").write_fvsolution(target, {"application": "simpleFoam"})
    relaxation = target.read_text().split("relaxationFactors", 1)[1]
    assert " p " not in relaxation


def generate(tmp_path, **settings):
    target = tmp_path / "fvSolution"
    load_module("fvsolution").write_fvsolution(target, {"application": "simpleFoam", **settings})
    return target.read_text()


def test_simplec_default(tmp_path):
    """Expected 0.9 is the maintainer choice in issue 3811's proposed block."""
    text = generate(tmp_path)
    assert 'equations {\n  ".*" 0.9;' in text
    assert "fields" not in text


def test_plain_simple(tmp_path):
    """Input factors from the base writer; hand mapping: p -> fields, U -> equations."""
    text = generate(tmp_path, consistent=False, relaxation={"U": 0.7, "p": 0.3})
    assert "consistent no;" in text
    assert "fields { p 0.3; }" in text
    assert "equations {\n  U 0.7;" in text


@pytest.mark.parametrize("consistent", [True, "yes"])
def test_simplec_rejects_explicit_pressure(tmp_path, consistent):
    """Even the base writer's p factor contradicts the SIMPLEC pressure rule."""
    with pytest.raises(ValueError, match="pressure.*consistent.*no"):
        generate(tmp_path, consistent=consistent, relaxation={"p": 0.3})
    assert not (tmp_path / "fvSolution").exists()


def test_explicit_no_string(tmp_path):
    assert "consistent no" in generate(tmp_path, consistent="no")


def test_equation_override(tmp_path):
    """0.7 is a caller input copied from the existing relaxation example."""
    assert '".*" 0.7;' in generate(tmp_path, relaxation={"U": 0.7})


@pytest.mark.parametrize("value", ["perhaps", None, 1])
def test_bad_consistent(tmp_path, value):
    with pytest.raises(ValueError, match="consistent"):
        generate(tmp_path, consistent=value)


@pytest.mark.parametrize("value", [True, "0.9; p 0.3", float("nan"), float("inf")])
def test_bad_relaxation(tmp_path, value):
    """Only finite numeric inputs; no inferred engineering range is imposed."""
    with pytest.raises(ValueError, match="relaxation"):
        generate(tmp_path, relaxation={"U": value})


@pytest.mark.parametrize("text,expected", [
    ('SIMPLE { consistent yes; } relaxationFactors { equations { ".*" 0.9; } }', []),
    ('SIMPLE { consistent no; } relaxationFactors { fields { p 0.3; } equations { U 0.7; } }', []),
    ('relaxationFactors { equations { p 0.3; } }', ["pressure"]),
    ('SIMPLE { consistent yes; } relaxationFactors { fields { p 0.3; } }', ["SIMPLEC"]),
    ('SIMPLE { consistent yes; ', ["brace"]),
    ('relaxationFactors { fields { U 0.7; } }', ["equations"]),
    ('relaxationFactors { fields { ".*" 0.9; } }', ["equations"]),
    ('relaxationFactors { p 0.3; }', ["sub-dictionary"]),
    ('relaxationFactors { equations { U 0.7 } }', ["semicolon"]),
    ('relaxationFactors { equations { U 0.7; U 0.9; } }', ["duplicate"]),
    ('}', ["brace"]),
    ('/* unclosed', ["comment"]),
    ('SIMPLE { consistent yes; } relaxationFactors { fields { "p" 0.3; } }', ["SIMPLEC"]),
    ('relaxationFactors { equations { U { p 0.3; } } }', ["scalar"]),
])
def test_structural_validation(text, expected):
    """Hand inspection of braces and key ancestry; factors copied from issue 3811.

    Guide 6.3.2 supplies the pressure rule; v2312 Under relaxation / Usage
    supplies the fields/equations split. No numeric acceptance threshold is tested.
    """
    issues = load_module("foamdict").validate_fvsolution(text)
    if expected:
        assert expected[0].lower() in " ".join(issues).lower()
    else:
        assert issues == []


def test_comments_and_quoted_regex():
    text = '// { ignored\n SIMPLE { consistent yes; } /* } ignored */\n'
    text += 'relaxationFactors { equations { "(U|k|epsilon|omega)" 0.9; } }'
    assert load_module("foamdict").validate_fvsolution(text) == []


def test_preflight_before_solver(tmp_path):
    """An invalid dictionary must fail even when no result files exist yet."""
    (tmp_path / "system").mkdir()
    (tmp_path / "system" / "fvSolution").write_text('relaxationFactors { equations { p 0.3; } }')
    validator = load_module("validate-analysis")
    passed, issues = validator.validate_dictionaries(tmp_path)
    assert not passed
    assert any("pressure" in issue for issue in issues)
    assert not any("convergence" in issue for issue in issues)


def test_missing_dictionaries(tmp_path):
    passed, issues = load_module("validate-analysis").validate_dictionaries(tmp_path)
    assert not passed
    assert any("fvSolution" in issue for issue in issues)


def test_shell_calls_writer_and_preflight_in_order():
    """Inspect the invocation contract without sourcing or running OpenFOAM."""
    script = (SCRIPTS / "run-analysis.sh").read_text()
    assert "from fvsolution import write_fvsolution" in script
    assert "--dictionaries-only" in script
    assert script.index("--dictionaries-only") < script.index("# Stage 3: Meshing")
    assert "relax.get(" not in script


def reference_relaxation(path):
    """Parse the committed reference block, not a duplicate of its numbers."""
    text = path.read_text()
    assert re.search(r"\bconsistent\s+yes\s*;", text)
    start = text.index("relaxationFactors\n{")
    tail = text[start:].split("```", 1)[0].split("{%", 1)[0]
    return load_module("foamdict").parse_dictionary(tail)["relaxationFactors"]


@pytest.mark.parametrize("reference", ["openfoam-dict-patterns.md", "openfoam-version-landscape.md"])
def test_reference_simplec_drift(tmp_path, reference):
    """Hand mapping: wildcard supplies U; explicit turbulence keys override it.

    Expected factors come directly from each committed v2312 reference example.
    The generator and reference must have equations only and equal effective factors.
    """
    foam = load_module("foamdict")
    ref = reference_relaxation(ROOT / "docs" / "research" / reference)
    assert set(ref) == {"equations"}
    settings = {name: float(value) for name, value in ref["equations"].items()}
    generated = foam.parse_dictionary(generate(tmp_path, relaxation=settings))
    assert foam.relaxation_issues(generated) == []
    actual = generated["relaxationFactors"]
    assert set(actual) == set(ref)
    effective = {name: actual["equations"].get(name, actual["equations"]['".*"']) for name in settings}
    assert effective == ref["equations"]


def generate_case(tmp_path, application="simpleFoam"):
    """Execute only the shell's dictionary-writing Python, with a stub YAML input.

    No shell or OpenFOAM startup is executed. Stub inputs copy the
    base writer's defaults; end_time is a symbolic caller input in this text test.
    """
    import yaml

    case = tmp_path / "case"
    (case / "system").mkdir(parents=True)
    config = tmp_path / "analysis.yaml"
    config.write_text(yaml.safe_dump({"solver": {"application": application, "end_time": "END_INPUT"}, "flow": {}}))
    script = (SCRIPTS / "run-analysis.sh").read_text()
    setup = script.split("# Stage 2: Case Setup", 1)[1]
    source = setup.split('python -c "', 1)[1].split('\n" 2>&1', 1)[0]
    source = source.replace('\\"', '"')
    for key, value in {"$ANALYSIS_YAML": config, "$RUN_DIR": case, "$SCRIPT_DIR": SCRIPTS}.items():
        source = source.replace(key, str(value))
    writer = tmp_path / "dictionary_writer.py"
    writer.write_text(source)
    result = subprocess.run([sys.executable, str(writer)], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    return case


@pytest.mark.parametrize("application", ["simpleFoam", "icoFoam", "pisoFoam"])
def test_shell_dictionary_path(tmp_path, application):
    case = generate_case(tmp_path, application)
    assert load_module("validate-analysis").validate_dictionaries(case) == (True, [])


@pytest.mark.parametrize("application,mutation,diagnostic", [
    ("pisoFoam", "steady-ddt", "steadyState"),
    ("simpleFoam", "transient-ddt", "steadyState"),
    ("simpleFoam", "wrong-algorithm", "SIMPLE"),
    ("pisoFoam", "wrong-algorithm", "PISO"),
    ("simpleFoam", "nested-scheme", "ddtSchemes"),
])
def test_algorithm_consistency(tmp_path, application, mutation, diagnostic):
    """Expected topology: Guide 6.3.3 and v2312 solver documentation.

    simpleFoam is steady SIMPLE; pisoFoam is transient PISO. Swapping the
    algorithm or time category contradicts those definitions, independent of values.
    """
    case = generate_case(tmp_path, application)
    schemes = case / "system" / "fvSchemes"
    solution = case / "system" / "fvSolution"
    if mutation == "steady-ddt":
        schemes.write_text(schemes.read_text().replace("Euler", "steadyState"))
    elif mutation == "transient-ddt":
        schemes.write_text(schemes.read_text().replace("steadyState", "Euler"))
    elif mutation == "nested-scheme":
        schemes.write_text('ddtSchemes { default { invalid value; } }')
    else:
        solution.write_text(solution.read_text().replace("SIMPLE", "PISO") if application == "simpleFoam"
                            else solution.read_text().replace("PISO", "SIMPLE"))
    passed, issues = load_module("validate-analysis").validate_dictionaries(case)
    assert not passed
    assert diagnostic in " ".join(issues)


def test_unknown_application_not_evaluated(tmp_path):
    case = generate_case(tmp_path, "unreviewedSolver")
    passed, issues = load_module("validate-analysis").validate_dictionaries(case)
    assert not passed
    assert any("NOT_EVALUATED" in issue for issue in issues)


def test_full_validation_includes_preflight(tmp_path):
    """A synthetic completed case uses directory labels, not numerical results."""
    case = generate_case(tmp_path)
    (case / "0").mkdir()
    (case / "1").mkdir()
    (case / "convergence-verdict.yaml").write_text("status: converged\n")
    (case / "log.simpleFoam").write_text("End\n")
    assert load_module("validate-analysis").validate(str(case)) == (True, [])
    solution = case / "system" / "fvSolution"
    solution.write_text(solution.read_text() + 'relaxationFactors { equations { p 0.3; } }')
    passed, issues = load_module("validate-analysis").validate(str(case))
    assert not passed
    assert any("duplicate" in issue for issue in issues)


def test_worked_example(tmp_path):
    """Independent examples in the documentation must match actual writer tails."""
    doc = ROOT / "docs" / "engineering" / "openfoam" / "relaxation-dictionaries.md"
    before, simplec, simple = re.findall(r"```text\n(.*?)```", doc.read_text(), re.DOTALL)
    foam = load_module("foamdict")
    assert any("pressure" in issue for issue in foam.validate_fvsolution(before))
    assert any("SIMPLEC" in issue for issue in foam.validate_fvsolution(before))
    assert foam.validate_fvsolution(simplec) == []
    assert foam.validate_fvsolution(simple) == []
    assert generate(tmp_path).removeprefix(HEADER) == simplec
    assert generate(tmp_path, consistent=False).removeprefix(HEADER) == simple


@pytest.mark.parametrize("mutation,diagnostic", [
    ("mesh", "Mesh quality FAILED"),
    ("diverged", "DIVERGED"),
    ("fatal", "FOAM FATAL"),
    ("incomplete", "did not complete"),
    ("continuity", "Continuity errors"),
    ("no-log", "No solver log"),
    ("no-verdict", "Missing convergence"),
])
def test_results_validation_regression(tmp_path, mutation, diagnostic):
    """Synthetic completion markers exercise existing validation branches.

    The continuity rejection threshold remains the base validator's Check 4;
    this fixture uses a local error of unity to exceed that unchanged threshold.
    Directory names are labels, not results from a simulation.
    """
    case = generate_case(tmp_path)
    (case / "0").mkdir()
    (case / "1").mkdir()
    if mutation != "no-verdict":
        status = "diverged" if mutation == "diverged" else "converged"
        (case / "convergence-verdict.yaml").write_text(f"status: {status}\n")
    if mutation != "no-log":
        text = "End\n"
        if mutation == "fatal":
            text = "FOAM FATAL ERROR\n  invalid dictionary\nEnd\n"
        elif mutation == "incomplete":
            text = "Starting\n"
        elif mutation == "continuity":
            text = "sum local = 1\nEnd\n"
        (case / "log.simpleFoam").write_text(text)
    if mutation == "mesh":
        (case / "mesh-verdict.yaml").write_text("pass: false\nissues: [invalid]\n")
    passed, issues = load_module("validate-analysis").validate(str(case))
    assert not passed
    assert diagnostic in " ".join(issues)


def test_missing_case(tmp_path):
    passed, issues = load_module("validate-analysis").validate(str(tmp_path / "absent"))
    assert not passed
    assert "does not exist" in " ".join(issues)


def test_dictionary_cli(tmp_path):
    case = generate_case(tmp_path)
    command = [sys.executable, str(SCRIPTS / "validate-analysis.py"), str(case), "--dictionaries-only"]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    assert result.returncode == 0
    assert "VALIDATION: PASS" in result.stdout
    path = case / "system" / "fvSolution"
    path.write_text("relaxationFactors { equations { p 0.3; } }")
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    assert result.returncode != 0
    assert "pressure" in result.stdout


def test_ddt_field_override(tmp_path):
    case = generate_case(tmp_path, "pisoFoam")
    path = case / "system" / "fvSchemes"
    path.write_text('ddtSchemes { default Euler; U steadyState; }')
    passed, issues = load_module("validate-analysis").validate_dictionaries(case)
    assert not passed
    assert any("ddtSchemes.U" in issue for issue in issues)


def test_relaxation_mapping_required(tmp_path):
    with pytest.raises(TypeError, match="mapping"):
        generate(tmp_path, relaxation=[])


def test_unknown_relaxation_key(tmp_path):
    """Unknown keys cannot silently discard a caller's requested factor."""
    with pytest.raises(ValueError, match="unsupported relaxation key"):
        generate(tmp_path, relaxation={"unknown": 0.9})


def test_archived_skill_simplec_drift(tmp_path):
    """The other writer's skill example uses U and a wildcard at the same factor.

    Hand expansion: the literal U factor wins for U; the wildcard supplies k,
    epsilon and omega. The expected factor is read from the committed example,
    not copied from the implementation. No coefficient is qualified by this test.
    """
    reference = ROOT / ".agents/skills/_archive/engineering/cfd/openfoam/15-fvsolution/SKILL.md"
    expected = reference_relaxation(reference)
    foam = load_module("foamdict")
    assert set(expected) == {"equations"}
    factors = expected["equations"]
    assert factors["U"] == factors['".*"']
    actual = foam.parse_dictionary(generate(tmp_path, relaxation={"U": float(factors["U"])}))
    assert foam.relaxation_issues(actual) == []
    assert set(actual["relaxationFactors"]) == {"equations"}
    for field in ("U", "k", "epsilon", "omega"):
        expected_value = factors.get(field, factors['".*"'])
        actual_factors = actual["relaxationFactors"]["equations"]
        assert actual_factors.get(field, actual_factors['".*"']) == expected_value
