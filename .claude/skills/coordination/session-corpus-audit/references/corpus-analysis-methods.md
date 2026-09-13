# Corpus analysis methods

These methods consolidate the former workspace-hub/session-corpus-audit workflow.
Use only the phases needed for the audit question. Resolve tools and repo-relative
paths from the explicit owning checkout; normalize display paths using recorded roots,
not one hardcoded machine prefix. Preserve original locators in authorized evidence.

## Sources and format adapters

| Surface | Evidence and handling |
|---|---|
| `.claude/state/session-signals/YYYY-MM-DD.jsonl` | Session/hook summaries; inspect actual fields such as session_id, transcript_path, cwd, permission_mode, hook_event_name and last_assistant_message. A Stop hook alone does not prove a crash. |
| `logs/orchestrator/claude/session_*.jsonl` | Legacy structured events commonly carry ts, hook, tool, repo/project, cmd or file. Filter hook=post for paired event streams; count malformed/skipped rows. |
| `logs/orchestrator/hermes/session_*.jsonl` | Structured events may additionally carry hermes_tool and model. Preserve native-tool identity alongside normalized categories. |
| `logs/orchestrator/codex/` and other provider roots | Inspect schema rather than extension or role. Historical .log files may be timestamped work records or JSON/plain-text reviews; current native streams may contain tool events. Parse each format explicitly. |
| `.claude/state/skill-scores.yaml` | Historical schema nests records under skills with tier/path and usage/reference metrics. Verify producer semantics; tiers hot/warm/cold/dead do not establish actual invocation. |
| `.claude/state/corrections/*.jsonl` | Historical correction events carry timestamp, file, basename, tool, correction_gap_seconds and type. Do not invent a description field or assume all providers collect corrections. |
| Session governor counters | Inspect reset scope and time basis before using them as session/day totals. Volume thresholds are heuristics, not automatic failure or continuation gates. |

Table 1. Source shapes are conditional on observed schema; unavailable roots do not imply no activity.

Record file/session counts, event-time window, capture gaps, duplicates and parser
failures per format. Deduplicate paired records using schema/call identity before
aggregating; never impose the legacy post-hook filter on unrelated native formats.
Review artifacts contribute verdict history, not fictitious read/write activity.

## Reuse existing analysis interfaces

Inspect current CLI help/source and source roots before execution. These commands
write reports when outputs are supplied; use only authorized destinations and avoid
running broad default corpora for a bounded task.

The focused Claude implementation and its tests are:
- `scripts/analysis/claude_session_ecosystem_audit.py`
- `tests/analysis/test_claude_session_ecosystem_audit.py`

Supported arguments are `--repo-root`, `--logs-dir`, `--output-json`, `--output-md`.
For example, from the owning checkout after resolving placeholders:

```bash
uv run python scripts/analysis/claude_session_ecosystem_audit.py \
  --repo-root <owner-root> --logs-dir <authorized-bounded-log-root> \
  --output-json <authorized-output.json> --output-md <authorized-output.md>
```

This script compares historical Claude reads/prompts/commands with current files
and stage evidence. Its defaults scan the owner's Claude orchestrator directory;
it has no date-window flag. Supply a suitably bounded existing corpus or use an
approved filtered view rather than inventing an option.

`scripts/analysis/provider_session_ecosystem_audit.py` supports `--json-output`,
`--markdown-output` and `--stdout`. It uses internal source discovery rather than
CLI log-root/date arguments. Inspect its source boundary before use; `--stdout`
ADDITIONALLY prints output and does not disable either report write. Do not invoke
it merely to check availability or assume it is read-only. A scoped parser may be
needed for a format the existing tools do not support; do not silently broaden access.

## Baseline and prompt drift

Produce relevant tool-call distributions, normalized read/write file frequencies,
command families, event-time trends, repo distribution and within-session module
co-occurrence. Keep provider-specific denominators beside any combined summary.
Normalize command families without discarding effectful subcommands; retain raw
commands only in authorized evidence. Reads and writes measure activity, not quality.
Where captured, report per-session read/write/exec/delegation counts or percentages,
with their denominators and native model field; mark unavailable fields as unknown.

For prompt-focused audits, classify prompt reads as stage prompts, planning/review
templates, plugin prompts or other prompt-like paths. Examine neighboring events
within a declared window (the historical method used about 8–12 records), then bind
stage interpretation to surviving tests, generated-package indexes and current docs.
Do not guess a deleted stage's meaning from its number. Record stages, surviving
prompt paths and associated evidence in both machine/human outputs when relevant.

Classify hot missing paths as replaced, renamed, intentionally ephemeral/minimal,
or historical-only. Confirm current active callers before recommending a redirect.
Prefer fixing misleading active callers over resurrecting removed workflow semantics.
For runtime-command drift, distinguish automation from templates, bootstrap exceptions
and historical fixtures. Do not rewrite preserved evidence to improve old metrics.

## Repeated workflows and skill coverage

As an exploratory method, use sliding windows of 5–15 related tool events; look for
sequences recurring across at least two sessions without observed explicit skill
invocations. Relatedness may use directory prefixes and tool sequence. Deduplicate
overlapping windows, keeping maximal comparable sequences. These parameters are
reported analysis settings, not universal significance thresholds.

Map candidate workflows to skills using names, descriptions, triggers and domain
content. Any ranking weights should be declared and sensitivity checked. A skill
body read is not necessarily invocation; implicit loading is not proven by absent
explicit calls. Separate capture limitations from a discoverability defect.

Compare live skill inventory, score records and domain activity for missing paths,
unscored skills, same-name collisions, exact duplicates and content drift. Include
framework loading mechanisms when known. Inventory actual canonical/provider roots
and declare excluded archive/internal/cache sets. No activity during a window does
not prove a skill is dead; replacement and caller evidence are required for removal.

## Corrections, memory and repository health

Group correction events by owner-relative file/module, extension, tool and time;
compare to available tests and repeated defect evidence. Missing correction capture
on one provider is a coverage gap, not superior quality. A path-derived test location
is only a candidate: inspect actual test collection before reporting absent coverage.

For memory audits, inspect authorized indexed stores, compare repeated facts for
agreement and identify the canonical source. Check current harness limits/references,
conflict markers and linked-file availability across enumerated owner checkouts.
Record machine-local versus tracked state; secrets and identity-bearing memory must
not be copied into public reports. Do not assume old CLAUDE.md/AGENTS.md path layouts
or historical conflict percentages still apply. Git history belongs to each owner.
Do not infer that `.claude/state/` is machine-local: verify tracked and ignored status.
For `workspace-hub:.claude/state/portfolio-signals.yaml`, regression checks should
assert tracked and not ignored against the current owner revision.

For routing intelligence, compare observed capabilities and capture coverage with
`config/agents/routing-config.yaml` and `config/agents/provider-capabilities.yaml`
when present. Read/write ratios and review agreement are descriptive; they do not
justify fixed provider roles or permission. Preserve original review verdicts and
map synonyms explicitly; invalid or unparsed review output is not a passing verdict.

Per-repo ecosystem checks may enumerate current harnesses, skills, hooks, quality
gates, tests and agent support. Scope the repo set from verified workspace ownership.
Treat file presence as configuration evidence only; runtime activation needs a probe.
Cross-repo duplicates require content, provenance and caller checks, not name equality.
Compare each harness-declared `test_command` with actual test discovery in its owning
repo. Flag missing commands or no collected tests; an empty `tests/` directory alone
does not establish a gap when the declared command discovers tests elsewhere.

## Product conversation catch-up

Keep `conversation-rating-provider-catchup.md` as the detailed rubric-preservation
procedure. Load rated examples/categories first; analyze provider sessions for
workflow defects such as delivery overclaims, tool leakage, canary/live order and
channel/scope confusion. Preserve no-reply/capture-gap cases in any authorized next
review packet. Auto-flags remain rating candidates, not final human scores.

## Report and remediation boundary

Cite the corpus window, adapter version/method, evidence locators and current repo
revision. Identify interpretation versus observation and post-fix outcomes separately.
Produce a bounded next-action list; related issue creation, changes, publication or
next-corpus extraction require the task's applicable authority. Audit analysis does
not authorize stash/rebase, merging, bulk deletion or scraping more private sources.
