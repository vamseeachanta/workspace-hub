---
name: respond
type: command
plugin: legal
source: https://github.com/anthropics/knowledge-work-plugins
---

# /respond -- Generate Legal Response from Templates

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Generate a customized legal response using pre-configured templates. Supports common inquiry types including data subject requests, discovery holds, vendor questions, NDAs, privacy inquiries, subpoenas, and insurance claims.

**Important**: This command assists with legal workflows but does not provide legal advice. Generated responses should be reviewed by qualified legal professionals before being sent.

## Invocation

```
/respond <inquiry type or description>
```

## Workflow

### Step 1: Identify the Inquiry Type

Determine the type of inquiry from the user's input. Supported categories:
- Data Subject Request (DSR)
- Discovery / Litigation Hold
- Vendor Legal Question
- NDA Request
- Privacy Inquiry
- Subpoena / Legal Process
- Insurance Notification

If the inquiry type is unclear, ask the user to clarify.

### Step 2: Load Templates

Check for configured templates in local settings. If templates exist, use them as the basis for the response. If no templates are configured, use the default structures from the **canned-responses** skill.

### Step 3: Check Escalation Triggers

Before generating a response, evaluate whether the situation warrants individualized attention rather than a templated response. Check for:

**Universal triggers**:
- Potential litigation or regulatory investigation
- Inquiry from a regulator or government agency
- Response could create binding legal commitment
- Potential criminal liability
- Media attention involved
- Unprecedented situation
- Multiple conflicting jurisdictions
- Executive or board involvement

**Category-specific triggers**: Check the relevant triggers from the canned-responses skill.

If an escalation trigger is detected:
1. Alert the user to the trigger
2. Explain why a templated response may be inappropriate
3. Recommend the appropriate escalation path
4. Offer to provide a draft marked "FOR COUNSEL REVIEW ONLY" instead

### Step 4: Gather Details

Collect the information needed to customize the response:
- Requester details (name, organization, contact)
- Specific facts of the inquiry
- Applicable jurisdiction and regulation
- Timeline and deadlines
- Any relevant prior correspondence or context

Pull additional context from connected sources if available:
- **CRM**: Relationship history
- **Email**: Prior correspondence on this topic
- **Support platform**: Related tickets
- **CLM**: Related agreements

### Step 5: Generate the Response

Populate the template with the gathered details:
- Customize all variable fields
- Adjust tone for the audience and situation
- Verify jurisdiction-specific requirements
- Include all legally required elements
- Apply the appropriate signature block

Present the response for review before sending.

### Step 6: Offer Iteration

After generating the response:
- "Want me to adjust the tone? (more formal / more conversational)"
- "Should I add or remove any sections?"
- "Want me to draft a follow-up message for [X days] from now?"
- "Should I create a template from this response for future use?"

## Template Creation

If no template exists for the inquiry type:

1. Inform the user that no template was found
2. Offer to create one based on the current inquiry
3. Walk through the template creation process from the canned-responses skill
4. Save the template for future use

## Notes

- Always present the response as a draft for review, not as a final communication
- Flag any elements that require verification (dates, regulatory citations, specific facts)
- If the response involves regulated communications (DSRs, subpoena responses), emphasize the need for counsel review
- Track which templates are frequently modified to identify improvement opportunities
