# Linked worktree detection audit

The inspected scripts contain directory-only discovery checks that omit linked
worktrees. Shared tier-1 resolution and content-index discovery now validate
working-tree roots through Git. Other findings below require consumer-specific
changes and tests; this audit does not claim ecosystem-wide remediation.

## Revision history

| Revision | Date | What changed and why |
| --- | --- | --- |
| Initial | 2026-10-22 | Inventory live repositories and correct shared discovery to accept linked worktrees. |
| 1 | 2026-10-25 | Refresh verification counts to include inherited-binding isolation and caller preservation cases. |

## Basis and observed coverage

Refs #3448. The related digitalmodel issue #662 records the original geometry
bridge work; its closed state does not establish that every provisioning
predicate has since been migrated. The live provisioning finding below remains.

The required repository set comes from `config/workstations/registry.yaml`;
`config/tier1-python-repos.txt` identifies its Python-tooling subset. The hub
was inspected in this worktree and each available sibling in its existing
checkout. No sibling files were modified. Observations were collected on
2026-10-22 before edits; locations below refer to those revisions.

| Repository | Observed layout | Revision | Tracked script files inspected | Candidate lines |
| --- | --- | --- | ---: | ---: |
| workspace-hub | linked worktree | 410bd3eb36c08be61b947713b08bd21afaf0119b | 1472 | 123 |
| digitalmodel | primary checkout | e92bcfe4d4e8df898ca79cc968ba682f1248636e | 713 | 8 |
| assetutilities | primary checkout | 8c8e83ef0f35400c050a45c9981b997e44b427dd | 56 | 6 |
| worldenergydata | primary checkout | 84e702f566fa26ccd00345dc9c9c4c46fa433199 | 332 | 7 |
| llm-wiki | not available as working-tree root | unavailable | 0 | 0 |
| assethold | primary checkout | 0e734cc7f406bd8b72a9a68672d027277437eaf9 | 21 | 1 |

Only tracked files under `scripts/` with `.sh`, `.py` or `.ps1` suffixes were
read. The candidate search selected lines matching this literal predicate
pattern (Python regular expression):

```text
(\[.*-d.*\.git|test\s+-d.*\.git|\.git.*(?:is_dir\(|isdir\(|exists\(|is_file\()|(?:isdir\(|exists\().*\.git)
```

The file set is reproducible with `git ls-files -z -- scripts`, followed by
suffix filtering and the expression above. Each matching line was classified
from its surrounding code. The inventory includes near matches so that
exclusions are visible rather than counted as repository discovery.

This boundary excludes untracked scripts, templates, other languages,
configuration, split-line or dynamically assembled predicates, sibling copies
outside the required set, and unavailable repositories. In particular, an
absent llm-wiki checkout was not inspected. No runtime safety claim is made
for scripts merely because their marker check accepts files.

## Classification and disposition

- **D — repository discovery:** a directory-only predicate can omit linked
  worktrees. Locations marked corrected use the shared Git-backed pattern;
  other locations need dedicated consumer tests before migration.
- **P — primary checkout only:** either an explicit safety restriction or a
  direct metadata-directory dependency. Retain until that contract is reviewed.
- **L — linked-worktree compatible marker:** accepts a file as well as a
  directory, or treats either as a repository boundary. This is a structural
  classification, not proof of valid Git metadata or environment isolation.
- **X — excluded:** test fixture, metadata binding, or near match unrelated to
  working-tree discovery.

No production candidate in this bounded search was intentionally specific to
bare-repository discovery. The bare-origin test below is classified X because
it queries a fixture with an explicit Git directory.

### workspace-hub

| Script | Lines at observed revision | Class | Disposition |
| --- | --- | --- | --- |
| `scripts/_core/sync-agent-configs.sh` | 230 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/_core/sync_statusline.sh` | 20 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/agents/claude_native_restore.py` | 63 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/agents/claude_runtime_transaction.py` | 96 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/agents/install-wiki-frontmatter-hook-cross-repo.sh` | 91 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/analysis/daily-reflect.sh` | 43 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/automation/consolidate_commands.py` | 548 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/automation/install_factory_all_repos.sh` | 36 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/automation/propagate-slash-commands.sh` | 66, 213 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/automation/propagate_claude_rules.sh` | 142 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/automation/propagate_updated_git_command.py` | 41 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/automation/setup_agents_folders.py` | 265 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/automation/setup_claude_memory_all_repos.sh` | 121 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/automation/sync_agent_configs.sh` | 69 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/automation/sync_and_propagate_commands.py` | 56, 224 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/automation/sync_resources.py` | 36 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/automation/sync_uv_commands.py` | 149 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/client_llm_wiki/bootstrap_git.py` | 180 | X | Excluded from migration: fixture or non-discovery use. |
| `scripts/coordination/context/analyze_patterns.sh` | 49 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/coordination/git/batch_commit_all.sh` | 19 | X | Excluded from migration: fixture or non-discovery use. |
| `scripts/coordination/git/check_all_repos_status.sh` | 27 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/coordination/git/check_trunk_status.sh` | 10 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/coordination/git/commit_and_sync_all.sh` | 86, 102 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/coordination/git/git_sync_all.sh` | 17 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/coordination/git/git_sync_all_enhanced.py` | 24 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/coordination/git/merge_and_cleanup_branches.sh` | 46 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/coordination/git/pull_all_repos.sh` | 25 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/coordination/git/push_all_repos.sh` | 28 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/coordination/git/remove_assetutilities_submodule.sh` | 58 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/coordination/git/resolve_repos.sh` | 124 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/coordination/git/sync-all-repos.sh` | 45, 144, 171, 200 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/coordination/git/sync_all_repos.sh` | 31 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/coordination/git/sync_repos.sh` | 73 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/coordination/repo_sync_batch.sh` | 39, 52, 74, 99 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/coordination/repository/check_all_status.sh` | 3 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/coordination/sync_objective_template.py` | 61 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/cron/commit-learning-artifacts.sh` | 149 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/cron/control-plane-drift.sh` | 43 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/cron/flywheel-review.py` | 45 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/cron/harness-update.sh` | 207, 221, 284, 310, 447, 468 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/cron/repo-ecosystem-hygiene-audit.sh` | 436, 570 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/data/research-literature/download_and_catalog.py` | 194 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/development/ai-review/install-codex-hooks.sh` | 108 | P | Primary-only implementation: writes directly into .git/hooks; detection alone is insufficient. |
| `scripts/development/ai-review/install-gemini-hooks.sh` | 88 | P | Primary-only implementation: writes directly into .git/hooks; detection alone is insufficient. |
| `scripts/ecosystem-sync/run.py` | 52 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/enforcement/check-client-wiki-registry.sh` | 154 | P | Private bootstrap binds a real metadata directory and rejects redirects. |
| `scripts/enforcement/check_no_new_claude_md.py` | 169 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/generate-resource-index.sh` | 183 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/install/codex-dispatch-prep.sh` | 95 | P | Explicit isolated-clone requirement; shared metadata is rejected. |
| `scripts/knowledge/tests/test_llm_wiki.py` | 130, 131 | X | Excluded from migration: fixture or non-discovery use. |
| `scripts/legal/tests/test_rule_authority_workflow.py` | 13 | X | Excluded from migration: fixture or non-discovery use. |
| `scripts/lib/tier1-repos.sh` | 51 | L | Corrected with Git-backed root validation; source-export fallback retained where applicable. |
| `scripts/lib/tier1_repos.py` | 57 | L | Corrected with Git-backed root validation; source-export fallback retained where applicable. |
| `scripts/maintenance/ai-tools-status.sh` | 235, 244 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/maintenance/repo-housekeeping.sh` | 142 | P | Explicit primary-only discovery avoids processing shared refs twice. |
| `scripts/maintenance/update-model-ids.sh` | 168 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/memory/bridge-hermes-claude.sh` | 69 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/memory/context-presence-report.py` | 19 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/memory/scope-repo-memory.sh` | 41 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/monitoring/tests/test_equivalence_sentinel.sh` | 71 | X | Excluded from migration: fixture or non-discovery use. |
| `scripts/operations/compliance/install_compliance_hooks.sh` | 24 | P | Primary-only implementation: writes directly into .git/hooks; detection alone is insufficient. |
| `scripts/operations/compliance/propagate_all_skills.sh` | 74 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/operations/compliance/propagate_guidelines.sh` | 63 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/operations/compliance/propagate_skill_references.sh` | 97 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/operations/monitoring/analyze_repo_health.py` | 307 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/operations/sanitize-machine-names.sh` | 61, 75 | X | Excluded from migration: fixture or non-discovery use. |
| `scripts/operations/surface-inventory.sh` | 37 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/operations/tests/test_job_queue_windows.py` | 307 | X | Excluded from migration: fixture or non-discovery use. |
| `scripts/operations/tests/test_workstation_hygiene.sh` | 67, 80, 116, 135, 139 | X | Excluded from migration: fixture or non-discovery use. |
| `scripts/operations/validate-file-placement.sh` | 146 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/operations/workstation-hygiene.sh` | 125, 132, 152 | P | Explicit clone-only sweep; linked worktrees are enumerated separately. |
| `scripts/operations/workstation-status.sh` | 81, 97 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/productivity/sections/branch-status.sh` | 29 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/productivity/sections/data-health.sh` | 29 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/productivity/sections/git-summary.sh` | 23 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/readiness/hermes-consistency-check.sh` | 44 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/readiness/nightly-readiness.sh` | 110 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/readiness/reconcile-ecosystem.sh` | 115 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/readiness/repair-sibling-sso-flow.py` | 120 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/readiness/telegram_hermes_readiness.py` | 117 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/repo-health.sh` | 47 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/repositories/work_surface_inventory.py` | 81 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/search/build_content_index.py` | 16 | D | Corrected with Git-backed root validation; source-export fallback retained where applicable. |
| `scripts/setup/mystran-build-linux.sh` | 55 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/skills/generate-skill-evals.py` | 43 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/skills/materialize_profile_schema.py` | 39 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/skills/merge-submodule-skills.sh` | 412 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/sync/sync-machine-branch.sh` | 28, 45 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/test/test-commit.sh` | 54, 68, 81 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/upkeep/health-check.sh` | 185 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/workstations/check-tier1-repo-baseline.py` | 49 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/workstations/core_equivalence.py` | 61 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/workstations/repo_footprint.py` | 250, 310, 318 | L | Retain; validates marker shape only or supplies a boundary check. |

### digitalmodel

| Script | Lines at observed revision | Class | Disposition |
| --- | --- | --- | --- |
| `scripts/automation/update_ai_agents_daily.sh` | 90 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/context/analyze_patterns.sh` | 49 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/cross_repo_change_propagator.py` | 124 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/git/git_manager.py` | 74, 215, 256 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/python/digitalmodel/tools/cleanup_stale_branches.py` | 381 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/setup/provision-cfd-box.sh` | 151 | D | Follow-up: directory-only clone/update selection remains; verification already calls rev-parse. |

### assetutilities

| Script | Lines at observed revision | Class | Disposition |
| --- | --- | --- | --- |
| `scripts/context/analyze_patterns.sh` | 49 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/deploy-enhanced-create-specs.sh` | 177 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/dev-env.sh` | 16, 158 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/setup-gitbash.sh` | 53, 163 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |

### worldenergydata

| Script | Lines at observed revision | Class | Disposition |
| --- | --- | --- | --- |
| `scripts/automation/update_ai_agents_daily.sh` | 90 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/context/analyze_patterns.sh` | 49 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |
| `scripts/reporting/generate_marketing_brochures.py` | 37 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/tools/convert_master_to_main.py` | 61 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/tools/git_all_repos.py` | 20 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/tools/git_commit_push_all_main.py` | 24 | L | Retain; validates marker shape only or supplies a boundary check. |
| `scripts/tools/quick_branch_check.sh` | 9 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |

### assethold

| Script | Lines at observed revision | Class | Disposition |
| --- | --- | --- | --- |
| `scripts/context/analyze_patterns.sh` | 49 | D | Follow-up: validate detection and downstream metadata/mutation behavior together. |

The classified totals are D: 70, P: 9, L: 52, X: 14. These are candidate-line counts,
not defect counts; multiple lines can belong to one behavior. Totals come from
the preceding inventory and include corrected locations at their base revision.

## Shared pattern and worked example

Source: Git [repository layout](https://git-scm.com/docs/gitrepository-layout),
and [rev-parse reference](https://git-scm.com/docs/git-rev-parse), options
`--local-env-vars`, `--is-inside-work-tree` and `--show-prefix`. Both were
opened successfully on 2026-10-22. Git documents a `.git` file pointing to
metadata and distinguishes being inside a working tree from being its root.

Inputs: an unborn primary checkout, a linked worktree created with Git, an
ordinary directory, and a bare repository. These commands need no commits or
identity overrides. `$example` is a caller-provided disposable directory.

```bash
git init -q "$example/primary"
git -C "$example/primary" worktree add --orphan -b example-linked "$example/linked"
git init -q --bare "$example/bare"
mkdir -p "$example/ordinary"
source scripts/lib/tier1-repos.sh
is_git_worktree_root "$example/linked"
```

Method: require a `.git` marker, ask Git for its repository-local environment
variable names, unset those names in the child, then inspect the successful
`rev-parse --is-inside-work-tree --show-prefix` response. The working-tree
answer must be `true` and the prefix must be empty. No Git configuration is
overridden and the parent environment is preserved.

| Input | Metadata | Git working-tree answer | Root decision |
| --- | --- | --- | --- |
| primary | directory | true, empty prefix | accept |
| linked | file pointing to metadata | true, empty prefix | accept |
| bare | no working-tree marker | false | reject |
| ordinary | absent | no valid repository | reject |
| child folder of primary | absent | inside ancestor, nonempty prefix | reject |
| malformed or empty marker | invalid | Git fails | reject |

The bare and markerless cases fail the marker precondition; the table describes
the independent Git semantics, rather than implying every rejected input is
probed. The Python equivalent is
`scripts.lib.git_worktree.is_git_worktree_root`. The tier-1 resolvers use this
predicate when metadata is present and preserve their existing `pyproject.toml`
fallback when metadata is absent. That fallback intentionally accepts source
exports and is not a claim that they are Git working trees.

## Verification and known limits

Focused tests exercise real Git-created layouts, separate metadata directories,
invalid and dangling markers, inherited Git bindings, precedence, source exports
and direct indexing. Expected outcomes follow the hand-derived decision table
in `tests/quality/test_git_worktree_detection.py`, not the implementation.
Existing resolver fixtures now initialize real metadata instead of making
empty directories. On 2026-10-25, the focused Python suites pass with 87 passed
and one optional private-data test skipped; 58 passing cases are in the new
regression module. The existing shell suites pass with 8 resolver, 7
consumer-layout and 38 quality assertions. Shell syntax and the documentation
register check pass.
The initial regression run recorded 31 failures and 16 passes before the
implementation; a subsequent standalone-command regression was also reproduced
before correction. These counts are observations of the test runs, not
acceptance limits. Git trust errors fail closed; repository identity,
authorization and race-free mutation remain consumer responsibilities.

### Baseline

Ruff reports `SIM102` at current content-index lines 77, 84 and 85 and
`FURB122` at line 155. The corresponding unchanged code is present at base
lines 72, 79, 80 and 150. ShellCheck reports `SC2317` at current helper line 97
(base line 78), and `SC2015` at resolver-test lines 14, 28 and 29 (base lines
14, 26 and 27). These baseline locations were confirmed by reading
`origin/main`; none of those statements was changed.

### Hooks that could not run

The hook framework is delegated to the publishing runner. Direct optional
checks could not run because Bats and Gitleaks are absent. The Bats invocation
reported `bats: command not found`; the existing secrets script reported
`ERROR: gitleaks not found in PATH`. No tools were installed or hooks bypassed.

## Follow-up

- Migrate remaining D predicates with focused regression tests in their owning
  repositories, including the provisioning clone/update selector above.
- Review hook installers using `git rev-parse --git-path hooks` and the intended
  shared-hook behavior before changing their P predicates.
- Preserve cleanup, isolated-clone and private-bootstrap restrictions until
  their specific safety contracts are reviewed.
- Audit the unavailable wiki checkout and predicates outside this search boundary.
- Obtain independent provider review before merge.
