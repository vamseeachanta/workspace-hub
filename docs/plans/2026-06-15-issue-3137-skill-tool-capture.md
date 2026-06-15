# Plan for #3137: Skill-invocation — capture Skill-tool calls (id→short_name resolution)

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-06-15
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3137
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-15-plan-3137-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `.claude/hooks/session-logger.sh` — the #3112 PostToolUse producer. Lines 31-40 emit `skill_name` (a rel-path under `.claude/skills/`) **only** for a `Read` of `*/.claude/skills/*/SKILL.md`. It parses `.tool_input.file_path`/`.tool_input.path` (line 27) and `.session_id` (line 29). It has NO awareness of the `Skill` tool or the `.tool_input.skill` field.
- Found: `scripts/skills/skill-invocation-scanner.py` — `scan_sessions()` joins events on `event.get("skill_name")` (line 77); `discover_skills()` walks `root.rglob("SKILL.md")` with **no `_archive`/`_core`/`_internal` exclusion** (line 99); `derive_short_name()` (line 105) = frontmatter `name` lowercased else dir basename; `classify()` (line 131) outputs rows keyed by `short_name`.
- Found: `scripts/skills/skill-usage-report.py` — `load_invocation_data()` (line 334) reads rows keyed by `skill` (the short_name); `apply_invocation_demotion()` (line 355) demotes one tier when `session_count == 0 and coverage_days >= MIN_COVERAGE_DAYS` (=14, line 331). `scan_skills()` (line 78) **excludes** `_archive`/`_core`/`_internal` (lines 86-88).
- Gap: no code path captures `Skill`-tool invocations; the entire signal today is Read-of-SKILL.md only. Plugin-namespaced ids (`<plugin>:<name>`) have no normalization path.

### Standards
Not applicable (harness/infrastructure issue).

### LLM Wiki pages consulted
No relevant wiki pages (harness instrumentation, not knowledge content).

### Documents consulted
- Issue #3137 body — decided scope: ALSO capture `Skill` tool calls; normalize `<plugin>:<name>` → canonical short_name; flag plugin skills not in `.claude/skills`; add to matcher only after the contract is empirically confirmed.
- Sibling #3139 (OPEN) — "reconcile scanner-vs-report skill universe (3,180 vs 833)". This plan's verification reproduced both figures exactly. **The universe-reconciliation is #3139's scope, not this issue's** — see Dependencies.
- Sibling #3138 (OPEN) — "backfill historical events from transcripts". The 1,080 historical `Skill` tool_use records this plan found are #3138's input corpus, not re-emitted by this issue. See Dependencies.
- `.claude/settings.json` — PostToolUse matcher for `session-logger.sh post` is `Bash|Read|Write|Edit|MultiEdit|Glob|Grep|Agent|Task` (line 174). `Skill` is absent → the hook never sees Skill-tool calls today.
- `tests/skills/test_skill_invocation_e2e.py` — the #3112 e2e proving emit→scan→demote composes on `short_name`. New tests follow this harness pattern.

### Gaps identified
- `session-logger.sh` does not parse `.tool_input.skill`, does not normalize `<plugin>:<name>`, and is not subscribed to the `Skill` tool.
- No mapping table or function from a namespaced/bare skill id to a workspace-hub short_name.
- No mechanism to record-but-flag a plugin-only id (e.g. `codex:rescue`) that has no `.claude/skills/` counterpart.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-15T18:42:17Z via `gh issue view`):
- `#3137` — OPEN — Skill-invocation: capture Skill-tool calls (id→short_name resolution) — follow-on to #3112
- `#3139` — OPEN — reconcile scanner-vs-report skill universe (3,180 vs 833) — follow-on to #3112
- `#3138` — OPEN — backfill historical events from transcripts — follow-on to #3112
- `#3112` — OPEN — Harden: instrument true skill/command invocation — epic #3058

**File existence** (verified 2026-06-15):
- EXISTS: `.claude/hooks/session-logger.sh`
- EXISTS: `scripts/skills/skill-invocation-scanner.py`
- EXISTS: `scripts/skills/skill-usage-report.py`
- EXISTS: `.claude/settings.json`
- MISSING (new — this plan creates): `tests/skills/test_skill_tool_capture.py`

**Q1 — Does PostToolUse fire for `Skill`, and what is the id field?**

Empirical scan of `~/.claude/projects/**/*.jsonl` (610 transcripts contain `Skill` tool_use records; 1,080 such records total):

```
=== Total Skill tool_use records: 1080
=== input field keys (Counter): {'skill': 1080, 'args': 896}
=== Sample inputs (first 15):
   {"skill": "superpowers:executing-plans"}
   {"skill": "superpowers:test-driven-development"}
   {"skill": "gsd:fast"}
   {"skill": "work", "args": "run 1323"}
   {"skill": "gsd:plan-phase", "args": "7"}
   {"skill": "data:md-to-pdf"}
   {"skill": "codex:rescue"}
   {"skill": "gsd-pause-work"}
   {"skill": "corporate-tax-form-fill"}
```

- **Id field is `input.skill` in 1080/1080 records.** A free-form arg string is under `input.args` (896/1080). `.tool_name == "Skill"`.
- **Hookability:** Claude Code hooks docs (verified via claude-code-guide subagent against https://code.claude.com/docs/en/hooks.md) list `Skill` as a standard hookable tool name — a `PostToolUse` matcher `Read|Skill` WILL fire on Skill invocations. **VERDICT: the hook fires and the id is resolvable.**
- **CONTRADICTION TO FLAG:** the docs-summary claimed the field is `.tool_input.skill_name`. The transcript evidence is unambiguous: it is `.tool_input.skill` (mirroring the assistant tool_use `input.skill`); `skill_name` NEVER appears as a Skill-tool input field. `grep -ho '"skill_name":"..."'` across all transcripts returned zero Skill-input matches (the only `skill_name` occurrences are session-logger's own Read-emit OUTPUT). **The implementation MUST read `.tool_input.skill` with `.tool_input.skill_name` only as a defensive fallback** (in case a future harness version renames it), and the design fails safe (records the raw id) if neither is present.

**Q2 — How does `<plugin>:<name>` map to a workspace-hub short_name? Are plugin skills under `.claude/skills/`? Quantify.**

Invocations by namespace prefix (1080 records):

```
  codex              815   (external plugin: ~/.claude/plugins/cache/openai-codex/codex)
  (bare)             108
  superpowers         97   (external plugin: ~/.claude/plugins/cache/claude-plugins-official/superpowers)
  gsd                 32
  workspace-hub       24
  data                 1
  field-dev            1   (matches a wshub bare skill: field-dev-code-recon — but only the prefix split)
  automation           1
  select               1
```

Resolution test — does the `<name>`-part match a workspace-hub short_name OR dir basename?

```
  namespace           resolves  no-match
  codex                      0       815   (plugin-only; NOT in .claude/skills)
  (bare)                    40        68
  superpowers               59        38   (superpowers skills mostly NOT mirrored in wshub tree)
  gsd                        5        27
  workspace-hub             10        14
  data                       1         0
```

- **Plugin skills are NOT under `.claude/skills/`.** `superpowers`, `codex`, `gsd`, `data` live under `~/.claude/plugins/cache/{claude-plugins-official,openai-codex}/` (verified by `ls`). 67 plugin SKILL.md total off-repo. So `codex:*` (815 invocations, 75% of all Skill calls) and most `superpowers:*` resolve to NOTHING in the workspace-hub tree — they must be **recorded-and-flagged**, never silently dropped (issue acceptance criterion).
- **`workspace-hub:<name>` is the namespace that SHOULD map**, but only 10/24 resolved. Detail:
```
  workspace-hub:repo-sync           -> OK
  workspace-hub:ecosystem-terminology -> OK
  workspace-hub:repo-structure      -> OK
  workspace-hub:work                -> NO-MATCH   (no 'work' SKILL.md; likely a command, not a skill)
  workspace-hub:knowledge           -> NO-MATCH
  workspace-hub:whats-next          -> NO-MATCH
```
  The `workspace-hub:` namespace is the plugin-style exposure of the repo's own skills/commands; not every id is a SKILL.md (some are slash-commands). Resolution must therefore be **best-effort with an explicit unresolved/plugin flag**.

**Q3 — Does session-logger currently see Skill-tool calls?**

`.claude/settings.json` PostToolUse registration for `session-logger.sh post`:
```
174:        "matcher": "Bash|Read|Write|Edit|MultiEdit|Glob|Grep|Agent|Task",
178:            "command": "bash .claude/hooks/session-logger.sh post",
```
- **NO.** `Skill` is absent from the matcher. The producer is structurally blind to Skill-tool calls today. (Same matcher on the PreToolUse `pre` registration at line 17.)

**Universe-mismatch cross-check (informs #3139 dependency, NOT this issue's scope):**
```
find .claude/skills -name SKILL.md | wc -l                       -> 3180
   ... under _archive                                            -> 2166
find ... | grep -vE '/_archive/|/_core/|/_internal/' | wc -l     -> 833
```
The scanner's `discover_skills()` (rglob, no exclusion) sees 3,180; the report's `scan_skills()` (excludes `_archive/_core/_internal`) sees 833. **This exactly reproduces #3139's "3,180 vs 833".** This plan does NOT fix that divergence; it consumes whatever universe the scanner exposes (see Risks + Dependencies).

**Reproduction proofs:** N/A — this is an instrumentation gap (no alleged runtime failure to reproduce). The "gap" proofs above (matcher lacks `Skill`; id field is `skill` not `skill_name`; plugin ids resolve to nothing) are the empirical substrate.

<!-- Distinct sources consulted: issue #3137 body, #3139, #3138, settings.json, session-logger.sh, scanner.py, report.py, e2e test, live transcripts, Claude Code hooks docs = 10+. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-15-issue-3137-skill-tool-capture.md |
| Tests | `tests/skills/test_skill_tool_capture.py` (new) |
| Implementation (emit) | `.claude/hooks/session-logger.sh` (modify) |
| Implementation (matcher) | `.claude/settings.json` (modify — gated, last step) |
| Normalizer (optional helper) | `scripts/skills/normalize_skill_id.py` (new — pure fn, unit-testable) |
| Plan review — Claude | scripts/review/results/2026-06-15-plan-3137-claude.md |
| Plan review — Codex | scripts/review/results/2026-06-15-plan-3137-codex.md |
| Plan review — Gemini | scripts/review/results/2026-06-15-plan-3137-gemini.md |

---

## Deliverable

`session-logger.sh` will, on a `Skill` tool PostToolUse event, emit a `skill_name` (canonical short_name when the id resolves to a workspace-hub `.claude/skills/` entry) plus a `skill_source` flag (`workspace-hub` | `plugin` | `unresolved`) and the raw `skill_id`, so Skill-tool invocations join the existing scanner→report short_name chain while plugin-only ids are logged-and-flagged rather than silently dropped. The `Skill` matcher is added to settings.json only as the final step, after the emit contract is test-proven.

---

## id→short_name resolution design

The id from `.tool_input.skill` has three observed shapes. Resolution (pure, no side effects):

```
normalize_skill_id(raw_id, skills_root):
    # 1. split namespace
    if ":" in raw_id:  ns, name = raw_id.split(":", 1)
    else:              ns, name = "", raw_id
    name_l = lower(name)

    # 2. try to resolve <name> against the workspace-hub skill universe:
    #    a) exact dir-basename match under skills_root (excluding _archive/_core/_internal)
    #    b) exact frontmatter-name (lowercased) match
    #    Build the lookup once from `find skills_root -name SKILL.md` (cached per hook run is fine —
    #    single id per call). Reuse derive_short_name semantics from the scanner so keys JOIN.

    # 3. classify source:
    #    - resolved AND (ns == "" or ns == "workspace-hub")  -> source="workspace-hub", skill_name=<short_name>
    #    - resolved but ns is a known external plugin          -> source="plugin", skill_name=<short_name> (still joinable)
    #    - unresolved                                          -> source="unresolved" OR "plugin",
    #                                                             skill_name="" , skill_id=<raw_id> preserved
    return {skill_name, skill_source, skill_id}
```

Key decisions:
- **Emit short_name (the report's join key), not the rel-path.** The Read-path emits a rel-path which the scanner's `derive_short_name` later converts; but for Skill-tool ids we already have only a name, so resolve straight to short_name. The scanner's `classify()` keys rows by short_name, and `load_invocation_data` keys by short_name — so emitting short_name directly is the correct, minimal join. **The scanner must be taught to also accept a pre-resolved short_name event** (today it only joins on rel-path then re-derives). See Files to Change.
- **Plugin-only ids (e.g. `codex:rescue`) are recorded with `skill_source="plugin"` and an empty `skill_name`** so they never demote a non-existent wshub skill, but the raw id is preserved in `skill_id` for #3138 backfill + future plugin-universe work. This satisfies the acceptance criterion "logged + flagged, not silently dropped."
- **No bash-side YAML parsing.** The bash hook can do basename matching cheaply (the existing `case` glob style). Frontmatter-name resolution is a Python concern; to avoid a per-event Python spawn in the hook, v1 resolves by **directory-basename only in bash** (fast, covers the common case), and records `skill_source="unresolved"` when no basename dir exists. The scanner (Python, batch) does the authoritative frontmatter-name → short_name canonicalization at scan time using the existing `derive_short_name`. This keeps the hot-path hook fast and pushes the yaml-aware mapping to the batch scanner where #3112 already lives.

---

## Pseudocode

session-logger.sh additions (after the existing Read-of-SKILL.md `case`, lines 31-40):

```
# Skill-tool capture (#3137). Field is .tool_input.skill (verified 1080/1080);
# fall back to .tool_input.skill_name defensively.
if [ "$TOOL" = "Skill" ]; then
    SKILL_ID=$(jq -r '.tool_input.skill // .tool_input.skill_name // ""' <<<"$INPUT")
    if [ -n "$SKILL_ID" ]; then
        NAME="${SKILL_ID#*:}"                 # strip "<plugin>:" prefix if present
        # basename resolve against skills tree (exclude _archive/_core/_internal)
        HIT=$(find "$WS/.claude/skills" -path '*/_archive/*' -prune -o \
                   -type d -name "$NAME" -print 2>/dev/null | head -1)
        if [ -n "$HIT" ]; then
            SKILL_NAME="$NAME"                # report joins on short_name; basename==short_name common case
            SKILL_SOURCE="workspace-hub"
        else
            SKILL_NAME=""                     # plugin-only / command / unresolved
            SKILL_SOURCE="plugin"
        fi
        # SKILL_ID always preserved in the entry for #3138 + audit
    fi
fi
```

Add `skill_id` and `skill_source` to the `jq -cn` ENTRY builder (only when non-empty), mirroring the existing conditional-merge style (lines 60-64).

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `.claude/hooks/session-logger.sh` | parse `.tool_input.skill`, normalize/resolve, emit `skill_name`+`skill_id`+`skill_source` for Skill-tool calls |
| Create | `scripts/skills/normalize_skill_id.py` | pure id→short_name+source resolver (frontmatter-aware), reusing `derive_short_name`; unit-testable; importable by scanner |
| Modify | `scripts/skills/skill-invocation-scanner.py` | accept events that already carry a resolved short_name in `skill_name` (Skill-tool path) in addition to rel-path events (Read path); reuse `normalize_skill_id` for authoritative frontmatter-name resolution; carry `skill_source` through for reporting |
| Modify | `.claude/settings.json` | add `Skill` to the two `session-logger.sh` matchers (`pre` line 17, `post` line 174) — **GATED: final step, only after emit tests pass** |
| Create | `tests/skills/test_skill_tool_capture.py` | TDD: id-normalization + emit-shape + scanner-join + plugin-flag-not-dropped |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_normalize_bare_resolved | bare id matching a wshub skill resolves | `"corporate-tax-form-fill"` | short_name set, source=`workspace-hub` |
| test_normalize_namespaced_workspace_hub | `workspace-hub:repo-sync` resolves | `"workspace-hub:repo-sync"` | short_name=`repo-sync`, source=`workspace-hub` |
| test_normalize_plugin_unresolved | `codex:rescue` (no wshub skill) flagged not dropped | `"codex:rescue"` | skill_name="", source=`plugin`, skill_id preserved |
| test_normalize_superpowers_unmirrored | superpowers id not in tree | `"superpowers:writing-plans"` | source=`plugin`, skill_id preserved |
| test_normalize_frontmatter_name | resolves via frontmatter `name` not just dir | id whose dir basename differs from `name:` | short_name = lowercased frontmatter name |
| test_emit_field_is_skill_not_skill_name | hook reads `.tool_input.skill` | `{"tool_name":"Skill","tool_input":{"skill":"x"}}` | entry has skill_id="x" |
| test_emit_defensive_fallback | falls back to `.tool_input.skill_name` if `.skill` absent | `{"tool_input":{"skill_name":"y"}}` | entry has skill_id="y" |
| test_emit_no_skill_field_safe | missing both fields → no crash, no skill emit | `{"tool_name":"Skill","tool_input":{}}` | entry written, no skill_name/skill_id |
| test_scanner_joins_skill_tool_event | scanner counts a short_name-keyed Skill event | event `{skill_name:"aqwa",skill_source:"workspace-hub"}` | aqwa row session_count>=1 |
| test_scanner_ignores_unresolved_plugin | plugin event with empty skill_name doesn't fabricate a row | event `{skill_id:"codex:rescue",skill_source:"plugin"}` | no wshub skill demoted by it |
| test_e2e_skill_tool_demotion | Skill-tool event prevents demotion of a real skill | aqwa Skill-event over >=14d | aqwa NOT demoted; mooring (no event) demoted |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest tests/skills/test_skill_tool_capture.py -v`
- [ ] No regression: `uv run pytest tests/skills/ -v` (existing #3112 e2e + scanner + shortname tests stay green)
- [ ] `session-logger.sh` emits `skill_name`+`skill_id`+`skill_source` on a synthetic `{"tool_name":"Skill","tool_input":{"skill":"repo-sync"}}` PostToolUse stdin (bash integration test)
- [ ] A `codex:rescue` Skill event appears in the daily session log with `skill_source:"plugin"` and a non-empty `skill_id` (logged + flagged, NOT dropped)
- [ ] `Skill` added to both `session-logger.sh` matchers in settings.json **only after** the above pass
- [ ] Field is `.tool_input.skill` (with `.tool_input.skill_name` defensive fallback) — verified against the 1080-record empirical finding
- [ ] Review artifacts posted to scripts/review/results/

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | pending | |
| Codex | pending | |
| Gemini | pending | |

**Overall result:** pending

---

## Risks and Open Questions

- **Risk (HIGH):** The Claude-Code-guide docs summary says the Skill id field is `.tool_input.skill_name`, but 1080/1080 live transcript records carry it under `.tool_input.skill`. The PostToolUse `tool_input` envelope mirrors the assistant tool_use `input`, so `.skill` is near-certain — but the harness version could differ. **Mitigation:** read `.tool_input.skill // .tool_input.skill_name` (already in pseudocode) and ship a one-shot bash integration test that feeds a real-shaped payload. A wrong field = silent total signal loss, so this is the single biggest risk and must be verified on the live harness before the matcher is enabled.
- **Risk (HIGH, cross-issue):** 75% of Skill calls are `codex:*` plugin ids that resolve to NOTHING in `.claude/skills/`. If resolution were naive (treat raw id as a skill name) it would fabricate phantom skills or, worse, the report could mis-demote. Design records them with empty `skill_name` + `skill_source=plugin` so they cannot affect demotion. A genuine "plugin-skill universe" is out of scope (no plugin SKILL.md in repo tree) — flagged for a possible follow-on.
- **Risk (MEDIUM):** scanner/report universe divergence (3,180 vs 833) is REAL and reproduced. If the scanner resolves a Skill id via its 3,180-entry rglob universe but the report only classifies 833, a resolved `_archive` skill could get a row the report never tiers (no-op) — tolerable, but the canonical fix belongs to **#3139**. This plan resolves against the *report's* exclusion set (`_archive/_core/_internal` excluded) to stay consistent with where demotion actually applies.
- **Risk (MEDIUM):** bash `find` per Skill event on a 3,180-file tree adds latency to the hook hot-path (timeout 5s in settings.json). **Mitigation:** v1 does a single `-prune` find for the basename; if measured cost is high, precompute a basename→short_name index file (`.claude/state/skill-index.json`) the scanner already could emit. Flag for review.
- **Open:** Should `workspace-hub:work` / `:knowledge` / `:whats-next` (commands, not SKILL.md) be tracked as a separate "command invocation" signal? #3137 scope is skills; recommend recording them as `skill_source=plugin/unresolved` for now and deferring command-tracking to a follow-on.

---

## Dependencies on sibling issues

- **#3139 (universe / short_name reconciliation):** This plan REPRODUCED the 3,180-vs-833 mismatch (scanner `rglob` no-exclusion vs report excludes `_archive/_core/_internal`). #3137 deliberately resolves Skill ids against the *report's* 833-entry exclusion set so demotion stays consistent; it does NOT change `discover_skills()`. If #3139 lands an exclusion fix in the scanner first, #3137's resolution simply inherits the aligned universe. **Ordering:** #3137 can land independently, but its resolver should import/share whatever canonical universe helper #3139 produces to avoid two divergent exclusion lists. Coordinate the shared helper.
- **#3138 (backfill historical events from transcripts):** The 1,080 historical `Skill` tool_use records (`input.skill`, 610 transcripts) are #3138's backfill corpus — this plan does NOT re-emit them. #3138 MUST reuse #3137's `normalize_skill_id` so backfilled events carry identical `skill_name`/`skill_source` semantics as live-captured ones (otherwise the historical and live signals won't join). **Ordering:** land #3137's normalizer first (or concurrently with a shared module) so #3138 backfills through it.

---

## Complexity: T2

**T2** — multi-file (hook + new pure module + scanner + settings + tests), TDD required, harness-touching, with a gated final settings.json change. Not T3 (single repo, no cross-provider/systemic surface; the cross-issue coordination is dependency-management, not shared implementation).
