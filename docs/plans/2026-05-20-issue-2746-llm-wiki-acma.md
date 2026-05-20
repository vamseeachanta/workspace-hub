# Plan for #2746: create private llm-wiki repo target llm-wiki-acma

> **Status:** draft (r1 + r2 review applied; r2-codex MAJOR resolved inline)
> **Complexity:** T2
> **Date:** 2026-05-20
> **Revision history:**
> - 2026-05-20 r1-claude — MINOR; blockers 1/2/3 (TDD fixture design, factory-skill step 9 commit semantics, NTFS sync verification depth) resolved inline
> - 2026-05-20 r2-codex — MAJOR; 6 blockers resolved inline: (1) `cp -r */*` glob excluding dotfiles (privacy-firewall failure), (2) DATA-CYCLE.md client-agnostic-ness, (3) existing scaffold stale after D4 rename, (4) TDD test 9 ordering inconsistency, (5) checker missing `isArchived` + remote-URL-match validations, (6) yq python-fallback false comment removed
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2746
> **Paired plan:** [`docs/plans/2026-05-20-issue-2745-acma-projects-freeze.md`](2026-05-20-issue-2745-acma-projects-freeze.md)
> **Brainstorming spec:** [`docs/governance/2026-05-20-client-llm-wiki-feature-and-acma-instance-design.md`](../governance/2026-05-20-client-llm-wiki-feature-and-acma-instance-design.md) (commit `277a855ee`)
> **Review artifacts:** `scripts/review/results/2026-05-20-plan-2746-claude.md` | `...-codex.md` (Gemini optional per T2)

---

## Resource Intelligence Summary

### Existing repo code
- Found: `/mnt/local-analysis/llm-wiki-acma/` — bootstrap scaffold (`README.md`, `DATA-CYCLE.md`, `sources/README.md`, `pages/README.md`, `reports/README.md`, `ledgers/promotion-ledger.example.yml`); 2 commits; pushed to `vamseeachanta/llm-wiki-acma` (PRIVATE, `main`, not archived)
- Found: `/mnt/local-analysis/workspace-hub/scripts/enforcement/` — has `check-no-abs-paths.sh`, `check-harness-file-size.sh`, `check-no-conflict-markers.sh` (pattern reference for new checker)
- Found: `/mnt/local-analysis/workspace-hub/.claude/skills/coordination/` — has 40+ coordination skills; `llm-wiki-roadmap-integration` is closest analog for the new factory skill
- Found: `/mnt/local-analysis/workspace-hub/docs/plans/_template-issue-plan.md` — required plan structure (this file)
- Gap: no `templates/client-llm-wiki/` tree exists
- Gap: no `config/client-wikis.yml` registry exists
- Gap: no `scripts/enforcement/check-client-wiki-registry.sh` checker exists
- Gap: no `coordination/client-llm-wiki-factory/SKILL.md` skill exists
- Gap: scaffold at `/mnt/local-analysis/llm-wiki-acma/` is missing `LICENSE`, `.gitignore`, `.claude/CLAUDE.md`, `REDACTION-POSTURE.md`

### Standards
Not applicable (governance/data-pipeline issue; no engineering calculation standards).

### LLM Wiki pages consulted
No relevant pages (this issue creates infrastructure, doesn't consume wiki content).

### Documents consulted
- `docs/governance/2026-05-20-client-llm-wiki-feature-and-acma-instance-design.md` — user-accepted brainstorming spec; Approach B locked
- Parent epic [#2744](https://github.com/vamseeachanta/workspace-hub/issues/2744) — 4-child decomposition; non-negotiable boundaries
- Sibling [#2745](https://github.com/vamseeachanta/workspace-hub/issues/2745) — paired freeze plan
- Dependency [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) — data-location D1–D8 seed (D4 amendment proposal at [issuecomment-4500952654](https://github.com/vamseeachanta/workspace-hub/issues/2731#issuecomment-4500952654))
- Dependency [#2732](https://github.com/vamseeachanta/workspace-hub/issues/2732) — mount/folder taxonomy
- Closed parent [#2727](https://github.com/vamseeachanta/workspace-hub/issues/2727) — data-layer-boundary model (`raw → readable → private → reviewed → public`)
- `.claude/rules/coding-style.md` — no absolute paths in scripts (use `$(git rev-parse --show-toplevel)`)
- `.claude/rules/patterns.md` — enforcement gradient Level 2 (script) → Level 3 (hook)

### Gaps identified
- Template tree must be built from scratch (8 files)
- Registry YAML must be built from scratch (6-row initial registry)
- Checker script must be built from scratch (9 test conditions per spec §7)
- Factory skill must be built from scratch (11-step operator checklist)
- ACMA scaffold needs 4 firewall files added (LICENSE, .gitignore, .claude/CLAUDE.md, REDACTION-POSTURE.md)

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-20T18:30Z via `gh issue view`):
- `#2744` — OPEN — epic(acma): client project data-cycle readiness and private llm-wiki launch
- `#2745` — OPEN, `status:needs-plan` — feat(acma): freeze acma-projects and move to local-only archive posture
- `#2746` — OPEN, `status:needs-plan` — feat(acma): create private llm-wiki repo target llm-wiki-acma
- `#2731` — OPEN, `status:needs-plan` — feat(data-governance): inventory and normalize canonical data/repo locations
- `#2732` — OPEN — feat(data-governance): canonical first/second-level mount and folder taxonomy
- `#2727` — CLOSED `status:done` — feat(architecture): define data layer boundary and llm-wiki data promotion model

**File existence** (`ls -la /mnt/local-analysis/llm-wiki-acma/` 2026-05-20T12:50Z):
- EXISTS: `README.md`, `DATA-CYCLE.md`, `ledgers/promotion-ledger.example.yml`, `sources/README.md`, `pages/README.md`, `reports/README.md`
- MISSING: `LICENSE`, `.gitignore`, `.claude/CLAUDE.md`, `REDACTION-POSTURE.md`

**GH repo state** (`gh repo view vamseeachanta/llm-wiki-acma` 2026-05-20T18:30Z):
- visibility: PRIVATE; isArchived: false; defaultBranchRef: `main`; url: https://github.com/vamseeachanta/llm-wiki-acma

**Workspace-hub artifact gaps** (`ls` 2026-05-20T18:30Z):
- MISSING: `templates/client-llm-wiki/`
- MISSING: `config/client-wikis.yml`
- MISSING: `scripts/enforcement/check-client-wiki-registry.sh`
- MISSING: `.claude/skills/coordination/client-llm-wiki-factory/SKILL.md`

## Artifact Map

### New files in workspace-hub
| Path | Purpose |
|---|---|
| `templates/client-llm-wiki/README.md` | Per-wiki README with `<CLIENT_SHORT_NAME>` placeholders |
| `templates/client-llm-wiki/DATA-CYCLE.md` | Client-agnostic version using `<CLIENT_SHORT_NAME>` placeholder; sed-substituted during factory step 6. NOT a verbatim copy of the existing acma DATA-CYCLE.md (which hardcodes ACMA + pre-rename repo name `acma-llm-wiki`). |
| `templates/client-llm-wiki/LICENSE` | Proprietary marker — NOT OSS |
| `templates/client-llm-wiki/.gitignore` | Blocks raw/, private/, large binaries, secrets |
| `templates/client-llm-wiki/.claude/CLAUDE.md` | Private-posture override for instantiated wikis |
| `templates/client-llm-wiki/REDACTION-POSTURE.md` | Per-client redaction rules with 6 default categories |
| `templates/client-llm-wiki/sources/README.md` | Source-card conventions |
| `templates/client-llm-wiki/pages/README.md` | Wiki-page conventions |
| `templates/client-llm-wiki/reports/README.md` | Output-provenance conventions |
| `templates/client-llm-wiki/ledgers/promotion-ledger.example.yml` | Schema template (copy from acma scaffold) |
| `templates/client-llm-wiki/ledgers/README.md` | Ledger usage rules |
| `config/client-wikis.yml` | 6-row registry (acma `bootstrapped`, 5 `planned`) |
| `scripts/enforcement/check-client-wiki-registry.sh` | Validator with 9 fail conditions |
| `tests/enforcement/test_client_wiki_registry.sh` | TDD test suite for the checker (uses `REGISTRY_PATH` env override) |
| `tests/enforcement/fixtures/client-wikis-*.yml` | Per-test fixture registries (consistent/duplicate-short-name/missing-repo/wrong-visibility/firewall-violation variants) |
| `.claude/skills/coordination/client-llm-wiki-factory/SKILL.md` | 11-step operator checklist |

### New files in `vamseeachanta/llm-wiki-acma` (separate repo)
| Path | Purpose |
|---|---|
| `LICENSE` | Proprietary marker |
| `.gitignore` | Raw/private/secret guards |
| `.claude/CLAUDE.md` | Private-posture override |
| `REDACTION-POSTURE.md` | ACMA-specific redaction rules |

### Existing files preserved (in `vamseeachanta/llm-wiki-acma`)
- `sources/README.md`, `pages/README.md`, `reports/README.md`, `ledgers/promotion-ledger.example.yml` — kept as-is (no naming references that diverge from `acma`)
- `README.md` + `DATA-CYCLE.md` — **MUST be updated** in T6 to reflect the D4-amended repo name (`llm-wiki-acma`, not `acma-llm-wiki`). Per r2-codex finding 3, the current acma `README.md` still says "Recommended repo name `acma-llm-wiki`" and `DATA-CYCLE.md` still names `vamseeachanta/acma-llm-wiki`. T6 substitutes these references; checker T7 verifies no stale `acma-llm-wiki` strings remain.

## Deliverable

A reusable feature for instantiating per-client private llm-wiki repos under [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) D4 (amended) — concretely the template + registry + checker + skill — and the ACMA instance ([#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746)) ratified against it.

## Scope Boundaries

**IN scope:**
- Build template tree, registry, checker, factory skill in workspace-hub
- Add 4 firewall files to existing `vamseeachanta/llm-wiki-acma` scaffold
- Register acma in `config/client-wikis.yml` with `status: bootstrapped`
- Delete NTFS clone at `/mnt/ace/llm-wiki-acma/` after confirming ext4 clone is fully synced (spec §5.1 step 4)
- TDD: write all 9 tests in `tests/enforcement/test_client_wiki_registry.sh` BEFORE implementing the checker

**OUT of scope:**
- Raw-data import into the wiki (deferred to post-approval implementation under [#2747](https://github.com/vamseeachanta/workspace-hub/issues/2747)/[#2748](https://github.com/vamseeachanta/workspace-hub/issues/2748))
- Other 5 wiki instances (rock-oil-field, client-projects, doris, frontierdeepwater, saipem) — Phase 4–5 follow-on issues
- Promotion ledger schema beyond the existing example file — that's [#2747](https://github.com/vamseeachanta/workspace-hub/issues/2747)'s scope
- Pre-commit hook promotion of the checker — Level 3 enforcement deferred to follow-on issue
- acma-projects freeze (archive GH remote, etc.) — that's the paired [#2745](https://github.com/vamseeachanta/workspace-hub/issues/2745) plan

## Patch Shape

Each task is self-contained, TDD-first, single-pathspec commits. Approximate sizes:

| Task | Files | Net LOC | Repo |
|---|---|---|---|
| T1 — Template tree scaffold | 11 new files | ~250 | workspace-hub |
| T2 — Registry YAML | 1 new file | ~50 | workspace-hub |
| T3 — Checker test suite (RED) | 1 new file | ~120 | workspace-hub |
| T4 — Checker implementation (GREEN) | 1 new file | ~150 | workspace-hub |
| T5 — Factory skill | 1 new file | ~120 | workspace-hub |
| T6 — Firewall files in llm-wiki-acma | 4 new files | ~80 | llm-wiki-acma |
| T7 — Registry: mark acma `bootstrapped` | 1 modified | ~3 | workspace-hub |
| T8 — NTFS-clone disposition | 0 new, 1 rm-dir | n/a | local FS |

## Pseudocode

### Checker (`scripts/enforcement/check-client-wiki-registry.sh`)

```bash
#!/usr/bin/env bash
# Validates config/client-wikis.yml against on-disk + GitHub reality.
# Exit non-zero on any failure. Machine-aware: skip mount checks when not present.

set -euo pipefail
REPO_ROOT="$(git rev-parse --show-toplevel)"
# Registry path is overridable for tests; defaults to canonical location.
REGISTRY="${REGISTRY_PATH:-${REPO_ROOT}/config/client-wikis.yml}"
# Precheck dependencies before doing any work.
command -v yq >/dev/null || { echo "FAIL: yq v4+ required (https://github.com/mikefarah/yq)"; exit 1; }
command -v gh >/dev/null || { echo "FAIL: gh CLI required"; exit 1; }
FAILED=0

# 1. Registry exists
[[ -f "$REGISTRY" ]] || { echo "FAIL: registry missing at $REGISTRY"; exit 1; }

# 2. Parse with yq (v4+ required; precheck above)
SHORT_NAMES=$(yq '.wikis[].short_name' "$REGISTRY")
REPOS=$(yq '.wikis[].repo' "$REGISTRY")
POSTURES=$(yq '.wikis[].posture' "$REGISTRY")

# 3. Uniqueness of short_name
DUPES=$(echo "$SHORT_NAMES" | sort | uniq -d)
[[ -z "$DUPES" ]] || { echo "FAIL: duplicate short_name: $DUPES"; FAILED=1; }

# 4. For each entry: gh repo exists + visibility check
for i in $(yq '.wikis | keys | .[]' "$REGISTRY"); do
  SHORT=$(yq ".wikis[$i].short_name" "$REGISTRY")
  REPO=$(yq ".wikis[$i].repo" "$REGISTRY")
  POSTURE=$(yq ".wikis[$i].posture" "$REGISTRY")
  STATUS=$(yq ".wikis[$i].status" "$REGISTRY")

  # Only check repo existence + archived for bootstrapped/live (not planned/retired)
  if [[ "$STATUS" =~ ^(bootstrapped|live)$ ]]; then
    REPO_JSON=$(gh repo view "$REPO" --json visibility,isArchived 2>/dev/null || echo "")
    if [[ -z "$REPO_JSON" ]]; then
      echo "FAIL: $SHORT repo $REPO not found on GH"; FAILED=1
    else
      VIS=$(echo "$REPO_JSON" | yq -r '.visibility')
      ARCHIVED=$(echo "$REPO_JSON" | yq -r '.isArchived')
      [[ "$POSTURE" == "client-private" && "$VIS" != "PRIVATE" ]] && \
        { echo "FAIL: $SHORT posture=client-private but visibility=$VIS"; FAILED=1; }
      # r2-codex finding 5: governance spec §4.3 requires isArchived=false for non-retired entries
      [[ "$ARCHIVED" == "true" ]] && \
        { echo "FAIL: $SHORT status=$STATUS but GH repo isArchived=true"; FAILED=1; }
    fi
  fi

  # Local clone check (machine-aware: skip if mount root absent)
  CLONE=$(yq ".wikis[$i].local_working_clone" "$REGISTRY")
  if [[ -d "$(dirname "$CLONE")" ]]; then
    [[ -d "$CLONE/.git" ]] || { echo "FAIL: $SHORT clone $CLONE missing or not a git repo"; FAILED=1; }
    # r2-codex finding 5: governance spec §4.3 requires clone's remote to match `repo`
    if [[ -d "$CLONE/.git" ]]; then
      CLONE_REMOTE=$(git -C "$CLONE" config --get remote.origin.url 2>/dev/null || echo "")
      EXPECTED=("https://github.com/$REPO" "https://github.com/$REPO.git" "git@github.com:$REPO.git")
      MATCH=0
      for u in "${EXPECTED[@]}"; do [[ "$CLONE_REMOTE" == "$u" ]] && MATCH=1 && break; done
      [[ $MATCH -eq 1 ]] || { echo "FAIL: $SHORT clone $CLONE remote=$CLONE_REMOTE doesn't match expected $REPO"; FAILED=1; }
    fi
  fi

  # Firewall guard: client-private raw_roots must not match a public llm-wiki path
  if [[ "$POSTURE" == "client-private" ]]; then
    RAW_ROOTS=$(yq ".wikis[$i].raw_roots[]" "$REGISTRY")
    echo "$RAW_ROOTS" | grep -E '/llm-wiki/?$|/llm-wiki/[^/]' && \
      { echo "FAIL: $SHORT client-private raw_roots overlaps public llm-wiki path"; FAILED=1; }
  fi
done

exit $FAILED
```

### Factory skill (`coordination/client-llm-wiki-factory/SKILL.md`) — operator checklist (verbatim core)

```markdown
# Client LLM-Wiki Factory — Operator Checklist

For instantiating a NEW per-client private llm-wiki under #2731 D4 (amended).
Requires user-approved plan per SHARED_SOUL.md gates before invocation.

## Steps

1. Read `config/client-wikis.yml`; confirm target `<short_name>` has `status: planned` (not already live).
2. Confirm `/mnt/ace/<bucket>/` exists (per #2731 D3 raw-root canonical).
3. `gh repo create vamseeachanta/llm-wiki-<short_name> --private --description "Private client llm-wiki for <short_name>"`
4. `git clone https://github.com/vamseeachanta/llm-wiki-<short_name>.git /mnt/local-analysis/llm-wiki-<short_name>/`
5. `cp -a workspace-hub/templates/client-llm-wiki/. /mnt/local-analysis/llm-wiki-<short_name>/` — **r2-codex finding 1**: use trailing-dot form (`SRC/.`), NOT `SRC/*`. Plain `cp -r SRC/* DEST/` SKIPS dotfiles, omitting `.gitignore` and `.claude/CLAUDE.md` from new repos — privacy-firewall failure. `cp -a SRC/. DEST/` copies all entries including dotfiles and preserves attributes.
6. Placeholder substitution: `find /mnt/local-analysis/llm-wiki-<short_name> -type f -exec sed -i "s/<CLIENT_SHORT_NAME>/<short_name>/g" {} +`
7. Open `REDACTION-POSTURE.md` and add client-specific redaction rules beyond the 6 defaults.
8. Initial commit in the NEW client wiki repo (pathspec form per `feedback_multi_agent_commit_serialization`) AND push to origin.
9. Switch to workspace-hub directory: `cd "$WORKSPACE_HUB"` (or `cd /mnt/local-analysis/workspace-hub`).
10. Edit `config/client-wikis.yml`: change `status: planned` → `status: bootstrapped`; add `instantiated_at` date.
11. Commit + push the registry edit in workspace-hub (pathspec form):
    ```
    git commit -m "chore(client-wiki-factory): mark <short_name> bootstrapped" -- config/client-wikis.yml
    git push
    ```
12. Run `scripts/enforcement/check-client-wiki-registry.sh` — MUST pass before declaring complete.
13. Post comment on parent client-wiki issue with: repo URL, scaffold commit SHA, registry entry diff.
```

## Files to Change

### Tasks (TDD-ordered)

**T1 — Template tree scaffold** (workspace-hub, single commit)
- Create `templates/client-llm-wiki/README.md` with `<CLIENT_SHORT_NAME>` placeholders
- Create `templates/client-llm-wiki/DATA-CYCLE.md` (copy verbatim from `/mnt/local-analysis/llm-wiki-acma/DATA-CYCLE.md`)
- Create `templates/client-llm-wiki/LICENSE` (proprietary marker; no OSS keywords)
- Create `templates/client-llm-wiki/.gitignore` (raw/, private/, *.dwg, *.sim, *.dat>10MB, credential patterns)
- Create `templates/client-llm-wiki/.claude/CLAUDE.md` (private-posture override; explicit no-public-promotion clause)
- Create `templates/client-llm-wiki/REDACTION-POSTURE.md` with 6-row default table (client legal name=REDACT, project IDs=REDACT, personal names=FLAG, geo coords=FLAG, vessel names=FLAG, financial figures=REDACT)
- Create `templates/client-llm-wiki/sources/README.md`, `pages/README.md`, `reports/README.md` (copy from acma scaffold)
- Create `templates/client-llm-wiki/ledgers/promotion-ledger.example.yml` (copy from acma scaffold)
- Create `templates/client-llm-wiki/ledgers/README.md` (ledger usage)
- Commit: `git commit -m "feat(client-wiki-factory): template tree for per-client private wikis" -- templates/client-llm-wiki/`

**T2 — Registry YAML** (workspace-hub, single commit)
- Create `config/client-wikis.yml` with `registry_version: 0.1` and 6 wiki entries per spec §4.2; acma `status: bootstrapped` (instance #1); other 5 `status: planned`
- Commit: `git commit -m "feat(client-wiki-factory): seed registry config/client-wikis.yml" -- config/client-wikis.yml`

**T3 — Checker test suite (RED)** (workspace-hub, single commit, MUST FAIL before T4)
- Create `tests/enforcement/test_client_wiki_registry.sh` with 9 test cases (one per condition in spec §7)
- Run: `bash tests/enforcement/test_client_wiki_registry.sh` → expect FAIL (no checker exists)
- Commit: `git commit -m "test(client-wiki-factory): TDD red — registry checker test suite" -- tests/enforcement/test_client_wiki_registry.sh`

**T4 — Checker implementation (GREEN)** (workspace-hub, single commit)
- Create `scripts/enforcement/check-client-wiki-registry.sh` matching the pseudocode above
- Make executable: `chmod +x scripts/enforcement/check-client-wiki-registry.sh`
- Run: `bash tests/enforcement/test_client_wiki_registry.sh` → expect PASS
- Run: `scripts/enforcement/check-client-wiki-registry.sh` → expect PASS (acma row passes against live state)
- Commit: `git commit -m "feat(client-wiki-factory): checker implementation (TDD green)" -- scripts/enforcement/check-client-wiki-registry.sh`

**T5 — Factory skill** (workspace-hub, single commit)
- Create `.claude/skills/coordination/client-llm-wiki-factory/SKILL.md` with the 13-step checklist (pseudocode above; expanded from 11 in r1 review to split workspace-hub registry edit into explicit edit + commit + push steps, resolving cross-repo-commit-semantics blocker)
- Include front-matter (`name`, `description`, `version`, `category: coordination`, `tags`, `related_skills`)
- Commit: `git commit -m "feat(client-wiki-factory): operator-checklist skill" -- .claude/skills/coordination/client-llm-wiki-factory/SKILL.md`

**T6 — Firewall files + post-rename text updates in llm-wiki-acma** (separate repo, single commit there)
- Per r2-codex finding 3: existing `README.md` + `DATA-CYCLE.md` still contain pre-rename name `acma-llm-wiki`. Must be updated here.
- `cd /mnt/local-analysis/llm-wiki-acma/`
- `sed -i 's|acma-llm-wiki|llm-wiki-acma|g' README.md DATA-CYCLE.md` (single-G substitution; verify no over-match on legitimate uses)
- Verify post-edit: `grep -n 'acma-llm-wiki' README.md DATA-CYCLE.md` → 0 hits
- `cd /mnt/local-analysis/llm-wiki-acma/`
- Copy `LICENSE`, `.gitignore`, `.claude/CLAUDE.md`, `REDACTION-POSTURE.md` from `workspace-hub/templates/client-llm-wiki/` — substitute `<CLIENT_SHORT_NAME>` with `acma`
- Customize `REDACTION-POSTURE.md` with acma-specific rules (defaults stand if no customization needed)
- Verify dotfile firewall artifacts present: `[[ -f .gitignore && -f .claude/CLAUDE.md ]]` → both must be true. If not, the `cp -a SRC/. DEST/` form failed and the privacy firewall is broken — ABORT before commit. (Defends r2-codex finding 1.)
- Commit (in llm-wiki-acma repo): `git add LICENSE .gitignore .claude/ REDACTION-POSTURE.md && git commit -m "feat: add firewall files per workspace-hub#2746 spec"`
- Push to `vamseeachanta/llm-wiki-acma`

**T7 — Registry: mark acma bootstrapped** (workspace-hub, single commit)
- Update `config/client-wikis.yml`: confirm acma row matches reality after T6 (already `bootstrapped` from T2; verify dates)
- Run `scripts/enforcement/check-client-wiki-registry.sh` — MUST pass
- Commit: `git commit -m "chore(client-wiki-factory): finalize acma registry entry post-firewall-files" -- config/client-wikis.yml`

**T8 — NTFS-clone disposition** (local FS only, no commit)

Pre-delete invariants (ALL must pass; ABORT if any fails):

```bash
cd /mnt/ace/llm-wiki-acma   # the NTFS clone being deleted (NOT the ext4 clone)

# Invariant 1: no uncommitted changes (staged or unstaged) and no untracked files
[[ -z "$(git status --porcelain)" ]] || { echo "ABORT: NTFS clone has uncommitted/untracked changes"; exit 1; }

# Invariant 2: each local branch is pushed to origin
git fetch origin --quiet
for branch in $(git for-each-ref --format='%(refname:short)' refs/heads/); do
  if ! git rev-parse --verify --quiet "origin/$branch" >/dev/null; then
    echo "ABORT: NTFS clone branch '$branch' has no origin counterpart (unpushed)"; exit 1
  fi
  if [[ "$(git rev-parse "$branch")" != "$(git rev-parse "origin/$branch")" ]]; then
    echo "ABORT: NTFS clone branch '$branch' diverges from origin/$branch"; exit 1
  fi
done

# Invariant 3: no stash entries
[[ -z "$(git stash list)" ]] || { echo "ABORT: NTFS clone has stash entries (would be lost)"; exit 1; }

# Invariant 4: GitHub remote reachable and matches expected repo
gh repo view vamseeachanta/llm-wiki-acma --json visibility,defaultBranchRef >/dev/null \
  || { echo "ABORT: GitHub remote unreachable"; exit 1; }
```

If ALL invariants pass: `rm -rf /mnt/ace/llm-wiki-acma/`

Rationale per `feedback_ntfs3_symlink_intxlnk`: NTFS-backed clone is a corruption hazard, not a backup; GitHub remote is the durable backup. The 4 invariants address the r1 finding that the original `git diff origin/main..main --quiet` only caught tracked-commit divergence on main, missing uncommitted changes, untracked files, non-main unpushed branches, and stash entries — all real data-loss vectors.

## TDD Test List

(Implemented in `tests/enforcement/test_client_wiki_registry.sh`)

All tests use `REGISTRY_PATH` env override to load per-test fixture YAMLs from `tests/enforcement/fixtures/`. Live `config/client-wikis.yml` is never touched by tests.

| # | Test | Fixture | Expected |
|---|---|---|---|
| 1 | Registry consistent → checker passes | `fixtures/client-wikis-consistent.yml` (acma bootstrapped, others planned) | Exit 0; no stderr |
| 2 | Registry missing `repo` field on entry | `fixtures/client-wikis-missing-repo-field.yml` | Exit non-zero, name offending `short_name` |
| 3 | GH repo for `bootstrapped` entry doesn't exist | `fixtures/client-wikis-fake-repo.yml` (points at `vamseeachanta/nonexistent-fake-repo`) | Exit non-zero |
| 4 | `client-private` posture but visibility != PRIVATE | `fixtures/client-wikis-wrong-visibility.yml` (points at a PUBLIC repo, e.g., `vamseeachanta/workspace-hub`) | Exit non-zero |
| 5 | `local_working_clone` missing when mount root present | `fixtures/client-wikis-missing-clone.yml` (clone path under existing `/mnt/local-analysis/`) | Exit non-zero |
| 6 | `local_working_clone` missing when mount root ABSENT | `fixtures/client-wikis-missing-mount.yml` (clone path under `/mnt/nonexistent-mount/`) | Exit 0 (machine-aware skip) |
| 7 | Duplicate `short_name` across two entries | `fixtures/client-wikis-duplicate-shortname.yml` | Exit non-zero |
| 8 | **Firewall guard:** `client-private` `raw_roots` contains a public llm-wiki path | `fixtures/client-wikis-firewall-violation.yml` (raw_root = `/mnt/local-analysis/llm-wiki/`) | Exit non-zero |
| 9 | Instantiated wiki repo: `grep` for OSS-license boilerplate in `LICENSE` | n/a (template-instantiation test, not registry test); run on `/mnt/local-analysis/llm-wiki-acma/LICENSE` after T6 | Tightened regex per r1 finding #4: grep for `'Licensed under the MIT'\|'Apache License, Version 2.0'\|'BSD 3-Clause'\|'Creative Commons'` → 0 hits AND `grep -i 'All rights reserved\|Proprietary\|Confidential'` → ≥1 hit |

Test runner shape (one test per `test_*` function in shell):

```bash
test_01_consistent_registry_passes() { ... }
test_02_missing_repo_field_fails() { ... }
# ...
main() {
  local -i fails=0
  for t in $(declare -F | awk '/test_/ {print $3}'); do
    "$t" || ((fails++))
  done
  exit $fails
}
```

## Acceptance Criteria

- [ ] **Registry-suite tests (1–8)** in `tests/enforcement/test_client_wiki_registry.sh` all pass at T3 RED → T4 GREEN; this is the suite gated before T4 implementation
- [ ] **Instantiation-suite test (9)** runs as a post-T6 verification check (not part of T3 RED) — `grep` for OSS-license boilerplate AND proprietary markers in `/mnt/local-analysis/llm-wiki-acma/LICENSE` per r2-codex finding 4 (tests cannot run before LICENSE file exists)
- [ ] `scripts/enforcement/check-client-wiki-registry.sh` exits 0 against the seeded registry (acma `bootstrapped`)
- [ ] `templates/client-llm-wiki/` contains all 11 files (README, DATA-CYCLE, LICENSE, .gitignore, .claude/CLAUDE.md, REDACTION-POSTURE, 3 sub-READMEs, ledger example, ledger README)
- [ ] `config/client-wikis.yml` contains 6 wiki entries with correct posture, raw_roots, status
- [ ] `vamseeachanta/llm-wiki-acma` has 4 added firewall files committed and pushed
- [ ] `/mnt/ace/llm-wiki-acma/` directory removed after sync verification
- [ ] Factory skill committed at `.claude/skills/coordination/client-llm-wiki-factory/SKILL.md` with proper frontmatter
- [ ] `LICENSE` in instantiated `llm-wiki-acma` does NOT contain OSS license keywords (grep -i for MIT|Apache|BSD|CC-BY returns 0 hits)
- [ ] No `<CLIENT_SHORT_NAME>` placeholders remain in instantiated `llm-wiki-acma` (grep returns 0 hits)
- [ ] Adversarial review (T2: Claude + Codex) produces APPROVE on both code and plan stages
- [ ] Legal-sanity scan passes on all new commits per `coordination/legal-sanity-scan` skill
- [ ] Spec ratification criterion: re-run checker after [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) lands `status:plan-approved`; if D4 final differs from D4', file a reconciliation issue (no scope expansion in this plan)
- [ ] Comment posted on [#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746) with implementation evidence (commit SHAs, test output, checker output)
- [ ] Issue closed with `gh issue close --comment` per `feedback_gh_issue_comment` + `feedback_gh_issue_close_silent_comment_drop` (reopen-comment-close if already closed)

## Adversarial Review Summary

(To be filled by reviewers; T2 default = Claude + Codex)

**Claude review (drafting agent):** TBD after plan posted
**Codex review:** TBD after plan posted
**Gemini review (optional T3 escalation):** TBD; degrade to UNAVAILABLE per `feedback_gemini_sandbox_overlay_blindness` if quota out

Plan must reach APPROVE or APPROVE-MINOR-NITS from both T2 reviewers before label flips to `status:plan-review`.

## Risks and Open Questions

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) D4 final differs from D4' (`llm-wiki-<client>`) | Medium | Medium | Acceptance criterion: ratify post-[#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731)-approval; reconciliation as separate issue |
| `yq v4+` not installed on operator's machine | Low | Low | Checker script's `command -v yq` precheck; document install in skill |
| GH rate-limit during checker's per-entry `gh repo view` calls | Low | Low | Batch with `gh api graphql` if N grows; for 6 entries, sequential is fine |
| Operator runs `sed -i` on macOS without `''` empty-suffix | Low | Low | Factory skill currently uses bare `sed -i` (Linux-only); per r2-codex finding 7, mitigation in factory skill must be updated to use `sed -i.bak ... && find ... -name '*.bak' -delete` for cross-platform safety, OR pin operator OS to Linux. Resolution deferred to skill-author at implementation; documented in T5 implementation notes. |
| Multi-agent commit race on `config/client-wikis.yml` during Phase 4–5 rollout | Medium | Low | Pathspec commit form mandatory per `feedback_multi_agent_commit_serialization` |
| Subagent-write phantom if T1 template tree dispatched via subagent | Low | Medium | Main session does T1 directly; subagent dispatch only for parallelizable read-only tasks per `feedback_subagent_write_phantom` |

**Open questions (deferred to implementation, not plan-approval):**
- Tests language confirmed shell (per task T3); revisit if YAML parsing complexity grows
- Implementation-notes.html running file format: HTML default per `feedback_html_default_artifact` (locked at plan-approval if user concurs)

## Complexity: T2

T2 justification: multi-file (15+ new files) + cross-repo (workspace-hub + llm-wiki-acma) + privacy-firewall stakes warrant 2-provider review (Claude + Codex). T3 (Gemini) optional escalation reserved for if privacy-firewall defect surfaces in adversarial review.

## Implementation Notes for Future Approved Work

- The factory skill is the unit-test for the template — Phase 4 (second-wiki validation) will exercise it. If Phase 1 implementation discovers that step 6 (sed placeholder substitution) corrupts non-ASCII placeholders, fix BEFORE Phase 4.
- The 11-step checklist in T5 includes pathspec-form commits. Operators MUST follow per `feedback_multi_agent_commit_serialization`.
- The 1.8 TB pre-move backup at `/mnt/ace/acma-projects.preexisting-*` is OUT of this plan's scope; [#2745](https://github.com/vamseeachanta/workspace-hub/issues/2745) plan picks its disposition.
- After T7 (registry finalize) the plan is implementation-complete for [#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746). [#2745](https://github.com/vamseeachanta/workspace-hub/issues/2745) (freeze) runs as a separate, paired execution.
