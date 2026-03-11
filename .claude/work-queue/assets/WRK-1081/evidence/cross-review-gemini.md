# WRK-1081 Cross-Review — Gemini (v1 issues; all resolved in v2+)
# WRK-1081 Plan Review — Gemini

## Verdict: REQUEST_CHANGES

### Issues Found

**High — Bandit `-ll` flag misused**
`-ll` filters to MEDIUM/HIGH only — LOW findings are NOT visible in output at all.
To "warn on LOW + block on MEDIUM+", must use `-f json` and parse severity in code.
Alternative: use bandit's native baseline: `bandit -f json -o bandit-baseline.json`, then
subsequent runs with `bandit -b bandit-baseline.json`.

**High — Baseline strategy too lossy**
`static-analysis-baseline.yaml` with counts only: if one old finding disappears and one
new finding appears, net count is unchanged and regression is missed.
Better: use tool-native baselines. Bandit has native JSON baseline support (`--baseline`).
Vulture: use `vulture_whitelist.py`. Radon: consider `xenon` for exit-code enforcement.

**Medium — `.bandit` config format wrong**
Bandit config files are YAML (not TOML). For TOML, embed under `[tool.bandit]` in
`pyproject.toml` and pass with `-c pyproject.toml`.

**Medium — `[tool.radon]` section wrong**
Radon reads `[radon]` in `setup.cfg` or `.radon.cfg`, not `[tool.radon]` in pyproject.toml.
Use `.radon.cfg` per repo (robust, standard).

**Medium — vulture exits non-zero by default**
`run_vulture()` must use `|| true` pattern or the pipeline blocks despite intent to warn-only.

**Medium — Pre-commit staged-file path**
`pass_filenames: true` with `bandit -r src/` rescans full tree, defeating staged-file intent.
Pre-commit hook must pass file args to bandit directly, not use `-r src/`.

### Suggestions
- Use `vulture src/ vulture_whitelist.py --min-confidence 80` with auto-generated whitelist
- Separate pre-commit command from full-suite command explicitly
- Consider `xenon` wrapper for radon if blocking-on-complexity needed later
