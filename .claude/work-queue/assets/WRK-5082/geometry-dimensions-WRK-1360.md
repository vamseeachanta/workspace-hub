# GT1R R35 Parachute Frame — Geometry Dimensions (WRK-1360)

> **Edit this file** to refine dimensions. Once finalized, coordinates will be
> regenerated from these values into `frame_geometry_3d.py`.

## Coordinate System

- **X** = transverse (+ right, − left), centered on vehicle centerline
- **Y** = longitudinal (+ forward, − rearward)
- **Z** = vertical (+ up)
- **Origin** = coupler pin (N5), center of rear trunk frame

### 3D Axes Convention

```
                +Z (up)
                 ↑
                 │
                 │
                 │
                 │
                 │
                 ●──────────────► +X (right)
                ╱  Origin = N5
               ╱   (coupler pin,
              ╱     center of
             ╱      rear trunk frame)
            ╱
           ↙
         +Y (forward)


    Axis    Direction          Vehicle Reference
    ────    ─────────          ─────────────────
    +X      right              passenger side
    −X      left               driver side
    +Y      forward            toward hood/engine
    −Y      rearward           toward bumper/chute
    +Z      up                 toward roof
    −Z      down               toward ground
```

### Plan View (top-down, X-Y plane)

```
                         +Y (forward)
                           ↑
                           │
              ┌────────────┼────────────┐
             ╱│            │            │╲
            ╱ │   HOOD     │            │ ╲
           ╱  │            │            │  ╲
          │   │  Assembly 2│(GT1R kit)  │   │
          │   │   under-   │            │   │
          │   │    hood    │            │   │
          │   ├────────────┼────────────┤   │
          │   │            │            │   │
          │   │  CABIN     │            │   │
          │   │            │            │   │
          │   │            │            │   │
          │   ├────────────┼────────────┤   │
          │   │            │            │   │
 -X ◄─────┼───┤  TRUNK    ●(N5 origin) ├───┼─────► +X
  (left)  │   │  Assembly 1│(custom wld)│   │  (right)
          │   │            │            │   │
          │   │   N0●━━━━━━●━━━━━━●N4   │   │
          │   │            │            │   │
           ╲  │            │            │  ╱
            ╲ └────────────┼────────────┘ ╱
             ╲─────────────┼─────────────╱
                           │
                           ● N6 (parachute)
                           │
                           ↓
                         -Y (rearward)
```

### Side View (right side, Y-Z plane)

```
                  +Z (up)
                    ↑
                    │
                    │         ╱╲
                    │        ╱  ╲  windshield
                    │   ____╱    ╲________
                    │  │roof              │trunk lid
                    │  │                  │   ╲
                    │  │     CABIN        │    ╲
                    │  │                  │ Assembly 1
   Assembly 2 ─────┤──┤                  ├──●━bar (Z=0)
   (under-hood)    │  │                  │  │╲
                    │  │                  │  │ ╲ v-strut
                    │  │                  │  │  ╲
  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│▓▓│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│▓▓●━━N5 (Z=-7.25)
  ▓▓ ground ▓▓▓▓▓▓▓│▓▓│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│▓▓│
                    │  └──────────────────┘  │ arm
                    │     ◎            ◎     │
                    │   (front         (rear ● N6 (chute)
                    │    wheel)        wheel)
                    │
   -Y ◄─────────────┼──────────────────────────────► +Y
   (rearward)       │                          (forward)
                    ↓
                  -Z (down)
```

### Front View (looking from rear, X-Z plane)

```
                  +Z (up)
                    ↑
                    │        ___________
                    │       ╱           ╲
                    │      ╱   rear      ╲
                    │     ╱   window      ╲
                    │    │                 │
                    │    │     TRUNK       │
                    │    │                 │
  N0●━━━━━━━━━━━━━━●━━━━●━━━━━━━━━━━━━━━━●━━━━━━━━━━●N4   Z=0
  (C3 fix)  N1     │    N2               N3     (C3 fix)
             ╲     │     │              ╱
              ╲    │     │  7.25"      ╱
               ╲   │     ↕           ╱
                ╲  │               ╱
                 ╲ │              ╱
                  ╲│             ╱
                   ●━━━━━━━━━━━● N5                        Z=-7.25
                   │  (coupler pin)
                   │
                   │  ◎ tailpipe   ◎ tailpipe
                   │
  -X ◄─────────────┼──────────────────────────────► +X
  (left)           │                           (right)
                   ↓
                 -Z (down)
```

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

## Assembly 2: Under-Hood Frame — GT1R Bolt-In Parachute Mount (sketch page 2)

> **This is the commercial GT1R bolt-in parachute mount kit** from T1 Race Development.
> It bolts to the frame rails under the hood where the OEM aluminum bumper beam attached.
> Reference: https://www.t1racedevelopment.com/product/gt1r-r35-bolt-on-parachute-kit/
>
> Assembly 1 (rear trunk) is a **separate custom welded structure** inside the trunk.
> The two assemblies share the load path through the vehicle frame rails.

### GT1R Kit Specs (from manufacturer)

| Parameter | Value | Unit | Confidence | Source | Notes |
|-----------|-------|------|------------|--------|-------|
| material | 4130 chromoly | — | high | T1 product page | Bent + TIG welded in-house |
| finish | gloss black powder coat | — | high | T1 product page | |
| mounting_bolts | M8x1.25, 25mm | — | high | T1 install guide | 10.9 grade |
| mounting_torque | 26 | ft-lbs | high | T1 install guide | Main mount bolts |
| upper_assembly_torque | 75 | ft-lbs | high | T1 install guide | |
| chute_hole_dia | 1.625 | in | high | T1 install guide | "1 5/8" hole saw" |
| cable_hole_dia | 0.375 | in | high | T1 install guide | 3/8" for release cable |
| chute_type | Stroud 430 | — | high | T1 recommendation | Single chute only |

### Frame Dimensions (from hand sketch page 2)

| Parameter | Value | Unit | Confidence | Source | Notes |
|-----------|-------|------|------------|--------|-------|
| hood_fwd_offset | 60.0 | in | low | estimate | Distance forward of trunk bar — needs measurement |
| hood_z_elevation | 12.0 | in | low | estimate | Height above trunk bar — needs measurement |
| hood_bar_main | 14.0 | in | medium | sketch "14" | N7→N8 horizontal bar span |
| hood_bar_end_horiz | 5.0 | in | medium | sketch "5" | N8→N9 horizontal to bolted connection |
| hood_bar_end_drop | 1.0 | in | medium | sketch "1" | N8→N9 vertical drop at B1 |
| curved_arm_fwd | 8.0 | in | medium | sketch "8" | N8→N10 curved member (150° arc) |
| curved_arm_angle | 150 | deg | medium | sketch "150° eth" | Included angle — not yet modeled as arc |

### Node Positions (under-hood)

| Node | X | Y | Z | Label | Connection | BC |
|------|---|---|---|-------|------------|----|
| N7 | -18.0 | 60.0 | 12.0 | hood bar left | C2 weld | free |
| N8 | -4.0 | 60.0 | 12.0 | hood bar right | C2 weld | free |
| N9 | 1.0 | 60.0 | 11.0 | B1 bolted | B1 (M8, 6 bolts) | bolted |
| N10 | -4.0 | 68.0 | 12.0 | P1 pinned | P1 | pinned |

## Tube Properties

### Assembly 1 — Rear Trunk (custom welded)

| Parameter | Value | Unit | Confidence | Notes |
|-----------|-------|------|------------|-------|
| tube_od | 1.75 | in | high | Client confirmed |
| tube_wall | 0.120 | in | high | Standard for 1.75" OD 4130 (NHRA SFI 25.1 roll cage spec) |
| material | 4130 chromoly | — | high | Known from client |
| tube_cl | 12.0 | in | medium | Sketch side view "12 CL" |

### Assembly 2 — Under-Hood (GT1R kit)

| Parameter | Value | Unit | Confidence | Notes |
|-----------|-------|------|------------|-------|
| tube_od | 1.75 | in | high | Client confirmed |
| tube_wall | 0.120 | in | high | Standard for 1.75" OD 4130 (NHRA SFI 25.1) |
| material | 4130 chromoly | — | high | T1 product spec |
| bolt_size | M8x1.25 | — | high | T1 install guide, 10.9 grade, 25mm length |

## Frame Rails (connecting assemblies)

| Member | From | To | Notes |
|--------|------|----|-------|
| frame_rail_left | N0 | N7 | Left C3 weld (trunk) → hood bar left (vehicle frame rail) |
| frame_rail_right | N4 | N8 | Right C3 weld (trunk) → hood bar right (vehicle frame rail) |

> **Load path:** Parachute drag → N6 bracket → arm → N5 coupler pin → V-struts →
> N1/N3 bar junctions → N0/N4 C3 welds → frame rails → N7/N8 under-hood mount →
> B1 bolted connection to chassis subframe

## Stick Figure Schematics

### Front View (looking from rear of car, X-Z plane, Y=0)

```
  X=  -18      -12        0       +12      +18
       │        │         │        │        │
       │   6"   │   12"   │  12"   │   6"   │
       ├────────┼─────────┼────────┼────────┤
       │        │         │        │        │
       ●━━━━━━━━●━━━━━━━━━●━━━━━━━━●━━━━━━━━●  ── Z=0 (bar)
      N0       N1        N2       N3       N4
   [C3 fix]  [C0 wld]  [C1 blt] [C0 wld] [C3 fix]
                ╲                  ╱
                 ╲                ╱
                  ╲   7.25"      ╱
                   ╲    │       ╱
                    ╲   ↓      ╱
                     ╲        ╱
                      ● N5                      ── Z=-7.25
                   [coupler pin]
                      │
                      │ 12" (into page, −Y)
                      │
                      ● N6                      ── Z=-7.25
                 [PARACHUTE POINT]
```

### Top View (looking down, X-Y plane)

```
  Y (forward +)
  ↑
  │
  │         Under-Hood Frame
  │
  │  N10 ●                                          Y=68
  │       │  8"
  │       │
  │  N7 ●━━━━━━━━━━━━━━● N8 ━━━━━● N9              Y=60
  │      ← ── 14" ── →    ← 5" →
  │       │                │
  │       │  frame         │  frame
  │       │  rail L        │  rail R
  │       │  ~61"          │  ~65"
  │       │                │
  │       │                │
  │       │   Rear Trunk Frame
  │       │                │
  │  N0 ●━━━━━━●━━━━━━●━━━━━━●━━━━━━● N4            Y=0
  │     -18   N1     N2     N3     +18
  │            -12    0     +12
  │                   │
  │                   │ 12" (arm)
  │                   │
  │                   ● N6                           Y=-12
  │              [PARACHUTE]
  │
  └──────────────────────────────────────→ X (right +)
       -18    -12     0    +12    +18
```

### Side View (looking from left, Y-Z plane, X=0 centerline)

```
  Z (up +)
  ↑
  │
  │                    N8
  │         ● ─────────                              Z=12
  │         N7         │╲N9                           Z=11
  │                    │
  │    frame rail      │
  │    (behind)        │
  │                    │
  │                    │
  ●━━━━━━━━━━━━━━━━━━━━● N2                          Z=0  (bar)
  │                    │
  │                    │ 7.25"
  │                    │
  │                    ● N5                           Z=-7.25
  │                    │
  │                    │ 12" (arm)
  │                    │
  │                    ● N6                           Z=-7.25
  │               [PARACHUTE]
  │
  └──────────────────────────────────────→ Y (fwd +)
       -12     0            60      68
```

## Items for Client Clarification

1. Tube wall thickness (Assembly 1) — 0.120" assumed, needs confirmation
2. Parachute arm length — 12" estimated from photos
3. Under-hood frame position relative to trunk (hood_fwd_offset, hood_z_elevation)
4. Curved member — is 150° the included angle or the bend angle?
5. Frame rail path — straight line or follows vehicle body contour?
6. GT1R kit tube OD/wall — not published, measure from physical kit
7. GT1R kit — is the chute arm (slip-fit tube) part of Assembly 2 or separate?
