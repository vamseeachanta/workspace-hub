# Landman Data Sources Research

> **Date**: 2026-01-26
> **Status**: Complete
> **Scope**: Free public county records only (no subscriptions)

## Overview

Landman data encompasses mineral ownership, lease records, and title chain information. This module focuses on **free public sources** until commercial subscriptions are acquired.

## Free Data Sources by State

### Federal - Bureau of Land Management (BLM)

| Resource | URL | Data |
|----------|-----|------|
| **MLRS** | https://mlrs.blm.gov/ | Mining claims, fluid minerals, land tenure |
| **GeoCommunicator** | https://www.geocommunicator.gov/ | Federal land records |

### Texas

| Resource | URL | Type | Cost |
|----------|-----|------|------|
| **Texas RRC** | https://www.rrc.texas.gov/ | Well permits, production | Free |
| **Texas GLO** | https://www.glo.texas.gov/ | State land leases (1944-2004) | Free |
| **County Clerks** | Varies by county | Deeds, leases | Free search, paid copies |
| **TexasFile** | https://www.texasfile.com/ | Aggregated records | Paid |

### New Mexico

| Resource | URL | Type |
|----------|-----|------|
| **OCD GIS** | https://www.emnrd.nm.gov/ocd/ | Oil & gas wells, permits |
| **County Tax Assessors** | Varies | Mineral ownership |
| **BLM NM Office** | Santa Fe | Federal mineral records |

### Oklahoma

| Resource | URL | Type |
|----------|-----|------|
| **OCC GIS** | https://oklahoma.gov/occ/ | Oil & gas data |
| **County Clerks** | Varies | Deeds, instruments |

### North Dakota

| Resource | URL | Type |
|----------|-----|------|
| **NDIC GIS** | https://www.dmr.nd.gov/oilgas/ | Wells, permits, production |
| **County Recorders** | Varies | Property records |

### Colorado

| Resource | URL | Type |
|----------|-----|------|
| **COGCC GIS** | https://cogcc.state.co.us/ | Wells, permits, operators |
| **County Recorders** | Varies | Deeds, liens |

## Data Types

### Available Free
- Well locations and permits (via state GIS)
- Production data (via state regulators)
- Operator information
- Field boundaries
- Basic ownership (from county assessors)

### Requires Subscription/Research
- Complete title chains
- Historical conveyances
- Mineral deed abstracts
- Lease terms and royalty rates
- Division orders

## Implementation Strategy

### Provider Abstraction Pattern

```python
class LandmanProvider(Protocol):
    """Base interface for all landman data providers."""

    @property
    def name(self) -> str: ...

    @property
    def coverage(self) -> List[str]: ...  # States covered

    def search_by_location(self, state: str, county: str, section: str) -> List[Record]: ...

    def search_by_owner(self, name: str, state: str = None) -> List[Record]: ...

    def get_record_detail(self, record_id: str) -> RecordDetail: ...
```

### Provider Implementations

1. **BLMProvider** - Federal land records via MLRS
2. **StateGISProvider** - State oil/gas commission GIS APIs
3. **CountyRecordsProvider** - County clerk record references

### Future Providers (Subscription Required)
- `LandmanAIProvider` - https://landman.ai/
- `TaxNetUSAProvider` - https://www.taxnetusa.com/
- `DrillingInfoProvider` - https://www.enverus.com/

## Record Types

### MineralOwnershipRecord
```python
@dataclass
class MineralOwnershipRecord:
    owner_name: str
    state: str
    county: str
    legal_description: str
    mineral_interest: float  # Decimal interest (0.0-1.0)
    source: str  # Provider name
    source_url: Optional[str]
    last_updated: Optional[date]
```

### LeaseRecord
```python
@dataclass
class LeaseRecord:
    lessor: str
    lessee: str
    state: str
    county: str
    legal_description: str
    lease_date: date
    expiration_date: Optional[date]
    royalty_rate: Optional[float]
    bonus_per_acre: Optional[float]
    source: str
```

## Key Considerations

### Legal/Access
- County records are public but may require in-person visits
- Some states charge for electronic access
- API availability varies significantly

### Data Quality
- Free sources may have gaps or delays
- Cross-reference multiple sources when possible
- Older records may not be digitized

### Rate Limiting
- Be respectful of public resources
- Conservative rate limits (1-2 req/sec)
- Cache results aggressively

## Sources

- [BLM MLRS](https://mlrs.blm.gov/)
- [NARO Online Resources](https://www.naro-us.org/Useful-Online-Resources)
- [Pheasant Energy - Mineral Rights Search](https://www.pheasantenergy.com/search-mineral-rights-records/)
