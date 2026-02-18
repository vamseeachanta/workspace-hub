---
title: "WRK-121: Licensed Software Usage Workflow & Burden Reduction"
description: "Document OrcaFlex license access workflow (TightVNC, credentials, availability) and review all licensed software (ANSYS, OrcaFlex) for usage optimization and maintenance cost reduction"
version: 0.1.0
module: admin/license-management
session:
  id: 2026-02-11-license-workflow
  agent: claude-opus-4.6
review: pending
work_item: WRK-121
target_repos: [acma-projects, assetutilities]
complexity: medium
route: B
---

# WRK-121: Licensed Software Usage Workflow & Burden Reduction

## Context

ACMA uses licensed engineering software (OrcaFlex, ANSYS) on shared workstations accessed via remote desktop (TightVNC). Current documentation is scattered across two repos and has critical gaps:

- `acma-projects/admin/orcaflex/use_instructions.md` -- Only contains a troubleshooting email exchange, not actual usage instructions
- `acma-projects/admin/orcaflex_license.md` -- Historical note about obtaining the license, not operational
- `acma-projects/admin/acma_vpn.md` -- Contains PLAINTEXT PASSWORDS (security risk, must fix)
- `assetutilities/docs/sub_hardware/server_remote_desktop.md` -- Shared vs simultaneous login diagram, needs consolidation
- `assetutilities/docs/sub_hardware/remote_desktop.md` -- Q&A about resource sharing, unanswered questions

Engineers currently lack a single, clear document answering: "How do I get OrcaFlex running and start an analysis?"

## Output Requirement

ALL deliverables must be **standalone, ASCII-friendly documents** suitable for printing or emailing to management/IT:
- Plain text tables (no mermaid, no HTML)
- No dependency on linked repo files — each document is self-contained
- Printable markdown (ASCII art for diagrams if needed)
- Ready to hand to a manager or IT department as-is

## Plan

### Step 1: Create work item WRK-121

Create `pending/WRK-121.md` in the work queue.

### Step 2: OrcaFlex License Usage Guide (standalone)

**File**: `acma-projects/admin/orcaflex/use_instructions.md` (overhaul existing)

Self-contained document covering:

```
ORCAFLEX LICENSE USAGE GUIDE
=============================

1. LICENSE OVERVIEW
   - Single-seat OrcaFlex license (includes OrcaWave)
   - License is tied to machine, not user
   - Only one user can run OrcaFlex at a time

2. HOW TO CONNECT (TightVNC)
   - Download TightVNC Viewer from: <URL>
   - Server address: <MACHINE_NAME>:<PORT>
   - Credentials: Contact IT / see password manager
   - Why TightVNC: Free, lightweight, works over VPN

3. CHECKING LICENSE AVAILABILITY
   - Before connecting: ping the machine / check with team
   - If license is in use: you'll see error "License in use by..."
   - Slack/Teams channel for coordination: <CHANNEL>

4. USAGE ETIQUETTE
   - Close OrcaFlex when not actively using it
   - Do not leave open overnight or over weekends
   - If stepping away >1 hour, close the application
   - Do not hoard the license "just in case"

5. TROUBLESHOOTING
   +---------------------------+--------------------------------+
   | Problem                   | Solution                       |
   +---------------------------+--------------------------------+
   | "License in use"          | Check who has it open, ask     |
   |                           | them to close if not using     |
   | Connection refused        | Check VPN, machine may be off  |
   | Version mismatch          | Contact IT for update          |
   +---------------------------+--------------------------------+
```

### Step 3: Fix credential security (BLOCKING)

**File**: `acma-projects/admin/acma_vpn.md`

- REMOVE all plaintext passwords immediately
- Replace with: "Credentials stored in company password manager. Contact IT for access."
- This is a security violation — must be fixed before any other deliverable

### Step 4: Update remote desktop documentation (standalone)

**File**: `assetutilities/docs/sub_hardware/server_remote_desktop.md`

Replace mermaid diagram with ASCII-friendly table:

```
REMOTE ACCESS: SHARED vs SIMULTANEOUS LOGIN
=============================================

+---------------------+--------------------+------------------------+
| Aspect              | Common Login       | Simultaneous Login     |
|                     | (TightVNC)         | (Windows Server)       |
+---------------------+--------------------+------------------------+
| Users at once       | 1 (shared account) | 2+ (separate accounts) |
| OS required         | Windows 11 ok      | Windows Server 2022    |
| Resources per user  | Full               | Split (halved for 2)   |
| Licenses needed     | 1                  | 1 per user             |
| Confidentiality     | None (shared view) | Per-user desktop       |
| Software examples   | TightVNC (free)    | RDP built-in           |
| Cost                | Free               | Server license cost    |
+---------------------+--------------------+------------------------+

RECOMMENDATION: Common login via TightVNC for single-license software
(OrcaFlex). Simultaneous login for multi-license software (ANSYS).
```

Answer open questions from `remote_desktop.md`:
- Q: Can multiple users run OrcaFlex simultaneously? A: Only with additional licenses
- Q: Does simultaneous login slow runs? A: Yes, CPU/RAM split per user
- Q: Is it using 1 or 2 licenses? A: 1 per running instance, regardless of login method

### Step 5: Licensed Software Audit & Recommendations (standalone)

**File**: `acma-projects/admin/licensed_software_review.md` (new)

Self-contained document for management:

```
LICENSED SOFTWARE REVIEW & RECOMMENDATIONS
============================================
Date: 2026-02-11
Prepared for: ACMA Management / IT Department

1. SOFTWARE INVENTORY
   +-------------+------------------+----------+------------------+
   | Software    | Products         | License  | Annual Maint.    |
   |             |                  | Type     | (est.)           |
   +-------------+------------------+----------+------------------+
   | OrcaFlex    | OrcaFlex,        | Single   | [TO BE FILLED]   |
   |             | OrcaWave         | seat     |                  |
   | ANSYS       | Mechanical,      | Named/   | [TO BE FILLED]   |
   |             | AQWA, etc.       | Concurrent|                 |
   +-------------+------------------+----------+------------------+

2. CURRENT ACCESS METHOD
   - OrcaFlex: TightVNC to dedicated workstation (ACMA-ANSYS machine)
   - ANSYS: Direct login or RDP to licensed machines

3. KNOWN ISSUES
   - License contention (only 1 OrcaFlex seat)
   - Plaintext credentials in documentation (being fixed)
   - No usage scheduling or coordination tool
   - Users sometimes leave software open, blocking others

4. RECOMMENDATIONS
   a) Short-term (0-3 months):
      - Fix credential storage (password manager, not plaintext)
      - Establish license checkout/coordination channel (Slack/Teams)
      - Document usage etiquette and circulate to all users
      - Audit who actually uses each product and how often

   b) Medium-term (3-6 months):
      - Evaluate cloud/elastic licensing (ANSYS Cloud, Orcina tokens)
      - Consider batch/scripted analysis to reduce license hold time
      - Review whether all ANSYS products are actively used
      - Drop unused modules to reduce maintenance costs

   c) Long-term (6-12 months):
      - Evaluate additional OrcaFlex seat if contention persists
      - Consider license server (FlexLM) for better tracking
      - Automated usage reporting for license optimization

5. WAY FORWARD
   +----+----------------------------------------+----------+--------+
   | #  | Action                                 | Owner    | By     |
   +----+----------------------------------------+----------+--------+
   | 1  | Remove plaintext passwords from docs   | IT/Eng   | ASAP   |
   | 2  | Distribute OrcaFlex usage guide        | Eng Lead | 1 week |
   | 3  | Set up license coordination channel    | IT       | 1 week |
   | 4  | Audit ANSYS product usage              | Eng Lead | 1 month|
   | 5  | Evaluate cloud licensing options        | IT/Mgmt  | 3 month|
   | 6  | Review annual maintenance vs. usage    | Mgmt     | 6 month|
   +----+----------------------------------------+----------+--------+
```

### Step 6: Cross-reference (inline, not linked)

Each document includes a "Related Documents" section at the bottom listing the other docs by file path, but each stands alone — no document requires another to be useful.

## Files to Modify

```
+----------------------------------------------+----------+----------------+
| File                                         | Action   | Repo           |
+----------------------------------------------+----------+----------------+
| .claude/work-queue/pending/WRK-121.md        | Create   | workspace-hub  |
| admin/orcaflex/use_instructions.md           | Overhaul | acma-projects  |
| admin/acma_vpn.md                            | SECURITY | acma-projects  |
|                                              | FIX      |                |
| admin/licensed_software_review.md            | Create   | acma-projects  |
| docs/sub_hardware/server_remote_desktop.md   | Update   | assetutilities |
+----------------------------------------------+----------+----------------+
```

### Step 7: Generate PDF copies

For each standalone document, generate a PDF copy in the same directory:
- `acma-projects/admin/orcaflex/use_instructions.pdf`
- `acma-projects/admin/licensed_software_review.pdf`

Method: Use `pandoc` (markdown to PDF) or Python `markdown` + `weasyprint` if pandoc unavailable. ASCII tables render cleanly in monospace PDF output.

```
pandoc use_instructions.md -o use_instructions.pdf
pandoc licensed_software_review.md -o licensed_software_review.pdf
```

If pandoc is not installed, fall back to Python:
```python
# pip install markdown weasyprint
import markdown, weasyprint
html = markdown.markdown(open("file.md").read(), extensions=["tables"])
weasyprint.HTML(string=f"<pre style='font-family:monospace'>{html}</pre>").write_pdf("file.pdf")
```

## Verification

- [ ] No plaintext passwords remain in any committed file
- [ ] Each document is standalone — can be printed/emailed without context
- [ ] All tables use ASCII formatting (no mermaid, no HTML)
- [ ] `use_instructions.md` answers "how do I run OrcaFlex remotely?" end-to-end
- [ ] `licensed_software_review.md` covers OrcaFlex + ANSYS with actionable recommendations
- [ ] Way-forward table has owners and timelines for management review
- [ ] PDF copies generated for key documents (use_instructions, licensed_software_review)
- [ ] PDFs render cleanly with ASCII tables in monospace font
- [ ] Work item WRK-121 created in queue with correct frontmatter
