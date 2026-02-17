# Texas RRC Data Sources Research

> **Date**: 2026-01-26
> **Status**: Complete

## Available Data Sets

### Production Data (Primary Target)

| Dataset | Format | Frequency | Best For |
|---------|--------|-----------|----------|
| **Production Data Query (PDQ) Dump** | CSV | Monthly (last Saturday) | **PRIMARY** - Most accessible |
| Gas Ledger (Districts 1-10) | EBCDIC | Monthly | Legacy systems |
| Oil Ledger (Districts 1-10) | EBCDIC | Monthly | Legacy systems |
| Statewide Production Oil/Gas | EBCDIC | Monthly | Aggregates |
| P-18 Skim Oil/Condensate | JSON | Monthly | Modern format |

### Well Data

| Dataset | Format | Frequency | Notes |
|---------|--------|-----------|-------|
| **Wellbore Query Data** | ASCII | Monthly | Good for well records |
| Full Wellbore | EBCDIC/ASCII | Weekly | Complete wellbore info |
| Oil Well Database | EBCDIC | Monthly | Oil wells only |
| Gas Well Database | EBCDIC | Monthly | Gas wells only |
| Directional Surveys | PDF | Nightly | Requires PDF parsing |

### Drilling Permits

| Dataset | Format | Frequency | Notes |
|---------|--------|-----------|-------|
| Daily File w/ Coordinates | ASCII | Nightly | Good for tracking |
| Pending Approvals | ASCII | Twice daily | New permits |
| Horizontal Permits | ASCII | Monthly | Horizontal wells |

## Download Portal

**Primary URL**: `https://mft.rrc.texas.gov/` (secure HTTPS downloads)
**Alternative**: `https://webapps2.rrc.texas.gov/EWA/ewaPdqMain.do` (PDQ web interface)

## Data Formats

### API Number Format (Texas)
- State Code: `42` (Texas)
- Format: `42-CCC-WWWWW-SS-DD`
  - CCC = County code (3 digits)
  - WWWWW = Well number (5 digits)
  - SS = Sidetrack (2 digits, optional)
  - DD = Directional (2 digits, optional)
- Example: `42-123-45678-00-00`

### RRC Districts
| District | Area |
|----------|------|
| 01 | San Antonio |
| 02 | Corpus Christi |
| 03 | Houston |
| 04 | Deep South Texas |
| 05 | East Central Texas |
| 06 | East Texas |
| 7B | West Central Texas |
| 7C | San Angelo |
| 8 | Midland |
| 8A | Lubbock |
| 09 | North Texas |
| 10 | Panhandle |

## Implementation Strategy

### Phase 1: CSV Downloads (Recommended Start)
1. **PDQ Dump** - Monthly CSV production data
2. **Wellbore Query Data** - Monthly ASCII well records
3. **Daily Drilling Permits** - ASCII with coordinates

### Phase 2: Web Scraping
1. Directional surveys (PDF extraction)
2. Real-time PDQ queries

### Phase 3: EBCDIC Processing (Optional)
1. Full wellbore data
2. Historical ledgers

## Data Dictionaries

| Dataset | Dictionary |
|---------|-----------|
| PDQ Dump | PDQ Dump Manual (available on RRC site) |
| Wellbore | WBA091, EWA Definition Manual |
| Drilling Permits | OGA049, OGA049M |
| Production | PDA001, LAD001 |

## Existing Tools

- [rrc-scraper](https://github.com/derrickturk/rrc-scraper) - Production data scraper
- [TXRRC_data_harvest](https://github.com/mlbelobraydi/TXRRC_data_harvest) - Well data scripts

## Key Considerations

1. **Rate Limiting**: Be conservative (2-5 req/sec)
2. **File Sizes**: PDQ dumps can be large (100MB+)
3. **Format Conversion**: EBCDIC requires special handling
4. **Authentication**: Most data is public, no auth required
5. **Updates**: Schedule monthly syncs for most datasets

## Contact

- Data questions: Publicassist@rrc.texas.gov
- PDQ questions: ProductionReporting-Info@rrc.texas.gov
