### Verdict: REQUEST_CHANGES (P1s addressed in plan update)

### Summary
Solid plan with good phasing (copy-first-then-delete) and TDD sequencing. Two blockers: the riskiest script (update-orchestration-paths.py) lacks dry-run/backup safeguards unlike its sibling migration scripts, and the path-pattern coverage for script patching is dangerously narrow given 72 scripts likely use more than the two listed patterns.

### Issues Found
- [P1] Critical: `update-orchestration-paths.py` is the highest-risk script (it modifies live runtime dispatchers: dispatch-run.sh, exit_stage.py, gate-evidence helpers) yet it is the ONLY migration script without a specified dry-run mode or pre-patch backup. `migrate-scripts-to-stages.sh` gets dry-run; this script does not. If a regex/AST transform corrupts a dispatcher, the workspace breaks immediately. Add: (a) mandatory dry-run that emits a diff without writing, (b) atomic backup of each file before in-place patching, (c) rollback sub-command that restores from backup. **ADDRESSED: Added to plan AC and script spec.**
- [P1] Critical: Path-pattern coverage for script patching (child-c) only lists `sys.path.append(...)` and `source ../` as rewrite targets. Across 72 scripts it is near-certain that other path idioms exist: `__file__`-relative resolution (`os.path.dirname(__file__)`), `pathlib.Path(__file__).parent`, `subprocess.run(['bash', 'scripts/work-queue/stages/...'])`, hardcoded string paths in YAML/JSON configs, and `BASH_SOURCE`-relative sourcing. **ADDRESSED: Added path-pattern discovery step and coverage matrix to child-c ACs.**

### Suggestions
- Add a `--dry-run` flag and `--rollback` sub-command to `update-orchestration-paths.py`. **DONE.**
- Add a path-pattern discovery step to child-c. **DONE.**
