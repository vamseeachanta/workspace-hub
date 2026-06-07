# Multi-Channel Hermes Chatbot Kanban Board

## Trigger

Use this note when planning or organizing Hermes chatbot work that spans more than the current Telegram bot surface, especially Telegram + Signal + WhatsApp + Microsoft Teams.

## Durable pattern

- Treat the chatbot as a product/workstream, not as a generic notification feature.
- Create or use a dedicated Kanban board for multi-channel chatbot work instead of burying cards in broad orchestration or notification boards.
- Keep the board channel-neutral at the top level, then split cards by adapter/channel only where the implementation or verification differs.
- Include all target channels explicitly in board/plan language: Telegram, Signal, WhatsApp, and Microsoft Teams.

## Board shape used successfully

```text
Board id: repo-workspace-hub-hermes-chatbot
Display:  workspace-hub · Hermes chatbot
Purpose:  Dedicated board for Hermes chatbot multi-platform interaction work:
          Telegram, Signal, WhatsApp, and Microsoft Teams.
```

Recommended dashboard metadata:

```text
icon: 💬
color: #14b8a6
default_workdir: /mnt/local-analysis/workspace-hub
```

## Verification checklist

After creating or refactoring boards, verify before reporting success:

1. The new board appears in `hermes kanban boards` / board list output.
2. The board metadata resolves to the intended workspace/workdir.
3. The board database exists under `~/.hermes/kanban/boards/<board-id>/kanban.db`.
4. Initial task counts are known and reported, even if all zero.
5. Existing related boards are inventoried so the user can decide whether to migrate, clone, or leave cards in place.

## Migration decision point

Do not silently migrate cards when the user only asked to add a dedicated board. Report the new board and ask/recommend the next explicit action:

- migrate relevant cards from broad boards,
- clone seed cards into the chatbot board, or
- keep it empty as a fresh execution board.

## Channel readiness fields to include in future cards

For each non-Telegram adapter, capture readiness separately:

- adapter/setup availability,
- auth/session/linking flow,
- recipient or group identifier model,
- session persistence/recovery,
- redaction coverage for channel identifiers and session artifacts,
- outbound send verification,
- inbound message webhook/polling verification,
- simultaneous fan-out semantics and failure isolation.

## Direct answer pattern for fan-out questions

When the user asks whether Hermes can emit to Telegram, WhatsApp, and Teams simultaneously, answer in three layers:

1. **Yes in architecture/orchestration:** Hermes can run one task and deliver the resulting message to multiple destinations if the gateway has multiple delivery targets configured.
2. **Only currently true for configured channels:** if Telegram is the only working bot today, then simultaneous Telegram + WhatsApp + Teams delivery is not operational yet. WhatsApp and Teams each need their own authenticated bot/connector, recipient/group identifiers, and send verification.
3. **Design decision still required:** decide whether fan-out means one broadcast copy to all channels, per-channel mirrored bot conversations, or event-specific routing. Keep failure isolation explicit so a WhatsApp/Teams failure does not block Telegram delivery.

Recommended concise user-facing shape:

```text
Yes, Hermes can be designed to fan out to multiple bots, but right now only Telegram is verified. To make Telegram + WhatsApp + Teams simultaneous, wire each platform as a gateway/tool delivery target, verify outbound send and inbound handling per channel, then add a fan-out route that targets all three with per-channel failure reporting.
```

## Pitfall

Do not answer “can Hermes send to all bots simultaneously?” as only a model/runtime question. Separate:

1. Hermes orchestration capability — can schedule/dispatch a task and target deliveries if connectors exist.
2. Gateway/tooling capability — each platform needs an installed, authenticated adapter/bot bridge.
3. Product routing semantics — decide whether one response fans out to all channels, mirrors only selected events, or keeps per-channel conversation state isolated.
4. Verified-current-state wording — explicitly distinguish “Telegram works now” from “WhatsApp/Teams are wired and tested.”
