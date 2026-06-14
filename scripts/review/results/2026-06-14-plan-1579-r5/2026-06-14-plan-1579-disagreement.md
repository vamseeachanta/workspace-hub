# Disagreement report — plan #1579 (2026-06-14)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | MAJOR |
| codex | MAJOR |
| gemini | UNAVAILABLE (gemini CLI failed, rc=1: Warning: Basic terminal detected (TERM=dumb). Visual rendering will be limited. For the best experience, use a terminal emulator with truecolor support. Warning: 256-color support not detected. Using a terminal with at least 256-color support is recommended for a better visual experience. Ripgrep is not available. Falling back to GrepTool. Error when talking to Gemini API Full report available at:) |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

- **STALE / OVER-BROAD `llm-wiki*` SET — denominator + drift pollution (MAJOR).** Plan §169-172 presents as a verified "Live filesystem proof" that `/mnt/local-analysis` holds exactly three `llm-wiki*` checkouts: `llm-wiki`, `llm-wiki-acma`, `llm-wiki-fdas`. Re-running the plan's own command at review time returns a **fourth**: `llm-wiki-vbatch-165-review` (a transient verify-batch review clone, not a client sibling). The plan's wiki logic enumerates the live set with `find /mnt/local-analysis -maxdepth 1 -type d -name 'llm-wiki*'` and classifies any live repo lacking registry `raw_roots`/alias as `observed-unregistered` registry drift (pseudocode `map_to_llm_wiki` §266; AC §398). If implemented as written: (a) the scratch clone is emitted as a false `observed-unregistered` drift candidate plus a spurious registry-reconciliation decision-queue item; (b) it injects a bogus "per-`llm-wiki*` repo" coverage denominator into headline percentages (AC §397). The plan anticipates *git-status* drift (§45,457) but not *set-membership* drift, and has no filter distinguishing real siblings (`llm-wiki` / `llm-wiki-<slug>`) from transient `*-vbatch-*` / `*-review` / worktree clones. Test `test_llm_wiki_live_repo_set_is_recorded` (§346) records the set but asserts no sibling-vs-transient filter.
- **No correctness contract excluding non-sibling clones (MAJOR — same root cause/fix).** AC §396 ("live `llm-wiki*` repo set is enumerated and compared with `config/client-wikis.yml`; registry drift is reported") will, given finding #1, report a scratch review clone as drift. No acceptance criterion or test asserts transient/worktree clones are excluded (or routed to a distinct `transient-non-sibling` bucket rather than `observed-unregistered`). Needs an explicit filter requirement + a test fixture containing a `*-vbatch-*` / `*-review` clone proving it does not enter coverage denominators or the reconciliation queue.

### codex

- Plan live wiki evidence is false and the denominator policy has no exclusion/classification for transient wiki worktrees. Plan `docs/plans/2026-06-14-issue-1579-ace-data-source-coverage.md:44` claims the live set is only `/mnt/local-analysis/llm-wiki`, `llm-wiki-acma`, and `llm-wiki-fdas`; the embedded proof at lines 168-172 repeats that set. Live enumeration now returns `llm-wiki-vbatch-165-review` as well, with origin `https://github.com/vamseeachanta/llm-wiki.git`. Acceptance criterion line 397 requires coverage percentages for “each live `llm-wiki*` repo”, but the plan only defines drift handling for registered/unregistered client siblings, not task/review clones of the generic wiki. This can pollute wiki coverage denominators or create a false registry-drift queue item.
- The completeness closeout still selects an evidence class by rationale instead of following the repo’s non-selectable class contract. Plan pseudocode line 296 calls `score_evidence(evidence_items, issue_number=1579)` directly, and acceptance criterion line 407 says the issue will compute “an explicit evidence-class record” because it adds no package-mapped code under `src/`. But `.claude/rules/completeness-before-close.md:11-14` says class is auto-derived from changed files, not selectable, and `scripts/workflow/completeness_score.py:5-6` plus `scripts/workflow/completeness_score.py:83-95` implement that contract via `classify(changed_files, path_package_map)`. The plan changes executable code under `scripts/data/` and tests under `tests/data/` yet never requires running `classify()` against the actual path map or proving that these paths legitimately resolve to `evidence`. This remains a gate-bypass risk.

### gemini

- (none)
