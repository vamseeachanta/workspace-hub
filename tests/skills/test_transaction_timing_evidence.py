"""Synthetic arithmetic examples for issue 3878; no installation qualification."""
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parents[2] / "scripts/skills/transaction_timing_evidence.py"
spec = importlib.util.spec_from_file_location("timing", MODULE)
timing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(timing)


def packet():
    """Hand calculation: cap 30 minus reserve 10 = 20 s at both guards.

    Synthetic inputs, not physical constants: first checkpoint 5 s (15 s
    margin), final checkpoint 19 s (1 s margin); final I/O 18 - 16 = 2 s.
    Policy source: issue 3878 acceptance, phase-specific comparisons.
    """
    policy = {"cap_s": 30, "basis_ref": "synthetic-policy-v1",
              "checkpoints": [
                  {"name": "publish", "boundary": "before first replacement",
                   "reserve_s": 10, "required_io": []},
                  {"name": "status", "boundary": "before final full-status scan",
                   "reserve_s": 10, "required_io": ["full-index"]}]}
    binding = {"source_sha256": "a" * 64, "target_sha256": "b" * 64,
               "policy_sha256": hashlib.sha256(json.dumps(
                   policy, sort_keys=True, separators=(",", ":"),
                   allow_nan=False).encode()).hexdigest()}
    run = {"run_ref": "synthetic-run", "binding": copy.deepcopy(binding),
           "kind": "measured", "clock_ref": "synthetic-monotonic-clock",
           "origin": "lock-acquired", "checkpoints": [
               {"name": "publish", "boundary": "before first replacement",
                "elapsed_s": 5, "io": []},
               {"name": "status", "boundary": "before final full-status scan",
                "elapsed_s": 19, "io": [
                    {"name": "full-index", "start_s": 16, "end_s": 18,
                     "trace_ref": "synthetic-trace", "operation": "full-index read"}]}]}
    return {"policy": policy, "binding": binding, "runs": [run]}


def evaluate(value):
    return timing.evaluate(value["policy"], value["binding"], value["runs"])


def test_hand_calculated_margins_and_io_cost():
    result = evaluate(packet())
    assert result["status"] == "PASS"
    phases = result["runs"][0]["checkpoints"]
    assert [p["allowance_s"] for p in phases] == [20, 20]
    assert [p["margin_s"] for p in phases] == [15, 1]
    assert phases[1]["io"][0]["duration_s"] == 2
    assert result["runtime_readiness"] == "NOT_ESTABLISHED"


def test_total_under_cap_does_not_rescue_failed_checkpoint():
    """21 > 30 - 10, despite a synthetic total of 28 < 30; margin = -1."""
    value = packet()
    value["runs"][0]["total_s"] = 28
    value["runs"][0]["checkpoints"][1]["elapsed_s"] = 21
    result = evaluate(value)
    assert result["status"] == "FAIL"
    assert result["runs"][0]["checkpoints"][1]["margin_s"] == -1


def test_total_alone_cannot_approve_or_reject():
    value = packet()
    value["runs"][0].update(checkpoints=[], total_s=100)
    assert evaluate(value)["status"] == "NOT_EVALUATED"


@pytest.mark.parametrize("mutation", ["missing", "boundary", "trace", "binding", "clock", "origin"])
def test_missing_or_mismatched_evidence_is_unresolved(mutation):
    value = packet()
    run = value["runs"][0]
    if mutation == "missing":
        run["checkpoints"].pop()
    elif mutation == "boundary":
        run["checkpoints"][1]["boundary"] = "after final full-status scan"
    elif mutation == "trace":
        run["checkpoints"][1]["io"][0]["trace_ref"] = ""
    elif mutation == "binding":
        run["binding"]["target_sha256"] = "c" * 64
    elif mutation == "clock":
        run.pop("clock_ref")
    else:
        run["origin"] = "forward-measurement-start"
    assert evaluate(value)["status"] == "NOT_EVALUATED"


@pytest.mark.parametrize("elapsed", [19, 21])
def test_estimates_never_become_measured_pass_or_failure(elapsed):
    value = packet()
    value["runs"][0].update(kind="additive_estimate", basis_ref="synthetic-addends")
    value["runs"][0]["checkpoints"][1]["elapsed_s"] = elapsed
    assert evaluate(value)["status"] == "ESTIMATED"


def test_estimate_requires_basis():
    value = packet()
    value["runs"][0]["kind"] = "additive_estimate"
    assert evaluate(value)["status"] == "NOT_EVALUATED"


@pytest.mark.parametrize("elapsed", [float("nan"), float("inf"), -1, True, "19"])
def test_invalid_elapsed_rejected(elapsed):
    value = packet()
    value["runs"][0]["checkpoints"][1]["elapsed_s"] = elapsed
    assert evaluate(value)["status"] == "NOT_EVALUATED"


@pytest.mark.parametrize("start,end", [(4, 18), (18, 16), (16, 20)])
def test_io_outside_phase_is_unresolved(start, end):
    value = packet()
    value["runs"][0]["checkpoints"][1]["io"][0].update(start_s=start, end_s=end)
    assert evaluate(value)["status"] == "NOT_EVALUATED"


def test_nonmonotonic_or_duplicate_checkpoints_rejected():
    value = packet()
    value["runs"][0]["checkpoints"][1]["elapsed_s"] = 4
    assert evaluate(value)["status"] == "NOT_EVALUATED"
    value = packet()
    value["runs"][0]["checkpoints"].append(value["runs"][0]["checkpoints"][0])
    assert evaluate(value)["status"] == "NOT_EVALUATED"


def test_policy_change_requires_new_binding():
    value = packet()
    value["policy"]["checkpoints"][1]["reserve_s"] = 1
    with pytest.raises(ValueError, match="policy"):
        evaluate(value)


def test_no_runs_is_unresolved_and_one_failed_run_cannot_be_averaged_away():
    value = packet()
    value["runs"] = []
    assert evaluate(value)["status"] == "NOT_EVALUATED"
    value = packet()
    bad = copy.deepcopy(value["runs"][0])
    bad.update(run_ref="second-synthetic-run")
    bad["checkpoints"][1]["elapsed_s"] = 21
    value["runs"].append(bad)
    assert evaluate(value)["status"] == "FAIL"


def test_equality_is_not_available_time():
    """Strict guard: elapsed 20 leaves zero margin under allowance 30 - 10."""
    value = packet()
    value["runs"][0]["checkpoints"][1]["elapsed_s"] = 20
    assert evaluate(value)["status"] == "FAIL"


def test_cli_read_only_and_duplicate_json_rejected(tmp_path):
    source = tmp_path / "evidence.json"
    source.write_text(json.dumps(packet()))
    before = source.read_bytes()
    command = [sys.executable, "-B", str(MODULE), str(source)]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    assert result.returncode == 0
    assert json.loads(result.stdout)["status"] == "PASS"
    assert source.read_bytes() == before
    source.write_text('{"policy": {}, "policy": {}}')
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    assert result.returncode == 2
    assert "duplicate" in result.stdout


def test_cli_binding_array_is_invalid_packet(tmp_path):
    data = packet()
    data["binding"] = ["source_sha256", "target_sha256", "policy_sha256"]
    source = tmp_path / "evidence.json"
    source.write_text(json.dumps(data))
    result = subprocess.run([sys.executable, "-B", str(MODULE), str(source)],
                            capture_output=True, text=True, check=False)
    assert result.returncode == 2
    assert json.loads(result.stdout)["status"] == "NOT_EVALUATED"
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("binding", [
    ["source_sha256", "target_sha256", "policy_sha256"], [], "", None, 1, True,
])
def test_nonobject_binding_rejected(binding):
    data = packet()
    data["binding"] = binding
    with pytest.raises(ValueError, match="invalid source/target/policy binding"):
        evaluate(data)


@pytest.mark.parametrize("field,value", [
    ("cap_s", -1), ("cap_s", True), ("basis_ref", ""),
    ("checkpoints", []),
])
def test_invalid_policy_fails_closed(field, value):
    data = packet()
    data["policy"][field] = value
    data["binding"]["policy_sha256"] = timing.policy_digest(data["policy"])
    with pytest.raises(ValueError):
        evaluate(data)


@pytest.mark.parametrize("mutation", ["reserve", "duplicate", "io", "digest"])
def test_invalid_policy_checkpoint_or_binding(mutation):
    data = packet()
    if mutation == "reserve":
        data["policy"]["checkpoints"][0]["reserve_s"] = 31
    elif mutation == "duplicate":
        data["policy"]["checkpoints"].append(data["policy"]["checkpoints"][0])
    elif mutation == "io":
        data["policy"]["checkpoints"][1]["required_io"] *= 2
    else:
        data["binding"]["source_sha256"] = "not-a-digest"
    data["binding"]["policy_sha256"] = timing.policy_digest(data["policy"])
    with pytest.raises(ValueError):
        evaluate(data)


@pytest.mark.parametrize("mutation", ["unknown-kind", "missing-io", "duplicate-io", "operation"])
def test_bad_trace_coverage_or_evidence_kind(mutation):
    data = packet()
    run = data["runs"][0]
    traces = run["checkpoints"][1]["io"]
    if mutation == "unknown-kind":
        run["kind"] = "fixture-ready"
    elif mutation == "missing-io":
        traces.clear()
    elif mutation == "duplicate-io":
        traces.append(copy.deepcopy(traces[0]))
    else:
        traces[0]["operation"] = ""
    assert evaluate(data)["status"] == "NOT_EVALUATED"


@pytest.mark.parametrize("kind,elapsed,code,status", [
    ("measured", 21, 1, "FAIL"),
    ("additive_estimate", 19, 1, "ESTIMATED"),
])
def test_cli_nonpassing_evidence_has_nonzero_exit(tmp_path, kind, elapsed, code, status):
    data = packet()
    data["runs"][0].update(kind=kind, basis_ref="synthetic-addends")
    data["runs"][0]["checkpoints"][1]["elapsed_s"] = elapsed
    source = tmp_path / "evidence.json"
    source.write_text(json.dumps(data))
    result = subprocess.run([sys.executable, "-B", str(MODULE), str(source)],
                            capture_output=True, text=True, check=False)
    assert result.returncode == code
    assert json.loads(result.stdout)["status"] == status


def test_committed_example_matches_hand_calculation():
    """Synthetic example: allowances 30 - 10, margins 20 - 5 and 20 - 19."""
    source = MODULE.parents[2] / "docs/examples/transaction-timing-evidence.json"
    data = json.loads(source.read_text())
    result = evaluate(data)
    assert result["status"] == "PASS"
    assert [p["margin_s"] for p in result["runs"][0]["checkpoints"]] == [15, 1]
    assert result["runtime_readiness"] == "NOT_ESTABLISHED"
