#!/usr/bin/env bash
# Read-only checkout provenance. Sourced after WS is resolved by the collector.
# Field semantics and the measured-path allowlist are preserved from the parent.

MEASURED=(.claude/skills .claude/memory/context.md .claude/memory/agents.md .codex/skills \
          .claude/dispatch .claude/rules AGENTS.md \
          .claude/hooks/plan-approval-gate.sh .claude/settings.json \
          scripts/readiness/harness-config.yaml scripts/readiness/provider_harness_parity.py \
          config/agents/claude/SOUL.runtime.md config/agents/codex/AGENTS.runtime.md \
          config/agents/codex/MEMORY.runtime.md config/agents/hermes/SOUL.runtime.md \
          config/scheduled-tasks/schedule-tasks.yaml)
checkout_sha="unknown"; dirty=false; behind_main="unknown"; ahead_main="unknown"; origin_ref_age_h="unknown"
if git -C "$WS" rev-parse --git-dir >/dev/null 2>&1; then
  checkout_sha=$(git -C "$WS" rev-parse --short HEAD 2>/dev/null); : "${checkout_sha:=unknown}"
  # dirty = TRACKED changes to the measured allowlist only. --untracked-files=no excludes
  # untracked noise (.DS_Store, __pycache__, editor swap files) that would otherwise
  # false-STALE a healthy machine on benign cruft inside a measured directory.
  [[ -n "$(git -C "$WS" status --porcelain --untracked-files=no -- "${MEASURED[@]}" 2>/dev/null)" ]] && dirty=true
  # behind_main / ahead_main = best-effort vs the LOCAL origin/main ref (no fetch). "unknown" if
  # ref absent ⇒ fail-closed downstream (BC2). BOTH directions matter: behind = missing upstream
  # commits (the #2801 stale-tree case); ahead = local commits NOT on origin/main (an unpushed
  # feature checkout whose measured dims are non-canonical). Either ≠0 ⇒ not the canonical tree.
  bm=$(git -C "$WS" rev-list --count HEAD..origin/main 2>/dev/null)
  [[ -n "$bm" ]] && behind_main="$bm"
  am=$(git -C "$WS" rev-list --count origin/main..HEAD 2>/dev/null)
  [[ -n "$am" ]] && ahead_main="$am"
  # origin-ref freshness from the last fetch, WITHOUT fetching (BC2): a stale LOCAL origin/main
  # ref false-negatives behind_main, so record its age and let the matrix fail-closed on it.
  # Use --git-common-dir, NOT --git-dir: in a linked worktree the shared FETCH_HEAD and
  # refs/remotes/origin/main live in the COMMON dir; --git-dir points at the per-worktree dir
  # that holds neither, which would false-STALE every worktree-based collection.
  gd=$(git -C "$WS" rev-parse --git-common-dir 2>/dev/null)
  # Join to WS only when gd is RELATIVE. On Windows (Git Bash) a linked worktree's --git-common-dir
  # is an absolute drive-letter path (e.g. C:/repo/.git) that does NOT begin with "/", so a bare
  # "!= /*" test wrongly treats it as relative and corrupts it (WS/C:/repo/.git) -> FETCH_HEAD not
  # found -> origin_ref_age_h "unknown" -> the matrix false-STALEs every worktree-based collection.
  # winabs matches a Windows drive root (C:/ or C:\); git emits forward slashes here in practice.
  winabs='^[A-Za-z]:[/\]'
  [[ -n "$gd" && "$gd" != /* && ! "$gd" =~ $winabs ]] && gd="${WS}/${gd}"
  # Age-check a fetch that proves origin/main. Prefer FETCH_HEAD only when its content explicitly
  # names branch 'main'; otherwise fall back to the tracked origin/main ref. This handles the
  # Windows wrapper's freshness preflight where origin/main may not move for >12h, while still
  # avoiding unrelated FETCH_HEAD refreshes from other branches.
  ref=""
  origin_main_sha="$(git -C "$WS" rev-parse --verify refs/remotes/origin/main 2>/dev/null || true)"
  if [[ -f "${gd}/FETCH_HEAD" ]] && grep -q "branch 'main' of " "${gd}/FETCH_HEAD" 2>/dev/null; then
    fetch_head_sha="$(awk "/branch 'main' of / {print \$1; exit}" "${gd}/FETCH_HEAD" 2>/dev/null)"
    if [[ -n "$fetch_head_sha" && -n "$origin_main_sha" && "$fetch_head_sha" == "$origin_main_sha" ]]; then
      ref="${gd}/FETCH_HEAD"
    fi
  elif [[ -f "${gd}/refs/remotes/origin/main" ]]; then
    ref="${gd}/refs/remotes/origin/main"
  fi
  if [[ -z "$ref" && -f "${gd}/refs/remotes/origin/main" ]]; then
    ref="${gd}/refs/remotes/origin/main"
  fi
  if [[ -n "$ref" ]]; then
    mt=$(date -r "$ref" +%s 2>/dev/null); now=$(date +%s 2>/dev/null)
    [[ -n "$mt" && -n "$now" ]] && origin_ref_age_h=$(( (now - mt) / 3600 ))
  fi
fi

