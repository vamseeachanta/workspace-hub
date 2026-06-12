---
name: crossprovider hermes catalog-schema-union-of-10-optional-fields-acros
description: Catalog schema: union of 10+ optional fields across resource types
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [resource-catalog, data-format, schema-pattern]
---

YAML resource catalogs use common required fields (id, name, category, url, cost_model, relevance_score, maturity, discovery_status) + optional fields per entry type: github, huggingface, huggingface_models, paper, data_license, code_license, commercial_use_permitted, attribution_required, citation, pip_install, pip_package, pip_version_tested, python_min, dataset_count, total_size_tb. Tested on 7 catalogs (73+ primary resources, 100+ total URLs). When unifying #1576, preserve optional-field union to avoid data loss.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
