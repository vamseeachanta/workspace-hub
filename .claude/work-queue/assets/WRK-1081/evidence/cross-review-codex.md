### Summary
The plan is directionally sound, but a few details will mis-specify the tools or weaken the gate. The main corrections are: use structured Bandit output instead of `-ll` text parsing, avoid count-only baselines, use the correct config format for Bandit/Radon, and split full-tree scans from staged-file pre-commit behavior.

### Issues Found
- High: The proposed Bandit severity approach is inconsistent with the acceptance criteria. In Bandit, `-ll` means "report MEDIUM or higher", so LOW findings are filtered out entirely. That means the plan cannot both "warn on LOW" and "block on MEDIUM+" with `-ll` alone. This affects the implementation described around [WRK-1081.md](/mnt/local-analysis/workspace-hub/.claude/work-queue/pending/WRK-1081.md#L27) and [WRK-1081.md](/mnt/local-analysis/workspace-hub/.claude/work-queue/pending/WRK-1081.md#L49). Use `-f json` (or Bandit’s baseline flow) and enforce the threshold in shell/Python logic instead of relying on the text filter flag.
- High: A per-repo count baseline is too lossy for blocking. If one old finding disappears and one new finding appears, the count is unchanged and the regression is missed. The baseline described at [WRK-1081.md](/mnt/local-analysis/workspace-hub/.claude/work-queue/pending/WRK-1081.md#L37) should store stable finding identities, not just counts. For Bandit, the native JSON baseline support is a better fit than a custom count-only file.
- Medium: The Bandit config plan is currently wrong on file format. A `.bandit` file is INI-style; TOML is supported via an explicitly passed config such as `pyproject.toml` with `-c`. The config statement at [WRK-1081.md](/mnt/local-analysis/workspace-hub/.claude/work-queue/pending/WRK-1081.md#L35) should not say ".bandit TOML".
- Medium: The Radon config section is also misnamed. Radon does read `pyproject.toml`, but its docs specify config under `[radon]`, not `[tool.radon]`. The Phase 3 plan should be corrected before implementation.
- Medium: The pre-commit design needs a separate invocation path from the full-suite script. If the hook is staged-files-only with `pass_filenames: true`, it should not reuse a recursive `bandit -r src/ ...` command, or it will rescan the full tree and defeat the staged-files intent. This affects the pre-commit behavior implied by [WRK-1081.md](/mnt/local-analysis/workspace-hub/.claude/work-queue/pending/WRK-1081.md#L39) and [WRK-1081.md](/mnt/local-analysis/workspace-hub/.claude/work-queue/pending/WRK-1081.md#L54).

### Suggestions
- For Bandit, run full-suite as JSON and gate in code: collect LOW/MEDIUM/HIGH separately, fail only when non-baselined MEDIUM/HIGH findings exist, and still print LOW findings as warnings.
- Change the baseline model from `repo -> count` to `repo -> findings[]`, keyed at least by tool, rule/test id, file, line, and a short message hash. For Bandit specifically, consider using native `-f json` plus `--baseline` support.
- Choose one Bandit config approach and make it explicit: either `.bandit` in INI format, or `pyproject.toml` under `[tool.bandit]` passed via `-c pyproject.toml`. Do not create TOML-formatted `.bandit` files.
- For Radon, use either `radon.cfg` or `pyproject.toml` with a `[radon]` section. `radon.cfg` is slightly less surprising; `pyproject.toml` is fine if the repos already centralize tool config there.
- Add one test covering the staged-file pre-commit path separately from the full-tree `check-all.sh` path. The current six tests miss that integration edge.
- Support an optional `vulture_whitelist.py` from day one, but keep it empty initially. Vulture explicitly recommends whitelist files for false positives, and that will matter once the repos hit decorators, plugin registries, or dynamic dispatch.

### Questions for Author
- Do you want the baseline to suppress only Bandit MEDIUM/HIGH findings, or also preserve warn-only baselines for Radon/Vulture so report drift is still visible over time?
- Will all five repos pin compatible Bandit/Radon/Vulture versions? If not, config behavior in `pyproject.toml` may diverge across repos and should be normalized first.
- Is the intent for pre-commit to scan only changed files, while CI/full-suite scans the whole repo? If yes, I would encode those as two different commands rather than one parameterized shell path.
