---
name: n8n-integration-with-github-and-jira
description: 'Sub-skill of n8n: Integration with GitHub and Jira.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# Integration with GitHub and Jira

## Integration with GitHub and Jira


```json
{
  "name": "GitHub to Jira Sync",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "github-webhook",
        "options": {}
      },
      "id": "github-webhook",
      "name": "GitHub Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1.1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.action }}",
              "operation": "equals",
              "value2": "opened"
            }
          ]
        }
      },
      "id": "filter-opened",
      "name": "Is New Issue?",
      "type": "n8n-nodes-base.filter",
      "typeVersion": 2,
      "position": [460, 300]
    },
    {
      "parameters": {
        "jsCode": "// Map GitHub issue to Jira format\nconst issue = $input.item.json.issue;\n\n// Map labels to Jira priority\nconst labels = issue.labels.map(l => l.name);\nlet priority = 'Medium';\nif (labels.includes('critical') || labels.includes('urgent')) {\n  priority = 'Highest';\n} else if (labels.includes('high')) {\n  priority = 'High';\n} else if (labels.includes('low')) {\n  priority = 'Low';\n}\n\n// Map to Jira issue type\nlet issueType = 'Task';\nif (labels.includes('bug')) {\n  issueType = 'Bug';\n} else if (labels.includes('feature')) {\n  issueType = 'Story';\n}\n\nreturn {\n  summary: `[GitHub] ${issue.title}`,\n  description: `${issue.body}\\n\\n---\\nGitHub Issue: ${issue.html_url}\\nCreated by: ${issue.user.login}`,\n  priority: priority,\n  issueType: issueType,\n  labels: labels.filter(l => !['bug', 'feature', 'critical', 'urgent', 'high', 'low'].includes(l)),\n  github_issue_number: issue.number,\n  github_repo: $input.item.json.repository.full_name\n};"
      },
      "id": "map-to-jira",
      "name": "Map to Jira Format",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [680, 300]
    },
    {
      "parameters": {
        "resource": "issue",
        "operation": "create",
        "project": "={{ $env.JIRA_PROJECT_KEY }}",
        "issueType": "={{ $json.issueType }}",
        "summary": "={{ $json.summary }}",
        "additionalFields": {
          "description": "={{ $json.description }}",
          "priority": "={{ $json.priority }}",
          "labels": "={{ $json.labels }}"
        }
      },
      "id": "create-jira",
      "name": "Create Jira Issue",
      "type": "n8n-nodes-base.jira",
      "typeVersion": 1,
      "position": [900, 300],
      "credentials": {
        "jiraSoftwareCloudApi": {
          "id": "7",
          "name": "Jira"
        }
      }
    },
    {
      "parameters": {
        "owner": "={{ $('Map to Jira Format').item.json.github_repo.split('/')[0] }}",
        "repository": "={{ $('Map to Jira Format').item.json.github_repo.split('/')[1] }}",
        "issueNumber": "={{ $('Map to Jira Format').item.json.github_issue_number }}",
        "body": "=Jira issue created: {{ $json.key }}\n\nLink: {{ $env.JIRA_BASE_URL }}/browse/{{ $json.key }}"
      },
      "id": "comment-github",
      "name": "Comment on GitHub",
      "type": "n8n-nodes-base.github",
      "typeVersion": 1,
      "position": [1120, 300],
      "credentials": {
        "githubApi": {
          "id": "8",
          "name": "GitHub"
        }
      }
    }
  ],
  "connections": {
    "GitHub Webhook": {
      "main": [
        [{ "node": "Is New Issue?", "type": "main", "index": 0 }]
      ]
    },
    "Is New Issue?": {
      "main": [
        [{ "node": "Map to Jira Format", "type": "main", "index": 0 }]
      ]
    },
    "Map to Jira Format": {
      "main": [
        [{ "node": "Create Jira Issue", "type": "main", "index": 0 }]
      ]
    },
    "Create Jira Issue": {
      "main": [
        [{ "node": "Comment on GitHub", "type": "main", "index": 0 }]
      ]
    }
  }
}
```
