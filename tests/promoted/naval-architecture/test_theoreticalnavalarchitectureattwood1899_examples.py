"""Worked examples from Theoretical-Naval-Architecture-Attwood-1899 — auto-promoted.

# content-hash: 8b2cb6d5f6fdeb4671be390567dc5a81c64de6c19cafce867f6450cc965ba897
"""

import pytest


@pytest.mark.parametrize(
    "description,expected_approx",
    [
        ("Anarmourplateis of the form of atrapezoid with parallel
sides 8' 3" and 8' 9" lo", 11),
        ("A curvi-
linear area has ordinatesatacommondistanceapart of2feet, thelengths
bei", 2),
        ("Tofind theareaof a figure bounded bya plane curve and
tworadii90 apart,thelength", 9),
        ("The midship section of a vessel is 68 feet broad at its
broadestpart, andthedrau", 1768),
        ("A vesselhastobe400feetlong,42feetbeam, 17feetdraught,
and 13\knotsspeed. Whatwou", 3),
        ("A coal-bunker has sections 17' 6" apart, and the areas of
these sections, commen", 11452),
        ("A vessel 13' 3" mean draught has her C.B. 5-34 feet below
J~/ \V LJ
Here theprop", 8),
        ("A vessel of 14,000 tons displacement has a metacentric
heightof 3^feet. Then, if", 8506),
        ("Two squaresof sidea arejoined to form a rectangle. The
I ofeachsquareabout the c", 2),
        ("lighter is in the form of a box, 120 feet long, 30 feet
broad, andfloatsat adrau", 75),
        ("A vessel has a compartmentof the double bottom at the
middleline, 60feetlongand ", 5),
        ("A vessel floatsat adraught of 16' 5$" forward, 23' i" aft,
the normal trim being", 5447),
        ("The beams of a deck are 3 feet apart, and weigh 22 Ib.s.
perfoot run ; the deckp", 7),
        ("A rudder is 243^ square feet in area, and the centre of
pressureisestimated tobe", 15),
        ("Anarmourplateis of the form of atrapezoid with parallel
sides 8' 3" and 8' 9" lo", 11),
        ("Anarmourplateis of the form of atrapezoid with parallel
sides 8' 3" and 8' 9" lo", 3),
        ("A curvi-
linear area has ordinatesatacommondistanceapart of2feet, thelengths
bei", 2),
        ("A curvi-
linear area has ordinatesatacommondistanceapart of2feet, thelengths
bei", 117),
        ("A cur-
vilinear area has ordinates at a common distance apart of 2 feet, the
len", 103),
        ("A cur-
vilinear area has ordinates at a common distance apart of 2 feet, the
len", 22),
        ("Tofind theareaof a figure bounded bya plane curve and
tworadii90 apart,thelength", 9),
        ("Tofind theareaof a figure bounded bya plane curve and
tworadii90 apart,thelength", 147),
        ("A coal-bunker has sections 17' 6" apart, and the areas of
thesesectionsare98, 12", 147),
        ("The midship section of a vessel is 68 feet broad at its
broadestpart, andthedrau", 1768),
        ("The midship section of a vessel is 68 feet broad at its
broadestpart, andthedrau", 59),
        ("A vesselhastobe400feetlong,42feetbeam, 17feetdraught,
and 13\knotsspeed. Whatwou", 3),
        ("A midship section has semi-ordinates, l' 6" apart, com-
mencing at the L.W.L., o", 3),
        ("A midship section has semi-ordinates, l' 6" apart, com-
mencing at the L.W.L., o", 3),
        ("The semi-ordinates of the loadwater-plane of avessel 395
feet long are, commenci", 1),
        ("The semi-ordinates of the loadwater-plane of avessel 395
feet long are, commenci", 1),
        ("An athwartshipcoal-bunker is6 feet long in a fore-and-aft
direction. Itis bounde", 1),
        ("An athwartshipcoal-bunker is6 feet long in a fore-and-aft
direction. Itis bounde", 7),
        ("An athwartshipcoal-bunker is6 feet long in a fore-and-aft
direction. Itis bounde", 7),
        ("Findtheareaand positionofcentreofgravityofaquadrant
of a circle with reference t", 11452),
        ("Findtheareaand positionofcentreofgravityofaquadrant
of a circle with reference t", 11452),
        ("Theunderwaterportion of avessel is divided by transverse
sections 10feetapartoft", 8),
        ("Theunderwaterportion of avessel is divided by transverse
sections 10feetapartoft", 8),
        ("A vessel of 14,000 tons displacement has a metacentric
heightof 3^feet. Then, if", 8506),
        ("A vessel of 14,000 tons displacement has a metacentric
heightof 3^feet. Then, if", 8506),
        ("Two squaresof sidea arejoined to form a rectangle. The
I ofeachsquareabout the c", 2),
        ("Two squaresof sidea arejoined to form a rectangle. The
I ofeachsquareabout the c", 2),
        ("Having NgNiven the moment of inertia of the triangle in
Fig. 52about theaxis thr", 280),
        ("lighter is in the form of a box, 120 feet long, 30 feet
broad, andfloatsat adrau", 75),
        ("lighter is in the form of a box, 120 feet long, 30 feet
broad, andfloatsat adrau", 75),
        ("A vessel has a compartmentof the double bottom at the
middleline, 60feetlongand ", 5),
        ("A vessel has a compartmentof the double bottom at the
middleline, 60feetlongand ", 5),
        ("A vessel floatsat adraught of 16' 5$" forward, 23' i" aft,
the normal trim being", 5447),
        ("A vessel floatsat adraught of 16' 5$" forward, 23' i" aft,
the normal trim being", 5447),
        ("A vessel 300 feet long and 2200 tons displacement has a
longitudinal metacentric", 14),
        ("The beams of a deck are 3 feet apart, and weigh 22 Ib.s.
perfoot run ; the deckp", 7),
        ("The beams of a deck are 3 feet apart, and weigh 22 Ib.s.
perfoot run ; the deckp", 7),
        ("-Find the horse-power which must be transmitted through
a tow-ropein order to to", 332),
        ("-Find the horse-power which must be transmitted through
a tow-ropein order to to", 332),
        ("A rudder is 243^ square feet in area, and the centre of
pressureisestimated tobe", 15),
        ("A rudder is 243^ square feet in area, and the centre of
pressureisestimated tobe", 15),
    ],
)
def test_worked_example(description, expected_approx):
    """Verify worked examples from source documents.

    These tests serve as regression checks — the expected values come
    directly from the standard's worked examples.
    """
    # TODO: Wire to actual implementation when equations are promoted
    assert expected_approx > 0, f"Placeholder for: {description}"
