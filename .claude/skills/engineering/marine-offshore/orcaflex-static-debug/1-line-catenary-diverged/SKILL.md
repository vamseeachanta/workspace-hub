---
name: orcaflex-static-debug-1-line-catenary-diverged
description: 'Sub-skill of orcaflex-static-debug: 1. Line Catenary Diverged (+4).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 1. Line Catenary Diverged (+4)

## 1. Line Catenary Diverged


**Symptoms:**
- Error mentions "catenary" or "line diverged"
- Specific line name in error message

**Causes:**
- Line too short for connection points
- Incorrect end positions
- Incompatible line type properties

**Solutions:**

```python
# Check line geometry
line = model["Failing_Line"]

# Get end positions
end_a_x, end_a_y, end_a_z = line.EndAX, line.EndAY, line.EndAZ
end_b_x, end_b_y, end_b_z = line.EndBX, line.EndBY, line.EndBZ

# Calculate required length (straight line minimum)
import math
min_length = math.sqrt(
    (end_b_x - end_a_x)**2 +
    (end_b_y - end_a_y)**2 +
    (end_b_z - end_a_z)**2
)

total_length = sum(line.Length)
print(f"Minimum length required: {min_length:.1f}m")
print(f"Total line length: {total_length:.1f}m")

if total_length < min_length * 1.1:
    print("Line is too short! Increase length by at least 10%")
```


## 2. Vessel Not in Equilibrium


**Symptoms:**
- "Vessel not in equilibrium"
- Large forces/moments on vessel

**Causes:**
- Mooring forces don't balance
- Incorrect initial position
- Missing or misconfigured lines

**Solutions:**

```yaml
# Option 1: Let OrcaFlex find equilibrium position
vessel:
  IncludedInStatics: "Included"
  CalculatedPosition: "Yes"  # Let OrcaFlex calculate position

# Option 2: Fix vessel position
vessel:
  IncludedInStatics: "Included"
  InitialX: 0.0
  InitialY: 0.0
  InitialZ: 0.0  # At draft
```


## 3. Anchor Not at Seabed


**Symptoms:**
- "End not at seabed"
- Anchor position mismatch

**Solutions:**

```python
# Ensure anchor is at seabed
water_depth = model.environment.WaterDepth

for line in lines:
    if line.EndAConnection == "Anchored":
        # Set anchor at seabed
        line.EndAZ = -water_depth

    if line.EndBConnection == "Anchored":
        line.EndBZ = -water_depth
```


## 4. Buoy/Structure Instability


**Symptoms:**
- 6D Buoy convergence failure
- Unrealistic rotations

**Solutions:**

```yaml
# Add constraints during statics
6DBuoy:
  Name: "CALM_Buoy"
  # Fix orientation during statics
  Constraint1: "Fixed"    # Fix X rotation
  Constraint2: "Fixed"    # Fix Y rotation
  Constraint3: "Free"     # Allow Z rotation (yaw)
```


## 5. Zero-Tension Lines


**Symptoms:**
- Singular stiffness matrix
- Lines with zero or negative tension

**Solutions:**

```python
# Check initial tensions
for line in lines:
    try:
        # Estimate initial tension from catenary
        weight_in_water = line.MassPerUnitLength * 9.81 * (1 - 1025/7850)
        length = sum(line.Length)

        # Very rough tension estimate
        estimated_tension = weight_in_water * length / 2

        if estimated_tension < 100:  # Very low tension
            print(f"Warning: {line.name} may have low tension")
            print("Consider:")
            print("  - Increasing line length")
            print("  - Adjusting end positions")
            print("  - Adding buoyancy")
    except:
        pass
```
