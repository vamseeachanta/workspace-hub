# Issue 3449 Code/Artifact Review — Round 1

- Issue: https://github.com/vamseeachanta/workspace-hub/issues/3449
- Approved baseline: `24e329f9b4c9c04d12492929f22b252a6cb6b87c`
- Reviewed pushed SHA: `1a5eed6d6422ba47885c896a2dc9f4607ec29b8d`
- Review posture: adversarial, default non-APPROVE
- Overall verdict: **MAJOR — implementation blocked; amended design requires user approval**

## Review Matrix

| Lane | Result | Scope |
|---|---|---|
| Codex child — renderer/contract | MAJOR | Descriptor binding, cleanup, Git snapshot, final validation |
| Codex child — schema/checker | MAJOR | Registry versions, no-touch boundary, checker fail-closed behavior |
| Codex child — factory/artifacts | MAJOR | Bootstrap operability, commit/push authority, privacy guidance |
| Claude CLI — focused renderer/contract retry | MAJOR | Cleanup residue and authorization invariants |
| Claude CLI — full diff | UNAVAILABLE | Two 300-second watchdog expirations; no structured result |
| Codex CLI 0.144.1 — full diff | UNAVAILABLE | Exit 124 with `Reading additional input from stdin`; no verdict |
| Gemini CLI 0.50.0 — full diff | UNAVAILABLE | Exit 41; interactive authorization required |

Provider outages degraded external review coverage. They do not convert any result to approval.

## Confirmed MAJOR Defect Classes

### 1. Python-native cleanup can delete a replacement victim

`bootstrap_renderer.py` checks an artifact's inode with `stat()` and then deletes the same pathname with a separate `unlink()` or `rmdir()`. A same-UID substitution between those calls passes the stale identity check and deletes the replacement. Stage cleanup has the same race. Regular files can also escape the ledger when `fstat()` or ledger insertion fails, and `KeyboardInterrupt`/`SystemExit` bypass `except Exception` cleanup.

The approved Python-native contract names only the directory `mkdir` → `open` gap as residual risk. Safe identity-conditional pathname deletion is not implementable with the current standard-library primitives under the stated active-substitution threat model.

### 2. Git can read disabled raw roots and untracked replacement refs

Sanitizing ambient/global/system Git configuration does not stop repository-local `[include]` or `[includeIf]` directives. `git remote get-url` followed a clone-local include into a registered disabled raw root during review. This violates the no-stat/open/enumerate raw-root guarantee.

The pinned-template Git commands also honor `.git/refs/replace/*`. A local replacement ref can change the tree/archive bytes while the manifest reports the original HEAD. Exact origin matching additionally strips meaningful leading/trailing whitespace, and the unborn-HEAD check conflates fatal exit 128 corruption with a genuinely absent branch ref.

### 3. Descriptor authority ends before content attestation and first push

The renderer validates inode inventory before its final callback but does not revalidate after the callback. It does not retain the absolute parent-path identity, and final inventory checks omit file bytes, size, and permission bits. In-place firewall mutation can therefore pass.

After render returns, the factory ignores the manifest's clone identity and uses `$TARGET` by pathname for `git add`, `commit`, and `push`. A target, `.git`, config, or origin substitution can redirect the first push after the last bound check. No executable remote-SHA attestation closes that gap.

### 4. Registry/checker state can audit green incorrectly

- Numeric legacy `0.1` accepts empty roots plus added `ingestion_enabled: true`, creating a downgrade audit bypass.
- Checker validation does not apply protected workspace/template/derived-target root disjointness.
- Checker requires fetch/push URL spellings to be identical even though each exact allowed spelling is independently valid.
- A string `"false"` for GitHub `isArchived` passes the shell checker as if it were Boolean false.

### 5. Factory guidance is not operable or privacy-consistent

The factory disables global/system Git config, then attempts a fresh commit and HTTPS push without local author identity or an explicit `gh` credential helper. On the target host, `git var GIT_AUTHOR_IDENT` exits 128 under that environment.

The rendered project README directs operators to add private client/project identifiers to the public workspace-hub `config/client-wikis.yml` relocation stub, contradicting the authoritative-private-registry contract.

## Evidence That Still Passes

- Full scoped suite at reviewed SHA: `263 passed`.
- Pinned-HEAD integration rendered 25 paths from `1a5eed6d6422ba47885c896a2dc9f4607ec29b8d`; `.git` identity was preserved.
- Ruff, `bash -n`, `shellcheck`, legal diff scan, changed-path absolute-path scan, and `git diff --check` passed.
- HEAD records `scripts/enforcement/check-client-wiki-registry.sh` as mode `100755`.
- Repository-wide absolute-path scan is unavailable in the 37%-sparse worktree because it tries to open a tracked-but-absent skill file; changed paths pass.

Passing tests do not override the demonstrated false-green cases above.

## Required User Decision

### Option 1 — Python-native residue-on-failure + bound finalizer (recommended)

The amended design will remove rehearsal staging and all automatic pathname deletion. A render failure will preserve and report a bounded residue manifest, avoiding victim deletion. Git commands will use `GIT_CONFIG=/dev/null`, disable replacement refs, and parse only a held local-config descriptor with includes/rewrites denied. Final validation will cover bytes/modes and run last. A new descriptor-bound finalize command will perform add/commit/push to an explicit registered URL, use explicit author plus `gh` credential helper, and verify the pushed remote SHA before registry update.

### Option 2 — Native syscall helper

The design will introduce a small reviewed Linux helper using `openat2`/`renameat2` no-replace semantics so identity-safe automatic cleanup can remain. This weakens the prior Python-standard-library-only decision and adds a native portability/security surface.

### Option 3 — Narrow the threat model

The design will state that no same-UID substitution is considered after descriptor binding or during cleanup/finalization. This is not recommended because it invalidates existing race claims and tests.

No option is self-approved. Implementation remains stopped until the user selects the amended contract.
