---
name: communication-testing-communication-skills
description: 'Sub-skill of communication: Testing Communication Skills.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Testing Communication Skills

## Testing Communication Skills


Validate integrations without spamming channels:

```bash
#!/bin/bash
# test_communication.sh

# Test Slack connection
test_slack_auth() {
    response=$(curl -s "https://slack.com/api/auth.test" \
        -H "Authorization: Bearer $SLACK_BOT_TOKEN")

    ok=$(echo "$response" | jq -r '.ok')
    [ "$ok" = "true" ] && echo "PASS: Slack auth" || echo "FAIL: Slack auth - $(echo "$response" | jq -r '.error')"
}

# Test Teams connection
test_teams_auth() {
    response=$(curl -s "https://graph.microsoft.com/v1.0/me" \
        -H "Authorization: Bearer $TEAMS_ACCESS_TOKEN" \
        -o /dev/null -w "%{http_code}")

    [ "$response" = "200" ] && echo "PASS: Teams auth" || echo "FAIL: Teams auth - HTTP $response"
}

# Test Calendly connection

*See sub-skills for full details.*
