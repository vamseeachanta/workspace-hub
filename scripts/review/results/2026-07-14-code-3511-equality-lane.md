# #3511 code review — equality/state lane

**Reviewer stance:** adversarial, read-only  
**Initial verdict:** MAJOR — do not approve  
**Disposition:** all three MAJOR findings and the bounded MINOR findings were patched inline and regression-tested.

## Findings and disposition

1. **MAJOR:** failed `git ls-tree` could be treated as an empty tree and erase fleet entries. Fixed by failing with `StoreUnavailable` before any mutating plumbing; regression test asserts no hash/tree/commit/push.
2. **MAJOR:** reconstruction discarded subtrees and rewrote executable/symlink modes. Fixed by preserving exact `(mode, type, sha, name)` entries and changing only the target fingerprint/intentional legacy entry; executable, symlink, subtree, CR-suffix, and regular-file tests added.
3. **MAJOR:** syntactically valid but schema-invalid ref JSON could crash comparison and be misreported as WARNING. Fixed by exact validation during collection plus controller-wide failure mapping to exit 3; poisoned-entry test added.
4. **MINOR:** unhashable role/phase values escaped as `TypeError`. Fixed with type-before-membership checks.
5. **MINOR:** `fromisoformat` accepted space-separated timestamps outside the documented RFC3339 contract. Fixed with an explicit RFC3339 syntax gate across fingerprint, health, collector, and matrix grading.
6. **MINOR:** CAS retry and atomic health preservation lacked direct tests. Added bounded success/exhaustion and failed-replace preservation tests.

## Verification

- State, publish-health, scheduler, and targeted collector tests: 78 passed.
- Fingerprint shell transaction suite: 9/9 passed.
- Sentinel isolated Git transaction suite: 4/4 passed.
- Schedule validator: 65 tasks valid.

