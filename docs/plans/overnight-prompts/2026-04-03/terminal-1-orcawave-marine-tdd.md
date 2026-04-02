# Terminal 1 — OrcaWave/Marine Pipeline TDD (Claude)

We are in /mnt/local-analysis/workspace-hub. Execute these 3 tasks in order.
Use `uv run` for all Python — never bare `python3` or `pip`.
Commit to `main` and push after each task. Do not branch.
TDD: write tests before implementation; mock external dependencies (no network, no OrcaWave license, no mounts).
Run `git pull origin main` before every push.
Do NOT ask the user any questions. Make reasonable decisions autonomously.

IMPORTANT: Do NOT write to any of the following paths — they are owned by other terminals:
- digitalmodel/tests/parametric_hull/ (Terminal 2)
- digitalmodel/tests/web/, digitalmodel/tests/field_development/, digitalmodel/tests/geotechnical/, digitalmodel/tests/nde/ (Terminal 3)
- scripts/document-intelligence/, data/document-index/, docs/document-intelligence/ (Terminal 4)
- digitalmodel/src/digitalmodel/{web,reservoir,infrastructure,marine_ops,solvers,hydrodynamics,specialized,signal_processing}/ (Terminal 5 docstrings)
- config/cron/, scripts/cron/ (Terminal 5)

Only write to:
- digitalmodel/src/digitalmodel/orcawave/
- digitalmodel/src/digitalmodel/specs/
- digitalmodel/tests/orcawave/
- digitalmodel/tests/specs/
- scripts/solver/ (only new files, not existing ones)
- data/hull-library/ (read-only reference, do not modify)

---

## TASK 1: Parametric spec.yml Generator (GH issue #1588)

Build a parametric spec.yml generator that bridges hull_library data to DiffractionSpec pipeline input.

### Context
- DiffractionSpec is defined in `digitalmodel/src/digitalmodel/orcawave/input_schemas.py` (~789 lines Pydantic v2)
- Hull library modules are in `digitalmodel/src/digitalmodel/naval_architecture/hull_library/`
- Existing spec files are at `digitalmodel/src/digitalmodel/orcawave/specs/` — see L00-L04 folders
- The generator should accept hull parameters (length, beam, draft, displacement) and produce a valid spec.yml

### Steps
1. Read `input_schemas.py` to understand DiffractionSpec schema
2. Read hull_library modules to understand available hull data (especially `rao_database.py`)
3. Write tests first: `digitalmodel/tests/orcawave/test_parametric_spec_generator.py`
   - Test: generate spec from minimal hull params → valid DiffractionSpec
   - Test: generate spec with frequency grid overrides
   - Test: generate spec referencing hull_library entry by name
   - Test: round-trip — generate spec → validate against schema → passes
4. Implement: `digitalmodel/src/digitalmodel/orcawave/parametric_spec_generator.py`
   - Class `ParametricSpecGenerator` with `from_hull_params()` and `from_hull_library(name)`
   - Method `generate_spec_yaml()` returns YAML string
   - Method `write_spec(output_dir)` writes spec.yml to disk
5. Run tests: `uv run pytest digitalmodel/tests/orcawave/test_parametric_spec_generator.py -v`

### Commit message
```
feat(orcawave): parametric spec.yml generator — hull_library to DiffractionSpec (#1588)
```

---

## TASK 2: RAO Extractor and Database Population Pipeline (GH issue #1597)

Build a pipeline to extract RAO data from .owr result files and populate RAODatabase.

### Context
- RAODatabase is in `digitalmodel/src/digitalmodel/naval_architecture/hull_library/rao_database.py`
- OrcaWave produces .owr result files (YAML-like format with frequency/heading/RAO data)
- The extractor should parse .owr files and insert into RAODatabase

### Steps
1. Read `rao_database.py` to understand the storage schema
2. Look at any existing .owr sample files or documentation in the orcawave directory
3. Write tests first: `digitalmodel/tests/orcawave/test_rao_extractor.py`
   - Test: parse a mock .owr file → extract frequency, heading, RAO arrays
   - Test: populate RAODatabase from extracted data
   - Test: handle missing/malformed .owr gracefully
   - Test: extract multiple vessel types from batch results
4. Implement: `digitalmodel/src/digitalmodel/orcawave/rao_extractor.py`
   - Class `RAOExtractor` with `parse_owr(path)` and `populate_database(db, results)`
   - Support batch extraction from a directory of .owr files
5. Run tests: `uv run pytest digitalmodel/tests/orcawave/test_rao_extractor.py -v`

### Commit message
```
feat(orcawave): RAO extractor pipeline — .owr results to RAODatabase (#1597)
```

---

## TASK 3: DiffractionSpec Reverse Parser (GH issue #1638)

Build a reverse parser that converts native OrcaWave YAML back to DiffractionSpec format.

### Context
- OrcaWaveBackend (in `digitalmodel/src/digitalmodel/orcawave/`) converts DiffractionSpec → native YAML
- The reverse parser goes the other direction: native OrcaWave YAML → DiffractionSpec
- This enables importing existing OrcaWave setups into the DiffractionSpec pipeline

### Steps
1. Read the OrcaWaveBackend code to understand the forward conversion
2. Study native OrcaWave YAML format in any existing examples
3. Write tests first: `digitalmodel/tests/orcawave/test_reverse_parser.py`
   - Test: round-trip — DiffractionSpec → native → reverse parse → matches original
   - Test: parse standalone native YAML → valid DiffractionSpec
   - Test: handle native YAML with fields not in DiffractionSpec (preserve as extras)
   - Test: error handling for invalid/incomplete native YAML
4. Implement: `digitalmodel/src/digitalmodel/orcawave/reverse_parser.py`
   - Function `native_to_diffraction_spec(yaml_path) -> DiffractionSpec`
   - Function `native_to_spec_yaml(yaml_path) -> str` (convenience wrapper)
5. Run tests: `uv run pytest digitalmodel/tests/orcawave/test_reverse_parser.py -v`

### Commit message
```
feat(orcawave): DiffractionSpec reverse parser — native YAML back to spec (#1638)
```

---

Post a brief progress comment on GH issues #1588, #1597, #1638 when each task completes.
