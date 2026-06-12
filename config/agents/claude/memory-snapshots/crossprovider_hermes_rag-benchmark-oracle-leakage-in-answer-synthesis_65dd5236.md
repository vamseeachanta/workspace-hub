---
name: crossprovider hermes rag-benchmark-oracle-leakage-in-answer-synthesis
description: RAG benchmark oracle leakage in answer synthesis
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [benchmark-validity, rag-methodology, oracle-leakage]
---

Answer synthesis that filters contexts to only include gold `required_citations` and extracts facts by iterating gold `required_facts` inflates citation and accuracy metrics. The baseline answer becomes oracle-assisted rather than derived purely from retrieved context, compromising benchmark validity.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
