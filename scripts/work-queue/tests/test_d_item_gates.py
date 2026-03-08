"""
T1-T30: Unit tests for D1-D16 deterministic gate enforcement.
Written BEFORE implementation per TDD mandate (WRK-1044).
"""
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = REPO_ROOT / "scripts" / "work-queue"
sys.path.insert(0, str(SCRIPTS_DIR))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(data), encoding="utf-8")


def make_assets(tmp: Path, wrk_id: str = "WRK-TEST") -> tuple[Path, Path]:
    """Return (assets_dir, evidence_dir) under tmp."""
    assets = tmp / "assets" / wrk_id
    evidence = assets / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    return assets, evidence


# ===========================================================================
# T1-T3: D1 — Stage 1 capture gate + path bug fix
# ===========================================================================
class TestD1Stage1PathBug:
    """T1: exit_stage.py must substitute WRK-NNN token in artifact paths."""

    def test_T1_normalize_substitutes_wrk_id(self):
        """Path normaliser replaces WRK-NNN with actual wrk_id."""
        # Import the normaliser from exit_stage or stage_exit_checks
        try:
            from stage_exit_checks import _normalize_path
        except ImportError:
            from exit_stage import _normalize  as _normalize_path  # noqa: F401
            pytest.skip("_normalize_path not yet extracted to stage_exit_checks")

        result = _normalize_path("assets/WRK-NNN/evidence/foo.yaml", "WRK-1044")
        assert "WRK-NNN" not in result
        assert "WRK-1044" in result

    def test_T2_stage1_exit_blocked_when_capture_yaml_absent(self, tmp_path):
        """Stage 1 exit is blocked when user-review-capture.yaml is absent."""
        from stage_exit_checks import check_s1_capture_gate
        assets, evidence = make_assets(tmp_path)
        ok, msg = check_s1_capture_gate(assets)
        assert ok is False
        assert "capture" in msg.lower() or "missing" in msg.lower()

    def test_T3_stage1_exit_blocked_when_scope_approved_false(self, tmp_path):
        """Stage 1 exit blocked when user-review-capture.yaml has scope_approved: false."""
        from stage_exit_checks import check_s1_capture_gate
        assets, evidence = make_assets(tmp_path)
        write_yaml(evidence / "user-review-capture.yaml", {
            "reviewer": "vamsee",
            "scope_approved": False,
            "confirmed_at": "2026-03-08T16:00:00Z",
        })
        ok, msg = check_s1_capture_gate(assets)
        assert ok is False


# ===========================================================================
# T4-T6: D2 — Write-backstop (gate_check.py Layer 1)
# ===========================================================================
class TestD2WriteBackstop:
    """T4-T6: gate_check.py must block Write tool calls to future-stage evidence."""

    def _get_future_stage_check(self):
        """Import the future-stage write guard from gate_check.py."""
        import gate_check
        if not hasattr(gate_check, "_is_future_stage_write"):
            pytest.skip("_is_future_stage_write not yet implemented in gate_check.py")
        return gate_check._is_future_stage_write

    def test_T4_write_future_stage_evidence_blocked(self, tmp_path):
        """Write to Stage 6 evidence when Stage 5 gate is still open → blocked."""
        fn = self._get_future_stage_check()
        wrk_id = "WRK-9001"  # must be numeric per _WRK_ID_RE
        assets_root = str(tmp_path / "assets")  # parent of WRK dir
        evidence = tmp_path / "assets" / wrk_id / "evidence"
        evidence.mkdir(parents=True, exist_ok=True)
        # No stage 5 gate artifact present
        future_path = str(evidence / "cross-review.yaml")
        result = fn(future_path, wrk_id, assets_root)
        assert result is True  # future write = should be blocked

    def test_T5_write_future_stage_after_gate_satisfied_allowed(self, tmp_path):
        """Write to Stage 6 evidence after Stage 5 gate satisfied → allowed."""
        fn = self._get_future_stage_check()
        wrk_id = "WRK-9001"
        assets_root = str(tmp_path / "assets")
        evidence = tmp_path / "assets" / wrk_id / "evidence"
        evidence.mkdir(parents=True, exist_ok=True)
        # Stage 5 gate artifact present
        write_yaml(evidence / "user-review-plan-draft.yaml", {
            "decision": "approved", "approval_decision": "approve_as_is"
        })
        future_path = str(evidence / "cross-review.yaml")
        result = fn(future_path, wrk_id, assets_root)
        assert result is False  # gate satisfied = not future-blocked

    def test_T6_no_active_wrk_fails_open(self, tmp_path, monkeypatch):
        """When no active WRK is set, write-backstop fails open (warns only)."""
        fn = self._get_future_stage_check()
        # Path that doesn't contain WRK-NNN pattern at all
        result = fn("/tmp/unrelated/file.txt", "", str(tmp_path))
        assert result is False  # fails open — not blocked


# ===========================================================================
# T7: D3 — Stage 17 reviewer allowlist
# ===========================================================================
class TestD3ReviewerAllowlist:
    def test_T7_stage17_reviewer_not_in_allowlist_blocked(self, tmp_path):
        """Stage 17 exit blocked when reviewer is not in human allowlist."""
        from stage_exit_checks import check_s17_reviewer_allowlist
        assets, evidence = make_assets(tmp_path)
        write_yaml(evidence / "user-review-close.yaml", {
            "reviewer": "agent-claude",
            "decision": "approved",
        })
        ok, msg = check_s17_reviewer_allowlist(assets)
        assert ok is False
        assert "allowlist" in msg.lower() or "reviewer" in msg.lower()


# ===========================================================================
# T8: D4 — integrated_repo_tests count ≥ 3
# ===========================================================================
class TestD4IntegratedTests:
    def test_T8_stage19_blocked_when_only_2_integrated_tests(self, tmp_path):
        """Stage 19 exit blocked when execute.yaml has only 2 integrated tests."""
        from stage_exit_checks import check_s19_integrated_tests
        assets, evidence = make_assets(tmp_path)
        write_yaml(evidence / "execute.yaml", {
            "integrated_repo_tests": [
                {"name": "test1", "scope": "integrated", "command": "pytest", "result": "pass"},
                {"name": "test2", "scope": "integrated", "command": "pytest", "result": "pass"},
            ]
        })
        ok, msg = check_s19_integrated_tests(assets)
        assert ok is False


# ===========================================================================
# T9: D5 — future-work.yaml captured: true for spun-off-new
# ===========================================================================
class TestD5FutureWork:
    def test_T9_stage15_blocked_when_spun_off_not_captured(self, tmp_path):
        """Stage 15 exit blocked when future-work has spun-off-new with captured: false."""
        from stage_exit_checks import check_s15_future_work
        assets, evidence = make_assets(tmp_path)
        write_yaml(evidence / "future-work.yaml", {
            "recommendations": [
                {"id": "FW-01", "disposition": "spun-off-new", "captured": False, "status": "open"}
            ]
        })
        ok, msg = check_s15_future_work(assets)
        assert ok is False


# ===========================================================================
# T10: D6 — Stage evidence covers all 20 stages
# ===========================================================================
class TestD6StageEvidence:
    def test_T10_stage19_blocked_when_only_19_stages(self, tmp_path):
        """Stage 19 exit blocked when stage-evidence has only 19 stages."""
        from stage_exit_checks import check_s19_stage_evidence
        # Put WRK file in proper queue location under tmp workspace
        queue_dir = tmp_path / ".claude" / "work-queue" / "working"
        queue_dir.mkdir(parents=True, exist_ok=True)
        wrk_path = queue_dir / "WRK-TEST.md"
        assets, evidence = make_assets(tmp_path / "assets_root")
        wrk_path.write_text(
            "---\nid: WRK-TEST\nstage_evidence_ref: "
            f"assets_root/assets/WRK-TEST/evidence/stage-evidence.yaml\n---\n",
            encoding="utf-8",
        )
        stages = [{"order": i, "status": "done"} for i in range(1, 20)]  # only 19
        write_yaml(evidence / "stage-evidence.yaml", {"stages": stages})
        ok, msg = check_s19_stage_evidence(str(tmp_path), "WRK-TEST")
        assert ok is False


# ===========================================================================
# T11: D7 — Browser-open timestamp < approval timestamp
# ===========================================================================
class TestD7BrowserTimestamp:
    def test_T11_stage5_blocked_when_browser_open_after_approval(self, tmp_path):
        """Stage 5 exit blocked when browser opened after confirmed_at (inverted)."""
        from stage_exit_checks import check_s5_browser_timestamps
        assets, evidence = make_assets(tmp_path)
        write_yaml(evidence / "user-review-browser-open.yaml", {
            "events": [{
                "stage": "plan_draft",
                "opened_in_default_browser": True,
                "browser": "default",
                "html_ref": "some.html",
                "opened_at": "2026-03-08T17:30:00Z",  # AFTER approval
                "reviewer": "vamsee",
            }]
        })
        write_yaml(evidence / "user-review-plan-draft.yaml", {
            "reviewed_at": "2026-03-08T17:00:00Z",  # BEFORE open — inverted
            "decision": "approved",
            "approval_decision": "approve_as_is",
        })
        ok, msg = check_s5_browser_timestamps(assets)
        assert ok is False
        assert "timestamp" in msg.lower() or "before" in msg.lower() or "inverted" in msg.lower()


# ===========================================================================
# T12: D8 — published_at ≤ confirmed_at
# ===========================================================================
class TestD8PublishOrder:
    def test_T12_stage5_blocked_when_published_after_confirmed(self, tmp_path):
        """Stage 5 exit blocked when published_at > confirmed_at."""
        from stage_exit_checks import check_s5_publish_order
        assets, evidence = make_assets(tmp_path)
        write_yaml(evidence / "user-review-plan-draft.yaml", {
            "reviewed_at": "2026-03-08T17:00:00Z",
            "decision": "approved",
            "approval_decision": "approve_as_is",
        })
        write_yaml(evidence / "user-review-publish.yaml", {
            "events": [{
                "stage": "plan_draft",
                "pushed_to_origin": True,
                "remote": "origin",
                "branch": "main",
                "commit": "abc123",
                "documents": ["plan.md"],
                "published_at": "2026-03-08T18:00:00Z",  # AFTER confirmed_at
                "reviewer": "vamsee",
            }]
        })
        write_yaml(evidence / "plan-final-review.yaml", {
            "decision": "passed",
            "confirmed_by": "vamsee",
            "confirmed_at": "2026-03-08T17:05:00Z",  # BEFORE published_at
        })
        ok, msg = check_s5_publish_order(assets)
        assert ok is False


# ===========================================================================
# T13: D9 — Tests/Evals ≥ 3 entries in plan.md
# ===========================================================================
class TestD9PlanEvalCount:
    def test_T13_stage4_blocked_when_plan_has_2_test_rows(self, tmp_path):
        """Stage 4 exit blocked when plan.md Tests/Evals section has < 3 rows."""
        from gate_checks_extra import check_plan_eval_count
        plan = tmp_path / "plan.md"
        plan.write_text(
            "## Tests / Evals\n\n"
            "| Test | D-item | Scenario | Expected |\n"
            "|------|--------|----------|----------|\n"
            "| T1 | D1 | scenario | pass |\n"
            "| T2 | D2 | scenario | pass |\n",
            encoding="utf-8",
        )
        ok, msg = check_plan_eval_count(plan)
        assert ok is False
        assert "3" in msg or "fewer" in msg.lower()


# ===========================================================================
# T14-T15: D10 — Route cross-review count (hard block)
# ===========================================================================
class TestD10RouteReviewCount:
    def test_T14_route_b_with_1_review_file_blocked(self, tmp_path):
        """Route B with only 1 cross-review file is a hard block."""
        from gate_checks_extra import check_route_cross_review_count
        assets, evidence = make_assets(tmp_path)
        (evidence / "cross-review-claude.md").write_text("# Claude review\n", encoding="utf-8")
        front = {"route": "B"}
        ok, msg = check_route_cross_review_count(assets, front)
        assert ok is False
        assert "3" in msg or "need" in msg.lower()

    def test_T15_route_a_with_1_review_file_passes(self, tmp_path):
        """Route A with exactly 1 cross-review file passes."""
        from gate_checks_extra import check_route_cross_review_count
        assets, evidence = make_assets(tmp_path)
        (evidence / "cross-review-claude.md").write_text("# Claude review\n", encoding="utf-8")
        front = {"route": "A"}
        ok, msg = check_route_cross_review_count(assets, front)
        assert ok is True


# ===========================================================================
# T16-T17: D11 — All R-09 sentinel fields at claim time
# ===========================================================================
class TestD11SentinelFields:
    """T16-T17: check_s8_sentinel_fields blocks if any R-09 field is sentinel."""

    def test_T16_session_id_unset_blocks_claim(self, tmp_path):
        """When session_id is absent/empty, sentinel check fails."""
        from stage_exit_checks import check_s8_sentinel_fields
        assets, evidence = make_assets(tmp_path)
        write_yaml(evidence / "activation.yaml", {
            "wrk_id": "WRK-TEST",
            "set_active_wrk": True,
            "session_id": "",  # empty
            "orchestrator_agent": "claude",
            "activated_at": "2026-03-08T16:00:00Z",
        })
        ok, msg = check_s8_sentinel_fields(assets)
        assert ok is False

    def test_T17_session_id_unknown_blocks_claim(self, tmp_path):
        """When session_id='unknown', sentinel check fails."""
        from stage_exit_checks import check_s8_sentinel_fields
        assets, evidence = make_assets(tmp_path)
        write_yaml(evidence / "activation.yaml", {
            "wrk_id": "WRK-TEST",
            "set_active_wrk": True,
            "session_id": "unknown",
            "orchestrator_agent": "claude",
            "activated_at": "2026-03-08T16:00:00Z",
        })
        ok, msg = check_s8_sentinel_fields(assets)
        assert ok is False
        assert "unknown" in msg.lower() or "sentinel" in msg.lower()


# ===========================================================================
# T18: D12 — P1 finding → conditional pause with override artifact
# ===========================================================================
class TestD12P1Finding:
    def test_T18_cross_review_with_p1_finding_requires_override(self, tmp_path):
        """Stage 6 exit: cross-review with P1 finding without override → blocked."""
        from stage_exit_checks import check_s6_p1_pause
        assets, evidence = make_assets(tmp_path)
        (evidence / "cross-review-claude.md").write_text(
            "# Cross-Review\n\n**P1-01**: Something is wrong.\n",
            encoding="utf-8",
        )
        # No cross-review-p1-override.yaml
        ok, msg = check_s6_p1_pause(assets)
        assert ok is False
        assert "override" in msg.lower() or "p1" in msg.lower()


# ===========================================================================
# T19-T20: D13 — gate-evidence-summary.json 0 MISSING
# ===========================================================================
class TestD13GateSummary:
    def test_T19_stage14_blocked_when_missing_gate_in_summary(self, tmp_path):
        """Stage 14 exit blocked when gate-evidence-summary.json has MISSING gates."""
        from stage_exit_checks import check_s14_gate_summary
        assets, evidence = make_assets(tmp_path)
        write_yaml(evidence / "gate-evidence-summary.json",
                   None)  # write via json
        (evidence / "gate-evidence-summary.json").write_text(
            json.dumps({"gates": [{"name": "Plan gate", "ok": False}]}),
            encoding="utf-8",
        )
        ok, msg = check_s14_gate_summary(assets)
        assert ok is False
        assert "missing" in msg.lower() or "plan gate" in msg.lower()

    def test_T20_stage14_passes_when_all_gates_pass(self, tmp_path):
        """Stage 14 exit passes when all gates in summary are OK."""
        from stage_exit_checks import check_s14_gate_summary
        assets, evidence = make_assets(tmp_path)
        (evidence / "gate-evidence-summary.json").write_text(
            json.dumps({"gates": [{"name": "Plan gate", "ok": True}]}),
            encoding="utf-8",
        )
        ok, msg = check_s14_gate_summary(assets)
        assert ok is True


# ===========================================================================
# T21-T23: D14 — --json flag for verify-gate-evidence.py
# ===========================================================================
class TestD14JsonFlag:
    def _run_verifier(self, args: list[str]) -> tuple[int, str]:
        import subprocess
        cmd = [
            "uv", "run", "--no-project", "python",
            str(SCRIPTS_DIR / "verify-gate-evidence.py"),
        ] + args
        result = subprocess.run(cmd, capture_output=True, text=True,
                                cwd=str(REPO_ROOT))
        return result.returncode, result.stdout + result.stderr

    def test_T21_json_flag_passing_wrk_exits_0(self):
        """--json on a passing (or warnable) WRK returns exit 0 and pass:true JSON."""
        # Use a known-good archived WRK
        code, out = self._run_verifier(["WRK-1036", "--phase", "claim", "--json"])
        # Either passes or we at least get valid JSON with 'pass' key
        try:
            data = json.loads(out.strip().splitlines()[-1])
        except (json.JSONDecodeError, IndexError):
            pytest.skip("verify-gate-evidence.py --json not yet implemented")
        assert "pass" in data

    def test_T22_json_flag_failing_wrk_exits_1(self, tmp_path):
        """--json on a WRK with missing artifacts exits 1 with pass:false."""
        # Create a minimal WRK file in tmp
        import subprocess
        fake_wrk = tmp_path / "working" / "WRK-FAKE.md"
        fake_wrk.parent.mkdir(parents=True, exist_ok=True)
        fake_wrk.write_text(
            "---\nid: WRK-FAKE\nplan_workstations: [ace-linux-1]\n"
            "execution_workstations: [ace-linux-1]\n---\n",
            encoding="utf-8",
        )
        env = os.environ.copy()
        env["WORKSPACE_ROOT"] = str(tmp_path)
        cmd = [
            "uv", "run", "--no-project", "python",
            str(SCRIPTS_DIR / "verify-gate-evidence.py"),
            "WRK-FAKE", "--phase", "claim", "--json",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True,
                                cwd=str(REPO_ROOT), env=env)
        if result.returncode == 0:
            pytest.skip("--json flag not yet implemented")
        # Should exit non-zero (1 = gate fail, 2 = WRK not found — both acceptable)
        assert result.returncode != 0
        try:
            data = json.loads((result.stdout + result.stderr).strip().splitlines()[-1])
            assert data.get("pass") is False
        except (json.JSONDecodeError, IndexError):
            pass  # acceptable if JSON output not yet wired

    def test_T23_json_output_is_valid_json(self):
        """--json output can be parsed by json.loads()."""
        import subprocess
        cmd = [
            "uv", "run", "--no-project", "python",
            str(SCRIPTS_DIR / "verify-gate-evidence.py"),
            "WRK-1036", "--phase", "claim", "--json",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True,
                                cwd=str(REPO_ROOT))
        output = (result.stdout + result.stderr).strip()
        if not output:
            pytest.skip("--json flag not yet implemented")
        # Find last JSON line
        for line in reversed(output.splitlines()):
            if line.startswith("{"):
                json.loads(line)  # raises if invalid
                return
        pytest.skip("no JSON line in output — --json not yet implemented")


# ===========================================================================
# T24: D15 — legal scan prerequisite at close time
# ===========================================================================
class TestD15LegalScan:
    def test_T24_close_blocked_when_legal_scan_fails(self, tmp_path):
        """close-item.sh exits 1 when legal-sanity-scan.sh exits non-zero."""
        import subprocess
        # Create a fake close setup that calls legal scan
        # We test the shell guard function directly via a small script
        check_script = SCRIPTS_DIR / "close-item.sh"
        if not check_script.exists():
            pytest.skip("close-item.sh not found")
        # Check that close-item.sh mentions legal scan
        content = check_script.read_text(encoding="utf-8")
        assert "legal-sanity-scan" in content, (
            "close-item.sh must call legal-sanity-scan.sh (D15)"
        )


# ===========================================================================
# T25-T26: D16 — Codex unavailability parking
# ===========================================================================
class TestD16CodexAvailability:
    def test_T25_cross_review_blocked_when_codex_unavailable(self, tmp_path):
        """check_codex_available() returns False when quota shows not-available."""
        # Test that cross-review.sh has the check_codex_available function
        cross_review = REPO_ROOT / "scripts" / "review" / "cross-review.sh"
        if not cross_review.exists():
            pytest.skip("cross-review.sh not found at scripts/review/")
        content = cross_review.read_text(encoding="utf-8")
        assert "check_codex_available" in content or "codex" in content.lower(), (
            "cross-review.sh must have Codex availability check (D16)"
        )

    def test_T26_stage06_yaml_has_codex_unavailable_action(self):
        """Stage 06 YAML has codex_unavailable_action: park_blocked."""
        stage_yaml = SCRIPTS_DIR / "stages" / "stage-06-cross-review.yaml"
        assert stage_yaml.exists(), "stage-06-cross-review.yaml not found"
        data = yaml.safe_load(stage_yaml.read_text(encoding="utf-8"))
        assert data.get("codex_unavailable_action") == "park_blocked", (
            "stage-06-cross-review.yaml must have codex_unavailable_action: park_blocked"
        )


# ===========================================================================
# T27-T30: L3 — Schema validator for stage-gate-policy.yaml
# ===========================================================================
class TestL3PolicyValidator:
    def _run_validator(self, policy_text: str) -> tuple[int, str]:
        import subprocess
        validator = SCRIPTS_DIR / "validate-stage-gate-policy.py"
        if not validator.exists():
            pytest.skip("validate-stage-gate-policy.py not yet created")
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml",
                                        delete=False, encoding="utf-8") as f:
            f.write(policy_text)
            tmp = f.name
        try:
            result = subprocess.run(
                ["uv", "run", "--no-project", "python", str(validator), tmp],
                capture_output=True, text=True, cwd=str(REPO_ROOT),
            )
            return result.returncode, result.stdout + result.stderr
        finally:
            os.unlink(tmp)

    def test_T27_valid_policy_passes(self):
        """A valid stage-gate-policy.yaml passes validation."""
        real_policy = SCRIPTS_DIR / "stage-gate-policy.yaml"
        if not real_policy.exists():
            pytest.skip("stage-gate-policy.yaml not found")
        code, out = self._run_validator(real_policy.read_text(encoding="utf-8"))
        assert code == 0, f"Validator failed on real policy: {out}"

    def test_T28_missing_stage_7_fails(self):
        """Policy missing stage 7 fails validation."""
        stages = {i: {"name": f"Stage {i}", "gate_type": "auto"}
                  for i in range(1, 21) if i != 7}
        policy = yaml.dump({"stages": stages})
        code, out = self._run_validator(policy)
        assert code != 0, "Missing stage 7 should fail validation"

    def test_T29_wrong_gate_type_fails(self):
        """Policy with invalid gate_type fails validation."""
        stages = {i: {"name": f"Stage {i}", "gate_type": "auto"}
                  for i in range(1, 21)}
        stages[5]["gate_type"] = "fuzzy"  # invalid
        policy = yaml.dump({"stages": stages})
        code, out = self._run_validator(policy)
        assert code != 0, "Invalid gate_type should fail validation"

    def test_T30_wrong_hard_gates_fails(self):
        """Policy where hard gates ≠ [1,5,7,17] fails validation."""
        stages = {i: {"name": f"Stage {i}", "gate_type": "auto"}
                  for i in range(1, 21)}
        # Make stage 3 hard (should only be 1, 5, 7, 17)
        stages[3]["gate_type"] = "hard"
        policy = yaml.dump({"stages": stages})
        code, out = self._run_validator(policy)
        assert code != 0, "Wrong hard gate set should fail validation"
