"""TDD — build_topics_index.py (#3189): class-grouped, deterministic, self-excluding."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

MOD_PATH = Path(__file__).resolve().parents[1] / "build_topics_index.py"
spec = importlib.util.spec_from_file_location("build_topics_index", MOD_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["build_topics_index"] = mod
spec.loader.exec_module(mod)


@pytest.fixture
def topics(tmp_path):
    d = tmp_path / "topics"
    d.mkdir()
    (d / "feedback_a.md").write_text(
        "---\nname: A lesson\ndescription: about git\ntype: feedback\n---\nbody a\n")
    (d / "project_b.md").write_text(
        "---\nname: Proj B\ndescription: ongoing\ntype: project\n---\nbody b\n")
    # no `type:` -> classified by slug prefix
    (d / "reference_c.md").write_text("---\nname: Ref C\ndescription: pointer\n---\nbody c\n")
    # no frontmatter at all -> "other", title = stem
    (d / "loose_note.md").write_text("just a note, no frontmatter\n")
    # leading quote block before frontmatter (real corpus shape)
    (d / "feedback_d.md").write_text(
        "> snapshot\n> source\n\n---\nname: D\ndescription: quoted\ntype: feedback\n---\nx\n")
    return d


def test_groups_by_class(topics):
    out = mod.build_index(topics)
    assert "## Feedback" in out and "## Project" in out and "## Reference" in out
    assert "[A lesson](feedback_a.md)" in out
    assert "[Proj B](project_b.md)" in out
    assert "[Ref C](reference_c.md)" in out  # slug-prefix classified


def test_loose_note_is_other_with_stem_title(topics):
    out = mod.build_index(topics)
    assert "## Other" in out
    assert "[loose_note](loose_note.md)" in out  # title falls back to stem


def test_excludes_self(topics):
    (topics / "INDEX.md").write_text("stale index\n")
    out = mod.build_index(topics)
    assert "(INDEX.md)" not in out


def test_deterministic_byte_identical(topics):
    assert mod.build_index(topics) == mod.build_index(topics)
    assert "name:" not in mod.build_index(topics).split("\n")[0]  # no frontmatter date leak in header


def test_no_timestamp_in_header(topics):
    out = mod.build_index(topics)
    # header is static — must not embed any 20YY-.. date
    import re
    assert not re.search(r"20\d\d-\d\d-\d\d", out.split("##")[0])


def test_leading_quote_block_tolerated(topics):
    out = mod.build_index(topics)
    assert "[D](feedback_d.md)" in out  # frontmatter after `>` lines still parsed
