---
name: teams-api-azure-devops-pipeline-integration
description: 'Sub-skill of teams-api: Azure DevOps Pipeline Integration (+1).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Azure DevOps Pipeline Integration (+1)

## Azure DevOps Pipeline Integration


```yaml
# azure-pipelines.yml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

stages:
  - stage: Build
    jobs:
      - job: BuildJob
        steps:
          - script: echo "Building..."

          - task: PowerShell@2
            displayName: 'Notify Teams - Build Started'
            inputs:
              targetType: 'inline'
              script: |
                $webhook = "$(TEAMS_WEBHOOK_URL)"
                $body = @{
                  "@type" = "MessageCard"
                  "@context" = "http://schema.org/extensions"
                  "themeColor" = "FFCC00"
                  "summary" = "Build Started"
                  "sections" = @(
                    @{
                      "activityTitle" = "Build Started: $(Build.DefinitionName)"
                      "facts" = @(
                        @{ "name" = "Branch"; "value" = "$(Build.SourceBranchName)" }
                        @{ "name" = "Commit"; "value" = "$(Build.SourceVersion)" }
                        @{ "name" = "Build ID"; "value" = "$(Build.BuildId)" }
                      )
                    }
                  )
                } | ConvertTo-Json -Depth 10
                Invoke-RestMethod -Uri $webhook -Method Post -Body $body -ContentType 'application/json'

  - stage: Deploy
    dependsOn: Build
    jobs:
      - deployment: DeployJob
        environment: 'production'
        strategy:
          runOnce:
            deploy:
              steps:
                - script: echo "Deploying..."

                - task: PowerShell@2
                  displayName: 'Notify Teams - Deployment Complete'
                  inputs:
                    targetType: 'inline'
                    script: |
                      $webhook = "$(TEAMS_WEBHOOK_URL)"
                      $body = @{
                        "@type" = "MessageCard"
                        "themeColor" = "00FF00"
                        "summary" = "Deployment Complete"
                        "sections" = @(
                          @{
                            "activityTitle" = "Deployment Complete"
                            "facts" = @(
                              @{ "name" = "Environment"; "value" = "Production" }
                              @{ "name" = "Version"; "value" = "$(Build.BuildNumber)" }
                            )
                            "potentialAction" = @(
                              @{
                                "@type" = "OpenUri"
                                "name" = "View Release"
                                "targets" = @(@{ "os" = "default"; "uri" = "$(System.TeamFoundationCollectionUri)/$(System.TeamProject)/_release?releaseId=$(Release.ReleaseId)" })
                              }
                            )
                          }
                        )
                      } | ConvertTo-Json -Depth 10
                      Invoke-RestMethod -Uri $webhook -Method Post -Body $body -ContentType 'application/json'
```


## FastAPI Bot Endpoint


```python
# main.py
# ABOUTME: FastAPI endpoint for Teams bot
# ABOUTME: Handles bot messages and card actions

from fastapi import FastAPI, Request, Response
from botbuilder.core import TurnContext
from botbuilder.integration.aiohttp import CloudAdapter, ConfigurationBotFrameworkAuthentication
from botbuilder.schema import Activity
from bot import TeamsBot
import os

# Configuration
class DefaultConfig:
    PORT = 3978
    APP_ID = os.environ.get("MICROSOFT_APP_ID", "")
    APP_PASSWORD = os.environ.get("MICROSOFT_APP_PASSWORD", "")

CONFIG = DefaultConfig()

# Create adapter
SETTINGS = ConfigurationBotFrameworkAuthentication(CONFIG)
ADAPTER = CloudAdapter(SETTINGS)

# Create bot
CONVERSATION_REFERENCES = {}
BOT = TeamsBot(CONVERSATION_REFERENCES)

# Error handler
async def on_error(context: TurnContext, error: Exception):
    print(f"Bot error: {error}")
    await context.send_activity("Sorry, an error occurred.")

ADAPTER.on_turn_error = on_error

# FastAPI app
app = FastAPI()

@app.post("/api/messages")
async def messages(request: Request) -> Response:
    """Main bot messaging endpoint"""

    if "application/json" not in request.headers.get("Content-Type", ""):
        return Response(status_code=415)

    body = await request.json()
    activity = Activity().deserialize(body)

    auth_header = request.headers.get("Authorization", "")

    response = await ADAPTER.process_activity(auth_header, activity, BOT.on_turn)

    if response:
        return Response(
            content=response.body,
            status_code=response.status
        )
    return Response(status_code=201)

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=CONFIG.PORT)
```
