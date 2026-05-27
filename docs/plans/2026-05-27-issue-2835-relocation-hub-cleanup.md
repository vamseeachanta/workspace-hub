# Plan for #2835: Remove relocated wiki content + retarget wiki_health_cron

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-05-27
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2835
> **Client:** N/A
> **Project:** (none)
> **Review artifacts:** inline Claude adversarial review (below); dispatched Codex/Gemini optional per scope

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/knowledge/wiki_health_cron.py:23-25` — `REPO_ROOT/knowledge/wikis`, `REPORTS_DIR = WIKIS_DIR/"health-reports"`. This cron is the ONLY functional writer of the health-reports files.
- Found: `scripts/content/wiki-to-website.py` — the only functional reference to the 3 software-entity pages being removed.
- Found: `scripts/data/llm-wiki/resolve_wiki_path.py:29` — `resolve_wiki_dir()` resolves the wiki data dir (env `LLM_WIKI_DATA_DIR` → `config/llm-wiki.yaml` → `data/llm-wiki` symlink → fallback `REPO_ROOT/knowledge/wikis`).

### LLM Wiki pages consulted
- llm-wiki `wikis/engineering/wiki/entities/{shell-scripting-patterns,python-type-safety,jsonl-knowledge-stores}.md` — merged via llm-wiki#120 (verified on origin/main).
- llm-wiki `docs/reports/wiki-health/health-2026-*.{json,md}` — 12 files merged via llm-wiki#121 (verified on origin/main).
- assethold `docs/domain/realestate/real-estate-analysis.md` — merged via assethold#53.

### Documents consulted
- [llm-wiki#118](https://github.com/vamseeachanta/llm-wiki/issues/118) — parent relocation coordination issue.
- `.claude/rules/coding-style.md` — no hardcoded absolute paths (enforced: `scripts/enforcement/check-no-abs-paths.sh`).
- `config/agents/claude/memory-snapshots/project_llm_wiki_spunout.md` — confirms personal/health-reports were "workspace-hub-internal".

### Gaps identified
- No mechanism currently routes wiki_health_cron output outside `knowledge/wikis/`.

### Evidence (embedded verification)

**Issue/PR statuses** (verified 2026-05-27 via `gh`):
- `workspace-hub#2835` — OPEN — this issue
- `llm-wiki#120` — MERGED; `llm-wiki#121` — MERGED; `assethold#53` — MERGED; `achantas-data#117` (revert) — MERGED

**Removal-impact (functional refs, `git grep` scoped to scripts/config/tests/skills):**
- `shell-scripting-patterns` / `python-type-safety` / `jsonl-knowledge-stores` → 1 ref each: `scripts/content/wiki-to-website.py`
- `real-estate-analysis` → 0 refs
- `wikis/health-reports` functional → 1 writer: `scripts/knowledge/wiki_health_cron.py` (others are historical review records)

**index.md references** (`knowledge/wikis/personal/wiki/index.md:17-20`): 4 entity rows present.

- Reproduction: N/A — cleanup/refactor, no alleged runtime failure.
- Source count: 6 (issue + 5 others).

---

## Deliverable
The 16 relocated files removed from workspace-hub, `wiki_health_cron.py` writing to a non-`knowledge/wikis` location, and all dangling references updated — with no broken hub automation.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Delete | `knowledge/wikis/personal/wiki/entities/real-estate-analysis.md` | merged → assethold#53 |
| Delete | `knowledge/wikis/personal/wiki/entities/shell-scripting-patterns.md` | merged → llm-wiki#120 |
| Delete | `knowledge/wikis/personal/wiki/entities/python-type-safety.md` | merged → llm-wiki#120 |
| Delete | `knowledge/wikis/personal/wiki/entities/jsonl-knowledge-stores.md` | merged → llm-wiki#120 |
| Delete | `knowledge/wikis/health-reports/health-2026-*.{json,md}` (12) | merged → llm-wiki#121 |
| Modify | `scripts/knowledge/wiki_health_cron.py` | `REPORTS_DIR` → `REPO_ROOT/docs/reports/wiki-health`; drop now-moot `health-reports` domain exclusion |
| Modify | `scripts/content/wiki-to-website.py` | update/remove the 3 personal-entity references |
| Update | `knowledge/wikis/personal/wiki/index.md` | remove the 4 entity rows; note relocation |
| Create | `tests/knowledge/test_wiki_health_cron_paths.py` | assert REPORTS_DIR resolves under docs/reports, not knowledge/wikis |

---

## Design decision: cron output target

**Recommended (low-coupling):** cron writes to **hub-local** `docs/reports/wiki-health/`. The 12 historical reports already published to llm-wiki (#121) are the relocation snapshot; ongoing telemetry stays where the cron runs. Avoids the cross-repo-writer coupling that made `data/document-index` non-relocatable (a hub cron dirtying the llm-wiki clone working tree on every run).

**Alternative (user may prefer):** cron writes directly into a configured llm-wiki clone via `resolve_wiki_dir().parent/"docs/reports/wiki-health"`. Requires `LLM_WIKI_DATA_DIR`/symlink configured AND a commit step in the clone — rejected as default for the coupling reason above. **Open question for approval.**

---

## TDD Test List

| Test | Verifies | Expect |
|---|---|---|
| test_reports_dir_under_docs | REPORTS_DIR is under `docs/reports`, not `knowledge/wikis` | path assertion |
| test_no_absolute_path_literal | cron has no hardcoded `/mnt` path | `check-no-abs-paths.sh` passes |
| test_get_wiki_domains_excludes_reports | domain list no longer depends on health-reports exclusion | health-reports absent |

---

## Acceptance Criteria
- [ ] 16 files removed; `git grep` for the 4 entity basenames + `wikis/health-reports` returns only historical (docs/logs/review-results) hits
- [ ] `scripts/content/wiki-to-website.py` no longer references removed entities (runs clean)
- [ ] `wiki_health_cron.py` writes to `docs/reports/wiki-health/`; `uv run scripts/knowledge/wiki_health_cron.py` succeeds
- [ ] `scripts/enforcement/check-no-abs-paths.sh` passes
- [ ] `index.md` updated; no dangling `[[...]]` to removed pages
- [ ] New test passes; no regression in `tests/knowledge/`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (inline) | MINOR | See findings below — addressed in plan |

**Findings & resolutions:**
1. *Removing `knowledge/wikis/personal/entities` breaks `resolve_wiki_dir()` fallback for the personal domain.* → Resolved: personal wiki was internal-only (per spunout snapshot); fallback consumers don't depend on these 4 pages (only `wiki-to-website.py`, being updated). engineering canonical lives in llm-wiki.
2. *`wiki-to-website.py` may hard-fail on missing entity files.* → Plan updates that script in the same change; verify it degrades gracefully or drops the references.
3. *Cron lints `knowledge/wikis` fallback (sparse), not the real llm-wiki domains.* → Pre-existing condition, out of scope; this plan only changes the OUTPUT dir, not the lint source.
4. *Health-report removal before cron retarget = regeneration.* → Sequence enforced: retarget cron first (same PR), then delete the 12 files.

**Overall result:** PASS (proportional T2; dispatched Codex/Gemini review available on request).

---

## Risks and Open Questions
- **Open (for approval):** cron output target — hub-local `docs/reports/wiki-health/` (recommended) vs. cross-repo write into llm-wiki clone. Pick before implement.
- **Risk:** `wiki_health_cron` scheduler is not in the user crontab — confirm the actual scheduler (systemd/Hermes) so the retarget takes effect where it runs.
- **Risk:** llm-wiki `CLAUDE.md` still declares "public OSS" though the repo went PRIVATE 2026-05-20 — out of scope here, but flagged for a separate fix.

---

## Complexity: T2
Multi-file cleanup + one cron code change + new test; one existing script modified. No new module.
