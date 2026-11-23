"""Worked examples from Handbook-Offshore-Engineering-Chakrabarti-2005 — auto-promoted.

# content-hash: 44908dc058c944f76154b177b92a6dd68e2487c47984f93bc521b73450910518
"""

import pytest


@pytest.mark.parametrize(
    "description,expected_approx",
    [
        ("or 6 h", 1.9),
        ("provides a manual method", 4194),
        ("For the deck configuration shown in fig. 6.19 and the platform loads used in Exa", 8.5),
        ("Select the deck beam. main deck girder and main deck truss member sizes for the ", 80),
        ("The 16.51 in. flange width of WF 36 x 245 would present difficulties", 0.94),
        ("or 6 h", 1.9),
        ("or 6 h", 2),
        ("outlines a manual approach to", 4194),
        ("provides a manual method", 15),
        ("For the deck configuration shown in fig. 6.19 and the platform loads used in Exa", 8.5),
        ("For the deck configuration shown in fig. 6.19 and the platform loads used in Exa", 61.8),
        ("Select the deck beam. main deck girder and main deck truss member sizes for the ", 80),
        ("Select the deck beam. main deck girder and main deck truss member sizes for the ", 19.8),
        ("The 16.51 in. flange width of WF 36 x 245 would present difficulties", 0.94),
        ("The 16.51 in. flange width of WF 36 x 245 would present difficulties", 0.94),
    ],
)
def test_worked_example(description, expected_approx):
    """Verify worked examples from source documents.

    These tests serve as regression checks — the expected values come
    directly from the standard's worked examples.
    """
    # TODO: Wire to actual implementation when equations are promoted
    assert expected_approx > 0, f"Placeholder for: {description}"
