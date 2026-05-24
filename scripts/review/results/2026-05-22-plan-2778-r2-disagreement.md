# Disagreement report — plan #2778 (2026-05-22)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | UNAVAILABLE (claude CLI failed, rc=124: SessionEnd hook [node \"${CLAUDE_PLUGIN_ROOT}/scripts/session-lifecycle-hook.mjs\" SessionEnd] failed: Hook cancelled ) |
| codex | UNAVAILABLE (codex CLI failed, rc=124: Reading additional input from stdin... ) |
| gemini | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

(no findings unique to this provider)

### codex

(no findings unique to this provider)

### gemini

- **Python-in-Bash implementation mismatch (MAJOR)**
-    * **Citation:** Plan §Pseudocode for `check-wiki-sibling-frontmatter.sh`.
-    * **Defect:** The plan defines the enforcement script as a `.sh` (Bash) file but specifies execution logic using Pythonic constructs (e.g., `entry = registry.lookup(client)`, `frontmatter.get()`). Complex YAML parsing and dictionary lookups cannot be executed safely natively in POSIX shell or Bash. The plan fails to specify the addition of YAML-parsing dependencies (like `yq` or a Python runtime) to the hook installer's target environment.
- **Edge-case bucket slug mismatch (MAJOR)**
-    * **Citation:** Plan §Risks #4 and §Pseudocode Rule C (`expected_client_slug = repo_name[len("llm-wiki-"):]`).
-    * **Defect:** Risk #4 states the registry explicitly uses `client_projects` (with an underscore) as a bucket edge case. However, the `basename` substring derivation for repo `llm-wiki-client-projects` yields the slug `client-projects` (with a hyphen). The validation condition `if client != expected_client_slug` will immediately fail (`client_projects != client-projects`), rendering the asserted edge-case mitigation broken.
- **Missing execution of registry cron re-sync (MAJOR)**
-    * **Citation:** Plan §Risks #8.
-    * **Defect:** The mitigation for preventing stale registry data inside wiki repos relies on "a periodic cron re-syncs it". However, the §Files to Change table and §Acceptance Criteria omit any setup, shell script, or configuration file to instantiate this cron job. The vendored registry will rapidly become stale, causing false positives and blocking commits for newly onboarded clients.
- **Project template README frontmatter omission (MAJOR)**
-    * **Citation:** Plan §Artifact Map `templates/client-llm-wiki/projects/_template-project/README.md` and §Pseudocode filter logic (`elif is_client_wiki and path matches projects/**/*.md`).
-    * **Defect:** The enforcement script mandates strictly valid YAML frontmatter for all `projects/**/*.md` files. The plan introduces a new `README.md` to the project template skeleton but does not instruct adding valid YAML frontmatter to it. When an operator instantiates the template (e.g., `projects/sirocco/README.md`), the resulting README will immediately trigger a validation failure loop.
- **CI mode diff relies on local history in shallow clones (MAJOR)**
-    * **Citation:** Plan §Pseudocode CI mode logic `changed_files = git diff --name-only --diff-filter=ACM "${base_ref}..HEAD"`.
-    * **Defect:** CI environments standardly employ shallow clones (e.g., `fetch-depth: 1`). The target `${base_ref}` (defaulting to `origin/main`) will likely not exist in the local object store, causing `git diff` to throw a fatal error and break the build pipeline. The script lacks explicit instructions to fetch the base reference before comparing.
- **Bypass environment variable entirely omitted from logic (MINOR)**
-    * **Citation:** Plan §Enforcement script section: "Bypass + scope discipline: WIKI_FRONTMATTER_ALLOW=1".
-    * **Defect:** The corresponding pseudocode logic entirely omits any evaluation of the `WIKI_FRONTMATTER_ALLOW` environment variable. The explicit bypass rule will not be implemented unless the executing agent decides to hallucinate it into existence.
- **Vendored registry dirties working tree (MINOR)**
-    * **Citation:** Plan §Files to Change `scripts/agents/install-pre-commit-hook-cross-repo.sh`.
-    * **Defect:** The installer script will "vendor a copy of config/client-wikis.yml into each wiki repo's `.workspace-hub/`". The plan never specifies appending `.workspace-hub/` or the vendored file to the target wiki repos' `.gitignore`. This risks creating perpetually dirty working trees or unintentionally committing the registry into downstream wikis.

