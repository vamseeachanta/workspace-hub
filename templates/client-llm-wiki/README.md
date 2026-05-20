# <CLIENT_SHORT_NAME>-llm-wiki

Private <CLIENT_SHORT_NAME> LLM wiki and evidence workspace.

## Purpose

This repo stores curated <CLIENT_SHORT_NAME> knowledge artifacts derived from local/private project sources. It is the private bridge between local raw data and downstream reports/chatbots.

## Canonical local raw-data root

```text
/mnt/ace/<CLIENT_RAW_ROOT>/
```

That raw-data root is intentionally local/private and may contain large client/project files. Do not push raw files here unless explicitly classified and approved for private wiki residency.

## Initial structure

```text
DATA-CYCLE.md                 # Layer contract and promotion gates
sources/README.md             # Source inventory conventions
pages/README.md               # Curated private wiki pages
ledgers/promotion-ledger.example.yml
reports/README.md             # Report and chatbot output provenance
```

## Naming decision

Recommended repo name for the private wiki is `<CLIENT_SHORT_NAME>-llm-wiki`:

- short and client-scoped
- avoids implying only "projects"
- separates private wiki knowledge from local raw project archive
- distinct from public `llm-wiki`
