# GT1R R35 Parachute Frame — Geometry Dimensions (WRK-1360)

> **Edit this file** to refine dimensions. Once finalized, coordinates will be
> regenerated from these values into `frame_geometry_3d.py`.
>
> **Convention:** Only +X nodes defined. −X nodes are mirror images about X=0 plane.

## Coordinate System

- **X** = transverse (+ right, − left), centered on vehicle centerline
- **Y** = longitudinal (+ forward, − rearward)
- **Z** = vertical (+ up)
- **Origin** = coupler pin (N5) = (0, 0, 0)

### 3D Axes Convention

```
                +Z (up)
                 ↑
                 │
                 │
                 │
                 │
                 │
                 ●──────────────► +X (right / passenger)
                ╱  Origin = N5
               ╱   (coupler pin)
              ╱
             ╱
            ╱
           ↙
         +Y (forward / toward hood)


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
          │   │  Under-Hood│Frame       │   │
          │   │  N14━━N13━━N10━━N11━━━━N9   │   Y=9 (N9,N14)
          │   │            │            │   │   Y=4 (N10,N11,N13)
          │   ├────────────┼────────────┤   │
          │   │            │            │   │
          │   │  CABIN     │            │   │
          │   │            │            │   │
          │   │            │  N8        │   │   Y=12.5
          │   ├────────────┼────────────┤   │
          │   │            │            │   │
 -X ◄─────┼───┤  TRUNK    ●(N5 origin) ├───┼─────► +X
  (left)  │   │            │            │   │  (right)
          │   │ N0━N12━N1━━N2━━N3━N7━N4 │   │   Y=24.5
          │   │            │            │   │
           ╲  │            │            │  ╱
            ╲ └────────────┼────────────┘ ╱
             ╲─────────────┼─────────────╱
                           │
                           ● N6 (parachute)          Y=-3.25
                           │
                           ↓
                         -Y (rearward)
```

### Side View (right side, Y-Z plane, X=0 centerline)

```
  Z (up +)
  ↑
  │
  │                              N2
  │                              ● ━━━━━━━━━━━━━     Z=+2.5 (bar)
  │                             ╱
  │                            ╱
  │                    N8     ╱
  │                    ●     ╱                        Z=+1
  │                   ╱     ╱
  │                  ╱     ╱
  │          N10    ╱     ╱
  │━━━━━━━━━━● ━━━╱━━━━╱━━━━━━━━━━━━━━━━━━━━━━━     Z=0
  │  N9(-4)  ╱   ╱   ╱
  │         ╱   ╱   ╱
  │        ╱  N5●  ╱                                  Z=0 (ORIGIN)
  │           │   ╱
  │           │  ╱
  │        N6 ● ╱                                     Z=0
  │      [CHUTE]
  │
  └──────────────────────────────────────→ Y (fwd +)
    -3.25  0   4    12.5        24.5
```

### Front View (looking from rear, X-Z plane, Y=24.5 bar section)

```
  X=  -18    -15    -12        0       +12    +15    +18
       │      │      │         │        │      │      │
       │  3"  │  3"  │   12"   │  12"   │  3"  │  3"  │
       │      │      │         │        │      │      │
       ●━━━━━━●━━━━━━●━━━━━━━━━●━━━━━━━━●━━━━━━●━━━━━━●  ── Z=+2.5
      N0     N12    N1        N2       N3     N7     N4
      (-0.5)              (bar at 2.5)             (-0.5)
   [C3 fix]                [C1 blt]             [C3 fix]
                ╲                      ╱
                  ╲                  ╱
                    ╲              ╱
                      ╲          ╱
                        ╲      ╱
                          ╲  ╱
                           ● N5 (ORIGIN)              ── Z=0
                        [coupler pin]
```

> **Note:** N0 and N4 are at Z=-0.5 (dropped 3" from N1/N3 at Z=2.5).
> N7 and N12 are bend points at Z=2.5 transitioning to the dropped ends.

---

## Assembly 1: Rear Trunk Frame

### Node Positions (+X side, origin at N5)

| Node | X | Y | Z | Label | Connection | BC | Notes |
|------|---|---|---|-------|------------|----|-------|
| N5 | 0.0 | 0.0 | 0.0 | coupler pin | double pin | free | **ORIGIN** |
| N6 | 0.0 | -3.25 | 0.0 | parachute bracket | bracket | free | Chute attach point |
| N10 | 0.0 | 4.0 | 0.0 | C2 weld junction | C2 weld | free | Shared with under-hood frame |
| N8 | 0.0 | 12.5 | 1.0 | center strut mid | weld | free | Intermediate point on center spine |
| N2 | 0.0 | 24.5 | 2.5 | center bolt | C1 bolt+pin | free (shear) | Center of horizontal bar |
| N3 | 12.0 | 24.5 | 2.5 | right strut junction | C0 weld | free | V-strut meets bar |
| N7 | 15.0 | 24.5 | 2.5 | right bar bend | weld | free | Bend point before drop to N4 |
| N4 | 18.0 | 24.5 | -0.5 | right C3 mount | C3 weld | fixed | Frame rail attachment |

### Node Positions (−X side, mirrored)

| Node | X | Y | Z | Label | Mirror of | Connection | BC |
|------|---|---|---|-------|-----------|------------|----|
| N1 | -12.0 | 24.5 | 2.5 | left strut junction | N3 | C0 weld | free |
| N12 | -15.0 | 24.5 | 2.5 | left bar bend | N7 | weld | free |
| N0 | -18.0 | 24.5 | -0.5 | left C3 mount | N4 | C3 weld | fixed |

### Members (rear trunk)

| ID | From | To | Label | Notes |
|----|------|----|-------|-------|
| M0 | N6 | N5 | parachute_arm | Chute → coupler pin, 3.25" |
| M1 | N5 | N10 | center_spine_lower | Coupler → C2 junction, 4" |
| M2 | N10 | N8 | center_spine_mid | C2 junction → intermediate, 8.5" |
| M3 | N8 | N2 | center_spine_upper | Intermediate → center bar, 12" |
| M4 | N3 | N5 | v_strut_right | Right bar junction → coupler pin |
| M5 | N1 | N5 | v_strut_left | Left bar junction → coupler pin |
| M6 | N2 | N3 | bar_right_inner | Center → right junction, 12" |
| M7 | N2 | N1 | bar_left_inner | Center → left junction, 12" |
| M8 | N3 | N7 | bar_right_mid | Right junction → bend, 3" |
| M9 | N7 | N4 | bar_right_end | Bend → right C3 mount, 3" (drops Z: 2.5→-0.5) |
| M10 | N1 | N12 | bar_left_mid | Left junction → bend, 3" |
| M11 | N12 | N0 | bar_left_end | Bend → left C3 mount, 3" (drops Z: 2.5→-0.5) |

---

## Assembly 2: Under-Hood Frame (GT1R Bolt-In Parachute Mount)

> **GT1R bolt-in kit** from T1 Race Development.
> Bolts to frame rails where OEM bumper beam attached.
> Reference: https://www.t1racedevelopment.com/product/gt1r-r35-bolt-on-parachute-kit/

### Node Positions (+X side)

| Node | X | Y | Z | Label | Connection | BC | Notes |
|------|---|---|---|-------|------------|----|-------|
| N10 | 0.0 | 4.0 | 0.0 | C2 weld junction | C2 weld | free | **Shared with Assembly 1** |
| N11 | 16.0 | 4.0 | 0.0 | hood bar right | weld | free | Under-hood bar endpoint |
| N9 | 21.0 | 9.0 | -4.0 | B1 bolted right | B1 (M8, 6 bolts) | bolted | Bolted to chassis subframe |

### Node Positions (−X side, mirrored)

| Node | X | Y | Z | Label | Mirror of | Connection | BC |
|------|---|---|---|-------|-----------|------------|----|
| N13 | -16.0 | 4.0 | 0.0 | hood bar left | N11 | weld | free |
| N14 | -21.0 | 9.0 | -4.0 | B1 bolted left | N9 | B1 (M8, 6 bolts) | bolted |

### Members (under-hood)

| ID | From | To | Label | Notes |
|----|------|----|-------|-------|
| M12 | N10 | N11 | hood_bar_right | C2 junction → right bar end, 16" |
| M13 | N11 | N9 | hood_bar_right_end | Right bar → B1 bolted, angled |
| M14 | N10 | N13 | hood_bar_left | C2 junction → left bar end, 16" |
| M15 | N13 | N14 | hood_bar_left_end | Left bar → B1 bolted, angled |

### GT1R Kit Specs (from manufacturer)

| Parameter | Value | Unit | Source | Notes |
|-----------|-------|------|--------|-------|
| mounting_bolts | M8x1.25, 25mm | — | T1 install guide | 10.9 grade |
| mounting_torque | 26 | ft-lbs | T1 install guide | Main mount bolts |
| upper_assembly_torque | 75 | ft-lbs | T1 install guide | |
| chute_hole_dia | 1.625 | in | T1 install guide | "1 5/8" hole saw" |
| cable_hole_dia | 0.375 | in | T1 install guide | 3/8" for release cable |
| chute_type | Stroud 430 | — | T1 recommendation | Single chute only |

---

## Load Path

```
Parachute drag
    → N6 (bracket)
    → N5 (coupler pin, ORIGIN)
    → N10 (C2 weld junction) ──────→ Under-hood frame → N9/N14 (B1 bolted to chassis)
    → N1/N3 (V-struts to bar)
    → N0/N4 (C3 welds to frame rails)
```

---

## Tube Properties

### Assembly 1 — Rear Trunk (custom welded)

| Parameter | Value | Unit | Confidence | Notes |
|-----------|-------|------|------------|-------|
| tube_od | 1.75 | in | high | Client confirmed |
| tube_wall | 0.120 | in | high | Standard for 1.75" OD 4130 (NHRA SFI 25.1) |
| material | 4130 chromoly | — | high | Known from client |

### Assembly 2 — Under-Hood (GT1R kit)

| Parameter | Value | Unit | Confidence | Notes |
|-----------|-------|------|------------|-------|
| tube_od | 1.75 | in | high | Client confirmed |
| tube_wall | 0.120 | in | high | Standard for 1.75" OD 4130 (NHRA SFI 25.1) |
| material | 4130 chromoly | — | high | T1 product spec |

---

## All Nodes Summary

| Node | X | Y | Z | Assembly | Connection | BC |
|------|---|---|---|----------|------------|----|
| N0 | -18.0 | 24.5 | -0.5 | rear_trunk | C3 weld | fixed |
| N1 | -12.0 | 24.5 | 2.5 | rear_trunk | C0 weld | free |
| N2 | 0.0 | 24.5 | 2.5 | rear_trunk | C1 bolt+pin | free |
| N3 | 12.0 | 24.5 | 2.5 | rear_trunk | C0 weld | free |
| N4 | 18.0 | 24.5 | -0.5 | rear_trunk | C3 weld | fixed |
| N5 | 0.0 | 0.0 | 0.0 | rear_trunk | double pin | free |
| N6 | 0.0 | -3.25 | 0.0 | rear_trunk | bracket | free |
| N7 | 15.0 | 24.5 | 2.5 | rear_trunk | weld | free |
| N8 | 0.0 | 12.5 | 1.0 | rear_trunk | weld | free |
| N9 | 21.0 | 9.0 | -4.0 | under_hood | B1 (6 bolts) | bolted |
| N10 | 0.0 | 4.0 | 0.0 | shared | C2 weld | free |
| N11 | 16.0 | 4.0 | 0.0 | under_hood | weld | free |
| N12 | -15.0 | 24.5 | 2.5 | rear_trunk | weld | free |
| N13 | -16.0 | 4.0 | 0.0 | under_hood | weld | free |
| N14 | -21.0 | 9.0 | -4.0 | under_hood | B1 (6 bolts) | bolted |

## All Members Summary

| ID | From | To | Assembly | Label |
|----|------|----|----------|-------|
| M0 | N6 | N5 | rear_trunk | parachute_arm |
| M1 | N5 | N10 | rear_trunk | center_spine_lower |
| M2 | N10 | N8 | rear_trunk | center_spine_mid |
| M3 | N8 | N2 | rear_trunk | center_spine_upper |
| M4 | N3 | N5 | rear_trunk | v_strut_right |
| M5 | N1 | N5 | rear_trunk | v_strut_left |
| M6 | N2 | N3 | rear_trunk | bar_right_inner |
| M7 | N2 | N1 | rear_trunk | bar_left_inner |
| M8 | N3 | N7 | rear_trunk | bar_right_mid |
| M9 | N7 | N4 | rear_trunk | bar_right_end |
| M10 | N1 | N12 | rear_trunk | bar_left_mid |
| M11 | N12 | N0 | rear_trunk | bar_left_end |
| M12 | N10 | N11 | under_hood | hood_bar_right |
| M13 | N11 | N9 | under_hood | hood_bar_right_end |
| M14 | N10 | N13 | under_hood | hood_bar_left |
| M15 | N13 | N14 | under_hood | hood_bar_left_end |

---

## Items for Client Clarification

1. Tube wall thickness (Assembly 1) — 0.120" assumed, needs confirmation
2. V-strut routing — do N1/N3 connect directly to N5, or through N8?
3. Center spine — is N8 a physical node (weld/junction) or just a bend?
4. N4/N0 drop — bar drops from Z=2.5 to Z=-0.5 at ends. Is this a smooth bend or sharp?
5. Under-hood N9 position (21, 9, -4) — the Z=-4 drop needs verification
6. Frame rail connections — are N0/N4 the only fixed BCs?
