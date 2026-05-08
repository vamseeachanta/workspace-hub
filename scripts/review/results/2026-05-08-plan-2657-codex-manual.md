## Verdict
UNAVAILABLE (Codex unavailable after documented workaround)

## Retrieval
- Ran `scripts/install/pin-codex.sh`; verified `codex-cli 0.123.0`.
- Retried Codex review manually using the same inline plan prompt and explicit Hermes stdin close pattern.
- Codex started with `OpenAI Codex v0.123.0` but the configured Hermes model rejected the older CLI.

## Findings
(none — invocation failed before Codex returned a usable review)

## Blockers
(none — this provider contributed no plan-review signal)

## Raw failure excerpt
```text
ERROR: {"type":"error","status":400,"error":{"type":"invalid_request_error","message":"The 'gpt-5.5' model requires a newer version of Codex. Please upgrade to the latest app or CLI and try again."}}
```
