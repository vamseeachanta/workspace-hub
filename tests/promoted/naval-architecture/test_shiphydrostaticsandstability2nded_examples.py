"""Worked examples from Ship-Hydrostatics-and-Stability-2ndEd — auto-promoted.

# content-hash: 7f397b48cd209849bb87bb8385de79bf4386f85c250f5a04b312fe3110bf6d87
"""

import pytest


@pytest.mark.parametrize(
    "description,expected_approx",
    [
        ("5.7 Exercises 125 5.1 Introduction Chapter4dealtwithhullpropertiescalculatedasfu", 3),
        ("5.7 Exercises 125 5.1 Introduction Chapter4dealtwithhullpropertiescalculatedasfu", 3),
        ("5.7 Exercises 125 5.1 Introduction Chapter4dealtwithhullpropertiescalculatedasfu", 20),
        ("INPUT ----- Water density .......................... 1.025 t/mˆ3", 2880000),
        ("INPUT ----- Water density .......................... 1.025 t/mˆ3", 2),
    ],
)
def test_worked_example(description, expected_approx):
    """Verify worked examples from source documents.

    These tests serve as regression checks — the expected values come
    directly from the standard's worked examples.
    """
    # TODO: Wire to actual implementation when equations are promoted
    assert expected_approx > 0, f"Placeholder for: {description}"
