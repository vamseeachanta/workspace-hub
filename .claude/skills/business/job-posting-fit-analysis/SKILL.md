---
name: job-posting-fit-analysis
description: Scrape specific job posting URLs, extract full details, score fit against practitioner's resume, rank by relevance, and prepare application pipeline. Use when user provides specific job URLs (e.g., from Rigzone, LinkedIn) and wants to know which ones are worth applying to.
tags: [gtm, consulting, job-applications, resume-tailoring, fit-assessment, rigzone]
triggers:
  - user provides job posting URLs for analysis
  - user wants to check if specific jobs match their profile
  - user mentions "apply" to a job
  - user wants tailored resumes for specific openings
---

# Job Posting Fit Analysis

Workflow for analyzing specific job postings against a practitioner's capabilities and preparing applications.

## Steps

### 1. Load the Resume

Resume lives at: `teamresumes/cv/va_resume.md` in workspace-hub.

**PITFALL:** va_resume.md has an unresolved git merge conflict (lines 1/230 contain `<<<<<<< Updated upstream` / `=======` / `>>>>>>> Stashed changes`). Both versions exist in same file. Use the SECOND version (after `=======`) unless told otherwise. The `va_resume_improved.md` is an alternate cleaner version.

Also available:
- `cv/va_resume.docx` — Word format
- `cv/va_resume.pdf` — PDF format
- `cv/va_bio.md` — Professional bio

Extract from the resume:
- Years of experience, PE status
- Key employers (Chevron, BP, ExxonMobil, etc.)
- Tools (OrcaFlex, AQWA, ANSYS, Python, SQL)
- Standards (API, DNV, ASME, BS)
- Domain expertise (subsea, risers, pipelines, mooring, LNG, FEA)
- Location (Houston, TX)

### 2. Fetch Each Posting

For Rigzone URLs, use `web_fetch` on each posting URL directly:
```
https://www.rigzone.com/oil/jobs/postings/{id}_{title}/
```

Extract from each posting:
- Job Title, Company, Location
- Job Type (FT, Contract, Part-time)
- Job ID number
- Responsibilities
- Required Qualifications
- Preferred Qualifications
- Apply URL (Rigzone redirects to real career sites)
- Posting date
- Salary range (if shown)

### 3. Score Fit (1-10 Scale)

Score each posting against the practitioner's profile:

- **Technical overlap:** Does the role require the person's core discipline?
- **Experience match:** Does the reqd years of exp fit (not over/underqualified)?
- **Tool/standard alignment:** Do specific tools or standards mentioned match?
- **Career trajectory:** Does this advance or maintain the practitioner's position?
- **Location fit:** Is the location match or acceptable?
- **Consulting angle:** Could this be done as consulting rather than FTE?

### 4. Check if Still Live

Postings expire quickly. Before investing in application:
- Check the Apply URL on the actual career site
- Common patterns:
  - Chevron: careers.chevron.com/job/{job_id}
  - Occidental: www.oxy.com/careers (Workday-based)
  - Cheniere: careers.cheniere.com
  - Shell: careers.shell.com
  - Wood Group: woodplc.com/careers (redirects)
- Use curl to check HTTP status (200 = live, 404 = expired)

### 5. Create GitHub Issues for Each Target

```bash
gh issue create --repo vamseeachanta/workspace-hub \
  --title "[WRK] Apply to {company} — {job_title} (Fit: {X}/10)" \
  --label "cat:strategy,domain:gtm,cat:business" \
  --body '{structured analysis with tasks, deliverables, apply URL}'
```

### 6. Tailor Resumes (When Applying)

Create company-specific resume variants:
- `teamresumes/cv/tailored/{company_short_name}.md`
- Reorder experience to surface most relevant first
- Adjust executive summary to match posting keywords
- Highlight specific qualifications mentioned in posting
- Keep factual content the same — only reframe emphasis

### 7. Generate Cover Letters / Application Statements

For each live posting, create:
- `docs/strategy/gtm/job-applications/{company}-{date}.md`
- 2-3 paragraphs connecting experience to their specific requirements
- Include specific projects, metrics, and qualifications

## Rigzone-Specific Findings

### URL Pattern
```
https://www.rigzone.com/oil/jobs/postings/{posting_id}_{title_formatted}/
```
Postings are static pages (not JS-rendered), so `curl` or `web_fetch` works directly.

### Posting Lifespan
- Rigzone postings typically expire 30-90 days after posting
- Jan-Feb 2026 postings were confirmed expired by April 2026
- Always verify on the real career site before proceeding

### Apply URL Redirection
Rigzone "Apply Now" buttons redirect to the actual employer's career site. Common platforms:
- Workday (Oxy, many others)
- SAP SuccessFactors
- Custom career portals

### Scanning Pipeline Integration
The existing `scripts/gtm/job-market-scanner.py` handles automated bulk scanning.
This skill is for manual deep-dive analysis of specific postings the user found manually.

## Pitfalls

### Google Search Rate Limiting
Google blocks with CAPTCHA on automated searches. Use DuckDuckGo or direct URL fetching instead when verifying postings.

### Career Site Navigation
Many enterprise career sites (Workday, SAP SF) use complex JS rendering. The curl/HTTP approach only works for checking if a specific URL returns 200/404. For browsing, use browser_navigate + browser_snapshot.

### Resume Merge Conflict
Always check va_resume.md for merge conflict markers before using it for applications. Both versions contain nearly identical facts but different summary framing.

### Expert Networks vs. Job Posts
When user asks about "paid ad-hoc work," expert networks (GLG, AlphaSights, Guidepoint) should be recommended BEFORE job applications. They offer:
- Zero application hassle (just sign up)
- $150-$1000/hr for 1-hour phone calls
- Non-exclusive — sign up for all 3
- Perfect match for deep domain expertise (PE, 23yr specialist)