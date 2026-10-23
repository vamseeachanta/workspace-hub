"""Independent arithmetic fixtures for qualified behavioral parity.

All quantities are synthetic counts, not measured provider performance.
Criteria are explicit test inputs, not universal acceptance limits.
"""
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "parity_evaluation", Path(__file__).resolve().parents[2]
    / "scripts" / "ai" / "parity_evaluation.py",
)
pe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pe)


@pytest.fixture
def criteria():
    return {"reference": "synthetic-example-v1", "minimum_sessions": 2,
            "verbosity_multiplier": 2, "clarification_delta": 1}


def digest(turns=4, tokens=40, asks=0, model="candidate"):
    return {"turns_by_model": {model: turns},
            "out_tokens_by_model": {model: tokens},
            "tool_histogram": {"AskUserQuestion": asks}}


def evaluate(criteria, current=None, baseline=None):
    return pe.evaluate_parity(
        [digest(), digest()] if current is None else current,
        [digest(model="reference"), digest(model="reference")]
        if baseline is None else baseline,
        "candidate", "reference", criteria,
    )


def test_worked_example(criteria):
    """Candidate (40+120)/(4+6)=16; reference (20+60)/(2+8)=8.

    Token limit 8*2=16, equality passes. Ask means (0+2)/2=1 and
    (0+0)/2=0, hence difference 1 equals the input limit and passes.
    """
    report = evaluate(criteria, [digest(4, 40), digest(6, 120, 2)],
                      [digest(2, 20, model="reference"),
                       digest(8, 60, model="reference")])
    assert report["status"] == "WITHIN_LIMITS"
    assert report["metrics"]["tokens_per_turn"]["current"] == 16
    assert report["metrics"]["tokens_per_turn"]["baseline"] == 8
    assert report["metrics"]["askuser_per_session"]["current"] == 1
    assert report["criteria"] == criteria


def test_regression_uses_unrounded_counts(criteria):
    """201/10=20.1 exceeds (100/10)*2=20, independent of display."""
    report = evaluate(criteria, [digest(5, 100), digest(5, 101)],
                      [digest(5, 50, model="reference")] * 2)
    assert report["status"] == "REGRESSION"
    assert report["metrics"]["tokens_per_turn"]["limit"] == 20


def test_clarification_regression(criteria):
    """(2+2)/2=2 exceeds reference 0 plus the input delta of 1."""
    report = evaluate(criteria, [digest(asks=2)] * 2)
    assert report["metrics"]["askuser_per_session"]["status"] == "REGRESSION"


@pytest.mark.parametrize("which", ["current", "baseline"])
def test_empty_or_short_cohort_is_not_evaluated(criteria, which):
    for records in ([], [digest(model="candidate" if which == "current" else "reference")]):
        report = evaluate(criteria, **{which: records})
        assert report["status"] == "NOT_EVALUATED"
        assert all(m["status"] == "NOT_EVALUATED" for m in report["metrics"].values())


def test_zero_reference_rate_is_not_evaluated(criteria):
    report = evaluate(criteria, baseline=[digest(tokens=0, model="reference")] * 2)
    assert report["metrics"]["tokens_per_turn"]["status"] == "NOT_EVALUATED"
    assert report["status"] == "NOT_EVALUATED"


def test_mixed_model_tool_counts_are_not_attributed(criteria):
    record = digest()
    record["turns_by_model"]["other"] = 1
    report = evaluate(criteria, current=[record, digest()])
    assert report["metrics"]["askuser_per_session"]["status"] == "NOT_EVALUATED"
    assert report["metrics"]["tokens_per_turn"]["status"] == "WITHIN_LIMITS"


def test_regression_is_visible_even_with_unevaluated_metric(criteria):
    record = digest(tokens=1000)
    record["turns_by_model"]["other"] = 1
    report = evaluate(criteria, current=[record] * 2)
    assert report["status"] == "REGRESSION"
    assert report["metrics"]["askuser_per_session"]["status"] == "NOT_EVALUATED"


@pytest.mark.parametrize("key,value", [
    ("minimum_sessions", 0), ("minimum_sessions", True),
    ("minimum_sessions", 1.5), ("verbosity_multiplier", 0),
    ("verbosity_multiplier", float("inf")), ("verbosity_multiplier", True),
    ("clarification_delta", -1), ("clarification_delta", float("nan")),
    ("reference", " "),
])
def test_invalid_criteria_rejected(criteria, key, value):
    criteria[key] = value
    with pytest.raises(ValueError):
        evaluate(criteria)


@pytest.mark.parametrize("field", ["turns_by_model", "out_tokens_by_model", "tool_histogram"])
@pytest.mark.parametrize("value", [-1, True, 1.5, float("nan"), "4"])
def test_invalid_counts_rejected(criteria, field, value):
    record = digest()
    key = "AskUserQuestion" if field == "tool_histogram" else "candidate"
    record[field][key] = value
    with pytest.raises(ValueError):
        evaluate(criteria, current=[record])


def test_missing_tokens_rejected(criteria):
    record = digest()
    record["out_tokens_by_model"] = {}
    with pytest.raises(ValueError):
        evaluate(criteria, current=[record])


def test_missing_histogram_rejected(criteria):
    record = digest()
    del record["tool_histogram"]
    with pytest.raises(TypeError):
        evaluate(criteria, current=[record])


def test_unrelated_models_do_not_add_samples(criteria):
    assert evaluate(criteria, current=[digest(model="other")] * 2)["status"] == "NOT_EVALUATED"


@pytest.mark.parametrize("text", ['{"x":1,"x":2}', '{"x":NaN}', '[]', 'null'])
def test_json_loader_rejects_ambiguous_or_nonobject_input(tmp_path, text):
    path = tmp_path / "bad.json"
    path.write_text(text, encoding="utf-8", newline="\n")
    with pytest.raises((ValueError, TypeError)):
        pe.read_object(path)


def test_loader_does_not_skip_corrupt_files(tmp_path):
    (tmp_path / "bad.json").write_text("broken", encoding="utf-8", newline="\n")
    with pytest.raises(ValueError):
        pe.load_cohort(tmp_path)


@pytest.mark.parametrize("state,exit_code", [("within", 0), ("regression", 1), ("empty", 2)])
def test_cli(tmp_path, capsys, criteria, state, exit_code):
    """Reference 10 tok/turn, candidate 10 or 100, limit 20."""
    current = tmp_path / "current"
    baseline = tmp_path / "baseline"
    current.mkdir()
    baseline.mkdir()
    for index in range(2):
        if state != "empty":
            (current / f"{index}.json").write_text(json.dumps(
                digest(tokens=400 if state == "regression" else 40)), encoding="utf-8", newline="\n")
        (baseline / f"{index}.json").write_text(json.dumps(digest(model="reference")), encoding="utf-8", newline="\n")
    policy = tmp_path / "criteria.json"
    policy.write_text(json.dumps(criteria), encoding="utf-8", newline="\n")
    assert pe.main([str(current), str(baseline), "--model", "candidate",
                    "--baseline-model", "reference", "--criteria", str(policy)]) == exit_code
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == {0: "WITHIN_LIMITS", 1: "REGRESSION", 2: "NOT_EVALUATED"}[exit_code]


def test_cli_invalid_input_is_error(tmp_path, capsys, criteria):
    policy = tmp_path / "criteria.json"
    policy.write_text(json.dumps(criteria), encoding="utf-8", newline="\n")
    assert pe.main([str(tmp_path / "absent"), str(tmp_path), "--model", "candidate",
                    "--baseline-model", "reference", "--criteria", str(policy)]) == 2
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "ERROR"
    assert str(tmp_path) not in json.dumps(report)


def test_small_exceedance_survives_display_rounding(criteria):
    """2001/100=20.01 exceeds 1000/100*2=20 with a displayed limit of 20.000."""
    report = evaluate(criteria, [digest(50, 1000), digest(50, 1001)],
                      [digest(50, 500, model="reference")] * 2)
    metric = report["metrics"]["tokens_per_turn"]
    assert metric["status"] == "REGRESSION"
    assert metric["current"] == 20.01
    assert metric["limit"] == 20.0


def test_documented_example(tmp_path, capsys):
    """Execute the HTML example: independently 160/10=16 and 80/10=8.

    The supplied multiplier gives limit 16; clarification means are 1 and 0,
    with a supplied delta of 1. Both equalities meet their respective limits.
    """
    from html.parser import HTMLParser

    class Examples(HTMLParser):
        def __init__(self):
            super().__init__()
            self.key = None
            self.values = {}

        def handle_starttag(self, tag, attrs):
            if tag == "pre":
                self.key = dict(attrs).get("id")
                if self.key:
                    self.values[self.key] = ""

        def handle_data(self, data):
            if self.key:
                self.values[self.key] += data

        def handle_endtag(self, tag):
            if tag == "pre":
                self.key = None

    examples = Examples()
    doc = Path(__file__).resolve().parents[2] / "docs/ai/behavioral-parity-evaluation.html"
    document = doc.read_text(encoding="utf-8")
    assert "examples/current" not in document
    assert '"$PARITY_EVIDENCE_DIR/current"' in document
    assert "outside the" in document
    examples.feed(document)
    for cohort in ("current", "baseline"):
        folder = tmp_path / cohort
        folder.mkdir()
        for index, record in enumerate(json.loads(examples.values[f"example-{cohort}"])):
            (folder / f"{index}.json").write_text(json.dumps(record), encoding="utf-8", newline="\n")
    policy = tmp_path / "criteria.json"
    policy.write_text(examples.values["example-criteria"], encoding="utf-8", newline="\n")
    assert pe.main([str(tmp_path / "current"), str(tmp_path / "baseline"),
                    "--model", "candidate", "--baseline-model", "reference",
                    "--criteria", str(policy)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "WITHIN_LIMITS"
    assert result["metrics"]["tokens_per_turn"]["current"] == 16
    assert result["metrics"]["tokens_per_turn"]["baseline"] == 8
    assert result["metrics"]["askuser_per_session"]["current"] == 1


@pytest.mark.parametrize("target", ["cohort", "criteria"])
def test_cli_deep_json_is_error(tmp_path, capsys, criteria, target):
    cohort = tmp_path / "cohort"
    cohort.mkdir()
    policy = tmp_path / "criteria.json"
    policy.write_text(json.dumps(criteria), encoding="utf-8", newline="\n")
    path = cohort / "deep.json" if target == "cohort" else policy
    path.write_text("[" * 2000 + "]" * 2000, encoding="utf-8", newline="\n")
    assert pe.main([str(cohort), str(cohort), "--model", "candidate",
                    "--baseline-model", "reference", "--criteria", str(policy)]) == 2
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "ERROR"
    assert str(tmp_path) not in json.dumps(report)


def test_exact_decimal_equality(criteria):
    """Reference 7/10 times 3 = 21/10, exactly equal to candidate 21/10."""
    criteria["verbosity_multiplier"] = 3
    report = evaluate(criteria, [digest(5, 10), digest(5, 11)],
                      [digest(5, 3, model="reference"),
                       digest(5, 4, model="reference")])
    assert report["metrics"]["tokens_per_turn"]["status"] == "WITHIN_LIMITS"
    assert report["metrics"]["tokens_per_turn"]["limit"] == 2.1


def test_clarification_display_preserves_margin(criteria):
    """3/20 = 0.150 exceeds 1/20 + 0.05 = 0.100 calls per session."""
    criteria["clarification_delta"] = 0.05
    report = evaluate(criteria, [digest(asks=3)] + [digest()] * 19,
                      [digest(asks=1, model="reference")]
                      + [digest(model="reference")] * 19)
    metric = report["metrics"]["askuser_per_session"]
    assert metric["status"] == "REGRESSION"
    assert (metric["current"], metric["baseline"], metric["limit"]) == (0.15, 0.05, 0.1)


def test_cli_evidence_hashes_loaded_bytes(tmp_path, capsys, criteria):
    cohort = tmp_path / "cohort"
    cohort.mkdir()
    payload = json.dumps(digest(), indent=2).encode("utf-8")
    (cohort / "sample.json").write_bytes(payload)
    policy = tmp_path / "criteria.json"
    policy.write_text(json.dumps(criteria), encoding="utf-8", newline="\n")
    pe.main([str(cohort), str(cohort), "--model", "candidate",
             "--baseline-model", "reference", "--criteria", str(policy)])
    report = json.loads(capsys.readouterr().out)
    assert report["models"] == {"current": "candidate", "baseline": "reference"}
    expected = [hashlib.sha256(payload).hexdigest()]
    assert report["evidence_sha256"] == {
        "current": expected, "baseline": expected,
        "criteria": [hashlib.sha256(policy.read_bytes()).hexdigest()],
    }
    assert str(tmp_path) not in json.dumps(report)


@pytest.mark.parametrize("key,lexeme,asks,metric,exit_code", [
    ("verbosity_multiplier", "0.99999999999999999", 0, "tokens_per_turn", 1),
    ("verbosity_multiplier", "1.00000000000000001", 0, "tokens_per_turn", 0),
    ("clarification_delta", "0.99999999999999999", 1, "askuser_per_session", 1),
    ("clarification_delta", "1.00000000000000001", 1, "askuser_per_session", 0),
])
def test_cli_preserves_decimal_criteria(tmp_path, capsys, key, lexeme, asks,
                                       metric, exit_code):
    """10*(1-10^-17)<10; 0+(1-10^-17)<1; opposite boundaries pass."""
    current = tmp_path / "current"
    baseline = tmp_path / "baseline"
    current.mkdir()
    baseline.mkdir()
    (current / "sample.json").write_text(
        json.dumps(digest(1, 10, asks)), encoding="utf-8", newline="\n")
    (baseline / "sample.json").write_text(
        json.dumps(digest(1, 10, model="reference")), encoding="utf-8", newline="\n")
    policy = tmp_path / "criteria.json"
    text = ('{"reference":"synthetic-boundary","minimum_sessions":1,'
            '"verbosity_multiplier":1,"clarification_delta":0}')
    original = '"verbosity_multiplier":1' if key == "verbosity_multiplier" else '"clarification_delta":0'
    text = text.replace(original, f'"{key}":{lexeme}')
    policy.write_text(text, encoding="utf-8", newline="\n")
    assert pe.main([str(current), str(baseline), "--model", "candidate",
                    "--baseline-model", "reference", "--criteria", str(policy)]) == exit_code
    report = json.loads(capsys.readouterr().out)
    assert report["metrics"][metric]["status"] == (
        "REGRESSION" if exit_code else "WITHIN_LIMITS")
    assert report["criteria"][key] == lexeme


@pytest.mark.parametrize("target", ["cohort", "criteria"])
@pytest.mark.parametrize("lexeme", ["1e9999999999999999999", "1e-9999999999999999999"])
def test_cli_unsupported_decimal_is_error(tmp_path, criteria, target, lexeme):
    """Unsupported decimal exponents are invalid evidence, never regressions."""
    cohort = tmp_path / "cohort"
    cohort.mkdir()
    policy = tmp_path / "criteria.json"
    policy.write_text(json.dumps(criteria), encoding="utf-8", newline="\n")
    path = cohort / "sample.json" if target == "cohort" else policy
    path.write_text('{"value":' + lexeme + '}', encoding="utf-8", newline="\n")
    result = subprocess.run(
        [sys.executable, str(SPEC.origin), str(cohort), str(cohort),
         "--model", "candidate", "--baseline-model", "reference",
         "--criteria", str(policy)],
        capture_output=True, encoding="utf-8", check=False,
    )
    assert result.returncode == 2
    assert result.stderr == ""
    report = json.loads(result.stdout)
    assert report == {"status": "ERROR", "reason": "input is unreadable or invalid JSON"}
