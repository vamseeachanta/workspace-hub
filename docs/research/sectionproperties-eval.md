# sectionproperties Evaluation

**Library**: [sectionproperties](https://github.com/robbievanleeuwen/section-properties)
**Version**: 3.10.2 (Jan 2026) | **License**: MIT | **Stars**: ~550
**Install**: `pip install sectionproperties` (pure Python, deps: numpy, scipy, shapely, cytriangle)
**Issue**: #1452 | **Parent**: #1397

## Summary

sectionproperties computes geometric and warping properties of arbitrary cross-sections via FEM meshing. Supports AISC, Eurocode, and AS code-compliant calculations. Excellent accuracy for standard steel sections and hollow members.

## Hands-On Validation (2026-03-31)

Tested in `/mnt/local-analysis/sectionprops-env/` (Python 3.11, sectionproperties 3.10.2).

### AISC W-Shape Validation

| Section | Property | Computed | AISC Reference | Error |
|---------|----------|----------|----------------|-------|
| W14x22 | Area | 6.577 in² | 6.49 in² | 1.3% |
| W14x22 | Ixx | 202.4 in⁴ | 199 in⁴ | 1.7% |
| W14x22 | Iyy | 7.0 in⁴ | 7.00 in⁴ | 0.0% |
| W24x68 | Area | 20.349 in² | 20.1 in² | 1.2% |
| W24x68 | Ixx | 1863.5 in⁴ | 1830 in⁴ | 1.8% |

Note: ~1-2% discrepancy is expected from fillet radius approximation (8-point arc vs true radius). Finer `n_r` reduces error.

### Hollow Section Validation

| Section | Property | Computed | Analytical | Error |
|---------|----------|----------|------------|-------|
| CHS 24×0.5 | Area | 36.854 in² | 36.914 in² | 0.16% |
| CHS 24×0.5 | Ixx | 2541.2 in⁴ | 2549.4 in⁴ | 0.32% |
| RHS 12×8×0.375 | Area | 14.064 in² | — | — |
| RHS 12×8×0.375 | Ixx | 149.0 in⁴ | — | — |

### Arbitrary Geometry

Custom T-section defined via Shapely polygon coordinates — meshed and solved without issues. Area=24.0 in², Ixx=198.0 in⁴.

## API Notes

- `steel_sections` module has parametric builders: `i_section`, `circular_hollow_section`, `rectangular_hollow_section`, `angle_section`, `channel_section`, `tee_section`
- Requires explicit `.create_mesh(mesh_sizes=[...])` before analysis
- Warping properties (J, Cw, shear centre) available via `.calculate_warping_properties()`
- Arbitrary sections via `Geometry(shapely_polygon)` — handles any 2D shape

## Recommendation

**Adopt** — excellent fit for structural cross-section calculations in digitalmodel. Covers AISC/Eurocode standard sections and arbitrary offshore members (tubular joints, stiffened panels). Accuracy validated against reference values.

## Related Issues

- #1497 — AISC shapes database lookup
- #1498 — Production module in digitalmodel
- #1499 — Composite/multi-material section analysis PoC
- #1489 — scikit-fem eval (complementary for full FEM, but lacks section property focus)
