"""V2 tests for the deterministic weekly skills housekeeping audit (#2486)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]


def _import_audit():
    audit_path = REPO_ROOT / "scripts" / "skills" / "weekly_skills_audit.py"
    import importlib.util

    spec = importlib.util.spec_from_file_location("weekly_skills_audit", audit_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["weekly_skills_audit"] = mod
    spec.loader.exec_module(mod)
    return mod


def _write_skill(
    base: Path,
    rel_path: str,
    name: str,
    *,
    category: str | None = None,
    description: str = "A useful deterministic test skill.",
    body_lines: int = 1,
    extra_frontmatter: dict | None = None,
) -> Path:
    d = base / rel_path
    d.mkdir(parents=True, exist_ok=True)
    fm = {
        "name": name,
        "description": description,
    }
    if category is not None:
        fm["category"] = category
    if extra_frontmatter:
        fm.update(extra_frontmatter)
    body = "\n".join(f"line {i}" for i in range(body_lines))
    path = d / "SKILL.md"
    path.write_text("---\n" + yaml.safe_dump(fm, sort_keys=False) + "---\n" + body + "\n", encoding="utf-8")
    return path


def _run(tmp_path: Path, skills_dir: Path, **kwargs):
    audit = _import_audit()
    return audit.run_audit(
        skills_dir=skills_dir,
        output_dir=tmp_path / "out",
        policy_path=REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml",
        **kwargs,
    )


class TestV2SchemaAndSignals:
    def test_v2_schema_contains_stable_optional_sections_when_usage_absent(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "business/good", "good", category="business")

        result = _run(tmp_path, skills_dir)

        assert result["schema_version"] == 2
        assert result["baseline_compatibility"]["state"] in {"absent", "compatible", "ignored"}
        assert result["usage_findings"] == []
        assert result["follow_up_candidates"] == []
        assert "github_update_payload_path" not in result
        assert {"active", "informational", "excluded", "malformed"} <= set(result["skill_counts"])
        assert "content_quality_findings" in result
        assert "grouping_findings" in result
        assert "size_findings" in result
        assert "scan_durations" in result

    def test_v2_reports_missing_category_frontmatter_with_stable_key(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "business/missing-category", "missing-category")

        first = _run(tmp_path, skills_dir)
        second = _run(tmp_path, skills_dir)

        findings = first["content_quality_findings"]
        missing = [f for f in findings if f["rule_id"] == "missing-category"]
        assert len(missing) == 1
        assert missing[0]["severity"] == "medium"
        assert missing[0]["paths"] == ["business/missing-category/SKILL.md"]
        assert missing[0]["finding_key"] == [
            f for f in second["content_quality_findings"] if f["rule_id"] == "missing-category"
        ][0]["finding_key"]

    def test_v2_reports_category_path_mismatch_and_policy_alias_family(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "workspace_hub_learned/drift", "drift", category="workspace-hub-learned")
        _write_skill(skills_dir, "business_admin/tax", "tax", category="business/admin")

        result = _run(tmp_path, skills_dir)

        grouping = result["grouping_findings"]
        assert any(f["rule_id"] == "category-path-mismatch" for f in grouping)
        alias_ids = {f.get("alias_family_id") for f in grouping}
        assert "workspace-hub-learned" in alias_ids
        assert "business-admin" in alias_ids
        for finding in grouping:
            assert len(finding["finding_key"]) <= 32

    def test_v2_reports_oversized_active_skill_but_suppresses_internal_headline(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "business/huge", "huge", category="business", body_lines=40)
        _write_skill(skills_dir, "_core/internal-huge", "internal-huge", category="_core", body_lines=40)

        result = _run(tmp_path, skills_dir)

        size = result["size_findings"]
        active = [f for f in size if "business/huge/SKILL.md" in f["paths"]]
        internal = [f for f in size if "_core/internal-huge/SKILL.md" in f["paths"]]
        assert active and active[0]["headline"] is True
        assert internal and internal[0]["headline"] is False

    def test_v2_policy_severity_confidence_headline_mapping_is_stable(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "business/no-category", "no-category")
        _write_skill(skills_dir, "business_admin/tax", "tax", category="business/admin")
        _write_skill(skills_dir, "business/huge", "huge", category="business", body_lines=40)
        _write_skill(skills_dir, "_core/huge", "core-huge", category="_core", body_lines=40)

        result = _run(tmp_path, skills_dir)
        mappings = {
            (f["family"], f["rule_id"]): (f["severity"], f["confidence"], f["headline"])
            for f in result["content_quality_findings"] + result["grouping_findings"] + result["size_findings"]
        }

        assert mappings[("content-quality", "missing-category")] == ("medium", "high", True)
        assert mappings[("grouping", "category-path-mismatch")] == ("medium", "high", True)
        assert mappings[("size", "oversized-skill")] == ("medium", "high", True)
        assert any(
            f["family"] == "size" and f["rule_id"] == "oversized-skill" and f["headline"] is False
            for f in result["size_findings"]
        )


class TestV2SafetyAndPayload:
    def test_v2_default_run_does_not_call_gh_or_network_or_write_usage_state(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "business/good", "good", category="business")
        state_dir = REPO_ROOT / ".claude" / "state" / "skill-usage-report"
        before_exists = state_dir.exists()
        monkeypatch.setenv("GH_TOKEN", "would-fail-if-used")

        result = _run(tmp_path, skills_dir)

        assert result["usage_findings"] == []
        assert state_dir.exists() is before_exists
        assert "github_update_payload_path" not in result

    def test_v2_renders_manual_github_payload_without_posting(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "business/good", "good", category="business")

        result = _run(tmp_path, skills_dir, render_github_payload=True)

        payload = Path(result["github_update_payload_path"])
        assert payload.exists()
        assert payload.parent == tmp_path / "out" / "logs" / "maintenance" / "skills-curation"
        assert payload.name == "github-update-payload.md"
        assert "gh issue comment" not in payload.read_text(encoding="utf-8")

    def test_v2_first_run_after_v1_baseline_carries_forward_legacy_findings(self, tmp_path: Path) -> None:
        audit = _import_audit()
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "business/dup-a", "shared", category="business")
        _write_skill(skills_dir, "business/dup-b", "shared", category="business")
        probe = audit.run_audit(
            skills_dir=skills_dir,
            output_dir=tmp_path / "probe-out",
            policy_path=REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml",
        )
        legacy_finding = dict(probe["findings"][0])
        legacy_key = legacy_finding["finding_key"]
        artifact_dir = tmp_path / "out" / "logs" / "maintenance" / "skills-curation"
        artifact_dir.mkdir(parents=True)
        (artifact_dir / "2026-01-01.json").write_text(
            json.dumps({
                "generated_at": "2026-01-01T00:00:00Z",
                "policy_version": "weekly-skills-audit-v1-v1",
                "audit_scope": audit._derive_audit_scope(skills_dir),
                "findings": [legacy_finding],
                "suppressed_findings": [],
            }),
            encoding="utf-8",
        )

        result = _run(tmp_path, skills_dir)

        assert result["baseline_compatibility"]["state"] == "compatible-previous-policy"
        duplicate = [f for f in result["findings"] if f["finding_key"] == legacy_key][0]
        assert duplicate["is_new"] is False
        assert duplicate["is_changed"] is False

    def test_v2_grouping_key_hashes_large_offender_sets(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        for i in range(120):
            _write_skill(skills_dir, f"workspace_hub_learned/skill-{i}", f"skill-{i}", category="workspace-hub-learned")

        result = _run(tmp_path, skills_dir)
        alias_findings = [
            f for f in result["grouping_findings"]
            if f.get("alias_family_id") == "workspace-hub-learned"
        ]

        assert alias_findings
        assert all(len(f["finding_key"]) <= 32 for f in alias_findings)
        assert all("skill-119" not in f["finding_key"] for f in alias_findings)


class TestV2ReviewRegressionCoverage:
    def test_v2_baseline_marks_content_quality_carry_forward_not_new_forever(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "business/missing-category", "missing-category")

        first = _run(tmp_path, skills_dir)
        second = _run(tmp_path, skills_dir)

        first_key = first["content_quality_findings"][0]["finding_key"]
        second_finding = [
            f for f in second["content_quality_findings"]
            if f["finding_key"] == first_key
        ][0]
        assert second_finding["is_new"] is False
        assert second_finding["is_changed"] is False
        assert second["baseline_compatibility"]["state"] == "compatible"

    def test_v2_waiver_suppresses_grouping_finding_into_suppressed_findings(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "business_admin/tax", "tax", category="business/admin")
        first = _run(tmp_path, skills_dir)
        key = [
            f for f in first["grouping_findings"]
            if f["rule_id"] == "category-path-mismatch"
        ][0]["finding_key"]
        waiver_path = tmp_path / "waivers.yaml"
        waiver_path.write_text(
            yaml.safe_dump({"waivers": [{"finding_key": key, "reason": "known taxonomy migration"}]}),
            encoding="utf-8",
        )

        second = _run(tmp_path, skills_dir, waiver_path=waiver_path)

        assert all(f["finding_key"] != key for f in second["grouping_findings"])
        suppressed = [f for f in second["suppressed_findings"] if f["finding_key"] == key]
        assert suppressed
        assert suppressed[0]["waiver_reason"] == "known taxonomy migration"

    def test_v2_markdown_and_summary_counts_include_v2_only_findings(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "business/missing-category", "missing-category")
        _write_skill(skills_dir, "business/huge", "huge", category="business", body_lines=40)

        result = _run(tmp_path, skills_dir)
        md_path = tmp_path / "out" / "logs" / "maintenance" / "skills-curation" / f"{Path(result['generated_at']).name[:10]}.md"
        # generated_at is an ISO timestamp; run_audit uses today's date for the filename by default.
        md_candidates = sorted((tmp_path / "out" / "logs" / "maintenance" / "skills-curation").glob("*.md"))
        markdown = md_candidates[-1].read_text(encoding="utf-8")

        assert result["summary_counts"]["total"] >= len(result["content_quality_findings"]) + len(result["size_findings"])
        assert "## Content Quality Findings" in markdown
        assert "missing-category" in markdown
        assert "## Oversized / Maintainability Findings" in markdown
        assert "oversized-skill" in markdown
        assert "## Follow-up Candidates" in markdown

    def test_v2_inventory_records_policy_required_source_id(self, tmp_path: Path) -> None:
        audit = _import_audit()
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "business/good", "good", category="business")

        inventory = audit.build_inventory(skills_dir)

        assert inventory
        assert all(item.get("source_id") == "local-skill-filesystem" for item in inventory)

    def test_v2_alias_drift_requires_mixed_raw_spellings_not_single_canonical_spelling(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "workspace-hub-learned/clean", "clean", category="workspace-hub-learned")

        clean = _run(tmp_path, skills_dir)
        assert not [
            f for f in clean["grouping_findings"]
            if f.get("alias_family_id") == "workspace-hub-learned" and f["rule_id"] == "category-alias-drift"
        ]

        _write_skill(skills_dir, "workspace_hub_learned/drift", "drift", category="workspace-hub-learned")
        drift = _run(tmp_path, skills_dir)
        assert [
            f for f in drift["grouping_findings"]
            if f.get("alias_family_id") == "workspace-hub-learned" and f["rule_id"] == "category-alias-drift"
        ]

    def test_v2_alias_drift_ignores_non_family_path_prefix_for_slash_category(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "business/tax", "tax", category="business/admin")

        result = _run(tmp_path, skills_dir)

        assert not [
            f for f in result["grouping_findings"]
            if f.get("alias_family_id") == "business-admin" and f["rule_id"] == "category-alias-drift"
        ]

        _write_skill(skills_dir, "business_admin/drift", "drift", category="business/admin")
        drift = _run(tmp_path, skills_dir)
        assert [
            f for f in drift["grouping_findings"]
            if f.get("alias_family_id") == "business-admin" and f["rule_id"] == "category-alias-drift"
        ]
