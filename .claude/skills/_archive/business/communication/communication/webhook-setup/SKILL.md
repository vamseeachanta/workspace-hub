---
name: communication-webhook-setup
description: 'Sub-skill of communication: Webhook Setup (+3).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Webhook Setup (+3)

## Webhook Setup


```bash
# Common webhook receiver pattern
#!/bin/bash

start_webhook_server() {
    local port="${1:-8080}"

    while true; do
        echo -e "HTTP/1.1 200 OK\n\n" | nc -l -p "$port" | while read line; do
            # Parse webhook payload

*See sub-skills for full details.*

## OAuth2 Authentication


```bash
# OAuth2 token exchange
get_access_token() {
    local client_id="$1"
    local client_secret="$2"
    local code="$3"

    curl -s -X POST "https://oauth.example.com/token" \
        -d "client_id=$client_id" \
        -d "client_secret=$client_secret" \

*See sub-skills for full details.*

## Rate Limiting


```bash
# Tier-based rate limiting
TIER1_LIMIT=1      # 1 request per second
TIER2_LIMIT=20     # 20 requests per minute
TIER3_LIMIT=50     # 50 requests per minute

rate_limited_request() {
    local tier="$1"
    shift


*See sub-skills for full details.*

## Error Response Handling


```bash
handle_api_response() {
    local response="$1"
    local status=$(echo "$response" | jq -r '.ok // .status // "unknown"')

    case "$status" in
        "true"|"200")
            echo "$response" | jq '.data // .'
            return 0
            ;;

*See sub-skills for full details.*
