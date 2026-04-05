# Plan Review

### Verdict: APPROVE

### Summary
The plan is solid and technically sound. It correctly leverages the existing `DiffractionSpec` schema (`input_schemas.py`) to standardize the benchmark inputs. The strategy to extract parameters from existing raw OrcaWave/AQWA files and migrate them to canonical `spec.yml` files is the right approach to establish a single source of truth. The verification method is appropriate.

### Issues Found
None.

### Suggestions
- **Path Verification**: Ensure the relative paths in `spec.yml` (e.g., `source_data/orcawave/barge_generated.gdf`) correctly point to the mesh files from the location of the `spec.yml` file. Based on your file structure, if `spec.yml` is in `docs/modules/orcawave/L02_barge_benchmark/` and the mesh is in `docs/modules/orcawave/L02_barge_benchmark/source_data/orcawave/`, the path `source_data/orcawave/...` is correct.
- **Mass Units**: Ensure consistent conversion of mass units (tonnes to kg) across all benchmarks, as `DiffractionSpec` expects SI units (kg).

### Questions for Author
None.
