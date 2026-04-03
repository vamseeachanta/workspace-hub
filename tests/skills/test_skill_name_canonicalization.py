"""Tests for canonical skill naming under leaf-directory collisions (#1740)."""
from __future__ import annotations

import importlib.util
import sys
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
USAGE_REPORT = REPO_ROOT / "scripts" / "skills" / "skill-usage-report.py"
DUPLICATE_CHECK = REPO_ROOT / "scripts" / "skills" / "detect_duplicate_skills.py"

spec = importlib.util.spec_from_file_location("skill_usage_report_canonical", USAGE_REPORT)
usage = importlib.util.module_from_spec(spec)
sys.modules["skill_usage_report_canonical"] = usage
assert spec and spec.loader
spec.loader.exec_module(usage)

spec2 = importlib.util.spec_from_file_location("detect_duplicate_skills_mod", DUPLICATE_CHECK)
dup = importlib.util.module_from_spec(spec2)
sys.modules["detect_duplicate_skills_mod"] = dup
assert spec2 and spec2.loader
spec2.loader.exec_module(dup)


def test_scan_skills_prefers_frontmatter_name_over_leaf_dir(tmp_path):
    first = tmp_path / "business" / "marketing" / "competitive-analysis"
    second = tmp_path / "business" / "product" / "competitive-analysis"
    first.mkdir(parents=True)
    second.mkdir(parents=True)

    (first / "SKILL.md").write_text("---\nname: marketing-competitive-analysis\n---\n")
    (second / "SKILL.md").write_text("---\nname: product-competitive-analysis\n---\n")

    skills = usage.scan_skills(tmp_path)
    assert skills["business/marketing/competitive-analysis"]["short_name"] == "marketing-competitive-analysis"
    assert skills["business/product/competitive-analysis"]["short_name"] == "product-competitive-analysis"


def test_duplicate_detector_reports_leaf_collisions_separately(tmp_path):
    first = tmp_path / "engineering" / "cfd" / "openfoam" / "analysis"
    second = tmp_path / "engineering" / "marine-offshore" / "orcawave" / "analysis"
    first.mkdir(parents=True)
    second.mkdir(parents=True)

    (first / "SKILL.md").write_text("---\nname: openfoam-analysis\n---\n")
    (second / "SKILL.md").write_text("---\nname: orcawave-analysis\n---\n")

    result = subprocess.run(
        [sys.executable, str(DUPLICATE_CHECK), "--skills-dir", str(tmp_path)],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "DUPLICATE leaf directory 'analysis'" in result.stdout
    assert "openfoam-analysis" not in result.stdout
    assert "orcawave-analysis" not in result.stdout
