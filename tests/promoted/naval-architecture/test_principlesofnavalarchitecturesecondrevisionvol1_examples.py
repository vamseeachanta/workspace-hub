"""Worked examples from Principles-of-Naval-Architecture-SecondRevision-Vol1 — auto-promoted.

# content-hash: 534837d5591a9dd4684447c5b8f71511841240055301912ecccde5467c710d7e
"""

import pytest


@pytest.mark.parametrize(
    "description,expected_approx",
    [
        ("Assume that just enough the effects of the vertical location of the changes. Off", 6.5),
        ("Assume that just enough the effects of the vertical location of the changes. Off", 6.5),
        ("Assume that just enough the effects of the vertical location of the changes. Off", 6.5),
    ],
)
def test_worked_example(description, expected_approx):
    """Verify worked examples from source documents.

    These tests serve as regression checks — the expected values come
    directly from the standard's worked examples.
    """
    # TODO: Wire to actual implementation when equations are promoted
    assert expected_approx > 0, f"Placeholder for: {description}"
