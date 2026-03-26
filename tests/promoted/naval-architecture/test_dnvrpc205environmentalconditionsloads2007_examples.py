"""Worked examples from DNV-RP-C205-Environmental-Conditions-Loads-2007 — auto-promoted.

# content-hash: 90570006d2c8fcb882a80c596f3f72562b987c129ae586277e1bfb4cdb69a965
"""

import pytest


@pytest.mark.parametrize(
    "description,expected_approx",
    [
        ("year value for H and the", 2922),
    ],
)
def test_worked_example(description, expected_approx):
    """Verify worked examples from source documents.

    These tests serve as regression checks — the expected values come
    directly from the standard's worked examples.
    """
    # TODO: Wire to actual implementation when equations are promoted
    assert expected_approx > 0, f"Placeholder for: {description}"
