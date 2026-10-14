# Procedure: closing and reopening issues

This page merges four audit procedures. An audit of 3,752 closed issues on 2026-10-13 and 2026-10-14 found these defects: bulk closures with template text; migration records created already closed; closures on unmerged branches; an epic closed by a commit message; "superseded" closures that name no successor; closed bodies overwritten with new scope; and SHAs that do not resolve. Closures use an authorized role, so a closure is attributable only through its comment.

## A. What may close an issue

1. **A merged PR** whose description says `Closes #N`, one line per issue, merged into the default branch at the head the reviewing role approved. One role builds and a different one reviews. The builder does not merge its own PR.
2. **An evidence comment (section B)** by the builder for work that landed through another PR, posted after the reviewing role has agreed on the issue.
3. **Not planned**, with one of these: an owner decision, quoted with its date; a retired tool or process, named with its retirement reference; or a passed date that the issue itself depended on.
4. **Duplicate or superseded**, written as `Superseded by #M`. The successor is open, or itself closed under these rules. Every unfinished acceptance item has been copied into it first. A chain that ends in a closure without delivery counts as not delivered.
5. **Nothing else.** This excludes: a push to a branch; a draft or unmerged PR; a commit message (closing keywords never go in commits); a migration, triage, sync or stale script; a "Status: done" line; elapsed time; an archived target repository; "implemented locally" or "unpushed"; "evidence recorded in the triage pass"; a comment that restates the plan; and a claim about a machine that no committed record backs.

## B. What a closing comment carries

1. The default-branch commit SHA, or the merged PR, that the evidence was read at. It is an ancestor of the default branch. If the issue named another branch, that branch was checked too.
2. Each acceptance item, ticked with its evidence (repository, path, symbol or PR), or written as `NOT DONE: <reason> -> #M`, where #M is open and holds the item. An unticked box without a live successor blocks closure. A partial close reads "Closing at delivered scope: N of M criteria met; remainder #M".
3. The test or builder that produced each deliverable: the command, the pass, fail and skip counts, and the SHA it ran on. Generated outputs also give their digests.
4. For engineering results: the native output location, read back, and each result against its criterion and comparator, with the standard cited by number, title and clause. It also carries the citation sidecar where the calc citation contract applies. Exit code 0, a live process or a passing unit test is not a result.
5. For data: the source URL, retrieval date, record count and digest.
6. The builder role, implementation channel, and reviewer with the verdict and review artifact.
7. Nothing from memory. Every number, path and status is read at closing time.

## C. Bulk actions, migrations and bodies

1. An agent closes at most 5 issues in one session. Each closure needs its own section-B comment; template comments do not count. More than 3 closures by one actor within a minute is treated as a defect and reviewed.
2. Scripts may label, comment and propose closures. A person or an agent closes each issue individually.
3. Imported records are created OPEN unless each one carries section-B evidence. No duplicate records are created.
4. The body of a closed issue is never edited to carry new scope. New scope goes in a new issue that links the old one.

## D. Reopening

1. Reopen, or open a successor that links the closed issue, when an audit or the owner finds any section-B element missing or false. Use a new issue where the closed body was overwritten or the record came from a migration.
2. The short plan sits on the issue itself, in five to ten lines: why it was reopened (cite the audit row); what exists (paths and SHAs, checked today); what remains, as numbered testable items with their standard clauses; the deliverable and the test that will prove it; the builder, a different reviewer, and the kind of machine the work needs; prerequisites and owner decisions; and the size. It is written in future tense. Past-tense claims cite a path or SHA.
3. Publication, delivery, data deletion and GitHub mass-writes each wait for explicit owner approval.

## E. The checker

The checker is read-only, and runs on each closing event (webhook or nightly) and monthly over the past month. Per event it reports PASS, WARN, FAIL or NOT_EVALUATED:

| # | Test | Result |
|---|---|---|
| 1 | Closer is a merged PR, a comment, or nothing; a closing event that cites a commit with no PR | commit-only or nothing: FAIL |
| 2 | PR merged head equals the approved review head, and a reviewer is recorded | mismatch: FAIL; review record unavailable: NOT_EVALUATED |
| 3 | Comment has a SHA or PR that resolves and is an ancestor of the default branch; each cited path exists at it | any missing: FAIL |
| 4 | Comment has a test command with a count | missing: FAIL (WARN for not-planned closures) |
| 5 | Every body checkbox is ticked or followed by an open `#M` | otherwise FAIL |
| 6 | Duplicate, superseded or not-planned closures name a successor or a decision, and the successor resolves and is open or itself closed under these rules | otherwise FAIL |
| 7 | Hedge words (deferred, follow-up, partial, stub, placeholder, tracked elsewhere) are followed by an open `#M` | otherwise FAIL |
| 8 | Same actor closed more than 5 issues within 10 minutes | each without test 3: FAIL |
| 9 | Closed within 60 s of creation with no comment (import) | FAIL |
| 10 | Body edited after the closing time | WARN; edit history unavailable: NOT_EVALUATED |

A FAIL is reported to the audit lane and proposed for reopening. The checker itself never writes to GitHub.
