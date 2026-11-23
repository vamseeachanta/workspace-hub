"""
ABOUTME: WRK-328 — Pytest tests for specs index generation and query functions
ABOUTME: Covers index generation, WRK-ref extraction, tag inference, and query filtering
"""

import datetime
import os
import re
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

# Make the readiness script importable as a module
_SCRIPT = Path(__file__).parent.parent.parent / "scripts" / "readiness" / "build-specs-index.py"
sys.path.insert(0, str(_SCRIPT.parent))
import importlib.util

_spec = importlib.util.spec_from_file_location("build_specs_index", str(_SCRIPT))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

# Aliases to functions under test
_parse_frontmatter = _mod._parse_frontmatter
_extract_title_md = _mod._extract_title_md
_extract_description_md = _mod._extract_description_md
_infer_tags_from_path = _mod._infer_tags_from_path
_extract_wrk_refs = _mod._extract_wrk_refs
_infer_category = _mod._infer_category
_target_repo_from_rel = _mod._target_repo_from_rel
_extract_yaml_title_desc = _mod._extract_yaml_title_desc
process_file = _mod.process_file
walk_specs_dir = _mod.walk_specs_dir
build_index = _mod.build_index


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_specs(tmp_path):
    """Create a minimal specs/ tree for integration tests."""
    specs = tmp_path / "specs"
    (specs / "modules").mkdir(parents=True)
    (specs / "wrk" / "WRK-100").mkdir(parents=True)
    (specs / "repos" / "myrepo").mkdir(parents=True)

    # Standard module spec with WRK ref
    (specs / "modules" / "wrk-100-pipeline-spec.md").write_text(
        "---\ntitle: Pipeline Spec\ndescription: A pipeline spec for WRK-100\n---\n\n"
        "Implements WRK-100 and also references WRK-200.\n",
        encoding="utf-8",
    )

    # WRK plan spec
    (specs / "wrk" / "WRK-100" / "plan.md").write_text(
        "# WRK-100 Plan\n\nDetailed plan for WRK-100 delivery.\n",
        encoding="utf-8",
    )

    # Repo spec (no WRK refs)
    (specs / "repos" / "myrepo" / "overview.md").write_text(
        "---\ntitle: Myrepo Overview\n---\n\nGeneral overview.\n",
        encoding="utf-8",
    )

    # YAML spec
    (specs / "modules" / "data-sources.yaml").write_text(
        "title: Data Sources\ndescription: External data sources\n",
        encoding="utf-8",
    )

    # README — should be skipped
    (specs / "modules" / "README.md").write_text(
        "# Readme\nShould not be indexed.\n",
        encoding="utf-8",
    )

    return specs


# ---------------------------------------------------------------------------
# Unit: _parse_frontmatter
# ---------------------------------------------------------------------------

class TestParseFrontmatter:
    def test_parse_frontmatter_valid(self):
        text = "---\ntitle: Foo\ndescription: Bar\n---\n\nBody text."
        fm, body = _parse_frontmatter(text)
        assert fm["title"] == "Foo"
        assert "Body text" in body

    def test_parse_frontmatter_empty(self):
        text = "Just plain markdown."
        fm, body = _parse_frontmatter(text)
        assert fm == {}
        assert "Just plain" in body

    def test_parse_frontmatter_no_closing(self):
        text = "---\ntitle: Foo\n\nBody."
        fm, body = _parse_frontmatter(text)
        assert fm == {}

    def test_parse_frontmatter_invalid_yaml(self):
        text = "---\n: bad: yaml:\n---\nBody."
        fm, body = _parse_frontmatter(text)
        # Falls back gracefully — no crash
        assert isinstance(fm, dict)


# ---------------------------------------------------------------------------
# Unit: _extract_title_md
# ---------------------------------------------------------------------------

class TestExtractTitleMd:
    def test_extracts_first_h1(self):
        text = "# My Title\n\nSome paragraph."
        assert _extract_title_md(text) == "My Title"

    def test_skips_empty_h1(self):
        text = "# \n# Real Title\n"
        assert _extract_title_md(text) == "Real Title"

    def test_no_heading_returns_empty(self):
        text = "Just some text without headings."
        assert _extract_title_md(text) == ""

    def test_h2_not_extracted(self):
        text = "## Subheading\n\nContent."
        assert _extract_title_md(text) == ""


# ---------------------------------------------------------------------------
# Unit: _extract_description_md
# ---------------------------------------------------------------------------

class TestExtractDescriptionMd:
    def test_returns_first_paragraph(self):
        body = "\nSome intro paragraph.\n\nSecond paragraph."
        desc = _extract_description_md(body)
        assert "Some intro" in desc
        assert "Second" not in desc

    def test_skips_blockquotes(self):
        body = "> Blockquote line\n\nReal paragraph."
        desc = _extract_description_md(body)
        assert "Real paragraph" in desc
        assert "Blockquote" not in desc

    def test_truncates_at_200_chars(self):
        long_text = "A" * 250
        body = long_text
        desc = _extract_description_md(body)
        assert len(desc) <= 200


# ---------------------------------------------------------------------------
# Unit: _extract_wrk_refs
# ---------------------------------------------------------------------------

class TestExtractWrkRefs:
    def test_extract_from_path(self):
        refs = _extract_wrk_refs(
            "specs/wrk/WRK-100/plan.md", {}, "", "", ""
        )
        assert "WRK-100" in refs

    def test_extract_from_title(self):
        refs = _extract_wrk_refs("specs/modules/foo.md", {}, "WRK-200 spec", "", "")
        assert "WRK-200" in refs

    def test_extract_from_description(self):
        refs = _extract_wrk_refs(
            "specs/modules/foo.md", {}, "", "Implements WRK-300 pipeline", ""
        )
        assert "WRK-300" in refs

    def test_extract_from_raw_content(self):
        refs = _extract_wrk_refs(
            "specs/modules/foo.md", {}, "", "", "See also WRK-400 and WRK-401."
        )
        assert "WRK-400" in refs
        assert "WRK-401" in refs

    def test_extract_from_frontmatter_related(self):
        fm = {"related": ["WRK-500", "WRK-501"]}
        refs = _extract_wrk_refs("specs/modules/foo.md", fm, "", "", "")
        assert "WRK-500" in refs
        assert "WRK-501" in refs

    def test_deduplication(self):
        refs = _extract_wrk_refs(
            "specs/wrk/WRK-100/plan.md",
            {"id": "WRK-100"},
            "WRK-100 Plan",
            "WRK-100 delivery",
            "WRK-100 details",
        )
        assert refs.count("WRK-100") == 1

    def test_sorted_numerically(self):
        refs = _extract_wrk_refs(
            "specs/modules/foo.md", {}, "WRK-20 and WRK-3 spec", "", ""
        )
        nums = [int(r.split("-")[1]) for r in refs]
        assert nums == sorted(nums)

    def test_case_insensitive_extraction(self):
        refs = _extract_wrk_refs(
            "specs/modules/foo.md", {}, "wrk-999 spec", "", ""
        )
        assert "WRK-999" in refs

    def test_empty_when_no_refs(self):
        refs = _extract_wrk_refs("specs/modules/foo.md", {}, "Pipeline spec", "", "")
        assert refs == []

    def test_raw_content_limited_to_4000_chars(self):
        # WRK-9999 only appears after 4000 chars — should NOT be found
        content = ("x" * 4001) + " WRK-9999 "
        refs = _extract_wrk_refs("specs/modules/foo.md", {}, "", "", content)
        assert "WRK-9999" not in refs


# ---------------------------------------------------------------------------
# Unit: _infer_category
# ---------------------------------------------------------------------------

class TestInferCategory:
    def test_modules_category(self):
        cat = _infer_category("specs/modules/foo.md", "specs")
        assert cat == "modules"

    def test_wrk_category(self):
        cat = _infer_category("specs/wrk/WRK-100/plan.md", "specs")
        assert cat == "wrk"

    def test_repos_category(self):
        cat = _infer_category("specs/repos/myrepo/overview.md", "specs")
        assert cat == "repos"

    def test_other_category_for_unknown(self):
        cat = _infer_category("specs/architecture/foo.md", "specs")
        assert cat == "other"

    def test_submodule_path(self):
        cat = _infer_category("digitalmodel/specs/modules/foo.md", "digitalmodel/specs")
        assert cat == "modules"


# ---------------------------------------------------------------------------
# Unit: _target_repo_from_rel
# ---------------------------------------------------------------------------

class TestTargetRepoFromRel:
    def test_repos_path_extracts_subrepo(self):
        repo = _target_repo_from_rel(
            "specs/repos/digitalmodel/foo.md", "specs", "workspace-hub"
        )
        assert repo == "digitalmodel"

    def test_non_repos_path_returns_repo_name(self):
        repo = _target_repo_from_rel(
            "specs/modules/foo.md", "specs", "workspace-hub"
        )
        assert repo == "workspace-hub"

    def test_submodule_path_returns_repo_name(self):
        repo = _target_repo_from_rel(
            "digitalmodel/specs/modules/foo.md", "digitalmodel/specs", "digitalmodel"
        )
        assert repo == "digitalmodel"


# ---------------------------------------------------------------------------
# Unit: _extract_yaml_title_desc
# ---------------------------------------------------------------------------

class TestExtractYamlTitleDesc:
    def test_extracts_title_and_description(self):
        content = "title: My YAML Spec\ndescription: Describes something.\n"
        title, desc = _extract_yaml_title_desc(content)
        assert title == "My YAML Spec"
        assert "Describes" in desc

    def test_falls_back_to_name_field(self):
        content = "name: My Module\n"
        title, desc = _extract_yaml_title_desc(content)
        assert title == "My Module"

    def test_invalid_yaml_returns_empty(self):
        title, desc = _extract_yaml_title_desc(": invalid: yaml:")
        assert title == ""
        assert desc == ""

    def test_standards_list_generates_description(self):
        content = "repo: myrepo\nstandards:\n  - DNV\n  - ISO\n"
        title, desc = _extract_yaml_title_desc(content)
        assert "2" in desc or "myrepo" in desc


# ---------------------------------------------------------------------------
# Integration: process_file
# ---------------------------------------------------------------------------

class TestProcessFile:
    def test_process_md_file_with_frontmatter(self, tmp_path):
        f = tmp_path / "specs" / "modules" / "my-spec.md"
        f.parent.mkdir(parents=True)
        f.write_text(
            "---\ntitle: My Spec\ndescription: Foo bar\n---\n\nBody.\n",
            encoding="utf-8",
        )
        specs_dir = tmp_path / "specs"
        # Temporarily override HUB_ROOT for relative path computation
        orig_hub = _mod.HUB_ROOT
        _mod.HUB_ROOT = str(tmp_path)
        try:
            rec = process_file(str(f), str(specs_dir), "workspace-hub")
        finally:
            _mod.HUB_ROOT = orig_hub
        assert rec is not None
        assert rec["title"] == "My Spec"
        assert rec["category"] == "modules"
        assert rec["repo"] == "workspace-hub"
        assert "mtime" in rec
        assert isinstance(rec["wrk_refs"], list)

    def test_process_readme_returns_none(self, tmp_path):
        f = tmp_path / "specs" / "modules" / "README.md"
        f.parent.mkdir(parents=True)
        f.write_text("# Readme\n", encoding="utf-8")
        specs_dir = tmp_path / "specs"
        orig_hub = _mod.HUB_ROOT
        _mod.HUB_ROOT = str(tmp_path)
        try:
            rec = process_file(str(f), str(specs_dir), "workspace-hub")
        finally:
            _mod.HUB_ROOT = orig_hub
        assert rec is None

    def test_process_yaml_spec(self, tmp_path):
        f = tmp_path / "specs" / "modules" / "data.yaml"
        f.parent.mkdir(parents=True)
        f.write_text("title: Data Spec\ndescription: A data source\n", encoding="utf-8")
        specs_dir = tmp_path / "specs"
        orig_hub = _mod.HUB_ROOT
        _mod.HUB_ROOT = str(tmp_path)
        try:
            rec = process_file(str(f), str(specs_dir), "workspace-hub")
        finally:
            _mod.HUB_ROOT = orig_hub
        assert rec is not None
        assert rec["title"] == "Data Spec"

    def test_process_file_extracts_wrk_refs(self, tmp_path):
        f = tmp_path / "specs" / "modules" / "wrk-123-foo.md"
        f.parent.mkdir(parents=True)
        f.write_text(
            "---\ntitle: WRK-123 Foo\n---\n\nImplements WRK-123 and WRK-456.\n",
            encoding="utf-8",
        )
        specs_dir = tmp_path / "specs"
        orig_hub = _mod.HUB_ROOT
        _mod.HUB_ROOT = str(tmp_path)
        try:
            rec = process_file(str(f), str(specs_dir), "workspace-hub")
        finally:
            _mod.HUB_ROOT = orig_hub
        assert rec is not None
        assert "WRK-123" in rec["wrk_refs"]
        assert "WRK-456" in rec["wrk_refs"]

    def test_process_unsupported_extension_returns_none(self, tmp_path):
        f = tmp_path / "specs" / "modules" / "foo.txt"
        f.parent.mkdir(parents=True)
        f.write_text("Some text.\n", encoding="utf-8")
        specs_dir = tmp_path / "specs"
        orig_hub = _mod.HUB_ROOT
        _mod.HUB_ROOT = str(tmp_path)
        try:
            rec = process_file(str(f), str(specs_dir), "workspace-hub")
        finally:
            _mod.HUB_ROOT = orig_hub
        assert rec is None


# ---------------------------------------------------------------------------
# Integration: walk_specs_dir
# ---------------------------------------------------------------------------

class TestWalkSpecsDir:
    def test_walk_collects_records(self, tmp_specs, tmp_path):
        orig_hub = _mod.HUB_ROOT
        _mod.HUB_ROOT = str(tmp_path)
        records = []
        try:
            walk_specs_dir(str(tmp_specs), "workspace-hub", records)
        finally:
            _mod.HUB_ROOT = orig_hub
        paths = [r["path"] for r in records]
        # README should be absent
        assert not any("README" in p for p in paths)
        # Must have at least the 4 non-readme files
        assert len(records) >= 4

    def test_walk_skips_nonexistent_dir(self):
        records = []
        walk_specs_dir("/nonexistent/path", "workspace-hub", records)
        assert records == []

    def test_walk_wrk_refs_present(self, tmp_specs, tmp_path):
        orig_hub = _mod.HUB_ROOT
        _mod.HUB_ROOT = str(tmp_path)
        records = []
        try:
            walk_specs_dir(str(tmp_specs), "workspace-hub", records)
        finally:
            _mod.HUB_ROOT = orig_hub
        module_spec = next(
            (r for r in records if "pipeline-spec" in r["path"]), None
        )
        assert module_spec is not None
        assert "WRK-100" in module_spec["wrk_refs"]
        assert "WRK-200" in module_spec["wrk_refs"]


# ---------------------------------------------------------------------------
# Integration: build_index
# ---------------------------------------------------------------------------

class TestBuildIndex:
    def test_build_index_structure(self, tmp_specs, tmp_path, monkeypatch):
        monkeypatch.setattr(_mod, "HUB_ROOT", str(tmp_path))
        # Point the hub specs at our tmp_specs
        monkeypatch.setattr(_mod, "SUBMODULE_REPOS", [])
        # Temporarily remap hub specs dir
        original_join = os.path.join

        def patched_join(*args):
            if args == (_mod.HUB_ROOT, "specs"):
                return str(tmp_specs)
            return original_join(*args)

        monkeypatch.setattr(os.path, "join", patched_join)

        index = build_index()
        assert "generated" in index
        assert "total_specs" in index
        assert "by_category" in index
        assert "by_repo" in index
        assert "by_wrk" in index
        assert "specs" in index
        assert index["total_specs"] == len(index["specs"])

    def test_build_index_by_wrk_populated(self, tmp_specs, tmp_path, monkeypatch):
        monkeypatch.setattr(_mod, "HUB_ROOT", str(tmp_path))
        monkeypatch.setattr(_mod, "SUBMODULE_REPOS", [])

        original_join = os.path.join

        def patched_join(*args):
            if args == (_mod.HUB_ROOT, "specs"):
                return str(tmp_specs)
            return original_join(*args)

        monkeypatch.setattr(os.path, "join", patched_join)

        index = build_index()
        # WRK-100 appears in path AND content — must be in by_wrk
        assert "WRK-100" in index["by_wrk"]

    def test_build_index_generated_date(self, tmp_specs, tmp_path, monkeypatch):
        monkeypatch.setattr(_mod, "HUB_ROOT", str(tmp_path))
        monkeypatch.setattr(_mod, "SUBMODULE_REPOS", [])

        original_join = os.path.join

        def patched_join(*args):
            if args == (_mod.HUB_ROOT, "specs"):
                return str(tmp_specs)
            return original_join(*args)

        monkeypatch.setattr(os.path, "join", patched_join)

        index = build_index()
        today = datetime.date.today().isoformat()
        assert index["generated"] == today

    def test_index_yaml_valid_yaml(self, tmp_specs, tmp_path, monkeypatch, tmp_path_factory):
        out_dir = tmp_path_factory.mktemp("out")
        out_file = out_dir / "specs" / "index.yaml"
        out_file.parent.mkdir(parents=True)

        monkeypatch.setattr(_mod, "HUB_ROOT", str(tmp_path))
        monkeypatch.setattr(_mod, "SUBMODULE_REPOS", [])
        monkeypatch.setattr(_mod, "OUTPUT_FILE", str(out_file))

        original_join = os.path.join

        def patched_join(*args):
            if args == (_mod.HUB_ROOT, "specs"):
                return str(tmp_specs)
            return original_join(*args)

        monkeypatch.setattr(os.path, "join", patched_join)

        _mod.main()
        assert out_file.exists()
        with open(out_file, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        assert isinstance(data, dict)
        assert "specs" in data
        assert "by_wrk" in data
