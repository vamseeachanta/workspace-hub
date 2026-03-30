"""
Shapely 2.x — Offshore Wind Site Layout Example
Integration example for workspace-hub#1491 (Shapely OSS catalog entry).

Demonstrates core Shapely operations relevant to offshore site layout:
  - Lease area polygon definition in UTM coordinates
  - Turbine grid placement (Point array)
  - Exclusion buffer zones around each turbine
  - Cable route corridor (LineString + buffer)
  - Restricted zone containment checks
  - Summary statistics (area, minimum spacing, corridor area)
  - pyproj CRS transform: WGS84 geographic → UTM projected

Dependencies (no system GEOS required — bundled in Shapely 2.x wheel):
    pip install shapely pyproj
"""

import math
import shapely
import numpy as np
from shapely import (
    Point,
    Polygon,
    LineString,
    MultiPoint,
    buffer,
    distance,
    contains,
    union_all,
    intersection,
)
from shapely.strtree import STRtree
from pyproj import Transformer

# ---------------------------------------------------------------------------
# 1.  CRS transform helper — WGS84 (EPSG:4326) → UTM Zone 31N (EPSG:32631)
#     North Sea typical zone.
# ---------------------------------------------------------------------------

_wgs84_to_utm31n = Transformer.from_crs("EPSG:4326", "EPSG:32631", always_xy=True)


def latlon_to_utm(lon: float, lat: float) -> tuple[float, float]:
    """Transform a single WGS84 coordinate to UTM Zone 31N (metres)."""
    return _wgs84_to_utm31n.transform(lon, lat)


# ---------------------------------------------------------------------------
# 2.  Lease area — approximate North Sea block in UTM 31N (metres)
#     Centred around ~56°N 4°E (southern North Sea).
# ---------------------------------------------------------------------------

# Four corner coordinates (lon, lat) → UTM
_corners_lonlat = [
    (3.50, 55.80),
    (4.50, 55.80),
    (4.50, 56.30),
    (3.50, 56.30),
]

lease_corners_utm = [latlon_to_utm(lon, lat) for lon, lat in _corners_lonlat]
lease_area = Polygon(lease_corners_utm)

print(f"Lease area:       {lease_area.area / 1e6:.2f} km²")
print(f"Lease perimeter:  {lease_area.length / 1e3:.2f} km")

# ---------------------------------------------------------------------------
# 3.  Turbine grid — 5 × 4 layout with 1 km spacing
# ---------------------------------------------------------------------------

TURBINE_SPACING_M = 1_000.0   # 1 km rotor-to-rotor minimum
COLS, ROWS = 5, 4

# Grid origin: offset 2 km from SW corner of lease area
origin_x, origin_y = lease_corners_utm[0]
origin_x += 2_000
origin_y += 2_000

turbine_coords = np.array([
    (origin_x + c * TURBINE_SPACING_M, origin_y + r * TURBINE_SPACING_M)
    for r in range(ROWS)
    for c in range(COLS)
])

# Vectorized Point array using shapely.points (v2.x functional API)
turbine_points = shapely.points(turbine_coords[:, 0], turbine_coords[:, 1])

print(f"\nTurbines placed:  {len(turbine_points)}")

# ---------------------------------------------------------------------------
# 4.  Exclusion buffer zones — 500 m radius around each turbine
# ---------------------------------------------------------------------------

EXCLUSION_RADIUS_M = 500.0

exclusion_buffers = buffer(turbine_points, EXCLUSION_RADIUS_M)
exclusion_union = union_all(exclusion_buffers)

print(f"Exclusion union area: {exclusion_union.area / 1e6:.3f} km²")

# ---------------------------------------------------------------------------
# 5.  Cable route corridor
#     Main export cable: spine from first to last turbine in bottom row,
#     then up to first turbine in top row (L-shaped trunk).
# ---------------------------------------------------------------------------

bottom_row_coords = turbine_coords[:COLS]           # first row
top_left_coord = turbine_coords[COLS * (ROWS - 1)]  # top-left turbine

cable_vertices = list(map(tuple, bottom_row_coords)) + [tuple(top_left_coord)]
cable_route = LineString(cable_vertices)

CABLE_CORRIDOR_WIDTH_M = 100.0  # 50 m either side
cable_corridor = buffer(cable_route, CABLE_CORRIDOR_WIDTH_M / 2)

print(f"\nCable route length:    {cable_route.length / 1e3:.2f} km")
print(f"Cable corridor area:   {cable_corridor.area / 1e6:.4f} km²")

# ---------------------------------------------------------------------------
# 6.  Restricted zone — simulated shipping lane cutting across the site
# ---------------------------------------------------------------------------

rx, ry = lease_corners_utm[0]  # SW corner
restricted_zone = Polygon([
    (rx + 3_200, ry + 500),
    (rx + 4_200, ry + 500),
    (rx + 4_200, ry + 2_500),
    (rx + 3_200, ry + 2_500),
])

# Vectorized containment check: which turbines fall inside the restricted zone?
inside_mask = contains(restricted_zone, turbine_points)
n_inside = int(inside_mask.sum())
n_outside = len(turbine_points) - n_inside

print(f"\nRestricted zone area:  {restricted_zone.area / 1e6:.3f} km²")
print(f"Turbines INSIDE zone:  {n_inside}")
print(f"Turbines OUTSIDE zone: {n_outside}")

# ---------------------------------------------------------------------------
# 7.  Minimum spacing check via STRtree (nearest-neighbour query)
# ---------------------------------------------------------------------------

tree = STRtree(turbine_points)

min_spacing = math.inf
for i, pt in enumerate(turbine_points):
    # query_nearest returns index of nearest geometry (excluding self)
    nearest_idx = tree.query_nearest(pt, return_distance=False, exclusive=True)
    if nearest_idx.size > 0:
        j = nearest_idx[0]
        d = float(distance(pt, turbine_points[j]))
        if d < min_spacing:
            min_spacing = d

print(f"\nMinimum turbine spacing: {min_spacing:.1f} m  (target ≥ {TURBINE_SPACING_M:.0f} m)")
spacing_ok = min_spacing >= TURBINE_SPACING_M
print(f"Spacing constraint met:  {'YES' if spacing_ok else 'NO'}")

# ---------------------------------------------------------------------------
# 8.  Net usable lease area (lease minus exclusions minus restricted zone)
# ---------------------------------------------------------------------------

net_area = lease_area.difference(exclusion_union).difference(restricted_zone)
print(f"\nNet usable lease area: {net_area.area / 1e6:.2f} km²  "
      f"({100 * net_area.area / lease_area.area:.1f}% of total)")

# ---------------------------------------------------------------------------
# 9.  Summary
# ---------------------------------------------------------------------------

print("\n--- Layout Summary ---")
print(f"  Turbines:           {len(turbine_points)}")
print(f"  Grid spacing:       {TURBINE_SPACING_M / 1e3:.1f} km")
print(f"  Exclusion radius:   {EXCLUSION_RADIUS_M:.0f} m")
print(f"  Cable corridor:     {CABLE_CORRIDOR_WIDTH_M:.0f} m wide, "
      f"{cable_route.length / 1e3:.2f} km long")
print(f"  Restricted zone:    {n_inside} turbine(s) affected")
print(f"  Min spacing OK:     {'yes' if spacing_ok else 'NO — layout violation'}")
print(f"  Net lease area:     {net_area.area / 1e6:.2f} km²")
