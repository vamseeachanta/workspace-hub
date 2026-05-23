# Disagreement report — plan #2778 (2026-05-22)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | UNAVAILABLE (claude CLI failed, rc=124: SessionEnd hook [node \"${CLAUDE_PLUGIN_ROOT}/scripts/session-lifecycle-hook.mjs\" SessionEnd] failed: Hook cancelled ) |
| codex | UNAVAILABLE (codex CLI failed, rc=3: INCOMPATIBLE (running under Claude-Code Bash — codex exec stdin-hangs regardless of version; upstream openai/codex#19945; see workspace-hub #2684; dispatch from a plain terminal OR unset the env var via 'env -u CLAUDECODE bash scripts/review/plan-review-fanout.sh ...' for Codex review) ) |
| gemini | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

(no findings unique to this provider)

### codex

(no findings unique to this provider)

### gemini

- **Repository context mismatch for `git diff` (MAJOR)**: Plan §Pseudocode uses `git diff --cached --name-only` to gather files, which outputs relative paths from the current repository root (e.g., `projects/sirocco/foo.md`). However, the `path matches:` filter expects paths containing the repository prefix (e.g., `llm-wiki-*/projects/**/*.md`). Because the output of `git diff` inside the sibling repository lacks the `llm-wiki-*/` prefix, the filter will fail to match any files, completely bypassing the validation. Additionally, `derive_repo_prefix_from_path(file)` will fail since the repo name is not present in the relative path.
- **CI vs. Pre-commit environment flaw (MAJOR)**: Plan §Deliverable states the script will "fail CI on staged content", while §Pseudocode uses `git diff --cached`. In a standard CI environment (like GitHub Actions), changes are already committed and the Git index is clean. `git diff --cached` will return empty, causing the script to exit 0 silently. If intended for CI validation, the script must diff against the base commit (e.g., `git diff HEAD~1..HEAD`); if intended as a local pre-commit hook, it will not fail CI.
- **Template path discrepancy (MAJOR)**: Plan §Resource Intelligence Summary explicitly notes that the `client-llm-wiki` template contains a `pages/` directory. However, the §Enforcement script pseudocode filters for `llm-wiki-*/wikis/**/*.md`. It omits `pages/`, meaning any non-project wiki content stored in the client-level `pages/` directory will be silently ignored during frontmatter validation.
- **Regex allowlist applied to YAML parser (MAJOR)**: Plan §Enforcement script claims that `templates/` paths are "exempt" via a "per-line sentinel allowlist" similar to `check-no-conflict-markers.sh`. However, the pseudocode explicitly includes `templates/client-llm-wiki/**/*.md` in the `wiki_files` to be checked via structured YAML parsing (`parse_yaml_frontmatter`). Since templates contain placeholder frontmatter (e.g., `client: <client-slug>`), the structured parser will read these placeholders, query the registry, and fail the script. Structured YAML validation cannot be skipped line-by-line using regex; the template paths must be excluded from `wiki_files` entirely.
- **Missing registry array validation (MINOR)**: Plan §Files to Change updates `config/client-wikis.yml` to include an optional `projects:` list per client. However, §Pseudocode Rule D only verifies that `visibility` is `private-client-llm-wiki` when a `project` is set; it does not validate that the `project:` value actually exists in the newly defined `projects:` registry list for that client, making the registry extension unused in validation.

