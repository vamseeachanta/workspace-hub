---
name: orcaflex-static-debug-basic-static-diagnosis
description: 'Sub-skill of orcaflex-static-debug: Basic Static Diagnosis.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Basic Static Diagnosis

## Basic Static Diagnosis


```python
import OrcFxAPI
from pathlib import Path

def diagnose_static_failure(model_path: str) -> dict:
    """
    Diagnose why static analysis might be failing.

    Args:
        model_path: Path to OrcaFlex model file

    Returns:
        Dictionary with diagnostic results
    """
    diagnostics = {
        "model_loaded": False,
        "issues": [],
        "warnings": [],
        "recommendations": []
    }

    try:
        model = OrcFxAPI.Model()
        model.LoadData(model_path)
        diagnostics["model_loaded"] = True
    except Exception as e:
        diagnostics["issues"].append(f"Failed to load model: {e}")
        return diagnostics

    # Check environment settings
    general = model.general

    # Wave should be off or very small for statics
    if hasattr(general, 'WaveType'):
        if general.WaveType != "None":
            diagnostics["warnings"].append(
                f"Wave type is '{general.WaveType}' - consider 'None' for statics"
            )

    # Check objects
    for obj in model.objects:
        obj_type = obj.typeName
        obj_name = obj.name

        # Check lines
        if obj_type == "Line":
            check_line(obj, diagnostics)

        # Check vessels
        elif obj_type == "Vessel":
            check_vessel(obj, diagnostics)

        # Check buoys
        elif obj_type in ["6D Buoy", "3D Buoy"]:
            check_buoy(obj, diagnostics)

    # Generate recommendations
    generate_recommendations(diagnostics)

    return diagnostics


def check_line(line, diagnostics: dict):
    """Check line configuration for common issues."""
    name = line.name

    # Check length
    try:
        total_length = sum(line.Length)
        if total_length <= 0:
            diagnostics["issues"].append(
                f"Line '{name}': Total length is {total_length}m (must be > 0)"
            )
    except:
        diagnostics["issues"].append(
            f"Line '{name}': Cannot read length - check Sections"
        )

    # Check connections
    try:
        end_a = line.EndAConnection
        end_b = line.EndBConnection

        if end_a == "Free" and end_b == "Free":
            diagnostics["issues"].append(
                f"Line '{name}': Both ends are Free - must have at least one connection"
            )
    except:
        pass

    # Check line type
    try:
        line_type = line.LineType
        if line_type is None or line_type == "":
            diagnostics["issues"].append(
                f"Line '{name}': No LineType assigned"
            )
    except:
        pass


def check_vessel(vessel, diagnostics: dict):
    """Check vessel configuration."""
    name = vessel.name

    # Check if vessel data is loaded
    try:
        displacement = vessel.Displacement
        if displacement <= 0:
            diagnostics["warnings"].append(
                f"Vessel '{name}': Displacement is {displacement} (check units)"
            )
    except:
        diagnostics["warnings"].append(
            f"Vessel '{name}': Cannot read displacement"
        )


def check_buoy(buoy, diagnostics: dict):
    """Check buoy configuration."""
    name = buoy.name

    # Check position
    try:
        z = buoy.InitialZ
        # Check if buoy is at reasonable depth
        if z > 100:  # Suspiciously high
            diagnostics["warnings"].append(
                f"Buoy '{name}': InitialZ = {z}m - check if this is intended"
            )
    except:
        pass


def generate_recommendations(diagnostics: dict):
    """Generate recommendations based on findings."""
    if diagnostics["issues"]:
        diagnostics["recommendations"].append(
            "Fix all issues before attempting static analysis"
        )

    if len(diagnostics["warnings"]) > 3:
        diagnostics["recommendations"].append(
            "Multiple warnings - consider simplifying model first"
        )

    if not diagnostics["issues"] and not diagnostics["warnings"]:
        diagnostics["recommendations"].append(
            "Model structure looks OK - try adjusting solver settings"
        )
```
