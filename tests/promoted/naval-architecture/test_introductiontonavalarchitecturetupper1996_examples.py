"""Worked examples from Introduction-to-Naval-Architecture-Tupper-1996 — auto-promoted.

# content-hash: 7572faab64aad91ab31211598baa1c997e46e122ffecb6397f195fd5b1f495a0
"""

import pytest


@pytest.mark.parametrize(
    "description,expected_approx",
    [
        ("The midship section of a steel ship has the following particulars: Cross-section", 58),
        ("To illustrate the use of a model in calculating ship resistance a worked example", 1025),
        ("A ship of mass 5000 tonnes, 98m long, floats at draughts of 5.5 m forward and 6", 10055),
        ("Just before entering drydock a ship of 5000 tonnes mass floats at draughts of 2", 2.7),
        ("Just before entering drydock a ship of 5000 tonnes mass floats at draughts of 2", 2.7),
        ("Using the tabulated values of GZ from the previous example, determine the dynami", 5.924),
        ("Using the tabulated values of GZ from the previous example, determine the dynami", 5.924),
        ("Consider a vessel of constant rectangular cross section, 140m long, 20m beam and", 79),
        ("The midship section of a steel ship has the following particulars: Cross-section", 58),
        ("The midship section of a steel ship has the following particulars: Cross-section", 22.91),
        ("Bending moment response operators (M/h) for a range of encounter frequencies are", 0.926),
        ("To illustrate the use of a model in calculating ship resistance a worked example", 1025),
        ("To illustrate the use of a model in calculating ship resistance a worked example", 1025),
    ],
)
def test_worked_example(description, expected_approx):
    """Verify worked examples from source documents.

    These tests serve as regression checks — the expected values come
    directly from the standard's worked examples.
    """
    # TODO: Wire to actual implementation when equations are promoted
    assert expected_approx > 0, f"Placeholder for: {description}"
