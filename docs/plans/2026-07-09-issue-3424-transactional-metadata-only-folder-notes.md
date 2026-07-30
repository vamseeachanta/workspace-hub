# Plan for [#3424](https://github.com/vamseeachanta/workspace-hub/issues/3424): Add transactional metadata-only folder-note publication workflow

> **Status:** adversarial-reviewed v9 — Codex r9 APPROVE; distinct-provider review pending
> **Complexity:** T3
> **Date:** 2026-07-09
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3424
> **Client:** N/A
> **Lane:** lane:codex
> **Review artifacts:** `scripts/review/results/2026-07-09-plan-3424-codex-skill-lifecycle-r{1,2,3,4,5,6,7,8,9}.md` | `...-codex-transaction-r{1,2,3,4,5,6,7,8,9}.md` | `...-claude.md` | `...-codex.md` | `...-gemini.md` | `...-provider-availability.md`

---

## Resource Intelligence Summary

### Existing repo code

- `.claude/skills/workspace-hub/learned/metadata-only-wiki-sweep-workflow/SKILL.md` currently defines a lightweight parent-centric document-stub workflow. It permits PDF header reads and does not define exact folder cardinality, resume, immutable snapshot/ledger, transactional publication, or verified Git candidate installation.
- `.claude/skills/workspace-hub/learned/metadata-only-inventory-sweep/SKILL.md` currently defines a 13-line legacy YAML/stub workflow with triplet markers. Its scope overlaps the lightweight sweep and does not fit deterministic private folder catalogs.
- `.claude/skills/workspace-hub/external-drive-ingest-planning/SKILL.md` currently governs read-only mounts, manifests, checksums, rsync, and dedupe for copy/migration work. It lacks a catalog-only route and can steer a note-generation request toward unnecessary file-transfer semantics.
- `.claude/skills/workspace-hub/workspace-knowledge-doc-contracts/SKILL.md` currently owns broad large/sensitive-corpus pointer-page work, including source-of-record absolute paths. For strict transactional catalogs, that conflicts with #216's path-minimization contract. The implementation will add a precedence route: ordinary pointer pages will retain that skill's contract; exact-cardinality transactional catalogs will use the new skill and will keep machine paths out of tracked notes, ledgers, reviews, and issue comments.
- `.claude/skills/research/llm-wiki/SKILL.md` currently triggers broadly for source ingestion, notes, and large batch wiki work. It will retain ordinary wiki ingest/query/lint behavior and will route source-in-place exact folder catalogs to the new skill before any batch-ingest or content-read command.
- `.claude/skills/development/artifact-commit-verification/SKILL.md`, `.claude/skills/coordination/legal-sanity-scan/SKILL.md`, `.claude/skills/research/llm-wiki-public-private-routing/SKILL.md`, and `.claude/skills/coordination/pre-completion-cleanup-audit/SKILL.md` provide reusable adjacent gates. The new skill will invoke or link them instead of duplicating their general contracts.
- `scripts/ai/build_skill_index.py`, `scripts/skills/validate_skills_frontmatter.py`, `scripts/skills/validate-skills.sh`, and `scripts/enforcement/check-skill-index-coherence.py` provide the existing generation and validation surface for canonical skills.
- `scripts/workflow/plan_approval_gate_check.py` already enforces current label state, authorized human/non-bot actor, approval freshness, plan binding, revision reachability, and plan-blob equality, but it is already 397 lines against the 400-line file limit and its PR entry point intentionally skips this all-low-risk path set. The implementation will create a bounded read-only local companion that imports and composes the canonical gate's loaders/evaluators directly, verifies the frozen delivery manifest, and contains no independent reduced-authority policy. The bootstrap will use those existing canonical functions directly, so it will not depend on the POSIX-only `fcntl` import in `approve-provider-plan.py` on this Windows host.
- The live repository does not define `PLAN_APPROVAL_OWNERS` (the similarly named completeness variable is a different policy surface). The approval allowlist for this issue is therefore frozen in this reviewed plan as the single repository owner `vamseeachanta`, whose GitHub account type was verified live as `User` on 2026-07-09. The bootstrap and companion will still use the canonical actor-type and authorization functions; changing this allowlist requires plan review and user re-approval.
- `git rev-parse --git-path hooks` resolves to the common workspace-hub hooks directory, and the live directory contains only `*.sample` files; no active commit hook exists. Because the planned `commit-tree` path intentionally bypasses porcelain hooks, implementation will re-verify that precondition immediately before candidate creation and will fail for plan revision if any active `pre-commit`, `prepare-commit-msg`, `commit-msg`, or `post-commit` hook appears.
- `scripts/ai/build_skill_index.py` currently down-weights description-only skills as auto-derived backfill. A live probe finds 408 skills with richer legacy sections plus descriptions and 434 backfill entries with descriptions; a global precedence/weight flip would be an unsafe 842-entry reroute. The implementation will preserve all legacy precedence and add full-weight `when_to_use_source: description` only for modern minimal skills whose frontmatter keys are exactly `name` and `description` and which have no legacy trigger section. The live tree currently has 11 such production/test candidates; their before/after ranking fixtures will be audited explicitly. All other legacy description-only entries will retain current backfill behavior until separately migrated.
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
- A live metadata-only source probe will inform the skill's two forward-test profiles: Drive P exposes 870 top-level directories, while Models exposes 10 top-level directories and 426 immediate child directories. The former will require top-folder-complete notes; the latter will require deterministic adaptive-two-level engineering/model coverage under an explicit inclusion predicate. No source body will be opened by this issue.
- `scripts/data/drive-index-search/search.py` returns no relevant indexed result for `metadata-only folder notes archive catalog`; a `Models CAD GHS AQWA` query returns one low-score literature-directory hit that does not define this workflow. Five registered indexes are unreachable on this machine, and two registry entries are stale, so the plan will rely on the live metadata probe and repo-local issue evidence rather than treating the drive index as complete.

### Gaps identified

- No canonical skill owns deterministic private folder-catalog publication from source inventory through verified commit installation.
- No current skill states that loss of access is an observed blocked state rather than evidence of deletion.
- No current skill binds every path-bearing checkpoint, stage, journal, snapshot, ledger, and candidate surface to caller-independent private residency checks.
- No current skill defines configurable depth and join profiles that distinguish a proposal/archive folder corpus from an engineering/model asset corpus.
- No current routing contract separates catalog-only external-folder work from copy/move/rsync ingest.
- Two broad wiki skills currently overlap this proposed trigger and disagree about tracked absolute source paths; no precedence rule resolves the conflict.
- No reusable verifier binds an issue's declared delivery paths/statuses to the NUL-delimited staged ACMR/tombstone set before scans and commit.
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
- EXISTS: `.claude/skills/workspace-hub/workspace-knowledge-doc-contracts/SKILL.md`
- EXISTS: `.claude/skills/research/llm-wiki/SKILL.md`
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

**Skill-index migration probe** (verified against the live skill tree on 2026-07-09):

```text
408 active skills have both a non-empty description and a richer legacy When-to-Use/Trigger section.
434 current backfill entries have a non-empty description.
11 active skills satisfy the narrow modern-minimal candidate rule:
   exact frontmatter keys {name, description} and no legacy trigger section.
```

This evidence rejects a global 842-entry reroute and bounds implementation to the audited minimal candidate set plus the new skill. The exact 11 candidate identities, description hashes, current sources/ranks, and expected post-change top ranks are frozen in the pre-approval planning artifact `tests/ai/fixtures/description-trigger-ranking-baseline.yaml` (SHA-256 `9ba4fb7aa79d81a9eb2a96caaa4ddcdd2ed09fa1ab57f7300c1ee7c8f6ab5f54`). Implementation will fail before changing the builder if the live candidate set or any description hash differs.

**Pre-approval delivery manifest binding:** `docs/plans/manifests/issue-3424-delivery.yaml` contains 22 pre-review, 26 final, and 8 closeout exact path/status/mode entries. SHA-256: `d191a10694b62440c45482f710d4ef3c8397c1e537067f4be6d472b8e422d175`.

**Reproduction proof:** N/A — this is a skill consolidation and workflow-governance issue, not an alleged runtime regression. The implementation phase will begin with red content-contract and routing tests.

Distinct source count: 14 (issue body, six workspace/llm-wiki issues, five existing skills, #209/#216 plans and reviews, live metadata probe, control-plane/boundary docs, and drive-index query).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-09-issue-3424-transactional-metadata-only-folder-notes.md` |
| User-authored approval marker | `.planning/plan-approved/3424.md` |
| Frozen routing baseline | `tests/ai/fixtures/description-trigger-ranking-baseline.yaml` |
| Skill contract tests | `tests/skills/test_transactional_metadata_only_folder_notes.py` |
| Approval-preflight companion | `scripts/workflow/plan_approval_local_check.py` |
| Approval-preflight tests | `tests/workflow/test_plan_approval_local_check.py` |
| New skill | `.claude/skills/workspace-hub/transactional-metadata-only-folder-notes/SKILL.md` |
| Skill UI metadata | `.claude/skills/workspace-hub/transactional-metadata-only-folder-notes/agents/openai.yaml` |
| Proven workflow reference | `.claude/skills/workspace-hub/transactional-metadata-only-folder-notes/references/verified-private-catalog-prior-art.md` |
| Lightweight sweep routing | `.claude/skills/workspace-hub/learned/metadata-only-wiki-sweep-workflow/SKILL.md` |
| Legacy overlap deprecation | `.claude/skills/workspace-hub/learned/metadata-only-inventory-sweep/SKILL.md` |
| External-drive routing | `.claude/skills/workspace-hub/external-drive-ingest-planning/SKILL.md` |
| Knowledge-contract routing | `.claude/skills/workspace-hub/workspace-knowledge-doc-contracts/SKILL.md` |
| General llm-wiki routing | `.claude/skills/research/llm-wiki/SKILL.md` |
| Generated full skill index | `config/agents/skill-index-full.yaml` |
| Generated Codex runtime index | `config/agents/codex/AGENTS.runtime.md` |
| Skill-index builder | `scripts/ai/build_skill_index.py` |
| Skill-index builder tests | `tests/ai/test_build_skill_index.py` |
| Skill-router tests | `tests/ai/test_skill_router.py` |
| Description-routing baseline | `tests/ai/fixtures/description-trigger-ranking-baseline.yaml` |
| Delivery manifest | `docs/plans/manifests/issue-3424-delivery.yaml` |
| Delivery verifier | `scripts/skills/verify_issue_delivery.py` |
| Delivery verifier tests | `tests/skills/test_verify_issue_delivery.py` |
| Forward-test evidence — archive profile | `scripts/review/results/2026-07-09-skill-3424-forward-test-archive.md` |
| Forward-test evidence — model profile | `scripts/review/results/2026-07-09-skill-3424-forward-test-models.md` |
| Plan review — Claude | `scripts/review/results/2026-07-09-plan-3424-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-07-09-plan-3424-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-07-09-plan-3424-gemini.md` |
| Plan review — Codex skill-lifecycle r1 | `scripts/review/results/2026-07-09-plan-3424-codex-skill-lifecycle-r1.md` |
| Plan review — Codex privacy/transaction r1 | `scripts/review/results/2026-07-09-plan-3424-codex-transaction-r1.md` |
| Plan review — Codex skill-lifecycle r2 | `scripts/review/results/2026-07-09-plan-3424-codex-skill-lifecycle-r2.md` |
| Plan review — Codex privacy/transaction r2 | `scripts/review/results/2026-07-09-plan-3424-codex-transaction-r2.md` |
| Plan review — Codex skill-lifecycle r3 | `scripts/review/results/2026-07-09-plan-3424-codex-skill-lifecycle-r3.md` |
| Plan review — Codex privacy/transaction r3 | `scripts/review/results/2026-07-09-plan-3424-codex-transaction-r3.md` |
| Plan review — Codex skill-lifecycle r4 | `scripts/review/results/2026-07-09-plan-3424-codex-skill-lifecycle-r4.md` |
| Plan review — Codex privacy/transaction r4 | `scripts/review/results/2026-07-09-plan-3424-codex-transaction-r4.md` |
| Plan review — Codex skill-lifecycle r5 | `scripts/review/results/2026-07-09-plan-3424-codex-skill-lifecycle-r5.md` |
| Plan review — Codex privacy/transaction r5 | `scripts/review/results/2026-07-09-plan-3424-codex-transaction-r5.md` |
| Plan review — Codex skill-lifecycle r6 | `scripts/review/results/2026-07-09-plan-3424-codex-skill-lifecycle-r6.md` |
| Plan review — Codex privacy/transaction r6 | `scripts/review/results/2026-07-09-plan-3424-codex-transaction-r6.md` |
| Plan review — Codex skill-lifecycle r7 | `scripts/review/results/2026-07-09-plan-3424-codex-skill-lifecycle-r7.md` |
| Plan review — Codex privacy/transaction r7 | `scripts/review/results/2026-07-09-plan-3424-codex-transaction-r7.md` |
| Plan review — Codex skill-lifecycle r8 | `scripts/review/results/2026-07-09-plan-3424-codex-skill-lifecycle-r8.md` |
| Plan review — Codex privacy/transaction r8 | `scripts/review/results/2026-07-09-plan-3424-codex-transaction-r8.md` |
| Plan review — Codex skill-lifecycle r9 | `scripts/review/results/2026-07-09-plan-3424-codex-skill-lifecycle-r9.md` |
| Plan review — Codex privacy/transaction r9 | `scripts/review/results/2026-07-09-plan-3424-codex-transaction-r9.md` |
| Provider availability | `scripts/review/results/2026-07-09-plan-3424-provider-availability.md` |
| Code/artifact review — Claude | `scripts/review/results/2026-07-09-code-3424-claude.md` |
| Code/artifact review — Codex | `scripts/review/results/2026-07-09-code-3424-codex.md` |
| Code/artifact review — Gemini | `scripts/review/results/2026-07-09-code-3424-gemini.md` |
| Code-review provider availability | `scripts/review/results/2026-07-09-code-3424-provider-availability.md` |
| Completeness artifact review — Claude | `scripts/review/results/2026-07-09-completeness-3424-claude.md` |
| Completeness artifact review — Codex | `scripts/review/results/2026-07-09-completeness-3424-codex.md` |
| Completeness artifact review — Gemini | `scripts/review/results/2026-07-09-completeness-3424-gemini.md` |
| Completeness-review provider availability | `scripts/review/results/2026-07-09-completeness-3424-provider-availability.md` |
| Completeness inputs | `docs/reports/issue-3424-completeness-inputs.json` |
| Completeness report | `docs/reports/2026-07-09-3424-completeness.html` |
| Completeness input derivation | `scripts/workflow/completeness_inputs.py` |
| Completeness input tests | `tests/workflow/test_completeness_inputs.py` |

---

## Deliverable

A canonical `transactional-metadata-only-folder-notes` skill will route and govern reusable source-in-place folder catalogs with deterministic depth and join profiles, fail-closed privacy, resumable checkpoints, transactional publication, and verified Git installation, while five existing skills will route cleanly around it.

---

## Proposed Contract and Pseudocode

The skill will remain procedural and repository-neutral. The #216-specific field names, schema examples, and transaction vocabulary will live in the reference, explicitly labeled as prior art that must be parameterized before code reuse.

```text
on metadata-only external-folder catalog request:
    pre-approval:
        permit only read-only metadata resource intelligence and plan/review artifacts
        forbid checkpoints, stages, destination notes, ledgers, journals, and publication

    post-approval preflight:
        require a current status:plan-approved label applied by an authorized human
        require a fresh authorized issue comment binding the exact plan path and pushed revision
        require the same authorized human to commit the exact approval marker on the PR branch
        require the label event to postdate the marker commit's GitHub pushed timestamp
        require the approved revision blob, PR-head plan blob, and local plan bytes to agree
        require remote PR-head marker bytes and local marker bytes to equal the exact schema
        require the frozen delivery-manifest and routing-baseline hashes to agree
        classify as strict catalog, lightweight document stubs, ordinary wiki ingest,
            content extraction, or copy/migration using mutually exclusive descriptions

    source fence:
        keep the source read-only and forbid source-body reads unless separately approved
        bind canonical root plus stable volume/device identity
        reject root or ancestor reparse/junction points
        recheck source identity before/after inventory and immediately before publish
        require a versioned stability rule: two identical complete observations or
            a trustworthy filesystem snapshot/change journal that proves no descendant
            mutation; root-directory timestamps alone never qualify

    coverage contract:
        inventory the live source empirically
        select a versioned inclusion predicate or explicit plan parameter before scanning
        record root and child denominators, empty/blocked/access-lost/reparse states,
            counts, bytes, extension aggregates, and every exclusion with a reason
        use top-folder-complete for broad project/proposal containers
        use deterministic adaptive-two-level coverage for directory-heavy model containers
        represent every observed unnoted directory as aggregated, excluded-with-reason,
            blocked, or reparse-not-traversed; keep files aggregated by default

    identity and join contract:
        derive root-namespaced opaque identity plus deterministic safe slug
        reject case-fold/Unicode-normalization collisions, reserved device names,
            trailing dot/space, ADS colon, invalid surrogate, traversal, UNC/device paths
        enforce Windows UTF-16 bounds over target/stage/backup/snapshot/temp/candidate
        compute canonical typed hashes over every identity-bearing input
        normalize only configured join columns and namespace
        classify joins as unique-candidate, ambiguous-candidates, or unmatched

    private residency and evidence contract:
        discover destination repo independently of caller CWD and verify private residency
        require transient roots inside the trusted repo and Git-ignored/untracked pre-write
        reject reparse/junction ancestors on every transient or destination surface
        keep raw volume/device identity in trusted runtime/checkpoint evidence and expose
            only an opaque root token outside that boundary
        apply an artifact-class path matrix:
            private wiki notes/ledgers may use approved root-relative source names
            ignored private checkpoints/logs may use exact names under residency controls
            workspace plans/reviews/provider prompts/results/errors/GitHub comments use
                opaque folder IDs and aggregate counts only, never source-derived paths
            public artifacts use sanitized/abstracted identifiers only
        use exact-key checkpoint/journal schemas with no executable or traversal path fields
        reconstruct mutation roots only from trusted runtime arguments
        bind generator inputs, inventory, join authority, output tree, journal,
            snapshot, ledger, and ownership manifest; revalidate before recovery/mutation

    ordered publication transaction:
        stage and validate full coverage/ownership/schema/link/privacy
        derive an index-authoritative manifest of exact delivery paths, modes, OIDs,
            and tombstones; verify append-only and existing-tree ownership
        snapshot parent/tree/index/worktree state before and after verification
        materialize a detached candidate sharing the object database
        scan candidate blobs with legal/privacy checks
        create the candidate commit; prove its single expected parent, exact manifest tree,
            modes/OIDs/tombstones, journal hash, snapshot, ledger, and ownership payload;
            committed blob OIDs must equal the already-scanned manifest OIDs
        acquire the exclusive index lock, then recheck index/worktree/branch/HEAD
        install with update-ref compare-and-swap; CAS-rollback on post-install failure
        require final HEAD tree/index/worktree equality
        push and fetch-verify the remote ref equals the installed commit; on rejection,
            inspect remote state and reflog before any retry
        recover/finalize idempotently, then apply the cleanup state matrix:
            after verified finalization, remove only transaction-owned ephemeral residue
            on incomplete recovery/install/verification/push, preserve recovery evidence
            never remove a pre-existing lock without ownership and no-active-process proof
            never classify immutable snapshots or ledgers as cleanup residue
            block completion while unexpected transactional residue remains
```

The forward tests will use abstracted scenario prompts. Positive cases will cover archive and model profiles. Negative cases will cover lightweight PDF stubs, ordinary wiki ingest, copy/migration, and content extraction. Transaction fault prompts will cover dirty index, branch switch, stale HEAD, ignored delivery path, missing tombstone, unowned existing tree, staged-blob tampering, source-volume replacement, mid-scan mutation, and coordinated journal/output tampering. Neither prompt nor result will serialize an absolute source path or source-derived client identifier.

```text
build_skill_index_entry(frontmatter, body):
    if legacy frontmatter when_to_use is non-empty:
        use it as authored legacy source
    else if legacy body When-to-Use/Trigger section is non-empty:
        use that legacy authored source
    else if frontmatter keys are exactly name+description and description is non-empty:
        use description as authored source with full routing weight
    else:
        preserve legacy name+description+family backfill and its existing penalty

check_local_issue_plan_approval(repo, issue, plan, marker, manifest, owners, pr):
    import and reuse canonical gate authority/binding loaders and evaluators
    require current label set by an authorized human, never a bot/app
    require the label to postdate the approved plan revision/binding
    require the authorized binding's plan path and pushed revision to match the PR
    require the authorized marker commit/bytes and label-after-marker freshness
    require approved-revision, PR-head, and local plan blobs to agree
    require exact frozen manifest and routing-baseline hashes
    fail closed on stale/malformed/missing/GitHub errors
    never create, edit, comment, relabel, or rewrite approval state

derive_completeness_inputs(repo, changed_files):
    enumerate tracked package manifests and src package roots at the scored HEAD
    reconcile against the HEAD-bound module-status matrix package set
    build the path/package map only from those authoritative sources
    apply a fixed versioned non-package prefix policy for scripts/tests/docs/config/skills
    fail if a changed executable path is omitted, ambiguous, or outside both sets
    persist source paths, HEAD, changed files, map, classification, and scoring inputs

verify_issue_delivery(manifest, phase, index):
    parse exact expected path plus A/M/D status and Git mode entries for the phase
    reject duplicates, NUL, leading-colon pathspec magic, traversal, absolute paths,
        globs, and unknown statuses
    parse git diff --cached --name-status -z and git ls-files -s -z without newline splitting
    require exact expected/actual path+status+mode equality, including tombstones
    require every expected A/M blob and mode to exist in the index and every D blob to be absent
    reject symlink/gitlink/unexpected executable modes unless the exact manifest entry allows it
    optionally emit the exact phase pathspec as NUL for git add --pathspec-from-file
    in commit mode, require commit parent/name-status/modes/OIDs/tombstones equal manifest
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `tests/skills/test_transactional_metadata_only_folder_notes.py` | Add red-first trigger, frontmatter, contract, privacy, routing, and generated-metadata tests |
| User creates and commits after approval decision, before label | `.planning/plan-approved/3424.md` | Persist the exact four-line owner/issue/plan/revision witness; bootstrap verifies its GitHub commit actor, pushed time, reachability, and exact remote/local bytes |
| Create | `tests/workflow/test_plan_approval_local_check.py` | Add red-first companion tests for stale/missing binding or marker, changed plan/PR head, altered marker bytes, label-before-marker, bot or unauthorized label/commit actor, GitHub failure, canonical-gate SKIP resistance, frozen-hash drift, and valid bound approval |
| Create | `scripts/workflow/plan_approval_local_check.py` | Compose the canonical gate's actor/freshness/revision loaders and evaluator with exact authorized remote/local marker and plan/manifest/baseline verification while staying under file/function limits and performing no mutations |
| Create via `skill-creator` scaffolder | `.claude/skills/workspace-hub/transactional-metadata-only-folder-notes/SKILL.md` | Define the concise repository-neutral workflow |
| Create via `skill-creator` scaffolder | `.claude/skills/workspace-hub/transactional-metadata-only-folder-notes/agents/openai.yaml` | Provide matching display metadata and an explicit `$transactional-metadata-only-folder-notes` default prompt |
| Create | `.claude/skills/workspace-hub/transactional-metadata-only-folder-notes/references/verified-private-catalog-prior-art.md` | Preserve the detailed #209/#216 contracts in a neutral prior-art reference without bloating the trigger-facing skill |
| Modify | `.claude/skills/workspace-hub/learned/metadata-only-wiki-sweep-workflow/SKILL.md` | Route exact-cardinality/resumable/transactional work to the new skill and retain lightweight document stubs |
| Modify | `.claude/skills/workspace-hub/learned/metadata-only-inventory-sweep/SKILL.md` | Deprecate the overlapping legacy workflow with an explicit two-way router |
| Modify | `.claude/skills/workspace-hub/external-drive-ingest-planning/SKILL.md` | Split catalog-only work from copy/move/rsync ingest |
| Modify | `.claude/skills/workspace-hub/workspace-knowledge-doc-contracts/SKILL.md` | Route strict transactional catalogs and resolve the tracked-absolute-path precedence conflict |
| Modify | `.claude/skills/research/llm-wiki/SKILL.md` | Keep ordinary wiki ingest/query/lint separate from exact folder-catalog publication |
| Modify | `scripts/ai/build_skill_index.py` | Treat `skill-creator`-compliant descriptions as authored triggers and reserve down-weighted backfill for missing authored trigger text |
| Modify | `tests/ai/test_build_skill_index.py` | Add red-first precedence/source tests for description-authored skills and no-description legacy fallback |
| Modify | `tests/ai/test_skill_router.py` | Prove description-authored entries are not penalized and true backfill remains down-weighted |
| Pre-create and freeze before approval | `tests/ai/fixtures/description-trigger-ranking-baseline.yaml` | Bind the exact 11 candidate identities, description hashes, current sources/ranks, and expected post-change top skill; implementation will verify this reviewed file without editing it |
| Create and freeze before approval | `docs/plans/manifests/issue-3424-delivery.yaml` | Declare exact pre-review, final implementation, and completeness-closeout paths with expected A/M/D status and Git mode; embedded plan SHA binding prevents post-approval expansion |
| Create | `scripts/skills/verify_issue_delivery.py` | NUL-safely stage and verify the exact manifest against index blobs and tombstones |
| Create | `tests/skills/test_verify_issue_delivery.py` | Cover omitted new file, unexpected staged file, wrong status, tombstone, newline-like/path traversal, duplicate, and valid phase sets |
| Regenerate | `config/agents/skill-index-full.yaml` | Keep the provider-neutral full index deterministic and current |
| Regenerate | `config/agents/codex/AGENTS.runtime.md` | Update the generated Codex family count and runtime skill index |
| Update | `docs/plans/README.md` | Index this issue plan |
| Create | `scripts/review/results/2026-07-09-skill-3424-forward-test-{archive,models}.md` | Retain fresh-agent routing evidence without source-private paths |
| Create | `scripts/review/results/2026-07-09-code-3424-{claude,codex,gemini}.md` | Retain named T3 code/artifact verdicts; unavailable providers will receive explicit UNAVAILABLE artifacts |
| Create | `scripts/review/results/2026-07-09-code-3424-provider-availability.md` | Record provider auth/quota/timeout evidence and any allowed degradation |
| Create at closeout | `scripts/review/results/2026-07-09-completeness-3424-{claude,codex,gemini}.md` | Retain named targeted completeness JSON/HTML artifact verdicts |
| Create at closeout | `scripts/review/results/2026-07-09-completeness-3424-provider-availability.md` | Record completeness-review provider availability/degradation |
| Create at closeout | `docs/reports/issue-3424-completeness-inputs.json` | Bind changed files, weighted acceptance evidence, issue number, and exact computed record |
| Create at closeout | `docs/reports/2026-07-09-3424-completeness.html` | Provide the fixed issue-plan-date owner-verification artifact required before close |
| Create | `scripts/workflow/completeness_inputs.py` | Derive non-gameable changed-file/package-map/class inputs from tracked manifests, src roots, fixed exclusions, and the HEAD-bound module matrix |
| Create | `tests/workflow/test_completeness_inputs.py` | Cover omitted/ambiguous/unmapped executable paths, stale matrix HEAD, fixed non-package prefixes, and valid derived code/evidence inputs |

---

## TDD Test List

Implementation will write this test file first and will record the intended failures before scaffolding the skill.

| Test name | What it will verify | Expected input | Expected output |
|---|---|---|---|
| `test_skill_files_exist` | Red gate proves the approved implementation has not been pre-created, then becomes the basic scaffold guard | Required skill, reference, and UI-metadata paths | File-not-found failure before scaffolding; all paths exist afterward |
| `test_skill_frontmatter_is_minimal_and_trigger_complete` | Frontmatter contains exactly `name` and `description`; description carries positive and negative trigger boundaries | New `SKILL.md` | Exact two-key mapping and mutually exclusive trigger phrases |
| `test_skill_description_is_the_authored_index_trigger` | The provider-neutral index honors the canonical `skill-creator` description without a duplicate body trigger | New skill plus generated full index | No body “when to use” duplication; generated entry has `when_to_use_source: description` |
| `test_index_builder_limits_description_promotion_and_preserves_legacy_precedence` | The builder supports modern minimal authoring without rerouting the legacy corpus | Builder fixtures plus live candidate baseline | Exact name+description/no-section entry is full weight; description-plus-section keeps section; legacy extra-key description remains `backfill`; candidate set/rankings match reviewed baseline |
| `test_skill_forbids_unapproved_source_body_reads` | Metadata-only remains the default and later content reads require a separate approved plan | Skill body | Explicit read boundary and approval language |
| `test_skill_requires_empirical_coverage_and_access_loss_state` | Root/child denominators, explicit inclusion predicate, empty/blocked/reparse/excluded accounting, and “access loss is not deletion” remain mandatory | Skill/reference text | Deterministic coverage anchors present |
| `test_skill_supports_deterministic_top_folder_and_adaptive_profiles` | Both profiles use a declared versioned predicate and account for every observed directory without forcing per-file notes | Skill/reference text | Profile, representation-state, and file-aggregation rules present |
| `test_skill_requires_stable_source_volume_and_generation_fences` | Same-path drive substitution and mixed-generation scans fail closed | Skill/reference text | Stable volume/device identity, three rechecks, and mutation/stability rule present |
| `test_skill_requires_deterministic_identity_hashes_and_conservative_joins` | Opaque identity, typed hashes, configured join namespace, and unique/ambiguous/unmatched states remain explicit | Skill/reference text | Required semantic anchors present |
| `test_skill_requires_private_residency_for_every_path_surface` | Destination classification plus checkpoint, stage, journal, snapshot, ledger, backup, and candidate paths use caller-independent fail-closed checks | Skill/reference text | Trusted repo, ignored/untracked, no-reparse, and sanitized durable-output anchors present |
| `test_skill_enforces_artifact_class_path_matrix` | Private notes, private checkpoints, control-plane artifacts, and public artifacts receive distinct identifier rules | Skill/reference text | Relative names limited to private notes/ledgers; control plane uses opaque IDs/counts only |
| `test_skill_forbids_executable_paths_in_checkpoint_and_journal` | Exact-key schemas cannot inject absolute, UNC/device, or relative-traversal mutation roots | Skill/reference text | Runtime-root reconstruction, journal binding, and pre-mutation revalidation present |
| `test_skill_requires_windows_identity_and_path_safety` | Source-derived filenames cannot collide or escape under Windows semantics | Skill/reference text | Case-fold, Unicode normalization, reserved-name, trailing-dot/space, ADS, surrogate, traversal, and UTF-16 bounds present |
| `test_skill_requires_ordered_transactional_git_candidate_protocol` | The reference preserves operation ordering, not just transaction keywords | Skill/reference text | Index-authoritative manifest; parent snapshots; detached candidate; verified single-parent commit/tree/payload; blob scan; exclusive lock; post-lock rechecks; update-ref CAS; rollback; final equality; push/fetch verification |
| `test_skill_requires_legal_privacy_and_cleanup_gates` | Existing legal, routing, artifact-verification, and cleanup skills are linked rather than replaced | Skill/reference text | Canonical adjacent skill references present |
| `test_openai_metadata_matches_skill` | UI metadata remains consistent and the default prompt explicitly invokes the skill | `agents/openai.yaml` | Correct name, 25–64 character description, `$transactional-metadata-only-folder-notes` prompt |
| `test_competing_frontmatter_descriptions_are_mutually_exclusive` | Discovery surfaces route before bodies load | New skill plus five affected owners | Six positive/negative descriptions separate strict catalog, lightweight stub, ordinary wiki, content extraction, and copy/migration work |
| `test_lightweight_sweep_routes_transactional_catalogs` | Exact-cardinality/resume/immutable/publication requests leave the lightweight stub workflow | Existing lightweight skill | Frontmatter and body both route to the new skill |
| `test_legacy_inventory_skill_is_deprecated_without_dead_end` | The overlapping legacy skill cannot win new routing | Legacy skill | Description begins with a non-invocation/deprecation boundary and body points to both current owners |
| `test_external_drive_skill_routes_catalog_only_requests` | “prepare notes/catalog” does not fall through to checksum/rsync/copy execution | External-drive skill | Frontmatter and catalog-only branch exclude transfer semantics |
| `test_workspace_knowledge_contract_resolves_absolute_path_precedence` | Strict catalogs do not inherit the generic pointer-page absolute-path rule | Knowledge-contract skill | Explicit precedence route and logical-root-token rule present |
| `test_general_llm_wiki_skill_routes_strict_folder_catalogs` | Broad wiki ingestion does not invoke content/batch commands for strict catalogs | General llm-wiki skill | Frontmatter and body route before ingest commands |
| `test_reference_does_not_advertise_drive_j_script_as_generic` | Prior implementation remains labeled repository-specific pending an approved parameterization issue | #216 reference | Explicit non-generic warning and no copy-paste execution directive |
| `test_progressive_disclosure_and_scaffold_cleanup` | The main skill stays bounded and tells the agent when to load its reference | New skill directory | No TODO/scaffold text; linked load condition; bounded `SKILL.md` line count |
| `test_new_skill_contains_no_absolute_machine_paths` | The reusable artifact does not leak or normalize around a workstation path | New skill directory text files | No drive-letter, UNC/device, or local mount absolute path; forensic test literals carry per-line sentinels |
| `test_generated_indexes_and_runtime_surface_new_skill` | Deterministic discovery artifacts remain coherent | Full skill index and Codex runtime | Exact skill entry plus incremented `workspace-hub` family count; runtime drift check passes |
| `test_local_approval_companion_reuses_authoritative_binding` | Local implementation cannot begin on stale/forged/unbound approval or canonical low-risk SKIP | Companion with stubbed canonical loaders plus temporary marker/plan/manifest/baseline and optimized-Python subprocess | Only current authorized-human label plus authenticated GitHub-web owner commit, valid web-flow signature, label-after-marker freshness, normal `100644` index entries, equal local/index/HEAD/remote blobs, and frozen hashes succeeds; forged author/pusher, missing signature, assume-unchanged/skip-worktree, mode, staged, local, or remote drift fails; a nonzero `git status` with empty stdout fails; `GIT_OPTIONAL_LOCKS=0` preserves index bytes/lock absence; mode performs no writes and fails identically with optimization enabled |
| `test_cleanup_state_matrix_preserves_recovery_authority` | Cleanup cannot destroy blocked recovery evidence or immutable records | Skill/reference text | State-specific remove/preserve/block rules and pre-existing-lock guard present |
| `test_delivery_manifest_matches_staged_set_exactly` | An incomplete, magic-expanded, mode-changed, or contaminated index/commit cannot pass | Manifest verifier fixtures | Exact NUL-safe A/M/D/mode/OID equality; omitted/unexpected file, leading-colon magic, NUL, executable-bit drift, symlink, gitlink, wrong parent/tree/status/OID, and missing tombstone fail |
| `test_candidate_install_verifies_locked_index_read_only` | The exclusive index lock cannot make verification self-block, hide mutation, strand the ref/lock, or publish an unscanned ref | Temporary Git repo with owned index lock, candidate commit, and bare remote | Traps are armed before lock creation; ownership token includes a per-attempt unpredictable nonce; verifier uses only read-only index/status/OID checks; rollback inspects the actual ref rather than a flag; `write-tree` is not invoked while locked; index-byte drift, dirty worktree, PID-reused stale lock, pre/post-CAS signals, CAS conflict, rollback failure, mutable-local-ref race, and remote lease conflict all stop or preserve the verified remote state; push source is the immutable candidate and only the owned lock is removed before traps are disarmed |
| `test_completeness_inputs_are_authoritatively_derived` | Completeness class cannot be gamed through an empty/selective map | Fixture repo with manifests/src/scripts/tests and changed paths | HEAD-bound deterministic map; omitted/ambiguous/unmapped executable path fails before classify |

---

## Exact Execution and Validation Sequence

The following sequence will run only after the user applies plan approval:

1. Commit and push the reviewed plan, manifest, routing baseline, and review evidence, then open the plan PR. Using the authenticated GitHub web editor—not a local/agent Git commit—the user/authorized owner will commit the exact four-line marker below to `.planning/plan-approved/3424.md` on that PR branch, record one issue comment containing the exact plan path and `Plan revision: <40-character reviewed plan commit>`, and apply `status:plan-approved` only after the marker commit and binding comment. The agent will create none of those three approval witnesses. Fetch and fast-forward the local branch to the user marker commit, then, before any implementation write, invoke the existing canonical authority/binding loaders and evaluator directly. The bootstrap will additionally prove `committedViaWeb`, GitHub-valid/web-flow signature, authenticated owner author, exact remote/local bytes, reachability, pushed timestamp, and label-after-marker freshness. It will bind local bytes, index blob/mode/flags, local HEAD blob, and remote PR-head blob for the plan, marker, manifest, and routing baseline; `assume-unchanged`, `skip-worktree`, symlink, executable, or filter-hidden drift will fail. This avoids both the PR entry point's intentional low-risk-path SKIP and the POSIX-only approval-transaction lock on this Windows host. Every comparison will fail explicitly under normal and optimized Python:

   ```text
   Approved by: vamseeachanta
   Issue: 3424
   Plan: docs/plans/2026-07-09-issue-3424-transactional-metadata-only-folder-notes.md
   Plan revision: <reviewed 40-character plan commit>
   ```

   ```bash
   set -euo pipefail
   export GIT_OPTIONAL_LOCKS=0
   repo=vamseeachanta/workspace-hub
   plan=docs/plans/2026-07-09-issue-3424-transactional-metadata-only-folder-notes.md
   marker=.planning/plan-approved/3424.md
   manifest=docs/plans/manifests/issue-3424-delivery.yaml
   baseline=tests/ai/fixtures/description-trigger-ranking-baseline.yaml
   pr="$(gh pr view --repo "${repo}" --json number --jq .number)"
   owners=vamseeachanta
   local_branch="$(git symbolic-ref --quiet --short HEAD)"
   local_head="$(git rev-parse HEAD)"
   test -n "${pr}" && test -n "${owners}"
   git diff --quiet
   git diff --cached --quiet
   status_output="$(git status --porcelain=v2 --untracked-files=all)"
   test -z "${status_output}"
   printf '%s  %s\n' \
     d191a10694b62440c45482f710d4ef3c8397c1e537067f4be6d472b8e422d175 "${manifest}" \
     9ba4fb7aa79d81a9eb2a96caaa4ddcdd2ed09fa1ab57f7300c1ee7c8f6ab5f54 "${baseline}" \
     | sha256sum --check --strict
   PYTHONOPTIMIZE=1 python - \
     "${repo}" "${pr}" "${owners}" "${local_branch}" "${local_head}" \
     "${plan}" "${marker}" "${manifest}" "${baseline}" <<'PY'
   import base64, hashlib, pathlib, subprocess, sys
   sys.path.insert(0, str(pathlib.Path("scripts/workflow").resolve()))
   from label_authority import gh_json, is_authorized_human, label_is_fresh
   from plan_approval_gate_check import (
       evaluate_plan_approval, fetch_actor_type, load_issue_approval,
       load_pr_context, parse_owners, validate_owner_types,
   )
   from plan_approval_gate_io import (
       fetch_commit_pushed_at, fetch_file_blob, revision_reaches_head,
   )
   (repo, pr_raw, owners_raw, local_branch, local_head,
    plan_path, marker_path, manifest_path, baseline_path) = sys.argv[1:]
   owners = parse_owners(owners_raw)
   owner_types = {owner: fetch_actor_type(owner) for owner in owners}
   owner_decision = validate_owner_types(owner_types)
   if not owner_decision.allowed:
       raise SystemExit(owner_decision.reason)
   context = load_pr_context(repo, int(pr_raw))
   if context.branch_name != local_branch:
       raise SystemExit("local branch does not equal approved PR branch")
   if context.head_sha != local_head:
       raise SystemExit("local HEAD does not equal approved PR head")
   approval = load_issue_approval(
       repo, 3424, owners, owner_types, context.head_sha, context.base_sha,
   )
   decision = evaluate_plan_approval(context, {3424: approval}, owners)
   if not decision.allowed:
       raise SystemExit(decision.reason)
   binding = approval.plan_binding
   expected_sha256 = {
       manifest_path: "d191a10694b62440c45482f710d4ef3c8397c1e537067f4be6d472b8e422d175",
       baseline_path: "9ba4fb7aa79d81a9eb2a96caaa4ddcdd2ed09fa1ab57f7300c1ee7c8f6ab5f54",
   }
   for artifact_path in (plan_path, marker_path, manifest_path, baseline_path):
       local_bytes = pathlib.Path(artifact_path).read_bytes()
       if artifact_path in expected_sha256:
           if hashlib.sha256(local_bytes).hexdigest() != expected_sha256[artifact_path]:
               raise SystemExit(f"frozen digest mismatch: {artifact_path}")
       flag_record = subprocess.check_output(
           ["git", "ls-files", "-v", "-z", "--", artifact_path],
       )
       if flag_record != f"H {artifact_path}\0".encode():
           raise SystemExit(f"index flag or tracked-path mismatch: {artifact_path}")
       stage_record = subprocess.check_output(
           ["git", "ls-files", "-s", "-z", "--", artifact_path],
       )
       if not stage_record.endswith(f"\t{artifact_path}\0".encode()):
           raise SystemExit(f"index stage path mismatch: {artifact_path}")
       mode, index_oid, stage = stage_record.split(b"\t", 1)[0].decode().split()
       if mode != "100644" or stage != "0":
           raise SystemExit(f"index mode/stage mismatch: {artifact_path}")
       local_oid = subprocess.check_output(
           ["git", "hash-object", "--stdin"], input=local_bytes,
       ).decode().strip()
       head_oid = subprocess.check_output(
           ["git", "rev-parse", f"HEAD:{artifact_path}"], text=True,
       ).strip()
       remote_oid = fetch_file_blob(repo, context.head_sha, artifact_path)
       if len({local_oid, index_oid, head_oid, remote_oid}) != 1:
           raise SystemExit(f"local/index/HEAD/remote blob mismatch: {artifact_path}")
   marker_meta = gh_json(
       "api", f"repos/{repo}/contents/{marker_path}?ref={context.head_sha}",
   ) or {}
   if marker_meta.get("type") != "file":
       raise SystemExit("approval marker is not a file at PR head")
   encoded_marker = "".join(marker_meta.get("content", "").split())
   remote_marker = base64.b64decode(encoded_marker, validate=True)
   local_marker = pathlib.Path(marker_path).read_bytes()
   expected_marker = (
       "Approved by: vamseeachanta\nIssue: 3424\n"
       "Plan: docs/plans/2026-07-09-issue-3424-transactional-metadata-only-folder-notes.md\n"
       f"Plan revision: {binding.revision_sha}\n"
   ).encode()
   if remote_marker != expected_marker or local_marker != expected_marker:
       raise SystemExit("approval marker bytes do not match the authorized binding")
   commits = gh_json(
       "api", f"repos/{repo}/commits?sha={context.head_sha}&path={marker_path}&per_page=1",
   ) or []
   if len(commits) != 1:
       raise SystemExit("unique approval-marker commit unavailable")
   marker_commit = commits[0]
   marker_sha = marker_commit.get("sha")
   if marker_sha != context.head_sha:
       raise SystemExit("approval marker commit must be the PR head")
   marker_commit = gh_json("api", f"repos/{repo}/commits/{marker_sha}") or {}
   parents = [item.get("sha") for item in marker_commit.get("parents", [])]
   changed = marker_commit.get("files", [])
   if parents != [binding.revision_sha]:
       raise SystemExit("approval marker commit is not the direct child of reviewed plan")
   if len(changed) != 1 or changed[0].get("filename") != marker_path:
       raise SystemExit("approval marker commit contains an unreviewed path")
   if changed[0].get("status") != "added":
       raise SystemExit("approval marker was not added by the approval commit")
   tree = gh_json("api", f"repos/{repo}/git/trees/{context.head_sha}?recursive=1") or {}
   marker_entries = [item for item in tree.get("tree", []) if item.get("path") == marker_path]
   if len(marker_entries) != 1 or marker_entries[0].get("mode") != "100644":
       raise SystemExit("approval marker mode/type is not a regular non-executable file")
   if marker_entries[0].get("sha") != marker_meta.get("sha"):
       raise SystemExit("approval marker tree/blob binding failed")
   marker_actor = ((marker_commit.get("author") or {}).get("login"))
   marker_actor_type = fetch_actor_type(marker_actor)
   if not is_authorized_human(
       marker_actor, owners, reject_bots=True, actor_type=marker_actor_type,
   ):
       raise SystemExit("approval marker commit author is not authorized")
   owner, name = repo.split("/", 1)
   signature_query = """
   query($owner:String!,$name:String!,$oid:GitObjectID!){
     repository(owner:$owner,name:$name){object(oid:$oid){... on Commit{
       committedViaWeb author{user{login}}
       signature{isValid wasSignedByGitHub signer{login} state}
     }}}
   }
   """
   signature_data = gh_json(
       "api", "graphql", "-f", f"owner={owner}", "-f", f"name={name}",
       "-f", f"oid={marker_sha}", "-f", f"query={signature_query}",
   ) or {}
   attestation = (((signature_data.get("data") or {}).get("repository") or {}).get("object")) or {}
   signature = attestation.get("signature") or {}
   web_author = (((attestation.get("author") or {}).get("user") or {}).get("login"))
   if not attestation.get("committedViaWeb") or web_author != "vamseeachanta":
       raise SystemExit("marker lacks authenticated owner GitHub-web provenance")
   if not signature.get("isValid") or not signature.get("wasSignedByGitHub"):
       raise SystemExit("marker lacks a valid GitHub signature")
   if signature.get("state") != "VALID" or (signature.get("signer") or {}).get("login") != "web-flow":
       raise SystemExit("marker GitHub signature provenance is invalid")
   if not revision_reaches_head(repo, marker_sha, context.head_sha):
       raise SystemExit("approval marker commit is not in PR head history")
   marker_pushed_at = fetch_commit_pushed_at(repo, marker_sha)
   if not label_is_fresh(approval.label_applied_at, marker_pushed_at):
       raise SystemExit("approval label predates approval marker commit")
   print(decision.reason)
   PY
   ```

2. Write the new skill/delivery/completeness/approval-companion tests and red cases in `tests/ai/test_build_skill_index.py` and `tests/ai/test_skill_router.py`; run them to capture the expected missing-skill, missing-companion, missing-delivery/completeness helpers, and description-trigger failures.
3. Read the system skill creator's `references/openai_yaml.md`, then initialize the skill with the repository path explicitly because this cross-provider workflow belongs in the repo-tracked control plane:

   ```bash
   python "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/init_skill.py" \
     transactional-metadata-only-folder-notes \
     --path .claude/skills/workspace-hub \
     --resources references \
     --interface display_name="Transactional Folder Notes" \
     --interface short_description="Publish verified metadata-only folder catalogs" \
     --interface 'default_prompt=Use $transactional-metadata-only-folder-notes to plan a private, metadata-only folder catalog with verified publication.'
   ```

4. Replace all scaffold placeholders, write the neutral prior-art reference, make the five bounded routing edits, add the read-only canonical-gate companion, add the delivery manifest/verifier and completeness-input derivation, and update the skill-index builder/router contract. Keep every new file at or below 400 lines and every function at or below 50 lines. Update all six relevant frontmatter descriptions before relying on routing tests.
5. Regenerate `agents/openai.yaml` from the final `SKILL.md`:

   ```bash
   set -euo pipefail
   python "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/generate_openai_yaml.py" \
     .claude/skills/workspace-hub/transactional-metadata-only-folder-notes \
     --interface display_name="Transactional Folder Notes" \
     --interface short_description="Publish verified metadata-only folder catalogs" \
     --interface 'default_prompt=Use $transactional-metadata-only-folder-notes to plan a private, metadata-only folder catalog with verified publication.'

   ```

6. Validate the new skill with both the system and workspace validators:

   ```bash
   set -euo pipefail
   python "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
     .claude/skills/workspace-hub/transactional-metadata-only-folder-notes
   uv run python scripts/skills/validate_skills_frontmatter.py
   bash scripts/skills/validate-skills.sh
   ```

7. Regenerate deterministic indexes, rebuild the Codex runtime artifact, and prove the generated surfaces are current:

   ```bash
   set -euo pipefail
   uv run python scripts/ai/build_skill_index.py
   bash scripts/agents/build-soul-runtime.sh
   uv run python scripts/enforcement/check-skill-index-coherence.py
   bash scripts/enforcement/check-soul-runtime-drift.sh
   rg -n 'transactional-metadata-only-folder-notes' config/agents/skill-index-full.yaml
   expected="$(find .claude/skills/workspace-hub -name SKILL.md | wc -l | tr -d ' ')"
   rg -n "workspace-hub/.*${expected} skill" config/agents/codex/AGENTS.runtime.md
   ```

8. Run the focused and related tests after generated artifacts exist. Drive-letter/UNC/device/traversal fixtures will use constructed literals or the no-absolute-path checker's per-line sentinel. Legal-deny behavior will use a synthetic temporary deny list with harmless fixture tokens because the legal scanner has no generic per-line sentinel; no production deny token or file-wide exemption will be embedded:

   ```bash
   set -euo pipefail
   uv run pytest \
     tests/skills/test_transactional_metadata_only_folder_notes.py \
     tests/skills/test_verify_issue_delivery.py \
     tests/workflow/test_plan_approval_local_check.py \
     tests/workflow/test_completeness_inputs.py \
     tests/ai/test_build_skill_index.py tests/ai/test_skill_router.py -v
   uv run pytest tests/skills tests/enforcement/test_skill_graph_integrity.py tests/enforcement/test_check_skill_index_coherence.py -q
   bash scripts/enforcement/check-no-abs-paths.sh tests/skills/test_transactional_metadata_only_folder_notes.py
   bash scripts/enforcement/check-no-abs-paths.sh
   bash scripts/enforcement/check-no-conflict-markers.sh
   git diff --check
   ```

   After the companion is green, run it against real issue #3424, the current plan PR/head, the authorized remote binding/label event, and both frozen planning artifacts. Any mismatch blocks staging; rerun the same command immediately before candidate-commit creation:

   ```bash
   set -euo pipefail
   python scripts/workflow/plan_approval_local_check.py \
     --repo vamseeachanta/workspace-hub --issue 3424 \
     --pr "$(gh pr view --repo vamseeachanta/workspace-hub --json number --jq .number)" \
     --plan docs/plans/2026-07-09-issue-3424-transactional-metadata-only-folder-notes.md \
     --marker .planning/plan-approved/3424.md \
     --delivery-manifest docs/plans/manifests/issue-3424-delivery.yaml \
     --delivery-sha256 d191a10694b62440c45482f710d4ef3c8397c1e537067f4be6d472b8e422d175 \
     --routing-baseline tests/ai/fixtures/description-trigger-ranking-baseline.yaml \
     --routing-baseline-sha256 9ba4fb7aa79d81a9eb2a96caaa4ddcdd2ed09fa1ab57f7300c1ee7c8f6ab5f54 \
     --owners vamseeachanta
   ```

9. Dispatch fresh adversarial agents in parallel against abstracted archive/model positive prompts, four routing-negative prompts, and transaction/source fault prompts. Require each agent to state the selected skill, depth predicate, join policy, privacy boundary, transaction boundary, and downstream issue route. Record the results in the two forward-test artifacts.
10. Emit the exact pre-review manifest phase as NUL pathspecs, stage only those paths, and require NUL-safe A/M/D/tombstone equality before scanning. Then require the artifact worktree bytes to equal the index, capture branch/HEAD/index-tree state, run staged-aware checks plus working-tree scanners against those equal bytes, and recheck every fence. This closes both omitted-new-file delivery gaps and bad-staged-blob/sanitized-worktree TOCTOU without claiming that `--diff-only` itself reads index blobs:

    ```bash
    set -euo pipefail
    python scripts/skills/verify_issue_delivery.py \
      --manifest docs/plans/manifests/issue-3424-delivery.yaml \
      --phase pre_review --paths0 \
      | git --literal-pathspecs add -f --pathspec-from-file=- --pathspec-file-nul
    python scripts/skills/verify_issue_delivery.py \
      --manifest docs/plans/manifests/issue-3424-delivery.yaml \
      --phase pre_review --cached
    git diff --quiet
    branch_before="$(git symbolic-ref --quiet --short HEAD)"
    head_before="$(git rev-parse HEAD)"
    tree_before="$(git write-tree)"
    uv run python scripts/legal/check-client-pii.py --staged
    bash scripts/legal/legal-sanity-scan.sh --diff-only
    bash scripts/enforcement/check-no-abs-paths.sh
    bash scripts/enforcement/check-no-conflict-markers.sh
    git diff --cached --check
    tree_after="$(git write-tree)"
    test "${tree_before}" = "${tree_after}"
    test "${branch_before}" = "$(git symbolic-ref --quiet --short HEAD)"
    test "${head_before}" = "$(git rev-parse HEAD)"
    git diff --quiet
    python scripts/skills/verify_issue_delivery.py \
      --manifest docs/plans/manifests/issue-3424-delivery.yaml \
      --phase pre_review --cached
    ```

11. Conduct T3 code/artifact adversarial review targeting Claude, Codex, and Gemini. If provider outages force degraded T2 review, record each unavailable provider and still require two distinct providers; multiple same-provider agents add depth but do not satisfy provider diversity. If only one provider is available, keep the review gate blocked. Any review-driven edit will return through tests, index regeneration, staging, and the equality-fenced scan in step 10.
12. Use the already-predeclared final manifest phase without modifying the frozen manifest. Stage its named review/provider artifacts with literal NUL pathspecs, verify `--phase final --cached`, rerun the approval companion, and rerun every step-10 equality/branch/HEAD/tree/scanner fence. Create a detached candidate commit directly from the persisted `scanned_tree`; never use pathspec `git commit`, which can reread working-tree bytes. Verify the candidate parent/tree/name-status/modes/OIDs/tombstones before installation and fail if a newly active commit hook would be bypassed. Acquire an ownership-marked exclusive index lock with a cryptographically unpredictable per-attempt nonce; while it is held, use only read-only index-byte hash, status, diff, and cached OID/mode checks—never `write-tree` or another index writer. Install the verified candidate with `update-ref` compare-and-swap, and use non-recursive signal/error traps to CAS-rollback and release only the owned lock on any post-install verification failure. Only then release the lock and push the immutable candidate object—not the mutable local ref—with a remote-head lease, fetch, and verify the local/remote refs and remote tree. On a rejected push, inspect the remote ref and reflog before retrying.

    ```bash
    set -euo pipefail
    # Stage the predeclared final phase and rerun the real approval/scanner gates.
    python scripts/skills/verify_issue_delivery.py \
      --manifest docs/plans/manifests/issue-3424-delivery.yaml \
      --phase final --paths0 \
      | git --literal-pathspecs add -f --pathspec-from-file=- --pathspec-file-nul
    python scripts/skills/verify_issue_delivery.py \
      --manifest docs/plans/manifests/issue-3424-delivery.yaml \
      --phase final --cached
    python scripts/workflow/plan_approval_local_check.py \
      --repo vamseeachanta/workspace-hub --issue 3424 \
      --pr "$(gh pr view --repo vamseeachanta/workspace-hub --json number --jq .number)" \
      --plan docs/plans/2026-07-09-issue-3424-transactional-metadata-only-folder-notes.md \
      --marker .planning/plan-approved/3424.md \
      --delivery-manifest docs/plans/manifests/issue-3424-delivery.yaml \
      --delivery-sha256 d191a10694b62440c45482f710d4ef3c8397c1e537067f4be6d472b8e422d175 \
      --routing-baseline tests/ai/fixtures/description-trigger-ranking-baseline.yaml \
      --routing-baseline-sha256 9ba4fb7aa79d81a9eb2a96caaa4ddcdd2ed09fa1ab57f7300c1ee7c8f6ab5f54 \
      --owners vamseeachanta
    branch_before="$(git symbolic-ref --quiet --short HEAD)"
    ref="$(git symbolic-ref --quiet HEAD)"
    head_before="$(git rev-parse HEAD)"
    git diff --quiet
    uv run python scripts/legal/check-client-pii.py --staged
    bash scripts/legal/legal-sanity-scan.sh --diff-only
    bash scripts/enforcement/check-no-abs-paths.sh
    bash scripts/enforcement/check-no-conflict-markers.sh
    git diff --cached --check
    python scripts/skills/verify_issue_delivery.py \
      --manifest docs/plans/manifests/issue-3424-delivery.yaml \
      --phase final --cached
    hooks_dir="$(git rev-parse --git-path hooks)"
    for hook in pre-commit prepare-commit-msg commit-msg post-commit; do
      test ! -x "${hooks_dir}/${hook}"
    done
    scanned_tree="$(git write-tree)"
    test "${branch_before}" = "$(git symbolic-ref --quiet --short HEAD)"
    test "${head_before}" = "$(git rev-parse HEAD)"
    test "${scanned_tree}" = "$(git write-tree)"
    git diff --quiet
    index_path="$(git rev-parse --git-path index)"
    index_sha="$(sha256sum "${index_path}" | awk '{print $1}')"
    candidate="$(printf '%s\n\n%s\n' \
      'feat(skills): add transactional folder-note workflow (#3424)' \
      'Implements the user-approved plan.' \
      | git commit-tree "${scanned_tree}" -p "${head_before}")"
    test "$(git rev-parse "${candidate}^{tree}")" = "${scanned_tree}"
    python scripts/skills/verify_issue_delivery.py \
      --manifest docs/plans/manifests/issue-3424-delivery.yaml \
      --phase final --commit "${candidate}" --expected-parent "${head_before}"
    index_lock="$(git rev-parse --git-path index).lock"
    lock_nonce="$(python -c 'import secrets; print(secrets.token_hex(16))')"
    test "${#lock_nonce}" = 32
    case "${lock_nonce}" in *[!0-9a-f]*) exit 1;; esac
    lock_token="issue=3424 pid=$$ nonce=${lock_nonce}"
    cleanup_lock() {
      if ! test -f "${index_lock}"; then return 0; fi
      if test "$(cat "${index_lock}")" != "${lock_token}"; then
        printf 'refusing to remove unowned index lock: %s\n' "${index_lock}" >&2
        return 1
      fi
      rm -f -- "${index_lock}"
    }
    rollback() {
      status="${1:-1}"
      trap - ERR INT TERM HUP
      current_ref="$(git rev-parse "${ref}" 2>/dev/null || printf unavailable)"
      rollback_failed=0
      if test "${current_ref}" = "${candidate}"; then
        if ! git update-ref "${ref}" "${head_before}" "${candidate}"; then
          rollback_failed=1
          printf 'candidate rollback CAS failed; observed ref=%s\n' \
            "$(git rev-parse "${ref}" 2>/dev/null || printf unavailable)" >&2
        fi
      elif test "${current_ref}" != "${head_before}"; then
        rollback_failed=1
        printf 'candidate rollback refused; unexpected ref=%s\n' "${current_ref}" >&2
      fi
      if ! cleanup_lock; then rollback_failed=1; fi
      if test "${rollback_failed}" = 1; then status=1; fi
      exit "${status}"
    }
    trap 'rollback $?' ERR
    trap 'rollback 130' INT TERM HUP
    (set -o noclobber; printf '%s\n' "${lock_token}" >"${index_lock}")
    test "${branch_before}" = "$(git symbolic-ref --quiet --short HEAD)"
    test "${head_before}" = "$(git rev-parse HEAD)"
    test "${index_sha}" = "$(sha256sum "${index_path}" | awk '{print $1}')"
    git diff --quiet
    git diff --cached --check
    python scripts/skills/verify_issue_delivery.py \
      --manifest docs/plans/manifests/issue-3424-delivery.yaml \
      --phase final --cached
    git update-ref "${ref}" "${candidate}" "${head_before}"
    test "$(git rev-parse HEAD)" = "${candidate}"
    test "$(git rev-parse 'HEAD^{tree}')" = "${scanned_tree}"
    test "${index_sha}" = "$(sha256sum "${index_path}" | awk '{print $1}')"
    git diff --quiet
    git diff --cached --quiet
    python scripts/skills/verify_issue_delivery.py \
      --manifest docs/plans/manifests/issue-3424-delivery.yaml \
      --phase final --commit HEAD --expected-parent "${head_before}"
    cleanup_lock
    trap - ERR INT TERM HUP
    if ! git push --force-with-lease="${ref}:${head_before}" \
      origin "${candidate}:${ref}"; then
      git ls-remote origin "${ref}" || true
      git reflog show --date=iso "${ref}" -n 10 || true
      exit 1
    fi
    git fetch origin "${ref}:refs/remotes/origin/${branch_before}"
    test "$(git rev-parse "${ref}")" = "${candidate}"
    test "$(git rev-parse "refs/remotes/origin/${branch_before}")" = "${candidate}"
    test "$(git rev-parse "refs/remotes/origin/${branch_before}^{tree}")" = "${scanned_tree}"
    ```
13. Post the required implementation summary comment on [#3424](https://github.com/vamseeachanta/workspace-hub/issues/3424), including red/green evidence, final tests/scans, review verdicts, commit, remote verification, sources consumed, and promotion candidates.
14. Use `scripts/workflow/completeness_inputs.py` to derive and persist the changed-file set plus path/package map in `docs/reports/issue-3424-completeness-inputs.json` from tracked manifests, `src` roots, fixed versioned non-package prefixes, and the HEAD-bound module-status matrix. Fail before classification if any changed executable path is omitted, ambiguous, or unmapped. Then call `completeness_score.classify(changed_files, path_package_map)`. If the derived class is `code`, compute `score_code` only with a HEAD-SHA-bound quality snapshot, changed-code coverage, and evidence-linked checklist; if it is `evidence`, compute `score_evidence` from weighted acceptance evidence. Never preselect the easier class. Fail closed and require plan revision if the derived class cannot satisfy its inputs/threshold. Stamp the exact resulting JSON block on the issue body, persist matching kanban metadata, and render `docs/reports/2026-07-09-3424-completeness.html`.
15. Update this plan and `docs/plans/README.md` to implementation-complete/owner-verification-pending, then conduct the targeted adversarial completeness artifact review into the four predeclared review/availability paths. This review has the same T3 target and degraded-T2 floor of two distinct providers as step 11; one available provider blocks closeout. Stage the manifest's exact eight-path `closeout` phase via literal NUL pathspecs, then run the delivery verifier plus every equality-fenced legal/privacy/conflict/diff scan. After any correction, regenerate/re-review the artifacts, restage the full closeout phase, and rerun all gates so the final review evidence is itself scanned and verified. Commit/push the closeout artifacts through the same detached-candidate/CAS protocol and fetch-verify the remote commit/tree. If record persistence, scans, review, or remote verification fails, stop closeout.
16. Run the mandatory pre-completion cleanup audit. Explicitly apply the cleanup state matrix to candidate worktrees, index locks, checkpoints, stages, journals, backups, and fresh-agent scratch; preserve blocked recovery evidence and never remove immutable snapshots/ledgers. No `.planning/approval-transactions/**` residue is expected from this read-only approval path, so any such task-created residue is UNEXPECTED.
17. Hard-stop for the user/owner to inspect the completeness record and apply `status:completeness-verified`. The agent will never apply that label. Only after the fresh owner label exists will `scripts/enforcement/check-completeness-before-close.sh 3424` run and the issue close; remote issue state will then be read back and verified.
18. Rerun the cleanup audit after issue closure and final remote verification before claiming completion.

---

## Acceptance Criteria

- [ ] The new skill directory is created through `init_skill.py`, contains no scaffold placeholders, and passes `quick_validate.py`.
- [ ] Implementation begins only after the authorized human commits the exact four-line `.planning/plan-approved/3424.md` marker on the PR branch, records the exact pushed plan-path/revision binding, and then applies the current `status:plan-approved` label; the agent creates none of those witnesses.
- [ ] Bootstrap and the reusable companion directly compose the canonical label-authority/binding loaders and evaluator, verify authorized non-bot label actor plus an authenticated owner `committedViaWeb` marker with valid GitHub/web-flow signature, label-after-marker freshness, the marker as the PR-head/direct-child single-path `100644` commit, and plan/marker/manifest/baseline local-index-HEAD-remote blob equality with normal index flags, use `GIT_OPTIONAL_LOCKS=0`, fail on status-command errors before testing empty output, preserve index bytes/lock absence, perform no mutations, stay within 400 lines/50 lines per function, and fail under normal or optimized Python on any stale/malformed/missing/GitHub/hash mismatch.
- [ ] The approved owner allowlist is exactly `vamseeachanta` (live GitHub type `User`); no missing repository variable or caller-selected username can broaden it, and any allowlist change returns to plan review and user re-approval.
- [ ] Before the first implementation write, local branch and HEAD equal the approved PR branch/head and both staged and unstaged diffs are empty; the companion repeats local/remote head binding before final staging.
- [ ] The pre-approved three-phase delivery manifest remains byte-identical to SHA-256 `d191a10694b62440c45482f710d4ef3c8397c1e537067f4be6d472b8e422d175`; any path/status/mode expansion requires plan review and user re-approval.
- [ ] The pre-approved routing baseline remains byte-identical to SHA-256 `9ba4fb7aa79d81a9eb2a96caaa4ddcdd2ed09fa1ab57f7300c1ee7c8f6ab5f54`; the live candidate IDs and description hashes must match it before the builder changes, and implementation never rewrites the fixture.
- [ ] `skill-creator/references/openai_yaml.md` is read before initialization, and `agents/openai.yaml` is regenerated after the final `SKILL.md` edit.
- [ ] `SKILL.md` frontmatter contains only `name` and `description`; its description carries mutually exclusive positive/negative trigger boundaries, the body does not duplicate trigger instructions, and the provider-neutral index records `when_to_use_source: description` without a backfill penalty.
- [ ] The skill keeps source observation metadata-only by default and requires a later approved issue/plan for any source-body read.
- [ ] The skill binds canonical source root plus stable volume/device identity, rejects reparse/junction ancestors, rechecks identity at three fences, and detects mid-scan mutation or drive substitution.
- [ ] The skill requires a versioned inclusion predicate or explicit plan parameter before inventory, then records root/child denominators and empty, blocked, access-lost, reparse, excluded-with-reason, aggregated, file-count, directory-count, byte-count, and extension evidence.
- [ ] The skill states that access loss is blocked evidence, not deletion, and requires full re-observation before publication.
- [ ] The skill supports top-folder-complete and deterministic adaptive-two-level profiles; every observed directory receives a representation state and no per-file note is emitted by default.
- [ ] Opaque root-namespaced identity, collision-safe slugs, canonical typed hashing, configured join authority, and unique-candidate/ambiguous-candidates/unmatched outcomes are deterministic and fail closed.
- [ ] Windows path safety covers case-fold and Unicode-normalization collisions, reserved device names, trailing dot/space, ADS colons, invalid surrogates, traversal, UNC/device paths, reparse/junctions, and UTF-16 bounds across all write surfaces.
- [ ] Caller-independent destination discovery proves private residency; transient roots are inside the trusted repo, ignored/untracked before write, and free of reparse/junction ancestors.
- [ ] Checkpoint and journal schemas contain no executable or traversal paths; mutation roots are reconstructed from trusted runtime inputs, journal ownership is hash-bound, and coordinated tampering fails before mutation/recovery.
- [ ] The artifact-class matrix is enforced: private notes/ledgers may contain approved root-relative source names; ignored private checkpoints/logs may contain exact names; workspace plans/reviews/provider outputs/errors/GitHub comments use only opaque IDs and aggregate counts; public artifacts are sanitized/abstracted. The generic pointer-page absolute-path rule remains available only outside this strict catalog route.
- [ ] The ordered transaction requires an index-authoritative modes/OIDs/tombstones manifest, existing-tree ownership, parent snapshots, detached candidate, verified single-parent commit/tree/payload, candidate-blob legal scan, exclusive index lock, post-lock state rechecks, update-ref CAS, CAS rollback, final HEAD/tree/index/worktree equality, and push/fetch remote verification.
- [ ] The new skill plus lightweight sweep, legacy inventory, drive-ingest, workspace knowledge-contract, and general llm-wiki descriptions route requests without overlap or dead ends.
- [ ] The #216 reference labels the existing implementation as repository- and corpus-specific and does not instruct agents to reuse it as a generic executable.
- [ ] The new skill links its neutral prior-art reference with an explicit load condition, remains bounded in size, and contains no scaffold placeholders.
- [ ] Focused tests pass and the intended red-first failure evidence is retained in the issue implementation comment.
- [ ] Fresh-agent forward tests select the archive profile for a broad top-folder corpus and deterministic adaptive depth with no default business-development join for an engineering/model corpus; negative prompts select lightweight stub, ordinary wiki, content extraction, or copy/migration routes instead.
- [ ] Fault prompts fail closed for source substitution/mutation, dirty index, branch switch, stale HEAD, ignored delivery path, missing tombstone, unowned current tree, staged-blob tampering, and coordinated journal/output tampering.
- [ ] `scripts/ai/build_skill_index.py` preserves legacy frontmatter/section/trigger precedence and legacy backfill weights, promotes only exact name+description/no-section modern skills, and the reviewed candidate/ranking baseline proves the bounded migration does not silently reroute the wider corpus.
- [ ] Delivery verification binds literal NUL-safe paths, A/M/D status, Git modes, blob OIDs, tombstones, scanned index tree, and final commit tree; unexpected/missing paths, pathspec magic, symlinks, gitlinks, executable drift, hook restaging, or OID changes fail before push.
- [ ] The lock-held integration test proves traps are armed before lock acquisition, the ownership token has an unpredictable per-attempt nonce resistant to PID reuse, candidate verification performs no index-writing Git command while `.git/index.lock` is owned, dirty-worktree and cached checks are separate fail-fast commands, rollback derives state from the observed ref across pre/post-CAS signals, rollback failure records the ref, and only the owned lock is removed before traps are disarmed.
- [ ] Push uses `${candidate}:${ref}` plus `--force-with-lease=${ref}:${head_before}`, never the mutable local ref as source; a local-ref race or lease conflict cannot publish an unscanned commit, and fetched local/remote refs plus the remote tree equal the verified candidate/scanned tree.
- [ ] Candidate creation re-verifies that no active commit hook exists; if an active hook appears, implementation stops for plan revision instead of silently bypassing it with `commit-tree`.
- [ ] `config/agents/skill-index-full.yaml` and `config/agents/codex/AGENTS.runtime.md` are regenerated deterministically; the new entry uses `when_to_use_source: description`, family counts match the live tree, index coherence passes, and soul-runtime drift is zero.
- [ ] Workspace skill tests, frontmatter validation, targeted and repo-wide no-absolute-path checks, equality-fenced staged/privacy checks, conflict-marker checks, Git diff checks, legal sanity scan, and T3 adversarial code/artifact review pass with at least two distinct provider verdicts; if provider availability cannot meet degraded T2 diversity, the review gate remains blocked.
- [ ] Candidate worktrees, locks, checkpoints, stages, journals, backups, and fresh-agent scratch receive explicit cleanup disposition.
- [ ] The implementation issue receives a summary comment with sources consumed and promotion candidates before close.
- [ ] Deterministic changed files plus an authoritative tracked-manifest/src/module-matrix package map drive `completeness_score.classify`; omitted/ambiguous/unmapped executable paths fail, and the derived code/evidence branch supplies all required inputs and reaches its threshold without caller-selected class.
- [ ] The matching completeness JSON/HTML artifacts pass exact-delivery, equality-fenced scans, targeted artifact review, commit/push, and remote verification; the owner, never the agent, applies `status:completeness-verified` before the close gate and issue closure.
- [ ] No Drive P or Models wiki notes, source copies, or source-body reads occur under this issue.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Codex parallel reviewer — skill lifecycle r1 | MAJOR | Omitted broad existing owners; trigger descriptions and generated-index behavior overlapped; self-enforcement, UI regeneration, runtime drift, progressive disclosure, and two-factor approval preflight were incomplete. |
| Codex parallel reviewer — privacy/transaction r1 | MAJOR | Private-root definition, volume/generation fencing, path-free journals, Windows collisions, deterministic adaptive coverage, ordered Git TOCTOU protocol, staged enforcement, and cleanup disposition were incomplete. |
| Codex parallel reviewer — skill lifecycle r2 | MAJOR | Approval commands were not compound fail-closed; generated tests ran before regeneration; description/body trigger duplication violated skill-creator; equality-fenced staged scans and full landing/completeness lifecycle were missing. |
| Codex parallel reviewer — privacy/transaction r2 | MAJOR | Control-plane relative-path leakage, candidate-commit/remote verification, scanner-incompatible sentinels, recovery-evidence cleanup, and T3 classification remained unresolved. |
| Codex parallel reviewer — skill lifecycle r3 | MAJOR | Global description promotion risk, weaker duplicate approval helper, missing staged delivery manifest, preselected completeness class, and unreviewed completeness artifacts remained. |
| Codex parallel reviewer — privacy/transaction r3 | MAJOR | Approval authority binding, fail-closed scan block, provider diversity, post-close cleanup, and committed/scanned OID equality remained. |
| Codex parallel reviewer — skill lifecycle r4 | MAJOR | Low-risk PR-gate SKIP, approval-gate file-size limit, commit/tree binding, non-gameable completeness map, literal pathspecs, and closeout review delivery remained. |
| Codex parallel reviewer — privacy/transaction r4 | MAJOR | Transaction-bound marker delivery, index Git modes, and fail-fast validation blocks remained unresolved. |
| Codex parallel reviewer — skill lifecycle r5 | MAJOR | POSIX-only approval bootstrap, optimization-strippable assertions, forgeable local marker evidence, mutable frozen-manifest instruction, and unfrozen 11-skill migration identities remained. |
| Codex parallel reviewer — privacy/transaction r5 | MAJOR | Canonical actor/freshness/binding proof, approval-evidence staging, frozen-manifest immutability, and scanned-index candidate-commit installation remained unresolved. |
| Codex parallel reviewer — skill lifecycle r6 | MAJOR | Missing approval-owner configuration, unbound local HEAD, self-blocking index lock verification, and removal of the still-mandatory approval marker remained. |
| Codex parallel reviewer — privacy/transaction r6 | MAJOR | Local/remote head binding, executable final gates, fail-fast locked checks, signal-safe rollback, rejected-push evidence, and hook bypass remained unresolved. |
| Codex parallel reviewer — skill lifecycle r7 | MAJOR | Forgeable Git-author marker provenance and missing local/index/HEAD/remote equality for approval-planning artifacts remained. |
| Codex parallel reviewer — privacy/transaction r7 | MAJOR | Pre-trap lock, post-CAS flag, pre-cleanup trap-disarm windows, and silent rollback CAS failure remained. |
| Codex parallel reviewer — skill lifecycle r8 | MAJOR | Masked `git status` failure and optional-lock index mutation remained in the read-only approval bootstrap. |
| Codex parallel reviewer — privacy/transaction r8 | MAJOR | Mutable-ref push source and PID-reusable lock ownership token remained. |
| Codex parallel reviewer — skill lifecycle r9 | APPROVE | Verified read-only status handling, authenticated marker provenance, exact four-view blob binding, frozen hashes, and skill/TDD lifecycle. |
| Codex parallel reviewer — privacy/transaction r9 | APPROVE | Verified nonce ownership, trap/rollback windows, read-only locked checks, immutable leased push, remote verification, and completeness closeout. |
| Claude CLI | UNAVAILABLE | The formal 600-second wrapper run and separate 300-second short path-only retry both returned no content; empty output is not review evidence. |
| Codex synthesis r9 | APPROVE | Two independent Codex axes reached APPROVE after eight incorporated MAJOR rounds; the named r9 artifacts provide the usable current verdict. |
| Gemini CLI r1 | UNAVAILABLE | No non-interactive Gemini authentication is configured on this machine. |

**Overall result:** Codex r9 APPROVE on both independent axes. Aggregate review remains blocked until a second distinct provider returns a non-MAJOR verdict; same-provider parallel reviewers do not satisfy degraded T2 diversity.

Revisions made based on review:

- Added `workspace-knowledge-doc-contracts` and general `llm-wiki` precedence routes and reconciled strict-catalog path minimization against generic pointer-page absolute paths.
- Made six frontmatter descriptions mutually exclusive and expanded the provider-neutral builder/router so canonical descriptions are authored triggers without duplicating “when to use” instructions in the body.
- Split pre-approval read-only intel from post-approval writes and added an authorized-label-plus-pushed-revision-binding implementation preflight.
- Added destination/private-root, ignored/untracked, reparse-ancestor, source-volume identity, three-fence, and mid-scan mutation contracts.
- Replaced agent-chosen adaptive scope with a versioned inclusion predicate, root/child denominators, and explicit representation states.
- Added exact-key path-free journal/checkpoint schemas, trusted-root reconstruction, journal hash binding, coordinated-tamper tests, and sanitized durable evidence.
- Added Windows case/Unicode/reserved-name/ADS/surrogate/traversal/UTF-16 safety across all write surfaces.
- Expanded the ordered Git transaction through index-authoritative manifest, ownership, detached candidate, candidate-blob scan, exclusive lock, post-lock rechecks, update-ref CAS/rollback, and final equality.
- Added `openai_yaml.md` read, post-edit UI regeneration, progressive-disclosure/scaffold tests, no-absolute-path self-enforcement, staged privacy checks, soul-runtime drift, and explicit cleanup disposition.
- Replaced the body-trigger compatibility workaround with a tested systemic builder/router rule that treats canonical descriptions as authored triggers and reserves penalty for true no-description backfill.
- Made the approval shell block compound fail-closed and added a reusable, TDD-covered canonical authority/binding helper for future runs.
- Reordered full green tests after UI/index/runtime regeneration.
- Added the artifact-class path matrix, trustworthy source stability evidence, candidate-commit/single-parent/tree/payload verification, remote push/fetch verification, and reflog-first rejected-push handling.
- Bracketed working-tree scanners with index/worktree equality plus `git write-tree` before/after fences; legal-deny tests will use synthetic deny lists because the legal scanner has no generic sentinel.
- Added failure-state cleanup preservation, pre-existing-lock ownership checks, immutable evidence exclusions, and completion-blocking residue rules.
- Reclassified the systemic cross-provider scope as T3 and added post-review restage/scan, detached candidate commit plus CAS installation, remote verification, issue comment, evidence completeness HTML, owner-only verification, and close verification.
- Limited description promotion to audited exact name+description/no-section skills, preserved all legacy precedence/weights, and added a per-candidate ranking baseline.
- Removed the weaker parallel approval helper; added a local mode to the canonical actor/freshness/revision-binding gate while retaining the existing PR gate as this issue's bootstrap preflight.
- Added exact phased delivery manifests, NUL pathspec staging, index-blob/tombstone verification, branch/HEAD/tree fences, and omitted/unexpected path tests.
- Made every scan block compound fail-closed and required two distinct providers even under degraded T2 review; same-provider agents are depth only.
- Made completeness class auto-derived from persisted changed-file/package-map inputs and added equality-fenced scans plus targeted artifact review for the JSON/HTML closeout commit.
- Added post-close cleanup audit and explicit committed-blob-OID equality with the already-scanned candidate manifest.
- Replaced the Windows-incompatible local transaction/marker bootstrap with direct read-only composition of the canonical authorized-human label event, freshness, pushed plan-revision binding, PR-head blob equality, and frozen planning-artifact hashes.
- Moved local approval verification into a bounded companion that imports the canonical gate instead of overflowing or weakening the 397-line canonical file.
- Pre-created and hash-bound the exact three-phase delivery manifest before approval; added literal pathspecs, index modes, symlink/gitlink/executable tests, and scanned-tree-to-commit verification.
- Added authoritative completeness-input derivation from tracked manifests/src roots/fixed non-package prefixes/HEAD-bound matrix with omitted/ambiguous/unmapped executable-path failure.
- Made validation/generation/test blocks fail-fast and added closeout review evidence to the exact reviewed/scanned closeout set.
- Pre-created and hash-bound the exact 11-skill routing baseline; kept it outside the post-approval implementation delta and restored the mandatory user-authored approval marker as a verified parent-commit witness.
- Replaced optimization-strippable assertions with explicit fail-closed decisions, required the same behavior under `PYTHONOPTIMIZE=1`, and made the frozen manifest immutable throughout implementation.
- Replaced pathspec commit with a verified `commit-tree` candidate, ownership-marked exclusive index lock, `update-ref` CAS install/rollback, and remote commit/tree equality.
- Froze the issue-specific approval owner after live account-type verification, bound a clean local branch/HEAD to the approved PR head, and restored the mandatory marker as an exact user-authored GitHub commit witness.
- Made the marker the direct-child PR-head commit containing only the `100644` marker path, then bound exact bytes, commit actor/pushed time, label freshness, plan revision, tree/blob, and local checkout.
- Replaced lock-held `write-tree` with read-only index-byte/OID/mode checks, added a lock-held integration test, expanded the actual final scanner commands, hardened signal/error rollback, diagnosed push rejection, and failed closed on newly active commit hooks.
- Required an authenticated `committedViaWeb` owner marker with valid GitHub/web-flow signature and added forged-author/pusher negative coverage.
- Bound normal index flags, `100644` mode, raw local bytes, index OID, local HEAD OID, and remote PR-head OID for the plan, marker, delivery manifest, and routing baseline.
- Armed rollback before lock acquisition, derived rollback from the observed ref across signal windows, reported CAS/ref conflicts, and cleaned only the owned lock before disarming traps.
- Made approval status enumeration separately fail-fast under `GIT_OPTIONAL_LOCKS=0` and added no-index/no-lock-mutation coverage.
- Added an unpredictable per-attempt lock nonce and changed push to immutable `${candidate}:${ref}` with exact `${head_before}` remote lease plus local/remote post-verification.

---

## Risks and Locked Decisions

- **Locked — canonical location:** The skill will live under `.claude/skills/workspace-hub/` because the workspace contract makes the repo-tracked control plane authoritative and the user wants reuse across future sessions/providers. It will not be stranded in a machine-local personal skill directory.
- **Locked — one new skill:** The change will create one focused skill and five bounded routers. It will not expand overlapping legacy or broad wiki skills into competing owners.
- **Locked — procedure before parameterization:** This issue will distill the proven workflow but will not generalize or copy the Drive-J-specific generator. The current generator source set is part of the committed Drive J generator hash and ownership/ledger evidence; editing it would invalidate candidate verification unless Drive J were deliberately migrated and republished. Downstream work will therefore use a separately hashed/configured implementation or a separately approved Drive J migration plan.
- **Locked — delivery set before approval:** The three-phase delivery manifest is a planning artifact bound by the approved plan's embedded SHA-256. Implementation may not expand it; any required path/status/mode change will return the issue to plan review and user re-approval.
- **Locked — approval owner:** The only approval actor authorized by this plan is repository owner `vamseeachanta`, verified by GitHub as account type `User`. The nonexistent `PLAN_APPROVAL_OWNERS` repository variable will not be assumed, and the separate completeness-owner variable will not be reused for plan approval.
- **Risk — prose-only drift:** Content-contract tests and generated-index checks will make the fragile requirements executable enough to catch omission without treating exact paragraph wording as an API.
- **Risk — security backdoor by example:** The reference will use logical placeholders and narrow forensic sentinels. It will not embed absolute machine paths, client identifiers, secrets, or blanket file exemptions that would weaken its own scanners.
- **Risk — fresh-agent false confidence:** Forward-test prompts will require explicit decisions and defect hunting; an unreasoned “looks good” result will not count as evidence.
- **Downstream sequencing:** Drive P will receive a child issue under llm-wiki-acma #208 only after this skill is finished. Models will revise and continue existing llm-wiki-acma #214 rather than create a duplicate issue.

---

## Complexity: T3

**T3** — one new canonical cross-provider skill, a bounded provider-neutral index/router correction, a canonical approval-gate local mode, exact delivery-manifest enforcement, five existing-owner routing edits, two generated control-plane indexes, security-sensitive source/publication contracts, and multi-scenario fresh-agent tests. Provider outages may degrade the available review wave, but they do not reduce implementation risk classification.
