# Plan for [#3424](https://github.com/vamseeachanta/workspace-hub/issues/3424): Add transactional metadata-only folder-note publication workflow

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-07-09
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3424
> **Client:** N/A
> **Lane:** lane:codex
> **Review artifacts:** `scripts/review/results/2026-07-09-plan-3424-claude.md` | `scripts/review/results/2026-07-09-plan-3424-codex.md` | `scripts/review/results/2026-07-09-plan-3424-gemini.md`

---

## Resource Intelligence Summary

### Existing repo code

- `.claude/skills/workspace-hub/learned/metadata-only-wiki-sweep-workflow/SKILL.md` currently defines a lightweight parent-centric document-stub workflow. It permits PDF header reads and does not define exact folder cardinality, resume, immutable snapshot/ledger, transactional publication, or verified Git candidate installation.
- `.claude/skills/workspace-hub/learned/metadata-only-inventory-sweep/SKILL.md` currently defines a 13-line legacy YAML/stub workflow with triplet markers. Its scope overlaps the lightweight sweep and does not fit deterministic private folder catalogs.
- `.claude/skills/workspace-hub/external-drive-ingest-planning/SKILL.md` currently governs read-only mounts, manifests, checksums, rsync, and dedupe for copy/migration work. It lacks a catalog-only route and can steer a note-generation request toward unnecessary file-transfer semantics.
- `.claude/skills/development/artifact-commit-verification/SKILL.md`, `.claude/skills/coordination/legal-sanity-scan/SKILL.md`, `.claude/skills/research/llm-wiki-public-private-routing/SKILL.md`, and `.claude/skills/coordination/pre-completion-cleanup-audit/SKILL.md` provide reusable adjacent gates. The new skill will invoke or link them instead of duplicating their general contracts.
- `scripts/ai/build_skill_index.py`, `scripts/skills/validate_skills_frontmatter.py`, `scripts/skills/validate-skills.sh`, and `scripts/enforcement/check-skill-index-coherence.py` provide the existing generation and validation surface for canonical skills.
- The llm-wiki-acma implementation for [#216](https://github.com/vamseeachanta/llm-wiki-acma/issues/216) contains a proven transaction across `scripts/archive_drive_j_notes.py` and `scripts/archive_notes/{inventory,hashing,joins,ledger,validation,workflow,publish,git_verify,git_candidate}.py`. Its CLI description, identifiers, output taxonomy, and joins remain Drive-J-specific, so this issue will promote the procedure rather than claim that implementation is already generic.

### Standards

| Standard | Status | Source |
|---|---|---|
| Engineering calculation standards | Not applicable | This issue will change agent workflow documentation and validation only; it will not emit calculations or standards-derived constants. |
| Skill authoring contract | Applicable | System `skill-creator/SKILL.md`: new skills will be initialized with `init_skill.py`, will use only `name` and `description` in `SKILL.md` frontmatter, will include generated `agents/openai.yaml`, and will pass `quick_validate.py`. |
| Workspace control-plane contract | Applicable | `docs/standards/CONTROL_PLANE_CONTRACT.md`: `.claude/skills/` is the workspace's canonical extended agent configuration surface. |

### LLM Wiki pages consulted

- No existing wiki page defines this workflow. This issue will create a durable workspace skill, not domain wiki content.
- llm-wiki-acma [#216](https://github.com/vamseeachanta/llm-wiki-acma/issues/216) supplies the completed archive-folder-note evidence; [#208](https://github.com/vamseeachanta/llm-wiki-acma/issues/208) remains the parent source-index lane; and [#214](https://github.com/vamseeachanta/llm-wiki-acma/issues/214) remains the distinct CAD/model lane.

### Documents consulted

- `docs/plans/_template-issue-plan.md` and `docs/plans/README.md` define the required issue-plan, review, approval, and TDD gates.
- `docs/document-intelligence/README.md` routes durable workflow knowledge to the operating-model and boundary contracts.
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` classifies reusable normative process knowledge as durable L3 and issue plans/reviews as execution-bound L5. The reusable procedure will therefore live in the canonical skill, while this plan and its reviews will remain evidence of the issue lifecycle.
- `docs/plans/2026-04-17-issue-2320-skill-usage-audit.md` demonstrates T2 skill/harness planning with explicit tests, deterministic generated state, and multi-provider adversarial review.
- llm-wiki-acma `docs/plans/2026-07-09-issue-216-archive-drive-j-folder-notes.md` defines exact source, note, join, ledger, resume, transaction, Git verification, and recovery contracts that the new reference will distill.
- llm-wiki-acma `scripts/review/results/2026-07-07-code-209-codex-r1.md` through `...-r4.md` show recurring scanner defects around caller-independent private residency, access-loss semantics, resume completeness, and Windows reparse handling.
- llm-wiki-acma `scripts/review/results/2026-07-09-plan-216-*` and `scripts/review/results/2026-07-09-code-216-*` show recurring publication defects around canonical typed hashes, immutable ledgers, journal ownership, staged-blob TOCTOU, path containment, branch races, and candidate-tree verification.
- A live metadata-only source probe will inform the skill's two forward-test profiles: Drive P exposes 870 top-level directories, while Models exposes 10 top-level directories and 426 immediate child directories. The former will require top-folder-complete notes; the latter will require adaptive two-level engineering/model coverage. No source body will be opened by this issue.
- `scripts/data/drive-index-search/search.py` returns no relevant indexed result for `metadata-only folder notes archive catalog`; a `Models CAD GHS AQWA` query returns one low-score literature-directory hit that does not define this workflow. Five registered indexes are unreachable on this machine, and two registry entries are stale, so the plan will rely on the live metadata probe and repo-local issue evidence rather than treating the drive index as complete.

### Gaps identified

- No canonical skill owns deterministic private folder-catalog publication from source inventory through verified commit installation.
- No current skill states that loss of access is an observed blocked state rather than evidence of deletion.
- No current skill binds every path-bearing checkpoint, stage, journal, snapshot, ledger, and candidate surface to caller-independent private residency checks.
- No current skill defines configurable depth and join profiles that distinguish a proposal/archive folder corpus from an engineering/model asset corpus.
- No current routing contract separates catalog-only external-folder work from copy/move/rsync ingest.
- No focused regression test prevents these trigger, privacy, transaction, and routing contracts from drifting.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-10T03:20:42Z via `gh issue view`):

- [workspace-hub #3424](https://github.com/vamseeachanta/workspace-hub/issues/3424) — OPEN — `[skills] Add transactional metadata-only folder-note publication workflow`
- [workspace-hub #1547](https://github.com/vamseeachanta/workspace-hub/issues/1547) — CLOSED — skills ecosystem umbrella; it does not supply this workflow
- [workspace-hub #1782](https://github.com/vamseeachanta/workspace-hub/issues/1782) — OPEN — zero-loss learning epic; it is broader than this bounded implementation
- [llm-wiki-acma #208](https://github.com/vamseeachanta/llm-wiki-acma/issues/208) — OPEN — living source/target index parent
- [llm-wiki-acma #209](https://github.com/vamseeachanta/llm-wiki-acma/issues/209) — CLOSED — read-only source manifest evidence
- [llm-wiki-acma #214](https://github.com/vamseeachanta/llm-wiki-acma/issues/214) — OPEN — CAD drawing/model inventory lane
- [llm-wiki-acma #216](https://github.com/vamseeachanta/llm-wiki-acma/issues/216) — CLOSED — Drive J metadata-only folder-note implementation

**File existence** (verified 2026-07-10T03:20:42Z):

- EXISTS: `.claude/skills/workspace-hub/learned/metadata-only-wiki-sweep-workflow/SKILL.md`
- EXISTS: `.claude/skills/workspace-hub/learned/metadata-only-inventory-sweep/SKILL.md`
- EXISTS: `.claude/skills/workspace-hub/external-drive-ingest-planning/SKILL.md`
- EXISTS in llm-wiki-acma: `scripts/archive_drive_j_notes.py`, `scripts/archive_notes/git_candidate.py`, and `docs/plans/2026-07-09-issue-216-archive-drive-j-folder-notes.md`
- MISSING (this plan will create): `.claude/skills/workspace-hub/transactional-metadata-only-folder-notes/SKILL.md`
- MISSING (this plan will create): `tests/skills/test_transactional_metadata_only_folder_notes.py`

**Live metadata-only source evidence** (verified 2026-07-09 local time):

```text
Drive P: 873 root entries = 870 directories + 3 files; 0 reparse points/errors.
Immediate children: 5,190 files + 1,087 directories; 56 empty top folders.
Recommended coverage: 870 top-folder notes; child indexes only for 2 directory-heavy containers.

Models: 13 root entries = 10 directories + 3 files; 0 reparse points/errors.
Immediate children: 306 files + 426 directories; no empty top folders.
Recommended coverage: 10 container notes plus adaptive child-directory notes/indexes; no per-file notes.
```

**Gap proof**:

```text
MISSING .claude/skills/workspace-hub/transactional-metadata-only-folder-notes/SKILL.md
MISSING tests/skills/test_transactional_metadata_only_folder_notes.py
```

**Reproduction proof:** N/A — this is a skill consolidation and workflow-governance issue, not an alleged runtime regression. The implementation phase will begin with red content-contract and routing tests.

Distinct source count: 12 (issue body, six workspace/llm-wiki issues, three existing skills, #209/#216 plans and reviews, live metadata probe, control-plane/boundary docs, and drive-index query).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-09-issue-3424-transactional-metadata-only-folder-notes.md` |
| Skill contract tests | `tests/skills/test_transactional_metadata_only_folder_notes.py` |
| New skill | `.claude/skills/workspace-hub/transactional-metadata-only-folder-notes/SKILL.md` |
| Skill UI metadata | `.claude/skills/workspace-hub/transactional-metadata-only-folder-notes/agents/openai.yaml` |
| Proven workflow reference | `.claude/skills/workspace-hub/transactional-metadata-only-folder-notes/references/llm-wiki-acma-archive-notes.md` |
| Lightweight sweep routing | `.claude/skills/workspace-hub/learned/metadata-only-wiki-sweep-workflow/SKILL.md` |
| Legacy overlap deprecation | `.claude/skills/workspace-hub/learned/metadata-only-inventory-sweep/SKILL.md` |
| External-drive routing | `.claude/skills/workspace-hub/external-drive-ingest-planning/SKILL.md` |
| Generated full skill index | `config/agents/skill-index-full.yaml` |
| Generated Codex runtime index | `config/agents/codex/AGENTS.runtime.md` |
| Forward-test evidence — archive profile | `scripts/review/results/2026-07-09-skill-3424-forward-test-archive.md` |
| Forward-test evidence — model profile | `scripts/review/results/2026-07-09-skill-3424-forward-test-models.md` |
| Plan review — Claude | `scripts/review/results/2026-07-09-plan-3424-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-07-09-plan-3424-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-07-09-plan-3424-gemini.md` |

---

## Deliverable

A canonical `transactional-metadata-only-folder-notes` skill will route and govern reusable source-in-place folder catalogs with configurable depth and join profiles, fail-closed privacy, resumable checkpoints, transactional publication, and verified Git installation, while three existing skills will route cleanly around it.

---

## Proposed Contract and Pseudocode

The skill will remain procedural and repository-neutral. The #216-specific field names, schema examples, and transaction vocabulary will live in the reference, explicitly labeled as prior art that must be parameterized before code reuse.

```text
on metadata-only external-folder catalog request:
    verify issue, reviewed plan, and user approval before destination writes
    classify request as catalog-only, lightweight document stubs, or copy/migration
    keep the source read-only; forbid source-body reads unless separately approved

    inventory the live source empirically
    record root entries, selected depth, reparse points, blocked/access-lost entries,
        empty folders, counts, bytes, extension aggregates, and coverage denominator
    choose a declared profile:
        top-folder-complete for broad project/proposal containers
        adaptive two-level for directory-heavy engineering/model containers
    keep files aggregated unless a later plan explicitly authorizes file-level notes

    derive opaque folder identity and canonical typed hashes
    normalize configured join columns only
    classify joins as unique, ambiguous, or unmatched; never infer an ambiguous owner

    place checkpoints, stages, journals, snapshots, ledgers, backups, and candidates
        only in approved private roots using caller-independent resolved-path checks
    bind generator inputs, inventory, join authority, output tree, snapshot, and ledger
    resume by re-observing cached source records; treat access loss as blocked, not removed

    stage -> validate full coverage/ownership/schema/link/privacy -> prepare journal
    verify staged blobs, index modes/OIDs/tombstones, materialized tree, and candidate commit
    fence branch/HEAD/index state and install with compare-and-swap
    recover or finalize idempotently, then run legal and cleanup gates
```

The two forward tests will use abstracted scenario prompts. The archive scenario will require one note per top-level folder plus bounded child indexes; the model scenario will require adaptive two-level folder coverage, extension aggregates, and no default proposal/job join. Neither prompt nor result will serialize an absolute source path or source-derived client identifier.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `tests/skills/test_transactional_metadata_only_folder_notes.py` | Add red-first trigger, frontmatter, contract, privacy, routing, and generated-metadata tests |
| Create via `skill-creator` scaffolder | `.claude/skills/workspace-hub/transactional-metadata-only-folder-notes/SKILL.md` | Define the concise repository-neutral workflow |
| Create via `skill-creator` scaffolder | `.claude/skills/workspace-hub/transactional-metadata-only-folder-notes/agents/openai.yaml` | Provide matching display metadata and an explicit `$transactional-metadata-only-folder-notes` default prompt |
| Create | `.claude/skills/workspace-hub/transactional-metadata-only-folder-notes/references/llm-wiki-acma-archive-notes.md` | Preserve the detailed #209/#216 contracts without bloating the trigger-facing skill |
| Modify | `.claude/skills/workspace-hub/learned/metadata-only-wiki-sweep-workflow/SKILL.md` | Route exact-cardinality/resumable/transactional work to the new skill and retain lightweight document stubs |
| Modify | `.claude/skills/workspace-hub/learned/metadata-only-inventory-sweep/SKILL.md` | Deprecate the overlapping legacy workflow with an explicit two-way router |
| Modify | `.claude/skills/workspace-hub/external-drive-ingest-planning/SKILL.md` | Split catalog-only work from copy/move/rsync ingest |
| Regenerate | `config/agents/skill-index-full.yaml` | Keep the provider-neutral full index deterministic and current |
| Regenerate | `config/agents/codex/AGENTS.runtime.md` | Update the generated Codex family count and runtime skill index |
| Update | `docs/plans/README.md` | Index this issue plan |
| Create | `scripts/review/results/2026-07-09-skill-3424-forward-test-{archive,models}.md` | Retain fresh-agent routing evidence without source-private paths |

---

## TDD Test List

Implementation will write this test file first and will record the intended failures before scaffolding the skill.

| Test name | What it will verify | Expected input | Expected output |
|---|---|---|---|
| `test_skill_files_exist` | Red gate proves the approved implementation has not been pre-created, then becomes the basic scaffold guard | Required skill, reference, and UI-metadata paths | File-not-found failure before scaffolding; all paths exist afterward |
| `test_skill_frontmatter_is_minimal_and_trigger_complete` | Frontmatter contains exactly `name` and `description`; description covers metadata-only folder catalogs and catalog-only routing | New `SKILL.md` | Exact two-key mapping and required trigger phrases |
| `test_skill_forbids_unapproved_source_body_reads` | Metadata-only remains the default and later content reads require a separate approved plan | Skill body | Explicit read boundary and approval language |
| `test_skill_requires_empirical_coverage_and_access_loss_state` | Coverage denominators, empty/blocked/reparse accounting, and “access loss is not deletion” remain mandatory | Skill/reference text | Required semantic anchors present |
| `test_skill_supports_top_folder_and_adaptive_depth_profiles` | One workflow can select archive and model depth without forcing per-file notes | Skill/reference text | Both profiles and file aggregation rule present |
| `test_skill_requires_deterministic_identity_hashes_and_conservative_joins` | Opaque identity, typed hashes, configured join namespace, and unique/ambiguous/unmatched states remain explicit | Skill/reference text | Required semantic anchors present |
| `test_skill_requires_private_residency_for_every_path_surface` | Checkpoint, stage, journal, snapshot, ledger, backup, and candidate paths use caller-independent fail-closed checks | Skill/reference text | Every surface and CWD-independent validation present |
| `test_skill_requires_transactional_git_candidate_protocol` | Journal binding, staged blob/index/tree verification, modes/OIDs/tombstones, fences, CAS, recovery, and finalization remain explicit | Skill/reference text | Complete transaction anchor set present |
| `test_skill_requires_legal_privacy_and_cleanup_gates` | Existing legal, routing, artifact-verification, and cleanup skills are linked rather than replaced | Skill/reference text | Canonical adjacent skill references present |
| `test_openai_metadata_matches_skill` | UI metadata remains consistent and the default prompt explicitly invokes the skill | `agents/openai.yaml` | Correct name, 25–64 character description, `$transactional-metadata-only-folder-notes` prompt |
| `test_lightweight_sweep_routes_transactional_catalogs` | Exact-cardinality/resume/immutable/publication requests leave the lightweight stub workflow | Existing lightweight skill | New canonical skill name appears in a precise routing rule |
| `test_legacy_inventory_skill_is_deprecated_without_dead_end` | The 13-line overlapping skill routes to lightweight or transactional owners | Legacy skill | Both destination skills named; legacy workflow marked deprecated |
| `test_external_drive_skill_routes_catalog_only_requests` | “prepare notes/catalog” does not fall through to checksum/rsync/copy execution | External-drive skill | Catalog-only branch names the new skill and excludes transfer semantics |
| `test_reference_does_not_advertise_drive_j_script_as_generic` | Prior implementation remains labeled repository-specific pending an approved parameterization issue | #216 reference | Explicit non-generic warning and no copy-paste execution directive |
| `test_new_skill_contains_no_absolute_machine_paths` | The reusable artifact does not leak or normalize around a workstation path | New skill directory text files | No drive-letter, UNC, or local mount absolute path |

---

## Exact Execution and Validation Sequence

The following sequence will run only after the user applies plan approval:

1. Write `tests/skills/test_transactional_metadata_only_folder_notes.py` and run it to capture the expected red failures.
2. Initialize the skill with the system skill creator, using the repository path explicitly because this cross-provider workflow belongs in the repo-tracked control plane:

   ```bash
   python "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/init_skill.py" \
     transactional-metadata-only-folder-notes \
     --path .claude/skills/workspace-hub \
     --resources references \
     --interface display_name="Transactional Folder Notes" \
     --interface short_description="Publish verified metadata-only folder catalogs" \
     --interface 'default_prompt=Use $transactional-metadata-only-folder-notes to plan a private, metadata-only folder catalog with verified publication.'
   ```

3. Replace all scaffold placeholders, write the reference, and make the three bounded routing edits.
4. Run the focused tests until green:

   ```bash
   uv run pytest tests/skills/test_transactional_metadata_only_folder_notes.py -v
   ```

5. Validate the new skill with both the system and workspace validators:

   ```bash
   python "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
     .claude/skills/workspace-hub/transactional-metadata-only-folder-notes
   uv run python scripts/skills/validate_skills_frontmatter.py
   bash scripts/skills/validate-skills.sh
   ```

6. Regenerate deterministic indexes, then rebuild the Codex runtime artifact:

   ```bash
   uv run python scripts/ai/build_skill_index.py
   bash scripts/agents/build-soul-runtime.sh
   uv run python scripts/enforcement/check-skill-index-coherence.py
   ```

7. Run the related skill test surface and generated-artifact checks:

   ```bash
   uv run pytest tests/skills tests/enforcement/test_skill_graph_integrity.py tests/enforcement/test_check_skill_index_coherence.py -q
   git diff --check
   ```

8. Dispatch two fresh adversarial agents in parallel against abstracted archive and model prompts. Require each agent to state the selected depth, join policy, privacy boundary, transaction boundary, and downstream issue route. Record their outputs in the two forward-test artifacts.
9. Run the repository legal sanity scan, inspect the exact staged diff, and conduct T2 code/artifact adversarial review with at least two providers; the default wave will target Claude, Codex, and Gemini and will document any unavailable provider.
10. Run the mandatory pre-completion cleanup audit before issue closeout.

---

## Acceptance Criteria

- [ ] The new skill directory is created through `init_skill.py`, contains no scaffold placeholders, and passes `quick_validate.py`.
- [ ] `SKILL.md` frontmatter contains only `name` and `description`; its description carries the complete trigger boundary.
- [ ] The skill keeps source observation metadata-only by default and requires a later approved issue/plan for any source-body read.
- [ ] The skill requires empirical enumeration of every live member in the selected coverage set and records empty, blocked, access-lost, reparse, file-count, directory-count, byte-count, and extension evidence.
- [ ] The skill states that access loss is blocked evidence, not deletion, and requires full re-observation before publication.
- [ ] The skill supports both top-folder-complete and adaptive two-level profiles without emitting per-file notes by default.
- [ ] Identity, canonical typed hashing, configured join authority, and unique/ambiguous/unmatched outcomes are deterministic and fail closed.
- [ ] Every checkpoint/stage/journal/snapshot/ledger/backup/candidate path is checked against an approved private root independently of caller CWD; durable artifacts contain only logical or repo-relative paths.
- [ ] Stage, full validation, journal binding, staged-blob/index/materialized-tree/candidate verification, branch/HEAD/index fences, CAS install, recovery, finalization, and cleanup are one explicit transaction.
- [ ] The lightweight sweep, legacy inventory, and drive-ingest skills route requests without overlap or dead ends.
- [ ] The #216 reference labels the existing implementation as repository- and corpus-specific and does not instruct agents to reuse it as a generic executable.
- [ ] Focused tests pass and the intended red-first failure evidence is retained in the issue implementation comment.
- [ ] Fresh-agent forward tests select the archive profile for a broad top-folder corpus and adaptive depth with no default business-development join for an engineering/model corpus.
- [ ] `config/agents/skill-index-full.yaml` and `config/agents/codex/AGENTS.runtime.md` are regenerated deterministically; index coherence passes.
- [ ] Workspace skill tests, frontmatter validation, Git diff checks, legal sanity scan, and T2 adversarial code/artifact review pass.
- [ ] The implementation issue receives a summary comment with sources consumed and promotion candidates before close.
- [ ] No Drive P or Models wiki notes, source copies, or source-body reads occur under this issue.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | Adversarial review will run after the draft is committed locally. |
| Codex | PENDING | Adversarial review will run after the draft is committed locally. |
| Gemini | PENDING | Adversarial review will run after the draft is committed locally. |

**Overall result:** PENDING

Revisions made based on review:

- Pending review.

---

## Risks and Locked Decisions

- **Locked — canonical location:** The skill will live under `.claude/skills/workspace-hub/` because the workspace contract makes the repo-tracked control plane authoritative and the user wants reuse across future sessions/providers. It will not be stranded in a machine-local personal skill directory.
- **Locked — one new skill:** The change will create one focused skill and three small routers. It will not expand two overlapping legacy skills into competing owners.
- **Locked — procedure before parameterization:** This issue will distill the proven workflow but will not generalize or copy the Drive-J-specific generator. The current generator source set is part of the committed Drive J generator hash and ownership/ledger evidence; editing it would invalidate candidate verification unless Drive J were deliberately migrated and republished. Downstream work will therefore use a separately hashed/configured implementation or a separately approved Drive J migration plan.
- **Risk — prose-only drift:** Content-contract tests and generated-index checks will make the fragile requirements executable enough to catch omission without treating exact paragraph wording as an API.
- **Risk — security backdoor by example:** The reference will use logical placeholders and narrow forensic sentinels. It will not embed absolute machine paths, client identifiers, secrets, or blanket file exemptions that would weaken its own scanners.
- **Risk — fresh-agent false confidence:** Forward-test prompts will require explicit decisions and defect hunting; an unreasoned “looks good” result will not count as evidence.
- **Downstream sequencing:** Drive P will receive a child issue under llm-wiki-acma #208 only after this skill is finished. Models will revise and continue existing llm-wiki-acma #214 rather than create a duplicate issue.

---

## Complexity: T2

**T2** — one new canonical skill with a focused reference and generated UI metadata, three bounded routing edits, one regression-test module, two generated indexes, and two fresh-agent forward tests. It spans multiple files and a security-sensitive workflow but introduces no runtime data pipeline or source write.
