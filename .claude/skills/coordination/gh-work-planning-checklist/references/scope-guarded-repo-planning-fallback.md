# Scope-guarded repo planning fallback

Use this when a repository blocks `git`/`gh` operations until an explicit active scope is set.

## Trigger signal

A guarded command fails with a message like:

```text
<Repo>: no active scope; set one before git/gh
```

or:

```text
<Repo> scope required for git/gh writes; run /scope [name]
```

## Required behavior

1. **Do not bypass the guard.** Treat it as an authorization/context boundary, not a nuisance.
2. **Separate live GitHub work from local planning.** If live issue numbers do not exist, do not create canonical `docs/plans/YYYY-MM-DD-issue-NNN-*.md` files yet.
3. **Create a local pre-issue planning bundle** when useful. It may include:
   - parent/child issue architecture;
   - recommended execution order;
   - exact user CTA;
   - drafted issue titles/bodies;
   - TDD-first test lists;
   - likely file targets;
   - dependencies and serialization points;
   - canonical conversion checklist for after live issue numbers exist.
4. **Give the CTA literally and standalone.** Example:

```text
/scope deckhand
```

Then ask the user to send:

```text
continue
```

5. **Verify scope activation by retrying the guarded operation once.** If it still fails, report the exact command and guard output. Do not proceed to gh/git writes.

## Example packet paths from Deckhand calibration work

Local-only artifacts used while `gh` writes were blocked:

```text
docs/reports/chat-quality/<date>-next-batch/issue-packet/issues.md
docs/reports/chat-quality/<date>-next-batch/issue-packet/parallel-recon-synthesis.md
docs/reports/chat-quality/<date>-next-batch/issue-packet/pre-issue-planning-bundle.md
```

The pre-issue bundle explicitly said it was not a canonical issue-numbered plan because live GitHub issues did not exist yet.

## Final response shape when still blocked

```text
Still blocked. Scope is not active in this session.

Command attempted:
<command>

Result:
<guard output>

Exact CTA:
/scope <repo>

Then send:
continue
```
