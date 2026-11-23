# Conversation-rating provider catch-up pattern

Use when a product/chatbot conversation QA loop already has rated examples and the user asks to review provider sessions (Claude/Codex/Hermes/Gemini) to catch up instead of restarting calibration.

## Trigger

- User asks to review conversations one-by-one and rate them, then says some are already rated.
- User asks to review Claude/provider sessions for work done on a product and find inconsistencies.
- Existing artifacts include `ratings.json`, `ratings2.json`, HTML chat-quality reports, or a conversation-rating harness.

## Procedure

1. **Load the rated baseline first.** Parse existing `ratings*.json` and extract the score categories, weighting, notes, and the lowest/highest examples. Do not invent a new rubric when one already exists.
2. **Scan provider logs by time window.** Split large log corpora into windows (for example: latest 48h, prior week, older weeks) and review in parallel when possible.
3. **Review provider sessions as meta-evidence, not replacement ratings.** Provider logs reveal workflow defects behind chat behavior: delivery-state overclaim, live/canary ordering, routing diagnosis, stale docs, or tool-output leakage. Preserve that distinction in the report.
4. **Extract defect classes that should become rating flags.** Common durable flags from Deckhand review:
   - delivery-state overclaim (`created`, `sent`, `live`, `set up`) without durable proof;
   - internal/tool leakage in client/public channels: paths, bash/python/code blocks, backend errors, skill/memory/self-improvement chatter;
   - canary-before-live drift: code deployed/restarted before route-specific canary passed;
   - channel/scope/domain/delivery-group terminology confusion;
   - blaming user input/routing before reading logs;
   - long wall response where an artifact + short summary should be used;
   - good engineering computation packaged badly for the audience.
5. **Cite exact evidence.** Include log path plus quote/timestamp/line when available. If a subagent reports evidence, either verify locally or label it as subagent-reported.
6. **Return a catch-up delta.** The useful output is not a full transcript mirror; it is: baseline used, sessions scanned, inconsistencies found, new rating flags, and recommended next packet/batch.
7. **Generate the next QA packet when the corpus is available.** After the meta-review, extract the current chat corpus from the product's gateway/state source, filter to the post-fix/post-charter window, and create a machine-readable review queue plus human-readable Markdown/HTML. Carry forward the defect flags as auto-flags, but label them as review candidates rather than final scores.

## Next-packet scaffold pattern

For a Deckhand-style corpus:

1. Run the extractor from a dated report directory and use `set -o pipefail` when piping to `tee`; otherwise a missing interpreter or extractor failure can be masked by `tee` returning success.
2. Preserve both matched replies and no-reply/capture-gap items. Capture gaps are themselves QA evidence when the user is reviewing delivery consistency.
3. Resolve raw chat IDs through routing config (`groups.yml`, `scopes.yml`, or equivalent) before summarizing channel coverage; unknown IDs should remain explicit rather than guessed.
4. Produce at least three artifacts:
   - `review-packet.json` — complete queue with timestamps, channel, user ask, reply, auto-flags, and priority score.
   - `review-packet.md` — top priority items for operator rating.
   - `review-packet.html` — browser-readable packet for fast review.
5. Treat policy-driven raw paths carefully. If a channel policy explicitly instructs the bot to name a deliverable path, auto-flag it as `internal_leakage` or `attachment_path_review`, but write the caveat clearly: human rating must decide whether raw paths are acceptable or should be translated into cleaner attachment/status wording.
6. Update the report index/README after writing artifacts, especially if prior closeout text says all gaps are closed. Replace global closure claims with bounded fixture-run claims when later evidence finds new risks.

## Output shape

```md
## Baseline used
- <ratings path>
- categories/weights
- existing calibration notes

## Provider session coverage
- <log roots>
- <date windows>
- <session count>

## Catch-up findings
### <defect class>
Evidence: `<path>` — "<quote>"
Rating implication: <how to score future conversations>

## New flags for next conversation batch
- <flag>

## Next action
- <create/update QA packet, review next N conversations, or file issue>
```

## Pitfalls

- Do **not** rerate from scratch when the user says early examples are already rated.
- Do **not** treat automated canary/scorer output as sufficient if the channel transcript contains leaked intermediate tool steps; scorer/capture can under-detect the real failure.
- Do **not** equate `configured`, `deployed`, `gateway-loaded`, `canary-pending`, and `canary-passed`.
- Do **not** collapse `scope`, `domain`, `delivery group`, and chat `channel` into one term during analysis.
