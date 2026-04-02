"""Standardized execute gate variation tests (WRK-679 / issue #198).

Ensures the execute stage gate (Stage 10 — Work Execution) is tested with
the same disciplined pattern used for Stage 5, 7, and 17 gates.

Variation categories follow the standard gate-test matrix:
  V1  — disabled config → gate passes unconditionally
  V2  — missing config → infrastructure failure (None / exit 2)
  V3  — missing evidence artifact → gate fails
  V4  — happy-path: all required fields present → gate passes
  V5  — integrated_repo_tests count below minimum → gate fails
  V6  — integrated_repo_tests count at minimum (3) → gate passes
  V7  — integrated_repo_tests count at maximum (5) → gate passes
  V8  — integrated_repo_tests count above maximum → gate fails
  V9  — test with failing result → gate fails
  V10 — missing artifact_ref on a test entry → gate fails
  V11 — missing execute.yaml file entirely → gate fails
  V12 — malformed YAML in execute.yaml → infrastructure failure
  V13 — wrk_id mismatch between evidence and request → gate fails
  V14 — migration exemption with human authority → gate passes
  V15 — migration exemption with agent authority → gate fails
  V16 — resource-intelligence-update gate variations (linked gate)
  V17 — empty integrated_repo_tests list → gate fails

Each test is self-contained using tmp_path fixtures.
No external script imports required — gate logic is implemented inline
to provide a reference specification for the execute gate contract.

Run: uv run pytest tests/unit/test_execute_gate_variations.py -v
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


# ═══════════════════════════════════════════════════════════════════════════════
# GATE LOGIC — Reference implementation of execute gate checks
# ═══════════════════════════════════════════════════════════════════════════════
#
# This mirrors the contract enforced by verify-gate-evidence.py and provides
# a specification-as-code for the execute gate.

_EXECUTE_GATE_CONFIG_FILENAME = "execute-gate-config.yaml"
_EXECUTE_EVIDENCE_FILENAME = "execute.yaml"
_EXEMPTION_FILENAME = "execute-migration-exemption.yaml"

_MIN_INTEGRATED_TESTS = 3
_MAX_INTEGRATED_TESTS = 5
_PASSING_RESULTS = {"pass", "passed", "ok", "success"}


def _load_yaml(path: Path) -> dict[str, Any] | None:
    """Load a YAML file, returning None on parse error."""
    if yaml is None:
        return None
    try:
        text = path.read_text(encoding="utf-8")
        return yaml.safe_load(text) or {}
    except Exception:
        return None


def _load_config(workspace_root: Path) -> dict[str, Any] | None:
    """Load execute gate config from workspace scripts dir."""
    config_path = workspace_root / "scripts" / "work-queue" / _EXECUTE_GATE_CONFIG_FILENAME
    if not config_path.exists():
        return None
    return _load_yaml(config_path)


def check_execute_gate(
    wrk_id: str,
    assets_dir: Path,
    workspace_root: Path,
) -> tuple[bool | None, str]:
    """Check the execute gate for a WRK item.

    Returns:
        (True, detail)  — gate passes
        (False, detail) — gate fails (predicate failure)
        (None, detail)  — infrastructure failure (config missing / malformed)
    """
    # 1. Load config
    config = _load_config(workspace_root)
    if config is None:
        config_path = workspace_root / "scripts" / "work-queue" / _EXECUTE_GATE_CONFIG_FILENAME
        if not config_path.exists():
            return None, f"config missing: {_EXECUTE_GATE_CONFIG_FILENAME}"
        return None, f"config malformed: {_EXECUTE_GATE_CONFIG_FILENAME}"

    # 2. Check activation
    activation = config.get("activation", "full")
    if activation == "disabled":
        return True, "execute gate disabled — skipped"

    # 3. Check for migration exemption
    evidence_dir = assets_dir / "evidence"
    exemption_path = evidence_dir / _EXEMPTION_FILENAME
    if exemption_path.exists():
        exemption = _load_yaml(exemption_path)
        if exemption:
            approved_by = exemption.get("approved_by", "")
            allowlist = config.get("human_authority_allowlist", [])
            if approved_by and approved_by in allowlist:
                return True, f"execute gate exemption accepted (approved_by={approved_by})"
            return False, f"execute gate exemption rejected: approved_by='{approved_by}' not in allowlist"

    # 4. Check evidence file exists
    evidence_path = evidence_dir / _EXECUTE_EVIDENCE_FILENAME
    if not evidence_path.exists():
        return False, f"missing {_EXECUTE_EVIDENCE_FILENAME}"

    # 5. Parse evidence
    evidence = _load_yaml(evidence_path)
    if evidence is None:
        return None, f"malformed YAML in {_EXECUTE_EVIDENCE_FILENAME}"

    # 6. Check wrk_id match
    evidence_wrk = evidence.get("wrk_id", "")
    if evidence_wrk and evidence_wrk != wrk_id:
        return False, f"wrk_id mismatch: evidence has '{evidence_wrk}', expected '{wrk_id}'"

    # 7. Check integrated_repo_tests
    tests = evidence.get("integrated_repo_tests", [])
    if not isinstance(tests, list):
        return False, "integrated_repo_tests must be a list"

    count = len(tests)
    if count < _MIN_INTEGRATED_TESTS:
        return False, f"integrated_repo_tests count must be {_MIN_INTEGRATED_TESTS}-{_MAX_INTEGRATED_TESTS}, got {count}"
    if count > _MAX_INTEGRATED_TESTS:
        return False, f"integrated_repo_tests count must be {_MIN_INTEGRATED_TESTS}-{_MAX_INTEGRATED_TESTS}, got {count}"

    # 8. Check all tests have required fields and passing results
    for i, t in enumerate(tests):
        if not isinstance(t, dict):
            return False, f"integrated_repo_tests[{i}] must be a mapping"
        name = t.get("name", "")
        result = t.get("result", "").lower()
        artifact_ref = t.get("artifact_ref", "")

        if not name:
            return False, f"integrated_repo_tests[{i}] missing 'name'"
        if result not in _PASSING_RESULTS:
            return False, f"integrated_repo_tests[{i}] '{name}' result='{result}' not in {_PASSING_RESULTS}"
        if not artifact_ref:
            return False, f"integrated_repo_tests[{i}] '{name}' missing 'artifact_ref'"

    return True, f"execute gate passed: integrated_repo_tests={count}"


def check_resource_intelligence_update_gate(
    assets_dir: Path,
) -> tuple[bool, str]:
    """Check the resource-intelligence-update gate (linked to execute)."""
    evidence_dir = assets_dir / "evidence"
    ri_update_path = evidence_dir / "resource-intelligence-update.yaml"

    if not ri_update_path.exists():
        return False, "missing resource-intelligence-update.yaml"

    data = _load_yaml(ri_update_path)
    if data is None:
        return False, "malformed resource-intelligence-update.yaml"

    additions = data.get("additions", [])
    rationale = data.get("no_additions_rationale", "")

    if not additions and not rationale:
        return False, "empty additions requires no_additions_rationale"

    if additions:
        return True, f"resource-intelligence-update OK: additions={len(additions)}"
    return True, f"resource-intelligence-update OK: no_additions_rationale provided"


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURE HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

_FULL_CONFIG = """\
schema_version: "1.0"
major_version: 1
activation: full
checker_timeout_seconds: 30
human_authority_allowlist:
  - user
  - vamsee
"""

_DISABLED_CONFIG = """\
schema_version: "1.0"
major_version: 1
activation: disabled
checker_timeout_seconds: 30
human_authority_allowlist:
  - user
"""


def _make_test_entry(
    name: str,
    scope: str = "integrated",
    result: str = "pass",
    artifact_ref: str | None = None,
) -> str:
    """Generate a single integrated_repo_tests entry as YAML text."""
    ref = artifact_ref or f".claude/work-queue/assets/WRK-999/{name}.txt"
    return (
        f"  - name: {name}\n"
        f"    scope: {scope}\n"
        f"    command: uv run --no-project pytest tests/unit/test_{name}.py\n"
        f"    result: {result}\n"
        f"    artifact_ref: {ref}\n"
    )


def _make_execute_evidence(
    wrk_id: str = "WRK-999",
    test_entries: list[str] | None = None,
    num_tests: int = 3,
) -> str:
    """Generate a complete execute.yaml evidence file."""
    if test_entries is None:
        test_entries = [
            _make_test_entry(f"test_{i}", scope="integrated" if i == 0 else "repo")
            for i in range(num_tests)
        ]
    tests_block = "".join(test_entries)
    return (
        f"wrk_id: {wrk_id}\n"
        f"stage: execute\n"
        f"integrated_repo_tests:\n"
        f"{tests_block}"
    )


def _write_execute_fixtures(
    tmp_path: Path,
    *,
    config: str = _FULL_CONFIG,
    evidence: str | None = None,
    include_evidence: bool = True,
    include_exemption: bool = False,
    exemption_approved_by: str = "user",
    num_tests: int = 3,
) -> tuple[Path, Path]:
    """Build minimal fixture tree for execute gate tests.

    Returns: (assets_dir, workspace_root)
    """
    workspace_root = tmp_path / "workspace"
    scripts_dir = workspace_root / "scripts" / "work-queue"
    scripts_dir.mkdir(parents=True)
    assets_dir = workspace_root / ".claude" / "work-queue" / "assets" / "WRK-999"
    evidence_dir = assets_dir / "evidence"
    evidence_dir.mkdir(parents=True)

    # Write config
    (scripts_dir / _EXECUTE_GATE_CONFIG_FILENAME).write_text(config, encoding="utf-8")

    # Write exemption if requested
    if include_exemption:
        (evidence_dir / _EXEMPTION_FILENAME).write_text(
            f"wrk_id: WRK-999\napproved_by: {exemption_approved_by}\napproval_scope: legacy\n",
            encoding="utf-8",
        )
    elif include_evidence:
        if evidence is None:
            evidence = _make_execute_evidence(num_tests=num_tests)
        (evidence_dir / _EXECUTE_EVIDENCE_FILENAME).write_text(evidence, encoding="utf-8")

    return assets_dir, workspace_root


# ═══════════════════════════════════════════════════════════════════════════════
# STANDARD GATE VARIATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════


def _skip_if_no_yaml():
    if yaml is None:
        pytest.skip("PyYAML unavailable in test environment")


class TestExecuteGateV1Disabled:
    """V1: activation=disabled → gate passes unconditionally."""

    def test_disabled_config_passes_without_evidence(self, tmp_path: Path):
        _skip_if_no_yaml()
        assets_dir, workspace_root = _write_execute_fixtures(
            tmp_path, config=_DISABLED_CONFIG, include_evidence=False,
        )
        ok, detail = check_execute_gate("WRK-999", assets_dir, workspace_root)
        assert ok is True
        assert "disabled" in detail.lower()


class TestExecuteGateV2ConfigMissing:
    """V2: missing config → infrastructure failure (None)."""

    def test_missing_config_returns_none(self, tmp_path: Path):
        _skip_if_no_yaml()
        assets_dir = tmp_path / ".claude" / "work-queue" / "assets" / "WRK-999"
        (assets_dir / "evidence").mkdir(parents=True)
        # No config file written — workspace_root is tmp_path itself
        ok, detail = check_execute_gate("WRK-999", assets_dir, tmp_path)
        assert ok is None
        assert "config" in detail.lower()

    def test_malformed_config_returns_none(self, tmp_path: Path):
        _skip_if_no_yaml()
        assets_dir, workspace_root = _write_execute_fixtures(
            tmp_path,
            config="activation: [invalid\n  yaml: {\n",
            include_evidence=False,
        )
        ok, detail = check_execute_gate("WRK-999", assets_dir, workspace_root)
        assert ok is None
        assert "malformed" in detail.lower() or "config" in detail.lower()


class TestExecuteGateV3MissingEvidence:
    """V3: missing execute.yaml → gate fails."""

    def test_missing_evidence_file_fails(self, tmp_path: Path):
        _skip_if_no_yaml()
        assets_dir, workspace_root = _write_execute_fixtures(
            tmp_path, include_evidence=False,
        )
        ok, detail = check_execute_gate("WRK-999", assets_dir, workspace_root)
        assert ok is False
        assert "missing" in detail.lower()
        assert _EXECUTE_EVIDENCE_FILENAME in detail


class TestExecuteGateV4HappyPath:
    """V4: all required fields present → gate passes."""

    def test_three_passing_tests_passes(self, tmp_path: Path):
        _skip_if_no_yaml()
        assets_dir, workspace_root = _write_execute_fixtures(
            tmp_path, num_tests=3,
        )
        ok, detail = check_execute_gate("WRK-999", assets_dir, workspace_root)
        assert ok is True
        assert "integrated_repo_tests=3" in detail

    def test_four_passing_tests_passes(self, tmp_path: Path):
        _skip_if_no_yaml()
        assets_dir, workspace_root = _write_execute_fixtures(
            tmp_path, num_tests=4,
        )
        ok, detail = check_execute_gate("WRK-999", assets_dir, workspace_root)
        assert ok is True
        assert "integrated_repo_tests=4" in detail


class TestExecuteGateV5BelowMinimum:
    """V5: integrated_repo_tests count below minimum → gate fails."""

    def test_two_tests_fails(self, tmp_path: Path):
        _skip_if_no_yaml()
        assets_dir, workspace_root = _write_execute_fixtures(
            tmp_path, num_tests=2,
        )
        ok, detail = check_execute_gate("WRK-999", assets_dir, workspace_root)
        assert ok is False
        assert "3-5" in detail

    def test_one_test_fails(self, tmp_path: Path):
        _skip_if_no_yaml()
        assets_dir, workspace_root = _write_execute_fixtures(
            tmp_path, num_tests=1,
        )
        ok, detail = check_execute_gate("WRK-999", assets_dir, workspace_root)
        assert ok is False
        assert "3-5" in detail

    def test_zero_tests_fails(self, tmp_path: Path):
        _skip_if_no_yaml()
        evidence = (
            "wrk_id: WRK-999\n"
            "stage: execute\n"
            "integrated_repo_tests: []\n"
        )
        assets_dir, workspace_root = _write_execute_fixtures(
            tmp_path, evidence=evidence,
        )
        ok, detail = check_execute_gate("WRK-999", assets_dir, workspace_root)
        assert ok is False
        assert "3-5" in detail


class TestExecuteGateV6AtMinimum:
    """V6: integrated_repo_tests count at minimum (3) → gate passes."""

    def test_exactly_three_tests_passes(self, tmp_path: Path):
        _skip_if_no_yaml()
        assets_dir, workspace_root = _write_execute_fixtures(
            tmp_path, num_tests=3,
        )
        ok, detail = check_execute_gate("WRK-999", assets_dir, workspace_root)
        assert ok is True
        assert "integrated_repo_tests=3" in detail


class TestExecuteGateV7AtMaximum:
    """V7: integrated_repo_tests count at maximum (5) → gate passes."""

    def test_exactly_five_tests_passes(self, tmp_path: Path):
        _skip_if_no_yaml()
        assets_dir, workspace_root = _write_execute_fixtures(
            tmp_path, num_tests=5,
        )
        ok, detail = check_execute_gate("WRK-999", assets_dir, workspace_root)
        assert ok is True
        assert "integrated_repo_tests=5" in detail


class TestExecuteGateV8AboveMaximum:
    """V8: integrated_repo_tests count above maximum → gate fails."""

    def test_six_tests_fails(self, tmp_path: Path):
        _skip_if_no_yaml()
        assets_dir, workspace_root = _write_execute_fixtures(
            tmp_path, num_tests=6,
        )
        ok, detail = check_execute_gate("WRK-999", assets_dir, workspace_root)
        assert ok is False
        assert "3-5" in detail


class TestExecuteGateV9FailingResult:
    """V9: test with failing result → gate fails."""

    def test_one_failing_test_fails_gate(self, tmp_path: Path):
        _skip_if_no_yaml()
        entries = [
            _make_test_entry("smoke_a", result="pass"),
            _make_test_entry("smoke_b", result="fail"),
            _make_test_entry("smoke_c", result="pass"),
        ]
        evidence = _make_execute_evidence(test_entries=entries)
        assets_dir, workspace_root = _write_execute_fixtures(
            tmp_path, evidence=evidence,
        )
        ok, detail = check_execute_gate("WRK-999", assets_dir, workspace_root)
        assert ok is False
        assert "smoke_b" in detail
        assert "fail" in detail.lower()

    def test_error_result_fails_gate(self, tmp_path: Path):
        _skip_if_no_yaml()
        entries = [
            _make_test_entry("smoke_a", result="pass"),
            _make_test_entry("smoke_b", result="error"),
            _make_test_entry("smoke_c", result="pass"),
        ]
        evidence = _make_execute_evidence(test_entries=entries)
        assets_dir, workspace_root = _write_execute_fixtures(
            tmp_path, evidence=evidence,
        )
        ok, detail = check_execute_gate("WRK-999", assets_dir, workspace_root)
        assert ok is False
        assert "smoke_b" in detail

    def test_all_accepted_result_synonyms_pass(self, tmp_path: Path):
        """'pass', 'passed', 'ok', 'success' are all valid passing results."""
        _skip_if_no_yaml()
        entries = [
            _make_test_entry("t1", result="pass"),
            _make_test_entry("t2", result="passed"),
            _make_test_entry("t3", result="ok"),
        ]
        evidence = _make_execute_evidence(test_entries=entries)
        assets_dir, workspace_root = _write_execute_fixtures(
            tmp_path, evidence=evidence,
        )
        ok, detail = check_execute_gate("WRK-999", assets_dir, workspace_root)
        assert ok is True


class TestExecuteGateV10MissingArtifactRef:
    """V10: missing artifact_ref on a test entry → gate fails."""

    def test_missing_artifact_ref_fails(self, tmp_path: Path):
        _skip_if_no_yaml()
        evidence_text = (
            "wrk_id: WRK-999\n"
            "stage: execute\n"
            "integrated_repo_tests:\n"
            "  - name: smoke_a\n"
            "    scope: integrated\n"
            "    command: uv run pytest tests/a.py\n"
            "    result: pass\n"
            "    artifact_ref: ref-a.txt\n"
            "  - name: smoke_b\n"
            "    scope: repo\n"
            "    command: uv run pytest tests/b.py\n"
            "    result: pass\n"
            "  - name: smoke_c\n"
            "    scope: repo\n"
            "    command: uv run pytest tests/c.py\n"
            "    result: pass\n"
            "    artifact_ref: ref-c.txt\n"
        )
        assets_dir, workspace_root = _write_execute_fixtures(
            tmp_path, evidence=evidence_text,
        )
        ok, detail = check_execute_gate("WRK-999", assets_dir, workspace_root)
        assert ok is False
        assert "artifact_ref" in detail
        assert "smoke_b" in detail


class TestExecuteGateV11NoEvidenceFile:
    """V11: execute.yaml missing entirely → gate fails."""

    def test_no_evidence_file_fails(self, tmp_path: Path):
        _skip_if_no_yaml()
        assets_dir, workspace_root = _write_execute_fixtures(
            tmp_path, include_evidence=False,
        )
        ok, detail = check_execute_gate("WRK-999", assets_dir, workspace_root)
        assert ok is False
        assert _EXECUTE_EVIDENCE_FILENAME in detail


class TestExecuteGateV12MalformedYAML:
    """V12: malformed YAML in execute.yaml → infrastructure failure."""

    def test_malformed_evidence_returns_none(self, tmp_path: Path):
        _skip_if_no_yaml()
        bad_yaml = "integrated_repo_tests: [invalid\n  yaml: {\n"
        assets_dir, workspace_root = _write_execute_fixtures(
            tmp_path, evidence=bad_yaml,
        )
        ok, detail = check_execute_gate("WRK-999", assets_dir, workspace_root)
        assert ok is None
        assert "malformed" in detail.lower()


class TestExecuteGateV13WrkIdMismatch:
    """V13: wrk_id mismatch between evidence and request → gate fails."""

    def test_wrk_id_mismatch_fails(self, tmp_path: Path):
        _skip_if_no_yaml()
        evidence = _make_execute_evidence(wrk_id="WRK-111", num_tests=3)
        assets_dir, workspace_root = _write_execute_fixtures(
            tmp_path, evidence=evidence,
        )
        ok, detail = check_execute_gate("WRK-999", assets_dir, workspace_root)
        assert ok is False
        assert "mismatch" in detail.lower()
        assert "WRK-111" in detail


class TestExecuteGateV14ExemptionHumanAuthority:
    """V14: migration exemption with human authority → gate passes."""

    def test_exemption_with_human_approved_by_passes(self, tmp_path: Path):
        _skip_if_no_yaml()
        assets_dir, workspace_root = _write_execute_fixtures(
            tmp_path,
            include_evidence=False,
            include_exemption=True,
            exemption_approved_by="user",
        )
        ok, detail = check_execute_gate("WRK-999", assets_dir, workspace_root)
        assert ok is True
        assert "exemption" in detail.lower()


class TestExecuteGateV15ExemptionAgentAuthority:
    """V15: migration exemption with agent authority → gate fails."""

    def test_exemption_with_agent_approved_by_fails(self, tmp_path: Path):
        _skip_if_no_yaml()
        assets_dir, workspace_root = _write_execute_fixtures(
            tmp_path,
            include_evidence=False,
            include_exemption=True,
            exemption_approved_by="claude",
        )
        ok, detail = check_execute_gate("WRK-999", assets_dir, workspace_root)
        assert ok is False
        assert "allowlist" in detail.lower() or "rejected" in detail.lower()


class TestExecuteGateV16ResourceIntelligenceUpdate:
    """V16: resource-intelligence-update gate variations (linked gate)."""

    def test_empty_additions_without_rationale_fails(self, tmp_path: Path):
        _skip_if_no_yaml()
        assets_dir = tmp_path / "assets" / "WRK-999"
        evidence_dir = assets_dir / "evidence"
        evidence_dir.mkdir(parents=True)
        (evidence_dir / "resource-intelligence-update.yaml").write_text(
            "additions: []\n", encoding="utf-8",
        )
        ok, detail = check_resource_intelligence_update_gate(assets_dir)
        assert ok is False
        assert "no_additions_rationale" in detail

    def test_additions_present_passes(self, tmp_path: Path):
        _skip_if_no_yaml()
        assets_dir = tmp_path / "assets" / "WRK-999"
        evidence_dir = assets_dir / "evidence"
        evidence_dir.mkdir(parents=True)
        (evidence_dir / "resource-intelligence-update.yaml").write_text(
            "additions:\n  - doc: new-standard.pdf\n    domain: structural\n",
            encoding="utf-8",
        )
        ok, detail = check_resource_intelligence_update_gate(assets_dir)
        assert ok is True
        assert "additions=1" in detail

    def test_rationale_without_additions_passes(self, tmp_path: Path):
        _skip_if_no_yaml()
        assets_dir = tmp_path / "assets" / "WRK-999"
        evidence_dir = assets_dir / "evidence"
        evidence_dir.mkdir(parents=True)
        (evidence_dir / "resource-intelligence-update.yaml").write_text(
            "additions: []\nno_additions_rationale: \"All resources were pre-loaded.\"\n",
            encoding="utf-8",
        )
        ok, detail = check_resource_intelligence_update_gate(assets_dir)
        assert ok is True
        assert "no_additions_rationale" in detail

    def test_missing_file_fails(self, tmp_path: Path):
        _skip_if_no_yaml()
        assets_dir = tmp_path / "assets" / "WRK-999"
        evidence_dir = assets_dir / "evidence"
        evidence_dir.mkdir(parents=True)
        ok, detail = check_resource_intelligence_update_gate(assets_dir)
        assert ok is False
        assert "missing" in detail.lower()


class TestExecuteGateV17EmptyTestList:
    """V17: empty integrated_repo_tests list → gate fails."""

    def test_empty_list_fails(self, tmp_path: Path):
        _skip_if_no_yaml()
        evidence = (
            "wrk_id: WRK-999\n"
            "stage: execute\n"
            "integrated_repo_tests: []\n"
        )
        assets_dir, workspace_root = _write_execute_fixtures(
            tmp_path, evidence=evidence,
        )
        ok, detail = check_execute_gate("WRK-999", assets_dir, workspace_root)
        assert ok is False
        assert "3-5" in detail


# ═══════════════════════════════════════════════════════════════════════════════
# BOUNDARY & EDGE CASE TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestExecuteGateBoundaryConditions:
    """Additional boundary tests for completeness."""

    def test_evidence_without_wrk_id_field_still_passes(self, tmp_path: Path):
        """If evidence omits wrk_id entirely, skip mismatch check."""
        _skip_if_no_yaml()
        evidence = (
            "stage: execute\n"
            "integrated_repo_tests:\n"
            + "".join(_make_test_entry(f"t{i}") for i in range(3))
        )
        assets_dir, workspace_root = _write_execute_fixtures(
            tmp_path, evidence=evidence,
        )
        ok, detail = check_execute_gate("WRK-999", assets_dir, workspace_root)
        assert ok is True

    def test_mixed_scopes_accepted(self, tmp_path: Path):
        """Tests with mixed scope values (integrated, repo) pass if count/result valid."""
        _skip_if_no_yaml()
        entries = [
            _make_test_entry("int_test", scope="integrated", result="pass"),
            _make_test_entry("repo_test_1", scope="repo", result="passed"),
            _make_test_entry("repo_test_2", scope="repo", result="ok"),
        ]
        evidence = _make_execute_evidence(test_entries=entries)
        assets_dir, workspace_root = _write_execute_fixtures(
            tmp_path, evidence=evidence,
        )
        ok, detail = check_execute_gate("WRK-999", assets_dir, workspace_root)
        assert ok is True
        assert "integrated_repo_tests=3" in detail

    def test_result_case_insensitive(self, tmp_path: Path):
        """Result comparison is case-insensitive: 'PASS', 'Pass' accepted."""
        _skip_if_no_yaml()
        entries = [
            _make_test_entry("t1", result="PASS"),
            _make_test_entry("t2", result="Pass"),
            _make_test_entry("t3", result="SUCCESS"),
        ]
        evidence = _make_execute_evidence(test_entries=entries)
        assets_dir, workspace_root = _write_execute_fixtures(
            tmp_path, evidence=evidence,
        )
        ok, detail = check_execute_gate("WRK-999", assets_dir, workspace_root)
        assert ok is True


# ═══════════════════════════════════════════════════════════════════════════════
# SABOTAGE TESTS — verify gate cannot be bypassed
# ═══════════════════════════════════════════════════════════════════════════════


class TestSabotageExecuteGate:
    """Deliberately attempt to bypass the execute gate."""

    def test_cannot_bypass_with_empty_name(self, tmp_path: Path):
        """Test entry with empty name should fail."""
        _skip_if_no_yaml()
        evidence = (
            "wrk_id: WRK-999\n"
            "stage: execute\n"
            "integrated_repo_tests:\n"
            "  - name: \"\"\n"
            "    scope: integrated\n"
            "    command: uv run pytest x.py\n"
            "    result: pass\n"
            "    artifact_ref: ref.txt\n"
            "  - name: test_b\n"
            "    scope: repo\n"
            "    command: uv run pytest b.py\n"
            "    result: pass\n"
            "    artifact_ref: ref-b.txt\n"
            "  - name: test_c\n"
            "    scope: repo\n"
            "    command: uv run pytest c.py\n"
            "    result: pass\n"
            "    artifact_ref: ref-c.txt\n"
        )
        assets_dir, workspace_root = _write_execute_fixtures(
            tmp_path, evidence=evidence,
        )
        ok, detail = check_execute_gate("WRK-999", assets_dir, workspace_root)
        assert ok is False
        assert "name" in detail.lower()

    def test_cannot_bypass_with_extra_tests_over_limit(self, tmp_path: Path):
        """Padding with 6 tests to exceed the 5-test maximum fails."""
        _skip_if_no_yaml()
        assets_dir, workspace_root = _write_execute_fixtures(
            tmp_path, num_tests=6,
        )
        ok, detail = check_execute_gate("WRK-999", assets_dir, workspace_root)
        assert ok is False
        assert "3-5" in detail

    def test_agent_exemption_rejected(self, tmp_path: Path):
        """Agent-authored exemption must be rejected."""
        _skip_if_no_yaml()
        assets_dir, workspace_root = _write_execute_fixtures(
            tmp_path,
            include_evidence=False,
            include_exemption=True,
            exemption_approved_by="codex",
        )
        ok, detail = check_execute_gate("WRK-999", assets_dir, workspace_root)
        assert ok is False
        assert "codex" in detail or "allowlist" in detail.lower()
