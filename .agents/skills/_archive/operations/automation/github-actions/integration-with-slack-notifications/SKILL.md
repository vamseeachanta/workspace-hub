---
name: github-actions-integration-with-slack-notifications
description: 'Sub-skill of github-actions: Integration with Slack Notifications (+1).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# Integration with Slack Notifications (+1)

## Integration with Slack Notifications


```yaml
# .github/workflows/notify.yml
name: Slack Notifications

on:
  workflow_run:
    workflows: ["CI Pipeline"]
    types: [completed]

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - name: Notify Slack
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "blocks": [
                {
                  "type": "header",
                  "text": {
                    "type": "plain_text",
                    "text": "${{ github.event.workflow_run.conclusion == 'success' && 'Build Succeeded' || 'Build Failed' }}"
                  }
                },
                {
                  "type": "section",
                  "fields": [
                    {
                      "type": "mrkdwn",
                      "text": "*Repository:*\n${{ github.repository }}"
                    },
                    {
                      "type": "mrkdwn",
                      "text": "*Branch:*\n${{ github.event.workflow_run.head_branch }}"
                    },
                    {
                      "type": "mrkdwn",
                      "text": "*Commit:*\n<${{ github.event.workflow_run.head_commit.url }}|${{ github.event.workflow_run.head_sha }}>"
                    },
                    {
                      "type": "mrkdwn",
                      "text": "*Author:*\n${{ github.event.workflow_run.head_commit.author.name }}"
                    }
                  ]
                },
                {
                  "type": "actions",
                  "elements": [
                    {
                      "type": "button",
                      "text": {
                        "type": "plain_text",
                        "text": "View Run"
                      },
                      "url": "${{ github.event.workflow_run.html_url }}"
                    }
                  ]
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
          SLACK_WEBHOOK_TYPE: INCOMING_WEBHOOK
```


## Integration with AWS Deployment


```yaml
# .github/workflows/aws-deploy.yml
name: AWS Deployment

on:
  push:
    branches: [main]

jobs:
  deploy-lambda:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: us-east-1

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install SAM CLI
        run: pip install aws-sam-cli

      - name: Build
        run: sam build

      - name: Deploy
        run: |
          sam deploy \
            --no-confirm-changeset \
            --no-fail-on-empty-changeset \
            --stack-name my-app \
            --capabilities CAPABILITY_IAM \
            --parameter-overrides Environment=production
```
