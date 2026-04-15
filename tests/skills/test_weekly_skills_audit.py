"""Tests for the deterministic weekly skills audit (#2281).

Covers: inventory scope, classification buckets, output schema,
stable finding keys, baseline delta, waiver handling, read-only behavior.
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Helpers — build fixture skill trees in tmp_path
# ---------------------------------------------------------------------------

def _write_skill(base: Path, rel_path: str, name: str, *, content: str = "") -> Path:
    """Create a SKILL.md with frontmatter at base/rel_path/SKILL.md."""
    d = base / rel_path
    d.mkdir(parents=True, exist_ok=True)
    skill_md = d / "SKILL.md"
    text = f"---\nname: {name}\ndescription: test skill\n---\n{content}"
    skill_md.write_text(text, encoding="utf-8")
    return skill_md


def _write_skill_no_frontmatter(base: Path, rel_path: str) -> Path:
    """Create a SKILL.md with no valid frontmatter."""
    d = base / rel_path
    d.mkdir(parents=True, exist_ok=True)
    skill_md = d / "SKILL.md"
    skill_md.write_text("This skill has no frontmatter at all.\n", encoding="utf-8")
    return skill_md


def _write_skill_malformed_frontmatter(base: Path, rel_path: str) -> Path:
    """Create a SKILL.md with malformed YAML frontmatter."""
    d = base / rel_path
    d.mkdir(parents=True, exist_ok=True)
    skill_md = d / "SKILL.md"
    skill_md.write_text("---\nname: [invalid yaml\n---\n", encoding="utf-8")
    return skill_md


def _write_waiver(path: Path, waivers: list[dict]) -> None:
    """Write a waiver registry YAML file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    yaml.dump({"waivers": waivers}, path.open("w"), default_flow_style=False)


def _import_audit():
    """Import the weekly_skills_audit module."""
    audit_path = REPO_ROOT / "scripts" / "skills" / "weekly_skills_audit.py"
    import importlib.util
    spec = importlib.util.spec_from_file_location("weekly_skills_audit", audit_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["weekly_skills_audit"] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Tests: Inventory scope
# ---------------------------------------------------------------------------

class TestInventoryScope:
    """Verify skill discovery, exclusion, and canonical identity rules."""

    def test_excludes_archive_and_diverged(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "workspace-hub/good-skill", "good-skill")
        _write_skill(skills_dir, "_archive/old-skill", "old-skill")
        _write_skill(skills_dir, "_diverged/fork-skill", "fork-skill")

        audit = _import_audit()
        inventory = audit.build_inventory(skills_dir)

        names = {s["canonical_name"] for s in inventory}
        assert "good-skill" in names
        assert "old-skill" not in names
        assert "fork-skill" not in names

    def test_treats_frontmatter_name_as_canonical(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "area/competitive-analysis", "marketing-competitive-analysis")

        audit = _import_audit()
        inventory = audit.build_inventory(skills_dir)

        assert len(inventory) == 1
        assert inventory[0]["canonical_name"] == "marketing-competitive-analysis"

    def test_handles_missing_frontmatter(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "area/normal", "normal-skill")
        _write_skill_no_frontmatter(skills_dir, "area/broken")

        audit = _import_audit()
        result = audit.run_audit(
            skills_dir=skills_dir,
            output_dir=tmp_path / "out",
            policy_path=REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml",
        )

        # Should complete without crashing; broken skill reported in errors
        assert result["errors"] or any(
            "broken" in str(s.get("paths", []))
            for s in result["findings"]
        )

    def test_handles_malformed_frontmatter(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "area/normal", "normal-skill")
        _write_skill_malformed_frontmatter(skills_dir, "area/malformed")

        audit = _import_audit()
        result = audit.run_audit(
            skills_dir=skills_dir,
            output_dir=tmp_path / "out",
            policy_path=REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml",
        )

        assert result is not None
        # Malformed frontmatter must appear in errors, not crash the run
        assert any("malformed" in str(e).lower() or "malformed" in str(e)
                    for e in result["errors"])


# ---------------------------------------------------------------------------
# Tests: Classification buckets
# ---------------------------------------------------------------------------

class TestClassification:
    """Verify findings are placed in the correct policy buckets."""

    def test_reports_duplicate_frontmatter_names_separately_from_leaf_collisions(
        self, tmp_path: Path
    ) -> None:
        skills_dir = tmp_path / "skills"
        # Same canonical name = duplicate frontmatter name
        _write_skill(skills_dir, "area-a/dup", "my-skill")
        _write_skill(skills_dir, "area-b/dup2", "my-skill")
        # Same leaf directory name, different canonical names = generic leaf collision
        _write_skill(skills_dir, "domain-x/analysis", "x-skill")
        _write_skill(skills_dir, "domain-y/analysis", "y-skill")

        audit = _import_audit()
        result = audit.run_audit(
            skills_dir=skills_dir,
            output_dir=tmp_path / "out",
            policy_path=REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml",
        )

        classifications = {f["classification"] for f in result["findings"]}
        # Must have at least exact-duplicate and generic-leaf-collision
        assert "exact-duplicate" in classifications
        assert "generic-leaf-collision" in classifications

    def test_buckets_internal_and_core_findings_separately(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "_core/group/core-a", "shared-core")
        _write_skill(skills_dir, "_core/group/core-b", "shared-core")
        _write_skill(skills_dir, "_internal/group/internal-a", "shared-internal")
        _write_skill(skills_dir, "_internal/group/internal-b", "shared-internal")
        _write_skill(skills_dir, "workspace-hub/regular", "regular")

        audit = _import_audit()
        result = audit.run_audit(
            skills_dir=skills_dir,
            output_dir=tmp_path / "out",
            policy_path=REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml",
        )

        active_names = {name for finding in result["findings"] for name in finding.get("canonical_names", [])}
        suppressed_names = {name for finding in result["suppressed_findings"] for name in finding.get("canonical_names", [])}

        assert "shared-core" not in active_names
        assert "shared-internal" not in active_names
        assert "shared-core" in suppressed_names
        assert "shared-internal" in suppressed_names

    def test_classifies_known_wrapper_pair(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        # Canonical skill
        _write_skill(skills_dir, "tools/main-tool", "main-tool",
                      content="Full implementation of main-tool workflow.\n")
        # Wrapper/stub pointing to canonical
        d = skills_dir / "shortcuts" / "main-tool-alias"
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(
            "---\nname: main-tool-alias\ndescription: Wrapper for main-tool\n"
            "canonical_target: main-tool\ntype: wrapper\n---\n"
            "This is a thin redirect to main-tool.\n",
            encoding="utf-8",
        )

        audit = _import_audit()
        result = audit.run_audit(
            skills_dir=skills_dir,
            output_dir=tmp_path / "out",
            policy_path=REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml",
        )

        wrapper_findings = [
            f for f in result["findings"]
            if f["classification"] == "canonical-wrapper-pair"
        ]
        assert len(wrapper_findings) >= 1

    def test_classifies_adjacent_specialization(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "engineering/cfd/analysis", "openfoam-analysis",
                      content="OpenFOAM mesh and solver analysis.\n")
        _write_skill(skills_dir, "engineering/marine/analysis", "orcawave-analysis",
                      content="OrcaWave diffraction analysis.\n")

        audit = _import_audit()
        result = audit.run_audit(
            skills_dir=skills_dir,
            output_dir=tmp_path / "out",
            policy_path=REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml",
        )

        # These share "analysis" leaf but are distinct specializations
        leaf_findings = [
            f for f in result["findings"]
            if set(f.get("canonical_names", [])) & {"openfoam-analysis", "orcawave-analysis"}
        ]
        assert leaf_findings, "Expected a finding for the analysis pair"
        for f in leaf_findings:
            assert f["classification"] == "adjacent-specialization"


# ---------------------------------------------------------------------------
# Tests: Output schema and artifact contract
# ---------------------------------------------------------------------------

class TestOutputContract:
    """Verify JSON + Markdown artifacts match the plan's required schema."""

    def test_audit_scope_is_stable_for_repo_skills_path(self, tmp_path: Path) -> None:
        audit = _import_audit()
        worktree_like = tmp_path / "some-worktree" / ".claude" / "skills"
        worktree_like.mkdir(parents=True)
        assert audit._derive_audit_scope(worktree_like) == "skills-dir:.claude/skills"

    def test_outputs_json_schema_and_markdown_summary(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "area/skill-a", "skill-a")
        _write_skill(skills_dir, "area/skill-b", "skill-b")

        out_dir = tmp_path / "out" / "logs" / "maintenance" / "skills-curation"

        audit = _import_audit()
        result = audit.run_audit(
            skills_dir=skills_dir,
            output_dir=tmp_path / "out",
            policy_path=REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml",
        )

        # JSON artifact must exist
        json_files = list(out_dir.glob("*.json"))
        assert len(json_files) == 1, f"Expected 1 JSON artifact, got {json_files}"

        data = json.loads(json_files[0].read_text())
        required_keys = {
            "generated_at", "policy_version", "audit_scope", "baseline_artifact",
            "summary_counts", "findings", "suppressed_findings", "errors",
        }
        missing = required_keys - set(data)
        assert not missing, f"JSON missing required keys: {missing}"

        # Markdown artifact must exist
        md_files = list(out_dir.glob("*.md"))
        assert len(md_files) == 1, f"Expected 1 Markdown artifact, got {md_files}"

        md_text = md_files[0].read_text()
        for section in [
            "New Findings", "Changed Findings", "Unresolved High-Confidence",
            "Suppressed", "Operational Errors",
        ]:
            assert section.lower() in md_text.lower(), f"Missing section: {section}"

    def test_finding_entries_have_required_fields(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "area-a/dup", "my-dup-skill")
        _write_skill(skills_dir, "area-b/dup2", "my-dup-skill")

        audit = _import_audit()
        result = audit.run_audit(
            skills_dir=skills_dir,
            output_dir=tmp_path / "out",
            policy_path=REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml",
        )

        required_fields = {
            "finding_key", "classification", "severity", "confidence",
            "canonical_names", "paths", "summary", "recommended_action",
            "is_new", "is_changed",
        }
        for finding in result["findings"]:
            missing = required_fields - set(finding)
            assert not missing, f"Finding missing fields: {missing}"


# ---------------------------------------------------------------------------
# Tests: Stable finding keys and baseline comparison
# ---------------------------------------------------------------------------

class TestBaselineDelta:
    """Verify stable keys and delta semantics across runs."""

    def test_computes_stable_finding_keys_across_unchanged_runs(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "area-a/dup", "my-skill")
        _write_skill(skills_dir, "area-b/dup2", "my-skill")

        out_dir = tmp_path / "out"
        policy_path = REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml"

        audit = _import_audit()

        # First run
        r1 = audit.run_audit(
            skills_dir=skills_dir, output_dir=out_dir, policy_path=policy_path,
        )
        keys_1 = {f["finding_key"] for f in r1["findings"]}

        # Second run — same inputs
        r2 = audit.run_audit(
            skills_dir=skills_dir, output_dir=out_dir, policy_path=policy_path,
        )
        keys_2 = {f["finding_key"] for f in r2["findings"]}

        assert keys_1 == keys_2, "Finding keys must be stable across unchanged runs"

        # On second run, findings should not be marked as new
        for f in r2["findings"]:
            if f["finding_key"] in keys_1:
                assert f["is_new"] is False, (
                    f"Finding {f['finding_key']} should not be new on second run"
                )

    def test_handles_first_run_without_baseline(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "area-a/dup", "my-skill")
        _write_skill(skills_dir, "area-b/dup2", "my-skill")

        audit = _import_audit()
        result = audit.run_audit(
            skills_dir=skills_dir,
            output_dir=tmp_path / "out",
            policy_path=REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml",
        )

        assert result["baseline_artifact"] is None
        for f in result["findings"]:
            assert f["is_new"] is True

    def test_ignores_incompatible_baseline_versions(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "area-a/dup", "my-skill")
        _write_skill(skills_dir, "area-b/dup2", "my-skill")

        out_dir = tmp_path / "out"
        artifact_dir = out_dir / "logs" / "maintenance" / "skills-curation"
        artifact_dir.mkdir(parents=True)

        # Write a fake prior baseline with incompatible version
        prior = {
            "generated_at": "2026-01-01T00:00:00",
            "policy_version": "incompatible-v99",
            "audit_scope": "different",
            "findings": [{"finding_key": "old-key"}],
        }
        (artifact_dir / "2026-01-01.json").write_text(
            json.dumps(prior), encoding="utf-8"
        )

        audit = _import_audit()
        result = audit.run_audit(
            skills_dir=skills_dir,
            output_dir=out_dir,
            policy_path=REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml",
        )

        # Should succeed; incompatible baseline treated as absent
        assert result is not None
        for f in result["findings"]:
            assert f["is_new"] is True

    def test_ignores_incompatible_baseline_scope(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "area-a/dup", "my-skill")
        _write_skill(skills_dir, "area-b/dup2", "my-skill")

        out_dir = tmp_path / "out"
        artifact_dir = out_dir / "logs" / "maintenance" / "skills-curation"
        artifact_dir.mkdir(parents=True)

        audit = _import_audit()
        first = audit.run_audit(
            skills_dir=skills_dir,
            output_dir=out_dir,
            policy_path=REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml",
        )
        first_path = artifact_dir / f"{date.today().isoformat()}.json"
        prior = json.loads(first_path.read_text(encoding="utf-8"))
        prior["audit_scope"] = "skills-dir:/different/scope"
        first_path.write_text(json.dumps(prior), encoding="utf-8")

        second = audit.run_audit(
            skills_dir=skills_dir,
            output_dir=out_dir,
            policy_path=REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml",
        )

        for f in second["findings"]:
            assert f["is_new"] is True

    def test_markdown_surfaces_unchanged_non_high_confidence_carry_forward(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "domain-x/analysis", "x-skill")
        _write_skill(skills_dir, "domain-y/analysis", "y-skill")

        out_dir = tmp_path / "out"
        audit = _import_audit()
        audit.run_audit(
            skills_dir=skills_dir,
            output_dir=out_dir,
            policy_path=REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml",
        )
        second = audit.run_audit(
            skills_dir=skills_dir,
            output_dir=out_dir,
            policy_path=REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml",
        )

        md_path = out_dir / "logs" / "maintenance" / "skills-curation" / f"{date.today().isoformat()}.md"
        md_text = md_path.read_text(encoding="utf-8")
        assert "Suppressed / Carry-Forward Findings" in md_text
        assert "Leaf collision on 'analysis'" in md_text
        assert second["summary_counts"]["suppressed"] >= 1

    def test_path_scope_changes_mark_existing_finding_as_changed(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "area-a/dup", "my-skill")
        _write_skill(skills_dir, "area-b/dup2", "my-skill")

        out_dir = tmp_path / "out"
        audit = _import_audit()
        first = audit.run_audit(
            skills_dir=skills_dir,
            output_dir=out_dir,
            policy_path=REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml",
        )
        first_key = first["findings"][0]["finding_key"]

        _write_skill(skills_dir, "area-c/dup3", "my-skill")
        second = audit.run_audit(
            skills_dir=skills_dir,
            output_dir=out_dir,
            policy_path=REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml",
        )
        second_finding = next(f for f in second["findings"] if f["finding_key"] == first_key)
        assert second_finding["is_new"] is False
        assert second_finding["is_changed"] is True


# ---------------------------------------------------------------------------
# Tests: Waiver handling
# ---------------------------------------------------------------------------

class TestWaiverHandling:
    """Verify waiver registry suppresses but surfaces findings."""

    def test_applies_and_surfaces_waivers(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "area-a/dup", "my-skill")
        _write_skill(skills_dir, "area-b/dup2", "my-skill")

        audit = _import_audit()

        # First run to get finding key
        r1 = audit.run_audit(
            skills_dir=skills_dir,
            output_dir=tmp_path / "out1",
            policy_path=REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml",
        )
        assert len(r1["findings"]) >= 1
        waived_key = r1["findings"][0]["finding_key"]

        # Write waiver for that key
        waiver_path = tmp_path / "waivers.yaml"
        _write_waiver(waiver_path, [
            {"finding_key": waived_key, "reason": "Accepted per #2019", "expires": "2027-01-01"},
        ])

        # Second run with waiver
        r2 = audit.run_audit(
            skills_dir=skills_dir,
            output_dir=tmp_path / "out2",
            policy_path=REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml",
            waiver_path=waiver_path,
        )

        # Waived finding should be in suppressed_findings, not in findings
        suppressed_keys = {f["finding_key"] for f in r2["suppressed_findings"]}
        active_keys = {f["finding_key"] for f in r2["findings"]}
        assert waived_key in suppressed_keys
        assert waived_key not in active_keys

    def test_expired_waiver_is_ignored(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "area-a/dup", "my-skill")
        _write_skill(skills_dir, "area-b/dup2", "my-skill")

        audit = _import_audit()
        first = audit.run_audit(
            skills_dir=skills_dir,
            output_dir=tmp_path / "out1",
            policy_path=REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml",
        )
        waived_key = first["findings"][0]["finding_key"]

        waiver_path = tmp_path / "waivers.yaml"
        _write_waiver(waiver_path, [
            {"finding_key": waived_key, "reason": "Expired waiver", "expires": "2000-01-01"},
        ])

        second = audit.run_audit(
            skills_dir=skills_dir,
            output_dir=tmp_path / "out2",
            policy_path=REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml",
            waiver_path=waiver_path,
        )
        assert waived_key in {f["finding_key"] for f in second["findings"]}
        assert waived_key not in {f["finding_key"] for f in second["suppressed_findings"]}


# ---------------------------------------------------------------------------
# Tests: Read-only behavior
# ---------------------------------------------------------------------------

class TestReadOnly:
    """Verify the audit makes no repo mutations."""

    def test_audit_is_read_only(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "area/skill-a", "skill-a")

        # Snapshot skills dir before audit
        before = set(skills_dir.rglob("*"))

        audit = _import_audit()
        audit.run_audit(
            skills_dir=skills_dir,
            output_dir=tmp_path / "out",
            policy_path=REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml",
        )

        # Skills dir must not be modified
        after = set(skills_dir.rglob("*"))
        assert before == after, "Audit must not modify the skills directory"


# ---------------------------------------------------------------------------
# Tests: Schedule validation (integration)
# ---------------------------------------------------------------------------

class TestScheduleIntegration:
    """Verify schedule-tasks.yaml stays valid after our changes."""

    def test_validate_schedule_still_passes_with_skills_curation_task(self) -> None:
        result = subprocess.run(
            ["uv", "run", "--no-project", "python",
             str(REPO_ROOT / "scripts" / "cron" / "validate-schedule.py")],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Schedule validation failed: {result.stdout}\n{result.stderr}"


import subprocess  # noqa: E402 — needed for schedule test
