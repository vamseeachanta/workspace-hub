# Domain Notes: WRK-1381

- GZ curves represent righting arm versus heel angle and are used for intact-stability
  validation and IMO criteria checks.
- The existing `digitalmodel` implementation already supports cross-curve correction:
  `GZ = KN - KG * sin(heel)`.
- Current test coverage is centered on DDG-51 and one generic tanker condition.
- The core engineering risk is data-quality and schema ambiguity, not missing solver logic.
- The likely value path is:
  1. define canonical curve-fixture schema,
  2. expand condition coverage,
  3. align dedicated curve fixtures with existing point-example stability tests.
