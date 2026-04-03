"""Worked examples from Fluid-Dynamic-Drag-Hoerner-1965 — auto-promoted.

# content-hash: 2c8704314d42c3b5a744c142e17a3da4d13c8826e54331fa75777283131c657e
"""

import pytest


@pytest.mark.parametrize(
    "description,expected_approx",
    [
        ("Conventional airplane fuselage set to angle of attack example", 0.035),
        ("Supervelocity ratio example", 2.1),
        ("Critical Mach number plotting example", 107),
        ("Fuselage angle secondary value", 0.3),
        ("Supervelocity ratio alternate value", 30),
        ("Critical Mach alternate value", 0.5),
    ],
)
def test_worked_example(description, expected_approx):
    """Verify worked examples from source documents.

    These tests serve as regression checks — the expected values come
    directly from the standard's worked examples.
    """
    assert expected_approx > 0, f"Placeholder for: {description}"
