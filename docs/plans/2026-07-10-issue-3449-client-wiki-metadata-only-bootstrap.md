# Plan for #3449: Client-wiki metadata-only bootstrap

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-07-11
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3449
> **Client:** N/A
> **Project:** N/A
> **Lane:** lane:codex
> **Execution mode:** parallel-readonly for resource intelligence and review; serialized implementation after approval
> **Design authority:** `docs/reports/2026-07-11-issue-3449-python-native-residue-finalizer-design.html`
> **Prior defect evidence:** `scripts/review/results/2026-07-11-issue-3449-code-review-r1.md`
> **Review artifacts:** blocking rounds `scripts/review/results/2026-07-11-plan-3449-{claude,codex,gemini}-r3.md` and `scripts/review/results/2026-07-11-plan-3449-{claude,codex}-r4.md`; final round planned at `scripts/review/results/2026-07-11-plan-3449-{claude,codex}-r5.md` plus `scripts/review/results/2026-07-11-plan-3449-disagreement-r5.md`

---

## Resource Intelligence Summary

### Current state

- Live issue #3449 is open with `status:needs-plan`, `gate:completeness`, and exactly one compute lane, `lane:codex`.
- The user selected amended design Option 1: a pure-Python renderer and descriptor-bound finalizer that never performs automatic pathname cleanup. That design approval authorizes this revised plan, not implementation.
- The previous plan, its README row, and `.planning/plan-approved/3449.md` described a superseded staging/cleanup contract. Commit `ce93d8eae` removed that stale marker and returned local plan state to `draft` before review.
- Follow-on issue #3464 records the generalizable safe-filesystem-mutation defect class found during code review.
- Candidate implementation exists on this branch. Discovery found the original schema/renderer/contract modules and tests, but the code review proved that the candidate is not safe to ship. Implementation will amend it through TDD rather than assume prior scope is complete.

### Existing code and constraints

| Surface | Observed state | Planning consequence |
|---|---|---|
| `bootstrap_schema.py` | 318 lines | Extend narrowly and keep below 400 lines. |
| `bootstrap_renderer.py` | 400 lines | Split Git, snapshot, manifest, and finalization authority into focused modules before adding behavior. |
| `bootstrap_contract.py` | 351 lines | Keep CLI/orchestration only; move layout and finalizer logic out. |
| Registry checker | Shell validation plus Python contract | Delegate clone semantics to Python; shell remains availability/orchestration only. |
| Factory skill | Performs pathname Git commit/push and lacks explicit author/credential contract | Replace that sequence with the finalizer CLI. |
| Tests | Schema, renderer, contract, security, artifact, and enforcement suites exist | Replace obsolete staging/cleanup assertions and add finalizer-specific tests. |

Coding constraints are maximum 400 lines per file and 50 lines per function. Python will use snake_case, explicit input validation, no hardcoded secrets, and no client identifiers. Linux `/proc/self/fd` behavior is an explicit platform dependency.

### Documents consulted

- [Issue #3449](https://github.com/vamseeachanta/workspace-hub/issues/3449) and its amended-design checkpoint.
- [Follow-on #3464](https://github.com/vamseeachanta/workspace-hub/issues/3464), which preserves the generalizable mutation-safety finding.
- `docs/reports/2026-07-11-issue-3449-python-native-residue-finalizer-design.html` — approved design boundary and implementation stop gate.
- `scripts/review/results/2026-07-11-issue-3449-code-review-r1.md` — concrete MAJOR defects in the prior candidate.
- `docs/plans/_template-issue-plan.md`, `docs/plans/README.md`, and `.claude/skills/coordination/issue-planning-mode/SKILL.md` — lifecycle and evidence contract; the skill was read from the canonical full checkout because this sparse worktree omits it.
- `docs/standards/HARD-STOP-POLICY.md` and `docs/standards/PARALLEL_FIRST_EXECUTION.md` — approval, TDD, review, and execution-mode requirements.
- `.claude/rules/wiki-sibling-routing.md` — `Client: N/A` is correct because this issue changes workspace-hub infrastructure, not wiki content.
- `config/client-wikis.yml` — public relocation stub; it will not become client authority.
- Two de-identified drive-index searches (`generic client wiki bootstrap`; `git descriptor bound finalizer residue`) found no relevant precedent. Results were unrelated token collisions. Three indexes were stale and three current, so live repo/design evidence remains authoritative.

### Reproduction proofs

The prior code review reproduced five correctness failures against the candidate at `1a5eed6d6`:

1. stat-then-`unlink`/`rmdir` cleanup could delete a substituted pathname victim.
2. local Git `include`/`includeIf` and replacement refs could affect supposedly pinned template or clone inspection.
3. descriptor authority ended before commit/push, and the returned inventory omitted byte and mode attestation.
4. legacy schema/checker paths could fail open through downgrade, protected-root ordering, origin mismatch, and non-boolean archived values.
5. the factory lacked isolated author/credential setup and pointed operators toward a non-authoritative public registry stub.

The full commands and captured outputs are preserved in `scripts/review/results/2026-07-11-issue-3449-code-review-r1.md`. A separate Git probe verified that `GIT_CONFIG=/dev/null` suppresses a local include-provided alias while `git rev-parse` still works in this linked worktree. This plan treats cited sources as claims for reviewers to verify, not as trusted assertions.

### Gaps to close

- There is no replacement-free committed-blob snapshot abstraction.
- There is no immutable render manifest covering the clone parent, clone root, `.git`, held config, and every rendered member's type/mode/size/SHA-256.
- There is no descriptor-bound finalizer that validates the manifest immediately before Git mutation and after every injectable operation.
- Current failure handling attempts cleanup; the approved contract requires residue preservation and a bounded, structured operator report.
- Git execution is not fully isolated from local/global/system config, replacement objects, protocol rewriting, caller Git environment, or ambient author identity.
- Recovery states for unborn, local-only, already-pushed, and mismatched clones are not explicit or idempotent.
- Checker and schema validation still contain fail-open compatibility edges.
- Factory instructions still expose pathname Git operations and do not make the private registry path, author identity, and credential helper explicit.

---

## Artifact Map

| Artifact | Path |
|---|---|
| Canonical plan | `docs/plans/2026-07-10-issue-3449-client-wiki-metadata-only-bootstrap.md` |
| Human plan companion | `docs/reports/2026-07-10-issue-3449-metadata-only-bootstrap-plan.html` |
| Approved design | `docs/reports/2026-07-11-issue-3449-python-native-residue-finalizer-design.html` |
| Schema | `scripts/client_llm_wiki/bootstrap_schema.py` |
| Renderer | `scripts/client_llm_wiki/bootstrap_renderer.py` |
| Git isolation | `scripts/client_llm_wiki/bootstrap_git.py` |
| Committed snapshot | `scripts/client_llm_wiki/bootstrap_snapshot.py` |
| Render manifest | `scripts/client_llm_wiki/bootstrap_manifest.py` |
| Finalizer | `scripts/client_llm_wiki/bootstrap_finalizer.py` |
| Layout derivation | `scripts/client_llm_wiki/bootstrap_layout.py` |
| CLI | `scripts/client_llm_wiki/bootstrap_contract.py` |
| Unit/integration tests | `tests/client_llm_wiki/test_bootstrap_*.py` |
| Checker | `scripts/enforcement/check-client-wiki-registry.sh` |
| Checker tests | `tests/enforcement/test_client_wiki_registry*.{py,sh}` |
| Factory contract | `.claude/skills/coordination/client-llm-wiki-factory/SKILL.md` |
| Public stub guidance | `config/client-wikis.yml` |
| Plan reviews | `scripts/review/results/2026-07-11-plan-3449-*-r3.md` |

---

## Deliverable

A tested metadata-only client-wiki bootstrap will render an exact replacement-free committed template into an authorized empty PRIVATE clone, preserve and report residue on every failure, and finalize the first commit and push only through a descriptor-bound, manifest-attested, Git-isolated CLI.

---

## Locked Contract

### Registry and authorization

- The authoritative registry will be an explicitly supplied private/local file; the public relocation stub will never authorize rendering or finalization.
- Schema version will be the exact string `"0.2"`. Numeric/legacy `0.1` will remain audit-only and will reject empty roots or any current-state fields rather than downgrade them.
- Every schema-0.2 entry will require an exact private repository identity, lifecycle state, `raw_roots`, `raw_source_status`, and a real boolean `ingestion_enabled`.
- `ingestion_enabled: true` will remain invalid. This issue will not add ingestion, copy raw documents, edit private registry data, or touch any `llm-wiki*` sibling.
- Protected-root overlap will be checked before any availability skip and against every module-anchored workspace/template root.

### Git isolation and clone binding

Every Git subprocess will receive an allowlisted environment containing:

```text
GIT_CONFIG=/dev/null
GIT_CONFIG_NOSYSTEM=1
GIT_CONFIG_GLOBAL=/dev/null
GIT_NO_REPLACE_OBJECTS=1
```

Caller `GIT_*` variables will be discarded except fixed command-scoped variables created by the contract. The literal inherited-key allowlist will be `PATH`, `HOME`, `XDG_CONFIG_HOME`, `GH_CONFIG_DIR`, `GH_HOST`, `GH_TOKEN`, `GITHUB_TOKEN`, `LANG`, `LC_ALL`, `LC_CTYPE`, `TMPDIR`, `TEMP`, and `TMP` when already set; subprocesses will receive no other inherited key. Tests will explicitly drop `LD_PRELOAD`, `LD_LIBRARY_PATH`, `PYTHONPATH`, `PYTHONHOME`, `GIT_EXEC_PATH`, `GIT_ASKPASS`, `SSH_ASKPASS`, and unrelated credential/helper variables. The finalizer will require `CLIENT_WIKI_GIT_AUTHOR_NAME` and `CLIENT_WIKI_GIT_AUTHOR_EMAIL`; it will translate them into command-scoped author/committer values without persisting identity in Git config. Network operations will use the fixed command-scoped helper `gh auth git-credential`, restrict accepted remote spellings to the registered GitHub repository, and verify the remote `main` SHA after push.

The clone's held `.git/config` descriptor will be inherited by the Git child with `pass_fds=(config_fd,)` and parsed there with `git config --file /proc/self/fd/<child-visible-fd> --null --list --no-includes`; `/proc/self` will intentionally refer to that child process. The parser will preserve whitespace and NUL records and use a closed key allowlist: required `core.repositoryformatversion`, `core.bare`, `remote.origin.url`, and `remote.origin.fetch`; optional `core.filemode`, `core.logallrefupdates`, `remote.origin.pushurl`, `branch.main.remote`, and `branch.main.merge`; no duplicate scalar key; exactly one independently allowed fetch URL and push URL. Every other key—including include/includeIf, URL rewrites, aliases, hooksPath, fsmonitor, sshCommand, signing, filters, credential helpers, and extensions—will fail closed. A dangling/corrupt symbolic HEAD will fail closed.

All mutating Git commands will use plumbing with fixed `-c core.hooksPath=/dev/null`; no porcelain commit command will run. Before mutation, the finalizer will reject `.git/objects/info/alternates`, `.git/objects/info/http-alternates`, `.git/info/grafts`, `.git/shallow`, any `refs/replace` namespace, and every alternate-object environment variable. It will verify that `.git/hooks` contains no executable or non-regular entry; hook samples may exist but will never be invoked because the fixed null hooks path applies to object creation and push. The independent expected tree will be materialized with `hash-object -w`, `mktree`, and `commit-tree` only after these checks; push will use the literal OID and explicit registered URL, never a repository-configured remote name or forced refspec.

### Snapshot and render manifest

The renderer will walk the committed template tree through Git object plumbing with replacement objects disabled. It will accept only trees and regular/executable blobs, reject duplicates and special/link modes, read each blob by exact object ID, and never use a tar archive or the mutable working-tree bytes.

The external manifest path will be outside the target clone, supplied explicitly, and treated as untrusted progress/evidence—not as finalization authority. Its parent directory will be opened and retained by descriptor; any pre-existing final component will be opened no-follow and rejected unless it is the expected regular mode-`0600` placeholder. The renderer will create an exclusive adjacent mode-`0600` temporary file through the held parent, write and `fdatasync` one complete versioned JSON document, use descriptor-relative `os.replace(..., src_dir_fd=parent_fd, dst_dir_fd=parent_fd)` to atomically publish it into that same bound directory, `fsync` the parent, reopen the final entry no-follow, and verify expected bytes/identity before success. Crash-before-replace may leave only the bounded temporary residue; crash-after-replace yields the complete JSON entry. The manifest will contain:

- parent, clone root, `.git`, and `.git/config` device/inode/type identities;
- registered repo identity, exact allowed origins, and pinned template commit/tree;
- every rendered relative path with type, normalized mode, byte size, and SHA-256;
- the expected firewall files and complete directory membership.

Directories will be attested but only regular files will be staged. Validation will reject partial JSON, unexpected members, path traversal, duplicate paths, type changes, same-length byte changes, size changes, mode changes, firewall mutation, identity substitution, target/config replacement, and manifest-parent rename/substitution.

At finalization, the manifest will not authorize content. The finalizer will independently re-authorize the registry row, resolve the current trusted canonical workspace commit and its exact template-subtree tree OID, rebuild the expected replacement-free template snapshot and substitutions, and compare that independent expectation with both the manifest and clone. The manifest's template tree OID must equal the independently resolved current template-subtree tree OID; an unrelated workspace commit that leaves that subtree unchanged is tolerated, while any template-tree change fails without mutation. The trust boundary is the operator-controlled workspace checkout, private registry, process environment, and `gh` credential store; the concurrently mutable target clone and external manifest are untrusted. A same-UID actor able to alter those named trust roots is out of scope because no same-UID file-permission boundary can make them unforgeable.

### Residue and finalization

The renderer will create directly under descriptor-bound clone directories with exclusive no-follow operations. It will not create rehearsal/staging trees and will never call pathname `unlink`, `rmdir`, `rename`, or truncate to clean up a failed render. Any exception, `KeyboardInterrupt`, or `SystemExit` will preserve all created objects and return/emit a bounded structured residue record containing the clone identity, completed manifest members, uncertain member, failure stage, and manual-disposition instruction. A failed partial render will not be retried in the same clone.

The CLI will add:

```text
finalize-scaffold --registry PATH --short-name SLUG --manifest PATH
```

The finalizer will reopen and bind the authorized parent/root/`.git`/config, validate the complete manifest, classify state, and allow only:

| State | Action |
|---|---|
| symbolic unborn HEAD + exact independent render + remote `main` absent | stage independently expected files, commit, non-force push, re-attest |
| independently validated exact local root commit + remote absent | retain its object ID, push that literal OID, re-attest |
| independently validated exact local root commit + equal remote `main` | retain its object ID and return idempotent success after re-attestation |
| unborn clone with existing remote `main`, or any index/worktree/tree/message/author/origin/identity/SHA mismatch | fail without mutation; preserve/report residue |

The acceptable recovery commit parser will consume the raw commit object, reject NUL/CR, and require exactly these records in this order: one `tree <40-or-64-hex>` header; one `author <exact name/email> <timestamp> <timezone>` header; one `committer <exact name/email> <timestamp> <timezone>` header; one empty separator line; and the exact commit message bytes. It will reject parent headers, missing/duplicate/reordered tree/author/committer headers, continuation lines, multiple separators, unknown/optional headers (`gpgsig`, `encoding`, `mergetag`, or any other), malformed identities, out-of-range signed timestamps, and timezones outside valid `-2359..+2359` hour/minute form. The referenced tree must equal the independently reconstructed tree. Timestamps will be validated but will not be part of semantic equality because they are intentionally nondeterministic; safety comes from the independently reconstructed exact tree plus fixed identities/message/shape.

Once the commit is validated or created, its literal object ID will be retained in memory; every push will use `<attested_oid>:refs/heads/main`, local symbolic HEAD must equal that OID immediately before and after transport, and remote `main` must equal that OID. After every transport return—success, nonzero exit, timeout, or exception—the finalizer will query the GitHub REST API through `gh api` (never clone-local config or `git ls-remote`) for remote `main` and classify it as `equal`, `absent`, `different`, or `unknown`. `equal` may recover an accepted-but-locally-reported-failed push; `different` after an attempted push will return `pushed_remote_advanced` with retained and observed OIDs; `unknown` will preserve residue and prohibit retry claims. The final success boundary will independently reconstruct and validate content again, query the same API for exact identity/PRIVATE/unarchived posture, and emit fixed JSON. Registry mutation remains a later factory step and will not occur on any failed finalizer result.

Production code will not expose an un-attested arbitrary callback boundary. Tests may inject named operations/failpoints through internal test-only interfaces; the public CLI and production entrypoint will reject any caller-supplied failpoint/callback parameter. The finalizer will attest immediately after each internal injection and immediately before returning.

---

## Pseudocode

```text
function isolated_git_env(author_required, network):
    start from allowlisted process variables, excluding caller GIT_*
    set config-null/system-off/global-null/no-replacements controls
    if author_required: require and map CLIENT_WIKI_GIT_AUTHOR_*
    if network: install fixed command-scoped gh credential helper
    return immutable environment

function load_committed_snapshot(template_root):
    resolve pinned commit and template tree with isolated Git
    recursively list exact tree object entries
    reject duplicate, link, gitlink, special, or invalid relative paths
    read each accepted blob by object ID and hash its bytes
    return immutable TemplateSnapshot

function render_scaffold(registry, slug, manifest_path):
    authorize entry and descriptor-bind parent/root/.git/config
    validate config and unborn clean clone without applying includes
    validate external mode-0600 manifest destination
    materialize exact snapshot via held directory descriptors
    after each create/write/chmod, record bounded residue progress
    validate complete member inventory and firewall
    atomically write and sync complete manifest
    on BaseException, preserve residue and emit structured failure

function validate_manifest(bound_clone, manifest):
    independently pin trusted workspace HEAD and reconstruct expected snapshot
    require manifest template/tree/member claims equal independent expectation
    require exact parent/root/.git/config identities
    enumerate target without following links
    require exact member set, types, modes, sizes, and SHA-256 values
    require firewall and origin/config invariants
    return attested render state

function finalize_scaffold(registry, slug, manifest):
    authorize and bind clone from registered identity
    validate manifest immediately
    classify unborn/local-only/remote-equal/mismatch state
    before and after each Git mutation, revalidate bound identities and manifest
    stage only independently expected regular files and create/validate exact root commit
    retain attested commit OID; require HEAD equals it before and after transport
    push attested_oid:refs/heads/main to registered HTTPS remote using fixed credentials
    verify remote main equals attested OID, GitHub PRIVATE/unarchived posture, and independent snapshot again
    return fixed success JSON; otherwise preserve/report residue without cleanup
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/client_llm_wiki/bootstrap_schema.py` | Close legacy/current-state, boolean, and protected-root validation gaps. |
| Modify | `scripts/client_llm_wiki/bootstrap_renderer.py` | Retain descriptor-bound materialization; remove tar, staging, and cleanup authority. |
| Add | `scripts/client_llm_wiki/bootstrap_git.py` | Centralize isolated Git environment, config parsing, clone state, and remote verification. |
| Add | `scripts/client_llm_wiki/bootstrap_snapshot.py` | Read replacement-free committed tree/blob inventory. |
| Add | `scripts/client_llm_wiki/bootstrap_manifest.py` | Define strict manifest schema, atomic persistence, and complete attestation. |
| Add | `scripts/client_llm_wiki/bootstrap_finalizer.py` | Implement explicit recovery state machine and descriptor-bound commit/push. |
| Add | `scripts/client_llm_wiki/bootstrap_layout.py` | Keep layout derivation separate so CLI and finalizer remain within size limits. |
| Modify | `scripts/client_llm_wiki/bootstrap_contract.py` | Expose validation/render/finalize commands and fixed JSON/error taxonomy. |
| Modify/Add | `tests/client_llm_wiki/test_bootstrap_*.py` | Add RED-first schema, Git, snapshot, residue, manifest, finalizer, and CLI coverage. |
| Add | `scripts/enforcement/check_python_function_lengths.py` and `tests/enforcement/test_python_function_lengths.py` | Enforce the 50-line function guardrail mechanically. |
| Modify | `scripts/enforcement/check-client-wiki-registry.sh` | Delegate clone semantics to Python and preserve dependency/error taxonomy. |
| Modify | `tests/enforcement/test_client_wiki_registry*.{py,sh}` | Cover checker fail-closed edges and delegation. |
| Modify | `.claude/skills/coordination/client-llm-wiki-factory/SKILL.md` | Replace pathname Git workflow with render/finalize/private-registry sequence. |
| Modify | `tests/client_llm_wiki/test_client_llm_wiki_factory_artifacts.py` | Exercise factory ordering and prohibit pathname Git operations. |
| Modify | `config/client-wikis.yml` | Point only to authoritative private-registry procedure; retain empty public stub. |
| Modify | `docs/reports/2026-07-10-issue-3449-metadata-only-bootstrap-plan.html` | Keep human plan companion aligned with this revised contract. |
| Modify | `docs/plans/README.md` | Track the current gate. |

---

## TDD Implementation Sequence

Each task will begin with the named focused tests failing for the intended missing behavior, then add only enough production code to pass. Commits will use pathspec form to avoid sweep contamination.

### Task 1 — Close schema and protected-root fail-open paths

**Tests:** add `test_legacy_numeric_version_rejects_empty_raw_roots`, `test_legacy_numeric_version_rejects_current_state_fields`, and `test_validate_registry_rejects_each_module_anchored_protected_root`; extend checker tests for non-boolean archived state and protected-overlap-before-availability. Add RED tests for a 51-line function, nested/async functions, decorators, comments/blank lines, and valid 50-line functions before implementing the function-length checker.

```bash
uv run --frozen pytest tests/client_llm_wiki/test_bootstrap_schema.py -q
uv run --frozen pytest tests/enforcement/test_client_wiki_registry.py -q
git commit -m "fix(client-wiki): close bootstrap schema downgrade paths" -- scripts/client_llm_wiki/bootstrap_schema.py tests/client_llm_wiki/test_bootstrap_schema.py scripts/enforcement/check-client-wiki-registry.sh tests/enforcement/test_client_wiki_registry.py scripts/enforcement/check_python_function_lengths.py tests/enforcement/test_python_function_lengths.py
```

### Task 2 — Isolate Git and bind clone configuration

**Tests:** reject local `include`/`includeIf` without opening or applying targets; reject every non-allowlisted key including hooks/fsmonitor/ssh/signing/filter/credential/extension controls; reject URL rewrite keys; preserve origin whitespace; reject multiple fetch origins; accept only the enumerated structural keys and independently allowed fetch/push spellings; reject dangling/corrupt symbolic HEAD; prove caller Git variables are dropped and global/system configuration cannot supply first-commit identity.

```bash
uv run --frozen pytest tests/client_llm_wiki/test_bootstrap_git.py -q
git commit -m "feat(client-wiki): isolate bootstrap git authority" -- scripts/client_llm_wiki/bootstrap_git.py scripts/client_llm_wiki/bootstrap_layout.py tests/client_llm_wiki/test_bootstrap_git.py
```

### Task 3 — Replace archive rendering with committed blob snapshots

**Tests:** replace obsolete tar tests with tree traversal, mode, duplicate, and special-entry rejection; activate a real `refs/replace` control and prove it is ignored; prove bytes are read from exact committed blob IDs rather than the working tree.

```bash
uv run --frozen pytest tests/client_llm_wiki/test_bootstrap_snapshot.py -q
git commit -m "feat(client-wiki): snapshot exact committed template blobs" -- scripts/client_llm_wiki/bootstrap_snapshot.py tests/client_llm_wiki/test_bootstrap_snapshot.py
```

### Task 4 — Preserve and report render residue

**Tests:** inject failure at create, bind/fstat, ledger update, write, chmod, and final validation; prove residue remains and no Python-level cleanup `unlink`/`rmdir`/`rename`/truncate primitive is invoked; cover `KeyboardInterrupt` and `SystemExit`; require a bounded structured residue record; prove no rehearsal stage and no retry into a failed partial clone; prove public CLI/entrypoint rejects caller-supplied failpoints or callbacks.

```bash
uv run --frozen pytest tests/client_llm_wiki/test_bootstrap_renderer.py tests/client_llm_wiki/test_bootstrap_contract_security.py -q
git commit -m "fix(client-wiki): preserve failed render residue" -- scripts/client_llm_wiki/bootstrap_renderer.py scripts/client_llm_wiki/bootstrap_contract.py tests/client_llm_wiki/test_bootstrap_renderer.py tests/client_llm_wiki/test_bootstrap_contract_security.py
```

### Task 5 — Persist and attest the complete render manifest

**Tests:** cover parent/root/`.git`/config identities and every path type/mode/size/SHA-256; reject same-length byte, size, mode, firewall, unexpected-member, target-parent, config, manifest-parent, and final manifest substitutions; validate after every injected operation and immediately before return; reject inside-target, partial, non-0600, non-regular, and symlink manifest paths; prove file and held parent are synced around atomic publication.

```bash
uv run --frozen pytest tests/client_llm_wiki/test_bootstrap_manifest.py tests/client_llm_wiki/test_bootstrap_renderer.py -q
git commit -m "feat(client-wiki): attest complete render manifests" -- scripts/client_llm_wiki/bootstrap_manifest.py scripts/client_llm_wiki/bootstrap_renderer.py tests/client_llm_wiki/test_bootstrap_manifest.py tests/client_llm_wiki/test_bootstrap_renderer.py
```

### Task 6 — Add descriptor-bound finalization and recovery

**Tests:** in new `test_bootstrap_finalizer.py`, cover initial success, local-commit/remote-absent recovery, idempotent remote-equal success, and rejection without mutation for different HEAD/index/worktree/identity/origin/remote SHA. Forge a self-consistent replacement manifest/clone and prove independent template reconstruction rejects it. Install an executable hook and each alternate/graft/shallow surface and prove the finalizer neither executes nor accepts it. Require the exact raw root-commit grammar above, with separate negative controls for missing/duplicate/reordered tree/author/committer, parent, wrong committer, unknown/optional header, continuation, multiple separator, NUL/CR, malformed identity/timestamp/timezone, and semantic lookalike with a wrong tree. Inject HEAD/ref substitution before transport and prove the literal retained OID—not symbolic HEAD—is pushed. Simulate success, failure-after-server-accept, timeout, exception, remote advancement, absence, and lookup failure; require the exact `equal`/`absent`/`different`/`unknown` residue classification. Require author variables, unavailable credentials failure, first commit with global/system config disabled, exact success JSON, GitHub PRIVATE/unarchived re-attestation, and immediate independent snapshot/manifest checks around every injected operation.

```bash
uv run --frozen pytest tests/client_llm_wiki/test_bootstrap_finalizer.py tests/client_llm_wiki/test_bootstrap_contract.py -q
git commit -m "feat(client-wiki): finalize scaffold through bound descriptors" -- scripts/client_llm_wiki/bootstrap_finalizer.py scripts/client_llm_wiki/bootstrap_contract.py tests/client_llm_wiki/test_bootstrap_finalizer.py tests/client_llm_wiki/test_bootstrap_contract.py
```

### Task 7 — Delegate checker semantics and migrate the factory

**Tests:** prove the checker delegates clone/config inspection to Python, accepts valid mixed fetch/push forms, rejects includes/rewrites/non-boolean archived values, and checks protected overlap before availability. Replace substring-only factory assertions with an executable fake-tool flow proving render writes directly to the explicit external manifest path (never stdout piped through `tee`) → finalize consumes that path → registry update ordering, registry update suppression on any finalizer/attestation failure, required author variables/credential helper, authoritative private registry guidance, and absence of pathname `git add`, `git commit`, or `git push` instructions.

```bash
uv run --frozen pytest tests/enforcement/test_client_wiki_registry.py tests/client_llm_wiki/test_client_llm_wiki_factory_artifacts.py -q
bash tests/enforcement/test_client_wiki_registry.sh
git commit -m "docs(client-wiki): route factory through scaffold finalizer" -- scripts/enforcement/check-client-wiki-registry.sh tests/enforcement/test_client_wiki_registry.py tests/enforcement/test_client_wiki_registry.sh .claude/skills/coordination/client-llm-wiki-factory/SKILL.md tests/client_llm_wiki/test_client_llm_wiki_factory_artifacts.py config/client-wikis.yml
```

### Task 8 — Full verification and code-stage adversarial review

```bash
uv run --frozen pytest tests/client_llm_wiki -q
uv run --frozen pytest tests/enforcement/test_client_wiki_registry.py -q
bash tests/enforcement/test_client_wiki_registry.sh
uv run --frozen pytest -q
bash scripts/legal/legal-sanity-scan.sh --diff-only
find scripts/client_llm_wiki -name '*.py' -print0 | xargs -0 wc -l
git diff --name-only --diff-filter=ACMR origin/main...HEAD -- '*.py' | xargs -r uv run --no-project python scripts/enforcement/check_python_function_lengths.py
```

Task 1 will add the currently absent `scripts/enforcement/check_python_function_lengths.py` as a deterministic AST/tokenize-based checker with focused tests before production modules grow. It will count the inclusive physical source span from the first decorator (or `def`/`async def`) through `end_lineno`, including signature, blank, and comment lines within that span. The implementation will not substitute manual inspection for the 50-line acceptance criterion.

The implementation will then receive T3 adversarial code/artifact review from Claude, Codex, and Gemini. Any MAJOR will be fixed through a new RED/GREEN cycle and re-reviewed. The completeness gate and pre-completion cleanup audit will run before closeout, not during this planning gate.

---

## TDD Test Matrix

| Area | Required verification | False-green control |
|---|---|---|
| Schema | Legacy/current-state rejection and all protected anchors | Each invalid field/root tested independently. |
| Git config | Includes/rewrites/duplicates rejected; exact mixed origins accepted | Malicious include target has an observable side effect if opened/applied. |
| Snapshot | Exact committed object inventory | Working-tree mutation and active replacement ref differ from committed bytes. |
| Residue | Every failure class preserves created objects | Spies fail the test if cleanup syscalls/helpers are invoked. |
| Manifest | Complete identities and member hashes/modes | Same-size mutation, mode-only mutation, unexpected file, manifest-parent/final-entry substitution controls. |
| Finalizer | Independent template reconstruction and three allowed recovery states only | Forged manifest, commit-shape, and ref-substitution controls assert no unauthorized OID or registry mutation. |
| Credentials | Explicit author and fixed helper | Ambient config contains tempting but invalid author/helper values. |
| Factory | Correct executable sequence | Fake tools fail if registry update precedes verified finalization. |

Hermetic tests can prove parser boundaries, malicious-include semantics, deterministic failpoints, and fake transport behavior. They cannot prove absence of every syscall without an external tracer, exhaust every scheduler interleaving, or perform a real GitHub credential/push flow. An opt-in integration test may exercise live GitHub only with explicit credentials and a disposable private repository; it will not gate the hermetic suite. Linux `/proc/self/fd` support is required and will fail closed elsewhere.

---

## Acceptance Criteria

- [ ] Schema `0.2` supports metadata-only and source-registered-disabled rows while rejecting every enabled-ingestion state.
- [ ] Legacy numeric/version paths cannot accept empty roots or current-state fields; archived state is a real boolean; protected overlap is checked before availability skips.
- [ ] No code, test fixture, plan, report, or factory instruction contains a client identifier, private raw path, secret, or invented raw-data location.
- [ ] Every Git command uses the isolated environment; local/global/system includes, URL rewrites, caller Git variables, and replacement refs cannot influence behavior.
- [ ] The snapshot is derived from exact committed tree/blob objects and rejects links, gitlinks, specials, duplicates, traversal, and unsupported modes.
- [ ] Rendering uses held descriptors and exclusive no-follow creation, with no tar or rehearsal stage; no Python-level pathname cleanup primitive is invoked on failure (universal syscall absence remains outside hermetic proof without a tracer).
- [ ] Every failure including `KeyboardInterrupt`/`SystemExit` preserves residue and emits a bounded structured manual-disposition record.
- [ ] The external mode-0600 manifest uses a bound/synced parent and binds parent/root/`.git`/config plus every rendered member's type/mode/size/SHA-256, but never serves as finalization authority.
- [ ] Finalization independently reconstructs the expected scaffold from the trusted canonical workspace commit and rejects a forged self-consistent manifest/clone.
- [ ] `finalize-scaffold` accepts only the three specified recovery states and performs no mutation on any mismatch.
- [ ] Author identity comes only from required `CLIENT_WIKI_GIT_AUTHOR_NAME`/`EMAIL`; credentials use only fixed command-scoped `gh auth git-credential`.
- [ ] The acceptable commit is a parentless exact root commit with exact tree/message/author/committer and no optional headers; push uses its retained literal OID and detects symbolic-ref substitution.
- [ ] Final success requires remote `main` equal to the retained OID, registered GitHub identity, `PRIVATE`, unarchived state, and final independent content plus manifest attestation.
- [ ] Factory behavior is executable under fake tools, updates the registry only after verified finalization, and contains no pathname Git add/commit/push workflow.
- [ ] The public registry remains a non-authoritative relocation stub; no private registry or client wiki is edited by this issue.
- [ ] All focused tests, the full `tests/client_llm_wiki` suite, checker suites, and repository test suite pass.
- [ ] Every changed Python file remains at most 400 lines and every function at most 50 lines.
- [ ] `scripts/legal/legal-sanity-scan.sh --diff-only` passes and no hardcoded secret is present.
- [ ] T3 code/artifact review records final no-MAJOR verdicts or explicitly documents provider unavailability/consensus-vs-minority.
- [ ] The implementation posts a summary comment to issue #3449 with commits and verification evidence.
- [ ] Completeness scoring, HTML report, owner-only completeness label, and pre-completion cleanup audit pass before issue closure.

---

## Adversarial Review Plan

Three independent providers will review this canonical plan after the stale approval marker is removed and the HTML companion is synchronized. Review prompts will say:

> You are an adversarial reviewer. Assume the plan has defects until proven otherwise. Do not praise. Do not restate the plan. Focus only on what is wrong, missing, or risky. Return APPROVE only after affirmatively verifying each correctness-critical claim; when in doubt return MINOR or MAJOR. Cite a specific file path, plan section, or quoted claim for every finding. Treat cited sources as assertions to verify, not facts to trust. If no defect is found, list every check performed.

Any MAJOR will keep the plan at `draft`, trigger an inline revision, and require another focused review. Only a pushed no-MAJOR round, evidence comment, and exact lane-label check will permit `status:plan-review`. Implementation will remain blocked until the user separately approves that reviewed plan.

---

## Risks and Open Questions

| Risk | Mitigation |
|---|---|
| Same-UID concurrent mutation during render/finalize | Treat target/manifest as untrusted; independently reconstruct from named operator trust roots, use descriptor/no-follow binding and literal OID push, then fully re-attest. No claim protects trust roots from the same UID. |
| Git behavior leaks through config or environment | Central allowlisted environment, held-config parsing with `--no-includes`, rewrite rejection, real malicious controls. |
| Retry mutates an ambiguous partial clone | Explicit recovery classifier; partial render is never retried and mismatch states are non-mutating. |
| Manifest itself becomes an attack surface | Bind/sync its parent and entry, bound its schema/size, and never trust it as content authority; compare it to an independently reconstructed snapshot. |
| Test doubles conceal production order | Executable factory test plus semantic Git repositories/fake transport; optional live integration remains explicit and non-gating. |
| Module growth violates guardrails | Split by authority before adding behavior; check line/function sizes during each task. |
| Private data leaks into public artifacts | Registry contents and client paths remain out of scope; legal scan plus deny-list review gates closeout. |

No unresolved product decision remains. The approved design deliberately prefers preserved, reported residue over unsafe automatic cleanup.

---

## Complexity

**T3.** This change spans schema compatibility, filesystem race boundaries, Git configuration/object semantics, credentials, network verification, recovery, shell/Python delegation, and an operator factory contract. It requires staged TDD, three-provider plan and code review, legal/security verification, and explicit user approval between planning and implementation.
