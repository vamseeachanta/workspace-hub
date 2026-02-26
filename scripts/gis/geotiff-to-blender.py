"""Export a GeoTIFF bathymetry/terrain raster to Blender-importable formats.

Outputs:
  - .obj  Wavefront OBJ mesh (Blender: File > Import > Wavefront OBJ)
  - .csv  X/Y/Z point cloud  (QGIS: Add Delimited Text Layer)

Usage
-----
  python geotiff-to-blender.py input.tif --output mesh.obj
  python geotiff-to-blender.py input.tif --output points.csv --subsample 4

Requires: pip install rasterio numpy
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import numpy as np

try:
    from digitalmodel.gis.io.geotiff_handler import GeoTIFFHandler
    _HAS_HANDLER = True
except ImportError:  # pragma: no cover
    _HAS_HANDLER = False

try:
    import rasterio  # noqa: F401
    _HAS_RASTERIO = True
except ImportError:  # pragma: no cover
    _HAS_RASTERIO = False

logger = logging.getLogger(__name__)


def _write_obj(
    grid: np.ndarray,
    xs: np.ndarray,
    ys: np.ndarray,
    out_path: Path,
    scale_xy: float = 0.001,
    scale_z: float = 0.001,
) -> None:
    """Write a regular grid to a Wavefront OBJ file."""
    rows, cols = grid.shape
    x0, y0 = xs[0], ys[0]

    with out_path.open("w") as fh:
        fh.write(
            "# Terrain mesh exported by geotiff-to-blender.py\n"
            "# Z = elevation/depth in map units.\n"
            "# Blender: File > Import > Wavefront (.obj)\n\n"
        )
        for r in range(rows):
            for c in range(cols):
                bx = (xs[c] - x0) * scale_xy
                by = (ys[r] - y0) * scale_xy
                bz = float(grid[r, c]) * scale_z
                fh.write(f"v {bx:.6f} {by:.6f} {bz:.6f}\n")
        fh.write("\n")
        for r in range(rows - 1):
            for c in range(cols - 1):
                v0 = r * cols + c + 1
                fh.write(f"f {v0} {v0+1} {v0+cols+1} {v0+cols}\n")

    logger.info("Wrote OBJ: %s (%d vertices)", out_path, rows * cols)


def _write_csv(
    grid: np.ndarray,
    xs: np.ndarray,
    ys: np.ndarray,
    out_path: Path,
) -> None:
    """Write grid as X,Y,Z CSV (QGIS-importable delimited text layer)."""
    rows, cols = grid.shape
    with out_path.open("w") as fh:
        fh.write("x,y,z\n")
        for r in range(rows):
            for c in range(cols):
                fh.write(f"{xs[c]:.6f},{ys[r]:.6f},{grid[r, c]:.3f}\n")
    logger.info("Wrote CSV: %s (%d points)", out_path, rows * cols)


def convert(
    input_tif: Path,
    output: Path,
    subsample: int = 1,
    scale_xy: float = 0.001,
    scale_z: float = 0.001,
) -> None:
    """Convert a GeoTIFF to OBJ or CSV.

    Parameters
    ----------
    input_tif:
        Path to the input GeoTIFF file.
    output:
        Output file path. Extension determines format (.obj or .csv).
    subsample:
        Take every Nth row/column (1 = full resolution).
    scale_xy:
        Blender unit scale for X/Y (metres to Blender units, OBJ only).
    scale_z:
        Blender unit scale for Z (OBJ only).
    """
    if not _HAS_HANDLER or not _HAS_RASTERIO:
        raise ImportError(
            "rasterio and the digitalmodel GIS package are required. "
            "Install with: pip install rasterio"
        )

    info = GeoTIFFHandler.read(input_tif)
    data: np.ndarray = info["data"].astype(float)
    bounds = info["bounds"]  # (min_x, min_y, max_x, max_y)
    nodata = info["nodata"]

    if nodata is not None:
        data[data == nodata] = np.nan

    if subsample > 1:
        data = data[::subsample, ::subsample]

    rows, cols = data.shape
    min_x, min_y, max_x, max_y = bounds
    xs = np.linspace(min_x, max_x, cols)
    ys = np.linspace(max_y, min_y, rows)  # top-to-bottom raster order

    suffix = output.suffix.lower()
    if suffix == ".obj":
        _write_obj(data, xs, ys, output, scale_xy=scale_xy, scale_z=scale_z)
    elif suffix == ".csv":
        _write_csv(data, xs, ys, output)
    else:
        raise ValueError(f"Unsupported output format '{suffix}'. Use .obj or .csv.")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="geotiff-to-blender",
        description="Export GeoTIFF terrain/bathymetry to Blender OBJ or QGIS CSV.",
    )
    p.add_argument("input", type=Path, help="Input GeoTIFF (.tif) file")
    p.add_argument(
        "--output", "-o", type=Path, default=None,
        help="Output file (.obj or .csv). Defaults to <input>.obj",
    )
    p.add_argument(
        "--subsample", type=int, default=1, metavar="N",
        help="Keep every Nth grid cell (default: 1 = full resolution)",
    )
    p.add_argument("--scale-xy", type=float, default=0.001,
                   help="XY scale for OBJ (metres → Blender units, default: 0.001)")
    p.add_argument("--scale-z", type=float, default=0.001,
                   help="Z scale for OBJ (default: 0.001)")
    p.add_argument("--verbose", "-v", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )

    if not args.input.exists():
        logger.error("Input file not found: %s", args.input)
        return 1

    output = args.output or args.input.with_suffix(".obj")
    try:
        convert(args.input, output,
                subsample=args.subsample,
                scale_xy=args.scale_xy,
                scale_z=args.scale_z)
        print(f"Written: {output}")
        return 0
    except Exception as exc:  # noqa: BLE001
        logger.error("Conversion failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
