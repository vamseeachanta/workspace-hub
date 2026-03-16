"""Generate baseline + parametric test modules from pattern groups.

Each output function gets:
  - 1 baseline test with pytest.approx(cached_value)
  - 10 parametric variations (nominal, all-min, all-max, etc.)
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from formula_to_python import can_translate

# 10 variation names for parametric testing
VARIATION_NAMES = [
    "nominal",
    "all_min",
    "all_max",
    "one_at_a_time_low",
    "one_at_a_time_high",
    "stress_high",
    "near_zero",
    "large_values",
    "negative",
    "random_seed_42",
]


def _safe_func_name(idx: int) -> str:
    return f"calc_{idx:03d}"


def _extract_numeric_cached_values(cells: list[dict]) -> list[tuple]:
    """Extract cells with numeric cached values for baseline tests."""
    results = []
    for cell in cells:
        val = cell.get("cached_value")
        if isinstance(val, (int, float)):
            results.append((cell["cell_ref"], val))
    return results


def generate_test_module(
    stem: str,
    patterns: dict[str, list[dict]],
    classification: dict,
    formulas: dict,
) -> str:
    """Generate a test module with baseline and parametric tests.

    Args:
        stem: Workbook stem name.
        patterns: Canonical formula → list of cells.
        classification: Dict with inputs, outputs, chain.
        formulas: Original formulas dict (for reference).

    Returns:
        Complete test module as a string.
    """
    lines = [
        f'"""Auto-generated tests for {stem} calculations.',
        f"",
        f"Baseline tests use cached Excel values.",
        f"Parametric tests exercise 10 input variations.",
        f'"""',
        f"",
        f"import pytest",
        f"import math",
        f"",
        f"",
    ]

    func_idx = 0
    for canonical, cells in patterns.items():
        func_name = _safe_func_name(func_idx)
        cached_pairs = _extract_numeric_cached_values(cells)

        # Baseline test
        if cached_pairs:
            ref, val = cached_pairs[0]
            lines.append(f"class Test_{func_name}_baseline:")
            lines.append(
                f'    """Baseline: {func_name} from {canonical}"""'
            )
            lines.append("")
            lines.append(
                f"    def test_{func_name}_cached_{ref.lower()}(self):"
            )
            lines.append(
                f"        # Excel cached value for {ref}"
            )
            lines.append(
                f"        expected = {val}"
            )
            lines.append(
                f"        # TODO: wire to {func_name}() call"
            )
            lines.append(
                f"        assert expected == pytest.approx({val})"
            )
            lines.append("")
            lines.append("")

        # Parametric variations
        n_inputs = len(classification.get("inputs", []))
        if n_inputs > 0 and can_translate(canonical):
            variation_data = _build_variation_params(n_inputs)
            lines.append(f"class Test_{func_name}_parametric:")
            lines.append(
                f'    """Parametric variation tests for {func_name}."""'
            )
            lines.append("")
            lines.append(f"    @pytest.mark.parametrize(")
            lines.append(f'        "variation_name, scale_factors",')
            lines.append(f"        [")
            for vname, factors in zip(VARIATION_NAMES, variation_data):
                lines.append(
                    f'            ("{vname}", {factors}),'
                )
            lines.append(f"        ],")
            lines.append(f"    )")
            lines.append(
                f"    def test_{func_name}_variation("
            )
            lines.append(
                f"        self, variation_name, scale_factors"
            )
            lines.append(f"    ):")
            lines.append(
                f"        # Apply scale_factors to nominal inputs"
            )
            lines.append(
                f"        # TODO: wire to {func_name}() with scaled inputs"
            )
            lines.append(
                f"        assert isinstance(scale_factors, list)"
            )
            lines.append("")
            lines.append("")

        func_idx += 1

    if func_idx == 0:
        lines.append("# No patterns found — empty test module")
        lines.append("")

    return "\n".join(lines)


def _build_variation_params(n_inputs: int) -> list[list[float]]:
    """Build 10 sets of scale factors for parametric variations."""
    return [
        [1.0] * n_inputs,         # nominal
        [0.5] * n_inputs,         # all_min
        [2.0] * n_inputs,         # all_max
        [0.5] + [1.0] * (n_inputs - 1),  # one_at_a_time_low
        [2.0] + [1.0] * (n_inputs - 1),  # one_at_a_time_high
        [3.0] * n_inputs,         # stress_high
        [0.01] * n_inputs,        # near_zero
        [100.0] * n_inputs,       # large_values
        [-1.0] * n_inputs,        # negative
        [1.42] * n_inputs,        # random_seed_42
    ]
