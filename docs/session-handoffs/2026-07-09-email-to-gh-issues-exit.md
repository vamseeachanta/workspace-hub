# Email-to-GitHub issue intake exit handoff

Date: 2026-07-09
Repo: `workspace-hub`
Branch: `main`

## Active task

Review an email and create GitHub issues for all live projects it affects.

## Completed in this session

- Loaded the Outlook and GitHub operating instructions.
- Loaded `config/agents/codex/MEMORY.runtime.md` and current `workspace-hub` repo instructions.
- Checked local live repo context under `C:/ws`.
- Verified `workspace-hub` was clean and synced before handoff creation:
  - `git status --short --branch` -> `## main...origin/main`
  - `git rev-list --left-right --count HEAD...origin/main` -> `0 0`
- Verified GitHub CLI auth is available for `vamseeachanta`.
- Discovered GitHub issue tools in this Codex session.
- Attempted Outlook tool discovery; no Outlook message tools were exposed in this Codex session.
- Searched for local email exports under `Downloads`, `Desktop`, `Documents`, and `C:/ws`.
  - Only unrelated local email artifact found: `C:/Users/vamseea/Desktop/OrcaFlex/license_instructions/OrcaFlex Licence Installation (Floating Licence).msg` from 2024-10-22.
- Checked recent session handoffs for active conflicts. No active issue-creation wave for this email-intake task was found.

## What did not happen

- No Outlook mailbox messages were read.
- No GitHub issues were created.
- No labels, comments, or issue state were changed.
- No implementation work started.

## Blocker

The email content is not accessible in this Codex session. Tool discovery exposed GitHub tools but no Outlook `list_messages`, `search_messages`, or `fetch_message` tools. Creating issues without the source email would risk duplicates, wrong repo routing, and weak evidence.

## Current live-project reference points

Use the memory slice and recent issue state before creating anything new:

- `config/agents/codex/MEMORY.runtime.md` contains the current live-project index.
- Local clean/synced repos observed under `C:/ws`:
  - `aceengineer-admin`
  - `assetutilities`
  - `deckhand`
  - `deckhand-licensed-runs-queue`
  - `digitalmodel`
  - `llm-wiki`
  - `llm-wiki-acma`
  - `raw-to-knowledge-playbook`
  - `workspace-hub`
  - `worldenergydata`
  - `worldenergydata-wiki`
- Recent issue scans were run for:
  - `vamseeachanta/workspace-hub`
  - `vamseeachanta/digitalmodel`

## Exact next checkpoint

1. Get the source email into the session:
   - paste the email body, or
   - provide a saved `.eml`/`.msg` path, or
   - run the task from a session where Outlook MCP tools are exposed.
2. Extract tasks by project with owner, due date, evidence, and ambiguity.
3. Map each task to the correct GitHub repo using `docs/REPO_MISSION_PORTFOLIO.md`, local repo origins, and the live-project memory slice.
4. Search existing open issues in each target repo before creating new issues.
5. Create only non-duplicate issues, with email-derived evidence and `status:needs-plan` unless the issue is explicitly a parking-lot or tracking-only item.

## Suggested skills

- `outlook-email`
- `outlook-email-task-extraction`
- `github`
- `coordination/pre-completion-cleanup-audit`
