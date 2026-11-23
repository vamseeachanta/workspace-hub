# Review provenance fields for local inline plan reruns

Use these fields when a plan review provider may fetch stale GitHub `main` content while the current plan artifact is local/uncommitted.

Minimum provenance block to include in the rerun prompt and saved review artifact:

```markdown
## Review Provenance
- Review target authority: inline local artifact below
- Local plan path: `docs/plans/<plan-file>.md`
- Local artifact hash: `<sha256 of exact inlined markdown>`
- Review timestamp UTC: `<YYYY-MM-DDTHH:MM:SSZ>`
- Repo branch/commit at dispatch: `<branch> / <sha or dirty-state note>`
- Remote/main visibility: may lag local draft until approval-ready evidence commit
- Retrieval rule: do not substitute GitHub `main` or path-fetched content for the inline body
```

Interpretation rule:
- A finding that says GitHub `main` or remote path content differs from the inline body is a provenance/promotion-gate finding, not automatically a substantive blocker against the local plan text.
- Still patch real content blockers found in the inline body.
- Do not publish `status:plan-review` until the final reviewed artifact and its provenance are committed/pushed or otherwise retrievable from the agreed branch.
