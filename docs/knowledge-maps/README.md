# Knowledge maps

Eight maps describe how the engineering ecosystem is laid out and how work moves through it. Each map
states the standard every machine is held to, the sources it was built from, and the commands that
regenerate it. They are the reference for keeping work, layout and practice the same on every
computer.

| Map | Covers |
|---|---|
| [file-structure](file-structure.md) | Work roots, reserved folders, worktree naming, where off-root work belongs |
| [repos](repos.md) | Repositories, purpose, visibility, lean-reset roots, one canonical clone per machine |
| [skills](skills.md) | Skill catalogue, rules, role agents, provider instruction files and how they deploy |
| [org-team](org-team.md) | Role types, decision rights, hand-offs between providers, channels |
| [machines](machines.md) | Machine classes, licence lanes, required runtimes, the readiness checklist |
| [ai-seats](ai-seats.md) | Provider lanes, stop lines, how each seat is best used, how usage is collected |
| [html-reviews](html-reviews.md) | Review pages, decision boards, saving beside the page, surface rules |
| [writing](writing.md) | Report, calc note, article and newsletter genres; claims, citations, register, review chain |

## Two layers

This repository is public, so each map here holds only the generic layer: the standard, the method
and the counts. The measured detail (per-machine readings, deviations, seat usage, page inventories,
registers and road maps) is held in the private fleet-ops repository under the same path,
`docs/knowledge-maps/<map>.yaml`, named by each file's `private_detail` key. That reference is
accessible only to the team.

## Format

Each `<map>.yaml` is the source of truth (`schema: knowledge-map/1`) with the keys `map`, `title`,
`purpose`, `owner`, `verified_at`, `sources`, `refresh`, `standard`, `entries`, `per_machine`,
`deviations` and `open_questions`. The `<map>.md` beside it is the plain-English reading. A map is
refreshed by running its `refresh` commands and re-reading `verified_at`; a map older than its
sources is stale and is not relied on until refreshed.

First built 27 November 2026 from live readings of every reachable machine, starting from the
existing status pages.
