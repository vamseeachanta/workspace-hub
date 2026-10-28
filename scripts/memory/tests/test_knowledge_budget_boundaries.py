"""Independent byte-boundary examples for shared knowledge under context pressure.

Policy citation: docs/plans/2026-07-14-issue-3532-cross-provider-memory-budget.md,
Pseudocode: reserve header and maximum-count marker; allocate 15% institutional,
50% operational, context remainder; spill unused bytes in original source order.
Supported caps are 2000 and 7000 bytes (same document, production-cap paragraph).
The literal wire format below cites curate_readback_slice.py, _HEADER and
_omitted_marker; no expected budget or membership uses its private helpers.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "curate_readback_slice.py"
SPEC = importlib.util.spec_from_file_location("knowledge_budget_curator", MODULE_PATH)
curator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = curator
SPEC.loader.exec_module(curator)

# Header UTF-8 segments: 5 + 11 + 24 + 5 + 18 + 15 + 23 + 6 = 107 bytes.
# The em dash contributes three bytes; all other header characters are ASCII.
HEADER = (
    "<!-- MANAGED by curate_readback_slice.py — do not hand-edit; "
    "regenerate via bridge-hermes-claude.sh -->\n\n"
)
# Ten synthetic context rows plus one knowledge bullet = eleven candidates.
# Marker reserve: 2 ("_[") + 2 ("11") + 9 (" entries ") + 9 ("omitted: ")
# + 17 ("oversize/over-cap") + 2 ("]_") + 1 newline = 42 ASCII bytes.
# Actual one-digit plural markers take 41 bytes.
RESERVED_MARKER = "_[11 entries omitted: oversize/over-cap]_\n"


@pytest.fixture(
    params=[
        # Hand calculation, cap 2000: usable = 2000 - 107 - 42 = 1851;
        # institutional = floor(1851 * 15 / 100) = 277;
        # operational = floor(1851 * 50 / 100) = 925; context = 649.
        # Exact: context first packs 2 * 300; spill = 1851 - 277 - 600
        # = 974, adding 3 rows: 5 retained, 5 omitted, 74 bytes unused.
        # Over: no knowledge fits; spill = 1851 - 600 = 1251, adding
        # 4 rows: 6 retained, 5 omitted, 51 bytes unused < 278.
        # Output: exact 107 + 1500 + 277 + 41 = 1925 bytes;
        # over 107 + 1800 + 41 = 1948 bytes.
        (2000, 300, 277, 5, 6, 1925, 1948),
        # Hand calculation, cap 7000: usable = 7000 - 107 - 42 = 6851;
        # institutional = floor(6851 * 15 / 100) = 1027;
        # operational = floor(6851 * 50 / 100) = 3425; context = 2399.
        # Exact: context first packs 1 * 1200; spill = 6851 - 1027 - 1200
        # = 4624, adding 3 rows: 4 retained, 6 omitted, 1024 bytes unused.
        # Over: spill = 6851 - 1200 = 5651, adding 4 rows:
        # 5 retained, 6 omitted, 851 bytes unused < 1028.
        # Output: exact 107 + 4800 + 1027 + 41 = 5975 bytes;
        # over 107 + 6000 + 41 = 6148 bytes.
        (7000, 1200, 1027, 4, 5, 5975, 6148),
    ],
    ids=["small-production-cap", "large-production-cap"],
)
def pressure_case(request, tmp_path):
    cap, row_bytes, reserved_bytes, exact_rows, over_rows, exact_size, over_size = request.param
    # Synthetic row: 27 ASCII prefix bytes + 5 for " — " + newline = 33.
    # Thus 267 or 1167 ASCII padding bytes make a 300- or 1200-byte row.
    rows = [
        f"- [Context {index}](context_{index}.md) — " + "x" * (row_bytes - 33) + "\n"
        for index in range(10)
    ]
    # Bullet: 2 ASCII prefix bytes + 2 per é + newline = 3 + 2*n.
    # n = 137 or 512 gives 277 or 1027 bytes; one ASCII z adds one byte.
    exact = "- " + "é" * ((reserved_bytes - 3) // 2) + "\n"
    over = exact.removesuffix("\n") + "z\n"
    assert len(HEADER.encode("utf-8")) == 107
    assert len(RESERVED_MARKER.encode("utf-8")) == 42
    assert all(len(row.encode("utf-8")) == row_bytes for row in rows)
    assert len("".join(rows).encode("utf-8")) > cap
    assert len(exact.encode("utf-8")) == reserved_bytes
    assert len(over.encode("utf-8")) == reserved_bytes + 1

    source = tmp_path / "memory"
    source.mkdir()
    auto = source / "claude-auto-memory.md"
    auto.write_text("".join(rows), encoding="utf-8")
    return source, rows, exact, over, cap, exact_rows, over_rows, exact_size, over_size


def test_multibyte_knowledge_exact_budget(pressure_case):
    source, rows, exact, _, cap, retained, _, expected_size, _ = pressure_case
    (source / "KNOWLEDGE.md").write_text(exact, encoding="utf-8")
    # Eleven candidates minus retained context rows minus the knowledge bullet.
    omitted = 11 - retained - 1
    marker = f"_[{omitted} entries omitted: oversize/over-cap]_\n"
    expected = HEADER + "".join(rows[:retained]) + exact + marker
    output = curator.curate(source, "hermes", cap, priority_slugs=())
    assert output == expected
    assert exact in output.splitlines(keepends=True)
    assert len(output.encode("utf-8")) == expected_size <= cap


def test_multibyte_knowledge_over_budget_preserves_entry_boundaries(pressure_case):
    source, rows, _, over, cap, _, retained, _, expected_size = pressure_case
    (source / "KNOWLEDGE.md").write_text(over, encoding="utf-8")
    # Eleven candidates minus retained context rows; knowledge is wholly omitted.
    omitted = 11 - retained
    marker = f"_[{omitted} entries omitted: oversize/over-cap]_\n"
    expected = HEADER + "".join(rows[:retained]) + marker
    output = curator.curate(source, "hermes", cap, priority_slugs=())
    assert output == expected
    assert "é" not in output  # no fragment of the oversize knowledge entry
    assert len(output.encode("utf-8")) == expected_size <= cap


def test_knowledge_pressure_provider_parity_and_idempotence(pressure_case):
    source, rows, exact, over, cap, exact_rows, over_rows, exact_size, over_size = pressure_case
    # Repeat each boundary case across all supported targets at equal caps.
    for bullet, retained, size, included in (
        (exact, exact_rows, exact_size, True),
        (over, over_rows, over_size, False),
    ):
        (source / "KNOWLEDGE.md").write_text(bullet, encoding="utf-8")
        before = {path.name: path.read_bytes() for path in source.iterdir()}
        omitted = 11 - retained - int(included)
        expected = (
            HEADER + "".join(rows[:retained]) + (bullet if included else "")
            + f"_[{omitted} entries omitted: oversize/over-cap]_\n"
        ).encode("utf-8")
        assert len(expected) == size <= cap
        for target in ("codex", "hermes", "gemini"):
            for _ in range(2):  # independent repeat to detect generation side effects
                output = curator.curate(source, target, cap, priority_slugs=())
                assert output.encode("utf-8") == expected
                assert {path.name: path.read_bytes() for path in source.iterdir()} == before
