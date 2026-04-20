#!/usr/bin/env bash
set -euo pipefail

# Copy/paste-ready commands to create the 3 ecosystem-sync follow-up issues.
# Run from a checkout authenticated with gh and pointed at the intended repo.
# By default this targets workspace-hub; change REPO if these belong elsewhere.

REPO="vamseeachanta/workspace-hub"
TMPDIR="${TMPDIR:-/tmp}/ecosystem-sync-gh-issues"
mkdir -p "$TMPDIR"

cat > "$TMPDIR/issue-1.md" <<'EOF'
## Summary
The ecosystem-sync signal tests currently hard-fail on a clean checkout if the local git fixture repos have not already been built under `tests/ecosystem-sync/fixtures/repos/`.

## Why this matters
Stage 1 test coverage is no longer self-contained. The current suite assumes a prior manual run of `tests/ecosystem-sync/fixtures/repos/build_fixtures.sh`, which means a fresh checkout can fail before any product bug is exercised.

## Evidence
- Review artifact: `docs/plans/2026-04-20-aceengineer-ecosystem-sync-review.md`
- Affected tests:
  - `tests/ecosystem-sync/test_signals_release.py`
  - `tests/ecosystem-sync/test_signals_casestudy.py`
  - `tests/ecosystem-sync/test_signals_readme.py`
- Supporting fixture builder:
  - `tests/ecosystem-sync/fixtures/repos/build_fixtures.sh`
- Current assumptions in tests:
  - `test_signals_release.py` reads directly from `fixtures/repos/repo-with-release`
  - `test_signals_casestudy.py` reads `repo-with-casestudy.baseline-sha`
  - `test_signals_readme.py` reads `fixtures/repos/repo-with-readme/README.md`

## Reproduction
1. Move or remove these locally built fixture artifacts:
   - `tests/ecosystem-sync/fixtures/repos/repo-with-release`
   - `tests/ecosystem-sync/fixtures/repos/repo-with-casestudy`
   - `tests/ecosystem-sync/fixtures/repos/repo-with-readme`
   - `tests/ecosystem-sync/fixtures/repos/repo-with-casestudy.baseline-sha`
2. Run:
   - `uv run pytest tests/ecosystem-sync/test_signals_release.py tests/ecosystem-sync/test_signals_casestudy.py tests/ecosystem-sync/test_signals_readme.py -q`
3. Observed review result: 9 failures, including `subprocess.CalledProcessError`, `FileNotFoundError`, and missing `README.md` fixture content.

## Expected behavior
Either:
1. the tests automatically build the required fixture repos before execution, or
2. the tests skip gracefully with a clear diagnostic explaining that fixture repos are absent.

## Proposed change
Add a bootstrap layer in `tests/ecosystem-sync/conftest.py` that:
- checks for the required fixture repos and baseline SHA file
- runs `bash tests/ecosystem-sync/fixtures/repos/build_fixtures.sh` when they are missing
- fails only if autobuild itself fails

If autobuild is intentionally rejected, convert the current hard failures into explicit `pytest.skip(...)` behavior with a diagnostic pointing to the fixture builder.

## Acceptance criteria
- A clean checkout can run the ecosystem-sync signal tests without manual fixture prep.
- Missing fixture repos no longer produce opaque hard failures.
- Test output clearly distinguishes product failures from fixture-bootstrap failures.
- The fixture bootstrap path is covered by tests or at minimum validated in CI/local repeat runs.

## Notes
This is a follow-up hardening issue from the adversarial review, not a Stage 1 blocker retroactively reopening Tasks 7–11.
EOF

cat > "$TMPDIR/issue-2.md" <<'EOF'
## Summary
`_extract_section()` in `scripts/ecosystem-sync/signals.py` currently treats `## <heading>` text inside fenced code blocks as real README headings. That can create malformed extracted bodies and false README-diff signals.

## Why this matters
Signal 3 is supposed to detect meaningful capability-section drift. Right now an example snippet inside a fenced block can be misread as the actual `## Capabilities` section, causing noisy or incorrect website-sync issues.

## Evidence
- Review artifact: `docs/plans/2026-04-20-aceengineer-ecosystem-sync-review.md`
- Affected implementation:
  - `scripts/ecosystem-sync/signals.py:144-159`
- Current logic:
  - starts a section when `line.strip() == f"## {heading}"`
  - stops only when `lines[j].startswith("## ")`
- Current tests do not cover fenced-code false positives:
  - `tests/ecosystem-sync/test_signals_readme.py`

## Reproduction
Evaluate `_extract_section()` on markdown like:

```md
# T
```md
## Capabilities
code
```

## Other
rest
```

Current observed result from review: `_extract_section(..., "Capabilities")` returned `code\n````, which is incorrect. The heading inside the fenced code block should have been ignored.

## Expected behavior
Unfenced ATX headings should be considered section boundaries. Heading-looking text inside fenced code blocks should be ignored entirely.

## Proposed change
Harden `_extract_section()` to be fence-aware:
- track fenced-code entry/exit while scanning
- ignore `## ...` matches while inside a fence
- only terminate on the next unfenced `## ` heading

A markdown parser is acceptable, but a small fence-aware scanner is likely enough for current scope.

## Acceptance criteria
- A fenced code block containing `## Capabilities` does not trigger section extraction.
- Existing basic heading extraction behavior still passes.
- `tests/ecosystem-sync/test_signals_readme.py` gains adversarial cases covering fenced blocks.
- README-diff detection continues to be silent when the real configured heading is absent.

## Notes
Keep the fix tightly scoped to section extraction behavior. This issue is about false parsing, not about broad markdown-normalization policy.
EOF

cat > "$TMPDIR/issue-3.md" <<'EOF'
## Summary
`detect_release_tag()` currently uses commit date (`git log -1 --format=%cI <tag>`) for the 90-day freshness cutoff. That is wrong for annotated tags created recently on older commits.

## Why this matters
A real recent release can be silently excluded if the tagged commit is old. That makes Signal 1 under-report releases exactly in the scenario where a project cuts an annotated release tag after stabilizing an older commit.

## Evidence
- Review artifact: `docs/plans/2026-04-20-aceengineer-ecosystem-sync-review.md`
- Affected implementation:
  - `scripts/ecosystem-sync/signals.py:30-76`
- Current freshness logic:
  - `git log -1 --format=%cI <tag>`
- Verified review repro:
  - old commit date: `2025-01-01T00:00:00+00:00`
  - annotated tag `v9.9.9` created today on that old commit
  - `git log -1 --format=%cI v9.9.9` returned the old commit date
  - `git for-each-ref refs/tags/v9.9.9 --format='%(taggerdate:iso-strict)'` returned today’s tagger date

## Expected behavior
- For annotated tags, freshness should use tagger date.
- For lightweight tags, freshness can fall back to commit date.
- The semantics should be explicit in code/tests so future readers know which timestamp defines “recent release”.

## Proposed change
Update release-age detection to:
1. attempt annotated tagger date first via `git for-each-ref` or `git cat-file tag`
2. fall back to commit date for lightweight tags
3. keep the current semver/noise filtering and existing dedupe behavior

## Acceptance criteria
- A recent annotated tag on an old commit is still detected as a fresh release.
- Lightweight tag behavior remains supported.
- Tests cover both annotated-tag and lightweight-tag cases.
- The 90-day cutoff semantics are documented inline or in test names.

## Notes
This is a semantic correctness fix, not a feature expansion. The issue should stay focused on release freshness policy and test coverage.
EOF

echo "Review issue packets ready under: $TMPDIR"
echo

echo "1) Fixture autobuild / graceful skip"
echo "gh issue create --repo \"$REPO\" --title \"test(ecosystem-sync): autobuild or skip missing local git fixtures\" --label bug --label tests --label priority:medium --label area:ecosystem-sync --body-file \"$TMPDIR/issue-1.md\""
echo

echo "2) Fenced-code-aware README extraction"
echo "gh issue create --repo \"$REPO\" --title \"fix(ecosystem-sync): ignore fenced code blocks when extracting README sections\" --label bug --label priority:medium --label area:ecosystem-sync --label parsing --body-file \"$TMPDIR/issue-2.md\""
echo

echo "3) Annotated tagger-date release freshness"
echo "gh issue create --repo \"$REPO\" --title \"fix(ecosystem-sync): use annotated tagger date for release freshness cutoff\" --label bug --label priority:medium --label area:ecosystem-sync --label releases --body-file \"$TMPDIR/issue-3.md\""
