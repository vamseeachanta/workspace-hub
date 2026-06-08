# Plan for #2981: Make SKILL.md Frontmatter YAML-Valid for Review Dispatch

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-06-08
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2981
> **Client:** N/A
> **Project:** N/A
> **Review artifacts:** scripts/review/results/2026-06-08-plan-2981-claude.md | scripts/review/results/2026-06-08-plan-2981-gemini.md | scripts/review/results/2026-06-08-plan-2981-r1-*.md | scripts/review/results/2026-06-08-plan-2981-r2-*.md | scripts/review/results/2026-06-08-plan-2981-r3-*.md | scripts/review/results/2026-06-08-plan-2981-r4-codex.md | scripts/review/results/2026-06-08-plan-2981-r5-codex.md | scripts/review/results/2026-06-08-plan-2981-r6-codex.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `.claude/skills/coordination/flywheel-closeout/SKILL.md` has YAML frontmatter with an unquoted colon-bearing `description:` value. Strict YAML parsers reject this file.
- Found: `scripts/skills/validate-skills.sh` already validates all `.claude/skills/**/SKILL.md` files, but it uses shell/grep checks for `name:` and `description:` instead of parsing YAML.
- Found: `.github/workflows/skills-validation.yml` runs `bash scripts/skills/validate-skills.sh`, but currently sets `continue-on-error: true`, says validation is soft-fail, and does not install Python/YAML dependencies before the script runs.
- Found: `tests/enforcement/test_check_wiki_sibling_frontmatter.py` provides a nearby hermetic subprocess-test pattern for frontmatter validation scripts.
- Found: `scripts/skills/audit_skill_lib.py` has `parse_frontmatter(content)` using `yaml.safe_load`, but it is audit-oriented: it returns `None` on parser failure, uses `content.lstrip()` plus `stripped.find("---", 3)` rather than a delimiter-line contract, and does not return structured validation errors suitable for a fail-closed enforcement script.
- Found: `scripts/skills/weekly_skills_audit.py` has `_extract_frontmatter(skill_md)` and `build_inventory()`, but it excludes `_archive` and `_diverged` by policy. This issue intentionally validates `_archive` too because the current dispatch failure came from loader/indexing behavior rather than a weekly quality report scope.
- Gap: no existing test proves that `scripts/skills/validate-skills.sh` catches malformed YAML frontmatter.

### Standards

| Standard | Status | Source |
|---|---|---|
| Issue planning gate | applies | `.claude/skills/coordination/issue-planning-mode/SKILL.md` |
| TDD mandatory | applies | `AGENTS.md` / SHARED_SOUL hard gate |
| Legal/security scan | applies | `scripts/legal/legal-sanity-scan.sh` |

### LLM Wiki pages consulted

- N/A — this plan does not touch wiki content or wiki repositories.

### Documents consulted

- [#2981](https://github.com/vamseeachanta/workspace-hub/issues/2981) — states the broken `flywheel-closeout` frontmatter and acceptance criteria.
- `origin/plan/issue-2975-ecosystem-wiki-flywheel-contract:scripts/review/results/2026-06-08-plan-2975-claude.md` — records the formal review finding that Codex failed to load `flywheel-closeout/SKILL.md` due invalid YAML.
- `docs/plans/_template-issue-plan.md` — plan shape and required evidence contract.
- `docs/plans/README.md` — plan index to update.

### Gaps identified

- `scripts/skills/validate-skills.sh` will need to delegate to a small Python helper so malformed frontmatter fails deterministically without running one Python process per skill file.
- Existing parsers in `scripts/skills/audit_skill_lib.py` and `scripts/skills/weekly_skills_audit.py` are not direct replacements for this issue's fail-closed validator. Implementation should either reuse a shared extraction primitive from `audit_skill_lib.py` after making it delimiter-line/structured-error safe, or keep the new helper narrowly scoped and file a follow-up parser-consolidation issue. It must not silently rely on the existing fail-open parser behavior.
- Tests will need a fixture that contains an unquoted colon-bearing description and proves the validator fails on it.
- `.github/workflows/skills-validation.yml` will need explicit `uv` setup, actual pytest execution for the new regression tests, and path filters for the new helper/test files before hard-fail posture is safe.
- The workflow will remove `continue-on-error: true` after `uv` setup is added and the live inventory passes. This is a deliberate hard-fail decision, not an open question.

### Evidence

**Issue statuses** (verified 2026-06-08T18:51:02Z via `gh issue view`):
- [#2981](https://github.com/vamseeachanta/workspace-hub/issues/2981) — OPEN — `fix: make SKILL.md frontmatter YAML-valid for review dispatch`

**File existence and scope**:
```
$ find .claude/skills -name SKILL.md | wc -l
3111
```

```
$ find docs/plans -maxdepth 1 -name '*2981*' -o -name '*skill-frontmatter*'
<no output before this plan was created>
```

**Line excerpts**:
```
$ sed -n '1,12p' .claude/skills/coordination/flywheel-closeout/SKILL.md
---
name: flywheel-closeout
description: Use this at the end of substantial repo or agent waves to convert evidence-backed lessons into proposed durable assets: skills, scripts, rules/checks, prompt templates, docs, or issues. Always use it when the user mentions flywheel, wave closeout, repo ecosystem learning, durable asset promotion, or learning-to-tools.
---
```

```
$ sed -n '1,80p' scripts/skills/validate-skills.sh
#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.claude/skills}"
...
  if ! printf '%s\n' "$frontmatter" | grep -Eq '^name:[[:space:]]*[^[:space:]].*'; then
    echo "Missing or empty name: $file"
...
  if ! printf '%s\n' "$frontmatter" | grep -Eq '^description:[[:space:]]*[^[:space:]].*'; then
    echo "Missing or empty description: $file"
```

```
$ sed -n '22,36p' .github/workflows/skills-validation.yml
      - name: Run skill validator
        # NOTE: Many SKILL.md files under _diverged/ and _internal/ do not yet have
        # YAML frontmatter. Validation runs in soft-fail mode until those are updated.
        # Tracked in the work queue for remediation.
        continue-on-error: true
        run: bash scripts/skills/validate-skills.sh
```

**Gap proofs**:
```
$ rg -n "check-skill-frontmatter|skill frontmatter|SKILL.md frontmatter|yaml.safe_load\(.*frontmatter|\.claude/skills.*SKILL.md" scripts tests .github docs .claude/rules | head -120
.github/workflows/skills-validation.yml:22:    name: Validate SKILL.md frontmatter
...
```

The search found the workflow and the grep-based validator surface, but no existing YAML-parse test for `.claude/skills/**/SKILL.md`.

**Current validator false negative**:
```
$ bash scripts/skills/validate-skills.sh; printf 'rc=%s\n' "$?"
Skill validation passed (3111 files).
rc=0
```

**Live inventory of YAML parse failures**:
```
$ uv run --no-project --with pyyaml python - <<'PY'
from pathlib import Path
import yaml
files = sorted(Path('.claude/skills').glob('**/SKILL.md'))
malformed = []
missing = []
for path in files:
    text = path.read_text(encoding='utf-8', errors='replace')
    if not text.startswith('---'):
        missing.append(path)
        continue
    end = text.find('\n---', 4)
    if end == -1:
        malformed.append((path, 'missing closing ---'))
        continue
    try:
        data = yaml.safe_load(text[4:end])
    except yaml.YAMLError as exc:
        malformed.append((path, str(exc).splitlines()[0]))
        continue
    if not isinstance(data, dict):
        malformed.append((path, 'frontmatter is not a mapping'))
print(f'total={len(files)}')
print(f'missing_frontmatter={len(missing)}')
print(f'malformed_or_unparseable={len(malformed)}')
for path, err in malformed:
    print(f'MALFORMED {path}: {err}')
PY
total=3111
missing_frontmatter=0
malformed_or_unparseable=1
MALFORMED .claude/skills/coordination/flywheel-closeout/SKILL.md: mapping values are not allowed here
```

**Reproduction proofs** (verify-against-repo-state, per Step 1.5 of `issue-planning-mode`):
```
$ uv run --no-project --with pyyaml python - <<'PY'
from pathlib import Path
import yaml
path = Path('.claude/skills/coordination/flywheel-closeout/SKILL.md')
text = path.read_text(encoding='utf-8')
block = text.split('---', 2)[1]
try:
    yaml.safe_load(block)
    print('PARSE_OK')
except yaml.YAMLError as exc:
    print('PARSE_FAIL')
    print(exc)
PY
PARSE_FAIL
mapping values are not allowed here
  in "<unicode string>", line 3, column 132:
     ... ons into proposed durable assets: skills, scripts, rules/checks, ... 
                                         ^
```

- Reproduced at: 2026-06-08T18:51:02Z
- Failure mode observed matches issue claim: YES
- Distinct sources consulted: 8

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-06-08-issue-2981-skill-frontmatter-yaml-valid.md` |
| Existing validator | `scripts/skills/validate-skills.sh` |
| Proposed validator tests | `tests/enforcement/test_validate_skills_frontmatter.py` |
| Broken skill to fix | `.claude/skills/coordination/flywheel-closeout/SKILL.md` |
| Existing workflow | `.github/workflows/skills-validation.yml` |
| Plan review — Claude | `scripts/review/results/2026-06-08-plan-2981-claude.md` |
| Plan review — Codex latest preserved | `scripts/review/results/2026-06-08-plan-2981-r6-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-06-08-plan-2981-gemini.md` |
| Plan review — round 1 preserved | `scripts/review/results/2026-06-08-plan-2981-r1-*.md` |
| Plan review — round 2 preserved | `scripts/review/results/2026-06-08-plan-2981-r2-*.md` |
| Plan review — round 3 preserved | `scripts/review/results/2026-06-08-plan-2981-r3-*.md` |
| Plan review — round 4 Codex | `scripts/review/results/2026-06-08-plan-2981-r4-codex.md` |
| Plan review — round 5 Codex | `scripts/review/results/2026-06-08-plan-2981-r5-codex.md` |
| Plan review — round 6 Codex | `scripts/review/results/2026-06-08-plan-2981-r6-codex.md` |

---

## Deliverable

A test-covered `SKILL.md` validator path that YAML-parses `.claude/skills/**/SKILL.md`, catches the malformed colon-bearing description fixture, and leaves `flywheel-closeout` trigger language intact while making its frontmatter parseable.

---

## Pseudocode

```
test malformed_colon_description_fails:
    create tmp skills root with bad/SKILL.md containing unquoted "description: ... assets: skills"
    run bash scripts/skills/validate-skills.sh <tmp skills root>
    assert returncode != 0
    assert stderr/stdout names bad/SKILL.md and YAML parse failure

test quoted_colon_description_passes:
    create tmp skills root with good/SKILL.md containing quoted description with colon text
    run validator against tmp skills root
    assert returncode == 0

test live_skill_tree_passes_after_fix:
    run validator against .claude/skills
    assert returncode == 0

validator:
    for each SKILL.md under root:
        require opening and closing frontmatter delimiters
        parse extracted frontmatter with yaml.safe_load
        require parsed frontmatter is a mapping
        require non-empty name and description fields
    print checked count
    exit 1 if any file fails
```

Implementation direction:
- Preserve the existing `scripts/skills/validate-skills.sh` entrypoint because the workflow already depends on it, but replace the grep/awk validation loop with one delegation call to the Python helper. Do not leave the old regex loop in parallel with the helper; that would create two validators with different acceptance sets.
- Create `scripts/skills/validate_skills_frontmatter.py` and have the shell script invoke it once for the full skill root through a single hermetic command:

```
UV_CACHE_DIR="${UV_CACHE_DIR:-.claude/state/uv-cache}" \
  uv run --no-project --with pyyaml python scripts/skills/validate_skills_frontmatter.py "$ROOT"
```

  The implementation may resolve `.claude/state/uv-cache` relative to the repo root before invocation so the cache is writable locally and in CI. `uv` must be installed in CI before this script runs. If `uv` is missing locally, the shell script should fail with a controlled message naming the missing dependency.
- The Python helper will parse all files in one interpreter process. Do not invoke Python or `uv` once per `SKILL.md`; 3,111 per-file interpreter startups would be a CI timeout risk.
- The Python helper will use a conservative line-oriented frontmatter splitter, validated against the current 3,111-file inventory:
  - read text with `encoding="utf-8"`
  - split with `splitlines()` so LF and CRLF both work
  - require the first line, after stripping whitespace, to equal `---`
  - find the next line whose stripped value equals `---`
  - parse only the intervening lines with `yaml.safe_load`
  - require a mapping result
- The helper will require `name` and `description` to be strings before calling `.strip()`, and will then require the stripped value to be non-empty. Reject `name: 123`, missing `description`, `description: false`, `description: []`, `description: ""`, and whitespace-only strings with controlled validation messages, not tracebacks.
- PyYAML is a conservative proxy for the dispatch-time skill loaders, not a claim that every loader is implemented with PyYAML. It is appropriate here because the observed Codex failure is a YAML parse failure (`invalid YAML: mapping values are not allowed...`) and PyYAML reproduces the same malformed-colon class. Code-stage validation must include a Codex dispatch smoke check after the fix so the actual consumer is tested, not only the proxy.
- Scope decision: validate every `.claude/skills/**/SKILL.md`, including `_archive/` and `_internal/`. Rationale: the current live inventory has 0 missing frontmatter and only 1 malformed file across all 3,111 skill files, and review dispatch failures can originate from recursive skill loading/indexing. If future `_archive/` churn makes this too fragile, file a follow-up to split live-vs-archived skill validation rather than silently excluding archived files in this issue.
- Update `.github/workflows/skills-validation.yml` to install `uv` before running the validator, run `bash scripts/skills/validate-skills.sh`, and run the new pytest file in the same workflow:

```
UV_CACHE_DIR=.claude/state/uv-cache uv run --no-project --with pytest --with pyyaml pytest tests/enforcement/test_validate_skills_frontmatter.py -v
```

  Also add path filters for `scripts/skills/*.py` and `tests/enforcement/test_validate_skills_frontmatter.py` because both now affect the workflow's executed checks.
- Use `UV_CACHE_DIR=.claude/state/uv-cache uv run --no-project --with pytest --with pyyaml pytest ...` for local test commands when the base environment is not guaranteed; this avoids relying on the default `~/.cache/uv` location.
- Quote the existing `flywheel-closeout` description rather than shortening/removing trigger language.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `.claude/skills/coordination/flywheel-closeout/SKILL.md` | Quote or otherwise YAML-safe the existing description without weakening trigger language. |
| Modify | `scripts/skills/validate-skills.sh` | Delegate to strict YAML parsing while preserving existing entrypoint. |
| Create | `scripts/skills/validate_skills_frontmatter.py` | Single-process YAML parser and metadata validator for all skill frontmatter. |
| Create | `tests/enforcement/test_validate_skills_frontmatter.py` | TDD coverage for malformed colon description, quoted colon pass, and live tree pass. |
| Modify | `.github/workflows/skills-validation.yml` | Add `uv` setup, run validator and pytest, add path filters for helper/tests, remove stale soft-fail comments in both the validator step and summary step, and remove `continue-on-error: true` after the live inventory passes. |
| Update | `docs/plans/README.md` | Add this plan to index. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_validator_fails_on_unquoted_colon_description` | The validator catches the #2981 defect class. | tmp `SKILL.md` with `description: proposed durable assets: skills` | nonzero exit; output mentions YAML/frontmatter error |
| `test_validator_passes_on_quoted_colon_description` | Quoting preserves colon-bearing trigger text safely. | tmp `SKILL.md` with quoted `description` containing colon text | exit 0 |
| `test_validator_requires_name_and_description` | Existing metadata requirements are preserved after YAML parsing. | tmp `SKILL.md` missing `description` | nonzero exit |
| `test_validator_rejects_empty_or_non_string_name_description` | YAML-valid but loader-unsafe metadata values are rejected. | tmp files with `name: 123`, `description: false`, `description: []`, `description: ""`, whitespace-only description | nonzero exit |
| `test_validator_reports_controlled_errors_not_tracebacks` | Missing/non-string fields fail cleanly. | tmp files with missing `description` and `name: 123` | nonzero exit; output has validation message; output does not contain `Traceback` |
| `test_validator_accepts_crlf_frontmatter_delimiters` | The conservative splitter supports CRLF files. | tmp `SKILL.md` with `\r\n---\r\n` delimiters and quoted description | exit 0 |
| `test_live_claude_skill_tree_passes_after_fix` | The repo's 3,111 live skill files are parseable after implementation. | `.claude/skills` | exit 0 |

---

## Acceptance Criteria

- [ ] RED: after creating `tests/enforcement/test_validate_skills_frontmatter.py` but before changing `scripts/skills/validate-skills.sh` or adding `scripts/skills/validate_skills_frontmatter.py`, `UV_CACHE_DIR=.claude/state/uv-cache uv run --no-project --with pytest --with pyyaml pytest tests/enforcement/test_validate_skills_frontmatter.py::test_validator_fails_on_unquoted_colon_description -v` fails because the current grep validator returns success for the malformed-colon fixture. This RED proof is invalid if pytest fails during collection or because the test file is missing.
- [ ] GREEN: `UV_CACHE_DIR=.claude/state/uv-cache uv run --no-project --with pytest --with pyyaml pytest tests/enforcement/test_validate_skills_frontmatter.py -v` passes.
- [ ] `bash scripts/skills/validate-skills.sh` fails before the skill fix and passes after the skill fix.
- [ ] `scripts/skills/validate-skills.sh` invokes `uv run --no-project --with pyyaml python scripts/skills/validate_skills_frontmatter.py "$ROOT"` once per run, with a repo-local/writable `UV_CACHE_DIR` default.
- [ ] `scripts/skills/validate_skills_frontmatter.py` parses all skill files in one Python process.
- [ ] Missing or non-string `name`/`description` failures produce controlled validator output and no Python traceback.
- [ ] `.claude/skills/coordination/flywheel-closeout/SKILL.md` frontmatter parses with PyYAML.
- [ ] `flywheel-closeout` description still contains the durable asset and trigger concepts from the issue body: `flywheel`, `wave closeout`, `repo ecosystem learning`, `durable asset promotion`, and `learning-to-tools`.
- [ ] `.github/workflows/skills-validation.yml` installs/sets up `uv` before invoking `bash scripts/skills/validate-skills.sh`.
- [ ] `.github/workflows/skills-validation.yml` runs `tests/enforcement/test_validate_skills_frontmatter.py`; path filters for the test file are only kept if the workflow actually executes that test.
- [ ] `.github/workflows/skills-validation.yml` path filters include `.claude/skills/**/SKILL.md`, `scripts/skills/*.sh`, `scripts/skills/*.py`, `tests/enforcement/test_validate_skills_frontmatter.py`, and the workflow file.
- [ ] Workflow hard-fail posture is implemented: after `uv` setup is added and the live skill inventory passes, remove `continue-on-error: true` from `.github/workflows/skills-validation.yml`. Stale comments in both the validator step and summary step claiming soft-fail mode or missing `_diverged/` / `_internal/` frontmatter are removed or corrected.
- [ ] Codex dispatch is smoke-tested after the fix with this exact command:

```
timeout -k 5s 120s codex exec "Return exactly CODEX_SKILL_LOAD_OK." </dev/null
```

  Success signal: exit code 0, stdout contains `CODEX_SKILL_LOAD_OK`, and stderr does not contain `failed to load skill`, `invalid YAML`, or `mapping values are not allowed`. This proves the Codex CLI session reached prompt execution after loading its skill surface.
- [ ] `scripts/legal/legal-sanity-scan.sh` passes.
- [ ] Code/artifact adversarial review is completed before close.
- [ ] Post an implementation summary comment on [#2981](https://github.com/vamseeachanta/workspace-hub/issues/2981).

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude r1 | MAJOR | Missing CI Python/YAML dependency setup; unsafe hard-fail sequencing; single-process parser not pinned; frontmatter extraction not canonicalized; stale workflow comment. |
| Codex r1 | MAJOR | Helper path not wired into workflow filters; bare `uv` cache issue; CI dependency contract missing; missing string/empty-field tests. |
| Gemini r1 | MAJOR | Retrieval miss claimed target files missing, but valid blockers matched other providers: single-process parsing, CI dependency setup, string type checks, empty-field tests, CRLF support. |
| Claude r2 | MAJOR | Shell-to-Python dependency mechanism still unspecified; PyYAML oracle not anchored to actual dispatch loader; stale summary text and soft-fail decision still ambiguous. |
| Codex r2 | MAJOR | Empty-artifact observation not reproduced locally; valid blockers: pytest not actually run by workflow and non-template `draft-needs-revision` status. |
| Gemini r2 | MAJOR | Retrieval miss repeated; valid blockers: controlled type/missing-field errors, remove old grep loop, hermetic local execution. |
| Claude r3 | MINOR | Tighten exact Codex smoke success signal, decide `_archive`/`_internal` scope, soften canonical splitter language, reconcile artifact header. |
| Codex r3 | MAJOR | Claimed latest artifacts were empty, plan still summarized r2 as FAIL, exact Codex smoke command missing. |
| Gemini r3 | UNAVAILABLE | CLI timed out/fell back with file-read failure; no review signal. |
| Codex r4 | MAJOR | Review provenance still omitted r3/r4 artifacts; summary still self-declared r3 FAIL; hard-fail decision remained open; RED proof could pass by missing test file. |
| Codex r5 | MAJOR | Review provenance still contested; existing `scripts/skills` parser surfaces not accounted for; hard-fail wording still had stale open-decision language; one stale "canonical splitter" phrase remained. |
| Codex r6 | MAJOR | Provenance still cited unsuffixed Codex artifact; Files-to-Change row retained stale "decide whether" hard-fail wording. |

**Overall result:** FAIL after r6 because Codex still returned MAJOR. This revision addresses r6 bookkeeping blockers; do not apply `status:plan-review` until a fresh focused review clears.

Revisions made based on review:
- Added explicit Python/PyYAML CI setup requirement and workflow path-filter updates.
- Required a `scripts/skills/validate_skills_frontmatter.py` helper invoked once per full skill root, preserving `scripts/skills/validate-skills.sh` as the workflow entrypoint.
- Added canonical line-oriented frontmatter splitting with CRLF support.
- Added non-empty string validation and tests for YAML-valid but loader-unsafe values.
- Replaced bare `uv` acceptance commands with `UV_CACHE_DIR=.claude/state/uv-cache` commands.
- Required stale soft-fail workflow comments to be removed or corrected.
- Replaced non-template `draft-needs-revision` status with `draft`.
- Pinned the shell entrypoint to a single hermetic `uv run --with pyyaml` invocation so local tests, direct shell runs, and CI use the same dependency path.
- Required the workflow to actually run the new pytest file instead of only triggering when it changes.
- Added controlled-error tests to avoid `AttributeError` tracebacks on missing/non-string fields.
- Stated PyYAML is a conservative proxy and added a Codex dispatch smoke check as the consumer-level validation.
- Added exact Codex smoke command and success/failure signals.
- Added explicit `_archive` and `_internal` scope decision.
- Replaced "canonical" splitter language with conservative splitter language.
- Added preserved r1/r2 artifacts to review provenance and recorded r3 verdicts.
- Added r3/r4 review provenance.
- Decided CI posture: remove `continue-on-error: true` after `uv` setup and live inventory pass.
- Tightened RED acceptance criterion so collection failure or a missing test file does not count as the red phase.
- Added resource intelligence for `scripts/skills/audit_skill_lib.py` and `scripts/skills/weekly_skills_audit.py`, with reasons they are not drop-in fail-closed replacements.
- Removed stale open-decision language around `continue-on-error: true`.
- Replaced remaining "canonical splitter" test wording with conservative splitter wording.
- Moved Codex review provenance to preserved `r6-codex` artifact and removed the final stale "decide whether" Files-to-Change wording.

---

## Risks and Open Questions

- **Risk:** Hard-failing `.github/workflows/skills-validation.yml` before `uv` setup is present would create a red CI for the wrong reason. Sequence: add `uv` setup first, verify live inventory pass after the skill fix, then remove `continue-on-error: true`.
- **Risk:** A validator that diverges from real skill-loader parsing can false-pass or false-fail. The implementation will document the canonical delimiter rule and keep it intentionally conservative: leading frontmatter only, delimiter line by itself after whitespace stripping, PyYAML mapping required.
- **Decision:** This issue will remove `continue-on-error: true` in the same implementation after adding `uv` setup and after live inventory passes. Rationale: retaining soft-fail leaves the root cause unguarded and a future malformed skill can still break review dispatch.

---

## Complexity: T2

**T2** — small implementation surface, but it touches validation infrastructure, CI posture, a skill runtime artifact, and requires TDD plus adversarial review because the defect blocks cross-provider review dispatch.
