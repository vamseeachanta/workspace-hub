# `docs/plans/overnight-prompts/` — wave index

This directory holds prompt packs for batched / overnight planning waves. Each wave lives in its own dated subdirectory.

## Layout convention (canonical, going forward)

```
docs/plans/overnight-prompts/
├── README.md                          # this file (wave-index)
└── YYYY-MM-DD-<wave-slug>/
    ├── README.md                      # wave-level index + boundaries
    ├── morning-synthesis.template.md  # copy-on-write synthesis template
    ├── streams/<stream-slug>.md       # one prompt per stream
    ├── child-issue-drafts/<stream-slug>.md  # markdown stubs (NOT auto-filed)
    ├── results/<stream-result>.md     # per-stream wave results
    └── logs/<stream>.log              # worker logs
```

Older waves use a flat `terminal-N-*.md` layout. New waves should use the structured `streams/<slug>.md` + `child-issue-drafts/<slug>.md` layout.

> **Naming note:** earlier drafts used `prompts/` for the per-stream prompt directory. That name conflicts with `.gitignore:427` (`prompts/` excluded globally as transient agent dispatch artifacts). The canonical name is `streams/`.

## Universal rules

- **Planning-only by default.** Overnight runs do not authorize extraction, raw-data ingestion, or production writes unless an approved separate plan covers it.
- **No self-approval.** Workers must NOT apply `status:plan-approved`. Approval is a user-in-loop gate.
- **No `gh issue create` in workers.** Child-issue drafts in `child-issue-drafts/` are markdown stubs; the user files them.
- **Zero write-overlap across streams.** Each stream declares allowed/forbidden paths; the wave README maps the contention surface.
- **Boundary files** (e.g., `docs/plans/README.md`, wiki indexes, wiki logs, `.gitignore`) are out of scope for overnight workers unless the corresponding issue is `status:plan-approved`.
- **No raw bulk copy.** No `/mnt/ace` writes. No raw files into wiki `raw/` or git.
- **Citation contract** ([#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471), [#2482](https://github.com/vamseeachanta/workspace-hub/issues/2482), `.claude/rules/calc-citation-contract.md`) applies to any standards-page proposal.

## Waves

| Date | Wave | Umbrella issue | Status |
|---|---|---|---|
| 2026-04-21 | nightly CI batch | n/a | archived |
| 2026-04-22 | CI plan resubmit / rerun review / tier1 knowledge | n/a | archived |
| 2026-04-28-12h-continuation | 12h continuation | n/a | archived |
| 2026-04-28-elements-wave | Elements corpus planning | [#2540](https://github.com/vamseeachanta/workspace-hub/issues/2540) | mostly executed; SESA still in plan-review |
| 2026-04-28-night-both-machines | both-machines night batch | n/a | archived |
| 2026-04-29-credit-burn-approval-readiness | approval-readiness | n/a | archived |
| 2026-04-29-next-wave-autofeed | next-wave autofeed | n/a | archived |
| 2026-04-29-reverse-prompt-48h | 48h reverse-prompt | n/a | archived |
| 2026-04-29-weekly-gtm-targets | weekly GTM targets | n/a | archived |

Waves not listed here exist as flat-layout subdirs; consult their internal `README.md` (where present) or the wave's master plan.

## Adding a new wave

1. Create `YYYY-MM-DD-<slug>/` with the canonical layout above.
2. Author `README.md` declaring umbrella issue, boundaries, streams (one row per stream with corpus + size).
3. Author one `streams/<stream-slug>.md` per stream with explicit allowed / forbidden paths and unique output artifact paths.
4. Author one `child-issue-drafts/<stream-slug>.md` per stream as a markdown stub for the user to file (do NOT auto-file).
5. Author `morning-synthesis.template.md` with stream review, approval-readiness, blocked items, next-execution recommendation.
6. Add a row to the Waves table above.
