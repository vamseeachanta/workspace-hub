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

`get_commit_list` builds the checked range from `REMOTE_OID..LOCAL_OID`. For a
new branch or an empty remote object, it checks the last ten commits reachable
from `LOCAL_OID`.

`needs_review` classifies commit subjects. Documentation, chore, test, CI,
style, sync, merge, revert and build subjects are skipped. Feature, fix,
refactor, performance and security subjects require review. Unknown prefixes
also require review.

`commit_touches_only_low_risk_paths` downgrades commits whose changed files are
documentation or other low-risk paths. Remaining feature-classified commits
require review evidence.

`has_review_evidence` passes when any one evidence check passes:
`check_review_results`, `check_planning_reviews`, `check_report_reviews`, or
`check_git_evidence`. These checks are global to the checkout state and recent
history; they do not bind evidence to the feature commits being pushed.

The pull-request workflow calls the gate with `HEAD` and the merge base with
`origin/main`. The local hook installer wires the pre-push hook to invoke the
gate without commit arguments, so the hook's default arguments apply there.

## Defect 1: Mainline Commits Are Rechecked

### What Happens

Commits already reachable from `origin/main` are counted as branch commits when
they enter a topic branch through a merge, a fast-forward, or a new branch push.
The gate then demands review evidence for work that has already landed on main.

### Mechanism

`get_commit_list` lists `REMOTE_OID..LOCAL_OID`, or the last ten commits for a
new branch. It does not subtract commits reachable from `origin/main`.

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

### Consequence

Reviewed work already on main is demanded again. That false block makes the
bypass variable attractive for ordinary branch maintenance.

## Defect 2: Evidence Is Not Commit-Bound

### What Happens

Evidence passes the gate without proving that the pushed feature commits were
reviewed. Three forms were reproduced:

- A fresh checkout gives old review files today's modification time and satisfies
  evidence checks.
- One current evidence file marks every feature commit in the push range as
  reviewed.
- A review keyword in an unrelated recent commit subject satisfies evidence.

### Mechanism

`check_review_results`, `check_planning_reviews` and `check_report_reviews` test
file modification time, not commit identity. `check_git_evidence` searches the
last thirty commit subjects for review keywords, not for a relationship to the
commits under review. When `has_review_evidence` returns success, the main gate
sets `reviewed` equal to the full feature commit count.

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

## Proposed Fix

`get_commit_list` should exclude commits reachable from `origin/main`. A normal
push can use a commit set equivalent to:

```bash
git rev-list "$LOCAL_OID" --not "$REMOTE_OID" origin/main
```

For a new branch, the remote-side subtraction is absent and `origin/main` still
serves as the common baseline:

```bash
git rev-list "$LOCAL_OID" --not origin/main
```

When `origin/main` is absent, the gate should fail closed with a clear diagnostic
in CI because the workflow fetches full history before calling the gate. For the
local hook, absence or staleness of `origin/main` should produce a diagnostic
that tells the developer to fetch; warn-only compatibility can be limited to the
migration period. CI's merge-base argument remains useful, but the script should
still subtract `origin/main` so a branch that merged or fast-forwarded main does
not recheck mainline commits.

Review evidence should name the full commit identifiers it covers. One concrete
form is a review result file with a machine-readable field such as:

```text
Reviewed-Commit: <full-commit-id>
```

Commit-bound review evidence should live in a later docs-only commit, or outside
the pushed tree, because an evidence file cannot name the identifier of the
commit that contains it; the proposed gate can recognize an evidence-only commit
by limiting the exemption to commits that touch only review-evidence paths.

For each feature commit in the checked range, the gate should require either:

- a review evidence file naming that full commit identifier, or
- a reviewed later commit in the same checked range that contains the earlier
  commit as an ancestor and whose evidence explicitly states that the review
  covers the ancestor range.

Merge commits should be ignored unless they introduce non-merge changes requiring
review. Rebases create new commit identifiers, so old evidence for pre-rebase
identifiers should not satisfy the gate unless a reviewer records the new
identifier or an approved range mapping. Modification time and recent subject
keywords should stop counting as evidence.

Migration should use a dated warn-only period for evidence files that lack commit
bindings. Existing evidence files can remain as historical records, but new
blocking enforcement should require commit-bound evidence after the migration
date. `docs/standards/REVIEW_GATE_BYPASS_POLICY.md` should receive a matching
edit when the gate behavior changes, because the bypass guidance currently
assumes the old evidence model and names the bypass variable in remediation text.

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

## Test Plan for the Later Fix

| Case | Setup | Expected verdict | Covered today by existing test |
|---|---|---|---|
| D1 merge | Topic branch merges `origin/main` after a feature commit lands on main | pass; mainline feature commit excluded | no |
| D1 fast-forward | Topic branch fast-forwards to `origin/main` after a feature commit lands on main | pass; mainline feature commit excluded | no |
| D1 new branch | New branch already contains commits reachable from `origin/main` | pass; mainline feature commit excluded | no |
| D2 fresh checkout | Old evidence file gains today's file time in a fresh clone | block; evidence does not name the feature commit | no |
| D2 one-for-all | Three feature commits and one generic evidence file | block until each feature commit is named or covered by a named reviewed range | partially; only a broad git-evidence pass is tested |
| D2 unrelated keyword | Unrelated recent commit subject contains a review keyword | block; subject keyword is ignored | partially; current test expects this pattern to pass |
| Correct evidence | Feature commit has evidence naming its full identifier | pass | no |
| Amended or squashed commit | Evidence names the pre-amend or pre-squash identifier, then the feature commit is amended or squashed | block; evidence for the old identifier does not cover the new commit | no |
| Partial evidence | Three feature commits, evidence names only one | block the two unevidenced commits | no |
| Docs-only push | Documentation-only commits in the range | pass; no review required | yes |
| New branch | New branch with feature commits not reachable from `origin/main` | block unless each feature commit has commit-bound evidence | no |
| SIGPIPE regression | Evidence exists and the search command sees an early match | pass without a pipefail false negative | indirectly; current script comments describe the risk, but no dedicated regression exists |

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
