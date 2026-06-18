# Plan for #3208: skill-index coherence/drift check (reshaped)

> **Status:** adversarial-reviewed (r1 Claude MAJOR — day-one drift surfaced; scope decision pending)
> **Complexity:** T2
> **Date:** 2026-06-18
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3208
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-18-plan-3208-claude.md

> Acceptance reshaped (operator-approved 2026-06-18) — the original (a)/(b) rested on wrong
> premises (id-namespace mismatch; no `when_to_use` in the graph). See the issue comment.

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/ai/build_skill_index.py` — generates `config/agents/skill-index-full.yaml` (833 flat entries). `--check` prints to stdout without writing (deterministic; sorted by id, date-pinned header, no timestamp). Records `when_to_use_source ∈ {frontmatter, section, trigger, backfill}` (lines 77-84). Excludes `_*` families.
- Found: `config/agents/skill-index-full.yaml` — 833 entries; ids are the actual `.claude/skills` family path (e.g. `business/communication/brand-guidelines`). **559/833 are `backfill` source.**
- Found: `.planning/skills/skills-knowledge-graph.yaml` — curated `nodes[].id` in **`<repo>/<skill>`** form (e.g. `workspace-hub/brand-guidelines`); fields are `capabilities`/`domain`/`input_types` — **no `when_to_use`** (grep = 0). `config/agents/skill-graph-index.yaml` mirrors it as `by_domain` lists (51 ids).
- Found: `.github/workflows/enforcement-gate.yml` — each check is a job (checkout + run step); model-id-sourcing job at l.226-235 is the template. `config/agents/README.md` exists (model hierarchy + file map) — needs a skill-index section.
- Pattern: `scripts/enforcement/check-wiki-sibling-frontmatter.py` (python enforcement check) + `tests/enforcement/test_*` — precedent for a **python** check (yaml-native) despite the issue naming `.sh`.

### Gaps identified
- No coherence check exists; the two artifacts can drift undetected.
- **Reshape rationale (verified):** curated↔full ids are different namespaces (`<repo>/skill` vs `<family-path>/skill`) → naive subset = 50/51 false "missing"; the graph has no `when_to_use` to override. So (a) must join by basename; (b) must target SKILL.md authored intent, not the graph.

### Evidence
- `python` overlap probe (2026-06-18): curated 51 nodes, **50 missing** from full by raw id; graph `when_to_use` fields = **0**; full `backfill` entries = **559/833**.
- Same skill, different id: curated `workspace-hub/brand-guidelines` vs full `business/communication/brand-guidelines` (confirmed via grep).
- `build_skill_index.py --check` exists and is deterministic (header pin, `sort_keys=True`).

<!-- sources: issue + build_skill_index.py + full index + knowledge-graph + skill-graph-index + enforcement-gate.yml + README = 7 -->

---

## Deliverable

`scripts/enforcement/check-skill-index-coherence.py` (+ an enforcement-gate CI job) that fails on three real drift classes — curated skill removed/renamed, SKILL.md-authored `when_to_use` silently backfilled, and a stale (non-regenerable) full index — plus a `config/agents/README.md` section documenting the curated-graph vs full-index split.

---

## Design / Pseudocode

`scripts/enforcement/check-skill-index-coherence.py` (python; stdlib + pyyaml; exit 1 on any failure, `SKILL_INDEX_COHERENCE_ALLOW=1` bypass per the enforcement convention):
```
load full = skill-index-full.yaml -> {id: entry}
full_basenames = { id.split("/")[-1] for id in full }

# (a) basename coherence — curated skill still exists somewhere in the full tree
curated_ids = nodes[].id (knowledge-graph) ∪ by_domain values (skill-graph-index)
for cid in curated_ids:
    if cid.split("/")[-1] not in full_basenames: FAIL("curated skill '<cid>' has no match in full index (removed/renamed)")

# (b) authored when_to_use not silently backfilled
HEADING = regex (?im)^#{1,4}\s*(when[\s_-]?to[\s_-]?use|trigger)\b   # heading-anchored -> low false positive
for entry where entry.when_to_use_source == "backfill":
    body = read .claude/skills/<entry.id>/SKILL.md
    if HEADING matches body OR frontmatter has when_to_use:
        FAIL("'<id>' authored a when_to_use heading but the index backfilled it (parser miss / stale)")

# (c) deterministic regen
out = subprocess(build_skill_index.py --check)            # uv run, python3 fallback
if out != committed skill-index-full.yaml: FAIL("full index is stale — regenerate via build_skill_index.py")

exit 1 if any FAIL else 0
```
Notes: (a) accepts the namespace difference (basename existence, not id equality). (b) is heading-anchored so a skill merely *mentioning* "use this when…" in prose doesn't false-flag. (c) is the comprehensive staleness guard.

`config/agents/README.md` — add a "Skill index (two artifacts)" section: curated `skill-graph-index.yaml`/`skills-knowledge-graph.yaml` (51 nodes, edges/feed-chains, repo-keyed, hand-curated) vs generated `skill-index-full.yaml` (833 flat entries, family-path-keyed, `build_skill_index.py`, never hand-edit) + the coherence check that binds them.

`.github/workflows/enforcement-gate.yml` — new job `skill-index-coherence` mirroring the model-id-sourcing job (checkout fetch-depth 0 → `uv run python scripts/enforcement/check-skill-index-coherence.py` → step summary).

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/enforcement/check-skill-index-coherence.py` | the three coherence checks |
| Create | `tests/enforcement/test_check_skill_index_coherence.py` | fixtures per check |
| Modify | `.github/workflows/enforcement-gate.yml` | new CI job |
| Update | `config/agents/README.md` | document curated-graph vs full-index |
| Update | docs/plans/README.md | index |

---

## TDD Test List

| Test | Verifies | Expected |
|---|---|---|
| test_clean_tree_passes | all 3 checks pass on a coherent fixture | exit 0 |
| test_curated_removed_skill_fails | curated basename absent from full | exit 1 + "removed/renamed" |
| test_curated_namespace_diff_does_not_false_fail | curated `repo/x` vs full `fam/x` (same basename) | exit 0 (no false drift) |
| test_authored_heading_backfilled_fails | SKILL.md has `## When to Use` but index source=backfill | exit 1 + "backfilled" |
| test_prose_mention_not_flagged | body says "use this when…" (no heading) + backfill | exit 0 (no false positive) |
| test_stale_index_fails | committed index != `--check` output | exit 1 + "stale" |
| test_bypass_env_allows | `SKILL_INDEX_COHERENCE_ALLOW=1` | exit 0 despite drift (logged) |

---

## Acceptance Criteria

- [ ] `check-skill-index-coherence.py` implements (a) basename coherence, (b) authored-not-backfilled, (c) deterministic-regen; exit 1 on drift
- [ ] CI job in enforcement-gate.yml runs it; drift fails the build
- [ ] `config/agents/README.md` documents curated-graph vs full-index roles + the check
- [ ] Runs clean against the CURRENT repo (no pre-existing drift) — or the plan surfaces real drift it finds
- [ ] `uv run pytest tests/enforcement/test_check_skill_index_coherence.py -v` green; no regression
- [ ] Review artifact posted

---

## Adversarial Review Summary

**r1 — Claude (adversarial subagent), 2026-06-18:** verdict **MAJOR** — the gate would be RED on day one (verified empirically), on pre-existing drift:

| # | Sev | Finding (verified) | Resolution |
|---|---|---|---|
| 1 | MAJOR | check (b) fails **138** entries today: generator `_section` regex (`build_skill_index.py:52`) matches `## When to Use$` exact only → `## When to Use This Skill`, `## Trigger Conditions`, `### …` all fall to `backfill`. Root cause is the generator, not stale data (a real router-quality bug: 138 authored when_to_use ignored). | scope decision A/B/C below |
| 2 | MAJOR | check (a) fails **10** curated ids: 3 live in excluded `_archive`/`_internal` families (false-positive), 7 truly absent (real unreconciled drift). | reconcile curated graph (git-log each; drop/repoint) + explicit `_*`-family rule |
| 3 | MAJOR | "drift fails the build" is false — `main` is unprotected, no required checks; a new job runs red but doesn't block (same as existing checks). | relabel CI job **advisory**; required-check wiring = separate operator action |
| 4 | MINOR | (a) basename existence is weak (6 duplicate basenames → false negatives). | accept as tripwire; possible family-tail crosswalk follow-up |
| ok | — | check (c) regen==committed **PASSES** today; entry.id→path correct (833/833); determinism portable. | — (if generator widened, MUST regenerate+recommit in same PR) |

**r2 — Codex:** UNAVAILABLE (env timeout, 3× this session).

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR | day-one red on (a)=10 + (b)=138; see table |

**Implementation (option A, operator-approved):** widened `build_skill_index.py` `_section` regex (depth + prefix) → regenerated index (backfill 559→464; 103 upgraded to real section sources); checker (a) whole-tree basename + 8-id `KNOWN_STALE_CURATED` allowlist (cleanup follow-up [#3214](https://github.com/vamseeachanta/workspace-hub/issues/3214)); (b) advisory (43 residual heading-variants reported); (c) deterministic-regen. CI job advisory. Runs **clean on HEAD**.

**Code-stage r3 — Claude (adversarial subagent), 2026-06-18:** verdict **MINOR** (ships safely; no blockers). Fixed: F1 prefix-match mis-bound `creative/claude-design` → prefer exact heading over prefix; F4 `(c)` CRLF-fragile compare → splitlines. Accepted/flagged: F2 code-fence `#`-comment truncation (latent, nil impact today), F3 basename-join specificity (known tripwire limitation; family-suffix join is a possible follow-up). Verified correct: `\b` boundaries, no catastrophic backtracking, determinism byte-stable, (b) advisory heading-anchored, KNOWN_STALE_CURATED exact (8/8, no dead entries), tests drive real functions.

**r2 — Codex:** UNAVAILABLE (env timeout, repeated this session).

---

## Risks and Open Questions

- **Risk — check (a) basename ambiguity:** duplicate skill basenames across families make basename-existence a weak (existence-only) check; it confirms "a skill of this name exists," not "the curated node's intended skill." Acceptable for drift-detection (catches removed/renamed); a stronger id-mapping is a possible follow-up. Flagged.
- **Risk — check (b) false positives:** heading-anchored regex minimizes them, but a SKILL.md with a `## Trigger` section that is genuinely not a when-to-use could flag. Mitigation: the bypass env + a per-line allow sentinel if a real case appears; (b) is advisory-leaning.
- **Risk — running clean today:** the check must pass on the current repo. If it surfaces REAL drift (e.g. a curated skill already removed, or an authored-but-backfilled skill), the plan will either fix the drift or document it as a pre-existing finding for a separate fix — implementation step 0 is "run it against HEAD and triage."
- **Naming deviation:** issue says `.sh`; implementing as `.py` (yaml-native, testable, matches `check-wiki-sibling-frontmatter.py` precedent). Flagged for approval.
- **Resolved (pre-plan):** the id-namespace + missing-`when_to_use` premise breaks (reshaped acceptance, operator-approved).

## Complexity: T2

**T2** — new enforcement check + CI + tests + docs; built on #3190's generator. Review = Claude inline (+ Codex if env permits; it has timed out repeatedly this session).
