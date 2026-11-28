# Skills knowledge map

Source of truth: [`skills.yaml`](skills.yaml). Verified 2026-11-27 15:50Z against
workspace-hub `origin/main` ffe9d649e. Per-machine deployment state, CLI versions,
link types, drift and local-only skills are held in the private detail map
(fleet-ops `docs/knowledge-maps/skills.yaml`, private repository).

## What the map covers

The map lists every agent skill, slash command, rule file, role agent and provider
instruction file in workspace-hub, states how each provider discovers them, and
records how the provider runtime files are built, deployed and checked on a
machine. The governing rule is `.claude/rules/soul-deployment-drift.md`: a machine
loads what `origin/main` holds, compared by SHA-256, and a link into a stale
checkout is drift.

## Skill trees

| Tree | Role | Active skills |
|---|---|---|
| `.claude/skills` | Canonical tree; wins on conflict | 477 (4 top level, 473 in 25 category folders); 2,100 archived |
| `.agents/skills` | Copy for Codex native project discovery | 965; 333 identical to canonical, 83 differ, 549 copy-only |
| `.claude/commands` | Claude Code slash commands | 166 |
| `config/agents/skill-index-full.yaml` | Flat index for the provider-neutral router | generated |

Table 1: Skill trees on `origin/main`.

The largest categories are `data` (85), `coordination` (60), `development` (54),
`workspace-hub` (45), `workspace-hub-learned` (38), `business` (30), `engineering`
(29) and `software-development` (25). The YAML lists every skill with its first
130 characters of purpose and the state of its `.agents/skills` copy.

## How each provider finds skills

- **Claude Code** lists the account-synced skills in `<home>/.claude/skills`, the four
  top-level repository skills and the slash commands. In the observed Claude Code
  2.1.332 session it did not list the 473 category-nested skills; those are reached
  through `scripts/ai/skill_router.py` over the index, or by reading the file.
- **Codex** reads its built-in `<home>/.codex/skills/.system` and the repository's
  `.agents/skills` when the session runs inside the repository.
- **Gemini** was observed in June 2026 to prefer `.agents/skills` over
  `.gemini/skills`; current behaviour is not verified.
- **Hermes** reads its own skill directories, with archive folders excluded by a
  patch in `config/agents/hermes/patches/`.
- **Agy** has a reference runtime file only.

No skill is marked `user-invocable: false`; one (`development/zoom-out`) sets
`disable-model-invocation`.

## Rules and role agents

`.claude/rules` holds 23 rule files plus an index; Claude Code loads all of them in
a session started inside workspace-hub. Each is summarised in one line in the YAML.
`.claude/agents` holds eight role agents: the six coordinator roles (scout,
explorer, builder, verifier, gap-checker, reporter) and two domain operators
(orcaflex-specialist, cfd-lane-operator). A portable reviewer definition sits in
`config/agents/agent-defs/`.

## Provider instruction files

`config/agents/SHARED_SOUL.md` (201 lines) is the shared source. Each provider has
a delta; `scripts/agents/build-soul-runtime.sh` combines them into a runtime file
that is never hand-edited.

| Provider | Runtime file | Destination on a machine | Deployment policy |
|---|---|---|---|
| claude | `claude/SOUL.runtime.md` | `<home>/.claude/CLAUDE.md` (legacy) or `<home>/.claude/rules/workspace-soul.md` (native) | symlink plus loader admission |
| codex | `codex/AGENTS.runtime.md` | `<home>/.codex/AGENTS.md` | symlink |
| hermes | `hermes/SOUL.runtime.md` | `<home>/.hermes/SOUL.md` | symlink |
| gemini | `gemini/SOUL.runtime.md` | `<home>/.gemini/GEMINI.md` | not deployed (issue 2719 Phase 6) |
| agy | `agy/SOUL.runtime.md` | `<home>/.agy/SOUL.md` | not deployed (issue 3573) |

Table 2: Provider runtime files under `config/agents/` and their deployment policy.

`AGENTS.md` at the repository root is the 20-line repository contract. CLAUDE.md is
retired as a repository file.

## Deployment and linking

- `scripts/agents/install-soul-runtime.sh` creates the Codex and Hermes symlinks,
  backs up any copy it replaces, and preserves the Claude link. It refuses to leave
  a copy on Windows, where `ln -s` copies by default.
- `scripts/enforcement/check-soul-deployment-drift.sh` reports each provider as
  CURRENT, STALE, UNLINKED, ABSENT, BLOCKED or NOT-DEPLOYED and exits 1 on any
  drift. A copy is UNLINKED even when its bytes match.
- `scripts/propagate-ecosystem.sh` links the shared skill templates in
  `.claude/skills/_internal/` into each ecosystem repository (symlink on Unix,
  junction on Windows). `scripts/skills/resync-skill-links.sh` reports link health
  and re-propagates only with `--apply`.
- Before any restore or delete on a skill link path, its link type is probed
  (`.claude/rules/windows-junction-restore-safety.md`). A `git restore` through a
  junction emptied the canonical tree on 2026-07-16.

## Clean-up workflow

The standard machine clean-up prompt, its runbook, the manifest-driven executor,
the merge hold check and the 6-hourly consistency run sit in the private fleet-ops
repository. The prompt needs no catalogue skill: it is pasted into any provider
session and depends on git, gh, Python, the rule files named in the YAML and the
workspace-hub scripts `workstation-hygiene.sh`, `check-soul-deployment-drift.sh`
and `resync-skill-links.sh`. Whether each machine can run it from origin is
recorded in the private map.

## Per-machine state

Seven machines were probed read-only on 2026-11-27. The private map records 21
deviations. This public layer carries the count only.

## Open questions

1. Should frequently used category-nested skills be promoted to the top level or
   exposed as commands, since Claude Code does not list them?
2. Is a sync or a reduction of `.agents/skills` planned? 83 copies differ and 549
   skills exist only in the copy.
3. `.claude/skills/README.md` states 298 skills in 9 domains; it is out of date.
4. `.claude/skills/eng/` holds 8 flat notes without `SKILL.md` that no provider
   discovers.
5. One skill folder under `data/energy` carries a client name (shown in the YAML by
   codename). A neutral folder name is recommended.
6. Which revision of the cleanup and consistency tools should each machine run?

## Refresh

The exact commands are in `refresh.commands` of the YAML. The two most used:

```bash
bash scripts/enforcement/check-soul-deployment-drift.sh      # this machine, against origin/main
bash scripts/skills/resync-skill-links.sh --verbose          # shared-skill link health, report only
```
