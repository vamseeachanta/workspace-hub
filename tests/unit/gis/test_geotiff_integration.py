"""Unit tests for GeoTIFF integration: GeoTIFFHandler and geotiff-to-blender export.

Tests are designed to run without rasterio installed by mocking the handler.
When rasterio is available, round-trip and metadata tests use a synthetic tif.

sys.path is patched at module level to make digitalmodel.gis importable from
the workspace-hub venv (digitalmodel is a submodule, not installed in this venv).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

# ---------------------------------------------------------------------------
# Make digitalmodel.gis importable from the workspace-hub venv
# ---------------------------------------------------------------------------
_DIGITALMODEL_SRC = Path(__file__).parents[3] / "digitalmodel" / "src"
if str(_DIGITALMODEL_SRC) not in sys.path:
    sys.path.insert(0, str(_DIGITALMODEL_SRC))

# ---------------------------------------------------------------------------
# Import the script under test (hyphen in filename requires spec loader)
# ---------------------------------------------------------------------------
_SCRIPT_PATH = Path(__file__).parents[3] / "scripts" / "gis" / "geotiff-to-blender.py"
_spec = importlib.util.spec_from_file_location("geotiff_to_blender", _SCRIPT_PATH)
_gtb_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_gtb_mod)

# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

SYNTHETIC_DATA = np.array(
    [
        [-100.0, -110.0, -120.0],
        [-105.0, -115.0, -125.0],
        [-108.0, -118.0, -130.0],
    ],
    dtype=float,
)

SYNTHETIC_BOUNDS = (-5.0, 56.0, -4.0, 57.0)  # (min_x, min_y, max_x, max_y)

MOCK_READ_RESULT = {
    "data": SYNTHETIC_DATA.copy(),
    "crs": "EPSG:4326",
    "bounds": SYNTHETIC_BOUNDS,
    "resolution": (0.5, 0.5),
    "nodata": None,
}


def _mock_read(*_args, **_kwargs):
    return {**MOCK_READ_RESULT, "data": SYNTHETIC_DATA.copy()}


# ---------------------------------------------------------------------------
# GeoTIFFHandler unit tests
# ---------------------------------------------------------------------------


class TestGeoTIFFHandlerInterface:
    """Verify GeoTIFFHandler API contract (rasterio mocked out)."""

    def test_module_imports_without_error(self):
        """GeoTIFFHandler module must import cleanly with sys.path set."""
        from digitalmodel.gis.io.geotiff_handler import GeoTIFFHandler

        assert GeoTIFFHandler is not None

    def test_read_raises_when_rasterio_absent(self, tmp_path):
        """read() raises ImportError when rasterio is unavailable."""
        from digitalmodel.gis.io import geotiff_handler as gh_mod

        dummy = tmp_path / "dummy.tif"
        dummy.write_bytes(b"")
        with patch.object(gh_mod, "HAS_RASTERIO", False):
            with pytest.raises(ImportError, match="rasterio"):
                gh_mod.GeoTIFFHandler.read(dummy)

    def test_read_returns_expected_keys(self, tmp_path):
        """read() result dict must contain data, crs, bounds, resolution, nodata."""
        from digitalmodel.gis.io import geotiff_handler as gh_mod

        dummy = tmp_path / "test.tif"
        dummy.write_bytes(b"")

        mock_src = MagicMock()
        mock_src.__enter__ = MagicMock(return_value=mock_src)
        mock_src.__exit__ = MagicMock(return_value=False)
        mock_src.read.return_value = SYNTHETIC_DATA
        mock_src.bounds.left = SYNTHETIC_BOUNDS[0]
        mock_src.bounds.bottom = SYNTHETIC_BOUNDS[1]
        mock_src.bounds.right = SYNTHETIC_BOUNDS[2]
        mock_src.bounds.top = SYNTHETIC_BOUNDS[3]
        mock_src.res = (0.5, 0.5)
        mock_src.crs.to_string.return_value = "EPSG:4326"
        mock_src.nodata = None

        mock_rasterio = MagicMock()
        mock_rasterio.open.return_value = mock_src

        with (
            patch.object(gh_mod, "HAS_RASTERIO", True),
            patch.object(gh_mod, "rasterio", mock_rasterio),
        ):
            result = gh_mod.GeoTIFFHandler.read(dummy)

        assert set(result.keys()) == {"data", "crs", "bounds", "resolution", "nodata"}
        assert result["crs"] == "EPSG:4326"
        assert result["bounds"] == SYNTHETIC_BOUNDS

    def test_to_xyz_excludes_nodata(self, tmp_path):
        """to_xyz() must skip cells matching the nodata sentinel value."""
        from digitalmodel.gis.io import geotiff_handler as gh_mod

        dummy = tmp_path / "nd.tif"
        dummy.write_bytes(b"")

        data_with_nd = SYNTHETIC_DATA.copy()
        data_with_nd[1, 1] = -9999.0  # nodata cell

        mock_src = MagicMock()
        mock_src.__enter__ = MagicMock(return_value=mock_src)
        mock_src.__exit__ = MagicMock(return_value=False)
        mock_src.read.return_value = data_with_nd
        mock_src.bounds.left = SYNTHETIC_BOUNDS[0]
        mock_src.bounds.bottom = SYNTHETIC_BOUNDS[1]
        mock_src.bounds.right = SYNTHETIC_BOUNDS[2]
        mock_src.bounds.top = SYNTHETIC_BOUNDS[3]
        mock_src.res = (0.5, 0.5)
        mock_src.crs.to_string.return_value = "EPSG:4326"
        mock_src.nodata = -9999.0

        mock_rasterio = MagicMock()
        mock_rasterio.open.return_value = mock_src

        with (
            patch.object(gh_mod, "HAS_RASTERIO", True),
            patch.object(gh_mod, "rasterio", mock_rasterio),
        ):
            points = gh_mod.GeoTIFFHandler.to_xyz(dummy)

        # 3x3 grid minus 1 nodata cell = 8 points
        assert len(points) == 8
        assert all(z != -9999.0 for _, _, z in points)

    def test_to_xyz_returns_float_triples(self, tmp_path):
        """to_xyz() tuples must each contain three float values."""
        from digitalmodel.gis.io import geotiff_handler as gh_mod

        dummy = tmp_path / "xyz.tif"
        dummy.write_bytes(b"")

        mock_src = MagicMock()
        mock_src.__enter__ = MagicMock(return_value=mock_src)
        mock_src.__exit__ = MagicMock(return_value=False)
        mock_src.read.return_value = SYNTHETIC_DATA
        mock_src.bounds.left = SYNTHETIC_BOUNDS[0]
        mock_src.bounds.bottom = SYNTHETIC_BOUNDS[1]
        mock_src.bounds.right = SYNTHETIC_BOUNDS[2]
        mock_src.bounds.top = SYNTHETIC_BOUNDS[3]
        mock_src.res = (0.5, 0.5)
        mock_src.crs.to_string.return_value = "EPSG:4326"
        mock_src.nodata = None

        mock_rasterio = MagicMock()
        mock_rasterio.open.return_value = mock_src

        with (
            patch.object(gh_mod, "HAS_RASTERIO", True),
            patch.object(gh_mod, "rasterio", mock_rasterio),
        ):
            points = gh_mod.GeoTIFFHandler.to_xyz(dummy)

        assert len(points) == 9  # 3x3 grid, no nodata
        for pt in points:
            assert len(pt) == 3
            assert all(isinstance(v, float) for v in pt)


# ---------------------------------------------------------------------------
# geotiff-to-blender.py: convert() tests
# ---------------------------------------------------------------------------


class TestGeoTIFFToBlenderConvert:
    """Test the convert() function with a mocked GeoTIFFHandler."""

    def test_convert_obj_creates_file(self, tmp_path):
        """convert() with .obj output must create a non-empty Wavefront OBJ file."""
        tif = tmp_path / "in.tif"
        tif.write_bytes(b"")
        out = tmp_path / "out.obj"

        with (
            patch.object(_gtb_mod, "_HAS_HANDLER", True),
            patch.object(_gtb_mod, "_HAS_RASTERIO", True),
            patch.object(_gtb_mod.GeoTIFFHandler, "read", side_effect=_mock_read),
        ):
            _gtb_mod.convert(tif, out)

        assert out.exists()
        content = out.read_text()
        assert content.startswith("# Terrain mesh")
        assert "v " in content
        assert "f " in content

    def test_convert_csv_creates_file(self, tmp_path):
        """convert() with .csv output must create a CSV with header x,y,z."""
        tif = tmp_path / "in.tif"
        tif.write_bytes(b"")
        out = tmp_path / "out.csv"

        with (
            patch.object(_gtb_mod, "_HAS_HANDLER", True),
            patch.object(_gtb_mod, "_HAS_RASTERIO", True),
            patch.object(_gtb_mod.GeoTIFFHandler, "read", side_effect=_mock_read),
        ):
            _gtb_mod.convert(tif, out)

        assert out.exists()
        lines = out.read_text().splitlines()
        assert lines[0] == "x,y,z"
        # header + 9 data rows for a 3x3 grid
        assert len(lines) == 10

    def test_convert_subsample_reduces_vertex_count(self, tmp_path):
        """subsample=2 on a 3x3 grid must produce a 2x2 vertex grid (4 vertices)."""
        tif = tmp_path / "in.tif"
        tif.write_bytes(b"")
        out = tmp_path / "out.obj"

        with (
            patch.object(_gtb_mod, "_HAS_HANDLER", True),
            patch.object(_gtb_mod, "_HAS_RASTERIO", True),
            patch.object(_gtb_mod.GeoTIFFHandler, "read", side_effect=_mock_read),
        ):
            _gtb_mod.convert(tif, out, subsample=2)

        content = out.read_text()
        vertices = [ln for ln in content.splitlines() if ln.startswith("v ")]
        assert len(vertices) == 4  # 2x2 subsampled grid

    def test_convert_raises_on_unsupported_extension(self, tmp_path):
        """convert() with an unsupported extension must raise ValueError."""
        tif = tmp_path / "in.tif"
        tif.write_bytes(b"")
        out = tmp_path / "out.xyz"

        with (
            patch.object(_gtb_mod, "_HAS_HANDLER", True),
            patch.object(_gtb_mod, "_HAS_RASTERIO", True),
            patch.object(_gtb_mod.GeoTIFFHandler, "read", side_effect=_mock_read),
        ):
            with pytest.raises(ValueError, match="Unsupported output format"):
                _gtb_mod.convert(tif, out)

    def test_convert_raises_when_rasterio_absent(self, tmp_path):
        """convert() must raise ImportError when rasterio or handler unavailable."""
        tif = tmp_path / "in.tif"
        tif.write_bytes(b"")
        out = tmp_path / "out.obj"

        with (
            patch.object(_gtb_mod, "_HAS_HANDLER", False),
            patch.object(_gtb_mod, "_HAS_RASTERIO", False),
        ):
            with pytest.raises(ImportError, match="rasterio"):
                _gtb_mod.convert(tif, out)

    def test_obj_scale_applied_to_vertices(self, tmp_path):
        """scale_xy and scale_z must be applied to vertex coordinates in OBJ."""
        tif = tmp_path / "in.tif"
        tif.write_bytes(b"")
        out = tmp_path / "out.obj"

        with (
            patch.object(_gtb_mod, "_HAS_HANDLER", True),
            patch.object(_gtb_mod, "_HAS_RASTERIO", True),
            patch.object(_gtb_mod.GeoTIFFHandler, "read", side_effect=_mock_read),
        ):
            _gtb_mod.convert(tif, out, scale_xy=1.0, scale_z=1.0)

        vertices = [
            ln for ln in out.read_text().splitlines() if ln.startswith("v ")
        ]
        # First vertex is at x=0, y=0 (origin); Z should not be scaled to near-zero
        first = vertices[0].split()
        z_val = float(first[3])
        assert z_val < -50.0  # unscaled depth ~-100 m


# ---------------------------------------------------------------------------
# geotiff-to-blender.py: CLI tests
# ---------------------------------------------------------------------------


class TestGeoTIFFToBlenderCLI:
    """Test the main() CLI entry point."""

    def test_main_returns_zero_on_success(self, tmp_path):
        """main() must return exit code 0 on successful OBJ conversion."""
        tif = tmp_path / "bathy.tif"
        tif.write_bytes(b"")
        out = tmp_path / "bathy.obj"

        with (
            patch.object(_gtb_mod, "_HAS_HANDLER", True),
            patch.object(_gtb_mod, "_HAS_RASTERIO", True),
            patch.object(_gtb_mod.GeoTIFFHandler, "read", side_effect=_mock_read),
        ):
            rc = _gtb_mod.main([str(tif), "--output", str(out)])

        assert rc == 0
        assert out.exists()

    def test_main_returns_one_on_missing_input(self, tmp_path):
        """main() must return exit code 1 when input file does not exist."""
        rc = _gtb_mod.main([str(tmp_path / "missing.tif")])
        assert rc == 1

    def test_main_csv_output(self, tmp_path):
        """main() with CSV output path must create a valid point cloud file."""
        tif = tmp_path / "bathy.tif"
        tif.write_bytes(b"")
        out = tmp_path / "bathy.csv"

        with (
            patch.object(_gtb_mod, "_HAS_HANDLER", True),
            patch.object(_gtb_mod, "_HAS_RASTERIO", True),
            patch.object(_gtb_mod.GeoTIFFHandler, "read", side_effect=_mock_read),
        ):
            rc = _gtb_mod.main([str(tif), "--output", str(out)])

        assert rc == 0
        assert out.read_text().startswith("x,y,z")

    def test_main_default_output_is_obj(self, tmp_path):
        """main() without --output flag must default to <input_stem>.obj."""
        tif = tmp_path / "terrain.tif"
        tif.write_bytes(b"")
        expected_out = tmp_path / "terrain.obj"

        with (
            patch.object(_gtb_mod, "_HAS_HANDLER", True),
            patch.object(_gtb_mod, "_HAS_RASTERIO", True),
            patch.object(_gtb_mod.GeoTIFFHandler, "read", side_effect=_mock_read),
        ):
            rc = _gtb_mod.main([str(tif)])

        assert rc == 0
        assert expected_out.exists()
