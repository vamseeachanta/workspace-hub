"""Text-generation preservation regressions for issue #3811.

Namespace oracle: issue #3811 requires SIMPLEC equations only, and plain SIMPLE
pressure in fields with velocity/turbulence in equations. Synthetic echo controls
come from that issue's regression specification: hand division gives U = 1/2 =
0.5, k = 1/4 = 0.25, epsilon = 1/8 = 0.125, omega = 1/16 = 0.0625 and
p = 3/4 = 0.75. These fractions imply no physical suitability or convergence claim.
"""

from copy import deepcopy
import importlib.util
from pathlib import Path
import re

import pytest


@pytest.fixture(scope="module")
def write_fvsolution():
    """Load only the text writer, without the production dictionary parser."""
    scripts = Path(__file__).resolve().parents[2] / "scripts" / "openfoam-analysis"
    spec = importlib.util.spec_from_file_location("fvsolution", scripts / "fvsolution.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.write_fvsolution


# Invalid examples and diagnostics: test_run_analysis_fvsolution.py's
# test_bad_consistent, test_relaxation_mapping_required,
# test_unknown_relaxation_key, test_bad_relaxation and
# test_simplec_rejects_explicit_pressure. The copied factors are invalid-input
# controls, not new engineering settings.
@pytest.mark.parametrize("settings,error,message", [
    pytest.param({"consistent": "perhaps"}, ValueError,
                 "consistent must be a boolean or 'yes'/'no'", id="invalid-mode-text"),
    pytest.param({"consistent": None}, ValueError,
                 "consistent must be a boolean or 'yes'/'no'", id="invalid-mode-null"),
    pytest.param({"consistent": 1}, ValueError,
                 "consistent must be a boolean or 'yes'/'no'", id="invalid-mode-number"),
    pytest.param({"relaxation": []}, TypeError,
                 "relaxation must be a mapping", id="non-mapping"),
    pytest.param({"relaxation": {"unknown": 0.9}}, ValueError,
                 "unsupported relaxation key: unknown", id="unknown-key"),
    pytest.param({"relaxation": {"U": float("nan")}}, ValueError,
                 "relaxation.U must be a finite number", id="not-a-number"),
    pytest.param({"relaxation": {"U": float("inf")}}, ValueError,
                 "relaxation.U must be a finite number", id="infinity"),
    pytest.param({"consistent": True, "relaxation": {"p": 0.3}}, ValueError,
                 "pressure relaxation requires consistent: no (plain SIMPLE)",
                 id="simplec-pressure-boolean"),
    pytest.param({"consistent": "yes", "relaxation": {"p": 0.3}}, ValueError,
                 "pressure relaxation requires consistent: no (plain SIMPLE)",
                 id="simplec-pressure-string"),
])
@pytest.mark.parametrize("target_present", [True, False], ids=["present", "absent"])
def test_refused_writer_preserves_existing_target(
    tmp_path, write_fvsolution, settings, error, message, target_present,
):
    """Refusals must preserve raw target bytes, directory entries and caller data."""
    target = tmp_path / "fvSolution"
    sentinel = b"synthetic sentinel\r\n\x00\xff\n"
    if target_present:
        target.write_bytes(sentinel)
    original_bytes = target.read_bytes() if target_present else None
    original_entries = set(tmp_path.iterdir())
    solver = {"application": "simpleFoam", **deepcopy(settings)}
    original_solver = deepcopy(solver)

    with pytest.raises(error, match=f"^{re.escape(message)}$"):
        write_fvsolution(target, solver)

    assert solver == original_solver
    assert set(tmp_path.iterdir()) == original_entries
    if target_present:
        assert target.read_bytes() == original_bytes == sentinel
    else:
        assert not target.exists()


# Independent, literal namespace and byte oracles. Decimal values follow the
# hand calculations in the module docstring; neither production parser nor
# writer output is used to construct these expectations.
SIMPLEC_RELAXATION = b'''{
  equations {
  ".*" 0.5;
  k 0.25;
  epsilon 0.125;
  omega 0.0625;
  }
}
'''
SIMPLE_RELAXATION = b'''{
  fields { p 0.75; }
  equations {
  U 0.5;
  k 0.25;
  epsilon 0.125;
  omega 0.0625;
  }
}
'''


@pytest.mark.parametrize("consistent,mode,expected", [
    pytest.param(True, "yes", SIMPLEC_RELAXATION, id="simplec-boolean"),
    pytest.param("yes", "yes", SIMPLEC_RELAXATION, id="simplec-string"),
    pytest.param(False, "no", SIMPLE_RELAXATION, id="simple-boolean"),
    pytest.param("no", "no", SIMPLE_RELAXATION, id="simple-string"),
])
def test_explicit_factor_placement_preserves_inputs(
    tmp_path, write_fvsolution, consistent, mode, expected,
):
    """Echo arbitrary caller fractions with issue #3811 topology and stable bytes."""
    factors = {"U": 0.5, "k": 0.25, "epsilon": 0.125, "omega": 0.0625}
    if mode == "no":
        factors["p"] = 0.75
    solver = {"application": "simpleFoam", "consistent": consistent, "relaxation": factors}
    original_solver = deepcopy(solver)
    targets = (tmp_path / "first", tmp_path / "repeated")
    generated = []

    for target in targets:
        write_fvsolution(target, solver)
        assert solver == original_solver
        raw = target.read_bytes()
        text = raw.decode("utf-8")
        assert f"consistent {mode};" in text
        # Compare the entire relaxation tail, including braces and namespace
        # membership: extra pressure, fields or equation entries must fail.
        prefix, relaxation = raw.split(b"\nrelaxationFactors ")
        assert prefix
        assert relaxation == expected
        generated.append(raw)

    first, repeated = generated
    assert first == repeated
    assert factors == original_solver["relaxation"]
    assert set(tmp_path.iterdir()) == set(targets)
