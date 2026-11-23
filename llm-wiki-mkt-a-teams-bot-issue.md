# Research options for a Microsoft Teams bot powered by Hermes Agent for Oil & Gas Q&A

## Background
We want to evaluate whether the `llm-wiki-mkt-a` repo ecosystem can expose a Microsoft Teams bot, backed by Hermes Agent, that answers oil and gas domain questions and returns grounded results from the repo ecosystem.

## Goal
Research and propose viable implementation options for a Teams bot that can:
- Accept oil and gas questions from users in Microsoft Teams.
- Route questions through Hermes Agent and/or repo-specific retrieval/query services.
- Search and cite relevant content from the `llm-wiki-mkt-a` repo ecosystem.
- Return concise answers, source references, and follow-up suggestions in Teams.
- Operate within the organization’s Microsoft Teams / Azure / Microsoft Graph governance model.

## Research tasks
1. **Map the repo ecosystem**
   - Identify repos, datasets, docs, indexes, APIs, and existing LLM/RAG components relevant to oil and gas Q&A.
   - Determine what content should be searchable and what access controls apply.

2. **Review Hermes Agent integration options**
   - Evaluate whether to use Hermes Gateway directly, a custom Teams adapter, Microsoft Bot Framework, Graph APIs, or incoming/outgoing webhooks.
   - Determine how Hermes profiles, skills, tools, memory, and retrieval/indexing should be configured for this use case.
   - Identify whether existing Hermes Teams / Microsoft Graph support can be reused or extended.

3. **Research Teams bot architecture options**
   Compare at least these approaches:
   - Microsoft Bot Framework / Azure Bot Service bot connected to Teams.
   - Teams app with bot + messaging extension.
   - Graph webhook or Teams channel integration that forwards messages to Hermes.
   - Simple incoming webhook or workflow-based proof of concept, if suitable.

4. **Review organization Teams / Azure settings**
   - Check whether custom Teams apps are allowed.
   - Check app permission policies, app setup policies, and bot installation policies.
   - Review whether side-loading / org app catalog publishing is available.
   - Identify required Azure app registration settings.
   - Identify needed Microsoft Graph permissions and whether admin consent is required.
   - Determine security/compliance constraints for exposing repo content through Teams.

5. **Permissions and approvals**
   - List all required permissions, likely owners, and approval steps, including:
     - Teams admin permissions or Teams app catalog approval.
     - Azure app registration ownership/admin consent.
     - Microsoft Graph delegated/application permissions.
     - Repository/content access permissions.
     - Hosting/network permissions for webhook or bot endpoints.

6. **Proof-of-concept plan**
   - Propose a minimal POC path.
   - Identify required infrastructure, secrets, deployment target, and rollback plan.
   - Define acceptance criteria and success metrics.

## Deliverables
- Short architecture recommendation with pros/cons for each option.
- Permissions/approval checklist for the organization’s Teams/Azure environment.
- POC implementation plan with estimated effort and risks.
- Open questions that need answers from Teams/Azure/repo owners.

## Acceptance criteria
- At least 2–3 viable architecture options are documented and compared.
- Recommended path is clearly identified, including why it fits this repo ecosystem.
- Teams organization settings and required permissions are reviewed or explicitly listed as needing admin confirmation.
- POC plan includes deployment approach, secrets/configuration, data access model, and validation steps.
- Risks are documented for security, permissions, data leakage, source attribution, and operational ownership.
