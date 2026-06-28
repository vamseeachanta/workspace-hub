# Incident-to-issue evidence research

Use this when the user references a problem from a chat/channel and asks what GitHub issue captured it, what happened, and what evidence/research is already on the issue.

## Workflow

1. **Separate observed incident from nearby GitHub work.** A chat incident may be about delivery/runtime behavior while the closest GitHub issue may be about a related asset or workflow. Do not collapse them unless evidence links them.
2. **Search session history first when the incident happened in chat.** Use exact phrases from the user's recollection and likely variants: channel name, bot handle, artifact type, failure symptom, and generated artifact filenames if visible.
3. **Search GitHub issues second.** Start with exact phrases from the incident (`"PDF attachment"`, `"HTML attachment"`, `"nothing came thru"`, artifact basename), then broaden to workflow/asset terms. Include open and closed issues.
4. **Read the candidate issue body and comments.** The useful evidence is often in comments: review rounds, plan decisions, verification outputs, live URLs, hashes, commits, and closeout notes.
5. **Report with a hard distinction:**
   - `Observed channel incident`: what happened in chat, with session evidence.
   - `GitHub issue evidence`: issue URL/title/state, body evidence, comments/research, artifacts, commits, validation.
   - `Gap`: whether a direct incident-tracking issue exists or whether only adjacent work exists.
6. **Do not claim a GitHub issue documents the incident unless the issue body or comments explicitly connect to the incident.** If only adjacent issues exist, say so and recommend filing a follow-up.

## Useful evidence fields to extract

- Issue URL, number, title, state, labels.
- Body `Evidence` or `Acceptance` sections.
- Comments containing adversarial review summaries, implementation closeout, deployed URLs, content types, file sizes, SHA256 hashes, commits, and test results.
- Session-search quotes showing user-visible failure symptoms.

## Pitfalls

- **Asset workflow ≠ messaging delivery bug.** A PDF/HTML generation issue can be complete while Telegram media delivery still fails for that file type.
- **Search result proximity is not proof.** The top GitHub result may be an umbrella issue or a related GTM asset issue, not the incident ticket.
- **Avoid over-generalizing transient API limits or auth state.** If public GitHub API search is rate-limited, continue with available browser/session evidence or authenticated tooling when available; do not encode the rate limit as a durable tool limitation.
