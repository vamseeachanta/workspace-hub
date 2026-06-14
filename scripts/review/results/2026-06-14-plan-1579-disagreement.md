# Disagreement report — plan #1579 (2026-06-14)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | UNKNOWN |
| codex | MAJOR |
| gemini | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

(no findings unique to this provider)

### codex

- Plan §Pseudocode lines 229-239 claims description evidence can come from a “summary artifact,” but `load_existing_indexes()` only streams `path`, `old_path`, `content_hash`, `summary`, `target_repos`, `domain`, `source`, and `status`. The live `data/document-index/index.jsonl` has rows where `summary` is `null` while `summary_done: true` and `summary_file_exists: true`, and `.gitignore` lines 459-462 ignore `data/document-index/summaries/`. The plan does not define how to locate/read those ignored sidecar summaries, and the TDD list only tests inline `summary` at plan line 310. This can materially undercount described coverage.
- Plan §TDD Test List line 324 requires `test_tracked_artifacts_redact_private_wiki_and_client_tokens` to build a leak corpus from “wiki project rosters, observed private paths, `index.jsonl`, dedup report, and raw fixture filenames,” while the single test command at lines 332-335 gives no local-prerequisite gating or fixture-only boundary. `index.jsonl` and summaries are ignored local state per `.gitignore` lines 459-462, and private sibling/wiki paths are machine-specific. As written, the TDD suite can become non-deterministic across CI/dev machines or silently depend on private local mounts.
- Plan §Files to Change lines 289-291 and Acceptance Criteria lines 342-345 use run-scoped sequential refs in tracked artifacts, with the only ref-to-path mapping stored in ignored `tmp/issue-1579/ace-data-source-description-coverage.full.json`. `.gitignore` line 328 ignores all `tmp/`. If that tmp artifact is cleaned, the tracked decision queue and relocation ledger become unjoinable; the plan’s future-transaction safety claim at line 358 then depends on “regenerate or securely load” without specifying a durable local handoff, retention check, or checksum-to-artifact location contract.
- Plan Acceptance Criteria line 371 weakens the completeness rule by allowing `hermes` unavailability to fall back to only the issue-body stamp. `.claude/rules/completeness-before-close.md` lines 14-16 requires both `hermes kanban complete --metadata ...` and an issue-body stamp. If the plan intends a Codex-lane fallback, it needs to explicitly reconcile that exception with the rule instead of treating it as equivalent persistence.
- Plan §Final issue comment line 373 asks for “deletion count with evidence,” but the plan’s own scope says no move/delete is executed in this issue at lines 356-358. That wording is ambiguous enough to make closeout look like executed deletions were expected. It should require proposed-deletion count and executed-deletion count separately, with executed count fixed at zero.

### gemini

- **(MAJOR)** The plan actively dodges code scoring via the ops path, violating `.claude/rules/completeness-before-close.md`. The plan adds new implementation code (`scripts/data/ace_data_source_coverage.py`) and a test surface (`tests/data/test_ace_data_source_coverage.py`), but explicitly relies on the fact that `scripts/data` is unmapped to secure the easier `evidence` classification (`§Acceptance Criteria`: "expected derived class is evidence because scripts/data is not represented in the module-status path map"). The completeness rule explicitly forbids this: `Class is auto-derived from changed files, not selectable (no dodging code scoring via the ops path)`. The plan resolves the prior review's blocker by simply opting out of the `code` class, which is a compliance bypass. To add new code, the plan must either add a package mapping to the `module-status-matrix` (and solve the snapshot blocker properly) or explicitly justify why an audit script with full TDD tests qualifies as `ops/docs/governance, no test surface` under the `evidence` class.
- **(MINOR)** In `§Pseudocode`, the plan delegates the completeness HTML generation to `render_completeness_html.write_html`. However, the exact signature in `scripts/workflow/render_completeness_html.py` (`lines 63-68`) is `write_html(result: dict, issue: int, title: str, repo_root: Path | None = None)`. The `title` argument is a required positional string, but the plan does not source, reference, or pass an issue title in its pseudocode or AC. The invocation will fail with a `TypeError` at closeout unless the title argument is correctly supplied.
