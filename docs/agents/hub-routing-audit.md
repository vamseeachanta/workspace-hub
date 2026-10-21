# Sibling contract routing audit

The read-only auditor reports literal routing evidence in each supplied
checkout's AGENTS.md and CLAUDE.md. No instruction file is created or changed.
The report establishes marker coverage for the supplied directories only.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-20 | Add literal routing observations and a fixture example so missing links can be inspected before edits. |
| 1 | 2026-10-21 | Recognize Contract headers with extra fields, preserve prose after fenced examples, decode a leading BOM, and distinguish absent retired files from missing markers. |

## Basis and method

Issue 3958, acceptance criteria, requires that the header carries
`Contract: ../workspace-hub/AGENTS.md`, alone or followed by whitespace and
a `|` field list such as `| Source: src/example/`. The
[template](hub-routing-block.md) supplies this line beneath a generic header;
maintainers will preserve existing repository-specific instructions when applying
it. It is a template, not an installed instruction file.

The hub [AGENTS.md](../../AGENTS.md), Required controls and Execution sections,
defines task authority, review, and the branch → PR → merge path. Issue 3957
explains the git path-to-main requirement inherited through that reference.
No equations, engineering constants, or numerical acceptance limits are used.

For each supplied directory, the tool will report a separate row for each of
AGENTS.md and CLAUDE.md:

- `yes`: an active prose line carries the required Contract token alone or
  followed by whitespace and a `|` field list.
- `partial`: a Contract prefix or hub AGENTS reference occurs, but a matching
  header is absent. Split markers, altered targets, and URL references fall here.
- `no`: neither marker occurs in active prose, or the file cannot be read.

Fenced code, indented code, and HTML comments are excluded. Comment openers
inside fenced code do not affect later prose. A leading UTF-8 BOM is ignored.
Line numbers are one-based physical lines. A `yes` row lists matching lines; a `partial` row
lists candidate evidence. Missing files have no evidence lines. An unreadable
file adds an explicit diagnostic. File-presence and routing observations are
separate; an absent CLAUDE.md has `n/a (file absent)` in the missing-marker
column and does not invalidate a complete AGENTS.md or call for a retired file
to be recreated.

## Invocation

Run from the hub root, supplying only directories authorized for inspection:

```sh
python scripts/agents/audit_agents_routing.py ../sample-one ../sample-two
python scripts/agents/audit_agents_routing.py --repos-json repositories.json
```

The optional JSON input is a nonempty list of nonempty path strings:

```json
["../sample-one", "../sample-two"]
```

JSON paths resolve relative to the JSON file's directory. Positional paths
resolve relative to the current directory. Both forms can be combined; duplicate
resolved paths are reported once. Distinct checkouts with identical basenames
are rejected to avoid ambiguous rows. Existing directories are required, but Git
metadata is not required, allowing disposable fixtures. The tool does not run
Git, load repository code, or execute the instructions it reads.

Output is a Markdown table on standard output. Basenames are displayed instead
of full paths; table delimiters and HTML characters are escaped. Basenames may
still contain private names: reports require review before publication.
Exit zero means the audit ran, including when gaps were found. Invalid arguments
or configuration return exit two. Findings do not authorize edits.

## Worked example

Inputs are created at test runtime beneath a temporary directory:

- `complete/AGENTS.md`: the template's header and exact Contract line.
- `unlinked/AGENTS.md`: `# Local instructions` followed by a newline.
- `partial/AGENTS.md`: `Contract: elsewhere/AGENTS.md` followed by a newline.
- `absent`: an existing directory containing neither instruction file.

No fixture contains CLAUDE.md. The method compares the literal active lines
against the acceptance marker. The complete marker is on physical line 2; the
partial prefix is on physical line 1. Neither other fixture contains a marker.
The expected output is written out below and compared with the tool's output
by `test_documented_fixture_table`.

<!-- fixture-table:start -->
| repository | file present | routes to the hub contract | missing marker(s) | line numbers |
| --- | --- | --- | --- | --- |
| complete | AGENTS.md: yes | yes | none | 2 |
| complete | CLAUDE.md: no | no | n/a (file absent) | none |
| unlinked | AGENTS.md: yes | no | Contract: ../workspace-hub/AGENTS.md | none |
| unlinked | CLAUDE.md: no | no | n/a (file absent) | none |
| partial | AGENTS.md: yes | partial | header carries: Contract: ../workspace-hub/AGENTS.md | 1 |
| partial | CLAUDE.md: no | no | n/a (file absent) | none |
| absent | AGENTS.md: no | no | Contract: ../workspace-hub/AGENTS.md | none |
| absent | CLAUDE.md: no | no | n/a (file absent) | none |
<!-- fixture-table:end -->

Table: Expected literal routing observations for synthetic inputs.

## Limits and follow-up

Literal matching does not establish semantic compliance, runtime loading,
header placement, line-cap compliance, target existence, or freshness of the hub
checkout. Markdown handling is deliberately limited to the constructs described
above; it is not a full Markdown parser. A URL reference may route successfully
in practice but receives `partial` against the exact sibling-path criterion.
Private reports remain private. No live sibling coverage is claimed by the
fixture example.

Issue 3958's comments record a standalone privacy exception and an excluded
retired repository, along with already-completed edits. Maintainers will inspect
current instruction files and those dispositions before applying the template.
The tool will report observed markers without overriding either exception.
Any migration of CLAUDE.md content will preserve repository-specific controls;
this change performs no migration and introduces no CLAUDE.md file.
