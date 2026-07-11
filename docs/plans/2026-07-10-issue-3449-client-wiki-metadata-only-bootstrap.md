# Plan for #3449: Client-wiki metadata-only bootstrap

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-07-10
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3449
> **Client:** N/A
> **Project:** N/A
> **Lane:** lane:codex
> **Review artifacts:** `scripts/review/results/2026-07-10-plan-3449-claude.md` | `scripts/review/results/2026-07-10-plan-3449-codex.md` | `scripts/review/results/2026-07-10-plan-3449-gemini.md`

---

## Resource Intelligence Summary

### Existing repo code

- `.claude/skills/coordination/client-llm-wiki-factory/SKILL.md` defines a manual, one-time private-repository bootstrap. Its prerequisites, variables, raw-source check, and placeholder substitution require a populated raw root before a scaffold can be created.
- `scripts/enforcement/check-client-wiki-registry.sh` validates registry shape plus selected GitHub, clone, and firewall facts. It accepts `raw_roots` as a sequence but does not define empty-root semantics, validate ingestion state, or expose a fail-closed ingestion gate.
- `tests/enforcement/test_client_wiki_registry.sh` uses static fixtures and checks that the registry checker is executable. The tracked checker mode is `100644`, so the suite reports eight skips as failures. Invoking the checker through `bash` then exposes live GitHub/clone dependencies in two nominal fixtures.
- `scripts/client_llm_wiki/promotion_ledger.py::validate_structure()` intentionally accepts `null` values in the example ledger, while full validation rejects a real entry without a source path. The metadata-only scaffold can therefore keep a clearly labeled structural example with `source_path: null` without weakening semantic validation for active ledgers.
- Seven files under `templates/client-llm-wiki/` contain `<CLIENT_RAW_ROOT>` assumptions, including the hidden `.gitignore`. The template tree already contains the privacy-firewall dotfiles that every render must preserve.
- Aggregate-only inspection of the private registry on live `main` shows eight entries: one explicit empty-root entry carries `raw_source_status` and `ingestion_enabled`, while seven source-backed legacy entries omit those fields. The reusable contract must recognize this migration state without treating omission as permission to ingest.
- `scripts/client_llm_wiki/` contains no raw reader, but live coverage is partial: the private registry has eight entries and only two matching client-wiki checkouts are present on this host. One inspected checkout contains eight actual raw-access surfaces (one dispatcher, six independently callable content extractors, and one directory-metadata scanner); four other matches consume generated/committed artifacts. The other inspected checkout's match consumes committed inputs. Six registered wikis are not checked out here. This issue will establish reusable contracts and a transition block; it will not claim that existing private consumers are already covered.

### Standards

Not applicable. This issue changes reusable repository-bootstrap governance and contains no engineering constants or standards-derived calculations.

### LLM Wiki pages consulted

No wiki content is in scope. The private/generic routing rule is relevant only as a boundary: this issue will change factory infrastructure in `workspace-hub`, not any client or generic wiki content.

### Documents consulted

- [Issue #3449](https://github.com/vamseeachanta/workspace-hub/issues/3449) — requires explicit empty roots, disabled ingestion, no invented or copied raw data, a later authorization transition, and fail-closed raw ingestion.
- `docs/plans/README.md` and `docs/plans/_template-issue-plan.md` — require resource intelligence, embedded reproduction evidence, adversarial review, and a hard user-approval stop.
- `docs/governance/` client-wiki foundation history — establishes one reusable template tree, a private registry as source of truth, a PRIVATE repository gate, and dotfile-based privacy firewall. This plan will preserve those decisions while removing the raw-root prerequisite.
- `config/client-wikis.yml` — is a public relocation stub; reusable tooling must accept a caller-provided private/local registry and must not infer client state from this empty public file.
- `docs/standards/PARALLEL_FIRST_EXECUTION.md` — supports parallel read-only discovery/review but serialized edits because the checker, factory, templates, and tests form one coupled contract.
- Drive-index query `client wiki bootstrap metadata-only factory` returned no relevant drive files. Three indexes were stale at query time, but the issue is fully specified by live code and registry-shape evidence; no mount-drive document path will enter this public plan or implementation.

### Gaps identified

- No machine-readable bootstrap-mode contract exists.
- No read-boundary API can bind an exact requested source to explicit registry permission; a standalone boolean check would still permit path substitution and check/use races.
- No deterministic renderer can create a path-neutral scaffold while preserving dotfiles and refusing symlink/data-copy hazards.
- The general registry checker can degrade open when the private registry is unavailable; a raw-ingestion decision must instead fail closed.
- Existing source-backed rows and the `registry_version: 0.1` private registry need an explicit migration posture: they may remain audit-compatible, but new bootstrap and raw-source reads must require schema `0.2` plus explicit state.
- Existing/private source readers require a client-scoped inventory and guarded-open integration before they may be described as governed by this contract. That work cannot enter this public reusable issue because the live checkout set is incomplete and consumer details are private.
- Existing checker tests are not hermetic and the tracked checker is not directly executable despite operator documentation invoking it as a program.

### Evidence (embedded verification)

**Issue status** (verified 2026-07-11T01:11:10Z via `gh issue view`):

- `#3449` — OPEN — `Client-wiki factory: support metadata-only bootstrap without invented raw bucket`; labels: `enhancement`, `status:needs-plan`; no comments.

**File and mode evidence** (verified at `origin/main` commit `8d501f3ce00369f01f704df067275004e27030bd`):

```text
EXISTS  .claude/skills/coordination/client-llm-wiki-factory/SKILL.md
EXISTS  scripts/enforcement/check-client-wiki-registry.sh
EXISTS  tests/enforcement/test_client_wiki_registry.sh
EXISTS  templates/client-llm-wiki/
MISSING scripts/client_llm_wiki/bootstrap_contract.py
MISSING tests/client_llm_wiki/test_bootstrap_contract.py

git ls-files -s scripts/enforcement/check-client-wiki-registry.sh
100644 03f01f0fa2cd13e7f8e89a39a26a520b5e9866b4 0 scripts/enforcement/check-client-wiki-registry.sh
```

**Raw-root assumption proof**:

```text
rg --hidden -l '<CLIENT_RAW_ROOT>' .claude/skills/coordination/client-llm-wiki-factory templates/client-llm-wiki
→ factory skill plus seven template files (including templates/client-llm-wiki/.gitignore)

rg -n 'raw_source_status|ingestion_enabled' scripts/enforcement/check-client-wiki-registry.sh
→ no matches

rg --hidden -n 'raw_roots|open_authorized_raw_source|require-ingestion' scripts/client_llm_wiki
→ no raw-source reader or ingestion entrypoint

privacy-safe aggregate checkout scan and candidate classification
→ registered wikis: 8; checked out on this host: 2 (25%); actual raw-access surfaces: 8 in one checkout; generated/committed-only matches: 5 across both checkouts; unexamined registered wikis: 6
```

**Reproduction proof** (2026-07-11T01:11:10Z):

```text
$ bash tests/enforcement/test_client_wiki_registry.sh
=== client-wiki-registry checker test suite ===
  test_01_consistent_registry_passes... SKIP (no checker yet — TDD RED expected)
  ... six equivalent skips omitted ...
  test_08_firewall_guard_fails... SKIP (no checker yet — TDD RED expected)
=== Total: 0 pass / 8 fail ===
exit 8
```

Direct `bash` invocation against the two nominal legacy fixtures exits `1` because they query live GitHub/clone state. Identifiers and host paths are intentionally omitted from this public reusable plan; the failing mechanism is visible in `tests/enforcement/test_client_wiki_registry.sh:25-63` and the fixture files.

The issue's functional claim also reproduces: the factory requires a raw variable, checks its mount path, and substitutes `<CLIENT_RAW_ROOT>` before repository creation. The observed behavior matches the issue claim: **YES**.

Distinct sources consulted: issue body; factory skill; registry checker; checker tests/fixtures; template tree; promotion-ledger validator; public/private registry shape; prior plan/design index; drive index.

---

## Artifact Map

| Artifact | Path |
|---|---|
| Canonical issue plan | `docs/plans/2026-07-10-issue-3449-client-wiki-metadata-only-bootstrap.md` |
| Human review companion | `docs/reports/2026-07-10-issue-3449-metadata-only-bootstrap-plan.html` |
| Bootstrap contract, guarded read boundary, and CLI | `scripts/client_llm_wiki/bootstrap_contract.py` |
| Contract/renderer tests | `tests/client_llm_wiki/test_bootstrap_contract.py` |
| Registry checker | `scripts/enforcement/check-client-wiki-registry.sh` |
| Deterministic checker tests | `tests/enforcement/test_client_wiki_registry.py` |
| Factory operator contract | `.claude/skills/coordination/client-llm-wiki-factory/SKILL.md` |
| Public schema guidance | `config/client-wikis.yml` |
| Path-neutral scaffold | `templates/client-llm-wiki/` |
| Plan reviews | `scripts/review/results/2026-07-10-plan-3449-{claude,codex,gemini}.md` |

---

## Deliverable

A generic, tested metadata-only client-wiki bootstrap mode will create a PRIVATE, path-neutral scaffold from an explicit empty-root registry entry, while a guarded read API will refuse to open a requested raw source until schema, lifecycle, privacy, root containment, live repository posture, and host availability all authorize that exact source.

---

## Locked Contract and State Transitions

The private/local registry will remain the authority. Schema `0.2` will introduce the permission-bearing fields, top-level `raw_root_bases` and `working_clone_base` host authorities, and a `raw_reader_integration` attestation required only when ingestion is enabled. Its YAML value will be the exact string `registry_version: "0.2"` rather than a floating-point number. The public relocation stub will move to that version, document the generic shape with empty/null host authorities, and remain empty; the private registry will migrate under a separate approved private/client-scoped change before any new bootstrap or raw-source read uses this contract.

`ingestion_enabled` will mean **raw-source ingestion only**. It will not prohibit owner notes, authorized public research, or metadata authoring. `raw_source_status: not-mounted` will mean that no authorized raw root is registered for the wiki; it will not claim that every host has the same transient mount state. Live host availability will be computed at the read boundary.

| State | `raw_roots` | `raw_source_status` | `ingestion_enabled` | Bootstrap | Raw ingest |
|---|---|---|---|---|---|
| Metadata-only | `[]` | `not-mounted` | `false` | allowed only for schema `0.2`, `status: planned`, `posture: client-private`, declared `visibility: PRIVATE` | denied |
| Source registered, disabled | unique normalized absolute strings | `mounted` | `false` | allowed under the same bootstrap preconditions | denied |
| Source registered, enabled | unique normalized absolute strings | `mounted` | `true` | registry-invalid unless lifecycle is `bootstrapped`/`live`; denied for a new bootstrap | denied unless `raw_reader_integration` is privately verified and bound to the checked-out repo commit/manifest; then selected consumers may use their approved guarded integration |
| Legacy source-backed | non-empty strings | absent | absent | schema `0.1` audit-compatible with warning; render/bootstrap denied | denied until explicitly migrated |
| Any other combination | any | any | any | denied | denied |

The later authorization sequence will be explicit and reversible without moving data:

1. A separately approved private/client-scoped change will first migrate the canonical private registry to schema `0.2`; legacy rows may remain audit-compatible but will not gain read permission.
2. That change may add the authorized root(s), set `raw_source_status: mounted`, and will retain `ingestion_enabled: false` while the registry row is `planned` and the repository is bootstrapped.
3. After the private scaffold is pushed and the row becomes `bootstrapped`, the registry checker will validate schema, declared privacy posture, actual repository privacy, and host-aware root state.
4. Before enablement, a separately approved private per-repository integration will inventory every raw-touching entrypoint, cover direct CLIs as well as dispatchers and directory scanners, install a supported guard boundary, add bypass tests, commit a canonical `.client-wiki/raw-reader-manifest.yml`, and record `raw_reader_integration` with exact contract/status, the 40-hex covered repository commit, the manifest's 64-hex SHA-256, and a private evidence URL whose repository slug matches the registry entry.
5. Only then may a second explicit, approved change set `ingestion_enabled: true`. A new bootstrap will never begin enabled, and schema/checker validation will reject true without the verified integration mapping.
6. Governed file-reading Python integrations may use `open_authorized_raw_source(...)`, passing the exact requested file. The API will open that file once, validate the opened descriptor against an authorized root, and yield the already-open stream; missing registry, schema `0.1`, public stub, missing entry, missing integration evidence, disallowed lifecycle/privacy, disabled state, path escape, symlink, non-regular file, unavailable root, or failed live repository lookup will raise before any bytes are returned. Directory scanners and subprocess/path consumers will remain blocked until their private integration supplies and tests an appropriate bound capability.
7. Disabling ingestion will only flip the boolean to `false`; it will not delete, move, copy, or dereference any raw source.

The general registry audit may continue to warn/skip when only the public relocation stub or schema `0.1` is available. That behavior will **not** be reused for bootstrap rendering or raw-source authorization. The fail-closed claim is scoped to governed factory/client-wiki APIs; arbitrary shell or filesystem tools are outside this repository's enforcement boundary and will be named as such in operator documentation.

---

## Pseudocode

```text
enum BootstrapMode:
    METADATA_ONLY
    SOURCE_BACKED_DISABLED
    SOURCE_BACKED_ENABLED
    LEGACY_SOURCE_BACKED

function load_registry_entry(registry_path, short_name):
    parse YAML with a duplicate-key-rejecting safe loader
    reject missing, relocated-only, malformed, duplicate, or absent target
    return one mapping

function classify_entry(entry):
    require raw_roots to be a list of nonblank strings
    if roots are empty:
        require raw_source_status == "not-mounted"
        require ingestion_enabled is exactly false
        return METADATA_ONLY
    if both state fields are absent:
        return LEGACY_SOURCE_BACKED with warning
    require raw_source_status == "mounted"
    require ingestion_enabled is a boolean
    if ingestion_enabled is true:
        require status in {"bootstrapped", "live"}
        require raw_reader_integration.contract_version == "1"
        require raw_reader_integration.status == "verified"
        require covered_repo_commit is 40 lowercase hex
        require entrypoint_manifest_sha256 is 64 lowercase hex
        require evidence_ref is a private-repo URL matching entry.repo
        return SOURCE_BACKED_ENABLED
    return SOURCE_BACKED_DISABLED

function validate_roots(registry, entry, require_present):
    require raw_root_bases and raw_roots to contain normalized absolute paths
    reject relative paths, dot-dot segments, filesystem root, and duplicate normalized roots
    require each raw root to be strictly below (never equal to) one allowlisted base
    when require_present, lstat real bases/roots and reject symlinks or non-directories
    require resolved roots to remain strictly contained in resolved bases and remain unique
    return normalized authorized roots

function authorize_bootstrap(registry_path, short_name):
    registry, entry = load authority internally from registry_path and short_name
    require registry_version == "0.2" and an explicit nonlegacy mode
    require status == "planned", posture == "client-private", visibility == "PRIVATE"
    require mode in {METADATA_ONLY, SOURCE_BACKED_DISABLED}
    if mode is SOURCE_BACKED_DISABLED: validate_roots(registry, entry, require_present=false)
    validate short_name and repo slug against strict allowlist patterns
    validate working_clone_base as an absolute real directory disjoint from every raw base/root
    derive destination internally as working_clone_base / validated repo basename
    require destination is disjoint in both directions from raw/template/workspace trees
    return authorized render inputs and derived destination

function open_authorized_raw_source(registry_path, short_name, requested_source):
    registry, entry = load authority internally from registry_path and short_name
    require registry_version == "0.2"
    mode = classify_entry(entry)
    require mode == SOURCE_BACKED_ENABLED
    require status in {"bootstrapped", "live"}
    require posture == "client-private" and declared visibility == "PRIVATE"
    call the module-owned live repository verifier; require PRIVATE and not archived
    require derived local wiki HEAD == covered_repo_commit
    hash the fixed committed raw-reader manifest and require entrypoint_manifest_sha256
    validate roots against registry-owned raw_root_bases with require_present=true
    open and retain the selected authorized root directory descriptor
    open requested_source relative to that root with Linux openat2
        RESOLVE_BENEATH | RESOLVE_NO_SYMLINKS | RESOLVE_NO_MAGICLINKS
        and O_RDONLY | O_NONBLOCK | O_CLOEXEC
    immediately fstat and require a regular file before wrapping the descriptor
    yield that same already-open stream; close every descriptor on exit or failure

function render_scaffold(registry_path, short_name):
    inputs = authorize_bootstrap(registry_path, short_name)
    pin repository HEAD sha and archive that exact Git object for the canonical template subtree
    inspect archive members; allow directories/regular blobs only and reject traversal/link/special modes
    extract members manually into a fresh staging directory adjacent to derived destination
    replace allowlisted identity/status placeholders in staging with literal string replacement
    never read dirty/untracked template files; never accept caller template/destination paths
    never read from raw_roots or embed a raw-root path
    validate staged manifest, privacy-firewall dotfiles, and zero unresolved CLIENT/raw-state placeholders
    preserve PROJECT_SHORT_NAME for later project instantiation
    atomically install staging with Linux renameat2(RENAME_NOREPLACE); fail closed if unavailable
    return rendered-file manifest with pinned template commit and derived destination

function validate_registry_contract(registry):
    missing, malformed, or unsupported registry_version fails
    exact legacy numeric 0.1 receives an audit-only warning
    exact string "0.2" validates host-authority types and classifies every entry
    explicit source-backed rows call validate_roots(..., require_present=false)
    errors make the checker fail; legacy rows never receive operation authorization
```

CLI subcommands will be limited to `validate-registry`, `classify`, `render`, and `verify-private-repo`. There will be no check-only raw-source CLI: it would invite `check && arbitrary-reader` and recreate the check/use bypass. Public operations will accept a registry path plus `short_name` and will derive the entry, verifier, committed template snapshot, and destination internally; tests may inject private module seams without exposing caller-selected authority in the public API. The only raw-source authorization surface implemented by #3449 will be the Linux `open_authorized_raw_source(...)` context manager, which yields the already-open stream and fails closed when `openat2` is unavailable. Separately approved private integrations may later add directory/subprocess capabilities with their own bypass tests. Registry/source paths will be caller-supplied where appropriate or resolved relative to the repository root; implementation code will not hardcode host-specific absolute paths.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/client_llm_wiki/bootstrap_contract.py` | Schema classifier, safe renderer, live PRIVATE verifier, already-open raw-source boundary, and CLI |
| Create | `tests/client_llm_wiki/test_bootstrap_contract.py` | Unit/integration TDD for schema version, operation-specific authorization, renderer, and guarded source reads |
| Modify mode/content | `scripts/enforcement/check-client-wiki-registry.sh` | Invoke the contract validator, preserve live checks, produce warnings for legacy state, and become executable |
| Create | `tests/enforcement/test_client_wiki_registry.py` | Hermetic subprocess tests using temporary registries, temporary git clones, and a stubbed `gh` executable |
| Delete | `tests/enforcement/test_client_wiki_registry.sh` | Remove the skip-based, live-state-dependent harness |
| Delete | `tests/enforcement/fixtures/client-wikis-consistent.yml` | Remove live-state fixture; pytest will generate a generic temporary equivalent |
| Delete | `tests/enforcement/fixtures/client-wikis-missing-repo-field.yml` | Remove live-state fixture; pytest will generate a generic temporary equivalent |
| Delete | `tests/enforcement/fixtures/client-wikis-fake-repo.yml` | Remove live-state fixture; pytest will generate a generic temporary equivalent |
| Delete | `tests/enforcement/fixtures/client-wikis-wrong-visibility.yml` | Remove live-state fixture; pytest will generate a generic temporary equivalent |
| Delete | `tests/enforcement/fixtures/client-wikis-missing-clone.yml` | Remove live-state fixture; pytest will generate a generic temporary equivalent |
| Delete | `tests/enforcement/fixtures/client-wikis-missing-mount.yml` | Remove live-state fixture; pytest will generate a generic temporary equivalent |
| Delete | `tests/enforcement/fixtures/client-wikis-duplicate-shortname.yml` | Remove live-state fixture; pytest will generate a generic temporary equivalent |
| Delete | `tests/enforcement/fixtures/client-wikis-firewall-violation.yml` | Remove live-state fixture; pytest will generate a generic temporary equivalent |
| Modify | `.claude/skills/coordination/client-llm-wiki-factory/SKILL.md` | Replace raw-root prerequisite and manual copy/sed flow with registry classification and renderer; initialize git after safe render; verify actual PRIVATE/unarchived state after creation and again before first push; document the later transition/read boundary; remove legacy client-specific examples |
| Modify | `templates/client-llm-wiki/.gitignore` | Remove the hidden raw-root assumption while preserving the raw/private file firewall |
| Modify | `templates/client-llm-wiki/README.md` | Replace embedded raw-root assumption with registry-backed ingestion posture |
| Modify | `templates/client-llm-wiki/DATA-CYCLE.md` | Make the first stage conditional on explicit registry authorization |
| Modify | `templates/client-llm-wiki/sources/README.md` | Allow no configured source and prohibit invented paths |
| Modify | `templates/client-llm-wiki/ledgers/README.md` | Document `source_path: null` until a source is authorized |
| Modify | `templates/client-llm-wiki/ledgers/promotion-ledger.example.yml` | Use a structural `null` source path rather than a raw-root placeholder |
| Modify | `templates/client-llm-wiki/projects/_template-project/README.md` | Keep project raw workspace empty when ingestion is disabled |
| Modify | `config/client-wikis.yml` | Bump the empty public stub to schema `0.2`, document generic state/host-authority fields, and replace the stale schema-design pointer without adding entries |
| Update | `docs/plans/README.md` | Track this plan and its live gate status |
| Create/update | `docs/reports/2026-07-10-issue-3449-metadata-only-bootstrap-plan.html` | Human-readable plan/review companion |

No private registry row, client wiki repository, client content, raw-source directory, or downstream/client-specific ingestion implementation will change in this issue. The new guarded-open boundary itself is reusable infrastructure in scope.

---

## TDD Test List

| Test name | What it will verify | Expected result |
|---|---|---|
| `test_duplicate_yaml_permission_key_is_rejected` | YAML cannot silently overwrite a permission-bearing field | duplicate key fails parse |
| `test_audit_warns_on_v01_but_operations_require_exact_string_v02` | Schema migration and type behavior are explicit | audit warns on legacy numeric `0.1`; render/read require string `"0.2"` |
| `test_missing_malformed_and_unsupported_registry_versions_fail` | Unknown schema cannot acquire semantics by accident | each invalid version fails audit/operations |
| `test_metadata_only_requires_exact_empty_disabled_state` | Empty roots require `not-mounted` and boolean `false` | valid tuple classifies metadata-only; string `"false"` and all mismatches fail |
| `test_nonempty_roots_require_mounted_state_when_fields_present` | Explicit source-backed states cannot claim `not-mounted` | invalid combinations fail |
| `test_roots_require_unique_normalized_absolute_paths_below_allowlisted_base` | Broad, duplicate, relative, traversal, or non-allowlisted roots cannot become authority | each invalid root/base combination fails |
| `test_present_roots_reject_symlink_or_resolved_escape` | Lexical containment cannot hide a filesystem escape | symlinked base/root and resolved escape fail |
| `test_registered_source_can_remain_disabled` | Root authorization can be staged before ingest enablement | classifies source-backed-disabled |
| `test_render_rejects_source_backed_enabled_state` | Bootstrap cannot silently activate ingestion when status later changes | enabled planned row fails render |
| `test_enabled_state_requires_commit_bound_reader_integration_mapping` | A boolean or vague attestation cannot bypass private consumer integration | missing/malformed/unverified/wrong-lifecycle fields fail |
| `test_legacy_source_backed_warns_but_does_not_authorize_ingestion` | Backward compatibility does not become permission | validation warning; ingestion denied |
| `test_render_requires_planned_private_v02_explicit_state` | Compatibility parsing is not bootstrap authorization | legacy, retired/live, non-private, and schema `0.1` renders fail |
| `test_open_source_rejects_missing_registry_stub_and_missing_entry` | Absent authority fails closed | exception before open for each case |
| `test_open_source_requires_enabled_integrated_bootstrapped_or_live_private_entry` | Lifecycle, declaration, boolean, and private integration attestation are load-bearing | planned/retired/public/non-private/disabled/unverified rows fail |
| `test_open_source_requires_live_private_unarchived_repo` | Registry declaration cannot substitute for live posture | fake lookup public/archived/error fails |
| `test_open_source_requires_matching_repo_commit_and_reader_manifest_hash` | Private integration evidence is bound to executable checkout state | wrong HEAD, missing manifest, or hash drift fails |
| `test_open_source_yields_exact_opened_contained_regular_file` | Authorization is bound to the requested read | contained regular file stream succeeds |
| `test_open_source_rejects_escape_symlink_special_file_and_root_swap` | Containment and opened-descriptor verification prevent substitution/TOCTOU | each attack fails before bytes return |
| `test_open_source_intermediate_symlink_and_fifo_fail_without_hang` | Final-component checks are not the only defense | openat2 rejects traversal; FIFO test returns within timeout |
| `test_render_metadata_only_preserves_dotfile_firewall` | `.gitignore` and `.claude/CLAUDE.md` survive render | files exist in destination |
| `test_render_copies_only_git_snapshot_and_rejects_special_members` | Renderer cannot traverse or copy from raw roots | committed symlink/FIFO/socket members and synthetic device-mode classification fail |
| `test_render_uses_internal_canonical_template_only` | Caller cannot substitute a raw directory as template source | public API exposes no template-root input; synthetic raw tree is untouched |
| `test_render_ignores_dirty_and_untracked_template_files` | “Committed template” means the pinned Git object, not working-tree state | output matches pinned SHA; dirty/private sentinel absent |
| `test_render_rejects_existing_or_symlinked_destination` | Existing content cannot be overwritten | unsafe destination fails |
| `test_render_derives_expected_destination_and_rejects_protected_overlap` | Caller cannot render into raw/template/workspace trees | expected basename under configured clone base only; overlap fails |
| `test_render_atomic_noreplace_handles_destination_race` | Renderer never overwrites a concurrently created destination or leaves partial installed output | race loses safely; destination sentinel unchanged |
| `test_render_metadata_and_source_backed_are_path_neutral` | Both modes omit configured roots rather than only the empty-root case | zero raw-root tokens and zero configured-root strings |
| `test_render_resolves_client_placeholders_but_preserves_project_placeholder` | Client bootstrap and later project instantiation stay separate | zero CLIENT/raw-state tokens; PROJECT token remains |
| `test_example_ledger_allows_null_source_path_structurally` | Path-neutral example remains compatible with validator | `validate_structure()` passes |
| `test_render_leaves_raw_sentinel_path_inode_and_hash_unchanged` | No raw source is created, moved, copied, renamed, deleted, or modified | sentinel and output inventory remain unchanged/bounded |
| `test_checker_is_directly_executable` | Operator command matches tracked mode | direct subprocess starts checker |
| `test_checker_public_stub_and_planned_metadata_need_no_gh_binary` | Lazy dependency loading preserves offline audit/bootstrap planning | exit 0 without `gh` on PATH |
| `test_checker_bootstrapped_metadata_uses_fake_gh` | Live rows still enforce actual PRIVATE/unarchived posture | fake call observed; wrong posture fails |
| `test_checker_rejects_invalid_state_matrix` | Checker consumes Python contract | non-zero with generic diagnostic |
| `test_checker_v01_legacy_row_warns_without_live_network_dependency` | Migration warning is deterministic | exit 0 plus warning |
| `test_checker_live_checks_use_stubbed_gh_and_temp_clone` | GitHub/clone checks no longer depend on live client state | deterministic pass/fail fixtures |
| `test_checker_root_availability_is_host_aware` | Missing mount parent warns, but a missing child under an available parent fails | specified exit/status for both cases |
| `test_checker_preserves_private_visibility_and_firewall_failures` | Existing privacy gates remain enforced | non-zero for public visibility or forbidden overlap |
| `test_factory_verifies_private_repo_before_render_and_before_push` | PRIVATE state is checked before content leaves the machine | skill command-order assertion passes |
| `test_public_stub_audit_skips_but_source_open_fails` | Audit availability and authorization semantics cannot be confused | checker 0 with info; guarded read raises |

Tests will use generated generic identifiers and temporary paths only. They will not contact a real repository or inspect a client checkout. A synthetic raw sentinel will prove the renderer and denied read paths leave its path, inode, and hash unchanged.

---

## Implementation Sequence (after user approval only)

1. **Contract RED:** tests for duplicate-key rejection, schema `0.2`, operation-specific state/lifecycle/privacy rules, exact-source containment, and the already-open read boundary will be written and run against the missing module; the expected failures will be captured.
2. **Contract GREEN:** the smallest classifier, root/base validator, Linux no-replace renderer, live-posture adapter, and guarded-open implementation will make those tests pass; functions will remain below 50 lines and the file below 400 lines.
3. **Checker RED/GREEN:** the Python checker harness will replace the legacy shell harness, first proving current mode/live-state failures, then driving checker integration and executable mode.
4. **Renderer RED/GREEN:** Git-object snapshot, dirty/untracked exclusion, special-member, sentinel, destination-disjointness, atomic race, and placeholder-scope tests will be added before the template/factory edits; the renderer will then replace manual raw-root substitution and render into a derived, previously absent destination before git initialization.
5. **Factory and schema documentation:** generic operator commands, migration state table, public stub guidance, and the HTML companion will be updated without adding any real identity/path.
6. **Candidate commit/push:** after RED→GREEN unit tests, template/factory edits, legal/security scans, and non-HEAD-dependent checks pass, the implementation will receive a pathspec-scoped candidate commit and feature-branch push. This is a testable review snapshot, not completion or closeout.
7. **Pinned-HEAD verification:** the real renderer will archive the candidate commit's template, and focused/full tests, placeholder/path scans, shell checks, and `git diff --check` will run against that exact pushed SHA. Any failure will receive a new fix commit and push.
8. **Artifact review:** Claude, Codex, and Gemini will adversarially review the pushed implementation diff. Any MAJOR finding will block completion and trigger a focused fix commit plus re-review.
9. **Issue closeout:** only after green pinned-HEAD verification and no-MAJOR artifact review will the implementation receive its issue summary comment, completeness evidence, final state reconciliation, and closeout.

Implementation commits will use conventional messages and pathspec-scoped commits. Parallel agents may perform read-only review, but writes to the coupled contract files will be serialized in one worktree.

---

## Acceptance Criteria

- [ ] `uv run pytest tests/client_llm_wiki/test_bootstrap_contract.py tests/client_llm_wiki/test_promotion_ledger.py tests/enforcement/test_client_wiki_registry.py -q` passes after the sparse worktree materializes `scripts/client_llm_wiki/` and `tests/client_llm_wiki/`.
- [ ] Related client-wiki and enforcement tests pass without contacting a real client repository or relying on a pre-existing clone.
- [ ] `scripts/enforcement/check-client-wiki-registry.sh` is tracked as mode `100755`; direct invocation against the public relocation stub exits `0` with an explicit informational skip even when `gh` is unavailable.
- [ ] General audit warns on schema `0.1`; `render` and guarded source reads reject schema `0.1`, legacy omission, and every inconsistent state combination.
- [ ] The factory verifies actual PRIVATE/unarchived repository state immediately after creation and again before the first push.
- [ ] Schema/checker validation rejects `ingestion_enabled: true` outside `bootstrapped`/`live` or without exact `raw_reader_integration` contract version, verified status, 40-hex covered repo commit, 64-hex reader-manifest SHA-256, and a matching private repository evidence URL.
- [ ] `open_authorized_raw_source(...)` is the reusable file-read authorization surface; no check-only CLI exists. It rejects metadata-only, disabled, unverified-integration, planned, retired, legacy, missing-registry, relocated-stub, absent-entry, non-private, public/archived live repo, unavailable/broad/duplicate/non-allowlisted root, path-escape, symlink, and non-regular-file cases before returning bytes.
- [ ] The guarded read succeeds only for schema `0.2`, verified `raw_reader_integration` whose covered commit and fixed manifest hash match the local wiki checkout, `bootstrapped`/`live`, `client-private`, declared and actual PRIVATE/unarchived state, explicit `mounted` + `ingestion_enabled: true`, normalized unique roots strictly below a registry-owned allowlisted base, and an exact regular file contained by an available authorized root.
- [ ] Metadata-only and source-backed-disabled rendering succeed under schema `0.2`; a source-backed-enabled planned row is rejected so a later status flip cannot silently activate ingestion.
- [ ] Metadata-only rendering succeeds without a raw bucket, preserves `.gitignore` and `.claude/CLAUDE.md`, and leaves no unresolved client/raw-state placeholder.
- [ ] Rendered metadata-only and source-backed-disabled output contain no raw-root path; the renderer exposes no caller-supplied template or destination path, derives the expected checkout under a registry-owned clone base, rejects protected-tree overlap, reads only from a pinned Git-object snapshot, rejects special members, validates staging before installation, uses atomic no-replace installation, and preserves the later `<PROJECT_SHORT_NAME>` placeholder.
- [ ] No code path creates, moves, copies, deletes, or renames a raw-source directory or file.
- [ ] Private repository creation remains explicit (`--private`) and both privacy-firewall dotfiles remain abort gates before commit.
- [ ] The public registry stub documents the generic fields but remains empty; no private registry entry or client repository is changed.
- [ ] `rg --hidden -n '<CLIENT_RAW_ROOT>' templates/client-llm-wiki .claude/skills/coordination/client-llm-wiki-factory` returns no matches.
- [ ] New/changed reusable artifacts contain no client identifier, real raw path, email address, credential, or private document metadata.
- [ ] `bash scripts/enforcement/check-no-abs-paths.sh` passes for the new/changed implementation files.
- [ ] `bash -n scripts/enforcement/check-client-wiki-registry.sh` and `shellcheck scripts/enforcement/check-client-wiki-registry.sh` pass using the installed shellcheck 0.11.0/yq 4.53.2 toolchain.
- [ ] `bash scripts/legal/legal-sanity-scan.sh --diff-only` passes with a non-empty deny list.
- [ ] `git diff --check` passes.
- [ ] Plan-stage and code/artifact-stage adversarial review artifacts exist; no MAJOR finding remains unresolved.
- [ ] The issue receives an implementation summary comment with test, legal/security, review, commit, and rollback evidence before closure.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | Pending initial adversarial review |
| Codex | PENDING | Pending initial adversarial review |
| Gemini | PENDING | Pending initial adversarial review |

**Overall result:** PENDING

Revisions made based on review:

- None yet.

---

## Risks and Open Questions

- **Risk — audit/authorization confusion:** the public registry checker intentionally degrades when private state is unavailable. Bootstrap rendering and source opening will instead require schema `0.2` plus operation-specific authorization, and tests will pin the distinction.
- **Risk — legacy omission becomes implicit permission:** seven source-backed rows currently omit the new fields. The checker will warn for compatibility, while the ingestion guard will deny until a private, separately approved migration makes intent explicit.
- **Risk — partial consumer coverage:** two of eight registered client-wiki repos are checked out on this host; one contains eight actual raw-access surfaces, including independently callable extractors and a directory scanner that an exact-file context manager cannot cover. This public issue will not modify or describe those private consumers. Arbitrary shell/filesystem reads also cannot be blocked by workspace-hub code. Schema `0.2` will therefore reject every enabled transition without verified private integration evidence. Metadata-only bootstrap remains independent because it performs no raw read.
- **Risk — duplicated state fields drift:** the classifier will accept only the state matrix above; every other combination will fail before rendering or ingest authorization.
- **Risk — schema migration blocks downstream bootstrap:** the live private registry remains `0.1`. This public reusable issue will not edit a private row; the downstream private/client-scoped plan must migrate the registry header to `0.2` before invoking `render` or opening a source.
- **Risk — template traversal or overwrite:** the renderer will validate allowlisted identifiers, derive a destination disjoint from protected trees, read only a pinned Git archive, reject unsafe archive members, stage and validate first, install with Linux atomic no-replace semantics, use literal replacement rather than shell evaluation, and return a bounded manifest plus source commit.
- **Risk — checker harness appears green while skipped:** the old harness and fixtures will be removed; pytest will assert subprocess exit codes and stub-call behavior directly.
- **Risk — a client-specific transition leaks into this public issue:** the later transition will be documented generically here but executed only under a separate approved private/client-scoped issue.
- **Rollback:** reverting the workspace-hub implementation commit will restore the prior factory/checker/templates. Disabling a live registry row will change only `ingestion_enabled` to `false`; rollback will never move or delete raw data.
- **Open question for approval:** none. The state names already exist in live registry usage; schema `0.2` will freeze their raw-only semantics without changing a private row in this public issue.

---

## Complexity: T3

**T3** — the work remains in one public repository, but it defines a permission-bearing schema, Linux descriptor-level read boundary, Git-object renderer, cross-repo migration contract, privacy gates, and deterministic adversarial fixtures. Partial private-consumer coverage and the security consequences of a false allow require three-provider plan and code review.
