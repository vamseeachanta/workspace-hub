# Engineering register — handover for other sessions on ace-win-1

Written 2026-09-10. Applies to every session on this machine, any provider.

## What changed on this box today

`workspace-hub` was 121 commits behind and has been fast-forwarded to `e4a796e8f`.
Three rule commits dated 2026-09-10 introduced the engineering register and
regenerated all five provider runtimes:

- `89e7e5e57` one engineering register across every repo and every provider
- `537a745b1` first-person rule applies to every document, enforced as R6
- `1b3532689` raw data as received is committed, with one carve-out

`llm-wiki` was 72 commits behind and has been fast-forwarded; the full house-style
guide is now on disk.

The souls were also deployed. `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md` and
`~/.hermes/SOUL.md` are now symlinks into `D:\ws\workspace-hub\config\agents\`,
created 20260910T214407Z. They load in every cwd.

**A Claude session started after that timestamp loads the register automatically
and needs nothing from this document.** A session started before it does not —
its soul was read at launch, when `~/.claude/CLAUDE.md` did not exist. The prompt
below exists for those sessions, and for any provider whose surface is not yet
linked (`gemini` and `agy` remain undeployed; see the open defect note at the end).

## The prompt

Paste this into a running session:

---

Engineering register now applies to this session. It landed in `workspace-hub`
on 2026-09-10 and governs **all** output: issued reports, wiki pages, commit
messages, chat replies, email, and text written for another agent. Read the
canonical statement before writing anything further:

- Rule: `D:\ws\workspace-hub\.claude\rules\engineering-register.md`
- Agent statement: `D:\ws\workspace-hub\config\agents\SHARED_SOUL.md`, section "Engineering register"
- Full guide, with a quoted exemplar per rule drawn from issued reports:
  `D:\ws\llm-wiki\wikis\engineering\wiki\concepts\engineering-report-house-style.md`
  (sections A–F, a recommended report skeleton, a 15-line house-voice checklist,
  and a list of phrases to avoid)

The governing rules, in short:

- The subject is the analysis, result, component, document or company — not a
  person. "The analysis is performed", not "I performed the analysis". This holds
  for internal working records too: "the survey records", not "we recorded". The
  single exemption is the proposal genre. Enforced as R6.
- Bind every conclusion to its criterion, comparator and governing case. A bare
  verdict is not a conclusion.
- State plainly when something is not established: name the missing evidence, say
  what cannot be calculated, mark the affected result approximate, and condition
  acceptance on obtaining the evidence. A generic disclaimer is not a limitation.
- `should` and `is recommended` carry advice; `shall` and `must` denote
  requirements, not emphasis.
- `-`, `n/a`, `TBD`, `Not Evaluated` and a true zero mean different things.
- Never write `acceptable`, `conservative` or `safe` without the criterion that
  makes it so.
- Tense: report-present passive for method, past for completed events, simple
  present for findings.
- Captions below tables and figures. Units in the header. Three decimals for
  thickness and corrosion allowance.

Three exclusions are deliberate and load-bearing:

- Verbatim third-party transcriptions are not checked — standards, papers and
  source extracts carry their own author's register.
- A list item that is only a quoted phrase is a citation, not a violation; a style
  guide must be able to list the constructions it bans.
- `<!-- register-lint: ignore -->` suppresses a line that must carry an example.

A negated intensifier is a hedge, not an intensifier, and is reported separately
as R5. "Not obviously correct" admits something is unproven, which is what the
register asks for. The remedy for R5 is to supply the criterion, not to delete the
word.

Check any document before issuing it:

    D:\ws\digitalmodel\.venv\Scripts\python.exe D:\ws\workspace-hub\scripts\enforcement\check-engineering-register.py <path>...

---

## Machine-specific notes for whoever runs the checker here

- **Use the digitalmodel interpreter.** `workspace-hub\.venv` is broken on this
  box (`No pyvenv.cfg file`, so `uv run` fails), and bare `python` resolves to the
  Microsoft Store stub. `D:\ws\digitalmodel\.venv\Scripts\python.exe` is 3.12.13
  and runs the checker correctly.
- **`--self-test` fails one of 29 fixtures**: `caption_above` expects at least one
  finding and produces none, so the caption-placement rule does not fire. The
  failure reproduces against an LF extract of the blob from `HEAD`, so it is a
  defect in the script as landed rather than a CRLF artifact of this checkout.
  Per-file linting is unaffected — a real document returned `0 violation(s)` with
  exit 0. Not yet filed.
- **The deployment gate cannot reach zero here.**
  `scripts/enforcement/check-soul-deployment-drift.sh` reports `3 current,
  2 drifted`; the `gemini` and `agy` rows check destinations that
  `scripts/agents/install-soul-runtime.sh` declines to create by design, so the
  gate's own remediation instruction cannot clear them. An issue draft is at
  `<scratchpad>\issue-soul-deployment-gate-installer-mismatch.md`, not yet filed.
- **Do not `git restore` `.codex/skills` or `.gemini/skills`** in any sibling repo.
  Both probe as NTFS junctions into `workspace-hub\.claude\skills`; restoring them
  empties the canonical tree. `skip-worktree` is set on those paths in `llm-wiki`
  as of today, which is what let the pull proceed. Canonical tree count before and
  after: 4,216 files.
