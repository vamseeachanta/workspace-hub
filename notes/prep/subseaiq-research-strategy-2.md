# SubseaIQ Data Acquisition Strategy

This document outlines a strategy for acquiring data from SubseaIQ, a key source of market intelligence for subsea field developments. Direct web scraping was not possible in this session, so this report details the public data landscape and a recommended approach for future extraction.

## Public Data Landscape

Based on prior knowledge and a simulated review of public sources, SubseaIQ's public-facing presence is limited. The most valuable data is behind a paywall.

*   **Publicly Available Data:**
    *   **High-level project announcements:** News articles and press releases often mention major project awards. This data is unstructured and sporadic.
    *   **Corporate presentations:** Operator and service company presentations may provide high-level data on key projects.
    *   **"Projects" section of the SubseaIQ website:** This offers a teaser of the full database, often with a project name, operator, and location, but with key details (water depth, contract values, vessel names) redacted or missing.

*   **Data Requiring Subscription:**
    *   Detailed project-level data: water depth, number of wells, pipeline and umbilical lengths, SURF contract values, vessel charters, technology selections.
    *   Historical data and trend analysis.
    *   Forecasts for future activity.

## Recommended Extraction Approach

A multi-pronged approach is recommended:

1.  **Manual, targeted extraction from public sources:** Continuously monitor industry news and press releases. This is labor-intensive but can yield high-level insights into major projects.

2.  **Web Scraping of the SubseaIQ Public Site:** A scraper could be developed to systematically pull the limited public data from the "Projects" section of the SubseaIQ website. This would provide a structured, though incomplete, dataset.

3.  **Direct Database Access (Subscription):** This is the most effective method. A subscription would provide direct access to the full, structured database, eliminating the need for scraping and providing much richer data. The feasibility of this would depend on budget.

4.  **API Access:** Investigate if SubseaIQ offers a data API. This would be the most efficient way to integrate their data into our systems.

## Next Steps

*   **Decision on subscription:** The key decision is whether the budget exists for a full SubseaIQ subscription. This would fundamentally change the data acquisition strategy.
*   **Develop a targeted scraper:** If a subscription is not pursued, a small-scale scraping project should be initiated to capture the public data. This would at least provide a baseline dataset.
