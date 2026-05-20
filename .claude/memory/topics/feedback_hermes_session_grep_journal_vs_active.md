> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-20
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_hermes_session_grep_journal_vs_active.md

---
name: feedback-hermes-session-grep-journal-vs-active
description: "Hermes session/goal grep matches historical chat transcripts; discriminator is session_id overlap with running pgrep'd workers, not file existence"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: cc26971a-8770-49db-81b9-ae41eb299110
---

When the [[mnt-analysis-cleanup]] skill §6 check runs
`grep -R --fixed-strings "<path>" ~/.hermes/goals ~/.hermes/sessions`, hits in
`.json` files do NOT mean the path is in active use. Hermes stores conversation
transcripts as session JSONs — any path the user mentioned in chat becomes a
match, even months later.

**Discriminator that matters:** does the file's `session_id` appear in the live
running-process list?

```bash
# Currently-running Hermes session keys:
RUNNING=$(pgrep -af tui_gateway.slash_worker | grep -oP -- '--session-key \K[0-9_a-f]+' | sort -u)

# For each grep'd file, extract its session_id and compare:
for f in $(grep -lR --fixed-strings "<path>" ~/.hermes/sessions); do
  sid=$(python3 -c "import json;print(json.load(open('$f')).get('session_id',''))")
  if grep -qxF "$sid" <(echo "$RUNNING"); then
    echo "ACTIVE: $f"; else echo "historical: $f"; fi
done
```

**Why:** on 2026-05-19, 1 goal + 4 sessions grep-matched `llm-wiki/` paths;
all 4 sessions had `last_updated` ≥10 hours stale and zero session_id overlap
with the two live `tui_gateway.slash_worker --session-key ...` processes. The
references were chat-history journal entries from past work. A literal reading
of the skill (any grep hit → Tier 3 defer) would have indefinitely deferred a
safe deletion.

**How to apply:** Add the session-id-overlap discriminator to the cleanup
skill's §6 protocol when invoking it; treat bare grep hits as Tier 2 (defer
pending discriminator), not Tier 3 (block).

Related: [[project_hermes_installation]], cleanup skill at
`.claude/skills/operations/mnt-analysis-cleanup/SKILL.md`.
