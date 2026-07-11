# Plan for #3449: Client-wiki metadata-only bootstrap

> **Status:** draft-needs-r2-review
> **Complexity:** T3
> **Date:** 2026-07-10
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3449
> **Client:** N/A
> **Project:** N/A
> **Lane:** lane:codex
> **Review artifacts:** `scripts/review/results/2026-07-10-plan-3449-{claude,codex,gemini}-r1.md` | r2 pending

---

## Resource Intelligence Summary

### Existing repo code

- `.claude/skills/coordination/client-llm-wiki-factory/SKILL.md` defines the one-time private-repository bootstrap. Its prerequisites and preflight require a populated raw root; its manual substitution later embeds that root into the scaffold.
- `scripts/enforcement/check-client-wiki-registry.sh` validates registry shape plus selected GitHub, clone, and firewall facts. It accepts `raw_roots` as a sequence but has no empty-root semantics or ingestion-state validation.
- `tests/enforcement/test_client_wiki_registry.sh` requires the checker to be executable, while the tracked checker mode is `100644`. The suite therefore reports eight skips as failures. When invoked through `bash`, nominal fixtures depend on live GitHub/clone state.
- `scripts/client_llm_wiki/promotion_ledger.py::validate_structure()` permits placeholder nulls in the example ledger, while full semantic validation rejects a real entry without `source_path`. A path-neutral scaffold can retain a clearly labeled structural example without weakening active-ledger validation.
- Seven template files contain `<CLIENT_RAW_ROOT>`, including the hidden `templates/client-llm-wiki/.gitignore`. The template already contains the privacy-firewall dotfiles that every render must preserve.
- Aggregate-only inspection of the private registry on live `main` shows eight entries: one explicit empty-root/disabled entry and seven legacy source-backed entries without the new state fields.
- Host-local coverage is partial: two of eight registered client-wiki checkouts are present. One inspected checkout contains eight actual raw-access surfaces (one dispatcher, six direct extractors, and one directory scanner); five other matches across the two checkouts consume generated/committed inputs. Six registered wikis are unavailable locally.

### Standards

Not applicable. This issue changes reusable repository-bootstrap governance and contains no standards-derived calculations or constants.

### LLM Wiki pages consulted

No wiki content is in scope. This work will change reusable factory infrastructure in `workspace-hub`, not client or generic wiki content.

### Documents consulted

- [Issue #3449](https://github.com/vamseeachanta/workspace-hub/issues/3449) — requires explicit empty roots, disabled ingestion, no invented/copied raw data, a later root-authorization transition, and fail-closed raw ingestion.
- `docs/plans/README.md` and `docs/plans/_template-issue-plan.md` — require resource intelligence, reproduction evidence, adversarial review, and a user-approval hard stop.
- The historical client-wiki foundation design under `docs/governance/` — establishes one reusable template, private-registry authority, PRIVATE repository creation, and dotfile privacy firewall. It remains historical schema context; schema `0.2` will be documented by current code, factory, and public stub.
- `config/client-wikis.yml` — is an empty public relocation stub. Tooling must accept a provisioned private/local registry and must not infer client state from the stub.
- `docs/standards/PARALLEL_FIRST_EXECUTION.md` — supports parallel read-only discovery/review and serialized writes to this coupled contract.
- Drive-index query `client wiki bootstrap metadata-only factory` returned no relevant files. Three indexes were stale, but the issue is fully specified by live code/registry evidence; no mount-drive document path will enter this public plan or implementation.

### Gaps identified

- No machine-readable metadata-only bootstrap state exists.
- No deterministic renderer can create a path-neutral scaffold from the committed template while preserving dotfiles and refusing protected-tree overlap.
- The general registry checker can skip when only the public stub is present, but no separate operation contract prevents that availability behavior from being mistaken for bootstrap authorization.
- Existing source-backed rows require a compatibility posture without implicit permission.
- Current checker tests are non-hermetic and the documented direct checker invocation does not match its tracked file mode.
- Ecosystem-wide raw-reader enforcement is not supportable from the observed 25% checkout coverage. Schema `0.2` must therefore reject every enabled-ingestion state rather than claim that private readers are guarded.

### Evidence (embedded verification)

**Issue status** (verified 2026-07-11T01:11:10Z):

- `#3449` — OPEN — labels `enhancement`, `status:needs-plan`; no comments.

**File/mode evidence** (verified against an ancestor of current `origin/main`):

```text
EXISTS  .claude/skills/coordination/client-llm-wiki-factory/SKILL.md
EXISTS  scripts/enforcement/check-client-wiki-registry.sh
EXISTS  tests/enforcement/test_client_wiki_registry.sh
EXISTS  templates/client-llm-wiki/
MISSING scripts/client_llm_wiki/bootstrap_schema.py
MISSING scripts/client_llm_wiki/bootstrap_renderer.py
MISSING scripts/client_llm_wiki/bootstrap_contract.py

git ls-files -s scripts/enforcement/check-client-wiki-registry.sh
100644 ... scripts/enforcement/check-client-wiki-registry.sh
```

**Raw-root assumption proof:**

```text
rg --hidden -l '<CLIENT_RAW_ROOT>' \
  .claude/skills/coordination/client-llm-wiki-factory \
  templates/client-llm-wiki
→ factory skill plus seven template files

rg -n 'raw_source_status|ingestion_enabled' \
  scripts/enforcement/check-client-wiki-registry.sh
→ no matches
```

**Checker reproduction** (2026-07-11T01:11:10Z):

```text
$ bash tests/enforcement/test_client_wiki_registry.sh
=== client-wiki-registry checker test suite ===
  test_01_consistent_registry_passes... SKIP (no checker yet — TDD RED expected)
  ... six equivalent skips omitted ...
  test_08_firewall_guard_fails... SKIP (no checker yet — TDD RED expected)
=== Total: 0 pass / 8 fail ===
exit 8
```

Direct `bash` invocation against two nominal legacy fixtures exits `1` because they query live GitHub/clone state. Identifiers and host paths are intentionally omitted; the mechanism is visible in `tests/enforcement/test_client_wiki_registry.sh:25-63`.

The issue's core claim reproduces: the factory requires a raw variable and checks its mount before repository creation; `<CLIENT_RAW_ROOT>` substitution occurs later, after repository creation and before the first push.

**Consumer-coverage evidence (privacy-safe aggregate):**

```text
registered wikis: 8
checked out on this host: 2 (25%)
actual raw-access surfaces found: 8 in one checkout
generated/committed-only matches: 5 across both checkouts
unexamined registered wikis: 6
```

Distinct sources: issue body; factory skill; registry checker; checker tests/fixtures; template tree; promotion-ledger validator; public/private registry shape; historical design/index; drive index; aggregate checkout audit.

---

## Artifact Map

| Artifact | Path |
|---|---|
| Canonical plan | `docs/plans/2026-07-10-issue-3449-client-wiki-metadata-only-bootstrap.md` |
| Human review companion | `docs/reports/2026-07-10-issue-3449-metadata-only-bootstrap-plan.html` |
| Schema/state contract | `scripts/client_llm_wiki/bootstrap_schema.py` |
| Git-snapshot renderer | `scripts/client_llm_wiki/bootstrap_renderer.py` |
| CLI/orchestration | `scripts/client_llm_wiki/bootstrap_contract.py` |
| Contract tests | `tests/client_llm_wiki/test_bootstrap_{schema,renderer,contract}.py` |
| Registry checker/tests | `scripts/enforcement/check-client-wiki-registry.sh` / `tests/enforcement/test_client_wiki_registry.py` |
| Factory contract | `.claude/skills/coordination/client-llm-wiki-factory/SKILL.md` |
| Public schema guidance | `config/client-wikis.yml` |
| Path-neutral scaffold | `templates/client-llm-wiki/` |
| Plan reviews | `scripts/review/results/2026-07-10-plan-3449-*.md` |

---

## Deliverable

A tested schema-`0.2` metadata-only bootstrap will create a verified PRIVATE, path-neutral client-wiki scaffold without any raw bucket, while every `ingestion_enabled: true` registry state will fail validation until a separately approved private reader-integration contract exists.

---

## Locked Contract and State Transitions

The private/local registry remains authoritative. Schema version is the exact YAML string `registry_version: "0.2"`.

`ingestion_enabled` means raw-source ingestion only; it does not prohibit owner notes, authorized public research, or metadata authoring. `raw_source_status: not-mounted` means no authorized raw root is registered; transient host availability is checked separately.

| State | `raw_roots` | `raw_source_status` | `ingestion_enabled` | Schema-`0.2` result |
|---|---|---|---|---|
| Metadata-only | `[]` | `not-mounted` | `false` | valid; new bootstrap allowed only for planned/private rows |
| Source registered, disabled | non-empty normalized strings | `mounted` | `false` | valid; new bootstrap allowed only for planned/private rows |
| Any enabled state | any | any | `true` | invalid and fail-closed |
| Legacy source-backed | non-empty | absent | absent | schema-`0.1` audit warning only; render denied |
| Any other combination | any | any | any | invalid |

The later transition will be explicit:

1. A separately approved private/client-scoped change may migrate the provisioned registry to `"0.2"`.
2. It may change metadata-only state to source-registered-disabled by adding authorized roots and setting `raw_source_status: mounted`, while retaining `ingestion_enabled: false`.
3. The checker will validate shape, firewall posture, and host-aware root availability.
4. Enabling ingestion will remain blocked. A future private integration issue must inventory every raw-touching entrypoint, cover direct CLIs plus dispatchers/directory scanners/subprocess consumers, install a supported guard boundary, add bypass tests, and define the next schema transition before `true` can become valid.

This is the load-bearing fail-closed rule: schema `0.2` has no enabled-ingestion state. Arbitrary filesystem tools are outside repository enforcement, so no ecosystem-wide reader-completeness claim will be made.

---

## Pseudocode

```text
function load_registry(path):
    parse YAML with duplicate-key-rejecting safe loader
    if version is legacy numeric 0.1:
        return audit-only legacy result with warning
    require version is exact string "0.2"
    reject missing, malformed, unsupported, or relocated-only authority

function classify_entry(entry):
    require posture == "client-private" and visibility == "PRIVATE"
    require raw_roots is a list and ingestion_enabled is a boolean
    if ingestion_enabled is true: reject unconditionally
    if roots are empty:
        require raw_source_status == "not-mounted"
        return METADATA_ONLY
    require raw_source_status == "mounted"
    validate unique normalized roots under configured raw_root_bases
    return SOURCE_REGISTERED_DISABLED

function authorize_render(registry_path, short_name):
    registry, entry = load exact registered entry internally
    require version "0.2", status "planned", and an explicit valid disabled mode
    validate short_name/repo slug and working_clone_base
    derive destination from working_clone_base + repo basename
    reject destination overlap with raw bases/roots, template, or workspace repo
    verify live repository is PRIVATE and not archived
    return immutable render inputs

function render(registry_path, short_name):
    inputs = authorize_render(...)
    pin workspace HEAD SHA
    archive canonical template subtree from that exact Git object
    inspect archive: directories/regular blobs only; reject links/special/traversal
    extract into adjacent staging; replace allowlisted CLIENT/raw-state tokens
    preserve PROJECT_SHORT_NAME; validate firewall and final manifest
    atomically mkdir absent destination and record its device/inode
    install validated directories/files with exclusive mkdir and O_CREAT|O_EXCL
    on failure, verify owned device/inode + created manifest before cleanup
    return manifest with pinned template SHA and derived destination
```

CLI subcommands will be `validate-registry`, `classify`, `render`, and `verify-private-repo`. There will be no raw-read or check-only ingestion command in schema `0.2`.

The shell checker will first use existing `yq` logic to detect the empty public relocation stub. Only a non-empty provisioned registry will invoke:

```bash
PYTHONPATH="$REPO_ROOT/scripts" \
  uv run --frozen python -m client_llm_wiki.bootstrap_contract \
  validate-registry --registry "$REGISTRY"
```

For a non-empty registry, missing `uv`, missing module, or locked-dependency failure exits `2` (dependency error); invalid registry exits `1`; valid/audit-warning state exits `0`. `gh` remains lazy and is required only for bootstrapped/live remote checks. Render/verify operations always fail closed on missing dependencies or lookup failure.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/client_llm_wiki/bootstrap_schema.py` | Duplicate-key loader, version/state/root validation |
| Create | `scripts/client_llm_wiki/bootstrap_renderer.py` | Pinned Git-object template renderer and no-overwrite destination install |
| Create | `scripts/client_llm_wiki/bootstrap_contract.py` | Thin CLI/orchestration and live PRIVATE verifier |
| Modify | `scripts/client_llm_wiki/__init__.py` | Export the new internal modules |
| Create | `tests/client_llm_wiki/test_bootstrap_schema.py` | Schema/state RED→GREEN tests |
| Create | `tests/client_llm_wiki/test_bootstrap_renderer.py` | Snapshot/filesystem safety RED→GREEN tests |
| Create | `tests/client_llm_wiki/test_bootstrap_contract.py` | CLI/private-verification tests |
| Modify mode/content | `scripts/enforcement/check-client-wiki-registry.sh` | Lazy Python contract invocation, preserved live checks, executable mode |
| Create | `tests/enforcement/test_client_wiki_registry.py` | Hermetic subprocess tests with temp registry/clone and fake `gh` |
| Delete | `tests/enforcement/test_client_wiki_registry.sh` | Remove skip/live-state harness |
| Delete | `tests/enforcement/fixtures/client-wikis-consistent.yml`<br>`tests/enforcement/fixtures/client-wikis-missing-repo-field.yml`<br>`tests/enforcement/fixtures/client-wikis-fake-repo.yml`<br>`tests/enforcement/fixtures/client-wikis-wrong-visibility.yml`<br>`tests/enforcement/fixtures/client-wikis-missing-clone.yml`<br>`tests/enforcement/fixtures/client-wikis-missing-mount.yml`<br>`tests/enforcement/fixtures/client-wikis-duplicate-shortname.yml`<br>`tests/enforcement/fixtures/client-wikis-firewall-violation.yml` | Replace only these eight existing live-state fixtures with generated generic fixtures; no glob sweep |
| Modify | `.claude/skills/coordination/client-llm-wiki-factory/SKILL.md` | Mode-aware preflight/render flow, PRIVATE checks, disabled transition, generic examples |
| Modify | seven raw-root-bearing template files, including hidden `.gitignore` | Remove raw-path assumptions while preserving firewall and project placeholder |
| Modify | `config/client-wikis.yml` | Empty schema-`0.2` public guidance; retain historical-design link as context and point current behavior to code/factory |
| Update | `docs/plans/README.md` | Track reviewed gate |
| Create/update | `docs/reports/2026-07-10-issue-3449-metadata-only-bootstrap-plan.html` | Human review companion |

Each Python implementation file will remain below 400 lines and each function below 50 lines. No private registry row, client wiki, client content, raw-source directory, or private reader will change.

---

## TDD Test List

| Test | Verification |
|---|---|
| duplicate/missing/malformed/unsupported version tests | YAML duplicates fail; only legacy numeric `0.1` audit or exact string `"0.2"` is recognized |
| exact metadata-only tuple tests | empty roots + `not-mounted` + boolean `false` passes; type/state mismatches fail |
| source-registered-disabled tests | non-empty roots + `mounted` + boolean `false` passes after root normalization |
| enabled-state matrix test | every `ingestion_enabled: true` row exits non-zero regardless of other fields |
| legacy audit-vs-operation test | schema-`0.1` row warns in audit and cannot render |
| planned/private render authorization tests | wrong status/posture/declared visibility fail |
| live PRIVATE verifier tests | fake `gh` PRIVATE/unarchived passes; public/archived/error fails |
| destination derivation/disjointness tests | no caller destination; raw/template/workspace overlap fails |
| pinned Git snapshot tests | dirty/untracked template files never render; output records exact commit |
| archive-member tests | link, traversal, FIFO/socket, and synthetic device modes fail |
| no-overwrite/cleanup tests | existing/racing destination sentinel is unchanged; exclusive creates never overwrite; forced install failure cleans only the recorded owned tree |
| path-neutral render tests | metadata and source-registered-disabled output contain no configured root or CLIENT_RAW_ROOT token |
| placeholder-scope test | CLIENT/raw-state tokens resolve; PROJECT_SHORT_NAME remains |
| firewall/ledger tests | privacy dotfiles survive; structural example with `source_path: null` remains structure-valid |
| raw sentinel test | raw sentinel path, inode, hash, and output inventory remain unchanged |
| checker executable-mode test | Git index records `100755` and fresh-checkout direct invocation works |
| checker dependency tests | public stub skips without `uv`/`gh`; non-empty registry missing `uv`/module exits `2` |
| checker planned/live tests | planned metadata avoids `gh`; bootstrapped/live rows use fake `gh` and temp clone |
| checker firewall/visibility/root tests | existing privacy gates and host-aware root behavior remain deterministic |
| factory-order documentation test | verifies documented command order only; behavioral PRIVATE refusal is covered by renderer/CLI tests |

Generated fixtures will use generic identifiers and temporary paths. Tests will not contact a real client repository or inspect a client checkout.

---

## Implementation Sequence (after user approval only)

1. Materialize `scripts/client_llm_wiki/` and `tests/client_llm_wiki/` in the sparse worktree.
2. Write split schema/renderer/CLI and checker tests first; capture expected RED failures.
3. Implement the three bounded modules and checker integration until non-HEAD-dependent tests pass.
4. Update factory/templates/public guidance under tests; run legal/security, shell, placeholder, and diff checks.
5. Create and push a pathspec-scoped candidate commit. This is a testable snapshot, not completion.
6. Run pinned-HEAD renderer integration against that candidate commit; fix with additional commits if needed.
7. Dispatch three-provider artifact review against the pushed diff; provider unavailability will be recorded explicitly, and no available MAJOR may remain.
8. Only after green verification and no-MAJOR artifact review will the issue receive implementation summary/completeness evidence and closeout.

---

## Acceptance Criteria

- [ ] `uv run --frozen pytest tests/client_llm_wiki/test_bootstrap_schema.py tests/client_llm_wiki/test_bootstrap_renderer.py tests/client_llm_wiki/test_bootstrap_contract.py tests/client_llm_wiki/test_promotion_ledger.py tests/enforcement/test_client_wiki_registry.py -q` passes.
- [ ] Every schema-`0.2` `ingestion_enabled: true` fixture fails validation; no raw-read/check CLI exists.
- [ ] Metadata-only render succeeds without a raw bucket; source-registered-disabled render also remains path-neutral.
- [ ] Renderer verifies actual PRIVATE/unarchived state before installing files; factory reruns verifier before first push.
- [ ] Renderer reads a pinned Git-object template, ignores dirty/untracked content, rejects unsafe members/protected overlap, installs via exclusive directory/file creation without overwrite, and cleans only a device/inode/manifest-verified owned partial destination on forced failure.
- [ ] Privacy dotfiles remain mandatory; `rg --hidden -n '<CLIENT_RAW_ROOT>' templates/client-llm-wiki .claude/skills/coordination/client-llm-wiki-factory` returns no matches.
- [ ] Raw sentinel path/inode/hash remain unchanged and no sentinel payload appears in rendered output.
- [ ] Public stub remains empty and can audit-skip without `uv` or `gh`; a non-empty registry missing the Python contract exits dependency-error `2`.
- [ ] Checker is tracked `100755`; planned rows do not invoke `gh`; bootstrapped/live checks remain PRIVATE/unarchived and clone-aware.
- [ ] `bash -n` and `shellcheck` pass for the checker; `yq --version` confirms major version 4 without pinning a host point release.
- [ ] `bash scripts/enforcement/check-no-abs-paths.sh`, `bash scripts/legal/legal-sanity-scan.sh --diff-only`, and `git diff --check` pass.
- [ ] New/changed reusable artifacts contain no client identifier, real raw path, email address, credential, or private document metadata.
- [ ] Plan-stage and code-stage review artifacts exist; no available provider has an unresolved MAJOR.
- [ ] Issue receives implementation summary with tests, legal/security, reviews, commits, rollback, and preserved private-integration blocker.

---

## Adversarial Review Summary

| Round/provider | Verdict | Result |
|---|---|---|
| r1 Claude | MAJOR | FFI/read-boundary scope, one-file size contradiction, checker dependency contract, and operational accuracy gaps |
| r1 Codex CLI | UNAVAILABLE | CLI timed out after the known stdin-reading symptom; no review signal |
| r1 Gemini | UNAVAILABLE | No non-interactive authentication |
| r2 | PENDING | Revised plan removes raw-read/FFI scope, splits modules, and specifies checker dependency/failure behavior |

**Overall result:** FAIL until r2 returns no MAJOR from at least Claude plus native Codex; Gemini unavailability remains documented.

Revisions after r1:

- Raw ingestion enablement/read-boundary implementation is removed from #3449; schema `0.2` rejects all enabled states.
- One overloaded module is split into schema, renderer, and CLI files under repository size limits.
- Checker invocation, locked dependency source, lazy ordering, and exit `0/1/2` behavior are explicit.
- Factory reproduction ordering is corrected.
- PRIVATE refusal moves into behavioral renderer/CLI tests; the skill-order test is labeled documentation-only.
- HEAD-binding/re-attestation and local-enabled-clone ambiguities disappear with the removed raw-read scope.
- Exact host tool point versions are replaced by capability/major-version checks.

---

## Risks and Open Questions

- **Partial consumer coverage:** only 25% of registered wiki checkouts were inspectable and eight real raw-access surfaces were found. Schema `0.2` rejects enablement; a future private integration issue must establish complete per-repo coverage.
- **Legacy compatibility:** schema-`0.1` entries remain audit warnings only. New operations require exact `"0.2"`.
- **Public-stub ambiguity:** the checker may skip the empty public stub, but render never treats that as authority and non-empty dependency failures return `2`.
- **Renderer cleanup:** the install is not an atomic whole-tree rename. The renderer will stage/validate first, atomically create the absent destination, use exclusive child creation, record device/inode/manifest ownership, clean only its own partial on failure, and never claim atomicity.
- **Pinned template:** rendering intentionally uses committed HEAD, so template edits require the candidate-commit step before pinned integration verification.
- **Schema migration:** the private registry remains `0.1`; its separately approved migration is a downstream prerequisite, not part of this public issue.
- **Rollback:** reverting the workspace-hub implementation commit restores prior factory/checker/templates. No raw data is moved or deleted.
- **Open question for approval:** none. The conservative `true`-is-invalid rule is the recommended scope until private readers can be inventoried and guarded.

---

## Complexity: T3

**T3** — implementation is one public repository, but the permission-bearing schema, privacy gates, Git-object renderer, checker migration, and partial private-consumer coverage require three-provider plan and code review.
