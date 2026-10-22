"""Publication evidence tests for issue #3505.

All payloads are synthetic. Expected ages are independent subtraction:
12:00 - 11:00 = one hour; 12:00 today - 10:00 yesterday = 26 hours.
Acceptance limits come from build-equality-matrix.py, PUBLISH_STALE_H and
PUBLISH_SLOW_S (publish-health contract introduced by issue #3502, 2026).
Schema versions and success codes come from equivalence_schema.py and
validate_publish_health in equivalence_state.py (version-1 contracts, 2026).
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "scripts/monitoring/equivalence_publish_check.py"
spec = importlib.util.spec_from_file_location("equivalence_publish_check", MODULE)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)
from equivalence_schema import LEARNING_KEYS

NOW = datetime(2026, 10, 22, 12, tzinfo=UTC)


def fingerprint(**changes):
    data = {
        "fingerprint_version": 1, "machine_id": "example", "hostname": "example",
        "role": "contribute-minimal", "ts": "2026-10-22T11:00:00Z",
        "clone_head": None, "behind_origin": None, "ahead_origin": None,
        "harness_version": None, "harness_install": None, "registry_sha256": None,
        "learning_cron_ages_h": dict.fromkeys(LEARNING_KEYS),
        "provider_soul_hashes": dict.fromkeys(
            ("hermes", "claude", "codex", "codex_agents", "gemini")
        ),
        "on_main": True, "index_lock_stale_min": None, "last_publish_duration_s": None,
    }
    return json.dumps(data | changes)


def health(**changes):
    return json.dumps({
        "schema_version": 1, "ts": "2026-10-22T11:00:02Z", "phase": "publish",
        "duration_s": 2, "rc": 0,
    } | changes)


def report(**changes):
    return {
        "machine": "example", "generated_at": "2026-10-22T11:01:00Z",
        "dimensions": {"publish_health": {
            "last_publish_at": "2026-10-22T11:00:02Z",
            "last_publish_duration_s": 2, "last_publish_rc": 0,
        }},
    } | changes


def assess(**changes):
    inputs = {"machine": "example", "published": fingerprint(), "local": fingerprint(),
              "health": health(), "report": report(), "now": NOW}
    return check.assess(**(inputs | changes))


def test_complete_consistent_evidence_passes():
    result = assess()
    assert result["status"] == "PASS"
    assert all(item["status"] == "PASS" for item in result["checks"].values())
    assert result["checks"]["matrix_publish_health"]["code"] == "PUBLISH-OK"


def test_observed_remote_absence_is_a_failure_not_missing_capture():
    result = assess(published=None)
    assert result["status"] == "FAIL"
    assert result["checks"]["published_fingerprint"]["code"] == "absent-fingerprint"


@pytest.mark.parametrize("field,value", [
    ("published", "{}"), ("published", "not JSON"),
    ("published", fingerprint(machine_id="other")),
    ("published", fingerprint(ts="2026-10-22T13:00:00Z")),
    ("published", fingerprint(ts="2026-10-21T09:59:59Z")),
    ("local", "{}"), ("local", fingerprint(machine_id="other")),
    ("local", fingerprint(clone_head="abcdef1")),
    ("health", health(rc=3)), ("health", health(phase="fingerprint")),
    ("health", health(duration_s=61)),
    ("health", health(ts="2026-10-22T13:00:00Z")),
    ("health", health(ts="2026-10-21T09:59:59Z")),
    ("health", health(ts="2026-10-22T10:59:59Z")),
    ("health", health(duration_s=float("nan"))),
    ("report", report(machine="other")),
    ("report", report(generated_at="2026-10-22T11:00:01Z")),
    ("report", report(generated_at="2026-10-22T13:00:00Z")),
    ("report", report(dimensions=[])),
    ("report", []),
])
def test_inconsistent_or_invalid_evidence_cannot_pass(field, value):
    assert assess(**{field: value})["status"] == "FAIL"


@pytest.mark.parametrize("field", ["local", "health", "report"])
def test_uncaptured_local_evidence_is_not_evaluated(field):
    result = assess(**{field: None})
    assert result["status"] == "NOT_EVALUATED"


def test_matrix_must_describe_the_successful_publish_receipt():
    evidence = report()
    evidence["dimensions"]["publish_health"]["last_publish_duration_s"] = 3
    result = assess(report=evidence)
    assert result["checks"]["matrix_publish_health"]["code"] == "receipt-mismatch"
    assert result["status"] == "FAIL"


def test_time_offsets_representing_the_same_instant_match():
    evidence = report()
    evidence["dimensions"]["publish_health"]["last_publish_at"] = "2026-10-22T12:00:02+01:00"
    assert assess(report=evidence)["status"] == "PASS"


def test_exact_existing_matrix_limits_pass():
    """26h = 12:00 today minus 10:00 yesterday; 60s is the matrix limit.

    Strict greater-than comparisons in the existing matrix permit equality.
    """
    stamp = "2026-10-21T10:00:00Z"
    fp = fingerprint(ts=stamp)
    receipt = health(ts=stamp, duration_s=60)
    evidence = report(generated_at=stamp)
    evidence["dimensions"]["publish_health"].update(
        last_publish_at=stamp, last_publish_duration_s=60,
    )
    assert assess(published=fp, local=fp, health=receipt, report=evidence)["status"] == "PASS"


def test_assessment_requires_an_explicit_aware_clock():
    with pytest.raises(ValueError):
        assess(now=datetime(2026, 10, 22, 12))


def test_no_payloads_or_identifiers_are_echoed():
    marker = "private-evidence-marker"
    result = assess(published=marker, health=marker, report={"machine": marker})
    assert marker not in json.dumps(result)
    assert "example" not in json.dumps(result)


def test_read_git_snapshot_is_pinned_and_ignores_inherited_bindings(tmp_path, monkeypatch):
    """Stub Git without writing metadata; the selected blob is read by its object id."""
    tip, blob = "a" * 40, "b" * 40  # Git SHA-1 object id width, existing store contract.
    calls = []
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE"):
        monkeypatch.setenv(key, "unrelated")

    def run(args, **kwargs):
        assert not any(key in kwargs["env"] for key in (
            "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
        ))
        assert kwargs["cwd"] == tmp_path
        calls.append(args)
        command = args[1]
        if command == "rev-parse":
            output = tip.encode() + b"\n"
        elif command == "ls-tree":
            assert args[-1] == tip
            output = f"100644 blob {blob}\texample.json".encode() + b"\0"
        elif command == "cat-file":
            assert args[-1] == blob
            output = fingerprint().encode()
        else:
            pytest.fail("unexpected Git operation")
        return subprocess.CompletedProcess(args, 0, output, b"")

    monkeypatch.setattr(check.subprocess, "run", run)
    content, revision = check.read_published(tmp_path, "refs/example", "example")
    assert json.loads(content)["machine_id"] == "example"
    assert revision == tip
    assert len(calls) == 3


@pytest.mark.parametrize("entry", [b"", b"100644 blob " + b"b" * 40 + b"\tother.json\0"])
def test_git_snapshot_absence_is_distinct_from_an_unreadable_ref(tmp_path, monkeypatch, entry):
    def run(args, **kwargs):
        output = b"a" * 40 if args[1] == "rev-parse" else entry
        return subprocess.CompletedProcess(args, 0, output, b"")
    monkeypatch.setattr(check.subprocess, "run", run)
    assert check.read_published(tmp_path, "refs/example", "example")[0] is None


@pytest.mark.parametrize("operation", ["rev-parse", "ls-tree", "cat-file"])
def test_git_read_failure_is_not_evaluated_and_redacts_stderr(tmp_path, monkeypatch, operation):
    def run(args, **kwargs):
        if args[1] == operation:
            return subprocess.CompletedProcess(args, 1, b"", b"private-evidence-marker")
        output = (b"a" * 40 if args[1] == "rev-parse" else
                  b"100644 blob " + b"b" * 40 + b"\texample.json\0")
        return subprocess.CompletedProcess(args, 0, output, b"")
    monkeypatch.setattr(check.subprocess, "run", run)
    with pytest.raises(check.EvidenceUnavailable) as exc:
        check.read_published(tmp_path, "refs/example", "example")
    assert "private-evidence-marker" not in str(exc.value)


@pytest.mark.parametrize("machine", ["../escape", "", "bad\nname", "-option"])
def test_unsafe_machine_key_is_rejected_before_git(tmp_path, monkeypatch, machine):
    def forbidden(*args, **kwargs):
        pytest.fail("unsafe input reached Git")
    monkeypatch.setattr(check.subprocess, "run", forbidden)
    with pytest.raises(ValueError):
        check.read_published(tmp_path, "refs/example", machine)


def test_symlink_or_tree_cannot_satisfy_published_evidence(tmp_path, monkeypatch):
    def run(args, **kwargs):
        output = (b"a" * 40 if args[1] == "rev-parse" else
                  b"120000 blob " + b"b" * 40 + b"\texample.json\0")
        return subprocess.CompletedProcess(args, 0, output, b"")
    monkeypatch.setattr(check.subprocess, "run", run)
    with pytest.raises(check.EvidenceUnavailable):
        check.read_published(tmp_path, "refs/example", "example")


def test_cli_checks_yaml_and_does_not_modify_inputs(tmp_path, monkeypatch, capsys):
    paths = {}
    for name, content in (("local", fingerprint()), ("health", health()),
                          ("report", "machine: example\n" +
                           "generated_at: '2026-10-22T11:01:00Z'\n" +
                           "dimensions:\n  publish_health:\n" +
                           "    last_publish_at: '2026-10-22T11:00:02Z'\n" +
                           "    last_publish_duration_s: 2\n    last_publish_rc: 0\n")):
        paths[name] = tmp_path / name
        paths[name].write_text(content)
    before = {name: path.read_bytes() for name, path in paths.items()}
    monkeypatch.setattr(check, "read_published", lambda *args: (fingerprint(), "a" * 40))
    rc = check.main([
        "--repo", str(tmp_path), "--state-ref", "refs/example", "--machine", "example",
        "--local-fingerprint", str(paths["local"]), "--health", str(paths["health"]),
        "--equality-report", str(paths["report"]), "--as-of", NOW.isoformat(),
    ])
    output = json.loads(capsys.readouterr().out)
    assert rc == 0 and output["status"] == "PASS"
    assert output["state_revision"] == "a" * 40
    assert before == {name: path.read_bytes() for name, path in paths.items()}


def test_cli_missing_capture_and_ref_cannot_pass(tmp_path, monkeypatch, capsys):
    def unavailable(*args):
        raise check.EvidenceUnavailable("state-ref-unavailable")
    monkeypatch.setattr(check, "read_published", unavailable)
    assert check.main([
        "--repo", str(tmp_path), "--machine", "example", "--state-ref", "refs/example",
        "--as-of", NOW.isoformat(),
    ]) == 1  # CLI contract: zero only when all evidence passes.
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "NOT_EVALUATED"
    assert output["checks"]["published_fingerprint"]["code"] == "state-ref-unavailable"


def test_script_help_runs_without_repository_mutations():
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run([sys.executable, str(MODULE), "--help"], env=env,
                            capture_output=True, text=True, check=False)
    assert result.returncode == 0 and "--state-ref" in result.stdout


def test_worked_example_matches_the_independent_answer():
    example_path = ROOT / "tests/monitoring/equivalence_publish_example.py"
    example_spec = importlib.util.spec_from_file_location("publication_example", example_path)
    example_module = importlib.util.module_from_spec(example_spec)
    example_spec.loader.exec_module(example_module)
    assert example_module.example() == {
        "status": "PASS",
        "checks": {
            "published_fingerprint": {"status": "PASS", "code": "published-fingerprint"},
            "local_publish": {"status": "PASS", "code": "publish-succeeded"},
            "matrix_publish_health": {"status": "PASS", "code": "PUBLISH-OK"},
        },
    }


def test_cli_inspects_a_real_local_tree_without_writing_git(tmp_path):
    """The repository tree contains no synthetic example fingerprint.

    The independently known answer is FAIL/absent-fingerprint even when local
    captures are unavailable. All real Git operations are read-only.
    """
    result = subprocess.run([
        sys.executable, str(MODULE), "--repo", str(ROOT), "--state-ref", "HEAD",
        "--machine", "example", "--local-fingerprint", str(tmp_path / "missing-local"),
        "--health", str(tmp_path / "missing-health"),
        "--equality-report", str(tmp_path / "missing-report"), "--as-of", NOW.isoformat(),
    ], capture_output=True, text=True, check=False)
    output = json.loads(result.stdout)
    assert result.returncode == 1
    assert output["status"] == "FAIL"
    assert output["checks"]["published_fingerprint"]["code"] == "absent-fingerprint"
    assert output["state_revision"]


@pytest.mark.parametrize("filename,content", [
    ("local", "{}"), ("health", "{}"), ("report", "dimensions: ["), ("report", ""),
])
def test_cli_invalid_capture_fails_with_redacted_output(tmp_path, monkeypatch, capsys,
                                                      filename, content):
    paths = {"local": tmp_path / "local", "health": tmp_path / "health",
             "report": tmp_path / "report"}
    paths["local"].write_text(fingerprint())
    paths["health"].write_text(health())
    paths["report"].write_text(json.dumps(report()))
    paths[filename].write_text(content)
    monkeypatch.setattr(check, "read_published", lambda *args: (fingerprint(), "a" * 40))
    result = check.main([
        "--repo", str(tmp_path), "--machine", "example", "--state-ref", "refs/example",
        "--local-fingerprint", str(paths["local"]), "--health", str(paths["health"]),
        "--equality-report", str(paths["report"]), "--as-of", NOW.isoformat(),
    ])
    output = capsys.readouterr().out
    assert result == 1 and json.loads(output)["status"] == "FAIL"
    assert str(tmp_path) not in output
