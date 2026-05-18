# Data-Layer Mount Taxonomy Sequencing

Use this reference when planning repo-ecosystem data-layer, llm-wiki, RAG, document-intelligence, or architecture-boundary issues.

## Core lesson

Define the data layer first. Execution-layer and report-layer work become clear only after the mount/folder taxonomy is canonical enough for agents to know where to search and what may be published.

## Minimum taxonomy pass

1. Inventory first-level folders under AI-provider-accessible key mounts, typically:
   - `/mnt`
   - `/mnt/local-analysis`
   - `/mnt/ace`
   - symlink aliases such as `/mnt/ace-data`
2. Classify every first-level path as one of:
   - active repo checkout
   - public llm-wiki repo
   - private/client llm-wiki repo
   - worktree/transient checkout
   - raw/source/bulk data
   - raw client/project bucket
   - standards/reference corpus
   - repo overflow / large artifacts
   - external OSS/vendor/tool checkout
   - archive/staging/legacy wiki-like corpus
   - runtime logs
   - cache/trash/system folder
   - alias
   - unclassified with follow-up decision
3. Then inventory second-level folders until search/routing is clear.

## Client-safe public path rules

Public issues/docs may name folder classes and root patterns. Do not publish exact client/project child names without explicit approval.

Allowed public examples:

```text
/mnt/ace/client_projects/<client-or-project>/
/mnt/ace/doris/<client-or-project-or-workstream>/
/mnt/ace/saipem/<client-or-project-or-workstream>/
/mnt/local-analysis/<client>-llm-wiki/
```

Avoid public examples like:

```text
/mnt/ace/client_projects/<actual-client-project-name>/
/mnt/ace/doris/<actual-client-project-name>/
```

## Planning deliverables to request

- Durable first-level mount map.
- Durable second-level canonical search map.
- Machine-readable path contract with layer, visibility, canonical status, search priority, allowed consumers, and redaction rule.
- Checker/tests for unclassified first-level folders and accidental client-name leakage.
- Follow-up transaction issues for any move/rename/delete/symlink changes.

## Gate

Classification is not migration approval. Bulk moves, deletes, renames, symlink changes, or private-to-public promotion require separate transaction-specific plans and user approval.