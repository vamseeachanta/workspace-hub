# Client LLM-Wiki Feature + ACMA Instance — Design Spec

> **Date:** 2026-05-20
> **Issues:** [#2744](https://github.com/vamseeachanta/workspace-hub/issues/2744) (epic), [#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746) + [#2745](https://github.com/vamseeachanta/workspace-hub/issues/2745) (paired plan target), [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) + [#2732](https://github.com/vamseeachanta/workspace-hub/issues/2732) (governance contract — seed)
> **Status:** Brainstorming spec — pending user review before handoff to `superpowers:writing-plans`.
> **Author session:** Claude main, 2026-05-20.
> **Brainstorming skill version:** superpowers 5.1.0.

## 1. Context

The repo ecosystem maintains a public knowledge wiki at `vamseeachanta/llm-wiki` (MIT + CC-BY-4.0, spun out 2026-05-05 per [`feedback_llm_wiki_spunout`](../../../.claude/memory/topics/feedback_llm_wiki_spunout.md)). Client-derived knowledge cannot land there — it requires a separate private layer per client. [#2744](https://github.com/vamseeachanta/workspace-hub/issues/2744) is the epic that decided this, with four children:

- [#2745](https://github.com/vamseeachanta/workspace-hub/issues/2745) — freeze `acma-projects` and move to local-only archive posture
- [#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746) — create private llm-wiki repo target `llm-wiki-acma`
- [#2747](https://github.com/vamseeachanta/workspace-hub/issues/2747) — raw-to-private-wiki promotion ledger with completion confidence scoring
- [#2748](https://github.com/vamseeachanta/workspace-hub/issues/2748) — client output scaffolding for reports / chatbots / evidence packs

The acma child #2746 was bootstrapped on 2026-05-18: PRIVATE GitHub repo `vamseeachanta/llm-wiki-acma` created, initial scaffold pushed (5 files, 2 commits). No client-derived content has been added. Today (2026-05-20) the raw client root was moved to `/mnt/ace/acma-projects/` with a `.preexisting-before-repo-move-*` backup sibling (~1.8 TB).

Mid-brainstorming scope expanded: the user surfaced that *several clients* and *several raw-data sources* need this same pattern. Loading the data-governance issues revealed that [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) already enumerates the planned wiki set:

```
llm-wiki-rock-oil-field, llm-wiki-client-projects, llm-wiki-doris,
llm-wiki-acma, llm-wiki-frontierdeepwater, llm-wiki-saipem     (6 wikis, acma is instance #1)
```

So this spec covers a **reusable feature** (template + skill + registry + checker) instantiated first for `acma`. Sequencing is parallel to [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731), not blocked by it: we plan against [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731)'s seed decisions D1–D8 and ratify against the final contract at user-approval time.

## 2. Objective + non-goals

### Objective

Deliver the repeatable mechanism for instantiating per-client private llm-wiki repos that conform to [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) D1–D8 and [#2732](https://github.com/vamseeachanta/workspace-hub/issues/2732) classification, with `acma` as the first invocation:

1. A **template tree** with `<client>` placeholders for repo bootstrap.
2. A **coordination skill** (`coordination/client-llm-wiki-factory`) that walks an operator through instantiation.
3. A **machine-readable registry** (`config/client-wikis.yml`) listing the 6 known target wikis, their raw roots, posture flags, and current status — proposed as a concrete instance of [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) deliverable #3.
4. A **checker** (`scripts/enforcement/check-client-wiki-registry.sh`) that validates the registry against on-disk and GitHub reality.
5. The **acma instance** ([#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746)) ratified against the new contract; existing scaffold preserved.
6. The **acma-projects freeze** ([#2745](https://github.com/vamseeachanta/workspace-hub/issues/2745)) executed: archive `vamseeachanta/acma-projects` GitHub remote read-only; preserve local raw archive.

### Non-goals (out of scope for this spec)

- Public `llm-wiki` changes (separate roadmap).
- The promotion-ledger schema beyond the existing example file — that's [#2747](https://github.com/vamseeachanta/workspace-hub/issues/2747)'s problem.
- Client-facing reports, chatbots, evidence packs — that's [#2748](https://github.com/vamseeachanta/workspace-hub/issues/2748).
- Importing any raw client material into `llm-wiki-acma` — explicitly deferred to a post-approval phase.
- Settling [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731)/[#2732](https://github.com/vamseeachanta/workspace-hub/issues/2732) themselves — we feed concrete-instance evidence into them; we do not own them.
- Generator script (operator-driven instantiation per design choice; see §4).
- Other 5 wiki instances (rock-oil-field, client-projects, doris, frontierdeepwater, saipem) — these are Phase 3 follow-ons, filed as new issues post-acma.

## 3. Constraints inherited from governance layer

The spec MUST conform to:

| Source | Constraint | Application here |
|---|---|---|
| [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) D1 | `/mnt/ace` is canonical; `/mnt/ace-data` is alias only | All raw-root paths use `/mnt/ace/<bucket>/` (heterogeneous per registry: `acma-projects`, `doris`, `saipem`, `frontierdeepwater`, `rock-oil-field`, `client_projects`) |
| [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) D2 | Active repo checkouts under `/mnt/local-analysis/<repo>` | Working clone landed at `/mnt/local-analysis/llm-wiki-acma/` ✓ |
| [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) D3 | Raw/client/source/bulk data stays under `/mnt/ace/<bucket>` | `/mnt/ace/acma-projects/` is the raw root |
| [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) D4 (**amendment proposed**) | D4 currently states `/mnt/local-analysis/<client>-llm-wiki/`; **spec proposes amendment to `/mnt/local-analysis/llm-wiki-<client>/`** for agentic-ecosystem glob symmetry with public `/mnt/local-analysis/llm-wiki/` (see §3.1 below). GH repo already renamed: `vamseeachanta/llm-wiki-acma` (PRIVATE, `main`, 2 commits, not archived). |
| [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) D7 | `/mnt/ace/llm-wiki`-likes need classification | Includes `/mnt/ace/llm-wiki-acma` — disposition pending in §5 |
| [#2732](https://github.com/vamseeachanta/workspace-hub/issues/2732) classification | "Private client llm-wiki repo" class defined | This feature populates that class |
| [#2727](https://github.com/vamseeachanta/workspace-hub/issues/2727) (closed) | Data layer boundary model | Raw → readable → private wiki → reviewed/sanitized → public is the only allowed flow |
| `SHARED_SOUL.md` must-fire rules | Plan gate, TDD, legal-sanity scan, no self-approval, adversarial review | All apply to the implementation plan; this spec is pre-plan |
| `.claude/rules/calc-citation-contract.md` | Citation sidecar for standards-derived constants | N/A this spec (no standards constants) but applies to any future calc that consumes private wiki content |
| `.claude/rules/coding-style.md` | No absolute paths in scripts | Checker script will use `$(git rev-parse --show-toplevel)` |
| `.claude/rules/patterns.md` | Enforcement gradient | Registry checker starts at Level 2 (script); may promote to Level 3 (pre-commit hook) in a later issue |
| `feedback_per_repo_metadata_is_firewall` | Firewall = LICENSE + .gitignore + per-repo `.claude/` + `.git/` | Template MUST include LICENSE selection (private, no public license) + .gitignore guarding raw paths + private-flavored `.claude/CLAUDE.md` if any |
| `feedback_html_default_artifact` | HTML default for human-facing artifacts | Wiki pages produced from this template are HTML by default; this spec stays markdown (governance-layer convention) |
| `feedback_ntfs3_symlink_intxlnk` | NTFS3 corrupts git symlinks | Working clones must live on ext4 (`/mnt/local-analysis/`); NTFS-backed `/mnt/ace/` is raw-only |

### 3.1 Naming convention — `llm-wiki-<client>` (amendment to [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) D4)

**Rule:** Per-client private wiki repos are named `llm-wiki-<short-name>` and live at `/mnt/local-analysis/llm-wiki-<short-name>/`. The public knowledge wiki at `/mnt/local-analysis/llm-wiki/` is the family root; private per-client siblings carry a suffix.

**Rationale (agentic-ecosystem ergonomics):**

1. **Single-glob family enumeration.** `llm-wiki*` matches the public wiki AND all per-client siblings. The reversed `*-llm-wiki` form requires two globs (per-client + the bare public name).
2. **Directory-listing clustering.** In any sorted `ls /mnt/local-analysis/`, all wikis cluster as `llm-wiki`, `llm-wiki-acma`, `llm-wiki-doris`, … visibly forming a family.
3. **Skill convention alignment.** Existing skills already use `llm-wiki-*` as a prefix (`coordination/llm-wiki-roadmap-integration`, `workspace-hub-learned/llm-wiki-ecosystem-gap-to-issues`). Repo names follow skill prefix conventions.
4. **`gh search repos owner:vamseeachanta llm-wiki`** returns the full family in a single clean filter.
5. **Future-proofing.** Non-client llm-wikis (e.g., `llm-wiki-standards`, `llm-wiki-public-research`) extend the family naturally.

**State of the amendment ([#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) D4):** the current D4 text in [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731)'s body says `<client>-llm-wiki`. This spec proposes the reversal to `llm-wiki-<client>`. A follow-up comment on [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) carries the proposal and links to this spec section. Operational state already reflects the new rule:

- GH repo: `vamseeachanta/acma-llm-wiki` → renamed to `vamseeachanta/llm-wiki-acma` on 2026-05-20 (PRIVATE preserved; GitHub URL-redirect active for ~1 year).
- Local working clone: `/mnt/local-analysis/acma-llm-wiki/` → renamed to `/mnt/local-analysis/llm-wiki-acma/` with `git remote set-url`.
- NTFS-backed `/mnt/ace/acma-llm-wiki/` → renamed to `/mnt/ace/llm-wiki-acma/` (disposition still per §5.1).

**6-wiki target list under the amended rule:**

```
llm-wiki-acma                  (instance #1; renamed 2026-05-20)
llm-wiki-rock-oil-field
llm-wiki-client-projects       (raw root: /mnt/ace/client_projects/, underscore per #2731 D5)
llm-wiki-doris
llm-wiki-frontierdeepwater     (raw root: /mnt/ace/frontierdeepwater/, no hyphen per #2731 D6)
llm-wiki-saipem
```

## 4. Architecture (Approach B)

Four artifacts, no generator script. Operator runs the skill as a checklist.

```
workspace-hub/
├── templates/
│   └── client-llm-wiki/                         (NEW — fixture tree)
│       ├── README.md                            (with <CLIENT_SHORT_NAME> placeholders)
│       ├── DATA-CYCLE.md                        (lifted from acma scaffold; client-agnostic)
│       ├── LICENSE                              (private/proprietary marker — not OSS license)
│       ├── .gitignore                           (blocks /raw, /private, large binary patterns)
│       ├── .claude/CLAUDE.md                    (private-posture override; no public-llm-wiki cross-refs)
│       ├── sources/README.md                    (placeholder)
│       ├── pages/README.md                      (placeholder)
│       ├── reports/README.md                    (placeholder)
│       ├── ledgers/
│       │   ├── promotion-ledger.example.yml     (schema template; client to clone to dated file)
│       │   └── README.md                        (ledger usage)
│       └── REDACTION-POSTURE.md                 (per-client redaction rules; defaults provided)
├── config/
│   └── client-wikis.yml                         (NEW — machine-readable registry of 6 wikis)
├── scripts/
│   └── enforcement/
│       └── check-client-wiki-registry.sh        (NEW — validates registry against reality)
└── .claude/skills/coordination/
    └── client-llm-wiki-factory/
        └── SKILL.md                             (NEW — operator checklist for instantiating)
```

### 4.1 `templates/client-llm-wiki/`

Source-of-truth directory tree with `<CLIENT_SHORT_NAME>` placeholders. Operator copies into the new client repo, runs placeholder substitution, commits. Tree mirrors the existing acma scaffold with three additions: a `LICENSE` file marking proprietary status, a `.gitignore` blocking raw-data leakage paths, and a `REDACTION-POSTURE.md` documenting per-client redaction defaults.

### 4.2 `config/client-wikis.yml`

Machine-readable registry. Schema (initial draft — final field set to be reviewed against [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) deliverable #3):

```yaml
registry_version: 0.1
wikis:
  - short_name: acma
    repo: vamseeachanta/llm-wiki-acma
    visibility: PRIVATE
    raw_roots:
      - /mnt/ace/acma-projects/
    archived_raw_remotes:
      - vamseeachanta/acma-projects        # frozen per #2745, post-approval
    local_working_clone: /mnt/local-analysis/llm-wiki-acma/
    secondary_clone: /mnt/ace/llm-wiki-acma/      # legacy NTFS — disposition TBD
    posture: client-private
    status: bootstrapped                          # bootstrapped | live | retired
    instantiated_at: 2026-05-18
    notes: "Instance #1. Scaffold only; no client-derived content."

  - short_name: rock-oil-field
    repo: vamseeachanta/llm-wiki-rock-oil-field
    visibility: PRIVATE
    raw_roots: [/mnt/ace/rock-oil-field/]
    posture: client-private
    status: planned

  - short_name: client-projects
    repo: vamseeachanta/llm-wiki-client-projects
    visibility: PRIVATE
    raw_roots: [/mnt/ace/client_projects/]       # note: underscore per #2731 D5
    posture: client-private
    status: planned

  - short_name: doris
    repo: vamseeachanta/llm-wiki-doris
    visibility: PRIVATE
    raw_roots: [/mnt/ace/doris/]
    posture: client-private
    status: planned

  - short_name: frontierdeepwater
    repo: vamseeachanta/llm-wiki-frontierdeepwater
    visibility: PRIVATE
    raw_roots: [/mnt/ace/frontierdeepwater/]    # note: no hyphen per #2731 D6
    posture: client-private
    status: planned

  - short_name: saipem
    repo: vamseeachanta/llm-wiki-saipem
    visibility: PRIVATE
    raw_roots: [/mnt/ace/saipem/]
    posture: client-private
    status: planned
```

### 4.3 `scripts/enforcement/check-client-wiki-registry.sh`

Validates the registry against runtime state. Exit non-zero on any of:

- `repo` exists on GitHub AND `visibility` matches AND `isArchived=false` for non-retired entries
- `raw_roots[*]` exist on disk (when machine is `ace-linux-1` or has the mount)
- `local_working_clone` exists AND is a git repo AND remote matches `repo`
- `short_name` is unique
- For `posture: client-private`, no entry's `raw_roots` contains a public llm-wiki path

Promotion to pre-commit hook (Level 3 in `.claude/rules/patterns.md`) deferred to a follow-on issue.

### 4.4 `.claude/skills/coordination/client-llm-wiki-factory/SKILL.md`

Operator checklist with the following ordered steps:

1. Read `config/client-wikis.yml` to confirm target `short_name` is `status: planned` (not already live).
2. Confirm raw root exists at `/mnt/ace/<short_name>` (or registered alternate) per [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) D3.
3. Run `gh repo create vamseeachanta/<short_name>-llm-wiki --private --description "Private client llm-wiki for <short_name>"`.
4. `git clone` to `/mnt/local-analysis/llm-wiki-<short_name>/`.
5. Copy template tree from `workspace-hub/templates/client-llm-wiki/`.
6. Substitute `<CLIENT_SHORT_NAME>` placeholders (sed / manual).
7. Review `REDACTION-POSTURE.md` for client-specific redaction additions.
8. Initial commit (CLAUDE.md sealed; not amended on push); push.
9. Update `config/client-wikis.yml` to `status: bootstrapped`.
10. Run `scripts/enforcement/check-client-wiki-registry.sh` — must pass.
11. Comment on the parent client-wiki issue with the wiki URL + scaffold commit SHA.

No automation; every step is operator-visible. Per the brainstorming skill HARD-GATE, this skill is **invoked only after the implementation plan ([#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746)) is `status:plan-approved` by the user**.

## 5. ACMA instance specifics ([#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746) + [#2745](https://github.com/vamseeachanta/workspace-hub/issues/2745))

### 5.1 llm-wiki-acma ([#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746)) — ratify scaffold + lock posture

The repo exists with bootstrap commits. Implementation plan will:

1. Reconcile existing `llm-wiki-acma` scaffold against the template tree from §4.1. Specifically: add missing `LICENSE`, `.gitignore`, `.claude/CLAUDE.md`, and `REDACTION-POSTURE.md`. Existing files (`README.md`, `DATA-CYCLE.md`, `ledgers/promotion-ledger.example.yml`) stay as-is — they were the seed for the template.
2. Register acma in `config/client-wikis.yml` (in workspace-hub).
3. Run the checker to confirm acma row passes.
4. Dispose of secondary NTFS clone at `/mnt/ace/llm-wiki-acma/`: **delete after confirming `/mnt/local-analysis/llm-wiki-acma/` is fully synced** (rationale: per `feedback_ntfs3_symlink_intxlnk`, the NTFS clone is a hazard, not a backup; the GitHub remote is the durable backup).
5. Add an acceptance criterion to **ratify the spec against [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) final contract** once that issue lands `status:plan-approved`. If [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) shifts D4 (the naming rule) or D5/D6 (path normalizations), file a reconciliation issue.

No raw-data import in this issue's scope. Promotion-ledger is [#2747](https://github.com/vamseeachanta/workspace-hub/issues/2747).

### 5.2 acma-projects freeze ([#2745](https://github.com/vamseeachanta/workspace-hub/issues/2745)) — archive GH remote + keep local 1.8 TB

The freeze posture (per locked decision):

1. **GitHub side:** `gh repo archive vamseeachanta/acma-projects` makes the remote read-only; preserves history and URL refs; reversible if needed. Add a `STATUS-FROZEN.md` note in the local working copy explaining the freeze for any operator who looks at the local repo.
2. **Local working copy:** `/mnt/ace/acma-projects/` (~73 GB, git-tracked) remains as a read-mostly local archive. Optionally remove `origin` push permissions in local config to belt-and-suspenders the freeze.
3. **Pre-move backup:** `/mnt/ace/acma-projects.preexisting-before-repo-move-20260520-075928/` (~1.8 TB) — disposition needs explicit decision in the implementation plan. Three reasonable options to surface there: (a) retain indefinitely as historical archive, (b) checksum + tar to slower bulk storage, (c) inventory + selective deletion of files now redundant with `/mnt/ace/acma-projects/`. Deferred to plan-draft time.
4. No deletion or compression touches `/mnt/ace/acma-projects/` itself in this issue's scope.

## 6. Privacy firewall + redaction posture

This is the load-bearing safety surface. Per `feedback_per_repo_metadata_is_firewall`, the firewall is enforced by per-repo metadata, not file-system distance.

### 6.1 Template-level defaults (every client wiki gets these)

- `LICENSE`: proprietary marker; explicitly NOT an OSS license; copyright vamseeachanta; "all rights reserved; private client knowledge"
- `.gitignore`: blocks common raw-data leakage patterns — `raw/`, `private/`, `*.dwg`, `*.sim`, `*.dat` over 10 MB (LFS only with manual approval), credentials patterns
- `.claude/CLAUDE.md` (private-posture override): refers to per-repo redaction rules; flags that this repo is NEVER public-eligible; forbids cross-repo promotion to public `llm-wiki` without explicit operator-driven sanitization
- `REDACTION-POSTURE.md`: per-client redaction rules — defaults for client legal name, project IDs (B-numbers etc.), personal names, geographic coordinates, vessel names, financial figures. Each entry has a default action (REDACT / KEEP / FLAG-FOR-REVIEW).

### 6.2 Promotion gate (from raw → wiki → public)

Per existing `DATA-CYCLE.md` (already in acma scaffold) and [#2727](https://github.com/vamseeachanta/workspace-hub/issues/2727) (closed):

```
raw source → readable derivative → private client wiki → reviewed/sanitized derivative → public llm-wiki (if appropriate)
```

Every transition requires a ledger entry (schema in [#2747](https://github.com/vamseeachanta/workspace-hub/issues/2747)). The checker from §4.3 enforces *registry* integrity; ledger enforcement is [#2747](https://github.com/vamseeachanta/workspace-hub/issues/2747)'s scope.

### 6.3 What this spec does NOT enforce

- Content-level redaction at promotion time (that's [#2747](https://github.com/vamseeachanta/workspace-hub/issues/2747)).
- Runtime retrieval boundaries (chatbot must-not-cross-firewall) — that's [#2748](https://github.com/vamseeachanta/workspace-hub/issues/2748).
- Public llm-wiki content gating — already governed by the public repo's own LICENSE + CC-BY-4.0 stance.

## 7. TDD / checker plan

Aligned with [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731)'s "TDD expectations" section. Tests/checkers MUST be written before implementation per the SOUL hard gate.

| Test | Expected behavior |
|---|---|
| `check-client-wiki-registry.sh` passes when registry is consistent | Exit 0; no output to stderr |
| `check-client-wiki-registry.sh` fails when `repo` doesn't exist on GH | Exit non-zero with message naming the offending `short_name` |
| `check-client-wiki-registry.sh` fails when `visibility != PRIVATE` for `client-private` posture | Exit non-zero |
| `check-client-wiki-registry.sh` fails when `local_working_clone` is missing | Exit non-zero (machine-aware: skip when path mount not present on current host) |
| `check-client-wiki-registry.sh` fails on duplicate `short_name` | Exit non-zero |
| `check-client-wiki-registry.sh` fails when a `client-private` entry's `raw_roots` matches a public llm-wiki path | Exit non-zero (firewall guard) |
| Path classifier (future, aligned with [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) TDD) maps `/mnt/local-analysis/llm-wiki-<client>` to "Private client llm-wiki repo" class | Exit 0 |
| Template substitution leaves no `<CLIENT_SHORT_NAME>` placeholders | grep returns 0 hits in instantiated repo |
| `LICENSE` in instantiated repo does NOT contain OSS license keywords | grep -i for "MIT", "Apache", "BSD", "CC-BY" returns 0 hits |

Tests live at `tests/enforcement/test_client_wiki_registry.sh` (or `tests/enforcement/test_client_wiki_registry.py` if Python is more ergonomic). Implementation plan will pick the framework.

## 8. Rollout phases

| Phase | Scope | Issue(s) | Gates |
|---|---|---|---|
| **Phase 1 — Feature foundation** | template/, config/client-wikis.yml, checker script, factory skill | [#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746) (drives the feature) | Plan-approved → TDD → impl → adversarial review → close |
| **Phase 2 — acma instance ratification** | Reconcile existing scaffold; register; dispose NTFS clone | [#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746) (continued in same plan) | Same gates |
| **Phase 3 — acma-projects freeze** | Archive GH remote; freeze local | [#2745](https://github.com/vamseeachanta/workspace-hub/issues/2745) | Separate plan (paired in spec, separate per-issue plans per `issue-planning-mode`) |
| **Phase 4 — second-wiki validation** | Instantiate one more from the list (e.g., `llm-wiki-saipem` or `llm-wiki-doris`) | New follow-on issues, parent [#2744](https://github.com/vamseeachanta/workspace-hub/issues/2744) | Tests the factory; not in this spec's plan |
| **Phase 5 — remaining 4 wikis** | Roll out rock-oil-field, client-projects, doris/saipem (whichever Phase 4 didn't pick), frontierdeepwater | New follow-on issues | Routine factory invocation |

Phases 1–3 are the deliverables of [#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746) + [#2745](https://github.com/vamseeachanta/workspace-hub/issues/2745). Phases 4–5 are explicitly **deferred** to new issues after acma lands.

## 9. Risks + mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) D-decision shifts at user-approval time, invalidating our registry schema | Medium | Medium | Acceptance criterion: ratify against final [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) contract; registry is a draft until [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) lands |
| Operator typo during factory invocation leaks raw data into wiki | Low (with checker) | High (NDA breach) | Checker + adversarial review per instance; LICENSE + .gitignore + posture override at template level |
| Naming drift across the 6 wikis (e.g., next operator picks `<client>-llm-wiki` reverting the convention, or `llm-wiki-<client>-projects` re-introducing the source-bucket suffix) | Medium | Low | Registry is the canonical name source; checker rejects unregistered repos; spec §3.1 documents the `llm-wiki-<client>` rule with rationale |
| NTFS-backed `/mnt/ace/llm-wiki-acma/` clone diverges from ext4 clone, creating split-brain | Low (after disposition) | Medium | Phase 2 deletes the NTFS clone after ext4 sync confirmed |
| Adversarial review surfaces firewall defect that requires re-template | Low–Medium | Medium | T2 adversarial review at plan AND code stage; defect-class promotion to `.claude/rules/` if generalizable per `SHARED_SOUL.md` |
| The 1.8 TB backup `/mnt/ace/acma-projects.preexisting-*` runs out of disk room | Medium | Medium | [#2745](https://github.com/vamseeachanta/workspace-hub/issues/2745) plan must decide disposition (retain / tar / selective delete); not silently leave |
| Multi-session race lands conflicting changes to `config/client-wikis.yml` | Medium | Low | Per `feedback_multi_agent_commit_serialization`, use `git commit -m "..." -- config/client-wikis.yml` pathspec form |

## 10. Open questions deferred to implementation plan

These are deliberately deferred — they need plan-stage analysis, not spec-stage decision:

1. **Tests language:** shell vs Python for the registry checker. Likely shell for portability; Python if YAML parsing complexity warrants.
2. **Where does the template's `.claude/CLAUDE.md` live?** Inside the template (and copied verbatim) vs symlinked to a shared private-posture base. Plan to evaluate.
3. **Disposition of `/mnt/ace/acma-projects.preexisting-before-repo-move-*` 1.8 TB backup.** Three options per §5.2; plan picks one.
4. **Disposition of `/mnt/ace/llm-wiki-acma/` NTFS clone:** spec says delete after sync confirmed; plan to verify "sync confirmed" criteria.
5. **Should `client-wikis.yml` live in `config/` or `config/data-governance/`?** Path will reconcile with [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731)'s deliverable #3 final path.
6. **Pre-commit hook promotion** of the checker — defer to a follow-on issue (Level 3 per `patterns.md`); spec leaves the hook out of [#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746)'s scope.
7. **Implementation-notes.html running file** requested in [#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746)'s second comment (running design-decision log) — plan to commit to this format.

## 11. Acceptance criteria for THIS SPEC (not the plan)

This spec is accepted when:

- User has read this file and confirmed (or requested changes to) all sections.
- No `TBD` placeholders remain in §§ 4, 5, 6, 7.
- No internal contradictions (verified by self-review pass).
- Spec is committed to `docs/governance/` and an update comment is posted to [#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746) linking this spec.
- Next-step skill (`superpowers:writing-plans`) is the only thing invoked after acceptance; no implementation skill fires.

## 12. Skill manifest for the implementation plan

Required by-stage (must-fire bold; recommended italic; ✗ excluded):

**Stage A — Pre-plan:** **`superpowers:writing-plans`**, **`coordination/issue-planning-mode`** (twice: once per child issue).

**Stage B — Discovery (light, scoped to changes):** *`coordination/knowledge-source-recon`* (if any unknowns surface about `/mnt/ace/acma-projects/` 73 GB content disposition).

**Stage C — Plan drafting:** **`coordination/legal-sanity-scan`** before any commit; **`coordination/llm-wiki-roadmap-integration`** (private-tier override).

**Stage D — Adversarial review:** **`coordination/cross-review-policy`** (T2 default — Claude + Codex; Gemini optional given recent quota volatility per `feedback_cross_provider_review_payoff`); **`coordination/agent-work-adversarial-review`**; *`workspace-hub-learned/iterative-plan-hardening-with-adversarial-waves`* (if review surfaces sustained defects).

**Stage E — Execution (after user approval):** **`coordination/pre-completion-cleanup-audit`** before declaring done; *`coordination/parallel-plan-drafting-worktrees`* (if [#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746) and [#2745](https://github.com/vamseeachanta/workspace-hub/issues/2745) are landed in parallel worktrees per `feedback_parallel_agent_write_only_pattern`).

**Cross-cutting must-fire rules:** never self-label `status:plan-approved`; check parallel work before each commit; discovery-first if any preexisting state surfaces.

**Excluded (not applicable):** `superpowers:frontend-design`, `mcp-builder`, `coordination/repo-portfolio-steering`, any wiki-content-curation skill (this spec is structure, not content).

---

## Self-review pass (run by author before user gate)

- [x] Placeholder scan: no `TBD` / `TODO` / `(fill in)` in §§ 4–7.
- [x] Internal consistency: §4 architecture matches §8 phases; §5 acma specifics match §4 template; §7 tests cover §4.3 checker behaviors.
- [x] Scope check: spec covers feature foundation + acma instance only. Phases 4–5 explicitly deferred. Adjacent issues ([#2747](https://github.com/vamseeachanta/workspace-hub/issues/2747), [#2748](https://github.com/vamseeachanta/workspace-hub/issues/2748)) named as non-goals.
- [x] Ambiguity check: every "deferred to plan" item in §10 is labeled as such; no ambiguous "should we" left for the plan to discover.
- [x] Legal sanity: no client legal names, no project numbers (B-codes), no credentials, no PII. All short-labels used (acma, doris, saipem, etc.) already appear in [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) public body.
- [x] Brainstorming HARD-GATE: no implementation skill invoked; no feature artifacts created (`templates/`, `config/client-wikis.yml`, `scripts/enforcement/check-client-wiki-registry.sh`, `coordination/client-llm-wiki-factory/SKILL.md` all absent). External-state actions taken under the user's explicit naming-convention authorization: GH repo rename `vamseeachanta/acma-llm-wiki` → `vamseeachanta/llm-wiki-acma`, local clone renames at `/mnt/local-analysis/` and `/mnt/ace/`, remote-URL updates, and two [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) comments (initial status update + D4-amendment proposal). All reversible.
- [x] Rename naming-amendment coherence: GH state, local-clone state, spec §3.1 rationale, [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) D4-amendment comment, and registry example in §4.2 all consistently use `llm-wiki-<client>`.

---

**Next:** user reviews this file. On approval, invoke `superpowers:writing-plans` to produce per-issue plans at `docs/plans/2026-05-20-issue-2746-llm-wiki-acma.md` + `docs/plans/2026-05-20-issue-2745-acma-projects-freeze.md` per `docs/plans/_template-issue-plan.md`.
