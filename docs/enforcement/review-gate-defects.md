# Review Gate Defect Record

Refs #4054

## Purpose and Status

This document records two defects in `scripts/enforcement/require-review-on-push.sh`
observed on 2026-10-12. The gate fix is implemented in warn-first form on
2026-10-12. Commit-bound evidence becomes the blocking default on or after
2026-10-26 by changing the single default assignment line for
`REVIEW_GATE_EVIDENCE_MODE` from `warn` to `strict`, after second-provider
review. Hook installer and workflow wiring are unchanged.

## Current Gate Decision

`get_commit_list` excludes commits reachable from the remote default branch. For
a new branch or an empty remote object, the checked range is `LOCAL_OID` minus
the remote default branch. For an existing branch, the checked range is
`LOCAL_OID` minus both the remote branch tip and the remote default branch. If
that range lookup cannot be computed, the gate emits a diagnostic, prints a
`BLOCKED` line, and exits non-zero.

`needs_review` classifies commit subjects. Documentation, chore, test, CI,
style, sync, merge, revert and build subjects are skipped. Feature, fix,
refactor, performance and security subjects require review. Unknown prefixes
also require review.

`commit_touches_only_low_risk_paths` downgrades commits whose changed files are
documentation or other low-risk paths. Remaining feature-classified commits
require review evidence.

Commit-bound evidence is evaluated before legacy evidence. `Reviewed-Commit`
matches one full commit identifier. `Reviewed-Range` matches a full ancestor
range only when the later reviewed commit is in the checked range. Malformed,
abbreviated, and unresolvable evidence lines are reported with file and line
number and do not count. Unreadable evidence files fail closed with a diagnostic
and a `BLOCKED` line.

`REVIEW_GATE_EVIDENCE_MODE=warn` remains the warn-first default until the dated
flip. In warn mode, missing commit-bound evidence prints `WOULD-REJECT`; legacy
modification-time or subject-keyword evidence may still pass the commit with a
`DEPRECATED` warning. In strict mode, only commit-bound evidence counts. When
unreviewed commits remain, the default strictness setting blocks with a
`BLOCKED` line, while `REVIEW_GATE_STRICT=0` permits the existing warning-only
exit.

The pull-request workflow calls the gate with `HEAD` and the merge base with
`origin/main`. The local hook installer wires the pre-push hook to invoke the
gate without commit arguments, so the hook's default arguments apply there.

## Defect 1: Mainline Commits Are Rechecked

### What Happened Before the Fix

Commits already reachable from `origin/main` were counted as branch commits
when they entered a topic branch through a merge, a fast-forward, or a new
branch push. The gate then demanded review evidence for work that had already
landed on main.

### Mechanism Before the Fix

`get_commit_list` listed `REMOTE_OID..LOCAL_OID`, or the last ten commits for a
new branch. It did not subtract commits reachable from `origin/main`.

### Minimal Reproduction

Run this from an empty temporary directory:

```bash
set -euo pipefail
root="$(mktemp -d)"
gate="<path-to-checkout>/scripts/enforcement/require-review-on-push.sh"
git init --bare -q "$root/origin.git"
git init -q "$root/repo"
cd "$root/repo"
git config user.name "Example User"
mail_user="example"
mail_domain="example.invalid"
git config user.email "${mail_user}@${mail_domain}"
git remote add origin "$root/origin.git"
printf 'init\n' > README.md
git add README.md
git commit -q -m "chore: initial"
git branch -M main
git push -q -u origin main
git checkout -q -b topic
mkdir -p docs
printf 'topic\n' > docs/topic.md
git add docs/topic.md
git commit -q -m "docs: topic notes"
git push -q -u origin topic
remote_tip="$(git rev-parse HEAD)"
git checkout -q main
mkdir -p src
printf 'print(1)\n' > src/main.py
git add src/main.py
git commit -q -m "feat: main code"
git push -q origin main
git checkout -q topic
git merge --no-edit origin/main
bash "$gate" "$(git rev-parse HEAD)" "$remote_tip"
```

Expected output: no feature commit requires review because the only code commit
is already reachable from `origin/main`.

Actual output observed:

```text
[review-gate] Summary: 1 feature/fix commit(s), 1 chore/docs/sync commit(s)
[review-gate]   Reviewed: 0, Unreviewed: 1
[review-gate] WARNING: 1 feature/fix commit(s) without review evidence:
  - <id> feat: main code
[review-gate] BLOCKED: strict mode (default) - push rejected.
```

The same defect was observed for a fast-forwarded branch and for the new-branch
case where the remote object is all zeros. The observed summaries were:

| Case | Expected verdict | Actual summary | Exit code |
|---|---|---|---|
| Merge from `origin/main` | pass, no feature commit under review | `Reviewed: 0, Unreviewed: 1` | 1 |
| Fast-forward to `origin/main` | pass, no feature commit under review | `Reviewed: 0, Unreviewed: 1` | 1 |
| New branch already containing `origin/main` | pass, no feature commit under review | `Reviewed: 0, Unreviewed: 1` | 1 |

### Consequence Before the Fix

Reviewed work already on main was demanded again. That false block made the
bypass variable attractive for ordinary branch maintenance.

## Defect 2: Evidence Is Not Commit-Bound

### What Happened Before the Fix

Evidence passed the gate without proving that the pushed feature commits had
been reviewed. Three forms were reproduced:

- A fresh checkout gives old review files today's modification time and satisfies
  evidence checks.
- One current evidence file marks every feature commit in the push range as
  reviewed.
- A review keyword in an unrelated recent commit subject satisfies evidence.

### Mechanism Before the Fix

`check_review_results`, `check_planning_reviews` and `check_report_reviews`
tested file modification time, not commit identity. `check_git_evidence`
searched the last thirty commit subjects for review keywords, not for a
relationship to the commits under review. When `has_review_evidence` returned
success, the main gate set `reviewed` equal to the full feature commit count.

### Minimal Reproduction: Fresh Checkout

```bash
set -euo pipefail
root="$(mktemp -d)"
gate="<path-to-checkout>/scripts/enforcement/require-review-on-push.sh"
git init -q "$root/repo"
cd "$root/repo"
git config user.name "Example User"
mail_user="example"
mail_domain="example.invalid"
git config user.email "${mail_user}@${mail_domain}"
printf 'init\n' > README.md
git add README.md
git commit -q -m "chore: initial"
mkdir -p scripts/review/results src
printf 'old evidence\n' > scripts/review/results/old.txt
touch -d '2020-01-01 00:00:00' scripts/review/results/old.txt
git add scripts/review/results/old.txt
GIT_AUTHOR_DATE='2020-01-01T00:00:00Z' \
GIT_COMMITTER_DATE='2020-01-01T00:00:00Z' \
  git commit -q -m "chore: old evidence fixture"
touch -d '2020-01-01 00:00:00' scripts/review/results/old.txt
base="$(git rev-parse HEAD)"
printf 'print(1)\n' > src/feature.py
git add src/feature.py
git commit -q -m "feat: unevidenced code"
head="$(git rev-parse HEAD)"
bash "$gate" "$head" "$base"
git clone -q . "$root/clone"
cd "$root/clone"
git config user.name "Example User"
git config user.email "${mail_user}@${mail_domain}"
bash "$gate" "$head" "$base"
```

Expected output: both runs block because the old evidence file does not name the
feature commit.

Actual output observed:

```text
# Original checkout with old file time
[review-gate] Summary: 1 feature/fix commit(s), 0 chore/docs/sync commit(s)
[review-gate]   Reviewed: 0, Unreviewed: 1
[review-gate] BLOCKED: strict mode (default) - push rejected.

# Fresh clone with today's file time
[review-gate] Summary: 1 feature/fix commit(s), 0 chore/docs/sync commit(s)
[review-gate]   Reviewed: 1, Unreviewed: 0
[review-gate] PASS: All feature/fix commits have review evidence.
```

### Minimal Reproduction: One Evidence File Covers All Commits

```bash
set -euo pipefail
root="$(mktemp -d)"
gate="<path-to-checkout>/scripts/enforcement/require-review-on-push.sh"
git init -q "$root/repo"
cd "$root/repo"
git config user.name "Example User"
mail_user="example"
mail_domain="example.invalid"
git config user.email "${mail_user}@${mail_domain}"
printf 'init\n' > README.md
git add README.md
git commit -q -m "chore: initial"
base="$(git rev-parse HEAD)"
mkdir -p src
for n in 1 2 3; do
  printf 'print(%s)\n' "$n" > "src/f$n.py"
  git add "src/f$n.py"
  git commit -q -m "feat: code $n"
done
head="$(git rev-parse HEAD)"
mkdir -p scripts/review/results
printf 'generic evidence\n' > scripts/review/results/generic.txt
bash "$gate" "$head" "$base"
```

Expected output: the gate blocks, or at most marks only the commit explicitly
covered by evidence as reviewed.

Actual output observed:

```text
[review-gate] Summary: 3 feature/fix commit(s), 0 chore/docs/sync commit(s)
[review-gate]   Reviewed: 3, Unreviewed: 0
[review-gate] PASS: All feature/fix commits have review evidence.
```

### Minimal Reproduction: Unrelated Keyword Commit

```bash
set -euo pipefail
root="$(mktemp -d)"
gate="<path-to-checkout>/scripts/enforcement/require-review-on-push.sh"
git init -q "$root/repo"
cd "$root/repo"
git config user.name "Example User"
mail_user="example"
mail_domain="example.invalid"
git config user.email "${mail_user}@${mail_domain}"
printf 'init\n' > README.md
git add README.md
git commit -q -m "chore: initial"
printf 'notes\n' > notes.txt
git add notes.txt
git commit -q -m "chore: review notes"
base="$(git rev-parse HEAD)"
mkdir -p src
printf 'print(1)\n' > src/keyword.py
git add src/keyword.py
git commit -q -m "feat: keyword code"
bash "$gate" "$(git rev-parse HEAD)" "$base"
```

Expected output: the gate blocks because the keyword commit is unrelated to the
feature commit.

Actual output observed:

```text
[review-gate] Summary: 1 feature/fix commit(s), 0 chore/docs/sync commit(s)
[review-gate]   Reviewed: 1, Unreviewed: 0
[review-gate] PASS: All feature/fix commits have review evidence.
```

### Consequence

The gate can pass with no review of the pushed commits. Modification time and
recent subject text are checkout-level signals, not review evidence for the
commit range.

## Implemented Fix

`get_commit_list` excludes commits reachable from the remote default branch. A
normal push uses a commit set equivalent to:

```bash
git rev-list "$LOCAL_OID" --not "$REMOTE_OID" origin/main
```

For a new branch, the remote-side subtraction is absent and the remote default
branch still serves as the common baseline:

```bash
git rev-list "$LOCAL_OID" --not origin/main
```

When the remote default branch is absent, warn evidence mode emits a fetch
diagnostic and uses the prior range calculation during the migration period.
Strict evidence mode fails closed without that ref. When the ref exists but the
range cannot be computed, the gate emits a range diagnostic, prints `BLOCKED`,
and exits non-zero. CI's merge-base argument remains useful, but the script
still subtracts the remote default branch so a branch that merged or
fast-forwarded main does not recheck mainline commits.

Review evidence names the full commit identifiers it covers. The implemented
review result file field is:

```text
Reviewed-Commit: <full-commit-id>
```

Commit-bound review evidence may live in a later evidence-only commit, or
outside the pushed tree, because an evidence file cannot name the identifier of
the commit that contains it. The gate recognizes an evidence-only commit by
limiting the exemption to commits that touch only review-evidence paths.

For each feature commit in the checked range, the gate requires either:

- a review evidence file naming that full commit identifier, or
- a reviewed later commit in the same checked range that contains the earlier
  commit as an ancestor and whose evidence explicitly states that the review
  covers the ancestor range.

Merge commits are ignored unless they introduce non-merge changes requiring
review. Rebases create new commit identifiers, so old evidence for pre-rebase
identifiers does not satisfy the gate unless a reviewer records the new
identifier or an approved range mapping. Modification time and recent subject
keywords count only as legacy evidence in warn mode.

Migration uses a dated warn-only period for evidence files that lack commit
bindings. Existing evidence files can remain as historical records, but strict
evidence mode requires commit-bound evidence. The bypass policy remains accurate
for the warn-first period.

## Evidence file format

Commit-bound review evidence is a plain-text review result file under the
existing `scripts/review/results/` evidence location. The gate recognizes these
fields:

```text
Reviewed-Commit: <full-commit-id>
Reviewed-Range: <oldest-full-commit-id>..<reviewed-full-commit-id>
```

`Reviewed-Commit` names one reviewed commit with its full 40-character lowercase
hexadecimal identifier. Abbreviated identifiers, non-hexadecimal identifiers,
unknown commit identifiers and malformed evidence fields are reported with the
file and line number. The invalid line does not count as evidence; the push is
then judged as if that line were absent in both evidence modes.

`Reviewed-Range` states that the later reviewed commit covers the ancestor range
from the oldest named commit through the reviewed commit. The later commit must
be in the checked push range, and the feature commit under evaluation must be
reachable between the oldest and later commit. Evidence for a pre-amend,
pre-squash or pre-rebase identifier does not cover the new commit identifier.

Evidence-only commits are exempt from review when every changed path is in a
review-evidence location. Modification time and recent subject keywords are
legacy evidence only during the warn-first migration period.

## Evidence mode

`REVIEW_GATE_EVIDENCE_MODE` selects the commit-bound evidence rule:

- `warn` is the default until the migration date. The gate evaluates the
  commit-bound rule and prints one `WOULD-REJECT` line per feature commit that
  would fail in strict evidence mode. If legacy evidence is present, the gate
  accepts that commit and prints a deprecation warning naming the legacy evidence
  kind and the 2026-10-26 migration date.
- `strict` requires commit-bound evidence for every feature-class commit in the
  checked range. Legacy modification-time and keyword evidence does not count.

`REVIEW_GATE_STRICT` keeps its existing meaning after evidence classification:
when unreviewed commits remain, `REVIEW_GATE_STRICT=0` permits a warning-only
push, and the default blocks the push. `SKIP_REVIEW_GATE=1` keeps its existing
bypass behavior and audit log. A feature-class commit with no commit-bound
evidence and no legacy evidence remains blocked under the current default.

## Regression Coverage

| Case | Setup | Expected verdict | Regression coverage |
|---|---|---|---|
| D1 merge | Topic branch merges `origin/main` after a feature commit lands on main | pass; mainline feature commit excluded | `case_d1_mainline_excluded merge`; known-defects D1 merge |
| D1 fast-forward | Topic branch fast-forwards to `origin/main` after a feature commit lands on main | pass; mainline feature commit excluded | `case_d1_mainline_excluded fast_forward`; known-defects D1 fast-forward |
| D1 new branch | New branch already contains commits reachable from `origin/main` | pass; mainline feature commit excluded | `case_d1_new_branch`; known-defects D1 new branch |
| Uncomputable range | Remote tip object is well-formed but absent locally | block; range lookup diagnostic and `BLOCKED`; no `PASS` | `case_uncomputable_range_blocks` |
| Empty range | Local and remote tips are the same commit | pass; no commits to check | `case_empty_range_passes` |
| D2 fresh checkout | Old evidence file gains today's file time in a fresh clone | strict mode blocks; warn mode reports `WOULD-REJECT` and accepts legacy evidence | `case_d2_fresh_checkout`; known-defects D2 fresh checkout |
| D2 one-for-all | Three feature commits and one generic evidence file | strict mode blocks until each feature commit is named or covered by a named reviewed range | `case_d2_one_for_all`; known-defects D2 generic evidence |
| D2 unrelated keyword | Unrelated recent commit subject contains a review keyword | strict mode blocks; warn mode reports legacy keyword evidence | `case_d2_keyword`; known-defects D2 unrelated keyword |
| Correct evidence | Feature commit has evidence naming its full identifier | pass | `case_correct_evidence_and_range` |
| Invalid range evidence | Malformed or abbreviated `Reviewed-Range` line | diagnostic with file and line; invalid line does not count | `case_invalid_range_evidence_warn_without_legacy`; `case_invalid_range_evidence_with_valid_commit` |
| Unreadable evidence file | Result file cannot be read by the gate process | block; diagnostic and `BLOCKED` | `case_unreadable_result_blocks` |
| Amended or squashed commit | Evidence names the pre-amend or pre-squash identifier, then the feature commit is amended or squashed | block; evidence for the old identifier does not cover the new commit | `case_amended_or_squashed_blocks` |
| Partial evidence | Three feature commits, evidence names only one | block the two unevidenced commits | `case_partial_evidence` |
| Docs-only push | Documentation-only commits in the range | pass; no review required | `case_docs_only_pass` |
| New branch | New branch with feature commits not reachable from `origin/main` | block unless each feature commit has commit-bound evidence | `case_new_branch_feature_blocks` |
| SIGPIPE regression | Evidence exists and the search command sees an early match | pass without a pipefail false negative | `case_sigpipe_regression` |

## Open Questions

- Missing default branch ref: `REVIEW_GATE_EVIDENCE_MODE=warn` prints a fetch
  diagnostic and falls back to the prior range calculation; `strict` fails
  closed.
- The local hook does not fetch. The script subtracts `origin/HEAD` when it names
  a valid remote default branch, otherwise `origin/main`.
- Review result files are the only commit-bound evidence format implemented by
  this fix. Commit trailers remain out of scope.
- Legacy non-bound evidence remains accepted only in `warn` mode until
  2026-10-26.
- Local-hook argument passing remains unchanged by this fix.
