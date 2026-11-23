---
name: paraview-interface-save-screenshots
description: 'Sub-skill of paraview-interface: Save Screenshots (+5).'
version: 1.1.0
category: engineering
type: reference
scripts_exempt: true
---

# Save Screenshots (+5)

## Save Screenshots


```python
def save_screenshot(view, filepath, resolution=(1920, 1080), transparent=False):
    """Save render view as image."""
    view.ViewSize = list(resolution)
    SaveScreenshot(
        filepath, view,
        ImageResolution=list(resolution),
        TransparentBackground=1 if transparent else 0,
    )
    print(f"Saved: {filepath}")
```


## Save Animation


```python
def save_animation(view, output_dir, prefix='frame', resolution=(1920, 1080)):
    """Save animation frames as image sequence."""
    view.ViewSize = list(resolution)
    SaveAnimation(
        f'{output_dir}/{prefix}.png', view,
        ImageResolution=list(resolution),
        FrameWindow=[0, GetAnimationScene().NumberOfFrames - 1],
    )
```


## Extract Data to CSV


```python
def extract_line_data(source, point1, point2, num_points=100, output_csv='line_data.csv'):
    """Extract data along a line (plot over line)."""
    plot_line = PlotOverLine(registrationName='LineProbe', Input=source)
    plot_line.Point1 = point1
    plot_line.Point2 = point2
    plot_line.Resolution = num_points

    # Save to CSV
    SaveData(output_csv, proxy=plot_line,
             ChooseArraysToWrite=0,
             Precision=8)
    print(f"Line data saved: {output_csv}")
    return plot_line

def extract_surface_integral(source, array_name, output_csv='surface_data.csv'):
    """Integrate variable over a surface."""
    integrate = IntegrateVariables(registrationName='Integral', Input=source)
    SaveData(output_csv, proxy=integrate)
    return integrate
```


## Parse CSV Output


```python
import csv

def parse_paraview_csv(csv_path):
    """Parse ParaView CSV export."""
    data = {}
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for key, value in row.items():
                key = key.strip().strip('"')
                if key not in data:
                    data[key] = []
                try:
                    data[key].append(float(value))
                except ValueError:
                    data[key].append(value)
    return data
```


## Common Filter Pipeline


```python
def build_standard_cfd_pipeline(reader):
    """Build standard CFD visualization pipeline."""
    results = {}

    # Velocity magnitude slice
    slice_filter = Slice(registrationName='ZSlice', Input=reader)
    slice_filter.SliceType = 'Plane'
    slice_filter.SliceType.Origin = [0, 0, 0]
    slice_filter.SliceType.Normal = [0, 0, 1]
    results['z_slice'] = slice_filter

    # Streamlines
    stream = StreamTracer(registrationName='Streams', Input=reader)
    stream.SeedType = 'Line'
    stream.SeedType.Point1 = [-1, -1, 0]
    stream.SeedType.Point2 = [-1, 1, 0]
    stream.SeedType.Resolution = 50
    stream.MaximumStreamlineLength = 20.0
    results['streamlines'] = stream

    # Contour (iso-surface)
    contour = Contour(registrationName='PressureIso', Input=reader)
    contour.ContourBy = ['POINTS', 'p']
    contour.Isosurfaces = [0.0]
    results['pressure_contour'] = contour

    # Calculator (derived quantity)
    calc = Calculator(registrationName='VelMag', Input=reader)
    calc.Function = 'mag(U)'
    calc.ResultArrayName = 'VelocityMagnitude'
    results['vel_magnitude'] = calc

    return results
```


## Filter Reference


| Filter | Purpose | Key Parameters |
|--------|---------|----------------|
| `Slice` | Cut plane through volume | `SliceType`, `Origin`, `Normal` |
| `Contour` | Iso-surface extraction | `ContourBy`, `Isosurfaces` |
| `StreamTracer` | Flow streamlines | `SeedType`, `MaximumStreamlineLength` |
| `Calculator` | Derived quantities | `Function`, `ResultArrayName` |
| `Clip` | Remove half of domain | `ClipType`, `InsideOut` |
| `Threshold` | Filter by value range | `ThresholdRange`, `Scalars` |
| `Glyph` | Vector arrows | `GlyphType`, `ScaleFactor` |
| `WarpByVector` | Deform mesh by vector | `Vectors`, `ScaleFactor` |
| `ExtractSurface` | Volume to surface | — |
| `CellDatatoPointData` | Interpolate cell→point | — |
| `IntegrateVariables` | Area/volume integrals | — |
| `PlotOverLine` | Line probe for XY plots | `Point1`, `Point2`, `Resolution` |
| `TemporalStatistics` | Time-averaged fields | `ComputeAverage`, `ComputeMinimum` |
