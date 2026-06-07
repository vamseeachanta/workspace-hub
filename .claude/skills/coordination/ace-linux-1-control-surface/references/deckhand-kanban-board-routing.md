# Deckhand Kanban Board Routing

## Trigger
Use when Hermes chatbot / mobile-control / multi-platform bot work appears in a broad AI orchestration or notification board and the user wants the work grouped under the product name.

## Product naming
- Treat **Deckhand** as the product name for the Hermes chatbot/control-surface work.
- Prefer board/card wording like `Deckhand Telegram`, `Deckhand multi-platform fanout`, and `workspace-hub · Deckhand` over generic `Hermes chatbot` once the work is clearly in this product lane.

## Board pattern
Use a dedicated board for Deckhand work instead of leaving related cards split across broad boards:

```text
repo-workspace-hub-deckhand
workspace-hub · Deckhand
```

Typical scope:
- Telegram mobile access and gateway operation.
- Signal / WhatsApp / Microsoft Teams platform parity planning.
- Shared delivery-group and fanout contracts.
- Conversation reply policy guardrails to prevent accidental cross-channel mirroring.
- Operator docs for bot/fanout behavior.

## Safe move protocol
1. Inventory candidate cards from broad boards (`ai-orchestration`, `notification`, or similar) by title/body, not just by board name.
2. Move only active relevant cards into the Deckhand board.
3. Archive or mark superseded originals in source boards so counts stay explainable and duplicate work is not routed twice.
4. Do not move closed/stale/non-Deckhand notification tasks just because they mention Telegram or notifications.
5. Verify destination and source counts after the move.
6. If a board switch command reports success but the active/current board check does not match, avoid relying on ambient board state; pass `--board repo-workspace-hub-deckhand` explicitly for reads/writes until the active board is verified.

## Verification shape
Report:

```text
repo-workspace-hub-deckhand        ready=<n>
repo-workspace-hub-ai-orchestration archived=<n>, blocked=<n>, ready=<n>
repo-workspace-hub-notification    archived=<n>, blocked=<n>
```

Then list the moved card IDs/titles so the operator can see the exact Deckhand queue.
