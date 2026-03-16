---
name: compliance-required-elements-gdpr-article-28
description: 'Sub-skill of compliance: Required Elements (GDPR Article 28) (+4).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Required Elements (GDPR Article 28) (+4)

## Required Elements (GDPR Article 28)


- [ ] **Subject matter and duration**: Clearly defined scope and term of processing
- [ ] **Nature and purpose**: Specific description of what processing will occur and why
- [ ] **Type of personal data**: Categories of personal data being processed
- [ ] **Categories of data subjects**: Whose personal data is being processed
- [ ] **Controller obligations and rights**: Controller's instructions and oversight rights


## Processor Obligations


- [ ] **Process only on documented instructions**: Processor commits to process only per controller's instructions (with exception for legal requirements)
- [ ] **Confidentiality**: Personnel authorized to process have committed to confidentiality
- [ ] **Security measures**: Appropriate technical and organizational measures described (Article 32 reference)
- [ ] **Sub-processor requirements**:
  - [ ] Written authorization requirement (general or specific)
  - [ ] If general authorization: notification of changes with opportunity to object
  - [ ] Sub-processors bound by same obligations via written agreement
  - [ ] Processor remains liable for sub-processor performance
- [ ] **Data subject rights assistance**: Processor will assist controller in responding to data subject requests
- [ ] **Security and breach assistance**: Processor will assist with security obligations, breach notification, DPIAs, and prior consultation
- [ ] **Deletion or return**: On termination, delete or return all personal data (at controller's choice) and delete existing copies unless legal retention required
- [ ] **Audit rights**: Controller has right to conduct audits and inspections (or accept third-party audit reports)
- [ ] **Breach notification**: Processor will notify controller of personal data breaches without undue delay (ideally within 24-48 hours; must enable controller to meet 72-hour regulatory deadline)


## International Transfers


- [ ] **Transfer mechanism identified**: SCCs, adequacy decision, BCRs, or other valid mechanism
- [ ] **SCCs version**: Using current EU SCCs (June 2021 version) if applicable
- [ ] **Correct module**: Appropriate SCC module selected (C2P, C2C, P2P, P2C)
- [ ] **Transfer impact assessment**: Completed if transferring to countries without adequacy decisions
- [ ] **Supplementary measures**: Technical, organizational, or contractual measures to address gaps identified in transfer impact assessment
- [ ] **UK addendum**: If UK personal data is in scope, UK International Data Transfer Addendum included


## Practical Considerations


- [ ] **Liability**: DPA liability provisions align with (or don't conflict with) the main services agreement
- [ ] **Termination alignment**: DPA term aligns with the services agreement
- [ ] **Data locations**: Processing locations specified and acceptable
- [ ] **Security standards**: Specific security standards or certifications required (SOC 2, ISO 27001, etc.)
- [ ] **Insurance**: Adequate insurance coverage for data processing activities


## Common DPA Issues


| Issue | Risk | Standard Position |
|---|---|---|
| Blanket sub-processor authorization without notification | Loss of control over processing chain | Require notification with right to object |
| Breach notification timeline > 72 hours | May prevent timely regulatory notification | Require notification within 24-48 hours |
| No audit rights (or audit rights only via third-party reports) | Cannot verify compliance | Accept SOC 2 Type II + right to audit upon cause |
| Data deletion timeline not specified | Data retained indefinitely | Require deletion within 30-90 days of termination |
| No data processing locations specified | Data could be processed anywhere | Require disclosure of processing locations |
| Outdated SCCs | Invalid transfer mechanism | Require current EU SCCs (2021 version) |
