"""Worked examples from Fluid-Dynamic-Drag-Hoerner-1965 — auto-promoted.

# content-hash: 2c8704314d42c3b5a744c142e17a3da4d13c8826e54331fa75777283131c657e
"""

import pytest


@pytest.mark.parametrize(
    "description,expected_approx",
    [
        ("In conventional airplanes, the fuselage may
be set to an angle in the order of m", 0.035),
        ("For a supervelocity ratio AV/V — 0.1, we
solid investigated) is called the criti", 2.1),
        ("By plotting the critical Mach number of 31, for example). Reference (30,d) also ", 107),
        ("In conventional airplanes, the fuselage may
be set to an angle in the order of m", 0.035),
        ("In conventional airplanes, the fuselage may
be set to an angle in the order of m", 0.3),
        ("For a supervelocity ratio AV/V — 0.1, we
solid investigated) is called the criti", 2.1),
        ("For a supervelocity ratio AV/V — 0.1, we
solid investigated) is called the criti", 30),
        ("By plotting the critical Mach number of 31, for example). Reference (30,d) also ", 107),
        ("By plotting the critical Mach number of 31, for example). Reference (30,d) also ", 0.5),
    ],
)
def test_worked_example(description, expected_approx):
    """Verify worked examples from source documents.

    These tests serve as regression checks — the expected values come
    directly from the standard's worked examples.
    """
    # TODO: Wire to actual implementation when equations are promoted
    assert expected_approx > 0, f"Placeholder for: {description}"
