# llm-wiki-<CLIENT_SHORT_NAME>

Private <CLIENT_SHORT_NAME> LLM wiki and evidence workspace.

## Purpose

This repo stores curated <CLIENT_SHORT_NAME> knowledge artifacts derived from local/private project sources. It is the private bridge between local raw data and downstream reports/chatbots.

## Raw-source posture

Raw sources remain outside this repository. Authorized absolute roots are
recorded only in the private registry and may be absent during metadata-only
bootstrap. Do not invent a local path or push raw files into this wiki; add a
source pointer only after the registry explicitly records the root.

## Initial structure

```text
DATA-CYCLE.md                 # Layer contract and promotion gates
sources/README.md             # Source inventory conventions
pages/README.md               # Curated private wiki pages
ledgers/promotion-ledger.example.yml
reports/README.md             # Report and chatbot output provenance
```

## Naming decision

Recommended repo name for the private wiki is `llm-wiki-<CLIENT_SHORT_NAME>` (per [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) D4'-amended convention):

- `llm-wiki-` prefix groups all private client wikis under a single namespace alongside the public `llm-wiki` trunk
- client-scoped suffix keeps each wiki short and identifiable
- avoids implying only "projects"
- separates private wiki knowledge from local raw project archive
- distinct from public `llm-wiki` while making the family relationship obvious at a glance
