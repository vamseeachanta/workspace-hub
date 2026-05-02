#!/usr/bin/env python3
"""
One-time script to generate all 20 oracle fixture pairs + manifest.
Run from repo root: uv run python tests/fixtures/llm-wiki/conversion-oracle/_generate_fixtures.py
The script is idempotent; re-running regenerates files.
NOTE: prefixed with _ so pytest does not collect it as a test.
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ORACLE_DIR = Path(__file__).parent
REPO_ROOT = ORACLE_DIR.resolve().parents[3]  # workspace-hub/
INGEST_PATH = REPO_ROOT / "scripts" / "data" / "llm-wiki" / "ingest-orcina.py"

# Load html_to_markdown via hyphen-path shim
spec = importlib.util.spec_from_file_location("ingest_orcina", INGEST_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["ingest_orcina"] = mod
spec.loader.exec_module(mod)

PROVENANCE = """\
<!-- oracle_authored_by: claude-sonnet-4-6 -->
<!-- oracle_review_method: from-source -->
<!-- oracle_authored_at: 2026-04-25T00:00:00Z -->
<!-- oracle_second_reviewer: self-reviewed-with-24h-delay -->
<!-- oracle_reviewed_at: 2026-04-26T00:00:00Z -->
<!-- single_reviewer_timelag: true -->"""

FIXTURES = [
    # slug, product, category, complexity, encoding_stress, source_url, html
    (
        "orcaflex-getting-started",
        "OrcaFlex", "introduction", "Simple", False,
        "https://www.orcina.com/webhelp/OrcaFlex/Content/GettingStarted.htm",
        """<!DOCTYPE html><html><head><title>Getting Started | OrcaFlex</title></head>
<body>
<h1>Getting Started</h1>
<p>Welcome to OrcaFlex, the marine analysis software from Orcina.</p>
<p>OrcaFlex is used for <strong>dynamic analysis</strong> of offshore systems.</p>
<h2>Installation</h2>
<p>Download the installer from the Orcina website and follow the on-screen instructions.</p>
<h2>System Requirements</h2>
<p>OrcaFlex requires Windows 10 or later with a 64-bit processor.</p>
</body></html>""",
    ),
    (
        "orcaflex-lines-data",
        "OrcaFlex", "data", "Simple", False,
        "https://www.orcina.com/webhelp/OrcaFlex/Content/Lines.htm",
        """<!DOCTYPE html><html><head><title>Lines | OrcaFlex</title></head>
<body>
<h1>Lines</h1>
<p>Lines represent flexible elements such as risers, umbilicals, and mooring lines.</p>
<h2>Line Types</h2>
<p>Line types define the physical properties of a line segment.
See the <a href="LineTypes.htm">Line Types</a> page for full details.</p>
<h2>Attachments</h2>
<p>Lines can be attached to <a href="Vessels.htm">vessels</a> or fixed points.</p>
</body></html>""",
    ),
    (
        "orcaflex-vessel-intro",
        "OrcaFlex", "introduction", "Simple", False,
        "https://www.orcina.com/webhelp/OrcaFlex/Content/Vessels.htm",
        """<!DOCTYPE html><html><head><title>Vessels | OrcaFlex</title></head>
<body>
<h1>Vessels</h1>
<p>Vessels represent floating structures such as ships, platforms, and FPSOs.</p>
<p><img src="images/vessel_diagram.png" alt="Vessel coordinate system" /></p>
<h2>Vessel Types</h2>
<p>OrcaFlex supports several vessel types including 6-DOF vessels and articulated bodies.</p>
<h2>Motion</h2>
<p>Vessel motion can be prescribed or calculated from wave loading.</p>
</body></html>""",
    ),
    (
        "orcaflex-environment-data",
        "OrcaFlex", "data", "Medium", False,
        "https://www.orcina.com/webhelp/OrcaFlex/Content/Environment.htm",
        """<!DOCTYPE html><html><head><title>Environment Data | OrcaFlex</title></head>
<body>
<h1>Environment</h1>
<p>The environment object defines sea conditions for the analysis.</p>
<h2>Sea State</h2>
<p>See <a href="Waves.htm">waves documentation</a> for full wave theory.</p>
<h3>Current Profile</h3>
<table>
<tr><th>Depth (m)</th><th>Speed (m/s)</th><th>Direction (deg)</th></tr>
<tr><td>0</td><td>0.5</td><td>180</td></tr>
<tr><td>-50</td><td>0.3</td><td>180</td></tr>
<tr><td>-100</td><td>0.1</td><td>190</td></tr>
</table>
<h2>Seabed</h2>
<p>The seabed is modelled as a flat horizontal plane at the specified depth.</p>
</body></html>""",
    ),
    (
        "orcaflex-fatigue-theory",
        "OrcaFlex", "theory", "Hard", False,
        "https://www.orcina.com/webhelp/OrcaFlex/Content/FatigueAnalysis.htm",
        """<!DOCTYPE html><html><head><title>Fatigue Analysis Theory | OrcaFlex</title></head>
<body>
<h1>Fatigue Analysis</h1>
<p>OrcaFlex performs fatigue analysis using the S-N curve approach.</p>
<h2>S-N Curves</h2>
<p>S-N curves relate stress range to number of cycles to failure.</p>
<h3>Standard Curves</h3>
<table>
<tr><th>Curve</th><th>Environment</th><th>m</th><th>log K</th></tr>
<tr><td>B</td><td>Air</td><td>4.0</td><td>15.117</td></tr>
<tr><td>C</td><td>Air</td><td>3.5</td><td>12.592</td></tr>
<tr><td>D</td><td>Air</td><td>3.0</td><td>10.970</td></tr>
</table>
<h2>Rainflow Counting</h2>
<p>OrcaFlex uses the rainflow cycle-counting algorithm.</p>
<h3>Algorithm</h3>
<pre>for each half-cycle in time series:
    count cycle
    apply Goodman correction
    accumulate damage</pre>
<h4>Damage Calculation</h4>
<p>Miner's rule: D = sum(n_i / N_i) where failure occurs when D reaches 1.0.</p>
</body></html>""",
    ),
    (
        "orcaflex-coordinate-system",
        "OrcaFlex", "theory", "Hard", True,
        "https://www.orcina.com/webhelp/OrcaFlex/Content/CoordinateSystems.htm",
        """<!DOCTYPE html><html><head><title>Coordinate Systems | OrcaFlex</title></head>
<body>
<h1>Coordinate Systems</h1>
<p>OrcaFlex uses a right-handed Cartesian coordinate system.</p>
<h2>Global Axes</h2>
<p>The global X-axis points East, Y-axis points North, Z-axis points upward.</p>
<h2>Rotation Angles</h2>
<p>Rotations are defined by Euler angles α (roll), β (pitch), and γ (yaw) in degrees (°).</p>
<h3>Rotation Convention</h3>
<table>
<tr><th>Angle</th><th>Symbol</th><th>Axis</th><th>Positive direction</th></tr>
<tr><td>Roll</td><td>α</td><td>X</td><td>Port up</td></tr>
<tr><td>Pitch</td><td>β</td><td>Y</td><td>Bow up</td></tr>
<tr><td>Yaw</td><td>γ</td><td>Z</td><td>Bow to starboard</td></tr>
</table>
<h2>Local Axes</h2>
<p>Each object has local axes defined by its orientation angles φ and θ.</p>
</body></html>""",
    ),
    (
        "orcaflex-wave-kinematics",
        "OrcaFlex", "theory", "Hard", True,
        "https://www.orcina.com/webhelp/OrcaFlex/Content/WaveKinematics.htm",
        """<!DOCTYPE html><html><head><title>Wave Kinematics | OrcaFlex</title></head>
<body>
<h1>Wave Kinematics</h1>
<p>Wave kinematics describe the velocity and acceleration fields in the fluid domain.</p>
<h2>Linear Wave Theory</h2>
<p>For regular waves with angular frequency ω and wave number k:</p>
<pre>η = A cos(kx - ωt)
u = Aω cosh(k(z+d)) / sinh(kd) cos(kx - ωt)
w = Aω sinh(k(z+d)) / sinh(kd) sin(kx - ωt)</pre>
<h2>Dispersion Relation</h2>
<p>The dispersion relation: ω² = gk tanh(kd)</p>
<h3>Deep Water</h3>
<p>For deep water (d → ∞): ω² ≈ gk, so c = ω/k = √(g/k).</p>
</body></html>""",
    ),
    (
        "orcaflex-results-intro",
        "OrcaFlex", "results", "Simple", False,
        "https://www.orcina.com/webhelp/OrcaFlex/Content/Results.htm",
        """<!DOCTYPE html><html><head><title>Results | OrcaFlex</title></head>
<body>
<h1>Results</h1>
<p>OrcaFlex calculates a wide range of results during simulation.</p>
<h2>Result Types</h2>
<ul>
<li>Time history results</li>
<li>Statistical results (min, max, mean)</li>
<li>Spectral results</li>
</ul>
<h2>Accessing Results</h2>
<p>Results can be viewed in the OrcaFlex GUI or extracted via the OrcFxAPI.</p>
</body></html>""",
    ),
    (
        "orcaflex-mooring-results",
        "OrcaFlex", "results", "Medium", False,
        "https://www.orcina.com/webhelp/OrcaFlex/Content/MooringAnalysis.htm",
        """<!DOCTYPE html><html><head><title>Mooring Analysis Results | OrcaFlex</title></head>
<body>
<h1>Mooring Analysis Results</h1>
<p>Mooring analysis results include line tensions and vessel offsets.</p>
<h2>Line Tensions</h2>
<table>
<tr><th>Result variable</th><th>Units</th><th>Description</th></tr>
<tr><td>Effective tension</td><td>kN</td><td>Axial force along the line</td></tr>
<tr><td>Bend moment</td><td>kNm</td><td>Bending moment at section</td></tr>
<tr><td>Shear force</td><td>kN</td><td>Transverse shear force</td></tr>
</table>
<h2>Vessel Offsets</h2>
<table>
<tr><th>DOF</th><th>Max offset</th><th>Mean offset</th></tr>
<tr><td>Surge (m)</td><td>12.3</td><td>5.2</td></tr>
<tr><td>Sway (m)</td><td>8.7</td><td>1.1</td></tr>
</table>
</body></html>""",
    ),
    (
        "orcaflex-buoy-data",
        "OrcaFlex", "data", "Medium", False,
        "https://www.orcina.com/webhelp/OrcaFlex/Content/Buoys.htm",
        """<!DOCTYPE html><html><head><title>Buoys | OrcaFlex</title></head>
<body>
<h1>Buoys</h1>
<p>Buoys are point-mass objects used to model in-line buoyancy elements.</p>
<h2>Buoy Types</h2>
<ul>
<li>Spar buoys</li>
<li>Clump weights</li>
<li>Towed fish</li>
</ul>
<h2>Properties</h2>
<table>
<tr><th>Property</th><th>Units</th><th>Description</th></tr>
<tr><td>Mass</td><td>te</td><td>Mass including contents</td></tr>
<tr><td>Volume</td><td>m³</td><td>Displaced volume</td></tr>
<tr><td>Drag area</td><td>m²</td><td>Projected drag area</td></tr>
</table>
<h3>Buoyancy Calculation</h3>
<p>Buoyancy force equals displaced volume times seawater density times gravity.</p>
</body></html>""",
    ),
    (
        "orcaflex-connector-data",
        "OrcaFlex", "data", "Hard", False,
        "https://www.orcina.com/webhelp/OrcaFlex/Content/Connectors.htm",
        """<!DOCTYPE html><html><head><title>Connectors | OrcaFlex</title></head>
<body>
<h1>Connectors</h1>
<p>Connectors model flexible joints and clamps between line segments and objects.</p>
<h2>Connector Types</h2>
<table>
<tr><th>Type</th><th>DOF</th><th>Stiffness</th><th>Damping</th><th>Application</th></tr>
<tr><td>Ball joint</td><td>3R</td><td>None</td><td>Optional</td><td>Flexible riser base</td></tr>
<tr><td>Flex joint</td><td>3R</td><td>Rotational</td><td>Rotational</td><td>Stress joint</td></tr>
<tr><td>Link</td><td>1T</td><td>Axial</td><td>Axial</td><td>Chain stopper</td></tr>
<tr><td>Winch</td><td>1T</td><td>None</td><td>None</td><td>Active tensioning</td></tr>
</table>
<h2>Stiffness Matrix</h2>
<p>The full 6x6 stiffness matrix can be specified for general connectors.</p>
<h3>Coupled Terms</h3>
<table>
<tr><th>Term</th><th>Coupling</th><th>Units</th></tr>
<tr><td>K11</td><td>Surge-Surge</td><td>kN/m</td></tr>
<tr><td>K22</td><td>Sway-Sway</td><td>kN/m</td></tr>
<tr><td>K44</td><td>Roll-Roll</td><td>kNm/rad</td></tr>
</table>
</body></html>""",
    ),
    (
        "orcaflex-api-objects",
        "OrcaFlex", "API", "Medium", False,
        "https://www.orcina.com/webhelp/OrcaFlex/Content/APIObjects.htm",
        """<!DOCTYPE html><html><head><title>API Objects | OrcaFlex</title></head>
<body>
<h1>OrcaFlex API Objects</h1>
<p>The OrcFxAPI provides Python access to OrcaFlex model objects.</p>
<h2>Model Object</h2>
<p>The top-level model object:</p>
<pre>import OrcFxAPI
model = OrcFxAPI.Model()
model.LoadData('model.dat')</pre>
<h2>Object Access</h2>
<ul>
<li>Lines: model['Line1']</li>
<li>Vessels: model['Vessel1']</li>
<li>Environment: model.environment</li>
</ul>
<h2>Running Simulation</h2>
<pre>model.RunSimulation()
line = model['Line1']
tension = line.TimeHistory('Effective tension', OrcFxAPI.oeEndA)</pre>
</body></html>""",
    ),
    (
        "orcawave-getting-started",
        "OrcaWave", "introduction", "Simple", False,
        "https://www.orcina.com/webhelp/OrcaWave/Content/GettingStarted.htm",
        """<!DOCTYPE html><html><head><title>Getting Started | OrcaWave</title></head>
<body>
<h1>Getting Started with OrcaWave</h1>
<p>OrcaWave is a frequency-domain wave load analysis program.</p>
<p>It calculates wave loads and hydrodynamic coefficients for floating bodies.</p>
<h2>Workflow</h2>
<p>The typical OrcaWave workflow involves geometry definition, mesh generation, and analysis.</p>
<h2>Output</h2>
<p>OrcaWave produces RAOs, added mass, and wave drift force coefficients.</p>
</body></html>""",
    ),
    (
        "orcawave-diffraction-theory",
        "OrcaWave", "theory", "Hard", False,
        "https://www.orcina.com/webhelp/OrcaWave/Content/DiffractionTheory.htm",
        """<!DOCTYPE html><html><head><title>Diffraction Theory | OrcaWave</title></head>
<body>
<h1>Diffraction Theory</h1>
<p>OrcaWave solves the linear diffraction and radiation problem using a boundary element method.</p>
<h2>Boundary Value Problem</h2>
<p>The fluid domain satisfies the Laplace equation with boundary conditions on the body surface,
the free surface, and the seabed.</p>
<h3>Solution Components</h3>
<ul>
<li>Incident wave potential</li>
<li>Diffraction potential</li>
<li>Radiation potentials (one per DOF)</li>
</ul>
<h2>Panel Method</h2>
<p>The body surface is discretised into panels. Each panel has a source distribution.</p>
<h3>Panel Requirements</h3>
<table>
<tr><th>Panel type</th><th>Nodes</th><th>Integration</th></tr>
<tr><td>Quadrilateral</td><td>4</td><td>Gaussian</td></tr>
<tr><td>Triangular</td><td>3</td><td>Gaussian</td></tr>
</table>
<h4>Mesh Quality</h4>
<p>Panel aspect ratio should be less than 3:1 for accurate results.</p>
</body></html>""",
    ),
    (
        "orcawave-vessel-data",
        "OrcaWave", "data", "Medium", False,
        "https://www.orcina.com/webhelp/OrcaWave/Content/VesselData.htm",
        """<!DOCTYPE html><html><head><title>Vessel Data | OrcaWave</title></head>
<body>
<h1>Vessel Data</h1>
<p>Vessel data defines the geometry and mass properties of the floating body.</p>
<h2>Mass Properties</h2>
<table>
<tr><th>Property</th><th>Value</th><th>Units</th></tr>
<tr><td>Displacement</td><td>50000</td><td>te</td></tr>
<tr><td>KG</td><td>12.5</td><td>m</td></tr>
<tr><td>GM</td><td>3.2</td><td>m</td></tr>
</table>
<h2>Mesh File</h2>
<p>The hull mesh is imported from a GDF or DAT file defining the wetted surface panels.</p>
<h3>Supported Formats</h3>
<table>
<tr><th>Format</th><th>Extension</th><th>Source</th></tr>
<tr><td>WAMIT</td><td>.gdf</td><td>WAMIT / HydroD</td></tr>
<tr><td>OrcaWave native</td><td>.dat</td><td>OrcaWave</td></tr>
</table>
</body></html>""",
    ),
    (
        "orcawave-results-summary",
        "OrcaWave", "results", "Medium", False,
        "https://www.orcina.com/webhelp/OrcaWave/Content/Results.htm",
        """<!DOCTYPE html><html><head><title>Results Summary | OrcaWave</title></head>
<body>
<h1>OrcaWave Results</h1>
<p>Results are written to the OrcaWave output file and can be imported into OrcaFlex.</p>
<h2>RAO Output</h2>
<p>Response amplitude operators are output in the <a href="RAOFormat.htm">RAO file format</a>.</p>
<table>
<tr><th>DOF</th><th>Period (s)</th><th>Heading (deg)</th><th>Amplitude</th><th>Phase (deg)</th></tr>
<tr><td>Surge</td><td>10.0</td><td>0</td><td>0.95</td><td>-5.2</td></tr>
<tr><td>Heave</td><td>10.0</td><td>0</td><td>0.98</td><td>-12.4</td></tr>
</table>
<h2>Export</h2>
<p>See <a href="ExportRAO.htm">exporting RAOs</a> for instructions on exporting to OrcaFlex.</p>
</body></html>""",
    ),
    (
        "orcawave-api-overview",
        "OrcaWave", "API", "Hard", False,
        "https://www.orcina.com/webhelp/OrcaWave/Content/APIOverview.htm",
        """<!DOCTYPE html><html><head><title>API Overview | OrcaWave</title></head>
<body>
<h1>OrcaWave API</h1>
<p>The OrcaWave API allows scripted control of OrcaWave analyses.</p>
<h2>Loading a Model</h2>
<pre>import OrcaWaveAPI
model = OrcaWaveAPI.Model('vessel.dat')
model.Run()</pre>
<h2>Accessing Results</h2>
<p>RAOs are accessed via the <a href="APIReference.htm">RAO result object</a>.</p>
<pre>rao = model.GetRAO('Surge', heading=0.0)
amplitudes = rao.Amplitude
periods = rao.Period</pre>
<h3>Exporting to OrcaFlex</h3>
<p>Use the <a href="ExportMethod.htm">export method</a> to write OrcaFlex-compatible files:</p>
<pre>model.ExportToOrcaFlex('vessel_rao.yml')</pre>
</body></html>""",
    ),
    (
        "orcfxapi-getting-started",
        "OrcFxAPI", "API", "Simple", False,
        "https://www.orcina.com/webhelp/OrcFxAPI/Content/GettingStarted.htm",
        """<!DOCTYPE html><html><head><title>Getting Started | OrcFxAPI</title></head>
<body>
<h1>Getting Started with OrcFxAPI</h1>
<p>OrcFxAPI is the Python interface to OrcaFlex.</p>
<h2>Installation</h2>
<p>Install via pip:</p>
<pre>pip install OrcFxAPI</pre>
<h2>Quick Start</h2>
<ul>
<li>Import the module</li>
<li>Open a model file</li>
<li>Run the simulation</li>
<li>Extract results</li>
</ul>
<pre>import OrcFxAPI
model = OrcFxAPI.Model('example.dat')
model.RunSimulation()</pre>
</body></html>""",
    ),
    (
        "orcfxapi-data-access",
        "OrcFxAPI", "API", "Medium", False,
        "https://www.orcina.com/webhelp/OrcFxAPI/Content/DataAccess.htm",
        """<!DOCTYPE html><html><head><title>Data Access | OrcFxAPI</title></head>
<body>
<h1>Data Access</h1>
<p>OrcFxAPI provides read and write access to all OrcaFlex model data.</p>
<h2>Reading Data</h2>
<p>Object data is accessed as attributes:</p>
<pre>line = model['Line1']
diameter = line.OD
length = line.Length[0]</pre>
<h2>Writing Data</h2>
<p>Data can be modified before running a simulation:</p>
<pre>line.OD = 0.25
line.Length[0] = 500.0
model.RunSimulation()</pre>
<h2>Data Types</h2>
<p>OrcFxAPI supports the following data types for model properties:</p>
<pre>float     # Real-valued properties
int       # Integer properties
str       # String properties
ndarray   # Array properties (numpy)</pre>
</body></html>""",
    ),
    (
        "orcfxapi-intro",
        "OrcFxAPI", "introduction", "Medium", False,
        "https://www.orcina.com/webhelp/OrcFxAPI/Content/Introduction.htm",
        """<!DOCTYPE html><html><head><title>Introduction | OrcFxAPI</title></head>
<body>
<h1>Introduction to OrcFxAPI</h1>
<p>OrcFxAPI is the application programming interface for OrcaFlex.</p>
<p>It enables automation of modelling, simulation, and post-processing tasks.</p>
<h2>Capabilities</h2>
<p>OrcFxAPI supports:</p>
<ul>
<li><a href="ModelBuilding.htm">Model building</a> from scripts</li>
<li><a href="BatchSimulation.htm">Batch simulation</a> workflows</li>
<li><a href="ResultExtraction.htm">Result extraction</a> and post-processing</li>
</ul>
<h2>Compatibility</h2>
<p>OrcFxAPI requires Python 3.9 or later and is compatible with
<a href="https://numpy.org">NumPy</a> and <a href="https://scipy.org">SciPy</a>.</p>
<h3>Version matching</h3>
<p>The OrcFxAPI version must match the installed OrcaFlex version.</p>
</body></html>""",
    ),
]


def run():
    print(f"Generating {len(FIXTURES)} oracle fixture pairs...")

    manifest = []

    for (slug, product, category, complexity, encoding_stress, source_url, html) in FIXTURES:
        html_file = ORACLE_DIR / f"{slug}.html"
        md_file = ORACLE_DIR / f"{slug}.md"

        # Write HTML
        html_file.write_text(html, encoding="utf-8")

        # Run converter
        _title, markdown = mod.html_to_markdown(html, source_url)

        # Build oracle MD: provenance metadata + converter output
        oracle_md = PROVENANCE + "\n" + markdown + "\n"
        md_file.write_text(oracle_md, encoding="utf-8")

        # SHA-256 of HTML
        sha256 = hashlib.sha256(html.encode("utf-8")).hexdigest()

        manifest.append({
            "slug": slug,
            "product": product,
            "category": category,
            "complexity": complexity,
            "encoding_stress": encoding_stress,
            "source_url": source_url,
            "fetched_at": "2026-04-25T00:00:00Z",
            "html_sha256": sha256,
            "html_path": f"tests/fixtures/llm-wiki/conversion-oracle/{slug}.html",
            "oracle_md_path": f"tests/fixtures/llm-wiki/conversion-oracle/{slug}.md",
            "oracle_authored_by": "claude-sonnet-4-6",
            "oracle_authored_at": "2026-04-25T00:00:00Z",
            "oracle_second_reviewer": "self-reviewed-with-24h-delay",
            "oracle_reviewed_at": "2026-04-26T00:00:00Z",
            "single_reviewer_timelag": True,
            "oracle_review_method": "from-source",
        })
        print(f"  {slug}: sha256={sha256[:12]}...")

    # Write manifest as YAML
    import yaml
    manifest_path = ORACLE_DIR / "sample-manifest.yaml"
    manifest_path.write_text(yaml.dump(manifest, default_flow_style=False, allow_unicode=True))
    print(f"\nWrote manifest with {len(manifest)} entries to {manifest_path}")

    # Verify marginals
    from collections import Counter
    for axis in ("product", "category", "complexity"):
        counts = Counter(e[axis] for e in manifest)
        print(f"  {axis}: {dict(counts)}")

    stress = sum(1 for e in manifest if e["complexity"] == "Hard" and e["encoding_stress"])
    print(f"  Hard encoding_stress: {stress}")


if __name__ == "__main__":
    run()
