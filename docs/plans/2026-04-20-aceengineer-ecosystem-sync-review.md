## Summary
Count of findings: Critical 0 / Major 3 / Minor 2 / Nit 1.

No CRITICAL finding currently blocks Tasks 7–11. Part B may proceed after this report is committed.

## Findings
### [MAJOR] Signal-detector tests hard-fail when local git fixtures have not been built
**Location:** tests/ecosystem-sync/test_signals_release.py:5-17; tests/ecosystem-sync/test_signals_casestudy.py:5-18; tests/ecosystem-sync/test_signals_readme.py:7-49; tests/ecosystem-sync/fixtures/repos/build_fixtures.sh:1-67
**Defect:** The release, case-study, and README tests assume locally built git fixture repos already exist. There is no `conftest.py` autobuild hook or skip/xfail guard. A clean checkout that has not run `build_fixtures.sh` produces hard failures instead of a self-healing test setup.
**Proof:** I temporarily moved `repo-with-release`, `repo-with-casestudy`, `repo-with-readme`, and `repo-with-casestudy.baseline-sha` out of `tests/ecosystem-sync/fixtures/repos/` and ran `uv run pytest tests/ecosystem-sync/test_signals_release.py tests/ecosystem-sync/test_signals_casestudy.py tests/ecosystem-sync/test_signals_readme.py -q`. Result: 9 failures, including `subprocess.CalledProcessError` from `git -C .../repo-with-release tag -l`, `FileNotFoundError` on `repo-with-casestudy.baseline-sha`, and `README.md` missing under `repo-with-readme`.
**Proposed fix:** Add a test bootstrap in `tests/ecosystem-sync/conftest.py` that checks for the required fixture repos and baseline file and runs `bash tests/ecosystem-sync/fixtures/repos/build_fixtures.sh` automatically when absent. If autobuild is intentionally rejected, make the tests skip with an explicit diagnostic rather than hard-failing.

### [MAJOR] `_extract_section` treats fenced code blocks as real headings and returns malformed section bodies
**Location:** scripts/ecosystem-sync/signals.py:143-158
**Defect:** `_extract_section()` scans raw lines and accepts any stripped line equal to `## <heading>`, even inside fenced code blocks. It then stops only at the next line starting with `## `, so a code fence can become the “section body” and leak closing backticks into the extracted text. This can create false README-diff signals from example snippets.
**Proof:** Running `_extract_section()` on markdown containing:

```md
# T
```md
## Capabilities
code
```

## Other
rest
```

returned `'code\n```'` instead of `''`. The current logic is exactly `if line.strip() == f"## {heading}":` followed by `if lines[j].startswith("## "):`.
**Proposed fix:** Parse headings with fence awareness. At minimum, track fenced-code state while scanning and ignore `##` markers inside fences; ideally use a markdown parser or a stricter regex anchored to unfenced ATX headings only.

### [MAJOR] Release-age cutoff checks commit date, not tag date, so recent annotated releases on older commits are silently dropped
**Location:** scripts/ecosystem-sync/signals.py:46-53
**Defect:** `detect_release_tag()` uses `git log -1 --format=%cI <tag>` and compares that parsed commit timestamp against the 90-day cutoff. For annotated tags created now on an older commit, `%cI` reports the commit date, not the tagger date, so a genuinely recent release can be excluded as “too old.”
**Proof:** In a temporary repo I created a commit dated `2025-01-01T00:00:00+00:00`, then created an annotated tag `v9.9.9` today. `git log -1 --format=%cI v9.9.9` returned `2025-01-01T00:00:00+00:00`, while `git for-each-ref refs/tags/v9.9.9 --format='%(taggerdate:iso-strict)'` returned today's timestamp `2026-04-20T10:29:27-05:00`. The detector would drop that tag under the current `<90 days old` rule despite the release tag being new.
**Proposed fix:** For annotated tags, read tagger date via `git for-each-ref` or `git cat-file tag`; for lightweight tags, fall back to commit date. Document the semantics explicitly and add tests for annotated tags on old commits.

### [MINOR] Symlinked import path is repo-correct on Linux but fragile on Windows/non-symlink filesystems
**Location:** scripts/ecosystem_sync (symlink); Task 1 symlink strategy in plan; import usage across tests and modules
**Defect:** The Python import path depends on `scripts/ecosystem_sync` being a real symlink to `scripts/ecosystem-sync`. This works in the current Linux repo, but clones on Windows or filesystems without symlink support may materialize a plain text file or no link at all, breaking imports.
**Proof:** `git ls-files --stage scripts/ecosystem_sync` shows mode `120000`, confirming a committed symlink. If checkout loses symlink semantics, imports such as `from scripts.ecosystem_sync.models import Signal` will fail before tests even start.
**Proposed fix:** Add a CI guard that asserts `scripts/ecosystem_sync` exists and resolves to `ecosystem-sync`, or replace the symlink approach with a supported package layout plus import-safe wrapper package.

### [MINOR] Production config is intentionally Linux-host-specific but not portable across the named multi-machine estate
**Location:** scripts/ecosystem-sync/config.yaml:1-23
**Defect:** All repo paths are hard-coded as `/mnt/local-analysis/workspace-hub/<repo>`. That is valid for `ace-linux-1`, but the file does not degrade gracefully on `ace-windows` or `ace-macos`, and there is no env-var expansion or host-specific override mechanism.
**Proof:** Every configured repo path uses the Linux mount root. The design file states the runner host is `ace-linux-1` and scope is “Local cron on ace-linux-1, daily at 6:00 AM CT,” so this is currently within scope, but it remains an explicit portability limitation.
**Proposed fix:** Either document `config.yaml` as host-bound and keep it that way, or support `${WORKSPACE_HUB}` / `${REPO_ROOT}` expansion so the same config can run on other machines later.

### [NIT] Commit-4 bypass history is real, but the current marker appears valid for ongoing work
**Location:** logs/hooks/plan-gate-events.jsonl:1-3; .planning/plan-approved/ecosystem-sync.md:1-9
**Defect:** The history shows the gate was blocked twice and then bypassed with `FORCE_PLAN_GATE=1`, which is process debt worth preserving in the review record.
**Proof:** `logs/hooks/plan-gate-events.jsonl` contains two `plan-gate-blocked` entries and one `plan-gate-bypassed` entry with note `FORCE_PLAN_GATE=1`. Current filesystem state:

```text
-rwxrwxrwx 1 vamsee vamsee 2230 Apr 20 02:26 .planning/STATE.md

.planning/plan-approved/:
...
-rwxrwxrwx 1 vamsee vamsee   714 Apr 20 09:53 ecosystem-sync.md
```

The marker is newer than `.planning/STATE.md`, contains user-approval wording, and is now old enough that the current hook's self-approval age check no longer flags it.
**Proposed fix:** None required for Part B. Keep the marker in place and do not repeat bypass behavior.

## Investigations performed
1. I inspected `signals.py` dedupe-key formats and explicitly checked the three requested probes: a case-study file named `released v1.0.0`, a README heading containing a colon, and a tag containing a slash. Because each detector prefixes a different namespace (`release:`, `case-study:`, `readme-diff:`), I did not find an actual key collision from those inputs. A colon inside the README heading makes the key less human-parseable, but not equal to a release/case-study key.

2. I tested fixture absence by temporarily moving the built fixture repos and baseline SHA file out of `tests/ecosystem-sync/fixtures/repos/`, then running the three signal test files with `uv run pytest ... -q`, and finally restoring the fixtures. Conclusion: without a prior `build_fixtures.sh` run, the suite fails hard in 9 places. I do not think the absence of a `conftest.py` autobuild hook is defensible in its current state.

3. I ran `_extract_section()` against four adversarial markdown cases using `uv run python`: (a) `## Capabilities` inside a fenced code block returned `'code\n```'`, which is wrong; (b) trailing whitespace on the heading line still matched and returned `'- one'`; (c) lowercase `## capabilities` returned `''`; (d) nested `### Capabilities` under an empty `## Features` section returned `''`. Conclusion: fenced-code handling is a real defect; the other three cases are current-behavior limitations but not all are necessarily bugs depending on desired heading strictness.

4. I reviewed `detect_release_tag()` and ran git probes in temporary repos. On this machine (`git version 2.43.0`), `%cI` is parseable by `datetime.fromisoformat`, and both lightweight and annotated tags returned ISO-8601 strings. The real problem is semantic: `%cI` reflects commit date, not annotated tagger date. Timezone-aware comparison against `datetime.now(timezone.utc)` is otherwise correct.

5. I simulated `git diff <missing-sha>..HEAD` in the case-study fixture repo with a bogus SHA. Git printed `fatal: Invalid revision range ...` and exited 128. `detect_new_case_study()` catches `subprocess.CalledProcessError` around the diff and returns `[]`, so rewritten history does not crash the detector. The failing-case example is a stale `last_commit_sha` pointing to a force-pushed-away commit.

6. I inspected `RepoState` in `state.py` and confirmed all mutable fields use `default_factory`. `run.py` does not yet exist, so I could not verify actual orchestrator usage, but nothing in the current dataclass definition aliases list/dict defaults across repos. I found no reuse bug in the present code.

7. I performed a YAML save/load/save-style round trip with a `RepoState` containing multiple dict/list fields. `yaml.safe_dump(sort_keys=True)` sorted mapping keys on disk, but `load_state()` reconstructed an equal dataclass object and `has_substantive_change(before, after)` returned `False`. Conclusion: canonical key ordering does not create false drift in the current implementation.

8. I checked symlink metadata with `git ls-files --stage scripts/ecosystem_sync`, which reported mode `120000`. That confirms the symlink is correctly committed. I then assessed portability risk: on Windows or any filesystem without symlink support, checkout/import behavior can break. I recommend a CI assertion for the symlink or a package-layout alternative.

9. I read `build_fixtures.sh` line by line. It is idempotent in the sense that it removes and rebuilds all fixture repos from scratch, and `set -euo pipefail` plus the `|| mkdir -p ...` pattern is sufficient for the `_draft` directory creation path. The remaining weakness is interruption: because the script starts with `rm -rf`, a partial run can leave the suite with missing fixtures until the script is rerun.

10. I searched the current changed surface for `kind="..."` constructors and found no inconsistent values like `releases` or `tag`. I also attempted type-checking, but neither `pyright` nor `mypy` is installed in this environment (`NO_TYPECHECKER`), so there is no tool-backed static-type confirmation yet.

11. I exercised `_previous_semver()` and `SEMVER_RE` directly. With only the current tag present, `_previous_semver(['v1.0.0'], 'v1.0.0')` returned `None`, which is sensible. With multiple semver tags pointing conceptually to the same commit, ordering still returns the previous semver string based on version sort, not commit topology. `SEMVER_RE.match('v0')` returned `False`, confirming `v0` is rejected; `v0.0` is accepted.

12. I inspected `scripts/ecosystem-sync/config.yaml` and cross-checked the design doc. The hard-coded `/mnt/local-analysis/workspace-hub/...` paths are not portable, but the design explicitly scopes the runner host to `ace-linux-1` and a local 6:00 AM CT cron. I therefore classified this as a portability limitation, not a current-scope blocker.

13. I inspected `logs/hooks/plan-gate-events.jsonl`, listed `.planning/plan-approved/` and `.planning/STATE.md`, and read `.planning/plan-approved/ecosystem-sync.md`. Conclusion: the bypass history is real and should remain documented, but the current marker file exists, is newer than `.planning/STATE.md`, and looks acceptable for Part B so long as no one deletes it or tries another bypass.