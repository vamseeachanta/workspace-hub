# GTM Job Market Scan Strategy

This document outlines the strategy for scanning job boards to identify potential clients and market trends in the offshore engineering sector.

## Job Board Sources

- **Primary:**
    - LinkedIn Jobs
    - Indeed
    - Rigzone
- **Secondary:**
    - Glassdoor
    - Company career pages

## Keywords for Offshore Engineering

- "offshore engineering"
- "subsea engineer"
- "riser analysis"
- "mooring design"
- "SURF"
- "naval architect"
- "OrcaFlex"

## Data Fields to Extract

- Company Name
- Job Title
- Location
- Job Description
- Required Skills/Experience
- Date Posted

## Mapping to ACE Services

- **Riser/Mooring Analysis:** Match with jobs requiring these specific skills.
- **OrcaFlex Expertise:** Target companies seeking OrcaFlex proficiency.
- **General Offshore Engineering:** Identify companies with a need for broad offshore engineering consulting.

## Automation Approach

1. **Web Scraping:** Develop or utilize a web scraping tool to automatically gather job postings from the specified sources.
2. **Data-extraction:** Use NLP to extract the relevant data fields from each job description.
3. **Database Storage:** Store the extracted data in a structured database (e.g., PostgreSQL, a CSV file, or a Google Sheet) for analysis.
4. **Recurring Scans:** Schedule the scraper to run weekly to gather new postings and identify trends.
5. **Reporting:** Create a dashboard or regular report to summarize the findings and highlight potential leads.
