<!-- oracle_authored_by: claude-sonnet-4-6 -->
<!-- oracle_review_method: from-source -->
<!-- oracle_authored_at: 2026-04-25T00:00:00Z -->
<!-- oracle_second_reviewer: self-reviewed-with-24h-delay -->
<!-- oracle_reviewed_at: 2026-04-26T00:00:00Z -->
<!-- single_reviewer_timelag: true -->
<!-- source: https://www.orcina.com/webhelp/OrcaFlex/Content/Connectors.htm -->

# Connectors

Connectors model flexible joints and clamps between line segments and objects.

## Connector Types

| Type | DOF | Stiffness | Damping | Application |
|---|---|---|---|---|
| Ball joint | 3R | None | Optional | Flexible riser base |
| Flex joint | 3R | Rotational | Rotational | Stress joint |
| Link | 1T | Axial | Axial | Chain stopper |
| Winch | 1T | None | None | Active tensioning |

## Stiffness Matrix

The full 6x6 stiffness matrix can be specified for general connectors.

### Coupled Terms

| Term | Coupling | Units |
|---|---|---|
| K11 | Surge-Surge | kN/m |
| K22 | Sway-Sway | kN/m |
| K44 | Roll-Roll | kNm/rad |
