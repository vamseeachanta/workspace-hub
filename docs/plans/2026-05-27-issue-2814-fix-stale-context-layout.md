# Plan for #2814: docs(harness): fix stale context.md repo-layout claim (siblings vs nested)

> **Status:** implemented (2026-05-29) — T1 review resolved the `aceengineer-strategy` open question (live-verified sibling); corrected ALL tier-1 siblings + regenerated `context.md` from the template; added anti-drift regression test.
> **Complexity:** T1
> **Date:** 2026-05-27
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2814
> **Client:** N/A
> **Review artifacts:** scripts/review/results/2026-05-29-2814-claude.md (T1 plan+code; APPROVE)
>
> **Implementation note (2026-05-29):** The `aceengineer-strategy` "open question" below is RESOLVED — live `.git` probe confirms it (and `digitalmodel`/`worldenergydata`/`assetutilities`/`assethold`) are all siblings at `/mnt/local-analysis/`. The fix edits the bridge heredoc template and regenerates `context.md` from it (faithful quoted-heredoc extraction — NOT a hand-edit), removing the prior `*stale:*` drift markers. `tests/memory/test_context_md_bridge_sync.py` locks the heredoc↔context.md sync so this drift cannot recur. Scoped to the Linux layout section; Windows (`D:\workspace-hub\`, genuinely nested) untouched.

---

## Resource Intelligence Summary

### Existing repo code

- **FOUND**: `scripts/memory/bridge-hermes-claude.sh` — the bridge script that generates
  `.claude/memory/context.md` at runtime via a heredoc (`cat > "${MEMORY_DIR}/context.md"
  << 'CONTEXT_EOF'` at line 129; heredoc ends at line 186). The stale layout claim is in
  this heredoc at lines 152–155:
  ```
  - `digitalmodel/` — **separate git repo** (vamseeachanta/digitalmodel.git), gitignored by parent
    - Commits MUST be made from inside `digitalmodel/` — not from workspace-hub root
  - `aceengineer-strategy/` — private GTM strategy repo, nested, gitignored by parent
  - `worldenergydata/` — energy data sub-repo
  ```
  These list `digitalmodel` and `worldenergydata` as relative paths implying they live
  inside workspace-hub. They do not — they are siblings at `/mnt/local-analysis/`.
- **FOUND**: `.claude/memory/agents.md` — authoritative correct claim: "Workspace-hub
  tier-1 repos live as siblings under `/mnt/local-analysis/<repo>`; `workspace-hub` at
  `/mnt/local-analysis/workspace-hub` is the harness/control-plane, not a parent for
  nested tier-1 checkouts."
- **FOUND**: `.claude/memory/context.md` — statically committed generated file; reproduces
  the stale template because the bridge has not been re-run with a corrected template.
- **NUANCE — aceengineer-strategy**: `agents.md` also calls this "private nested repo"
  (`*stale: 2026-05-25*`). This repo may genuinely be nested inside workspace-hub (unlike
  tier-1 siblings). The plan preserves its "nested" description pending live confirmation,
  but flags it as an open question.

### Standards

Not applicable — documentation fix.

### LLM Wiki pages consulted

No relevant wiki pages.

### Documents consulted

- `.claude/memory/agents.md` — canonical authoritative sibling layout claim (source #2)
- `scripts/memory/bridge-hermes-claude.sh` lines 129–186 — heredoc template generating
  context.md; source of the stale claim (source #3)
- Issue #2801 (machine-equality) — confirmed sibling layout on ace-linux-1 via live `ls`
  (source #4)
- `.claude/memory/context.md` — the statically committed generated file with stale claim
  (source #5)

### Gaps identified

- Bridge script heredoc at lines 152–155 omits absolute paths for tier-1 siblings.
- The committed `context.md` reflects the stale template (bridge regeneration required
  or manual sync after template fix).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-27 via GitHub MCP):
- `#2814` — OPEN — docs(harness): fix stale context.md repo-layout claim (siblings vs nested)

**File existence** (`ls` 2026-05-27):
- EXISTS: `scripts/memory/bridge-hermes-claude.sh` (292 lines)
- EXISTS: `.claude/memory/context.md`
- EXISTS: `.claude/memory/agents.md`

**Line excerpts — bridge script (lines 147–156, the stale Workspace Layout section):**
```
## Workspace Layout (Linux)

- `/mnt/local-analysis/workspace-hub/` — the real git repo mount
- `~/workspace-hub` — **sparse overlay** on ace-linux-1; writes may fail silently
- `digitalmodel/` — **separate git repo** (vamseeachanta/digitalmodel.git), gitignored by parent
  - Commits MUST be made from inside `digitalmodel/` — not from workspace-hub root
- `aceengineer-strategy/` — private GTM strategy repo, nested, gitignored by parent
- `worldenergydata/` — energy data sub-repo
```

**Authoritative counter-claim in agents.md (grep verified 2026-05-27):**
```
Workspace-hub tier-1 repos live as siblings under `/mnt/local-analysis/<repo>`;
`workspace-hub` at `/mnt/local-analysis/workspace-hub` is the harness/control-plane,
not a parent for nested tier-1 checkouts.
```

**Gap proofs:**
```
$ grep "mnt/local-analysis/digitalmodel" .claude/memory/context.md
(no output — absolute sibling path not present in current context.md)

$ grep "mnt/local-analysis/worldenergydata" .claude/memory/context.md
(no output — absolute sibling path not present)
```

**Reproduction proofs:** N/A — documentation correctness issue; no runtime failure to
reproduce. The "failure" is verified by comparing bridge script lines 152–155 against
`agents.md`. Skip-allowed per issue-planning-mode Step 1.5: "documentation-only ... has
no runtime claim to verify."

<!-- Verification: sources = issue body (#1) + agents.md (#2) + bridge script (#3) +
     #2801 machine-equality (#4) + context.md (#5). Count: 5 ≥ 3. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-27-issue-2814-fix-stale-context-layout.md` |
| Bridge template fix | `scripts/memory/bridge-hermes-claude.sh` (lines 152–155) |
| Generated file sync | `.claude/memory/context.md` (Workspace Layout section) |
| Plan review — Claude | `scripts/review/results/2026-05-27-plan-2814-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-27-plan-2814-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-27-plan-2814-gemini.md` |

---

## Deliverable

`scripts/memory/bridge-hermes-claude.sh` heredoc updated so it correctly describes
`digitalmodel` and `worldenergydata` as tier-1 siblings at `/mnt/local-analysis/<repo>`,
not as repos nested under workspace-hub. The committed `.claude/memory/context.md` synced
to the corrected template immediately; future bridge runs will regenerate from the corrected
template automatically.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/memory/bridge-hermes-claude.sh` | fix Workspace Layout heredoc at lines 152–155 |
| Modify | `.claude/memory/context.md` | sync the committed generated file to corrected template |
| Update | `docs/plans/README.md` | add this plan to index |

**Proposed corrected heredoc block (lines 152–158 replacement):**

```markdown
## Tier-1 sibling repos (on ace-linux-1)
- `/mnt/local-analysis/digitalmodel/` — separate git repo (vamseeachanta/digitalmodel.git);
  commits MUST be made from inside `digitalmodel/` — not from workspace-hub root
- `/mnt/local-analysis/worldenergydata/` — energy data repo (vamseeachanta/worldenergydata.git)
- `/mnt/local-analysis/aceengineer-strategy/` — private GTM strategy repo (sibling on ace-linux-1;
  may also appear nested inside workspace-hub on some machines — see open question below)

## Repos nested inside workspace-hub (gitignored by parent)
- `aceengineer-strategy/` — confirm per machine; nested on some configs *stale pending #2814*
```

Note: the exact wording is implementation-level detail; the key constraints are that
`digitalmodel` and `worldenergydata` must show absolute sibling paths, and the "gitignored
by parent" language for them must be removed or qualified.

---

## TDD Test List

For a documentation fix, the "tests" are grep-based verification checks run after the fix:

| Check | Command | Expected |
|---|---|---|
| bridge no longer uses relative path for digitalmodel | `grep "^\- \`digitalmodel/\`" scripts/memory/bridge-hermes-claude.sh` | 0 lines |
| bridge no longer uses relative path for worldenergydata | `grep "^\- \`worldenergydata/\`" scripts/memory/bridge-hermes-claude.sh` | 0 lines |
| context.md describes sibling path for digitalmodel | `grep "mnt/local-analysis/digitalmodel" .claude/memory/context.md` | ≥1 line |
| context.md describes sibling path for worldenergydata | `grep "mnt/local-analysis/worldenergydata" .claude/memory/context.md` | ≥1 line |
| no other memory file uses the stale nested claim | `grep -r "digitalmodel.*gitignored by parent\|worldenergydata.*nested" .claude/memory/` | 0 lines |

---

## Acceptance Criteria

- [ ] `scripts/memory/bridge-hermes-claude.sh` heredoc no longer describes `digitalmodel`
  or `worldenergydata` with bare relative paths (implying nesting under workspace-hub)
- [ ] Both repos now appear with their absolute sibling paths (`/mnt/local-analysis/<repo>/`)
  in the bridge heredoc
- [ ] `.claude/memory/context.md` Workspace Layout section updated to match the corrected
  bridge template
- [ ] `aceengineer-strategy/` description preserved (potentially nested — do not change without
  live verification on ace-linux-1)
- [ ] `grep -r "digitalmodel.*gitignored by parent\|worldenergydata.*nested" .claude/memory/` → 0 hits
- [ ] All 5 grep checks in TDD Test List pass

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | TBD | — |
| Codex | TBD | — |
| Gemini | TBD | — |

**Overall result:** PENDING (review not yet run)

---

## Risks and Open Questions

- **Risk (bridge overwrites fix):** If the bridge cron runs between the bridge script fix
  being committed and the `context.md` fix being committed, it would regenerate `context.md`
  from the corrected template — which is FINE (the corrected template is the source of truth).
  Commit the bridge script fix first; commit `context.md` fix in the same push or immediately
  after.
- **Risk (aceengineer-strategy layout ambiguity):** `agents.md` calls it nested; the issue
  does not clarify. This plan preserves the current description as nested pending live
  verification on ace-linux-1 (`ls /mnt/local-analysis/` and `ls workspace-hub/`). If it
  is also a sibling, a follow-on one-liner fix can update it.
- **Risk (ace-linux-2 partial checkout):** From `agents.md`, `digitalmodel` and
  `worldenergydata` were absent on ace-linux-2 during the #2801 probe. The context.md Layout
  section should add a per-machine availability note (e.g., "not checked out on ace-linux-2
  as of 2026-05-16") to avoid future confusion.
- **Open:** Is there a `--dry-run` flag on `bridge-hermes-claude.sh` for validation? From
  a quick scan of the script: the bridge runs live commands. Implementer should comment out
  the bridge invocation and only update both files manually, then verify with the grep checks.

---

## Complexity: T1

**T1** — documentation fix in 2 files (bridge script heredoc + committed generated file).
No code change, no test suite (grep checks are the acceptance gates), no new dependencies.
