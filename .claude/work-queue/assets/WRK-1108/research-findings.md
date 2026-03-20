# WRK-1108: WhatsApp MCP Integration Research

**Research date:** 2026-03-10
**Status:** Multiple production-ready options exist — integration IS possible now.

## TL;DR

WhatsApp MCP servers **exist today** and are community-maintained. No official Anthropic or Meta endorsement.
Top recommendation for personal use: **`lharries/whatsapp-mcp`** (5,400+ stars, QR-code setup, Claude Desktop ready).

---

## Top Options

### 1. `lharries/whatsapp-mcp` ★ Best for personal use
- **URL**: https://github.com/lharries/whatsapp-mcp
- **Stars**: 5,400 | Go + Python | Active development
- **Backend**: Unofficial WhatsApp Web API (whatsmeow Go library)
- **Capabilities**: Search contacts/chats, read/send messages, send files, voice messages, media download
- **Setup**: Go + Python + uv + Claude Desktop; QR-code phone link
- **Risk**: Unofficial API — account ban risk for high-volume use; prompt injection warning

### 2. `delltrak/wamcp` ★ Most feature-complete
- **URL**: https://github.com/delltrak/wamcp
- **Stars**: 10 (newer) | TypeScript | Docker-based
- **Backend**: Both Baileys (unofficial) AND Meta Cloud API (official)
- **Capabilities**: 63 tools — messaging, groups, contacts, reactions, edits, presence, stories, calls
- **Setup**: Node.js ≥22 + Redis + `docker compose up`
- **Notable**: Only server supporting both backends with identical interface; most complete API

### 3. `aldinokemal/go-whatsapp-web-multidevice` (GOWA)
- **URL**: https://github.com/aldinokemal/go-whatsapp-web-multidevice
- **Stars**: 3,642 | Go | Mature platform
- **Backend**: Unofficial WhatsApp Web
- **Capabilities**: REST API + MCP + UI + webhooks + Chatwoot; multi-account
- **Setup**: Docker or Go binary; QR-code

### 4. Official Meta Cloud API (business-grade)
- **Server**: `Harikrishnan46624/WHATSAPP-MCP-SERVER` or `delltrak/wamcp` in Cloud API mode
- **Requires**: Meta Business account, verified phone number, Meta approval, pre-approved message templates
- **Benefit**: ToS-compliant; suitable for business use

---

## Decision Framework

| Use case | Recommendation |
|----------|---------------|
| Quick personal test | `lharries/whatsapp-mcp` |
| Full-featured agent | `delltrak/wamcp` |
| REST + MCP together | GOWA (aldinokemal) |
| Business/ToS-compliant | Meta Cloud API mode in `delltrak/wamcp` |

---

## Critical Caveats

1. **Unofficial API risk**: Most servers use reverse-engineered WhatsApp Web. Account bans possible for automated/high-volume use.
2. **Official path**: Requires Meta Business account approval + dedicated phone number.
3. **Prompt injection**: Received message content exposed to LLM — malicious messages could exfiltrate data. Mitigate by sandboxing tool access.
4. **No `modelcontextprotocol/servers` listing**: None are officially endorsed by Anthropic/MCP maintainers.

---

## Conclusion

Integration is available **now** (not in the future). Spinning off WRK-1109 to implement `lharries/whatsapp-mcp` on dev-primary with Claude Desktop.
