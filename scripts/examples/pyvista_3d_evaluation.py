"""
PyVista 3D Visualization Evaluation
====================================
Integration example for vamseeachanta/workspace-hub#1448.

Demonstrates PyVista capabilities relevant to engineering workflows:
  1. Built-in mesh generation (sphere, cylinder, pipe geometry)
  2. STL import/export round-trip
  3. Mesh inspection (bounds, volume, quality)
  4. Offscreen rendering to PNG (headless/CI-compatible)
  5. Interactive rendering (when display is available)
  6. GPU information and performance timing

Requirements:
    pip install pyvista vtk numpy

Tested against PyVista 0.47.x, VTK 9.6.x, NVIDIA GTX 750 Ti.
"""

import sys
import time
import tempfile
import os
import warnings

import numpy as np

# Ensure offscreen rendering works even without a display
# (set before importing pyvista)
if "DISPLAY" not in os.environ:
    os.environ["PYVISTA_OFF_SCREEN"] = "true"

import pyvista as pv


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def environment_info():
    """Report PyVista, VTK, and GPU environment details."""
    print_section("1. Environment Info")
    print(f"  PyVista version : {pv.__version__}")

    import vtk
    print(f"  VTK version     : {vtk.vtkVersion.GetVTKVersion()}")
    print(f"  Python version  : {sys.version.split()[0]}")
    print(f"  NumPy version   : {np.__version__}")

    # GPU info
    try:
        gpu_info = pv.GPUInfo()
        print(f"  GPU info        : {gpu_info}")
    except Exception as e:
        print(f"  GPU info        : unavailable ({e})")

    # Report global theme
    print(f"  PyVista theme   : {pv.global_theme.name}")


def builtin_meshes():
    """Demonstrate built-in mesh primitives."""
    print_section("2. Built-in Mesh Primitives")

    meshes = {
        "Sphere": pv.Sphere(radius=1.0, theta_resolution=30, phi_resolution=30),
        "Cylinder": pv.Cylinder(radius=0.5, height=2.0, resolution=40),
        "Plane": pv.Plane(i_size=5, j_size=5, i_resolution=10, j_resolution=10),
        "Arrow": pv.Arrow(start=(0, 0, 0), direction=(1, 0, 0), scale=2.0),
        "Box": pv.Box(bounds=(-1, 1, -0.5, 0.5, -0.3, 0.3)),
    }

    for name, mesh in meshes.items():
        print(f"  {name:12s}: {mesh.n_points:6d} points, {mesh.n_cells:6d} cells, "
              f"bounds={[f'{b:.2f}' for b in mesh.bounds]}")

    return meshes


def pipe_geometry():
    """Create a sample pipe geometry relevant to offshore/subsea engineering."""
    print_section("3. Pipe Geometry (Engineering Example)")

    # Create a pipe by extruding a ring along a spline path
    # Spline path: gentle catenary-like curve
    n_points = 50
    t = np.linspace(0, 10, n_points)
    x = t
    y = np.zeros_like(t)
    z = 2.0 * np.cosh((t - 5) / 5) - 2.0 * np.cosh(0)  # catenary shape

    spline_points = np.column_stack((x, y, z))
    spline = pv.Spline(spline_points, n_points=200)

    # Create pipe by extruding a circle along the spline
    pipe = spline.tube(radius=0.15, n_sides=20)

    print(f"  Spline length   : {spline.length:.2f} m")
    print(f"  Pipe points     : {pipe.n_points}")
    print(f"  Pipe cells      : {pipe.n_cells}")
    print(f"  Pipe bounds     : x=[{pipe.bounds[0]:.2f}, {pipe.bounds[1]:.2f}]")
    print(f"                    y=[{pipe.bounds[2]:.2f}, {pipe.bounds[3]:.2f}]")
    print(f"                    z=[{pipe.bounds[4]:.2f}, {pipe.bounds[5]:.2f}]")

    return pipe, spline


def stl_roundtrip(mesh):
    """Test STL export and re-import."""
    print_section("4. STL Import/Export Round-Trip")

    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as f:
        stl_path = f.name

    try:
        # Export
        t0 = time.perf_counter()
        mesh.save(stl_path)
        export_time = time.perf_counter() - t0
        file_size = os.path.getsize(stl_path)
        print(f"  Exported to     : {stl_path}")
        print(f"  File size       : {file_size / 1024:.1f} KB")
        print(f"  Export time     : {export_time * 1000:.1f} ms")

        # Re-import
        t0 = time.perf_counter()
        reimported = pv.read(stl_path)
        import_time = time.perf_counter() - t0
        print(f"  Re-imported     : {reimported.n_points} points, {reimported.n_cells} cells")
        print(f"  Import time     : {import_time * 1000:.1f} ms")

        # Verify integrity
        orig_bounds = np.array(mesh.bounds)
        reimp_bounds = np.array(reimported.bounds)
        max_diff = np.max(np.abs(orig_bounds - reimp_bounds))
        print(f"  Bounds match    : max diff = {max_diff:.6f} (pass: {max_diff < 1e-3})")
    finally:
        os.unlink(stl_path)

    return reimported


def mesh_quality_analysis(mesh):
    """Compute and report mesh quality metrics."""
    print_section("5. Mesh Quality Analysis")

    # Use compute_cell_quality (deprecated in 0.47 but cell_quality segfaults on
    # tube meshes with VTK 9.6 --- revisit after PyVista 0.48+).
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        quality = mesh.compute_cell_quality(quality_measure="scaled_jacobian")
    q = quality["CellQuality"]

    print(f"  Quality metric  : Scaled Jacobian")
    print(f"  Min quality     : {q.min():.4f}")
    print(f"  Max quality     : {q.max():.4f}")
    print(f"  Mean quality    : {q.mean():.4f}")
    print(f"  Std quality     : {q.std():.4f}")

    # Volume (for closed meshes)
    if mesh.is_manifold:
        print(f"  Manifold        : Yes")
        print(f"  Volume          : {mesh.volume:.4f}")
    else:
        print(f"  Manifold        : No (volume not computable)")

    return quality


def offscreen_render(pipe, spline, output_dir):
    """Render scenes offscreen to PNG files (headless-compatible)."""
    print_section("6. Offscreen Rendering (Headless/CI)")

    pv.global_theme.background = "white"

    # --- Render 1: Pipe geometry with scalar coloring ---
    t0 = time.perf_counter()
    plotter = pv.Plotter(off_screen=True, window_size=(1280, 720))

    # Color pipe by Z-coordinate (depth)
    pipe["Depth"] = pipe.points[:, 2]
    plotter.add_mesh(pipe, scalars="Depth", cmap="coolwarm",
                     show_edges=False, opacity=1.0,
                     scalar_bar_args={"title": "Depth (m)"})

    # Add spline centerline
    plotter.add_mesh(spline, color="black", line_width=2, label="Centerline")

    plotter.add_axes()
    plotter.camera_position = "xz"

    pipe_png = os.path.join(output_dir, "pyvista_pipe_geometry.png")
    plotter.screenshot(pipe_png)
    render_time = time.perf_counter() - t0
    plotter.close()

    print(f"  Pipe render     : {pipe_png}")
    print(f"  Render time     : {render_time * 1000:.1f} ms")
    print(f"  Image size      : {os.path.getsize(pipe_png) / 1024:.1f} KB")

    # --- Render 2: Multi-object engineering scene ---
    t0 = time.perf_counter()
    plotter = pv.Plotter(off_screen=True, window_size=(1280, 720))

    # Seabed plane
    seabed = pv.Plane(center=(5, 0, -2.5), direction=(0, 0, 1),
                      i_size=14, j_size=4, i_resolution=20, j_resolution=10)
    plotter.add_mesh(seabed, color="sandybrown", opacity=0.5, label="Seabed")

    # Pipe
    plotter.add_mesh(pipe, scalars="Depth", cmap="viridis",
                     show_edges=False, opacity=0.9)

    # Platform anchor point
    platform = pv.Sphere(radius=0.3, center=(0, 0, 0))
    plotter.add_mesh(platform, color="red", label="Hang-off")

    # Touchdown point
    tdp = pv.Sphere(radius=0.2, center=(10, 0, pipe.bounds[4]))
    plotter.add_mesh(tdp, color="green", label="TDP")

    plotter.add_legend()
    plotter.add_axes()
    plotter.view_xz()

    scene_png = os.path.join(output_dir, "pyvista_engineering_scene.png")
    plotter.screenshot(scene_png)
    render_time = time.perf_counter() - t0
    plotter.close()

    print(f"  Scene render    : {scene_png}")
    print(f"  Render time     : {render_time * 1000:.1f} ms")
    print(f"  Image size      : {os.path.getsize(scene_png) / 1024:.1f} KB")

    # --- Render 3: Point cloud from mesh vertices ---
    t0 = time.perf_counter()
    plotter = pv.Plotter(off_screen=True, window_size=(1280, 720))

    cloud = pv.PolyData(pipe.points)
    cloud["elevation"] = pipe.points[:, 2]
    plotter.add_mesh(cloud, scalars="elevation", point_size=3,
                     render_points_as_spheres=True, cmap="plasma")
    plotter.add_axes()
    plotter.view_xz()

    cloud_png = os.path.join(output_dir, "pyvista_point_cloud.png")
    plotter.screenshot(cloud_png)
    render_time = time.perf_counter() - t0
    plotter.close()

    print(f"  Cloud render    : {cloud_png}")
    print(f"  Render time     : {render_time * 1000:.1f} ms")
    print(f"  Image size      : {os.path.getsize(cloud_png) / 1024:.1f} KB")

    return [pipe_png, scene_png, cloud_png]


def format_support_test():
    """Test reading/writing various 3D file formats."""
    print_section("7. File Format Support")

    mesh = pv.Sphere()
    formats = {
        ".stl": "STL (stereolithography)",
        ".ply": "PLY (polygon file)",
        ".vtk": "VTK (legacy)",
        ".vtp": "VTP (XML polydata)",
        ".obj": "OBJ (Wavefront)",
    }

    results = {}
    for ext, desc in formats.items():
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
            path = f.name
        try:
            mesh.save(path)
            reloaded = pv.read(path)
            ok = reloaded.n_points > 0
            results[ext] = ok
            status = "OK" if ok else "FAIL"
            print(f"  {desc:30s} : {status} ({os.path.getsize(path)/1024:.1f} KB)")
        except Exception as e:
            results[ext] = False
            print(f"  {desc:30s} : FAIL ({e})")
        finally:
            os.unlink(path)

    return results


def performance_benchmark():
    """Benchmark rendering performance with increasing mesh complexity."""
    print_section("8. Performance Benchmark")

    resolutions = [10, 30, 50, 100, 200]
    print(f"  {'Resolution':>12s}  {'Points':>8s}  {'Cells':>8s}  {'Render (ms)':>12s}")
    print(f"  {'-'*12}  {'-'*8}  {'-'*8}  {'-'*12}")

    for res in resolutions:
        mesh = pv.Sphere(theta_resolution=res, phi_resolution=res)

        plotter = pv.Plotter(off_screen=True, window_size=(800, 600))
        plotter.add_mesh(mesh, color="steelblue")

        t0 = time.perf_counter()
        plotter.screenshot()
        elapsed = (time.perf_counter() - t0) * 1000
        plotter.close()

        print(f"  {res:>12d}  {mesh.n_points:>8d}  {mesh.n_cells:>8d}  {elapsed:>12.1f}")


def main():
    """Run the full PyVista evaluation suite."""
    print("PyVista 3D Visualization Evaluation")
    print(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Output directory for rendered images
    output_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "reports", "pyvista-evaluation"
    )
    output_dir = os.path.normpath(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")

    # Run evaluation steps
    environment_info()
    meshes = builtin_meshes()
    pipe, spline = pipe_geometry()
    stl_roundtrip(pipe)
    mesh_quality_analysis(pipe)
    images = offscreen_render(pipe, spline, output_dir)
    format_support_test()
    performance_benchmark()

    # Summary
    print_section("9. Summary")
    print(f"  Rendered images : {len(images)}")
    for img in images:
        print(f"    - {img}")
    print(f"\n  Evaluation complete. All outputs in: {output_dir}")
    print(f"  PyVista is ready for engineering 3D visualization workflows.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
