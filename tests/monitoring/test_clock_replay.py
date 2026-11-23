"""Synthetic arithmetic replays; expected answers are derived below, not sampled."""

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parents[2] / "scripts/monitoring/clock_replay.py"


def load():
    spec = importlib.util.spec_from_file_location("clock_replay", MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reading(value, domain="monotonic", clock_id="synthetic-origin", resolution=1):
    return {
        "value_ns": value,
        "domain": domain,
        "clock_id": clock_id,
        "resolution_ns": resolution,
    }


def packet():
    """Hand calculation, synthetic ns: 110-100=10; 210-200=10; 220-210=10.

    Both durations equal the inclusive [10,10] limits. Age equals max_age=10.
    Second start equals first end, so continuity is exact at the boundary.
    Small integers are illustrative inputs, not operational acceptance limits.
    Contract: docs/monitoring/clock-domain-audit.html, Replay contract.
    """
    return {
        "criteria": {"min_duration_ns": 10, "max_duration_ns": 10, "max_age_ns": 10},
        "now": reading(220, "wall", "synthetic-epoch"),
        "samples": [
            {
                "start": reading(100),
                "end": reading(110),
                "interval": reading(10),
                "observed_at": reading(200, "wall", "synthetic-epoch"),
            },
            {
                "start": reading(110),
                "end": reading(120),
                "interval": reading(10),
                "observed_at": reading(210, "wall", "synthetic-epoch"),
            },
        ],
    }


def test_boundaries_and_original_evidence():
    source = packet()
    frozen = copy.deepcopy(source)
    answer = load().replay(source)
    assert answer["replay_status"] == "PASS"
    assert answer["durations_ns"] == [10, 10]
    assert answer["age_ns"] == 10
    assert answer["evidence"] == frozen == source
    assert answer["evidence"] is not source


@pytest.mark.parametrize(
    "monotonic_offset,wall_offset", [(0, 10**20), (10**20, 0), (10**20, 10**21)]
)
@pytest.mark.parametrize(
    "now,expected_age,expected_verdict",
    [(220, 10, "PASS"), (221, 11, "FAIL")],
    ids=["valid", "stale"],
)
def test_epoch_translation_preserves_replay_verdict(
    monotonic_offset, wall_offset, now, expected_age, expected_verdict
):
    """Source: docs/monitoring/clock-domain-audit.html, Replay contract/example.

    Independently, (end+k)-(start+k)=end-start and
    (now+j)-(observed+j)=now-observed. The example's durations are
    110-100=10 and 120-110=10; latest age is 220-210=10 (PASS), or
    221-210=11>10 (stale FAIL). Epoch shifts preserve these literal answers.
    Synthetic nonnegative k and j differ: zero leaves one origin unchanged;
    10**20 and 10**21 exceed binary64's exact consecutive-integer range
    (through 2**53). The contract requires integer nanoseconds to avoid
    floating-point loss. Intervals are durations, so they are not shifted;
    the inclusive [10,10] duration bounds and maximum age 10 stay unchanged.
    """
    source = packet()
    source["now"]["value_ns"] = now
    shifted = copy.deepcopy(source)
    for sample in shifted["samples"]:
        for key in ("start", "end"):
            sample[key]["value_ns"] += monotonic_offset
        sample["observed_at"]["value_ns"] += wall_offset
    shifted["now"]["value_ns"] += wall_offset

    for candidate in (source, shifted):
        answer = load().replay(candidate)
        assert answer["replay_status"] == expected_verdict
        assert answer["durations_ns"] == [10, 10]
        assert answer["age_ns"] == expected_age


def test_replay_evidence_is_deeply_independent():
    """Source: docs/monitoring/clock-domain-audit.html, deep-copy contract.

    The worked example/packet supplies first start 100, now 220, and age
    limit 10. Synthetic mutations use 100-1=99 then 100-2=98 for start,
    220+1=221 then 220+2=222 for now, and 10+1=11 then 10+2=12 for
    the limit. These are copy-isolation probes, not acceptance criteria.
    Index zero selects the first sample. All expected values are literals.
    """
    source = packet()
    evidence = load().replay(source)["evidence"]

    evidence["samples"][0]["start"]["value_ns"] = 99
    evidence["now"]["value_ns"] = 221
    evidence["criteria"]["max_age_ns"] = 11
    assert source["samples"][0]["start"]["value_ns"] == 100
    assert source["now"]["value_ns"] == 220
    assert source["criteria"]["max_age_ns"] == 10

    source["samples"][0]["start"]["value_ns"] = 98
    source["now"]["value_ns"] = 222
    source["criteria"]["max_age_ns"] = 12
    assert evidence["samples"][0]["start"]["value_ns"] == 99
    assert evidence["now"]["value_ns"] == 221
    assert evidence["criteria"]["max_age_ns"] == 11


@pytest.mark.parametrize(
    "field,value",
    [
        ("domain", "wall"),
        ("clock_id", "other-origin"),
        ("resolution_ns", 2),
    ],
)
def test_mixed_duration_metadata_is_not_evaluated(field, value):
    """Equal numeric ticks do not establish equal clock domains/origins/quanta."""
    source = packet()
    source["samples"][1]["interval"][field] = value
    assert load().replay(source)["replay_status"] == "NOT_EVALUATED"


@pytest.mark.parametrize(
    "case", ["backward", "overlap", "short", "long", "stale", "future"]
)
def test_invalid_time_evidence_fails_without_repair(case):
    """Independent arithmetic: 99<100; 109<110; 9<10; 11>10; age=11 or -1."""
    source = packet()
    if case == "backward":
        source["samples"][0]["end"]["value_ns"] = 99
    elif case == "overlap":
        source["samples"][1]["start"]["value_ns"] = 109
        source["samples"][1]["end"]["value_ns"] = 119
    elif case in ("short", "long"):
        duration = 9 if case == "short" else 11
        source["samples"][1]["end"]["value_ns"] = 110 + duration
        source["samples"][1]["interval"]["value_ns"] = duration
    else:
        source["now"]["value_ns"] = 221 if case == "stale" else 209
    frozen = copy.deepcopy(source)
    result = load().replay(source)
    assert result["replay_status"] == "FAIL"
    assert result["evidence"] == source == frozen


def test_independently_clocked_interval_does_not_become_continuity():
    """Synthetic mismatch: endpoint delta=10, separately recorded interval=11."""
    source = packet()
    source["samples"][1]["interval"]["value_ns"] = 11
    assert load().replay(source)["replay_status"] == "FAIL"


@pytest.mark.parametrize("value", [True, 1.0, "10", None, -1])
def test_ticks_must_be_nonnegative_integers(value):
    source = packet()
    source["samples"][0]["end"]["value_ns"] = value
    assert load().replay(source)["replay_status"] == "NOT_EVALUATED"


@pytest.mark.parametrize(
    "case", ["criteria", "empty", "quantum", "wall_origin", "wall_backward"]
)
def test_incomplete_or_incompatible_evidence(case):
    source = packet()
    if case == "criteria":
        del source["criteria"]["max_age_ns"]
    elif case == "empty":
        source["samples"] = []
    elif case == "quantum":
        source["samples"][0]["start"]["resolution_ns"] = 3
    elif case == "wall_origin":
        source["now"]["clock_id"] = "unrelated-epoch"
    else:
        source["samples"][1]["observed_at"]["value_ns"] = 199
    expected = "FAIL" if case == "wall_backward" else "NOT_EVALUATED"
    assert load().replay(source)["replay_status"] == expected


def test_large_integer_ticks_do_not_lose_precision():
    """(10**20+110)-(10**20+100)=10 exactly, beyond binary64 integer precision."""
    source = packet()
    for sample in source["samples"]:
        for key in ("start", "end"):
            sample[key]["value_ns"] += 10**20
    assert load().replay(source)["durations_ns"] == [10, 10]


def test_cli_reads_stdin_and_retains_evidence():
    result = subprocess.run(
        [sys.executable, str(MODULE)],
        input=json.dumps(packet()),
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    assert json.loads(result.stdout)["evidence"] == packet()


def test_cli_rejects_duplicate_json_keys():
    result = subprocess.run(
        [sys.executable, str(MODULE)],
        input='{"now":1,"now":2}',
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
    assert "duplicate" in result.stderr


@pytest.mark.parametrize(
    "field,value",
    [
        ("clock_id", "reset-origin"),
        ("resolution_ns", 2),
        ("domain", "wall"),
    ],
)
def test_continuity_requires_same_clock_across_samples(field, value):
    source = packet()
    for key in ("start", "end", "interval"):
        source["samples"][1][key][field] = value
    assert load().replay(source)["replay_status"] == "NOT_EVALUATED"


@pytest.mark.parametrize(
    "key,value",
    [
        ("min_duration_ns", True),
        ("max_duration_ns", -1),
        ("max_age_ns", 1.0),
        ("min_duration_ns", 11),
    ],
)
def test_invalid_limits_are_not_evaluated(key, value):
    source = packet()
    source["criteria"][key] = value
    assert load().replay(source)["replay_status"] == "NOT_EVALUATED"


@pytest.mark.parametrize("source", [None, [], {}, {"criteria": {}}])
def test_incomplete_packet_does_not_crash(source):
    assert load().replay(source)["replay_status"] == "NOT_EVALUATED"


@pytest.mark.parametrize("text", ['{"value":NaN}', '{"value":Infinity}', "{"])
def test_cli_rejects_malformed_json(text):
    result = subprocess.run(
        [sys.executable, str(MODULE)],
        input=text,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 2
    assert not result.stdout


@pytest.mark.parametrize(
    "case,expected", [("future", "FAIL"), ("missing", "NOT_EVALUATED")]
)
def test_cli_nonpass_exit_code(case, expected):
    source = packet()
    if case == "future":
        source["now"]["value_ns"] = 209
    else:
        del source["criteria"]
    result = subprocess.run(
        [sys.executable, str(MODULE)],
        input=json.dumps(source),
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert json.loads(result.stdout)["replay_status"] == expected


def test_documented_example_is_executable():
    """Published hand calculation: 110-100=10; 220-210=10; each equals its limit."""
    document = MODULE.parents[2] / "docs/monitoring/clock-domain-audit.html"
    text = document.read_text()
    example = text.split("<pre>")[2].split("</pre>")[0]
    answer = load().replay(json.loads(example))
    assert answer["replay_status"] == "PASS"
    assert answer["durations_ns"] == [10]
    assert answer["age_ns"] == 10


def test_resolution_does_not_imply_epoch_aligned_tick_grid():
    """Resolution is not divisibility: 110-100=10 with declared 3 ns resolution.

    Python 3.13 time.get_clock_info defines resolution as clock resolution,
    without an epoch alignment guarantee. Replay compares recorded integers;
    it does not certify uncertainty of the supplied operational limits.
    """
    source = packet()
    for sample in source["samples"]:
        for key in ("start", "end", "interval"):
            sample[key]["resolution_ns"] = 3
    assert load().replay(source)["replay_status"] == "PASS"
