### Verdict: REQUEST_CHANGES

### Summary
The stage-entry flow is close, but two correctness issues break advertised behavior in important paths. I did not find an obvious security problem in the provided code, but the fallback parsing and chained-stage handling need to be fixed before this should ship.

### Issues Found
- [P1] Critical: start_stage.py:29-44 The advertised no-dependency YAML fallback does not parse lists or nested structures, yet the rest of the script depends on list-valued fields like `exit_artifacts`, `entry_reads`, and `chained_stages`. On systems where `PyYAML` is unavailable, stage contracts will be loaded incorrectly and prompts/checklists will be incomplete or wrong.
- [P2] Important: start_stage.py:129-136 and start_stage.py:257-260 `chained_agent` is documented as writing a combined prompt for all chained stages, but `route_stage()` never loads or passes chained stage contracts into `build_prompt()`. The generated prompt only contains the current stage contract, so the agent will not receive the downstream stage requirements it is supposed to execute.
- [P3] Minor: start_stage.py:141-143 `build_prompt()` writes `stage-N-prompt.md` without ensuring `output_dir` exists. Stage 1 happens to create an evidence directory first, but non-stage-1 entry can still fail with `FileNotFoundError` if the WRK asset directory has not already been created.

### Suggestions
- Either make `PyYAML` a hard requirement for this script or replace `_load_yaml()` with a real fallback parser that preserves lists and nested mappings used by stage contracts.
- Implement actual chained-stage aggregation: resolve each stage listed in `chained_stages`, load those contracts, and pass them via `extra_contracts` so the prompt matches the documented behavior.
- Create `output_dir` inside `build_prompt()` or before any prompt generation so stage entry is robust regardless of prior filesystem state.
- Add focused tests for the no-`yaml` code path, `chained_agent` prompt composition, and stage entry when the WRK asset directory does not yet exist.

### Questions for Author
- Is `PyYAML` guaranteed on every machine that runs `uv run --no-project python scripts/work-queue/start_stage.py ...`, or is the fallback path expected to be production-safe?
- For `chained_stages`, should the combined prompt include full `entry_reads` and `exit_artifacts` for every downstream stage, or only a summary of later stages?
