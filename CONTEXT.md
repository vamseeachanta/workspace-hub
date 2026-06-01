# Deckhand

Deckhand is the operator-facing name for Hermes-mediated chatbot control of the
workspace-hub ecosystem: mobile/chat access to AI operations, multi-platform
message fanout, and repository-scoped action authorization. This glossary keeps
the language of that work precise.

## Language

**Scope**:
A named set of repositories plus the permission policy that governs what Deckhand
may do to them (e.g. `ecosystem`, `acma`, `doris`). A scope answers "which repos,
and read/write/delete?" — it says nothing about which messaging platform a reply
goes to.
_Avoid_: Channel (means a transport target here), named channel, repo group

**Channel**:
A single reachable messaging destination on one platform — a Telegram chat, a
Slack `#channel`, a Discord channel, a contact. This is what
`gateway/channel_directory.py` enumerates and resolves.
_Avoid_: Target alone (ambiguous), chat (platform-specific)

**Delivery group**:
A named set of channels that a notification fans out to (defined by #2902). A
delivery group answers "where does this message go?" across one or more platforms.
In Hermes terms it expands to multiple `DeliveryTarget`s / `send_message` targets
(`gateway/delivery.py`); Hermes has no native grouping term — this is Deckhand's.
_Avoid_: Channel, scope, target (Hermes uses "target" for a single destination)

**Fanout**:
Sending one explicit notification to every channel in a delivery group, with
per-target preflight, dedup, and per-target result reporting (Path B in #2900).
_Avoid_: Broadcast, mirror

**Permission level**:
What a scope authorizes against its repos: `read` (clone/inspect) or `write`
(commit/push/PR — including a commit that removes file lines, which is reviewable
in a diff). Independent of, and never implying, destructive operations. This is
*repo/action* permission — independent of Hermes platform access control
(`*_ALLOWED_USERS` / pairing), which governs who may talk to the bot.
_Avoid_: Access, role, grant

**Sensitivity** / **Clearance**:
A scope declares a *sensitivity* (e.g. `acma` = private, `ecosystem` = internal);
a delivery group declares the *clearance* — which sensitivities it may receive.
Output produced under a scope may only fan out to delivery groups cleared for that
scope's sensitivity (the origin chat is always allowed). This is what couples the
otherwise-orthogonal scope and routing concepts, mirroring the wiki
`client → other-client` leakage ban.
_Avoid_: Classification, label (overloaded with GitHub labels here)

**Operator**:
An authenticated human identity that may drive Deckhand — a specific platform
user ID (Telegram user, Teams AAD identity, WhatsApp number) on Hermes' gateway
allowlist. Maps to a Hermes authenticated platform sender/contact, usually
controlled by `*_ALLOWED_USERS` or pairing. Each scope additionally names which
operators may invoke it; an unknown sender, or a known operator not on a scope's
list, is denied before any action.
_Avoid_: User (ambiguous — could mean an end-user of a target repo), sender

**Destructive operation**:
An irreversible action a scope denies separately from write: repo deletion,
branch/tag/release deletion, force-push / history rewrite, and `git reset --hard`
/ `git clean`. This — not a commit that removes file lines — is what "deletion
explicitly disallowed" forbids. Enforced at the git/gh command layer (cf. the
`git-guardrails` skill), never by prompt text alone.
_Avoid_: Delete (too narrow / ambiguous)
