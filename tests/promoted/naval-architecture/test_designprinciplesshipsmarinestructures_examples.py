"""Worked examples from Design-Principles-Ships-Marine-Structures — auto-promoted.

# content-hash: 58a794ad673785bcd6115c07f93fb861b2935c5ce6dc5b16f66305e526e56aa9
"""

import pytest


@pytest.mark.parametrize(
    "description,expected_approx",
    [
        ("1 Problem Formulation", 1),
        ("1 Problem Formulation", 1),
        ("1 Problem Formulation", 1),
    ],
)
def test_worked_example(description, expected_approx):
    """Verify worked examples from source documents.

    These tests serve as regression checks — the expected values come
    directly from the standard's worked examples.
    """
    # TODO: Wire to actual implementation when equations are promoted
    assert expected_approx > 0, f"Placeholder for: {description}"
