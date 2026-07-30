# #3449 plan review disagreement — r2 and inline resolution

| Provider | Verdict | Signal |
|---|---|---|
| Native Codex | MAJOR | Undefined destination authority, renderer/factory clone contradiction, and cleanup unsafe for the clone/`.git` boundary |
| Claude CLI | UNAVAILABLE | Timed out after 600 seconds with no usable output |
| Gemini CLI | UNAVAILABLE | No non-interactive authentication configured |

## Synthesis

There is no provider-verdict disagreement because native Codex supplied the only r2 verdict. Its MAJOR is controlling. Claude's independent r1 MAJOR had already reduced the scope by removing raw-reader FFI, splitting modules, and defining checker dependencies.

Per the repository's r3 inline loop-break rule, the main session resolved the new findings without dispatching another provider cycle:

- removed nonexistent `raw_root_bases` and `working_clone_base` authority;
- anchored the template to its module checkout and derived the canonical sibling root from the absolute Git common directory, including linked-worktree coverage;
- required the factory-created clean, unborn clone with a matching origin before render;
- replaced whole-destination creation/cleanup with held no-follow directory descriptors, exclusive child creation, and a device/inode-bound created-artifact ledger that can never include the clone root or `.git`;
- added main-checkout/linked-worktree, clone-precondition, path-substitution race, `.git` preservation, and ledger-bounded cleanup tests and acceptance criteria.

The cross-provider state is therefore **PASS for user review with degraded r2 availability**: Claude r1 plus native Codex r2 provided independent defect signal, all available MAJOR findings are resolved inline, and implementation remains blocked on explicit user approval.

## Inline-resolution verification

- Contract matrix assertions found exact schema `"0.2"`, unconditional enabled-ingestion rejection, common-dir derivation, clean/unborn/matching clone preconditions, `O_DIRECTORY|O_NOFOLLOW`, created-artifact ledger cleanup, linked-worktree coverage, and the user-approval implementation hard stop.
- Negative assertions found none of the superseded `working_clone_base`, configured `raw_root_bases`, or absent-destination creation design.
- `git diff --cached --check`, HTML structure/render inspection, legal diff scan, and explicit private-identifier/path scan passed.
- The full absolute-path scan is not applicable to this plan-only diff (zero staged `.sh`/`.py` files) and its sparse-checkout crash was promoted separately below; no bypass was used.

## Promoted findings

- The non-executable direct-review-helper defect was added to existing [issue #3142](https://github.com/vamseeachanta/workspace-hub/issues/3142#issuecomment-4941838852).
- The sparse-checkout failure in the absolute-path enforcement scan was filed as [issue #3459](https://github.com/vamseeachanta/workspace-hub/issues/3459). It is not part of #3449 implementation.
