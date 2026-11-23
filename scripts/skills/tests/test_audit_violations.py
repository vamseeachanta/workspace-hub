#!/usr/bin/env python3
"""Tests for violation checks in audit-skill-lib.py."""

from __future__ import annotations

import importlib.util
import textwrap
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def lib():
    spec = importlib.util.spec_from_file_location(
        "audit_skill_lib", Path(__file__).parent.parent / "audit_skill_lib.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def skill_tree(tmp_path):
    d = tmp_path / "skills"
    d.mkdir()
    return d


def _write(skill_dir: Path, name: str, content: str) -> Path:
    d = skill_dir / name
    d.mkdir(parents=True, exist_ok=True)
    p = d / "SKILL.md"
    p.write_text(textwrap.dedent(content))
    return p


class TestReadmePresent:
    def test_flags_readme(self, lib, skill_tree):
        _write(skill_tree, "has-readme", "---\nname: t\ndescription: t\n---\n# T")
        (skill_tree / "has-readme" / "README.md").write_text("old")
        assert any(v["check"] == "readme_present" for v in lib.run_violations_audit(skill_tree))

    def test_no_readme_clean(self, lib, skill_tree):
        _write(skill_tree, "no-readme", "---\nname: t\ndescription: t\n---\n# T")
        assert not any(v["check"] == "readme_present" for v in lib.run_violations_audit(skill_tree))


class TestWordCount:
    def test_flags_over_5000(self, lib, skill_tree):
        _write(skill_tree, "wordy", f"---\nname: w\ndescription: t\n---\n{'word ' * 5001}")
        assert any(v["check"] == "word_count_exceeded" for v in lib.run_violations_audit(skill_tree))

    def test_under_5000_clean(self, lib, skill_tree):
        _write(skill_tree, "short", f"---\nname: s\ndescription: t\n---\n{'word ' * 100}")
        assert not any(v["check"] == "word_count_exceeded" for v in lib.run_violations_audit(skill_tree))


class TestDescriptionLength:
    def test_flags_over_1024(self, lib, skill_tree):
        _write(skill_tree, "ld", f"---\nname: ld\ndescription: \"{'a' * 1025}\"\n---\n# LD")
        assert any(v["check"] == "description_too_long" for v in lib.run_violations_audit(skill_tree))

    def test_short_desc_clean(self, lib, skill_tree):
        _write(skill_tree, "sd", "---\nname: sd\ndescription: short\n---\n# SD")
        assert not any(v["check"] == "description_too_long" for v in lib.run_violations_audit(skill_tree))


class TestXmlTags:
    def test_flags_custom_xml(self, lib, skill_tree):
        _write(skill_tree, "xml", "---\nname: x\ndescription: t\n---\n<CUSTOM_TAG>c</CUSTOM_TAG>")
        assert any(v["check"] == "xml_html_tags_in_body" for v in lib.run_violations_audit(skill_tree))

    def test_ignores_code_blocks(self, lib, skill_tree):
        _write(skill_tree, "cb", "---\nname: cb\ndescription: t\n---\n```\n<CUSTOM>ok</CUSTOM>\n```")
        assert not any(v["check"] == "xml_html_tags_in_body" for v in lib.run_violations_audit(skill_tree))

    def test_allows_standard_html(self, lib, skill_tree):
        _write(skill_tree, "html", "---\nname: h\ndescription: t\n---\n<details><summary>hi</summary></details>")
        assert not any(v["check"] == "xml_html_tags_in_body" for v in lib.run_violations_audit(skill_tree))
