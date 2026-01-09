# OpenFOAM v2212 to v13 Migration Guide

## Overview

This guide helps migrate OpenFOAM cases from v2212 (ESI/OpenCFD) to v13 (OpenFOAM Foundation).

## Key Differences

### 1. Solver Names Changed

OpenFOAM v13 introduces a unified `foamRun` application with solver modules.

| v2212 Solver | v13 Equivalent |
|--------------|----------------|
| `simpleFoam` | `foamRun -solver incompressibleFluid` |
| `pisoFoam` | `foamRun -solver incompressibleFluid` |
| `pimpleFoam` | `foamRun -solver incompressibleFluid` |
| `buoyantSimpleFoam` | `foamRun -solver fluid` |
| `buoyantPimpleFoam` | `foamRun -solver fluid` |
| `multiphaseEulerFoam` | `foamRun -solver multiphaseEuler` |
| `interFoam` | `foamRun -solver incompressibleVoF` |
| `twoPhaseEulerFoam` | `foamRun -solver multiphaseEuler` |

### 2. System Dictionary Changes

#### controlDict

No major changes, but check:
```
application     simpleFoam;  // v2212
```
Changes to:
```
application     foamRun;     // v13
solver          incompressibleFluid;
```

#### fvSolution

Most settings remain compatible. Check for:
- `SIMPLE` algorithm → still supported
- `PIMPLE` algorithm → still supported
- `PISO` algorithm → still supported

#### fvSchemes

Most schemes are backward compatible. Check:
- `Gauss linear` → still supported
- `bounded Gauss upwind` → still supported

## Migration Steps

### Step 1: Backup Your Case

```bash
cp -r /path/to/your-case /path/to/your-case-v2212-backup
```

### Step 2: Load OpenFOAM v13

```bash
of13  # or: source /opt/openfoam13/etc/bashrc
```

### Step 3: Update controlDict

**Option A: Manual edit**

Edit `system/controlDict`:
```
application     foamRun;
solver          incompressibleFluid;  // choose appropriate solver module
```

**Option B: Keep old format** (compatibility mode)

OpenFOAM v13 may still recognize old solver names with warnings.

### Step 4: Check Boundary Conditions

Most boundary conditions are compatible, but verify:

```bash
cd your-case
foamDictionary -entry boundaryField -value 0/U
foamDictionary -entry boundaryField -value 0/p
```

### Step 5: Regenerate Mesh (if needed)

```bash
blockMesh
# or if using snappyHexMesh:
snappyHexMesh -overwrite
```

### Step 6: Test Run

```bash
# Run for a few time steps first
sed -i 's/endTime.*/endTime         0.01;/' system/controlDict
foamRun
```

### Step 7: Full Run

```bash
# Restore original endTime
foamRun
```

## Common Issues and Fixes

### Issue 1: "Unknown solver type"

**Error:**
```
Unknown solver type simpleFoam
```

**Fix:**
Update controlDict:
```
application     foamRun;
solver          incompressibleFluid;
```

### Issue 2: "Cannot find library"

**Error:**
```
cannot open shared object file: libincompressibleTransportModels.so
```

**Fix:**
Check `system/controlDict` libs entry and remove v2212-specific libraries.

### Issue 3: Boundary Condition Incompatibility

**Error:**
```
Unknown patchField type 'inletOutlet'
```

**Fix:**
Some BC names changed. Check:
- `inletOutlet` → `outletInlet` (reversed in some cases)
- Check v13 documentation for current BC names

### Issue 4: Function Objects

**Error:**
```
Unknown function object type
```

**Fix:**
Function object syntax may have changed. Update `system/controlDict`:

```
// Old v2212 format
functions
{
    forces
    {
        type    forces;
        ...
    }
}

// New v13 format (usually compatible)
functions
{
    forces
    {
        type    forces;
        libs    (forces);
        ...
    }
}
```

## Automated Migration Script

```bash
#!/bin/bash
# migrate_case_v2212_to_v13.sh

CASE_DIR="$1"

if [ -z "$CASE_DIR" ]; then
    echo "Usage: $0 <case_directory>"
    exit 1
fi

cd "$CASE_DIR" || exit 1

echo "Migrating case: $CASE_DIR"

# Backup
echo "Creating backup..."
cp -r ../$(basename "$CASE_DIR") ../$(basename "$CASE_DIR")-v2212-backup

# Update controlDict
echo "Updating controlDict..."
if grep -q "application.*simpleFoam" system/controlDict; then
    sed -i '/application/a solver          incompressibleFluid;' system/controlDict
    sed -i 's/application.*/application     foamRun;/' system/controlDict
fi

if grep -q "application.*pisoFoam" system/controlDict; then
    sed -i '/application/a solver          incompressibleFluid;' system/controlDict
    sed -i 's/application.*/application     foamRun;/' system/controlDict
fi

if grep -q "application.*pimpleFoam" system/controlDict; then
    sed -i '/application/a solver          incompressibleFluid;' system/controlDict
    sed -i 's/application.*/application     foamRun;/' system/controlDict
fi

echo "Migration complete. Test with: foamRun"
```

## Solver Module Reference

### incompressibleFluid

For incompressible, single-phase flows:
- Steady (SIMPLE) or transient (PISO/PIMPLE)
- Laminar or turbulent
- No density variation

**controlDict settings:**
```
application     foamRun;
solver          incompressibleFluid;
```

### fluid

For compressible flows with energy equation:
- Compressible
- Includes temperature/energy
- Natural convection, buoyancy

**controlDict settings:**
```
application     foamRun;
solver          fluid;
```

### incompressibleVoF

For multiphase with Volume of Fluid:
- Two immiscible phases
- Free surface tracking
- Interface capturing

**controlDict settings:**
```
application     foamRun;
solver          incompressibleVoF;
```

### multiphaseEuler

For Eulerian multiphase:
- Multiple phases
- Momentum exchange between phases
- Bubble columns, fluidized beds

**controlDict settings:**
```
application     foamRun;
solver          multiphaseEuler;
```

## Testing Your Migrated Case

### 1. Check Mesh

```bash
checkMesh
```

### 2. Initialize Fields

```bash
# If needed
setFields
```

### 3. Short Test Run

```bash
# Run for 10 time steps
foamRun -endTime 0.01
```

### 4. Check Results

```bash
# Check last time directory
foamListTimes
# View residuals
foamLog log.foamRun
gnuplot -e "plot 'logs/Ux_0' with lines"
```

### 5. Full Run

```bash
foamRun
```

## Performance Comparison

After migration, compare performance:

```bash
# v2212 timing (from old logs)
grep "ExecutionTime" log.simpleFoam | tail -1

# v13 timing
grep "ExecutionTime" log.foamRun | tail -1
```

OpenFOAM v13 often shows improved performance due to optimizations.

## Additional Resources

- **OpenFOAM v13 Release Notes**: https://openfoam.org/release/13/
- **User Guide**: https://doc.cfd.direct/openfoam/user-guide-v13
- **Migration Guide**: https://openfoam.org/news/v13-migration/

## Getting Help

If migration issues persist:

1. Check OpenFOAM forum: https://www.cfd-online.com/Forums/openfoam/
2. Review v13 tutorials for similar cases
3. Check solver documentation: `foamRun -solver <solver> -help`

## Rollback to v2212

If needed, you can run old cases with v2212:

```bash
# Unload v13
unalias of13 2>/dev/null

# Install and load v2212 (if needed)
sudo apt-get install openfoam2212
source /usr/lib/openfoam/openfoam2212/etc/bashrc

# Run case
simpleFoam
```
