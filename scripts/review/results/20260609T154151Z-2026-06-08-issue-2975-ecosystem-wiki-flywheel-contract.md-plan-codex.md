### Verdict: MAJOR

### Summary
The plan is much tighter than earlier rounds, but it is not implementation-ready. The remaining blockers are around fail-closed authority: the config-driven allowlist can override the plan's fixed public-safe policy, and the legal/projection path safety rules are specified but under-tested or underspecified.

### Issues Found
- [P1] Critical: The public-safe allowlist authority is internally inconsistent. The plan says public publication requires `source_publication_class` in `{public-federal-data, public-commercial-open, open-academic}` and `license_terms_class` in `{public-domain, open-license}`, but it also says the validator will derive public-safe classes from `source-classification.yaml` flags and has a test where toggling a config flag changes the result. That means a bad config edit could make `vendor-licensed`, `client-private`, or `unknown` public-safe despite the fixed acceptance criterion. The plan needs an invariant test that only the approved enum subset may ever carry `public_safe: true`.
- [P2] Important: Legal attestation path-hardening is specified but not covered by the blocking test floor. The plan requires repo-relative POSIX paths, rejects absolute paths, `..`, and symlinks, and rehashes artifacts. The blocking tests cover forged/stale evidence, but not absolute path injection, traversal, or symlink escape. Given the repo rule against absolute paths and the public-output security role of this validator, those should be non-cuttable tests.
- [P2] Important: Public projection `destination` is underspecified. The allowlist schema permits a `destination` object with a "Public URL or repo-relative public wiki path only," but the plan does not define allowed hosts, sibling repo names, path prefixes, traversal rejection, or whether arbitrary external public URLs are allowed. That leaves a route around the sibling-wiki routing contract and could let quick-reference pointers publish ungoverned destinations.

### Suggestions
- Make `source-classification.yaml` config-driven for metadata, but add a schema/invariant check that public-safe flags exactly match the plan's fixed public-safe source and license sets unless a future issue changes the standard.
- Add blocking tests for legal attestation path handling: absolute path rejected, `..` rejected, symlink rejected, and repo-relative normalized path accepted.
- Define `destination` as a closed object, for example `{repo: llm-wiki|worldenergydata-wiki|llm-wiki-<client?>, path: ...}` for repo-relative destinations plus an explicit host allowlist if public URLs are truly needed.

### Questions for Author
- Should `public_safe` flags be editable policy in config, or should config be validated against the fixed standard-defined allowlist? The current plan says both.
