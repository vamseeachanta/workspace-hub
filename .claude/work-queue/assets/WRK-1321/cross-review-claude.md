### Verdict: REQUEST_CHANGES

### Summary
Solid plan with good phasing (copy-first-then-delete) and TDD sequencing. Two blockers: the riskiest script (update-orchestration-paths.py) lacks dry-run/backup safeguards unlike its sibling migration scripts, and the path-pattern coverage for script patching is dangerously narrow given 72 scripts likely use more than the two listed patterns.

### Issues Found
- [P1] Critical: `update-orchestration-paths.py` is the highest-risk script (it modifies live runtime dispatchers: dispatch-run.sh, exit_stage.py, gate-evidence helpers) yet it is the ONLY migration script without a specified dry-run mode or pre-patch backup. `migrate-scripts-to-stages.sh` gets dry-run; this script does not. If a regex/AST transform corrupts a dispatcher, the workspace breaks immediately. Add: (a) mandatory dry-run that emits a diff without writing, (b) atomic backup of each file before in-place patching, (c) rollback sub-command that restores from backup.
- [P1] Critical: Path-pattern coverage for script patching (child-c) only lists `sys.path.append(...)` and `source ../` as rewrite targets. Across 72 scripts it is near-certain that other path idioms exist: `__file__`-relative resolution (`os.path.dirname(__file__)`), `pathlib.Path(__file__).parent`, `subprocess.run(['bash', 'scripts/work-queue/stages/...'])`, hardcoded string paths in YAML/JSON configs, and `BASH_SOURCE`-relative sourcing. Any unpatched pattern will silently break after cutover. Add: (a) an explicit enumeration step in child-c that greps all path-construction patterns in the 72 scripts and produces a coverage report, (b) extend the patching spec to cover the discovered patterns, (c) add a post-patch test that imports/sources every patched script and asserts no FileNotFoundError / 'source: not found'.

### Suggestions
- Add a `--dry-run` flag and `--rollback` sub-command to `update-orchestration-paths.py`, matching the safeguards already given to `migrate-scripts-to-stages.sh`. The dry-run should output a unified diff per file.
- Add a path-pattern discovery step to child-c: `grep -rn 'os\.path\|pathlib\|__file__\|BASH_SOURCE\|source \|\$\{REPO_ROOT\}' scripts/work-queue/` → produce a coverage matrix of all path idioms found, then verify each is handled by the patching logic before proceeding to cutover.

### Questions for Author
- For `update-orchestration-paths.py`: is the intent to use Python AST rewriting (safe, structured) or regex (fast, fragile)? The plan says 'AST/regex' — which is the primary strategy and which is fallback? This matters because AST can't handle bash files and regex can't safely handle Python.
- Have you inventoried the actual path-construction patterns across the 72 scripts? If not, can you run a quick grep for `os.path`, `pathlib`, `__file__`, `BASH_SOURCE`, and hardcoded `scripts/work-queue` string literals to confirm the two listed patterns are sufficient?
