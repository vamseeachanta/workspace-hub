# GT1R R35 Parachute Frame — Geometry Dimensions (WRK-1360)

> **Edit this file** to refine dimensions. Once finalized, coordinates will be
> regenerated from these values into `frame_geometry_3d.py`.

## Coordinate System

- **X** = transverse (+ right, − left), centered on vehicle centerline
- **Y** = longitudinal (+ forward, − rearward)
- **Z** = vertical (+ up)
- **Origin** = coupler pin (N5), center of rear trunk frame

## Assembly 1: Rear Trunk Frame (sketch page 1 + photos)

### Parachute Arm (from chute attachment to coupler pin)

| Parameter | Value | Unit | Confidence | Source | Notes |
|-----------|-------|------|------------|--------|-------|
| arm_length | 12.0 | in | low | photo estimate | N6→N5, Y-direction. Revised down from 18" based on bracket closeup |
| arm_z | -7.25 | in | high | sketch | Arm and coupler pin sit 7.25" below horizontal bar |

### Coupler Pin (N5) — V-strut convergence point

| Parameter | Value | Unit | Confidence | Source | Notes |
|-----------|-------|------|------------|--------|-------|
| coupler_x | 0.0 | in | high | symmetry | Centered on vehicle |
| coupler_y | 0.0 | in | — | origin | Reference point |
| coupler_z | -7.25 | in | high | sketch "7.25" | Below horizontal bar |

### Horizontal Bar (symmetric about X=0)

| Parameter | Value | Unit | Confidence | Source | Notes |
|-----------|-------|------|------------|--------|-------|
| bar_total_width | 36.0 | in | high | sketch 6+12+12+6 | Full transverse span |
| outer_segment | 6.0 | in | high | sketch | N0→N1 and N3→N4 (end stubs to frame rail mounts) |
| inner_segment | 12.0 | in | high | sketch | N1→N2 and N2→N3 (strut junction to center bolt) |
| bar_z | 0.0 | in | — | reference | Bar defines Z=0 plane |

### Node Positions (rear trunk, from centerline)

| Node | X | Y | Z | Label | Connection | BC |
|------|---|---|---|-------|------------|----|
| N0 | -18.0 | 0.0 | 0.0 | left C3 mount | C3 weld | fixed |
| N1 | -12.0 | 0.0 | 0.0 | left strut junction | C0 weld | free |
| N2 | 0.0 | 0.0 | 0.0 | center bolt | C1 bolt+pin | free (shear) |
| N3 | +12.0 | 0.0 | 0.0 | right strut junction | C0 weld | free |
| N4 | +18.0 | 0.0 | 0.0 | right C3 mount | C3 weld | fixed |
| N5 | 0.0 | 0.0 | -7.25 | coupler pin | double pin | free |
| N6 | 0.0 | -12.0 | -7.25 | parachute bracket | bracket | free |

### V-Struts

| Parameter | Value | Unit | Notes |
|-----------|-------|------|-------|
| v_strut_length | 14.02 | in | Computed: √(12² + 7.25²) |
| v_strut_left | N1→N5 | — | Left junction to coupler pin |
| v_strut_right | N3→N5 | — | Right junction to coupler pin |

## Assembly 2: Under-Hood Frame (sketch page 2)

> **Not symmetric** — single bar assembly on one side of engine bay.

### Dimensions

| Parameter | Value | Unit | Confidence | Source | Notes |
|-----------|-------|------|------------|--------|-------|
| hood_fwd_offset | 60.0 | in | low | estimate | Forward of trunk bar — no sketch dimension |
| hood_z_elevation | 12.0 | in | low | estimate | Above trunk bar — no sketch dimension |
| hood_bar_main | 14.0 | in | medium | sketch "14" | N7→N8 horizontal bar |
| hood_bar_end_horiz | 5.0 | in | medium | sketch "5" | N8→N9 horizontal component |
| hood_bar_end_drop | 1.0 | in | medium | sketch "1" | N8→N9 vertical drop |
| curved_arm_fwd | 8.0 | in | medium | sketch "8" | N8→N10 (modeled straight, should be 150° arc) |
| curved_arm_angle | 150 | deg | medium | sketch "150° eth" | Not yet modeled as arc |

### Node Positions (under-hood)

| Node | X | Y | Z | Label | Connection | BC |
|------|---|---|---|-------|------------|----|
| N7 | -18.0 | 60.0 | 12.0 | hood bar left | C2 weld | free |
| N8 | -4.0 | 60.0 | 12.0 | hood bar right | C2 weld | free |
| N9 | 1.0 | 60.0 | 11.0 | B1 bolted | B1 (6 bolts) | bolted |
| N10 | -4.0 | 68.0 | 12.0 | P1 pinned | P1 | pinned |

## Tube Properties (all members)

| Parameter | Value | Unit | Confidence | Notes |
|-----------|-------|------|------------|-------|
| tube_od | 1.5 | in | medium | Sketch side view "1.5 (H)" |
| tube_wall | 0.120 | in | low | Assumed — pending client measurements |
| material | 4130 chromoly | — | high | Known from client |
| tube_cl | 12.0 | in | medium | Sketch side view "12 CL" |

## Bolt Properties

| Parameter | Value | Unit | Notes |
|-----------|-------|------|-------|
| b1_bolt_size | 5/8 | in | Sketch annotation, 6 bolts at B1 |

## Frame Rails (connecting assemblies)

| Member | From | To | Notes |
|--------|------|----|-------|
| frame_rail_left | N0 | N7 | Left C3 mount to hood bar left |
| frame_rail_right | N4 | N8 | Right C3 mount to hood bar right |

## Items for Client Clarification

1. Tube wall thickness — 0.120" assumed, needs confirmation
2. Parachute arm length — 12" estimated from photos
3. Under-hood frame position relative to trunk (hood_fwd_offset, hood_z_elevation)
4. Curved member — is 150° the included angle or the bend angle?
5. Frame rail path — straight line or follows vehicle body contour?
