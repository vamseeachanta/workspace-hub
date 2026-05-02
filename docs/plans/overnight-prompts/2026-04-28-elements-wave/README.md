# Wave: 2026-04-28 Elements overnight planning

> **Umbrella issue:** [#2540](https://github.com/vamseeachanta/workspace-hub/issues/2540)
> **Predecessors:** [#2535](https://github.com/vamseeachanta/workspace-hub/issues/2535) (metadata-first indexing), [#2536](https://github.com/vamseeachanta/workspace-hub/issues/2536) (first-pass deep extraction), [#2526](https://github.com/vamseeachanta/workspace-hub/issues/2526) (Elements ingest), [#2534](https://github.com/vamseeachanta/workspace-hub/issues/2534) (retention cleanup, gated until 2026-05-28)
> **Mode:** planning-only — extraction is gated behind a separate user-in-loop approval

## Wave goal

Produce safe, bounded, approval-ready planning artifacts for the four remaining metadata-only Elements corpora. The wave does NOT extract content, does NOT write to `/mnt/ace`, and does NOT self-approve any plan.

## Boundaries (apply to every stream)

- Raw `/mnt/ace` files remain the source of record. No raw bulk copy into git or wiki.
- No write to `/mnt/ace` (read-only listings only).
- No deletion or movement of `_from_elements/` provenance staging.
- No persisted full-text dump in `.planning/`, `docs/`, or `knowledge/`.
- No vendor-derivative content under `knowledge/wikis/**/sources/` per [#2482](https://github.com/vamseeachanta/workspace-hub/issues/2482).
- No `wiki/standards/<code-id>.md` page without verified frontmatter (`code_id`, `publisher`, `revision`) per [#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471).
- No `status:plan-approved` self-labeling. Approval is a separate user-in-loop gate.
- [#2534](https://github.com/vamseeachanta/workspace-hub/issues/2534) cleanup remains blocked until 2026-05-28.

## Streams (zero write-overlap)

| Stream | Slug | Issue | Corpus | Size / files |
|---|---|---|---|---|
| 1 | `sesa-lng` | [#2541](https://github.com/vamseeachanta/workspace-hub/issues/2541) | `/mnt/ace/doris/62092_sesa` | 1.7 GB / 889 files |
| 2 | `doris-university` | [#2542](https://github.com/vamseeachanta/workspace-hub/issues/2542) | `/mnt/ace/doris/training` | 11 GB / 1,129 files |
| 3 | `doris-codes` | [#2543](https://github.com/vamseeachanta/workspace-hub/issues/2543) | `/mnt/ace/doris/codes` | 25 GB / 70,400 files |
| 4 | `woodfibre-lng` | [#2544](https://github.com/vamseeachanta/workspace-hub/issues/2544) | `/mnt/ace/acma-projects/31522-woodfibre-lng` | 1.8 TB / 10,729 files |

## Layout

```
2026-04-28-elements-wave/
├── README.md                          # this file
├── master-plan.md                     # legacy contention map (pre-existing)
├── morning-synthesis.template.md      # synthesis template (copy-on-write)
├── prompts/                           # one prompt per stream (slug-based)
│   ├── sesa-lng.md
│   ├── doris-university.md
│   ├── doris-codes.md
│   └── woodfibre-lng.md
├── child-issue-drafts/                # markdown stubs (NOT auto-filed)
│   ├── sesa-lng.md
│   ├── doris-university.md
│   ├── doris-codes.md
│   └── woodfibre-lng.md
├── results/                           # per-stream wave-result summaries
│   ├── README.md
│   ├── terminal-1-sesa.md
│   ├── terminal-2-doris-university.md
│   ├── terminal-3-doris-codes.md
│   └── terminal-4-woodfibre.md
├── logs/                              # per-stream worker logs (PID + stdout)
│   └── ...
├── terminal-1-sesa.md                 # legacy flat prompt (pre-existing)
├── terminal-2-doris-university.md
├── terminal-3-doris-codes.md
└── terminal-4-woodfibre.md
```

The `terminal-N-*.md` flat-layout prompts predate this README and reflect the launched workers. The `prompts/<slug>.md` files in this canonical layout are the durable reference; both forms point at the same write contract.

## Status (snapshot)

| Stream | Issue state (2026-05-02) | Plan / intel artifacts |
|---|---|---|
| sesa-lng | OPEN — `status:plan-review` | drafted; awaiting clearance gate before extraction |
| doris-university | CLOSED — `status:done` | bounded metadata-only execution landed in commit `b0dac4608` |
| doris-codes | CLOSED — `status:done` | bounded metadata-only execution landed in commit `b0dac4608` |
| woodfibre-lng | CLOSED — `status:plan-approved` | scout-only artifacts landed; extraction remains a separate gated future plan |

## Operational guidance

- **Launch:** `claude -p --permission-mode acceptEdits --no-session-persistence ...` per stream prompt; see legacy `master-plan.md` for the original launch invocations.
- **Synthesis:** copy `morning-synthesis.template.md` to `morning-synthesis-YYYY-MM-DD.md` and fill it in main session (do NOT delegate synthesis to a subagent).
- **Approval:** ONLY the user can apply `status:plan-approved`. Do not delegate.
- **Cleanup:** [#2534](https://github.com/vamseeachanta/workspace-hub/issues/2534) is independent — do NOT bundle into any extraction approval.
