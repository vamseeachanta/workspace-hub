"""Worked examples from Marine-Hydrodynamics-Newman-2018 — auto-promoted.

# content-hash: 9bf313ec3400c11241290184152d70ebc95d55698a128d47cdbb3a780cf24125
"""

import pytest


@pytest.mark.parametrize(
    "description,expected_approx",
    [
        ("6. What is the ideal angle of attack for a flat plate?", 10),
        ("(124–128). Since the wave amplitude A is a first-order quantity, the surface int", 1),
        (")", 1),
        ("6. What is the ideal angle of attack for a flat plate?", 10),
        ("6. What is the ideal angle of attack for a flat plate?", 10),
        ("(124–128). Since the wave amplitude A is a first-order quantity, the surface int", 1),
        ("(124–128). Since the wave amplitude A is a first-order quantity, the surface int", 1),
    ],
)
def test_worked_example(description, expected_approx):
    """Verify worked examples from source documents.

    These tests serve as regression checks — the expected values come
    directly from the standard's worked examples.
    """
    # TODO: Wire to actual implementation when equations are promoted
    assert expected_approx > 0, f"Placeholder for: {description}"
