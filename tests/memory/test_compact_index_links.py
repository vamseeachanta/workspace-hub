"""Synthetic, hand-counted examples for annotation-only index shortening.

Preservation basis: issue #3366 requires keeping all index entries. No policy
threshold is chosen here; budgets are byte lengths of literal expected strings.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[2] / "scripts/memory/compact_index_links.py"
spec = importlib.util.spec_from_file_location("compact_index_links", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
shorten_index = module.shorten_index

# Two entries, with two headings and a non-entry note. The mandatory skeleton
# has 18 + 1 + 12 + 25 + 25 + 16 = 97 bytes (em dash = three UTF-8 bytes).
INDEX = (
    "# Synthetic index\n"
    "\n"
    "## Guidance\n"
    "- [First](first.md) — long annotation about repeatable checks\n"
    "- [Other](other.md) — café 漢字🙂 and further details\n"
    "Keep this note.\n"
)
SKELETON = (
    "# Synthetic index\n"
    "\n"
    "## Guidance\n"
    "- [First](first.md) — \n"
    "- [Other](other.md) — \n"
    "Keep this note.\n"
)


def test_every_link_survives_shortening():
    expected = SKELETON.replace("— \n", "— lo\n", 1).replace(
        "[Other](other.md) — \n", "[Other](other.md) — ca\n"
    )
    result = shorten_index(INDEX, len(expected.encode("utf-8")))
    assert result.status == "shortened"
    assert result.text == expected
    assert result.output_bytes == len(expected.encode("utf-8"))
    assert result.minimum_bytes == len(SKELETON.encode("utf-8"))
    assert result.text.count("[First](first.md)") == 1
    assert result.text.count("[Other](other.md)") == 1


def test_utf8_budget_counts_bytes():
    # Prefix = 16 bytes, newline = one; é = two, 漢 = three, 🙂 = four.
    source = "- [A](a.md) — é漢🙂\n"
    expected = "- [A](a.md) — é漢\n"
    assert len(expected.encode("utf-8")) == 22  # 16 + 2 + 3 + 1
    result = shorten_index(source, len(expected.encode("utf-8")))
    assert result.status == "shortened"
    assert result.text == expected
    assert result.output_bytes == len(expected.encode("utf-8"))
    assert result.text.encode("utf-8").decode("utf-8") == expected
    # One byte below the next character's full width leaves unused space.
    smaller = "- [A](a.md) — é\n"
    assert shorten_index(source, len(expected.encode("utf-8")) - 1).text == smaller


def test_impossible_budget_keeps_original():
    # Literal mandatory skeleton is independently encoded, never inferred from
    # the implementation's reported minimum.
    result = shorten_index(INDEX, len(SKELETON.encode("utf-8")) - 1)
    assert result.status == "cannot-fit"
    assert result.text == INDEX
    assert result.output_bytes == len(INDEX.encode("utf-8"))
    assert result.minimum_bytes == len(SKELETON.encode("utf-8"))


def test_exact_minimum_keeps_every_entry():
    result = shorten_index(INDEX, len(SKELETON.encode("utf-8")))
    assert result.status == "shortened"
    assert result.text == SKELETON


@pytest.mark.parametrize("extra", ["", "spare capacity"])
def test_fitting_input_is_unchanged(extra):
    result = shorten_index(INDEX, len((INDEX + extra).encode("utf-8")))
    assert result.status == "unchanged"
    assert result.text == INDEX


def test_shortening_is_deterministic_and_idempotent():
    expected = "- [A](a.md) — ab\n- [B](b.md) — x\n"
    source = "- [A](a.md) — abcdefgh\n- [B](b.md) — x\n"
    budget = len(expected.encode("utf-8"))
    first = shorten_index(source, budget)
    assert first.text == expected
    assert shorten_index(source, budget) == first
    assert shorten_index(first.text, budget).text == first.text


def test_nonentries_and_additional_links_are_preserved():
    protected = (
        "# Heading\r\n"
        "A [prose link](prose.md) — remains.\r\n"
        "- [Bare](bare.md)\r\n"
        "- [Extra](extra.md) — see [More](more.md) then detail\r\n"
        "- [Ref](ref.md) — see [reference][key]\r\n"
        "- [Web](web.md) — <https://example.invalid>\r\n"
        "    - [Code](code.md) — example\r\n"
        "```markdown\r\n"
        "- [Example](example.md) — example\r\n"
        "```\r\n"
        "~~~\r\n"
        "- [Tilde](tilde.md) — example\r\n"
        "~~~\r\n"
        "[key]: reference.md\r\n"
    )
    source = protected + "- [Trim](trim.md) — abcdef"
    expected = protected + "- [Trim](trim.md) — a"
    result = shorten_index(source, len(expected.encode("utf-8")))
    assert result.text == expected
    assert result.status == "shortened"


@pytest.mark.parametrize("entry", [
    r'- [Title \[literal\]](folder/topic_(detail).md "tip") — ',
    '  * [Nested [label]](../relative.md#section) — ',
    '+ [Étiquette](<relative file.md>) — ',
    '1. [Numbered](relative.md) — ',
])
def test_link_spelling_and_bullet_style_survive(entry):
    expected = entry + "é\n"
    result = shorten_index(entry + "é and much more\n", len(expected.encode("utf-8")))
    assert result.text == expected


def test_unsupported_or_malformed_entries_are_immutable():
    source = (
        "- [Bad](missing — annotation\n"
        "- [Other](other.md): unsupported delimiter\n"
        "- [Unclosed](other.md)\n"
    )
    result = shorten_index(source, len(source.encode("utf-8")) - 1)
    assert result.text == source
    assert result.status == "cannot-fit"


@pytest.mark.parametrize("budget", [-1, 1.5, True, "10"])
def test_budget_must_be_a_nonnegative_integer(budget):
    with pytest.raises((TypeError, ValueError)):
        shorten_index(INDEX, budget)


def test_empty_index_accepts_zero_budget():
    result = shorten_index("", 0)
    assert result.status == "unchanged"
    assert result.text == ""
    assert result.minimum_bytes == 0


@pytest.mark.parametrize("cannot_fit", [False, True])
def test_cli_dry_run_writes_no_files(tmp_path, cannot_fit):
    source = "- [A](a.md) — é漢🙂\r\n"
    expected = "- [A](a.md) — é\r\n"
    index = tmp_path / "index.md"
    index.write_bytes(source.encode("utf-8"))
    budget = 0 if cannot_fit else len(expected.encode("utf-8"))
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    run = subprocess.run(
        [sys.executable, str(SCRIPT), str(index), "--dry-run", "--byte-budget", str(budget)],
        capture_output=True, text=True, cwd=tmp_path,
    )
    assert run.returncode == (1 if cannot_fit else 0), run.stderr
    report = json.loads(run.stdout)
    assert report["status"] == ("cannot-fit" if cannot_fit else "shortened")
    assert report["text"] == (source if cannot_fit else expected)
    assert {p.name: p.read_bytes() for p in tmp_path.iterdir()} == before


@pytest.mark.parametrize("contents,budget", [(b"\xff", "10"), (b"valid", "-1")])
def test_cli_rejects_invalid_input_without_writes(tmp_path, contents, budget):
    index = tmp_path / "index.md"
    index.write_bytes(contents)
    run = subprocess.run(
        [sys.executable, str(SCRIPT), str(index), "--dry-run", "--byte-budget", budget],
        capture_output=True, text=True, cwd=tmp_path,
    )
    assert run.returncode == 2
    assert run.stdout == ""
    assert run.stderr
    assert index.read_bytes() == contents
    assert list(tmp_path.iterdir()) == [index]


@pytest.mark.parametrize("entry", [
    '- [A](a.md "title ) — mandatory") — ',
    "- [A](a.md 'title ) — mandatory') — ",
    '- [A](<folder/a) — b.md> "title") — ',
])
def test_delimiters_in_destination_and_title_are_preserved(entry):
    expected = entry + "a\n"
    result = shorten_index(entry + "abcdef\n", len(expected.encode("utf-8")))
    assert result.text == expected
    minimum = len((entry + "\n").encode("utf-8"))
    assert result.minimum_bytes == minimum
    impossible = shorten_index(entry + "abcdef\n", minimum - 1)
    assert impossible.status == "cannot-fit"
    assert impossible.text == entry + "abcdef\n"


@pytest.mark.parametrize("protected", [
    '---\nsummary: example\n- [Data](data.md) — keep metadata\n---\n',
    '<!--\n\n- [Comment](comment.md) — keep example\n-->\n',
    '<pre>\n\n- [Code](code.md) — keep example\n</pre>\n',
    '<div>\n- [Markup](markup.md) — keep example\n</div>\n\n',
])
def test_metadata_and_html_blocks_are_not_entries(protected):
    expected = protected + '- [A](a.md) — a\n'
    source = protected + '- [A](a.md) — abcdef\n'
    result = shorten_index(source, len(expected.encode("utf-8")))
    assert result.text == expected
