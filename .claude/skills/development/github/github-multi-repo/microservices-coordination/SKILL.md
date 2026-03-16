---
name: github-multi-repo-microservices-coordination
description: 'Sub-skill of github-multi-repo: Microservices Coordination (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Microservices Coordination (+2)

## Microservices Coordination


```bash
npx ruv-swarm github microservices \
  --services "auth,users,orders,payments" \
  --ensure-compatibility \
  --sync-contracts \
  --integration-tests
```

## Library Updates


```bash
npx ruv-swarm github lib-update \
  --library "org/shared-lib" \
  --version "2.0.0" \
  --find-consumers \
  --update-imports \
  --run-tests
```

## Organization-Wide Changes


```bash
npx ruv-swarm github org-policy \
  --policy "add-security-headers" \
  --repos "org/*" \
  --validate-compliance \
  --create-reports
```
