# Multi-machine Telegram/Hermes dispatch closeout pattern

Use this when turning a one-control-surface idea into governed multi-machine Hermes/Telegram execution.

## Durable pattern

1. Treat live cross-machine dispatch as a new planning-gated issue unless an approved plan already exists.
2. First collect read-only status from each host:
   - hostname / OS / uptime
   - Hermes installed/version/config source
   - Telegram gateway or bot login state
   - reachable SSH or platform transport
   - available licensed programs and whether license checks are read-only
3. Convert the findings into a readiness matrix before any remote side-effecting action.
4. Keep the initial dispatch contract redacted and low risk:
   - no secrets in prompts, logs, issue bodies, or Telegram messages;
   - host allowlist required;
   - command allowlist starts with status/readiness probes only;
   - all side-effecting runs require explicit approval.
5. Close the initial implementation issue once the control-plane/readiness artifacts land; put live dispatch execution into follow-up issues rather than stretching the original issue.

## Exit handoff lesson

When closing a multi-machine/control-plane session, explicitly record:

- which machines are known vs assumed;
- whether a fifth Telegram-connected host is named or still unknown;
- issue state and landed commit(s);
- exact next planning target;
- external-action status (`No external send/action performed` unless approved);
- preserved dirty-state exceptions from provider dashboards, session logs, and skill reference artifacts.

## Anti-patterns

- Do not treat Telegram login on multiple machines as approval to execute remote commands.
- Do not mix readiness probing, dispatch policy, and live machine execution into one unbounded issue.
- Do not close out by saying the repo is clean if unrelated generated/session artifacts remain; report counts and classes.