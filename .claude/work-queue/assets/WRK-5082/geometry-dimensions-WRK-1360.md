# GT1R R35 Parachute Frame — Geometry Dimensions (WRK-1360)

> **Edit this file** to refine dimensions. Once finalized, coordinates will be
> regenerated from these values into `frame_geometry_3d.py`.
>
> **Convention:** Only +X nodes defined explicitly. −X nodes are mirror images about X=0 plane.

## Coordinate System

- **X** = transverse (+ right, − left), centered on vehicle centerline
- **Y** = longitudinal (+ forward, − rearward)
- **Z** = vertical (+ up)
- **Origin** = N0 (C2 weld junction) = (0, 0, 0) — shared between both assemblies

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
                ╱  Origin = N0
               ╱   (C2 weld junction,
              ╱     shared between
             ╱      Assy 1 & Assy 2)
            ╱
           ↙
         +Y (forward)


    Axis    Direction          Vehicle Reference
    ────    ─────────          ─────────────────
    +X      right              passenger side
    −X      left               driver side
    +Y      forward            toward engine
    −Y      rearward           toward bumper/chute
    +Z      up                 toward roof
    −Z      down               toward ground
```

## Node Numbering Convention

```
    N0          = C2 weld junction (ORIGIN, shared between assemblies)

    Assembly 1 — Rear Trunk Frame (center spine → bar, chute outward)
    N1          = parachute bracket (chute attachment)
    N2          = coupler pin (V-strut convergence)
    N3          = center spine intermediate
    N4          = center bar C1 bolt (center of horizontal bar)
    N5  / N8    = right / left strut junction (C0 weld, +X / −X)
    N6  / N9    = right / left bar bend (+X / −X)
    N7  / N10   = right / left C3 mount, fixed BC (+X / −X)

    Assembly 2 — Under-Chassis Frame (GT1R bolt-in kit)
    N11 / N13   = right / left bar end (+X / −X)
    N12 / N14   = right / left B1 bolted to subframe (+X / −X)
```

---

## Assembly 1: Rear Trunk Frame

### Node Positions (centerline + right side)

| Node | X | Y | Z | Label | Connection | BC | Notes |
|------|---|---|---|-------|------------|----|-------|
| **N0** | **0.0** | **0.0** | **0.0** | **C2 weld junction** | **C2 weld** | **free** | **ORIGIN — shared with Assy 2** |
| N1 | 0.0 | -7.25 | 0.0 | parachute bracket | bracket | free | Chute attachment point |
| N2 | 0.0 | -4.0 | 0.0 | coupler pin | double pin | free | V-strut convergence |
| N3 | 0.0 | 8.5 | 1.0 | center spine mid | weld | free | Intermediate on center spine |
| N4 | 0.0 | 20.5 | 2.5 | center bar C1 bolt | C1 bolt+pin | free (shear) | Center of horizontal bar |
| N5 | 12.0 | 20.5 | 2.5 | right strut junction | C0 weld | free | V-strut meets bar (+X) |
| N6 | 15.0 | 20.5 | 2.5 | right bar bend | weld | free | Bend before drop to C3 (+X) |
| N7 | 18.0 | 20.5 | -0.5 | right C3 mount | C3 weld | fixed | Frame rail attachment (+X) |

### Node Positions (left side, mirrored from +X)

| Node | X | Y | Z | Label | Mirror of | Connection | BC |
|------|---|---|---|-------|-----------|------------|----|
| N8 | -12.0 | 20.5 | 2.5 | left strut junction | N5 | C0 weld | free |
| N9 | -15.0 | 20.5 | 2.5 | left bar bend | N6 | weld | free |
| N10 | -18.0 | 20.5 | -0.5 | left C3 mount | N7 | C3 weld | fixed |

### Members (rear trunk)

| ID | From | To | Label | Notes |
|----|------|----|-------|-------|
| M0 | N1 | N2 | parachute_arm | Chute bracket → coupler pin, 3.25" |
| M1 | N2 | N0 | center_spine_lower | Coupler pin → C2 weld origin, 4" |
| M2 | N0 | N3 | center_spine_mid | C2 weld → intermediate, 8.5" |
| M3 | N3 | N4 | center_spine_upper | Intermediate → center bar, 12" |
| M4 | N5 | N2 | v_strut_right | Right bar junction → coupler pin |
| M5 | N8 | N2 | v_strut_left | Left bar junction → coupler pin |
| M6 | N4 | N5 | bar_right_inner | Center bar → right junction, 12" |
| M7 | N4 | N8 | bar_left_inner | Center bar → left junction, 12" |
| M8 | N5 | N6 | bar_right_mid | Right junction → bend, 3" |
| M9 | N6 | N7 | bar_right_end | Bend → right C3, 3" (Z drops 2.5→-0.5) |
| M10 | N8 | N9 | bar_left_mid | Left junction → bend, 3" |
| M11 | N9 | N10 | bar_left_end | Bend → left C3, 3" (Z drops 2.5→-0.5) |

---

## Assembly 2: Under-Chassis Frame (GT1R Bolt-In Kit)

> **GT1R bolt-in parachute mount kit** from T1 Race Development.
> Bolts to chassis subframe where OEM bumper beam attached.
> Reference: https://www.t1racedevelopment.com/product/gt1r-r35-bolt-on-parachute-kit/

### Node Positions (+X side)

| Node | X | Y | Z | Label | Connection | BC | Notes |
|------|---|---|---|-------|------------|----|-------|
| **N0** | **0.0** | **0.0** | **0.0** | **C2 weld junction** | **C2 weld** | **free** | **ORIGIN — shared with Assy 1** |
| N11 | 16.0 | 0.0 | 0.0 | right bar end | weld | free | Under-chassis bar (+X) |
| N12 | 21.0 | 5.0 | -4.0 | right B1 bolted | B1 (M8, 6 bolts) | bolted | Bolted to chassis subframe (+X) |

### Node Positions (−X side, mirrored)

| Node | X | Y | Z | Label | Mirror of | Connection | BC |
|------|---|---|---|-------|-----------|------------|----|
| N13 | -16.0 | 0.0 | 0.0 | left bar end | N11 | weld | free |
| N14 | -21.0 | 5.0 | -4.0 | left B1 bolted | N12 | B1 (M8, 6 bolts) | bolted |

### Members (under-chassis)

| ID | From | To | Label | Notes |
|----|------|----|-------|-------|
| M12 | N0 | N11 | chassis_bar_right | C2 weld → right bar end, 16" |
| M13 | N11 | N12 | chassis_bar_right_end | Right bar → B1 bolted, angled |
| M14 | N0 | N13 | chassis_bar_left | C2 weld → left bar end, 16" |
| M15 | N13 | N14 | chassis_bar_left_end | Left bar → B1 bolted, angled |

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
    → N1 (bracket)
    → N2 (coupler pin)
    → N0 (C2 weld, ORIGIN) ──────→ Assy 2: N11/N13 → N12/N14 (B1 bolted to chassis)
    → N5/N8 (V-struts to bar)
    → N7/N10 (C3 welds to frame rails, fixed BC)
```

---

## Stick Figure Schematics

### Front View (looking from rear, X-Z plane, Y=20.5 bar section)

```
  X=  -18    -15    -12        0       +12    +15    +18
       │      │      │         │        │      │      │
       │  3"  │  3"  │   12"   │  12"   │  3"  │  3"  │
       │      │      │         │        │      │      │
       ●━━━━━━●━━━━━━●━━━━━━━━━●━━━━━━━━●━━━━━━●━━━━━━●  ── Z=+2.5
      N10    N9     N8        N4       N5     N6     N7
      (-0.5)              (bar at 2.5)             (-0.5)
   [C3 fix]                [C1 blt]             [C3 fix]
                ╲                      ╱
                  ╲                  ╱
                    ╲              ╱
                      ╲          ╱
                        ╲      ╱
                          ╲  ╱
                           ● N2 (coupler pin)     ── Z=0
                           │
                           ● N0 (ORIGIN, C2 weld) ── Z=0
```

> **Note:** N7/N10 drop from Z=2.5 to Z=-0.5 at the C3 mount ends.

### Top View (looking down, X-Y plane)

```
  Y (forward +)
  ↑
  │
  │   Under-Chassis Frame
  │
  │  N14 ●                     ● N12                Y=5
  │       ╲                   ╱
  │        ╲                 ╱
  │  N13 ●━━━━━━━● N0 ●━━━━━━━● N11                Y=0 (ORIGIN)
  │     -16    (ORIGIN)     +16
  │                │
  │                │  center spine
  │                │
  │           N3   ●                                Y=8.5
  │                │
  │                │
  │   Rear Trunk Frame
  │                │
  │  N10━━N9━━N8━━━N4━━━N5━━N6━━N7                  Y=20.5
  │  -18 -15 -12   0   +12 +15 +18
  │
  │                │
  │           N2   ●  (coupler pin)                  Y=-4
  │                │
  │           N1   ●  [PARACHUTE]                    Y=-7.25
  │
  └──────────────────────────────────────→ X (right +)
       -21   -16   -12     0    +12   +16   +21
```

### Side View (looking from left, Y-Z plane, X=0 centerline)

```
  Z (up +)
  ↑
  │
  │                              N4
  │                              ● (bar center)       Z=+2.5
  │                             ╱
  │                            ╱
  │                    N3     ╱
  │                    ●     ╱                        Z=+1
  │                   ╱     ╱
  │                  ╱     ╱
  ●━━━━N13━━━━━━━━━N0━━━━━━━━━━N11━━━━━━━━━━━━━━━    Z=0 (ORIGIN)
  │              (ORIGIN)
  │  N12/N14          │
  │  (-4) ╲      N2   ●  (coupler pin)               Z=0
  │         ╲         │
  │          ╲   N1   ●  [PARACHUTE]                  Z=0
  │
  └──────────────────────────────────────→ Y (fwd +)
    -7.25  -4   0     8.5         20.5
```

---

## Tube Properties

### Assembly 1 — Rear Trunk (custom welded)

| Parameter | Value | Unit | Confidence | Notes |
|-----------|-------|------|------------|-------|
| tube_od | 1.75 | in | high | Client confirmed |
| tube_wall | 0.120 | in | high | Standard for 1.75" OD 4130 (NHRA SFI 25.1) |
| material | 4130 chromoly | — | high | Known from client |

### Assembly 2 — Under-Chassis (GT1R kit)

| Parameter | Value | Unit | Confidence | Notes |
|-----------|-------|------|------------|-------|
| tube_od | 1.75 | in | high | Client confirmed |
| tube_wall | 0.120 | in | high | Standard for 1.75" OD 4130 (NHRA SFI 25.1) |
| material | 4130 chromoly | — | high | T1 product spec |

---

## All Nodes Summary

| Node | X | Y | Z | Assembly | Connection | BC |
|------|---|---|---|----------|------------|----|
| **N0** | **0.0** | **0.0** | **0.0** | **shared** | **C2 weld** | **free** |
| N1 | 0.0 | -7.25 | 0.0 | rear_trunk | bracket | free |
| N2 | 0.0 | -4.0 | 0.0 | rear_trunk | double pin | free |
| N3 | 0.0 | 8.5 | 1.0 | rear_trunk | weld | free |
| N4 | 0.0 | 20.5 | 2.5 | rear_trunk | C1 bolt+pin | free |
| N5 | 12.0 | 20.5 | 2.5 | rear_trunk | C0 weld | free |
| N6 | 15.0 | 20.5 | 2.5 | rear_trunk | weld | free |
| N7 | 18.0 | 20.5 | -0.5 | rear_trunk | C3 weld | fixed |
| N8 | -12.0 | 20.5 | 2.5 | rear_trunk | C0 weld | free |
| N9 | -15.0 | 20.5 | 2.5 | rear_trunk | weld | free |
| N10 | -18.0 | 20.5 | -0.5 | rear_trunk | C3 weld | fixed |
| N11 | 16.0 | 0.0 | 0.0 | under_chassis | weld | free |
| N12 | 21.0 | 5.0 | -4.0 | under_chassis | B1 (6 bolts) | bolted |
| N13 | -16.0 | 0.0 | 0.0 | under_chassis | weld | free |
| N14 | -21.0 | 5.0 | -4.0 | under_chassis | B1 (6 bolts) | bolted |

## All Members Summary

| ID | From | To | Assembly | Label |
|----|------|----|----------|-------|
| M0 | N1 | N2 | rear_trunk | parachute_arm |
| M1 | N2 | N0 | rear_trunk | center_spine_lower |
| M2 | N0 | N3 | rear_trunk | center_spine_mid |
| M3 | N3 | N4 | rear_trunk | center_spine_upper |
| M4 | N5 | N2 | rear_trunk | v_strut_right |
| M5 | N8 | N2 | rear_trunk | v_strut_left |
| M6 | N4 | N5 | rear_trunk | bar_right_inner |
| M7 | N4 | N8 | rear_trunk | bar_left_inner |
| M8 | N5 | N6 | rear_trunk | bar_right_mid |
| M9 | N6 | N7 | rear_trunk | bar_right_end |
| M10 | N8 | N9 | rear_trunk | bar_left_mid |
| M11 | N9 | N10 | rear_trunk | bar_left_end |
| M12 | N0 | N11 | under_chassis | chassis_bar_right |
| M13 | N11 | N12 | under_chassis | chassis_bar_right_end |
| M14 | N0 | N13 | under_chassis | chassis_bar_left |
| M15 | N13 | N14 | under_chassis | chassis_bar_left_end |

---

## Items for Client Clarification

1. Tube wall thickness (Assembly 1) — 0.120" assumed, needs confirmation
2. V-strut routing — do N5/N8 connect directly to N2, or through N3?
3. Center spine — is N3 a physical node (weld/junction) or just a bend?
4. N7/N10 drop — bar drops from Z=2.5 to Z=-0.5 at ends. Smooth bend or sharp?
5. N12 position (21, 5, -4) — the Z=-4 drop needs verification
6. Frame rail connections — are N7/N10 the only fixed BCs?
