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


def _import_disposition_report():
    """Import the issue-scoped #2488 disposition helper."""
    report_path = REPO_ROOT / "scripts" / "skills" / "issue_2488_disposition_report.py"
    import importlib.util
    spec = importlib.util.spec_from_file_location("issue_2488_disposition_report", report_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["issue_2488_disposition_report"] = mod
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


    def test_surfaces_active_filesystem_only_skills_without_archive_aliases(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        tracked = _write_skill(skills_dir, "domain/tracked-skill", "tracked-skill")
        orphan = _write_skill(skills_dir, "personal-tools/loss-risk", "loss-risk")
        archived = _write_skill(skills_dir, "email/_archived/old-skill", "old-skill")

        audit = _import_audit()
        policy = audit._load_policy(REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml")
        inventory = audit.build_inventory(skills_dir)
        trust = {"trusted": True, "reason": "test manifest", "evidence": {}}
        findings = audit._detect_filesystem_inventory_findings(
            inventory,
            policy,
            skills_dir=skills_dir,
            tracked_skill_paths={str(tracked.relative_to(skills_dir))},
            trust=trust,
        )

        assert [f["classification"] for f in findings] == ["filesystem-only-active"]
        finding = findings[0]
        assert finding["family"] == "filesystem-inventory"
        assert finding["severity"] == "high"
        assert finding["paths"] == [str(orphan.relative_to(skills_dir))]
        assert str(archived.relative_to(skills_dir)) not in finding["paths"]
        assert finding["recommended_action"] == "Disposition as promote_after_review, archive_intentionally, ignore_with_rationale, or delete_after_backup before local filesystem state is lost."

    def test_untrusted_git_inventory_suppresses_authoritative_filesystem_findings(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "domain/loss-risk", "loss-risk")

        audit = _import_audit()
        policy = audit._load_policy(REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml")
        inventory = audit.build_inventory(skills_dir)
        trust = {"trusted": False, "reason": "git ls-files returned zero while filesystem has skills", "evidence": {"tracked_count": 0}}
        findings = audit._detect_filesystem_inventory_findings(
            inventory,
            policy,
            skills_dir=skills_dir,
            tracked_skill_paths=set(),
            trust=trust,
        )

        assert findings == []


    def test_inventory_summary_paths_counts_and_mirrors_are_schema_stable(self, tmp_path: Path) -> None:
        repo = tmp_path / "repo"
        skills_dir = repo / ".claude" / "skills"
        tracked = _write_skill(skills_dir, "domain/tracked-skill", "tracked-skill")
        orphan = _write_skill(skills_dir, "domain/loss-risk", "loss-risk")
        _write_skill(skills_dir, "_archive/old-skill", "old-skill")

        audit = _import_audit()
        policy = audit._load_policy(REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml")
        trust = {"trusted": True, "reason": "test", "evidence": {"skills_dir": ".claude/skills"}}
        summary = audit.build_inventory_summary(
            skills_dir,
            policy,
            tracked_skill_paths={str(tracked.relative_to(skills_dir)), "domain/missing-skill/SKILL.md"},
            trust=trust,
        )

        assert set(summary["counts"]) == {
            "tracked_total",
            "tracked_active",
            "filesystem_total",
            "filesystem_active",
            "filesystem_only_total",
            "filesystem_only_active",
            "missing_tracked_total",
            "missing_tracked_active",
            "filesystem_only_archived_total",
        }
        assert summary["counts"]["filesystem_only_active"] == 1
        assert summary["counts"]["missing_tracked_active"] == 1
        assert summary["paths"]["filesystem_only_active"] == [
            {"path": f".claude/skills/{orphan.relative_to(skills_dir)}", "informational": False}
        ]
        assert summary["paths"]["missing_tracked_active"] == [
            {"path": ".claude/skills/domain/missing-skill/SKILL.md", "informational": False}
        ]
        assert summary["paths"]["filesystem_only_archived"] == [
            {"path": ".claude/skills/_archive/old-skill/SKILL.md", "informational": True}
        ]
        assert summary["mirrors"] == {"codex_skills_link": "missing", "gemini_skills_link": "missing"}

    def test_untrusted_git_inventory_suppresses_inventory_summary_authoritative_counts(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "repo" / ".claude" / "skills"
        _write_skill(skills_dir, "domain/loss-risk", "loss-risk")

        audit = _import_audit()
        policy = audit._load_policy(REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml")
        summary = audit.build_inventory_summary(
            skills_dir,
            policy,
            tracked_skill_paths=set(),
            trust={"trusted": False, "reason": "git ls-files returned zero while filesystem has skills", "evidence": {"skills_dir": ".claude/skills"}},
        )

        assert summary["counts"]["filesystem_only_total"] == 0
        assert summary["counts"]["filesystem_only_active"] == 0
        assert summary["counts"]["missing_tracked_total"] == 0
        assert summary["counts"]["missing_tracked_active"] == 0
        assert summary["paths"]["filesystem_only_active"] == []
        assert summary["paths"]["missing_tracked_active"] == []
        assert summary["warnings"] == ["Git inventory not trusted: git ls-files returned zero while filesystem has skills"]

    def test_archived_duplicate_collision_baseline_remains_legacy_compatible(self, tmp_path: Path) -> None:
        fixture = json.loads((REPO_ROOT / "tests" / "fixtures" / "skills" / "issue-2488-archived-duplicate-baseline.json").read_text())
        skills_dir = tmp_path / "skills"
        for rel in fixture["fixture_paths"]:
            _write_skill(skills_dir, str(Path(rel).parent), "gmail-data-extraction")

        audit = _import_audit()
        policy = audit._load_policy(REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml")
        inventory = audit.build_inventory(skills_dir)
        findings = audit._detect_findings(inventory, policy)
        tuple_set = [
            {
                "classification": f["classification"],
                "severity": f["severity"],
                "paths": f["paths"],
            }
            for f in findings
        ]

        assert len(findings) == fixture["expected_legacy_summary_counts"]["findings"]
        assert tuple_set == fixture["expected_tuple_set"]
        assert audit.build_inventory_summary(
            skills_dir,
            policy,
            tracked_skill_paths=set(),
            trust={"trusted": True, "reason": "test", "evidence": {}},
        )["counts"]["filesystem_only_active"] == 0

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
# Tests: #2488 one-time disposition helper
# ---------------------------------------------------------------------------

class TestIssue2488DispositionReport:
    """Verify the issue-scoped closeout helper has deterministic, reviewed output."""

    def _init_repo(self, tmp_path: Path) -> Path:
        repo = tmp_path / "repo"
        repo.mkdir()
        subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True)
        (repo / "config" / "skills").mkdir(parents=True)
        (repo / "config" / "skills" / "weekly-audit-policy.yaml").write_text(
            (REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        (repo / "docs" / "reports").mkdir(parents=True)
        (repo / "docs" / "reports" / "issue-2488-planning-inventory-snapshot.json").write_text(
            json.dumps({"paths": {"filesystem_only_active": [".claude/skills/domain/vanished/SKILL.md"]}}),
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "config/skills/weekly-audit-policy.yaml", "docs/reports/issue-2488-planning-inventory-snapshot.json"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", "seed"], cwd=repo, check=True, capture_output=True, text=True)
        return repo

    def test_disposition_report_uses_snapshot_and_allowed_dispositions(self, tmp_path: Path) -> None:
        repo = self._init_repo(tmp_path)
        skill = repo / ".claude" / "skills" / "domain" / "loss-risk" / "SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("---\nname: loss-risk\ndescription: has token word only\n---\ncontains token marker\n", encoding="utf-8")

        helper = _import_disposition_report()
        output = repo / "docs" / "reports" / "issue-2488-skills-disposition.md"
        data = helper.generate(repo, output)
        text = output.read_text(encoding="utf-8")

        assert data["issue_body_drift"] == [".claude/skills/domain/vanished/SKILL.md"]
        assert data["rows"][0]["disposition"] == "ignore_generated_transient"
        assert set(data["allowed_dispositions"]) == helper.ALLOWED_DISPOSITIONS
        assert "ignore_with_rationale" not in text
        assert "`.claude/skills/domain/loss-risk/SKILL.md`" in text
        assert "`.claude/skills/domain/vanished/SKILL.md`" in text

    def test_disposition_report_rejects_unclassified_live_active_paths(self) -> None:
        helper = _import_disposition_report()
        try:
            helper._validate_report_rows([], [".claude/skills/domain/loss-risk/SKILL.md"])
        except ValueError as exc:
            assert "missing disposition rows" in str(exc)
        else:
            raise AssertionError("expected unclassified active path to be rejected")


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

    def test_schedule_task_only_description_changes_raw_yaml_block(self) -> None:
        expected_description = (
            "Weekly skills curation v2 (Monday 04:00): scans .claude/skills/ for "
            "duplicate names, leaf collisions, wrapper pairs, and filesystem-only active "
            "skill loss-risk inventory. Emits JSON + Markdown artifacts to "
            "logs/maintenance/skills-curation/. Local-only/report-only; no network "
            "posting. Issues #2281, #2488."
        )
        schedule = yaml.safe_load((REPO_ROOT / "config" / "scheduled-tasks" / "schedule-tasks.yaml").read_text())
        task = next(t for t in schedule["tasks"] if t["id"] == "skills-curation")

        assert task["label"] == "Weekly skills audit"
        assert task["schedule"] == "0 4 * * 1"
        assert task["command"] == (
            "PATH=$HOME/.local/bin:$PATH; cd $WORKSPACE_HUB && bash scripts/cron/skills-curation.sh "
            ">> $WORKSPACE_HUB/logs/maintenance/skills-curation-$(date +\\%Y\\%m\\%d).log 2>&1"
        )
        assert task["description"] == expected_description


import subprocess  # noqa: E402 — needed for schedule test
