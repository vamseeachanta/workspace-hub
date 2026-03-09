# WRK-1073 AC Test Matrix

| # | Acceptance Criterion | Test | Result |
|---|---------------------|------|--------|
| 1 | AGENTS.md created for all 5 tier-1 repos (≤20 lines each) | `uv run --no-project python -c "..."` line count check | PASS |
| 2 | AGENTS.md has YAML frontmatter with required keys | frontmatter parse + key validation | PASS |
| 3 | `config/onboarding/repo-map.yaml` generated and committed | generator run + file existence check | PASS |
| 4 | repo-map.yaml contains all 5 repos with required fields | yaml.safe_load + field assertion | PASS |
| 5 | `generate-repo-map.py` produces valid YAML from AGENTS.md + pyproject.toml | idempotent re-run | PASS |
| 6 | Session-start SKILL.md updated with step 5b for repo-map context | manual review of SKILL.md | PASS |

## Test Run Output

```
PASS: assetutilities/AGENTS.md = 11 lines
PASS: digitalmodel/AGENTS.md = 11 lines
PASS: worldenergydata/AGENTS.md = 12 lines
PASS: assethold/AGENTS.md = 11 lines
PASS: OGManufacturing/AGENTS.md = 11 lines
PASS: assetutilities/AGENTS.md frontmatter OK
PASS: digitalmodel/AGENTS.md frontmatter OK
PASS: worldenergydata/AGENTS.md frontmatter OK
PASS: assethold/AGENTS.md frontmatter OK
PASS: OGManufacturing/AGENTS.md frontmatter OK
Written: config/onboarding/repo-map.yaml (5 repos)
PASS: 5 repos, all required fields present
```

## Notes

- Cross-review (AC5): Codex quota exhausted; Gemini REQUEST_CHANGES resolved (YAML frontmatter, error handling)
- Session-start integration tested by manual review; no runtime test possible without live session
