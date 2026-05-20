---
name: client-llm-wiki-factory
description: Operator checklist for instantiating a new per-client private llm-wiki repo under workspace-hub [#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746) + [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) D4 (amended) naming convention `llm-wiki-<client>`.
version: 1.0.0
category: coordination
tags: [client-wiki, factory, instantiation, privacy-firewall, llm-wiki, governance]
related_skills:
  - coordination/legal-sanity-scan
  - coordination/llm-wiki-roadmap-integration
  - coordination/pre-completion-cleanup-audit
---

# Client LLM-Wiki Factory — Operator Checklist

## Use when
- You need to instantiate a new private per-client llm-wiki under the canonical `vamseeachanta/llm-wiki-<short_name>` naming convention.
- The target client appears in `config/client-wikis.yml` with `status: planned` and you have approval to bootstrap.
- You are setting up the privacy firewall layer (`.gitignore` + per-client `.claude/CLAUDE.md`) for a brand-new client repo.

## Do not use when
- A `vamseeachanta/llm-wiki-<short_name>` repo already exists with `status: bootstrapped` or `status: live` in the registry — this is a one-time bootstrap; ongoing operations live in `coordination/llm-wiki-roadmap-integration` and the per-client repo's `DATA-CYCLE.md`.
- You are adding a new entry to `config/client-wikis.yml` (registry edit only) — no factory work is needed until status flips to `planned` and is approved for bootstrap.
- You are renaming or relocating an existing client wiki — out of scope; route to a dedicated migration plan.

## Prerequisites
- Workspace-hub checked out at `/mnt/local-analysis/workspace-hub` (or `$WORKSPACE_HUB` env var).
- Templates present under `workspace-hub/templates/client-llm-wiki/` (T1 deliverable from [#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746)).
- Registry present at `config/client-wikis.yml` (T2 deliverable from [#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746)).
- Checker present at `scripts/enforcement/check-client-wiki-registry.sh` (T3/T4 deliverable from [#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746)).
- `gh` CLI authenticated and authorized to create private repos under `vamseeachanta`.
- Target client's raw-source bucket present under `/mnt/ace/<bucket>/` per [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) D3 (raw-root canonical).

## Template placeholders

The template tree contains four placeholders. The operator MUST set all four shell variables before running step 6. Substitution is single-pass via `find ... -exec sed -i`; verification uses a `grep` that must return 0 hits.

| Placeholder | Substitute for `acma` | Notes |
|---|---|---|
| `<CLIENT_SHORT_NAME>` | `acma` | Lowercase, hyphenated short-name; matches repo-name suffix in `llm-wiki-<short_name>`. |
| `<CLIENT_SHORT_NAME_UPPER>` | `ACMA` | Uppercase variant; used as ledger source-ID prefix (e.g., `ACMA-SOURCE-0001`) in `ledgers/promotion-ledger.example.yml`. |
| `<CLIENT_PRIVATE_REPO>` | `vamseeachanta/llm-wiki-acma` | Full GH `org/repo` slug; used in `DATA-CYCLE.md` and any cross-link prose. |
| `<CLIENT_RAW_ROOT>` | `acma-projects` | Bucket name under `/mnt/ace/`. Often differs from `<short_name>` — see edge cases below. |

### Per-client invocations (5 remaining wikis)

Examples for the other planned clients in `config/client-wikis.yml`. Note the bucket-name edge cases per [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) D5 (`client_projects` is underscore-separated, not hyphen) and [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) D6 (`frontierdeepwater` is one word, no hyphen).

| `<short_name>` | `<CLIENT_RAW_ROOT>` | `<CLIENT_PRIVATE_REPO>` |
|---|---|---|
| `rock-oil-field` | `rock-oil-field` | `vamseeachanta/llm-wiki-rock-oil-field` |
| `client-projects` | `client_projects` (underscore per [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) D5) | `vamseeachanta/llm-wiki-client-projects` |
| `doris` | `doris` | `vamseeachanta/llm-wiki-doris` |
| `frontierdeepwater` | `frontierdeepwater` (no hyphen per [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) D6) | `vamseeachanta/llm-wiki-frontierdeepwater` |
| `saipem` | `saipem` | `vamseeachanta/llm-wiki-saipem` |

## Step 0 + 13-step checklist

Run these in order. Step 0 sets the shell variables referenced throughout; steps 9 and 12 are commit steps and use the **pathspec form** per `feedback_multi_agent_commit_serialization` to avoid sweeping parallel-session staged changes.

### 0. Set variables

Set these once at the start — referenced throughout the checklist. `RAW` differs from `$SHORT` for `acma` (`acma-projects`) and `client-projects` (`client_projects`, underscore per [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) D5); see Step 2 + per-client table above for edge cases.

```bash
# Set these once at the start — referenced throughout the checklist.
SHORT="acma"                                    # lowercase short_name (replace with your client)
UPPER=$(echo "$SHORT" | tr '[:lower:]' '[:upper:]')   # e.g., ACMA
PRIV="vamseeachanta/llm-wiki-$SHORT"            # full GH slug
RAW="acma-projects"                             # bucket name under /mnt/ace/ — see Step 2 for edge cases (D5/D6)
```

### 1. Pre-flight: confirm registry entry

```bash
grep -A6 "short_name: $SHORT" config/client-wikis.yml
```

Confirm the target client appears with `status: planned`. If `status: bootstrapped` or `status: live`, STOP — this is a one-time bootstrap; the wiki already exists.

### 2. Confirm raw-source bucket exists

```bash
ls -ld /mnt/ace/$RAW/
```

Per [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) D3 (raw-root canonical) the bucket must exist on `/mnt/ace/` before instantiation; the new private wiki's `DATA-CYCLE.md` will reference it. If missing, route to the raw-source onboarding step first.

### 3. Create the private GitHub repo

```bash
gh repo create "$PRIV" \
  --private \
  --description "Private client llm-wiki for $SHORT"
```

Private is mandatory — these wikis carry client-derived material and MUST NOT be public.

### 4. Clone to local working tree

```bash
git clone "https://github.com/$PRIV.git" \
  /mnt/local-analysis/llm-wiki-$SHORT/
```

Use `/mnt/local-analysis/` as the working-clone root (per the established workspace layout — distinct from `/mnt/ace/` raw-source bucket).

### 5. Copy the template tree — `cp -a SRC/. DEST/` form

```bash
cp -a /mnt/local-analysis/workspace-hub/templates/client-llm-wiki/. \
      /mnt/local-analysis/llm-wiki-$SHORT/
```

**Critical**: use the trailing-dot form (`SRC/.`), NOT `SRC/*`. Plain `cp -r SRC/* DEST/` SKIPS dotfiles, omitting `.gitignore` and `.claude/CLAUDE.md` from the new repo — a **privacy-firewall failure**. The `-a` flag also preserves attributes and is recursive.

### 6. Substitute all 4 placeholders

Variables `SHORT` / `UPPER` / `PRIV` / `RAW` were set in Step 0 — re-shown here for context. Run the multi-expression sed:

```bash
# Already set in Step 0 — re-shown here for context:
#   SHORT="acma"
#   UPPER="ACMA"
#   PRIV="vamseeachanta/llm-wiki-$SHORT"
#   RAW="acma-projects"

find /mnt/local-analysis/llm-wiki-$SHORT -type f -exec sed -i \
  -e "s|<CLIENT_SHORT_NAME>|$SHORT|g" \
  -e "s|<CLIENT_SHORT_NAME_UPPER>|$UPPER|g" \
  -e "s|<CLIENT_PRIVATE_REPO>|$PRIV|g" \
  -e "s|<CLIENT_RAW_ROOT>|$RAW|g" \
  {} +
```

**Verify**: every placeholder must be substituted; this grep MUST return 0 hits:

```bash
grep -rE '<CLIENT_(SHORT_NAME|SHORT_NAME_UPPER|PRIVATE_REPO|RAW_ROOT)>' \
  /mnt/local-analysis/llm-wiki-$SHORT
```

If any hits remain, the substitution failed — re-run with the missing variable populated.

### 7. Optional: customize `REDACTION-POSTURE.md`

Open `/mnt/local-analysis/llm-wiki-$SHORT/REDACTION-POSTURE.md`. The template ships with 6 default redaction rules; add client-specific rules only if the client has a known PII / confidentiality pattern beyond the defaults (e.g., a specific project codename, a named vessel, a named field). The defaults stand if no customization is needed.

### 8. Verify dotfile firewall — ABORT gate

This is the defense against a silent `cp` failure in step 5. Both files MUST exist; if either is missing, the privacy firewall is broken — STOP, do not commit, re-run step 5 with the trailing-dot form.

```bash
[[ -f /mnt/local-analysis/llm-wiki-$SHORT/.gitignore \
   && -f /mnt/local-analysis/llm-wiki-$SHORT/.claude/CLAUDE.md ]] \
  || { echo "ABORT: privacy-firewall dotfiles missing"; exit 1; }
```

### 9. Initial commit + push in the new client wiki

```bash
cd /mnt/local-analysis/llm-wiki-$SHORT
git add .
git commit -m "feat: bootstrap private client llm-wiki for $SHORT" --signoff
git push origin main
```

Pathspec form (`-- <file>`) is not used here because this is the FIRST commit in a fresh repo with no parallel-agent activity — `git add .` over a clean tree is safe. Pathspec form IS used in step 12 (workspace-hub) where parallel agents are active.

Capture the commit SHA — it goes in the closing-comment payload (step 13).

### 10. Switch back to workspace-hub

```bash
cd /mnt/local-analysis/workspace-hub    # or: cd $WORKSPACE_HUB
```

### 11. Edit the registry — flip status and record instantiation

Edit `config/client-wikis.yml` and update the target entry:

- `status: planned` → `status: bootstrapped`
- add `instantiated_at: YYYY-MM-DD` (today's date)
- add `local_working_clone: /mnt/local-analysis/llm-wiki-<short_name>/`

### 12. Commit + push the registry edit (pathspec form)

```bash
git commit -m "chore(client-wiki-factory): mark <short_name> bootstrapped" \
  -- config/client-wikis.yml
git push
```

Pathspec form per `feedback_multi_agent_commit_serialization` — workspace-hub has frequent parallel-agent activity, and bare `git commit` would sweep any unrelated staged files from concurrent sessions.

### 13. Run the registry checker + post closeout comment

```bash
scripts/enforcement/check-client-wiki-registry.sh
```

Must exit 0. If it fails, fix the registry entry and re-commit before declaring complete.

Then post a comment on the parent client-wiki tracking issue (or [#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746) if no per-client child issue exists) containing:

- New private repo URL: `https://github.com/vamseeachanta/llm-wiki-<short_name>`
- Scaffold commit SHA from step 9
- Diff of the registry entry from step 12 (one-paragraph summary or `git show -- config/client-wikis.yml`)

## Pitfalls (record verified hazards)

- **`cp -r SRC/*` skips dotfiles** — silently omits `.gitignore` and `.claude/CLAUDE.md`. Always use `cp -a SRC/.`. Step 8 is the catch.
- **Missing placeholder substitution** — if a variable is unset, sed substitutes nothing and leaves `<CLIENT_…>` in the file. The step-6 verify-grep is the catch; do not skip it.
- **Public repo creation** — `gh repo create` defaults vary by org. Always pass `--private` explicitly.
- **Bucket-name drift** — `<CLIENT_RAW_ROOT>` is NOT always equal to `<CLIENT_SHORT_NAME>`. See per-client table above; [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) D5 (`client_projects`, underscore) and D6 (`frontierdeepwater`, no hyphen) are the documented edge cases.
- **Cross-repo commit semantics** — steps 9 and 12 commit to DIFFERENT repositories (new client wiki vs workspace-hub). The `cd` in step 10 is load-bearing; without it, step 12 commits to the wrong repo.
- **Parallel-agent sweep on workspace-hub commit** — step 12 uses pathspec form for this reason. If you forget, you may sweep an unrelated agent's staged work into the registry commit.

## Verification summary

A successful run produces:

- one new private GitHub repo `vamseeachanta/llm-wiki-<short_name>`
- one initial commit in that new repo (scaffold + 4-placeholder substitution + dotfile firewall)
- one commit in workspace-hub touching only `config/client-wikis.yml` (status flip)
- registry checker exits 0
- one closeout comment on the tracking issue with repo URL, SHA, and registry diff

## References

- Plan: `docs/plans/2026-05-20-issue-2746-llm-wiki-acma.md`
- Naming convention: workspace-hub [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) D4 (amended); raw-root canonical D3; bucket-name edge cases D5, D6
- Privacy firewall pattern: `feedback_per_repo_metadata_is_firewall`
- Commit serialization: `feedback_multi_agent_commit_serialization`
- Sibling skill (post-bootstrap operations): `coordination/llm-wiki-roadmap-integration`
- Sibling skill (legal scan before push): `coordination/legal-sanity-scan`
