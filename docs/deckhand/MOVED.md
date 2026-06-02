# Deckhand moved

Deckhand migrated out of workspace-hub into its own **private** repo on 2026-06-02:
**`vamseeachanta/deckhand`** (engine + operational data + session history).

Why: workspace-hub is public; Deckhand's config references client repos and its dashboard/issues
carried client-referencing info. The private repo de-publicizes it. Issues moved too (this repo's
Deckhand issues #2931/#2936–#2944/#2948 were transferred to `deckhand`).

Client/GTM/strategy stays in `aceengineer-strategy`; client domain data in `llm-wiki-<client>`.
