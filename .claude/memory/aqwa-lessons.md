# AQWA Backend Lessons

## DAT File Format (Non-Workbench / Standalone)

### Element Types
- `QPPL` = quad panel plate (radiation only)
- `QPPL DIFF` = quad panel plate, diffracting (REQUIRED for panel method)
- Without DIFF keyword, elements are classified as "NON-DIFFRACTING" and produce zero RAOs

### ILID Card (Internal Lid)
- `1ILID AUTO <group>` after ZLWL card
- Creates internal lid panels at waterline for irregular frequency removal
- Group number (e.g., 21) is assigned to auto-generated lid elements
- Without ILID, AQWA reports "REGLID:NO DIFFRACTING ELEMENTS FOUND"
- ILID fails if there are no DIFF elements in the model

### SEAG Card (Sea Grid)
- Non-Workbench mode: `SEAG ( nx, ny)` — 2 parameters only
- Workbench mode: `SEAG ( nx, ny, xmin, xmax, ymin, ymax)` — 6 parameters
- If 6 params provided in standalone mode, AQWA warns and uses defaults for grid size
- The warning about bounding box is non-fatal, but the `)` must be within 80 columns

### OPTIONS Cards
- `OPTIONS GOON` — continue past non-fatal errors (separate line, before feature OPTIONS)
- `OPTIONS LHFR SFBM MQTF REST END` — feature options
- GOON does NOT override FATAL mesh quality errors

### Mesh Quality (FATAL errors)
- "Elements must be at least 1.000 * Facet Radius apart" — FATAL, cannot override
- "Ratio of areas of adjacent elements must be greater than 0.333" — FATAL
- Both checked at 90-degree corners of box geometries
- Fix: panels must be roughly square (aspect ratio near 1:1)
- For 100m x 20m x 8m barge: nx=40, ny=8, nz=4 gives 704 panels that pass checks
- Facet radius = sqrt(panel_area / pi)
- At 90 deg corners: distance = sqrt((dim1/2)^2 + (dim2/2)^2) must >= max(facet_radius)

### Heading Convention
- AQWA outputs -180 to +180 degrees (9 headings for 5 requested)
- Symmetric barge: negative headings are automatically included
- Heading harmonization needed to filter to common headings with other solvers

## LIS File Parsing

### RAO Section
- Section header: "R.A.O.S-VARIATION WITH WAVE PERIOD/FREQUENCY"
- First occurrence = displacement RAOs (use this)
- Subsequent occurrences = velocity/acceleration RAOs (skip these)
- Lines with 15 fields: period, freq, heading, then 6 amp/phase pairs
- Lines with 14 fields: reuse previous heading (continuation)

### Added Mass / Damping Matrices
- Section header: "ADDED  MASS" (two spaces!) and "DAMPING"
- WAVE FREQUENCY line appears ~3 lines before ADDED MASS, ~23 lines before DAMPING
- Matrix rows have blank lines between them (not consecutive)
- Each frequency block: 6x6 matrix with X, Y, Z, RX, RY, RZ labels
- Search backward up to 30 lines for frequency info

### Units
- RAO translational: m/m
- RAO rotational: deg/m (not rad/m like OrcaWave)
- Added mass: kg (translational), kg.m (coupling), kg.m^2 (rotational)
- Damping: N.s/m, N.s, N.s.m
