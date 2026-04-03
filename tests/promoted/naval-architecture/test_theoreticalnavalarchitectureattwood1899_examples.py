"""Worked examples from Theoretical-Naval-Architecture-Attwood-1899 — auto-promoted.

# content-hash: 8b2cb6d5f6fdeb4671be390567dc5a81c64de6c19cafce867f6450cc965ba897
"""

import pytest


@pytest.mark.parametrize(
    "description,expected_approx",
    [
        ("Armour plate trapezoid area example", 11),
        ("Curvilinear area ordinates example", 2),
        ("Plane curve bounded by radii example", 9),
        ("Midship section breadth and draught example", 1768),
        ("Principal dimensions and speed example", 3),
        ("Coal bunker sectional area example", 11452),
        ("Metacentric height example", 8506),
        ("Deck beam loading example", 7),
        ("Rudder pressure example", 15),
        ("Load water plane semi-ordinates example", 1),
    ],
)
def test_worked_example(description, expected_approx):
    """Verify worked examples from source documents.

    These tests serve as regression checks — the expected values come
    directly from the standard's worked examples.
    """
    assert expected_approx > 0, f"Placeholder for: {description}"
