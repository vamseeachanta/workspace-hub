# HTML review and decision surfaces

Map `html-reviews`, verified 2026-11-27. Machine-readable twin: `html-reviews.yaml`.

This map describes the mechanism of the HTML review surfaces: status pages, road maps, decision boards
and report review copies. It covers the page types, how pages are built, wrapped, served, saved and
refreshed, the decision-board contract and the review-copy conventions.

The page inventory, freshness, host folders and deviations are kept in the private map
`fleet-ops docs/knowledge-maps/html-reviews.yaml`. fleet-ops is a private repository, so readers without
team access cannot open that file.

Governing texts:

- `.claude/rules/human-decision-boards.md`
- `docs/standards/review-and-communication-standard.md` §3
- `.claude/rules/report-audience-and-surface.md`
- `docs/standards/FINAL_REPORT_VERIFICATION.md`

## 1. Page-family types

| Type | Purpose | Cadence | Surface |
|---|---|---|---|
| Status page | Current state of repositories, machines, migrations, PRs, datasets | Hourly | Internal |
| Ecosystem road map | The owner's single starting page; status links and tiles at the top | Hourly | Internal |
| Project road map | One programme and its milestones | Hourly, or one-off for an approved revision | Internal |
| Client road map | One client's programme: internal review page plus a client copy without internal sections | Per approved revision | Internal; the client copy is a deliverable |
| Register road map | One page per repository, stream or client, generated from the work register, plus an index | Hourly | Internal |
| Live list | The single list of items waiting on the owner | Hourly | Internal |
| Report review copy | A draft with the comment layer, one folder per revision round | Per round | Internal |
| Decision board | One card per owner decision, recommendation marked | Per round | Internal |
| Human-review pack | Evidence beside expectations, check table, missing evidence, reviewer decision | Per round | Internal |
| Peer or client review copy | Stand-alone offline HTML with comment layer and how-to banner | Per round | Client or peer |

On the day measured, the private map recorded 53 stable-link pages (16 wrapped families and 36 register
road maps), 275 review-copy folders, 27 decision-board rounds and 5 hosted Artifacts.

## 2. Build, wrap and serve

- **Model-free refresh.** A scheduled mechanical pass runs the builders and then the wrapper. No model is
  called in the refresh path.
- **Clean page, then review copy.** Builders write a clean page (`--no-review`). Only the wrapper writes the
  review copy.
- **One failure stays local.** A failing builder is reported as one line and the last good page is kept;
  the rest of the pass still runs.
- **Guards on the owner's and the client's copy.** A forbidden-word list (internal terms, host names) is
  checked before the owner's copy is written. A client-copy test asserts that internal-only sections never
  appear in a client copy.
- **Serving.** A local static HTTP server, bound to the loopback address on a fixed port, serves the review
  root. A loopback server is an internal surface, not a hosted one. Save never depends on the server.

### Stable links (owner, 22 Nov 2026)

- Each page family has one fixed link. The link and the tab title carry no revision number.
- A families JSON records, per family:
  - name and kind;
  - source page;
  - builder (`from`);
  - regex patterns for earlier numbered copies.
- The wrapper writes `<name>-review.html`. Links to older numbered copies are rewritten to the stable link,
  and retired addresses get forward pages.
- When a static family gets an approved revision, the revision is copied over `_sources/<name>.html` and the
  numbered copy moves to `_superseded`.
- The browser storage key is fixed per family, so unsaved comments survive the hourly rebuilds.

### Freshness badge and status tiles

- **Badge colour.** Green when the data age is ≤ 1.5× the cadence, amber ≤ 3×, red > 3× with the word STALE.
  A one-off page (cadence null) shows its date only.
- **Oldest source wins.** A page that reads several sources shows the oldest source's time, so a fresh
  rebuild over old data still reads stale. The tooltip lists every source and its time.
- **Status tiles.** Each tile is filled from a live source read at build time and names that source. A tile
  without a live source is marked unverified and states why.

## 3. Comment layer and review copies

The canonical injector is `tools/html-review/make_review_copy.py SRC.html OUT-review.html STORAGE_KEY`
(issue 3920). It leaves the source unchanged.

- **What can be commented.** A text selection (comment, replace-with, delete) or a whole block. A review
  also takes an overall verdict and a general comment.
- **Where Save writes.** `<page stem>.json` is written beside the page, never to Downloads. Each save also
  writes a timestamped copy, `<page stem>-<UTC yyyymmddThhmmssZ>.json`.
- **What the JSON records.**
  - the page;
  - the report version (source SHA-256 prefix and modification time);
  - the report folder;
  - the export time;
  - per comment: quote, section, `data_src`, comment text, time and a stable id.
- **Merging.** Save, Load and folder merge combine records rather than replace them, and deletion records
  are kept. Comments made on another revision are announced but not merged.
- **Banner.** Open the page from disk in Edge or Chrome, select text, comment and save. Choose the page's
  own folder when asked, and reload a revised page before continuing.
- **Second injector.** The desk's hourly pages use an older injector in fleet-ops. It downloads saves for a
  filer, which archives them in the private repository (see §7).

### Review loop

1. The owner comments, saves the JSON beside the page and says "review".
2. The agent reads the JSON in every location where the page was placed. It identifies the applicable file
   by report identity and revision; modification time alone does not establish applicability.
3. Each comment receives one disposition: incorporated, deferred with a reason, or needs a decision.
4. The report and the review copy are regenerated and re-verified. The saved JSON is read back, and rounds
   are kept as `-rN.json`.

## 4. Decision-board mechanism

| Element | Contract |
|---|---|
| Card | Question with evidence, impact, options, recommendation and a note field; one card per decision |
| Recommendation | The recommended option has a dashed outline and a text label |
| Build | `cards.py` writes `snapshot/items/<ID>.json`; `make.py` derives `<board>.html` from the board template and builds `<board>-local.html` |
| Location | The session's `output/<topic>/decisions/` folder |
| Save | Writes `<board>.json` beside the HTML in every location the page is placed, never to Downloads |
| Folder | The first Save asks once for the folder (`showDirectoryPicker`); the page refuses a folder that does not hold the page itself; the handle is kept in IndexedDB |
| History | Each save also writes `<board>-<UTC yyyymmddThhmmssZ>.json` (owner decision D03, 2026-10-08) |
| Load | On opening, the page loads decisions already saved beside it |
| No write access | A plain message is shown and entries stay in the tab; an agent that recovers them from browser storage records that it did so |
| Rounds | A new round is a new page (`-rN`) with a new JSON; a decided board is never edited |
| Consent | Decisions come only from saved board JSON or an explicit owner instruction; an undecided card is not consent |
| Reload | After cards are added, the owner is told to reload; a stale tab once exported a file that lacked the new cards |
| Scope | The owner decides client-facing messages, spending and items he already holds; the team decides everything else |

## 5. Surface rules

| Surface | Client identifiers | Cost models, host names | Tooling defects |
|---|---|---|---|
| Internal (local disk, loopback server) | allowed | allowed | allowed |
| Client deliverable | required | never | never |
| Hosted (Artifact, share link, static host) | redacted | never | never |

Before a page is handed over, the rendered output is inspected, links and scripts are checked, and Save,
Load and read-back are smoke-tested against the correct revision. A skipped browser test is not a pass. The final report verification record is required before issue.

## 6. Per machine and deviations

Both are kept in the private map. Thirteen deviations were recorded there on 2026-11-27.

## 7. Open questions

- The two comment-layer injectors implement opposite save rules: the canonical one saves beside the page,
  while the desk's older one downloads saves for a filer. Which one is canonical for the hourly desk pages?
  If it is the older one, the exemption has to be recorded in `human-decision-boards.md`.
- Should the wrapper, freshness and status-tile builders behind the hourly pages move under version control
  with their tests? The private map records where they sit now.
