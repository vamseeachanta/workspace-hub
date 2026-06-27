# Plan for #3253: Hermes pattern auto-promotion into canonical skills — epic #3248

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-06-27
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3253
> **Client:** N/A
> **Lane:** lane:claude   <!-- harness/self-improvement; relabel the issue if scope class changed -->
> **Review artifacts:** scripts/review/results/2026-06-27-plan-3253-claude.md | scripts/review/results/2026-06-27-plan-3253-codex.md

---

## Resource Intelligence Summary

This issue (#3253, child of epic #3248, gap #3) asks for a path so **Hermes session learnings flow back as
skill/memory CANDIDATES through the bridge** instead of only via manual `~/.hermes/memories` writes. The
issue is explicit: **candidates only** — promotion to canonical still goes through the **same human
owner-review gate as #3252**. This plan delivers a candidate-emitter (`extract_hermes_patterns.py`) wired
best-effort into `scripts/memory/bridge-hermes-claude.sh`, reusing the existing candidate-file substrate and
the detector pure-core/inject-notify pattern. **It adds NO matrix dimension** (justified in §Decision).

> **Round-2 blocker fix (headline):** the de-dup gate is now built against a **bridge-block-stripped**
> canonical surface. The bridge's own §2-3 step (`bridge-hermes-claude.sh:65-112`) **injects the same
> Hermes-authored `MEMORY.md`/`USER.md` text into `agents.md`** (between the `<!-- BRIDGE:START -->` and
> `<!-- BRIDGE:END -->` markers) on **every run, BEFORE** the new §7c extractor runs. A naive
> `MEMORY.rglob('*.md')` content index would therefore read back the content the bridge just injected
> moments earlier in the **same process** and, because `_slug('- foo bar') == _slug('foo bar')`, mark
> **every** extracted pattern already-canonical → drop them all → the feature becomes a near-perpetual
> no-op. The fix (Design decision #3 below) excludes the bridge-injected block from the de-dup index, so
> de-dup runs only against **genuinely human-promoted** memory — and is **independent of §7c's placement
> relative to §3.**

### Existing repo code
- Found: `scripts/memory/bridge-hermes-claude.sh:50-57` — the bridge **already reads Hermes-authored memory**
  (`~/.hermes/memories/MEMORY.md` + `USER.md`). It runs daily on **both** OSes (Linux cron; Windows Task
  Scheduler) **as the same cross-platform `.sh`** — there is no per-step `.ps1` twin. This is the exact hook
  site the issue names. The bridge is `set -euo pipefail`, so any new step it calls **must be `|| …`-guarded**
  *and* must not reference an unbound variable (which `set -u` aborts on **before** the `||` is evaluated —
  see Rule 4 fix below).
- Found: **`scripts/memory/bridge-hermes-claude.sh:65-112` — the §2-3 direct-injection step (the blocker
  source).** §2 (`:68-90`) builds `BRIDGE_CONTENT` by splitting the Hermes-authored `MEMORY.md` (`### Environment
  Facts`) and `USER.md` (`### User Profile`) on `§` and emitting each non-empty line as `- ${line}` (`:75-78`,
  `:84-87`). §3 (`:101-112`, awk) injects `BRIDGE_CONTENT` into `agents.md` **between the markers**
  `<!-- BRIDGE:START -->` (matched `:102`) and `<!-- BRIDGE:END -->` (matched `:108`); **both marker lines are
  preserved in the output** (the awk prints START, prints bridge, then prints END after clearing `in_bridge`).
  Result: after every run, `agents.md` contains a delimited block holding the Hermes-authored lines verbatim
  (minus the leading `- `). **The extractor derives its candidates from the SAME `MEMORY.md`/`USER.md`, the SAME
  `§` split, slugified via `_slug` (which strips the leading `- `), so its candidate slugs are byte-identical to
  the slugs of the lines the bridge just injected.** The de-dup index MUST therefore exclude this block (Design
  decision #3; option (b) of the round-2 fix).
- Found: `scripts/memory/bridge-hermes-claude.sh:264-314` — the **read-back slice block** (Codex/Gemini/Hermes
  slices). Its python launcher `RBPY` is assigned **only inside** the `if [[ -f "${CURATE}" ]]` guard
  (opens `:264`, `RBPY` assigned `:265-269`). That `if` closes at **`:313`** (`fi`), followed by `echo ""`
  (`:314`); §8 begins at `:316`. **Any new step placed after that `fi` must NOT reference `RBPY` — it is out of
  scope there and `set -u` would abort the bridge.** The new §7c step (inserted after `:314`, before `:316`)
  therefore resolves its **own** launcher (`HPY`) inside its own guard (Rule-4 fix).
- Found: `scripts/memory/bridge-hermes-claude.sh:283-292` — the bridge **writes** `~/.hermes/memories/cross-provider.md`
  (a read-back slice derived FROM canonical `.claude/memory/`). **The extractor must NOT read this file** — it
  is bridge-generated from already-canonical content, so reading it would create a feedback loop that
  re-proposes already-promoted patterns. Source set is the Hermes-AUTHORED files only (`MEMORY.md`, `USER.md`).
- Found: **`scripts/memory/bridge-hermes-claude.sh:319-363` — the §8 `--commit` stash/pop path (minor-finding
  source).** In commit mode the bridge stages **only** `.claude/memory/` (`:322`) + the codex/gemini runtime
  slices (`:325`). It then runs `git diff-index --quiet HEAD` (`:334`); if **any** tracked file is dirty
  (including the §7c-written, git-tracked `hermes-pattern-candidates.md`, which the bridge does **not** stage),
  it does `git stash push -m pre-bridge-stash` (`:336`), commits, `git pull --rebase`, pushes, then
  `git stash pop 2>/dev/null || echo "… WARNING: stash pop failed"` (`:362`). So the freshly-written candidate
  file is stashed-and-popped on every commit-mode run, and a stash-pop **conflict** leaves the write parked in
  the stash. Handled by the idempotency + deterministic-re-extraction argument in §Risks (minor #2).
- Found: `scripts/curation/detect_skill_drift.py` (#3250, MERGED) — **the exact template**: a PURE
  `evaluate_drift(facts, last_seen, …)` + `drift_signature(...)` core (no IO/clock), a thin `run_cli` that
  routes alerts through an **injectable `notify_fn`** (default shells `scripts/notify.sh`), **last-seen
  signature spam-suppression** (`.claude/state/…-last-seen-<machine>.json`), and a **bounded fail-soft
  publish** (`PUBLISH_TIMEOUT_S=90`, OFF by default). It also shows the **cross-dir import idiom**: it imports a
  sibling via an explicit `sys.path.insert(0, _CURATION_DIR)` at lines 49-54. The new extractor lives in
  `scripts/memory/` but imports from `scripts/curation/`, so it MUST do the analogous insert (minor #3).
- Found: `scripts/operations/venue_absence_detector.py` — the canonical pure-`evaluate(...)` + thin-`run_cli`
  + injectable-notify pattern detect_skill_drift itself mirrors; cited for the test taxonomy.
- Found: `scripts/analysis/session-analysis.sh:21,168-247` — the **candidate-routing substrate**: the morning
  cron appends `## Candidates` blocks to `.claude/state/candidates/{script,skill,hook,agent,mcp}-candidates.md`
  (each header: *"Updated by … — do not edit manually"*). The new `hermes-pattern-candidates.md` **joins this
  family**; the dir already exists and is **git-tracked** — `git ls-files .claude/state/candidates/` returns
  **5 `*-candidates.md` files** (agent, hook, mcp, script, skill) **plus `correction-promotions.yaml`** (6 total)
  — and is **committed by the existing learning-artifact path** (`scripts/cron/commit-learning-artifacts.sh:96,113`
  commits `.claude/state/candidates/`), so no new commit/push is introduced.
- Found: `.claude/state/candidates/correction-promotions.yaml` — the existing **candidate→promotion schema**:
  ranked items each carrying `status: identified` (never `promoted`/`approved`) + `rationale` + `target_skill`.
  The new candidates carry an analogous `status: candidate` and an explicit owner-review header — the same
  "identified, not promoted" convention this issue requires.
- Found: `scripts/curation/curate_session_memory.py:75-90` (`machine_label()`) + `:240-256`
  (`publish_fingerprint`, the **90s bounded fail-soft** `subprocess.run(..., timeout=PUBLISH_TIMEOUT_S)` that a
  hung state-ref push "(observed stuck >1h)" can never stall) — reused for label + the optional publish.
  `MEMORY = .claude/memory` is defined at `:48` and `REPO` at `:46`; both reused by import.
- Found: `scripts/curation/curate_session_memory.py:158-170` (`memory_delta`) — its docstring is *"Basenames of
  memory files changed since the last curation"*; it returns a list of **relative `.md` path basenames**,
  mtime-bounded by `cutoff`, **hard-capped at `changed[:200]`** (line 170). It is a **recently-changed delta of
  FILE NAMES, not a content enumerator** and is therefore **NOT used for the de-dup gate** in this plan. The
  extractor builds its **own** canonical-CONTENT index by walking `MEMORY.rglob('*.md')`, **stripping each
  file's bridge-injected block (round-2 fix)**, and slugifying the remaining **text** (no cap, no mtime cutoff).
  `MEMORY` (the constant) is reused by import; `memory_delta` is **not** imported.
- Found: `scripts/notify.sh` — `bash scripts/notify.sh <source> <job> <status> [details]`; appends one JSONL
  event, **always exits 0**. The alert channel (`source=cron`, `job=hermes-pattern-candidates`).
- Found: `scripts/readiness/build-equality-matrix.py:274-304` (`memory_freshness_verdict`, #3255) — already
  grades the bridge's last-refresh as a **dead-man's-switch** (MEMORY-FRESH / STALE). This is the reason a NEW
  matrix cell for Hermes-candidate freshness is **redundant** (see §Decision).
- Found: `scripts/legal/legal-sanity-scan.sh` + `.legal-deny-list.yaml` (repo-root client patterns per
  `context.md` §Legal Compliance) — Hermes memory can contain client identifiers/PII; candidates land in a
  **git-tracked** file, so emitted text **must be scrubbed fail-closed** against this deny-list (must-fix #1).

### Standards
Not applicable — harness/self-improvement infrastructure, no engineering standard involved.

### LLM Wiki pages consulted
No relevant wiki pages — harness-internal change, out of scope of `.claude/rules/wiki-sibling-routing.md`
("Do not apply when … workspace-hub-internal artifact").

### Documents consulted
- Issue #3253 body (verified live via `gh issue view 3253`): *"Hermes session learnings only flow back via
  manual ~/.hermes/memories writes. Add a path for Hermes patterns to become skill/memory candidates through
  the bridge. Closes gap #3. Parent: epic #3248."*
- Sibling #3252 (auto-graduate corrections) — establishes the **human owner-review gate** this child reuses;
  per the issue, promotion stays that gate. This plan does NOT invent its own approval mechanism — it writes
  `status: candidate` and stops, exactly like the existing candidate files + `correction-promotions.yaml`.
- Sibling plans `docs/plans/2026-06-26-3250-skill-drift-detector-alert.md`,
  `…-3255-memory-staleness-alert.md`, `…-3251-resync-skills-no-freeze-at-link.md` — section headers + the
  pure-core/inject-notify/bounded-publish patterns followed here, and the `-claude.md | -codex.md`
  review-artifact naming convention adopted in this plan's front-matter.
- `docs/plans/memory-bridge-architecture.md` — the three-silo model; confirms `~/.hermes/memories/` is the
  Hermes-authored source and `.claude/memory/` is the canonical sink.
- `.claude/rules/patterns.md` (enforcement gradient — this stays Level-2 script + tests),
  `.claude/rules/coding-style.md` (no hardcoded abs paths — `scripts/enforcement/check-no-abs-paths.sh`).

### Gaps identified
- No path exists from Hermes-authored memory to a **candidate** surface: today the bridge copies Hermes facts
  **directly into canonical `agents.md`** (§2-3, no human review step), and no `hermes-pattern-candidates.md`
  exists. (`ls .claude/state/candidates/` → no `hermes-*` file.)
- No `scripts/memory/extract_hermes_patterns.py`, no `tests/memory/test_extract_hermes_patterns.py`,
  no last-seen state, no notify wiring for Hermes candidates.
- The bridge's direct Hermes→`agents.md` injection (§2-3) is **unreviewed promotion** — but this plan does NOT
  remove it (out of scope; would change canonical-memory behavior). It ADDS the candidate path alongside it and
  **resolves the de-dup interaction** by excluding the bridge-injected block from the candidate de-dup index
  (Design decision #3), so the candidate gate sees only genuinely human-promoted memory.

### Evidence (embedded verification)

**Issue status** (verified 2026-06-27 via `gh issue view`):
- `#3253` — OPEN — "Self-improvement: Hermes pattern auto-promotion into canonical skills — epic #3248".

**File existence** (`ls`/`wc`/`git ls-files`/`Read` 2026-06-27, repo HEAD `37d9a984a`):
- EXISTS: `scripts/memory/bridge-hermes-claude.sh` (**366 lines** — verified `wc -l`; Hermes read `:50-57`;
  §2-3 direct injection `:65-112`, BRIDGE markers matched at `:102`/`:108`; `set -euo pipefail` near top;
  read-back guard `if [[ -f "${CURATE}" ]]` opens `:264`, `RBPY` assigned `:265-269`, `fi` `:313`, `echo ""`
  `:314`; §8 commit/stash path `:319-363`).
- EXISTS: `scripts/curation/detect_skill_drift.py` (the template; pure core + inject-notify + bounded publish;
  cross-dir import idiom `:49-54`).
- EXISTS: `scripts/operations/venue_absence_detector.py`, `scripts/notify.sh`,
  `scripts/curation/curate_session_memory.py` (`machine_label`:75, `memory_delta`:158, `MEMORY`:48,
  `REPO`:46, `publish_fingerprint`:240, `PUBLISH_TIMEOUT_S=90`:59).
- EXISTS + git-tracked (verified `git ls-files`): `.claude/state/candidates/{agent,hook,mcp,script,skill}-candidates.md`
  (5 files) **+** `.claude/state/candidates/correction-promotions.yaml`.
- EXISTS: `scripts/legal/legal-sanity-scan.sh`, `.legal-deny-list.yaml`.
- EXISTS: `~/.hermes/memories/{MEMORY.md,USER.md,cross-provider.md}` (Hermes box only — dev-primary).
- MISSING (this plan creates): `scripts/memory/extract_hermes_patterns.py`,
  `tests/memory/test_extract_hermes_patterns.py`, `.claude/state/candidates/hermes-pattern-candidates.md`
  (seeded header), `.claude/state/candidates/hermes-patterns-last-seen-<machine>.json` (runtime, gitignored).

**Line excerpts** (`bridge-hermes-claude.sh:75-78` — §2 emits each Hermes line as `- ${line}`, the slug-collision source):
```
        while IFS= read -r line; do
            [[ -z "${line}" || "${line}" == "§" ]] && continue
            BRIDGE_CONTENT+="- ${line}"$'\n'
        done < <(tr '§' '\n' <<< "${HERMES_MEMORY}")
```

**Line excerpts** (`bridge-hermes-claude.sh:101-112` — §3 injects BRIDGE_CONTENT between the preserved markers):
```
    awk -v bridge="${BRIDGE_CONTENT}" '
        /<!-- BRIDGE:START/{ print; print bridge; in_bridge=1; next }
        /<!-- BRIDGE:END/{ in_bridge=0 }
        !in_bridge { print }
    ' "${TEMPLATE}" > "${AGENTS_OUT}"
```

**Line excerpts** (`bridge-hermes-claude.sh:332-337,360-363` — §8 stashes the unrelated tracked candidate file):
```
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        echo "[bridge] Uncommitted changes detected — stashing before pull..."
        git stash push -m "pre-bridge-stash"
        HAS_STASH=true
    fi
    ...
    if [[ "${HAS_STASH}" = true ]]; then
        git stash pop 2>/dev/null || echo "[bridge] WARNING: stash pop failed — run 'git stash pop' manually"
    fi
```

**Line excerpts** (`detect_skill_drift.py:49-54` — the cross-dir import idiom the extractor must mirror):
```
_CURATION_DIR = str(Path(__file__).resolve().parent)
if _CURATION_DIR not in sys.path:
    sys.path.insert(0, _CURATION_DIR)
import audit_skill_currency  # noqa: E402  (path set up above)
```

**Gap proofs:**
- `ls scripts/memory/extract_hermes_patterns.py` → "No such file or directory" → extractor absent.
- `ls .claude/state/candidates/hermes-*` → none → no Hermes candidate surface.
- `grep -rn hermes-pattern scripts/` → empty → no wiring today.

**Reproduction proof of the blocker** (static, no runtime needed): `_slug('- /mnt/local-analysis is the repo mount')`
== `_slug('/mnt/local-analysis is the repo mount')` (leading `- ` stripped by the `[^a-z0-9]+` collapse). The
bridge writes `- /mnt/local-analysis is the repo mount` into the BRIDGE block of `agents.md`; an unstripped
`MEMORY.rglob` index would slugify that line to the **same key** the extractor produces from the source
`MEMORY.md` line → `is_already_canonical → True` → dropped. Stripping the BRIDGE block removes the collision.
The substrate it builds on is verified live: the bridge reads Hermes memory + injects it today, and
`detect_skill_drift.py` is the running precedent for the pure-core + notify + bounded-publish shape.

<!-- Source count: issue #3253 + epic #3248 + bridge-hermes-claude.sh + detect_skill_drift.py +
     venue_absence_detector.py + session-analysis.sh + correction-promotions.yaml +
     curate_session_memory.py + notify.sh + memory-bridge-architecture.md + legal-sanity-scan.sh = ≥3. -->

---

## Decision: candidate-emitter pipeline, NO new matrix dimension

**Rule 6 first-assessment — a new matrix dimension is NOT warranted. `addsMatrixDimension = false`.** Unlike
#3250/#3251/#3255 (which each grade a per-machine *equality/freshness STATE* across the fleet), #3253 is an
**automation pipeline** that produces review *candidates*. Three reasons it hooks into existing machinery
instead of adding a cell:

1. **Single-box signal, not a fleet equality.** Hermes runs **only on dev-primary** (ace-linux-1). A
   `hermes_candidates` matrix cell would grade **MISSING-EVIDENCE / by-design on every other box** (Windows
   ace-win-1/2, dev-secondary have no `~/.hermes/`) — exactly the kind of non-cross-machine signal the equality
   matrix is **not** for.
2. **Dead-man's-switch already exists.** The "is the Hermes→candidate path still alive?" question is already
   answered by **`memory_freshness_verdict` (#3255, `build-equality-matrix.py:274-304`)** (grades the bridge's
   last-refresh; the extractor rides the same bridge cron) **and the bridge's own `notify.sh` fail event**. A
   second freshness cell is redundant.
3. **The candidate surface is the right output, not a verdict.** The deliverable is *reviewable candidates for a
   human*, which the `.claude/state/candidates/*.md` family + `notify.sh`-on-new already model.

**Consequence (the Rule 3 win):** by NOT adding a dimension we **avoid all ~11 matrix touchpoints** that a new
line item would force. For completeness, the touchpoints we deliberately do **not** touch (and therefore cannot
break): in `scripts/readiness/build-equality-matrix.py` — (1) a new verdict function, (2) the `verdict_for()`
precedence branch (`:411`), (3) `BASE_DISPLAY_DIMS` (`:461`), (4) `DISPLAY_DIMS` (`:464`), (5) `GROUPS`
(`:475`), (6) `ROLLUP_SEVERITY` (`:491`), (7) `OK_VERDICTS` (`:516`), (8) `remediate()` (`:521`), (9) HTML
legend/CSS spans; plus (10) `scripts/readiness/collect-equality.sh` emit block; (11)
**`scripts/readiness/reconcile-ecosystem.sh:~204` OK-skip `case` list** (the
`CONFORMS|EQUAL|…|MEMORY-FRESH|SKILL-LINKS-OK` line) — every new green verdict string must be added there or
healthy cells fire spurious reconcile actions. None of these change.

**Rejected alternative — a `hermes_candidates` matrix line item.** Rejected per (1)-(3): permanently
MISSING-EVIDENCE on 3 of 4 active boxes, redundant with memory_freshness, and a verdict cell is the wrong shape
for "candidates awaiting human review." Adopting it would also drag in all 11 touchpoints for zero reviewer
gain.

**Rejected alternative — emit Hermes patterns straight into a skill / `agents.md` (auto-promote).** This is
what the issue title's word "promotion" could be misread as, and it is exactly what the **human gate forbids**.
Hermes-authored text is unreviewed and may carry PII; auto-writing it to canonical surfaces violates Rule 1.
The extractor stops at `status: candidate`.

**Rejected alternative — defer the §3-injection / §7c-extraction collision to a later issue.** The round-2 review
correctly judged that deferring this nullifies the deliverable (steady-state ZERO candidates). It is resolved
**in-scope** here by Design decision #3 (bridge-block exclusion), not deferred.

---

## Deliverable

A `scripts/memory/extract_hermes_patterns.py` that, on the Hermes box, reads the **Hermes-authored** memory
(`~/.hermes/memories/MEMORY.md` + `USER.md`; **never** the bridge-written `cross-provider.md`), extracts
recurring **pattern candidates**, **de-dups** them against a **bridge-block-stripped canonical-CONTENT index**
of `.claude/memory/` (walks `MEMORY.rglob('*.md')` text but **excludes the `<!-- BRIDGE:START -->`…
`<!-- BRIDGE:END -->` block** of `agents.md` so the bridge's own §2-3 self-injection cannot suppress every
candidate) and the skills tree, **scrubs each emitted candidate fail-closed** against `.legal-deny-list.yaml`
(drop any client/PII match), and **idempotently appends** them as `status: candidate` items to a new
git-tracked `.claude/state/candidates/hermes-pattern-candidates.md` — joining the existing session-analysis
candidate family and the `correction-promotions.yaml` "identified-not-promoted" convention. It fires
`notify.sh` **only on NEW (not previously-seen) candidates** (last-seen signature spam-suppression), optionally
publishes the candidate fingerprint to a bounded fail-soft `hermes-pattern-candidate-state` git ref (OFF by
default), and is wired **best-effort** (Rule 4 guarded, with its own self-contained python launcher) into
`scripts/memory/bridge-hermes-claude.sh`. It **never** writes any canonical surface, never applies a status
label, and never marks a candidate promoted — promotion stays the **human owner-review gate (same as #3252)**.

---

## Design decisions

1. **Separate extractor module, wired into the bridge — not inline bridge bash.** The pattern-extraction +
   de-dup + scrub + dedup-alert logic is a PURE testable core (mirrors `detect_skill_drift.py`'s split). The
   bridge gains only a thin best-effort call. Keeps the bridge's `set -euo pipefail` commit path untouched and
   gives the logic a real TDD surface.
2. **Source set excludes `cross-provider.md` (feedback-loop guard).** The bridge generates `cross-provider.md`
   *from* canonical `.claude/memory/`; reading it back would re-propose already-promoted content forever. Read
   only `MEMORY.md` + `USER.md` (Hermes-authored).
3. **De-dup against the FULL canonical CONTENT surface MINUS the bridge-injected block (round-2 BLOCKER fix).**
   A pattern already present in **genuinely human-promoted** canonical memory or the skills tree is not a
   candidate. The gate walks **every** `MEMORY.rglob('*.md')` file and slugifies its **text** (no 200-cap, no
   mtime cutoff). **Critically, for `agents.md` the index strips the `<!-- BRIDGE:START -->`…
   `<!-- BRIDGE:END -->` block before slugifying** — because the bridge's §2-3 step
   (`bridge-hermes-claude.sh:65-112`) re-injects the *same* Hermes-authored `MEMORY.md`/`USER.md` lines into
   that block on every run, *before* §7c, and `_slug('- foo') == _slug('foo')`, so an unstripped index would
   mark every candidate already-canonical and emit ZERO candidates in steady state. Stripping the block makes
   the de-dup compare candidates only against human-promoted memory (template baseline, topics, other memory
   files, skills) and is **independent of whether §7c runs before or after §3** — robust by construction. A
   generic `_strip_bridge_block(text)` helper removes the inclusive marker span from any file (only `agents.md`
   carries it today; defensive for any future file). `memory_delta` (capped, mtime-bounded basenames) is
   explicitly **not** used. **This also resolves the round-1 "open question":** narrowing the direct injection
   to env-facts-only is no longer load-bearing for this feature's correctness — it is demoted to a genuine
   non-blocking future enhancement (§Risks, last bullet).
4. **Fail-closed PII/secret scrub (must-fix #1).** Hermes memory may contain client identifiers/PII; the
   candidate file is git-tracked in workspace-hub. Every emitted candidate's text is checked against
   `.legal-deny-list.yaml` patterns; a match → **drop the candidate** (do not redact-and-emit; fail closed) and
   increment a `dropped_sensitive` counter surfaced in the run summary. The candidate emits a **pattern summary
   + provenance pointer**, not raw Hermes lines.
5. **Spam suppression via last-seen signature.** A stable signature over sorted candidate keys is compared to
   `.claude/state/candidates/hermes-patterns-last-seen-<machine>.json`; `notify.sh` fires only on a transition
   into / change-of the candidate set. The last-seen JSON is **gitignored** (runtime), so it is **not stashed**
   by the bridge's §8 stash/pop and remains the durable spam-suppression anchor across stash churn (minor #2).
6. **Idempotent, append-only candidate surface; no canonical writes (Rule 1).** `append_candidates_md`
   **de-dups against the candidate keys already present in the file** and never double-appends — so the write
   is idempotent under repeated runs *and* under the bridge's §8 stash-then-restore (or a lost-stash revert):
   the candidate content is a pure deterministic function of (durable Hermes memory + canonical memory), so a
   lost stash-pop only **defers** the append to the next bridge cycle, never loses it permanently (minor #2).
   The extractor writes ONLY under `.claude/state/candidates/`. A test asserts it never opens any path under
   `.claude/memory/`, `.claude/skills/`, `config/agents/` for write, and never emits the strings
   `status:plan-approved` / `status:completeness-verified` / `promoted` / `approved`.
7. **Machine label + bounded publish reused, not reinvented — via explicit cross-dir import.** `machine_label()`,
   the `MEMORY` constant, and the 90s bounded fail-soft `subprocess` publish are imported/cloned from
   `scripts/curation/curate_session_memory.py`. Because the new module lives in `scripts/memory/` while its
   dependency lives in `scripts/curation/`, the module performs an explicit
   `sys.path.insert(0, <repo>/scripts/curation)` **before** the import (mirroring `detect_skill_drift.py:49-54`)
   so the reuse is real, not assumed (minor #3).

---

## Pseudocode

```python
# scripts/memory/extract_hermes_patterns.py  (clone of detect_skill_drift.py shape)
import sys, re, subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
# Cross-dir reuse: the dependency lives in scripts/curation/, this module in scripts/memory/.
# Mirror detect_skill_drift.py:49-54 — insert the curation dir on sys.path BEFORE importing.
_CURATION_DIR = str(REPO / "scripts" / "curation")
if _CURATION_DIR not in sys.path:
    sys.path.insert(0, _CURATION_DIR)
from curate_session_memory import machine_label, MEMORY   # REUSE; NOT memory_delta (basenames-only)

PUBLISH_TIMEOUT_S = 90
CAND_REF = "hermes-pattern-candidate-state"
HERMES_DIR = Path.home() / ".hermes" / "memories"
SOURCES = ["MEMORY.md", "USER.md"]          # Hermes-AUTHORED only — NOT cross-provider.md (loop guard)
STATE_CAND = REPO / ".claude" / "state" / "candidates"
CANDIDATES = STATE_CAND / "hermes-pattern-candidates.md"
BRIDGE_START, BRIDGE_END = "BRIDGE:START", "BRIDGE:END"   # markers written by bridge §3 (:102/:108)

def _slug(text: str) -> str:                                 # PURE — normalize to a stable key
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

def slug_tokens(text: str) -> set[str]:                      # PURE — line/section slugs of a blob
    return {_slug(ln) for ln in text.splitlines() if _slug(ln)}

def strip_bridge_block(text: str) -> str:                    # PURE — round-2 BLOCKER fix
    # Remove the inclusive span between the bridge markers so the bridge's own §2-3 self-injection
    # of Hermes-authored lines into agents.md cannot make every extracted pattern look already-canonical.
    out, skipping = [], False
    for ln in text.splitlines():
        if BRIDGE_START in ln: skipping = True;  continue    # drop START marker line
        if BRIDGE_END   in ln: skipping = False; continue    # drop END marker line
        if not skipping: out.append(ln)
    return "\n".join(out)

def extract_patterns(hermes_text: str) -> list[dict]:        # PURE — no IO
    # split Hermes '§'-delimited / line items (same split the bridge uses), normalize, keep recurring/
    # sectioned learnings; each → {key, summary, source_file, kind: "skill"|"memory"}; key = _slug(text).
    # _slug strips any leading '- ', matching the bridge's `- ${line}` injection form.

def canonical_text_index() -> set[str]:                      # reads canonical CONTENT (no clock)
    # Walk EVERY MEMORY.rglob('*.md') — no 200-cap, no mtime cutoff — but STRIP the bridge block so
    # de-dup runs only against genuinely human-promoted memory (round-2 fix).
    idx: set[str] = set()
    if MEMORY.exists():
        for p in MEMORY.rglob("*.md"):
            try: idx |= slug_tokens(strip_bridge_block(p.read_text(encoding="utf-8", errors="replace")))
            except OSError: continue
    return idx

def skill_text_index() -> set[str]:                          # .claude/skills slugs (names + headers)
    ...

def is_already_canonical(cand, canonical_slugs, skill_slugs) -> bool:   # PURE — de-dup gate
    return cand["key"] in canonical_slugs or cand["key"] in skill_slugs

def is_sensitive(text, deny_patterns) -> bool:               # PURE — fail-closed scrub
    return any(re.search(p, text, re.I) for p in deny_patterns)

def candidate_signature(cands) -> str:                       # PURE — sorted keys ⇒ order-independent
    return "CLEAN" if not cands else "|".join(sorted(c["key"] for c in cands))

def evaluate(patterns, canonical_slugs, skill_slugs, deny_patterns, last_seen, *, now_iso) -> dict:  # PURE
    fresh, dropped = [], 0
    for c in patterns:
        if is_already_canonical(c, canonical_slugs, skill_slugs): continue
        if is_sensitive(c["summary"] + c["key"], deny_patterns): dropped += 1; continue   # fail-closed
        fresh.append(c)
    sig = candidate_signature(fresh)
    new = sig != (last_seen or {}).get("signature") and sig != "CLEAN"
    alerts = ([{"job":"hermes-pattern-candidates","status":"pass","detail":f"{len(fresh)} new candidate(s)"}]
              if new else [])
    return {"candidates": fresh, "dropped_sensitive": dropped, "signature": sig, "new": new,
            "alerts": alerts, "new_state": {"signature": sig, "updated_at": now_iso}}

def existing_candidate_keys(path) -> set[str]:               # PURE-ish — read the file's current keys
    return {m.group(1) for m in re.finditer(r"^- key: (\S+)", path.read_text(), re.M)} if path.exists() else set()

def append_candidates_md(path, cands, dropped):              # IDEMPOTENT — never double-appends (minor #2)
    have = existing_candidate_keys(path)
    new = [c for c in cands if c["key"] not in have]
    if not new and dropped == 0: return            # nothing to write → file untouched (stash-churn safe)
    # append a dated `## Candidates` block listing only `new`, status: candidate ...

def run_cli(args, notify_fn=_default_notify) -> int:
    machine = machine_label()
    text = "\n".join((HERMES_DIR/s).read_text() for s in SOURCES if (HERMES_DIR/s).exists())
    if not text: return 0                       # no Hermes on this box (Windows/dev-secondary) → no-op
    patterns = extract_patterns(text)
    canonical = canonical_text_index()           # bridge-block-stripped canonical CONTENT → de-dup
    skills    = skill_text_index()               # .claude/skills slugs
    deny = load_deny_patterns(REPO/".legal-deny-list.yaml")
    last = read_json(STATE_CAND / f"hermes-patterns-last-seen-{machine}.json") or None
    r = evaluate(patterns, canonical, skills, deny, last, now_iso=_now())
    append_candidates_md(CANDIDATES, r["candidates"], dropped=r["dropped_sensitive"])   # idempotent
    for a in r["alerts"]: notify_fn(a)                       # gated by dedup
    write_json(STATE_CAND / f"hermes-patterns-last-seen-{machine}.json", r["new_state"])  # gitignored
    if args.publish: print(publish_candidates(machine), file=sys.stderr)   # bounded, OFF by default
    return 0                                                 # ALWAYS 0 on candidates-found (Rule 4)

def publish_candidates(machine) -> str:        # exact publish_fingerprint clone — 90s, fail-soft
    try: subprocess.run([py, equivalence_state, "publish", "--repo", str(REPO), "--role", machine,
                         "--file", str(CANDIDATES), "--ref", CAND_REF], timeout=PUBLISH_TIMEOUT_S, check=False)
    except subprocess.TimeoutExpired: return f"publish-timeout ({PUBLISH_TIMEOUT_S}s)"
    ...                                        # never raises, never blocks the bridge
```

`append_candidates_md` emits, per NEW item (mirroring `correction-promotions.yaml` + the `*-candidates.md` header):
```
## Candidates (from 2026-06-27 — Hermes patterns)
> Auto-emitted by extract_hermes_patterns.py — status: candidate. Promotion to a skill/memory
> is a HUMAN owner-review action (gate per #3252). Do not edit manually.
- key: <slug>  status: candidate  kind: skill  source: MEMORY.md  summary: "<scrubbed summary>"
(dropped 2 sensitive candidate(s) — see run log)
```

**Bridge wiring** (`scripts/memory/bridge-hermes-claude.sh`, new step ~7c, placed AFTER the §7 read-back block's
closing `fi` (`:313`) + its `echo ""` (`:314`) and BEFORE §8 (`:316`)). The de-dup correctness no longer depends
on this placement (Design decision #3 strips the bridge block regardless), but §7c stays after §7b to keep all
read-derived steps together. **RULE-4 FIX:** §7c does **not** reference `RBPY` (scoped only inside the
`if [[ -f "${CURATE}" ]]` read-back guard, assigned `:265-269`, **unbound** at §7c's position — under `set -u`
an unbound-array expansion aborts the shell *before* the `||` guard runs). §7c resolves its **own** launcher
`HPY` inside its own guard, so every variable it touches is always in-scope:
```bash
# 7c. Emit Hermes-pattern CANDIDATES (#3253) — review-gated; writes only .claude/state/candidates/.
#     Self-contained launcher (does NOT use RBPY — out of scope here under set -u). Rule-4 guarded.
EXTRACT="${REPO_ROOT}/scripts/memory/extract_hermes_patterns.py"
if [[ -f "${EXTRACT}" ]]; then
  if command -v uv >/dev/null 2>&1 && uv run --no-project python -c "print(1)" >/dev/null 2>&1; then
    HPY=(uv run --no-project python)
  else
    HPY=(python3)
  fi
  "${HPY[@]}" "${EXTRACT}" >/dev/null 2>&1 || echo "  ⚠️  WARN: hermes-pattern candidate emit failed (soft)" >&2
fi
```
Re-verified under `set -euo pipefail`: `HPY` is assigned on **both** branches of the inner `if/else` before the
`"${HPY[@]}"` expansion, so `set -u` cannot fire; a non-zero exit from the extractor is caught by `|| echo …`;
the block is entered only when `${EXTRACT}` exists. No path through §7c can abort the bridge.

---

## Implementation Steps (TDD-first — tests before code)

1. **Write `tests/memory/test_extract_hermes_patterns.py` FIRST** (red) — the full list in §Test Plan,
   including the round-2 **bridge-block-strip** tests (`test_dedup_survives_bridge_injection`,
   `test_dedup_drops_human_promoted_outside_block`), the **idempotency** test
   (`test_append_idempotent_no_double`), the content-index de-dup test, the canonical-gate test, the
   feedback-loop guard, spam-suppression, bounded-publish, and the no-Hermes no-op. Load the module via
   `importlib.util.spec_from_file_location` per the sibling test idiom.
2. **Create `scripts/memory/extract_hermes_patterns.py`** (green) — PURE core (`extract_patterns`,
   `strip_bridge_block`, `canonical_text_index`, `skill_text_index`, `is_already_canonical`, `is_sensitive`,
   `candidate_signature`, `evaluate`, `existing_candidate_keys`) + thin `run_cli` with injectable `notify_fn` +
   `_default_notify` shelling `scripts/notify.sh` + idempotent `append_candidates_md` + bounded
   `publish_candidates`. **Add the explicit `sys.path.insert(0, str(REPO/"scripts"/"curation"))` BEFORE
   `from curate_session_memory import machine_label, MEMORY`** (mirror `detect_skill_drift.py:49-54`). Reuse
   `machine_label`/`MEMORY` by import; **do NOT import `memory_delta`**. No hardcoded abs paths
   (`Path(__file__).resolve().parents[2]`).
3. **Seed `.claude/state/candidates/hermes-pattern-candidates.md`** with the family header (mirrors
   `hook-candidates.md`) so the surface exists git-tracked before first run; add the last-seen JSON glob
   (`hermes-patterns-last-seen-*.json`) to `.gitignore` matching the skill-drift last-seen treatment (so §8's
   stash never touches it — minor #2).
4. **Wire the bridge** — add the guarded, self-contained §7c block (own `HPY` launcher, no `RBPY` reference) to
   `scripts/memory/bridge-hermes-claude.sh` after `:314`, before §8 (`:316`). Single cross-platform `.sh`; **no
   `.ps1` change** (Rule 2). Do **not** add the candidate file to the bridge's §8 `git add`/`git commit`
   pathspec — it is committed by the existing `commit-learning-artifacts.sh` path (`:96,113`), keeping the
   bridge's stash interaction the only one to reason about (minor #2).
5. **Run the suite green**, then run the legal + abs-path enforcement scans on changed files.
6. **Index the plan** in `docs/plans/README.md`.
7. **Adversarial review** (T2 → 2 providers: Claude + Codex) → fold findings → `status:plan-review` →
   **USER APPROVES** (never self-applied).

---

## Test Plan

| Test name | Verifies | Input | Output |
|---|---|---|---|
| test_extract_basic | parses §/line Hermes items into keyed candidates | `"a§b§c"` | 3 candidates, stable slug keys |
| test_signature_order_independent | signature is set-stable | keys `[b,a]` vs `[a,b]` | identical signature |
| test_signature_clean_when_empty | no candidates → CLEAN | `[]` | `"CLEAN"` |
| **test_dedup_survives_bridge_injection** | **round-2 BLOCKER**: a Hermes pattern NOT yet human-promoted survives even when the bridge has injected it into the `BRIDGE:START`…`BRIDGE:END` block of `agents.md` in the same run | tmp MEMORY/agents.md with the pattern text ONLY inside the bridge markers | candidate PRESENT (proves the block is stripped from the index) |
| **test_dedup_drops_human_promoted_outside_block** | **round-2 companion**: the SAME pattern text placed OUTSIDE the markers (genuinely human-promoted) is dropped | tmp agents.md with the text outside `BRIDGE:*` | candidate ABSENT |
| test_strip_bridge_block_removes_span | helper drops the inclusive marker span, keeps surrounding text | text with header + bridge block + footer | output has header+footer, no block, no marker lines |
| **test_dedup_uses_full_content_surface** | gate indexes `MEMORY.rglob` TEXT (not basenames); pattern in an OLD memory file (>200 / older than any mtime cutoff) still dropped | tmp MEMORY with pattern text in `topics/old.md` | candidate absent |
| test_dedup_against_canonical | already-canonical pattern dropped | cand.key in canonical content index | not in `candidates` |
| test_dedup_against_skills | already-in-skills pattern dropped | cand.key in skill index | not in `candidates` |
| **test_scrub_sensitive_failclosed** | **must-fix #1**: client/PII match dropped, not emitted | summary matches a deny pattern | candidate absent; `dropped_sensitive==1` |
| test_scrub_clean_passes | non-sensitive candidate survives | no deny match | present |
| **test_never_reads_cross_provider_md** | feedback-loop guard | SOURCES list / monkeypatched open spy | `cross-provider.md` never opened |
| test_new_candidates_alert_once | first appearance fires one pass alert | last_seen=None, 2 fresh | `new=True`, 1 alert status=pass |
| test_same_candidates_suppressed | unchanged set → no alert | last_seen.signature==sig | `new=False`, 0 alerts |
| test_changed_set_realerts | candidate set changed → re-alert | last `a`, now `a,b` | `new=True`, 1 alert |
| test_cleared_no_alert | fresh set empty | CLEAN, last had items | 0 alerts |
| **test_append_idempotent_no_double** | **minor #2**: appending the same candidates twice yields ONE entry (stash-restore / re-run safe) | append `[a,b]`, then append `[a,b]` again | file has one block; key `a`/`b` appear once |
| test_append_noop_when_nothing_new | no new keys + no drops → file byte-unchanged | append already-present keys | file mtime/content unchanged |
| **test_canonical_gate_no_canonical_writes** | **Rule 1**: writes only under candidates/ | run_cli with spied open | no write to `.claude/memory/`, `.claude/skills/`, `config/agents/` |
| test_no_promotion_status_strings | never emits owner-gate labels | any candidate output | excludes `status:plan-approved`,`status:completeness-verified`,`promoted`,`approved` |
| test_status_is_candidate | emitted items carry `status: candidate` | fresh candidate | line contains `status: candidate` |
| test_no_hermes_is_noop | Windows/dev-secondary box | HERMES_DIR absent | rc 0, file unchanged, 0 alerts |
| test_run_cli_injected_notify | CLI routes alerts via injected fn, writes last-seen | tmp dirs + fresh facts | notify called once; last-seen written; rc 0 |
| **test_cross_dir_import_resolves** | **minor #3**: imports `machine_label`/`MEMORY` from scripts/curation via the sys.path insert | import the module fresh | no ImportError; `machine_label` callable |
| test_machine_label_reused | label from `curate_session_memory.machine_label` | EQ_MACHINE=foo | last-seen keyed `…-foo.json` |
| test_publish_off_by_default | no `--publish` ⇒ no subprocess push | run_cli no flag | no publish call |
| **test_publish_bounded_timeout** | **Rule 5**: publish wraps a 90s timeout, fail-soft | monkeypatch subprocess→TimeoutExpired | returns `publish-timeout (90s)`, no raise |
| test_evaluate_pure_no_io | `evaluate` performs no file/subprocess IO | monkeypatch open/subprocess to raise | passes |
| test_returns_zero_on_candidates | rc 0 even when new candidates found | fresh candidates | rc 0 (Rule 4) |
| **test_bridge_wiring_self_contained (grep)** | **Rule 4 fix**: §7c defines its own `HPY` (no `RBPY`), `||`-guarded, after §7b before §8 | read bridge file | `HPY=` present in §7c; no `RBPY` token in §7c; `|| echo …(soft)` guard present |

**Acceptance commands:**
- `uv run --no-project --with pyyaml pytest tests/memory/test_extract_hermes_patterns.py -v` (green).
- `uv run --no-project --with pyyaml python scripts/memory/extract_hermes_patterns.py` on dev-primary emits/updates
  `.claude/state/candidates/hermes-pattern-candidates.md` with `status: candidate` items (NON-empty in steady
  state — proves the blocker fix), zero canonical writes; a second back-to-back run leaves the file unchanged
  (idempotent).
- `bash scripts/legal/legal-sanity-scan.sh` clean; `bash scripts/enforcement/check-no-abs-paths.sh` clean on changed files.
- `grep -n "extract_hermes_patterns\|HPY" scripts/memory/bridge-hermes-claude.sh` shows the self-contained guarded §7c call;
  `grep -c RBPY` over the §7c block is 0.

---

## Risks & Hard-Rule Compliance

**Rule 1 — never self-apply owner gates; promotion stays HUMAN.** The extractor writes ONLY `status: candidate`
items under `.claude/state/candidates/`; it never writes canonical (`.claude/memory/`, `.claude/skills/`,
`config/agents/`), never applies `status:plan-approved`/`status:completeness-verified`, never marks a candidate
`promoted`/`approved`. Promotion to a skill/memory is a separate human owner-review action — the same gate as
#3252. Locked by `test_canonical_gate_no_canonical_writes` + `test_no_promotion_status_strings` +
`test_status_is_candidate`.

**Rule 2 — session/curation audits must be wired into BOTH `curate-session-memory.sh` AND `.ps1`.** **Not
applicable, by design.** This change adds **no session/curation audit and no matrix cell**, so it does not touch
the curate wrappers at all. It wires into `scripts/memory/bridge-hermes-claude.sh`, a **single cross-platform
`.sh`** (Windows runs the same `.sh` via Task Scheduler/Git Bash — no `.ps1` twin of the bridge). No
machine-equality audit substrate (`machine_label`→audit→state-JSON→collect-equality→verdict) is created or
rebuilt; `machine_label` is *reused* by import only for the last-seen filename. So the BOTH-wrappers mandate has
nothing to bind to here.

**Rule 3 — a new matrix dimension touches ~11 places.** **Avoided entirely** — no dimension is added (see
§Decision). The 11 touchpoints we deliberately do not modify are enumerated in §Decision with verified line
refs (`build-equality-matrix.py` verdict fn / `verdict_for`:411 / `BASE_DISPLAY_DIMS`:461 / `DISPLAY_DIMS`:464 /
`GROUPS`:475 / `ROLLUP_SEVERITY`:491 / `OK_VERDICTS`:516 / `remediate`:521 / HTML legend; collect-equality
emit; **reconcile-ecosystem.sh:~204 OK-skip case**). Because none change, no healthy cell can fire a spurious
reconcile action from this work.

**Rule 4 — do not overload exit codes (non-zero aborts the Windows cron under `$ErrorActionPreference='Stop'`,
and the bridge runs `set -euo pipefail`).** The extractor returns **0 on the candidates-found path** (candidates
are not errors); the "new candidates" signal travels via the last-seen state + `notify.sh`, **not** the exit
code (`test_returns_zero_on_candidates`). The bridge §7c block resolves its **own** `HPY` launcher (no `RBPY`,
which is unbound at §7c's position — under `set -u` an unbound-array expansion aborts the shell *before* `||` is
evaluated), `HPY` assigned on both `if/else` branches before use, and the call is `|| echo "…(soft)"`-guarded.
Re-verified: no path through §7c can abort the bridge; same `.sh` covers Windows. Locked by
`test_bridge_wiring_self_contained`.

**Rule 5 — cross-machine state-ref pushes HANG; bound them.** The default path performs **no push** — candidates
are committed by the existing `commit-learning-artifacts.sh` `.claude/state/` commit (`:96,113`), and Hermes is
single-box so no fleet transfer is needed. The optional `--publish` to `hermes-pattern-candidate-state` is **OFF
by default** and bounded by a **90s `subprocess` timeout, fail-soft** (exact `publish_fingerprint` clone,
`curate_session_memory.py:240-256`) — a hung push degrades to a `publish-timeout (90s)` string and never stalls
the bridge. The bridge's own `git push` of `.claude/memory/` is untouched. Locked by
`test_publish_off_by_default` + `test_publish_bounded_timeout`.

**Rule 6 — assess whether a NEW MATRIX DIMENSION is warranted.** Assessed: **no** (§Decision). Single-box
candidate pipeline hooking into the existing bridge + candidate-file substrate; dead-man's-switch coverage
already exists via `memory_freshness_verdict` (#3255, `build-equality-matrix.py:274-304`) and the bridge's
notify-on-fail. `addsMatrixDimension = false`.

**Other risks:**
- **(BLOCKER, round-2) De-dup nullified by the bridge's own §2-3 self-injection.** The bridge re-injects the
  Hermes-authored `MEMORY.md`/`USER.md` lines into the `BRIDGE:START`…`BRIDGE:END` block of `agents.md` on every
  run (`:65-112`), *before* §7c; with `_slug('- foo') == _slug('foo')` a naive `MEMORY.rglob` index would mark
  every candidate already-canonical → ZERO candidates forever. **Fixed in-scope** by stripping the bridge block
  from `canonical_text_index()` (Design decision #3, `strip_bridge_block`), so de-dup compares candidates only
  against human-promoted memory — independent of §7c placement.
  `test_dedup_survives_bridge_injection` + `test_dedup_drops_human_promoted_outside_block` +
  `test_strip_bridge_block_removes_span`.
- **(MINOR, round-2) Bridge §8 `--commit` stash/pop churns the tracked candidate file.** §7c writes the
  git-tracked `hermes-pattern-candidates.md`; the bridge does not stage it, so §8's `git diff-index --quiet HEAD`
  (`:334`) sees it dirty and `git stash push`/`git stash pop` it around the rebase, and a stash-pop **conflict**
  (`git stash pop 2>/dev/null || echo WARNING`, `:362`) can park the write in the stash. Acknowledged: this is
  **not data loss** because (a) `append_candidates_md` is **idempotent** (de-dups against existing file keys —
  `test_append_idempotent_no_double`), (b) the candidate content is a **pure deterministic function** of durable
  Hermes memory + canonical memory, so a stash-then-restore OR a lost-stash revert only **defers** the append to
  the next bridge cycle, and (c) the last-seen JSON is **gitignored** (not stashed), so alert-suppression state
  survives the churn. Worst case = a one-cron-cycle delay in the candidate appearing, never permanent loss. No
  code is added to the bridge's §8 commit/stash path (the candidate file stays out of the bridge's `git add`
  pathspec; `commit-learning-artifacts.sh` owns its commit).
- **PII/secret leak into a git-tracked candidate file (must-fix #1).** Mitigated by the fail-closed
  `.legal-deny-list.yaml` scrub (drop, don't redact) + emitting summaries not raw Hermes lines + the acceptance
  `legal-sanity-scan.sh` gate. `test_scrub_sensitive_failclosed`.
- **De-dup completeness.** Gate indexes the **full** canonical CONTENT surface (`MEMORY.rglob('*.md')` text, no
  cap, no mtime, bridge-block stripped), not `memory_delta`'s capped basename slice — so older promoted patterns
  are not silently re-proposed. `test_dedup_uses_full_content_surface`.
- **Cross-dir import fragility (minor #3).** Explicit `sys.path.insert(0, scripts/curation)` before the import
  (mirrors `detect_skill_drift.py:49-54`); without it the import raises `ImportError`. `test_cross_dir_import_resolves`.
- **Feedback loop via `cross-provider.md`.** The bridge writes that file from canonical memory; reading it would
  re-propose promoted content forever. Source set excludes it. `test_never_reads_cross_provider_md`.
- **Candidate-file unbounded growth.** Idempotent append + last-seen suppression; an unchanged set never
  re-appends. (Follow-on: a compaction pass if the file grows large — out of scope.)
- **Future enhancement (non-blocking; round-1 "open question" RESOLVED).** The bridge still promotes Hermes
  facts directly into the `agents.md` BRIDGE block with no review. The de-dup fix above means this no longer
  breaks the candidate feature. Whether to *additionally* narrow the direct injection to environment-facts only
  and route *learnings* exclusively through the candidate gate is a **genuine, separable future enhancement** —
  it would change canonical-memory behavior and is **not** required for this issue's correctness. Flagged for the
  owner; out of scope here.

---

## Rollout

1. Land behind the existing daily bridge cron — first real run emits **non-empty** candidates on dev-primary the
   next bridge cycle (the blocker fix guarantees the de-dup no longer self-suppresses). No new cron, no new push.
   Windows/dev-secondary runs are silent no-ops (no Hermes).
2. Owner reviews `.claude/state/candidates/hermes-pattern-candidates.md` and **manually** promotes worthy items
   to a skill/memory/rule (the human gate). The file is a standing review queue, like the other `*-candidates.md`.
3. `notify.sh` fires only on NEW candidates, so the owner is pinged on change, not every bridge run.
4. Optional later: enable `--publish` (bounded) if fleet visibility is ever wanted — still no matrix cell.
5. Reversible: delete the §7c bridge block + the module; the candidate file is inert data. No canonical surface
   was ever mutated, so there is nothing to unwind.

---

## Complexity: T2

**T2** — one new pure-core module + one new test file, one guarded wiring edit to an existing script (the
bridge), reuse of the candidate-file + detector + bounded-publish substrate; multi-file and harness-touching but
**not** cross-provider-systemic and **adds no matrix dimension**. TDD mandatory; adversarial review at T2 scale =
2 providers (Claude + Codex), artifacts at `scripts/review/results/2026-06-27-plan-3253-claude.md` and
`…-3253-codex.md`.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (r1) | needs-revision → addressed | de-dup memory_delta mis-wiring (→ canonical content index); §7c RBPY out-of-scope Rule-4 abort (→ self-contained HPY launcher); cross-dir import (→ explicit sys.path insert); line/count/naming nits (→ corrected) |
| Codex (r2) | needs-revision → addressed | BLOCKER: bridge §2-3 self-injection nullifies de-dup in the same process (→ `strip_bridge_block` excludes the BRIDGE:START/END block from the canonical index; new survives/drops tests; open question resolved not deferred). MINOR: §8 stash/pop churns the tracked candidate file (→ idempotent append + deterministic re-extraction + gitignored last-seen; stash-pop-conflict edge acknowledged in Risks). Hard rules 1/3/4/5/6 re-verified OK; rule 2 N/A. |

**Overall result:** revised after round-2; blocker + minor both resolved in-scope.
