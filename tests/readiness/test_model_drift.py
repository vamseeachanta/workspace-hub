"""Offline gate examples; dates and counts are independently derived below."""

import importlib.util
import json
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "model_drift", ROOT / "scripts/readiness/model_drift.py"
)
gate = importlib.util.module_from_spec(SPEC)


@pytest.fixture(autouse=True)
def load_gate():
    SPEC.loader.exec_module(gate)


@pytest.fixture
def registry():
    # Synthetic IDs and capacities are inputs, not provider specifications.
    return {"latest_models": {"claude_primary": "alpha", "claude_strong": "beta",
                              "openai_primary": "gamma"},
            "context_windows_k": {"alpha": 1, "beta": 1, "gamma": 1},
            "last_updated": "2026-10-01"}


def evaluate(registry, tmp_path):
    return gate.evaluate(registry, tmp_path, tmp_path, date(2026, 10, 15), 14)


def test_missing_strong_context(registry, tmp_path):
    del registry["context_windows_k"]["beta"]
    assert ("FAIL", "claude_strong: context window missing for beta") in evaluate(registry, tmp_path)


@pytest.mark.parametrize("value", [None, "", 9, []])
def test_invalid_id(registry, tmp_path, value):
    registry["latest_models"]["claude_strong"] = value
    assert any(s == "FAIL" and "claude_strong" in m for s, m in evaluate(registry, tmp_path))


def test_alias_must_document_exact_keys(registry, tmp_path):
    registry["latest_models"]["claude_strong"] = "alpha"
    assert any(s == "FAIL" and "shared" in m for s, m in evaluate(registry, tmp_path))
    registry["model_aliases"] = {"alpha": ["claude_primary", "claude_strong"]}
    assert not any(s == "FAIL" for s, _ in evaluate(registry, tmp_path))


def test_deprecated_reference(registry, tmp_path):
    registry["audit"] = {"old": {"model_id": "beta", "deprecated": True}}
    assert any(s == "FAIL" and "deprecated" in m for s, m in evaluate(registry, tmp_path))
    registry["latest_models"].pop("claude_strong")
    registry["context_windows_k"].pop("beta")
    assert not any(s == "FAIL" for s, _ in evaluate(registry, tmp_path))


@pytest.mark.parametrize("offset,status", [(13, "PASS"), (14, "PASS"), (15, "WARN")])
def test_freshness_boundary(registry, tmp_path, offset, status):
    """October day 1 to day 14/15/16 is 13/14/15 days; bound is fixture input 14."""
    rows = gate.evaluate(registry, tmp_path, tmp_path, date(2026, 10, 1 + offset), 14)
    assert any(s == status and m.startswith("freshness:") for s, m in rows)


@pytest.mark.parametrize("value", [None, "not-a-date", "2026-02-30"])
def test_invalid_date(registry, tmp_path, value):
    registry["last_updated"] = value
    assert any(s == "NOT_EVALUATED" and m.startswith("freshness:") for s, m in evaluate(registry, tmp_path))


def test_all_readable_match(registry, tmp_path):
    """Three supplied observations compare; one strong key has no live binding."""
    for directory, name, text in [
        (".claude", "settings.json", '{"model":"alpha"}'),
        (".codex", "config.toml", 'model = "gamma"'),
        (".hermes", "config.yaml", 'model: gamma'),
    ]:
        target = tmp_path / directory / name
        target.parent.mkdir(exist_ok=True)
        target.write_text(text)
    rows = evaluate(registry, tmp_path)
    assert not any(s == "FAIL" for s, _ in rows)
    assert rows[-1] == ("INFO", "live: compared=3 not_evaluated=1")


@pytest.mark.parametrize("model,status", [("gamma", "PASS"), ("beta", "FAIL")])
def test_hermes_mapping_default(registry, tmp_path, model, status):
    cfg = tmp_path / ".hermes/config.yaml"
    cfg.parent.mkdir()
    cfg.write_text(f"model:\n  default: {model}\n  provider: fixture-provider\n")
    rows = evaluate(registry, tmp_path)
    assert (status, f"openai_primary/hermes: live={model} registry=gamma") in rows


@pytest.mark.parametrize("project_model", [
    "model:\n  default: beta\n  provider: fixture-provider\n",
    "model: beta\n",
])
def test_hermes_project_override(registry, tmp_path, project_model):
    user, project = tmp_path / "user", tmp_path / "project"
    for root, text in [
        (user, "model:\n  default: gamma\n  provider: fixture-provider\n"),
        (project, project_model),
    ]:
        cfg = root / ".hermes/config.yaml"
        cfg.parent.mkdir(parents=True)
        cfg.write_text(text)
    rows = gate.evaluate(registry, user, project, date(2026, 10, 15), 14)
    assert ("FAIL", "openai_primary/hermes: live=beta registry=gamma") in rows


def test_hermes_provider_only_does_not_override_default(registry, tmp_path):
    user, project = tmp_path / "user", tmp_path / "project"
    for root, text in [
        (user, "model:\n  default: gamma\n  provider: fixture-provider\n"),
        (project, "model:\n  provider: another-provider\n"),
    ]:
        cfg = root / ".hermes/config.yaml"
        cfg.parent.mkdir(parents=True)
        cfg.write_text(text)
    rows = gate.evaluate(registry, user, project, date(2026, 10, 15), 14)
    assert ("PASS", "openai_primary/hermes: live=gamma registry=gamma") in rows


@pytest.mark.parametrize("value", ["null", "false", "''", "[]", "{}"])
def test_hermes_invalid_default_fails(value, tmp_path, registry):
    cfg = tmp_path / ".hermes/config.yaml"
    cfg.parent.mkdir()
    cfg.write_text(f"model:\n  default: {value}\n  provider: fixture-provider\n")
    assert ("FAIL", "openai_primary/hermes: invalid model value") in evaluate(registry, tmp_path)


@pytest.mark.parametrize("model", ["alpha", "unused"])
@pytest.mark.parametrize("value", [None, 0, -1, "unknown", True, False,
                                  float("inf"), float("-inf"), float("nan"), [], {}])
def test_invalid_context_capacity(registry, tmp_path, model, value):
    """All context entries, including unused ones, need a positive finite number."""
    registry["context_windows_k"][model] = value
    rows = evaluate(registry, tmp_path)
    assert ("FAIL", f"context_windows_k/{model}: positive finite number required") in rows
    if model == "alpha":
        assert ("PASS", "claude_primary: registry consistent") not in rows


@pytest.mark.parametrize("value", [1, 0.5])
def test_positive_context_capacity(registry, tmp_path, value):
    registry["context_windows_k"]["alpha"] = value
    registry["context_windows_k"]["unused"] = value
    assert not any(s == "FAIL" for s, _ in evaluate(registry, tmp_path))


@pytest.mark.parametrize("text,expected", [
    ('{"model":"future-generation"}', "unknown id future-generation"),
    ('{"model":"beta"}', "live=beta registry=alpha"),
    ('{broken', "malformed"),
    ('{"model":false}', "invalid model"),
])
def test_claude_failure(registry, tmp_path, text, expected):
    cfg = tmp_path / ".claude/settings.json"
    cfg.parent.mkdir()
    cfg.write_text(text)
    assert any(s == "FAIL" and expected in m for s, m in evaluate(registry, tmp_path))


def test_missing_claude_is_not_evaluated(registry, tmp_path):
    assert ("NOT_EVALUATED", "claude_primary/claude: no readable configuration") in evaluate(registry, tmp_path)


def test_project_override_is_not_hidden_by_user(registry, tmp_path):
    user = tmp_path / "user"
    project = tmp_path / "project"
    for root, model in [(user, "alpha"), (project, "beta")]:
        cfg = root / ".claude/settings.json"
        cfg.parent.mkdir(parents=True)
        cfg.write_text(json.dumps({"model": model}))
    rows = gate.evaluate(registry, user, project, date(2026, 10, 15), 14)
    assert any(s == "FAIL" and "live=beta registry=alpha" in m for s, m in rows)


def test_nightly_adapter_does_not_report_partial_pass(tmp_path):
    """An all-missing runtime has zero comparisons and three missing sources."""
    import os
    import subprocess

    (tmp_path / "config/agents").mkdir(parents=True)
    (tmp_path / "scripts/readiness").mkdir(parents=True)
    (tmp_path / "scripts/readiness/model_drift.py").write_bytes(
        (ROOT / "scripts/readiness/model_drift.py").read_bytes()
    )
    (tmp_path / "config/agents/model-registry.yaml").write_text(
        'latest_models: {claude_primary: alpha, openai_primary: gamma}\n'
        'context_windows_k: {alpha: 1, gamma: 1}\nlast_updated: "2026-10-01"\n'
    )
    text = (ROOT / "scripts/readiness/nightly-readiness.sh").read_text()
    start = text.index("check_r_model_drift() {")
    function = text[start:text.index("} ; check_r_model_drift || true", start) + 1]
    script = ('declare -A check_results=() check_details=()\n'
              'log_pass() { echo "AGGREGATE_PASS"; }\n'
              'log_fail() { echo "AGGREGATE_FAIL"; }\n' + function +
              '\ncheck_r_model_drift\nprintf "%s" "${check_results[R-MODEL-DRIFT]}"')
    env = dict(os.environ, WORKSPACE_HUB=str(tmp_path), HOME=str(tmp_path / "absent"))
    env.pop("MODEL_REGISTRY_FILE", None)
    proc = subprocess.run(["bash", "-c", script], env=env, text=True, capture_output=True, check=True)
    assert "compared=0 not_evaluated=3" in proc.stdout
    assert "AGGREGATE_PASS" not in proc.stdout
    assert proc.stdout.endswith("not_evaluated")


def test_nightly_report_is_not_green_when_drift_is_unevaluated(tmp_path):
    """Zero failed checks plus one unevaluated check cannot establish a pass."""
    import os
    import subprocess

    text = (ROOT / "scripts/readiness/nightly-readiness.sh").read_text()
    start = text.index("_emit_harness_report() {")
    function = text[start:text.index("} ; _emit_harness_report || true", start) + 1]
    script = ('_resolve_workstation_key() { echo fixture; }\n'
              'declare -A check_results=([R-MODEL-DRIFT]=not_evaluated)\n'
              'declare -A check_details=([R-MODEL-DRIFT]=missing)\n'
              'fail_count=0; pass_count=0; not_evaluated_count=1; RUN_TS=fixture\n' + function +
              '\n_emit_harness_report')
    subprocess.run(["bash", "-c", script], env=dict(os.environ, STATE_DIR=str(tmp_path)), check=True)
    assert "overall: not_evaluated" in (tmp_path / "harness-readiness-fixture.yaml").read_text()


def test_worked_example_output(tmp_path):
    """The documented output is read back from an independent synthetic fixture."""
    import subprocess
    import sys

    fixtures = ROOT / "tests/readiness/fixtures/model-drift"
    project = tmp_path / "project"
    settings = project / ".claude/settings.json"
    settings.parent.mkdir(parents=True)
    settings.write_bytes((fixtures / "settings.json").read_bytes())
    proc = subprocess.run([
        sys.executable, str(ROOT / "scripts/readiness/model_drift.py"),
        "--registry", str(fixtures / "registry.yaml"), "--user-root", str(tmp_path / "empty"),
        "--project-root", str(project), "--today", "2026-10-15",
    ], capture_output=True, text=True, check=True)
    doc = (ROOT / "docs/operations/model-drift.md").read_text()
    expected = doc.split("```text\n", 1)[1].split("```", 1)[0]
    assert proc.stdout == expected


def test_duplicate_yaml_keys_are_not_silent():
    with pytest.raises(ValueError, match="duplicate"):
        gate.yaml.load("latest_models: {x: alpha, x: beta}", Loader=gate.UniqueLoader)
