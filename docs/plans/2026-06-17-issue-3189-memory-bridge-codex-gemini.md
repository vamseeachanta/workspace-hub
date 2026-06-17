# Plan for #3189: Bridge cross-provider memory to Codex/agy + topics INDEX + provider-neutral recall

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-06-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3189
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-17-plan-3189-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/memory/curate_readback_slice.py` — the ONE shared cross-provider read-back selector (`curate(source_dir, target, cap)`). Sources ONLY git-tracked `.claude/memory/` (machine-invariance F1), filters Claude-only entries by slug (F4), caps at entry boundaries (F5), deterministic (no body timestamp → no churn). `DEFAULT_CAPS = {"codex": 7000, "hermes": 2000}` — the extension point for a `gemini` target.
- Found: `scripts/memory/bridge-hermes-claude.sh` — §7b regenerates `config/agents/codex/MEMORY.runtime.md` + hermes slice via temp-file-then-`mv`-on-success; §6 mirrors auto-memory topics into `.claude/memory/topics/` (182 files); §8 pathspec-scoped commit, gated by `SLICE_OWNER`. No INDEX generation, no gemini target.
- Found: `config/agents/codex/MEMORY.runtime.md` (7069 B, `MANAGED by curate_readback_slice.py`) — the parity template for gemini.
- Found: `config/agents/codex/AGENTS.runtime.md:169-171` — the loader wiring (`## Consolidated Cross-Provider Memory (read at session start)`) to replicate for gemini.
- Gap: `config/agents/gemini/` has SOUL.runtime/SOUL.delta/settings.json but **no MEMORY.runtime.md**; `.claude/memory/topics/INDEX.md` doesn't exist; no `recall` skill (`find .claude/skills -iname '*recall*'` empty).

### Standards / LLM Wiki
Not applicable / none — control-plane harness, Client: N/A (wiki-sibling-routing doesn't apply).

### Documents consulted
- `docs/plans/2026-05-28-issue-2841-...md` — direct predecessor; built `curate_readback_slice.py` + the codex surface + F1 machine-invariance fix + single-designated-machine commit. #3189 extends this; must preserve F1/F4/F5 + determinism.
- `config/scheduled-tasks/schedule-tasks.yaml` — `hermes-claude-bridge` (04:20 UTC, prefer dev-primary, commits to repo) runs `bridge-hermes-claude.sh`; new INDEX + gemini-slice ride this run — **no schedule change**.
- `scripts/readiness/provider_harness_parity.py:97-118` — `_memory_read()` parity check (codex requires AGENTS.runtime.md + MEMORY.runtime.md); extend for gemini.
- `.claude/rules/coding-style.md` — no abs paths (`check-no-abs-paths.sh`); harness files ≤20 lines (`check-harness-file-size.sh`; GEMINI.md is 10 lines today).
- `install-soul-runtime.sh:79-84` — Gemini CLI loads `GEMINI.md` (workspace + ~/.gemini), NOT SOUL.md → the read instruction must live in GEMINI.md (+ SOUL.delta.md so build-soul-runtime doesn't drop it).

### Gaps
No INDEX generator; no gemini target in curate + no gemini MEMORY.runtime.md; no Gemini startup memory pointer; no provider-neutral recall.

### Evidence
#3189 OPEN; #3058 OPEN (parent). Files verified present/missing as above (`ls`/`find` empties prove absence). Topic classes via `grep '^type:'`: 85 feedback + memory/reference/user; 180/182 carry frontmatter → class grouping derives from `type:` + slug prefix (no parsing invention). Sources consulted: 6.

---

## Approach / Deliverable
On each `hermes-claude-bridge` run, regenerate `.claude/memory/topics/INDEX.md` (class-grouped) + a gemini-target `config/agents/gemini/MEMORY.runtime.md` (parity with codex), plus a provider-neutral `scripts/memory/recall.py` + `.claude/skills/memory/recall/` skill (keyword + class filter) returning the same topic set regardless of invoking provider.

- `build_topics_index.py` (new, stdlib): parse frontmatter (tolerate missing), classify by `type:`/slug, group, render deterministically (no body timestamp), exclude self.
- `recall.py` (new, stdlib, CLI-first): keyword + optional class filter over topics, deterministic ordering (cross-provider parity).
- `curate_readback_slice.py`: add `"gemini": 7000` to `DEFAULT_CAPS` — reuses the codex code path (same F1/F4/F5), no new logic.
- Bridge: call `build_topics_index.py` after §6; add gemini slice to §7b slice-owner block + §8 commit pathspec (temp-then-mv).
- Gemini wiring: one-line session-start read pointer in `GEMINI.md` (keep ≤20 lines) + `SOUL.delta.md` (survives rebuild).
- `provider_harness_parity.py`: extend `_memory_read()` to verify the gemini surface.

## Files to change
Create: `scripts/memory/build_topics_index.py`, `scripts/memory/recall.py`, `scripts/memory/tests/test_build_topics_index.py`, `scripts/memory/tests/test_recall.py`, `config/agents/gemini/MEMORY.runtime.md` (generated), `.claude/skills/memory/recall/SKILL.md`.
Modify: `scripts/memory/curate_readback_slice.py` (gemini cap), `scripts/memory/tests/test_curate_readback_slice.py`, `scripts/memory/bridge-hermes-claude.sh`, `GEMINI.md`, `config/agents/gemini/SOUL.delta.md`, `scripts/readiness/provider_harness_parity.py`, `docs/plans/README.md`.

## TDD test list
index-groups-by-class; index-excludes-self; index-deterministic (byte-identical, no churn); index-tolerates-missing-frontmatter; recall-keyword-match; recall-class-filter; recall-no-match-empty; recall-deterministic-ordering (cross-provider parity); curate-gemini-target (valid capped slice, same filter polarity); curate-gemini-parity-with-codex (byte-identical at equal cap). Red first.

## Risks / open questions
- **Churn:** bridge commits `.claude/memory/` daily across machines — INDEX + gemini slice MUST be deterministic (inherit curate's contract). Top defect-hunt.
- **Gemini loader reality:** instruction must live in GEMINI.md (actually-loaded) not just SOUL.runtime.md (phantom). Verify Gemini surfaces it before claiming parity.
- **Slice-owner asymmetry:** gemini slice must be gated by the same `SLICE_OWNER` guard + §8 pathspec as codex, else never-commits or per-machine divergence.
- **Open:** recall as CLI-only (recommended, stdlib, runs under codex/agy) vs also MCP tool? INDEX taxonomy = frontmatter `type:` (recommended) vs semantic problem-classes? Flag at approval.

## Adversarial review (T2; default 3-agent since cross-provider artifact)
PENDING. Force: determinism/churn (F1 hazard); slice-owner gating; self-indexing (INDEX excluded from §6 re-mirror); recall parity ORACLE (plant a known topic, assert identical ordered set per provider — not just "returns results", per #3116); leak polarity (gemini reuses F4 default-include).

## Acceptance criteria
Mirror issue #3189: INDEX generated+regenerated class-grouped; gemini MEMORY.runtime.md + GEMINI.md/SOUL.delta wiring; recall skill invokable by all 3 providers returning identical ordered set; tests pass; no regression; abs-path + harness-size + legal scans pass; bridge dry-run produces artifacts without committing; two runs byte-identical (no churn); review artifacts posted.
