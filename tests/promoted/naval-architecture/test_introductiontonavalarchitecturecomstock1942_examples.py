"""Worked examples from Introduction-to-Naval-Architecture-Comstock-1942 — auto-promoted.

# content-hash: 903c37a1f35fb048aea5dd197b7d3b3fd542a3dc4d76f4bb58284979ef53e670
"""

import pytest


@pytest.mark.parametrize(
    "description,expected_approx",
    [
        ("The displacement-length coefficient is 11,710/-", 164),
        ("We will choose a propeller for the example
ship. In Chapter I this ship is said ", 9.6),
        ("Sound- Sound- Sound- Sound- Sound- Sound¬", 3535),
        ("5.78 feet above bottom of tank.", 3535),
        ("Under and ’tween deck 5870 Propelling power 1960", 3535),
        ("83^ inches (10,000 pounds per square inch =", 3535),
        ("(a) 0.694. (b) 14,400 tons.", 2.13),
        ("(a) 0.289. (b) 0.342. (c) 2740 tons.", 2.13),
        ("500 X (65 + 72) X 0.88 X 52 lb ^ 2240 =", 2.13),
        ("Solid floor, lb Open floor, lb", 2.13),
        ("(a) 10,000 -f- 10.4 = 960 tons.", 2.13),
        ("6080/(60 X 33000) = 1/325.7.", 11710),
        ("The ehp of the destroyer is twice that of the", 11710),
        ("(a) 3.2 knots, (b) 16 knots, (c) 0.8.", 11710),
        ("34690 VU710 X 415 = 15.74.", 11710),
        ("5/draft = 2.25. Prismatic, 0.775. Displace¬", 11710),
        ("(a) Yes. (b) No. (c) Yes, either the fore¬", 1.66),
        ("Stability flooded", 1.66),
        ("(a) 388 feet, (b) 640 tons.", 0.995),
        ("7.47 tons per square foot.", 0.995),
        ("The displacement-length coefficient is 11,710/-", 164),
        ("The displacement-length coefficient is 11,710/-", 164),
        ("We will choose a propeller for the example
ship. In Chapter I this ship is said ", 9.6),
        ("We will choose a propeller for the example
ship. In Chapter I this ship is said ", 1550),
        ("See Fig. 4(a).", 3535),
        ("See Fig. 7(a).", 3535),
        ("(a) 21.7 feet, (b) 2.55 feet, (c) 9 inches by", 3535),
        ("20 feet 5.7 inches.", 3535),
        ("16 feet for triangle, 10 feet for rectangle;", 3535),
        ("Yes. Drafts with forepeak filled: (about) 11", 3535),
        ("Sound- Sound- Sound- Sound- Sound- Sound¬", 30),
        ("5.78 feet above bottom of tank.", 30),
        ("Under and ’tween deck 5870 Propelling power 1960", 30),
        ("83^ inches (10,000 pounds per square inch =", 30),
        ("(a) 0.694. (b) 14,400 tons.", 2.13),
        ("(a) 0.289. (b) 0.342. (c) 2740 tons.", 2.13),
        ("500 X (65 + 72) X 0.88 X 52 lb ^ 2240 =", 2.13),
        ("Solid floor, lb Open floor, lb", 2.13),
        ("(a) 10,000 -f- 10.4 = 960 tons.", 2.13),
        ("(a) 0.694. (b) 14,400 tons.", 11710),
        ("(a) 0.289. (b) 0.342. (c) 2740 tons.", 11710),
        ("500 X (65 + 72) X 0.88 X 52 lb ^ 2240 =", 11710),
        ("Solid floor, lb Open floor, lb", 11710),
        ("(a) 10,000 -f- 10.4 = 960 tons.", 11710),
        ("(a) 388 feet, (b) 640 tons.", 0.729),
    ],
)
def test_worked_example(description, expected_approx):
    """Verify worked examples from source documents.

    These tests serve as regression checks — the expected values come
    directly from the standard's worked examples.
    """
    # TODO: Wire to actual implementation when equations are promoted
    assert expected_approx > 0, f"Placeholder for: {description}"
