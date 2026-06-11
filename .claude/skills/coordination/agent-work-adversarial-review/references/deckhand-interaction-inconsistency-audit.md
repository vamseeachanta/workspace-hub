# Deckhand interaction inconsistency audit pattern

Use this reference when an adversarial review covers Deckhand/customer-channel behavior, not just repo commits.

## Review axes

1. **Channel fit**
   - Public/Open Deck: no broad local filesystem inventory, no secrets/path exposure, no internal tool chatter.
   - Client/private channel: client-facing language; avoid software internals unless the channel is explicitly software/admin.
   - Operator/super-admin/software-ops: software, routing, and gateway details are allowed.

2. **Domain scope**
   - Compare observed replies against `config/deckhand/scopes.yml`, channel packs, audience deltas, and `routing/audiences.yaml`.
   - Treat “I can work on anything reachable from this machine” as a defect in constrained client/marketing channels.
   - If a channel says pack-only, refusal must be plain and must not consult outside files.

3. **Result delivery state**
   - Distinguish: `drafted_local`, `artifact_created`, `posted_remote`, `media_delivered`, `client_action_pending`, `blocked_auth`.
   - If GitHub creation or media delivery fails, never summarize as “created/assigned/added/sent.” Say “drafted locally, not posted/delivered,” and include blocker evidence.

4. **Engineering credibility**
   - Look for confident numeric/design claims later walked back after user challenge.
   - For engineering public/client responses, separate resource upper bound from device rating, simulation/visualization from solver-backed analysis, and preliminary assumptions from validated code-standard results.

5. **Live readiness claims**
   - “Config exists,” “gateway restarted,” or “tests passed” is not enough for Deckhand channel behavior.
   - Require a real-channel canary before saying a route/prompt/domain behavior is live and healthy.

6. **Audit/config drift**
   - Check that active scopes are represented consistently in groups/audience docs and that audit rows include required fields such as `scope` and `domain`.
   - Re-run focused routing/group tests when possible; a passing route probe can still miss stale registry maps.

## Common defect phrases

- “Public channel file-disclosure overreach”
- “Delivery-state overclaim: local draft presented as posted/sent”
- “Pack-only channel answered from broad machine scope”
- “Live/readiness claim made before canary proof”
- “Governance metadata says proposed while sessions operate it as live”
- “Client delivery still pending despite internal artifact completion”

## Recommended final report shape

Group findings by severity and class:

1. Highest-severity inconsistencies
2. Claude/session-work inconsistencies
3. Config/routing inconsistencies
4. Pattern-level diagnosis
5. Fix order: P0 safety/trust, P1 routing/config, P2 client-facing quality, P3 governance cleanup

Keep evidence concrete: corpus idx, file path, line range, test command/result, and exact contradictory wording.
