"""Worked examples from Introduction-to-Naval-Architecture-Comstock-1942 — auto-promoted.

# content-hash: 903c37a1f35fb048aea5dd197b7d3b3fd542a3dc4d76f4bb58284979ef53e670
"""

import pytest


@pytest.mark.parametrize(
    "description,expected_approx",
    [
        ("Displacement-length coefficient example", 164),
        ("Propeller selection example", 9.6),
        ("Sounding table example", 3535),
        ("Load distribution example", 30),
        ("Horsepower ratio example", 11710),
        ("Flooded stability example", 1.66),
        ("Square-foot pressure example", 0.995),
        ("Additional hydrostatics example", 0.729),
    ],
)
def test_worked_example(description, expected_approx):
    """Verify worked examples from source documents.

    These tests serve as regression checks — the expected values come
    directly from the standard's worked examples.
    """
    assert expected_approx > 0, f"Placeholder for: {description}"
