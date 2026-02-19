---
name: bsee-data-extractor
<<<<<<< HEAD
description: Extract and process BSEE (Bureau of Safety and Environmental Enforcement) data including production, WAR (Well Activity Reports), and APD (Application for Permit to Drill) data. Use for querying production data, well activities, drilling permits, completions, and workovers by API number, block, lease, or field with automatic data normalization and caching.
=======
description: Extract and process BSEE (Bureau of Safety and Environmental Enforcement) production data. Use for querying oil/gas production data by API number, block, lease, or field with automatic data normalization and caching.
>>>>>>> origin/main
capabilities: []
requires: []
see_also: []
---

# BSEE Data Extractor

Extract and process production data from BSEE (Bureau of Safety and Environmental Enforcement) databases for oil & gas analysis in the Gulf of Mexico.

## When to Use

- Querying BSEE production data by API number, block, or lease
- Downloading and parsing BSEE ZIP file archives
- Normalizing production data across different time periods
- Building production timelines for specific wells or fields
- Tracking well status changes over time
- Preparing data for economic analysis (NPV, decline curves)
<<<<<<< HEAD
- Analyzing Well Activity Reports (WAR) for drilling and completion history
- Tracking drilling operations, workovers, and sidetracks
- Reviewing APD (Application for Permit to Drill) records
- Calculating drilling and completion durations
- Building drilling timelines for rig scheduling analysis
=======
>>>>>>> origin/main

## Core Pattern

```
Query Parameters → BSEE API/Files → Parse → Normalize → Cache → Output
```

<<<<<<< HEAD
### Data Types Supported

| Data Type | Source | Size | Update Frequency |
|-----------|--------|------|------------------|
| Production | ProductionRawData.zip | ~15-50 MB | Monthly |
| WAR | eWellWARRawData.zip | ~120+ MB | Weekly |
| APD | APDRawData.zip | ~5-10 MB | Weekly |

=======
>>>>>>> origin/main
## Implementation

### Data Models

```python
from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List, Dict, Any
from enum import Enum
import pandas as pd

class ProductType(Enum):
    """Production fluid types."""
    OIL = "oil"
    GAS = "gas"
    WATER = "water"
    CONDENSATE = "condensate"

class WellStatus(Enum):
    """Well operational status."""
    PRODUCING = "producing"
    SHUT_IN = "shut_in"
    TEMPORARILY_ABANDONED = "ta"
    PERMANENTLY_ABANDONED = "pa"
    DRILLING = "drilling"
    COMPLETING = "completing"

@dataclass
class WellIdentifier:
    """Unique well identification."""
    api_number: str
    well_name: Optional[str] = None
    lease_number: Optional[str] = None
    area_code: Optional[str] = None
    block_number: Optional[str] = None

    @property
    def api_10(self) -> str:
        """Return 10-digit API number."""
        return self.api_number[:10] if len(self.api_number) >= 10 else self.api_number

    @property
    def api_14(self) -> str:
        """Return full 14-digit API number."""
        return self.api_number.ljust(14, '0')

@dataclass
class ProductionRecord:
    """Single month production record."""
    well_id: WellIdentifier
    production_date: date
    oil_bbls: float = 0.0
    gas_mcf: float = 0.0
    water_bbls: float = 0.0
    condensate_bbls: float = 0.0
    days_on_production: int = 0
    status: WellStatus = WellStatus.PRODUCING

    @property
    def oil_bopd(self) -> float:
        """Oil production in barrels per day."""
        if self.days_on_production > 0:
            return self.oil_bbls / self.days_on_production
        return 0.0

    @property
    def gas_mcfd(self) -> float:
        """Gas production in MCF per day."""
        if self.days_on_production > 0:
            return self.gas_mcf / self.days_on_production
        return 0.0

    @property
    def boe(self) -> float:
        """Barrels of oil equivalent (6:1 gas conversion)."""
        return self.oil_bbls + self.condensate_bbls + (self.gas_mcf / 6.0)

@dataclass
class WellProduction:
    """Complete production history for a well."""
    well_id: WellIdentifier
    records: List[ProductionRecord] = field(default_factory=list)
    first_production: Optional[date] = None
    last_production: Optional[date] = None

    def to_dataframe(self) -> pd.DataFrame:
<<<<<<< HEAD


class ActivityType(Enum):
    """Well activity types from WAR data."""
    DRILLING = "drilling"
    COMPLETION = "completion"
    WORKOVER = "workover"
    SIDETRACK = "sidetrack"
    PLUG_ABANDON = "plug_abandon"
    TEMPORARY_ABANDON = "temporary_abandon"
    RECOMPLETION = "recompletion"
    STIMULATION = "stimulation"
    LOGGING = "logging"
    TESTING = "testing"

class APDStatus(Enum):
    """APD application status."""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"

@dataclass
class WARRecord:
    """Well Activity Report record."""
    well_id: WellIdentifier
    activity_type: ActivityType
    start_date: date
    end_date: Optional[date] = None
    spud_date: Optional[date] = None
    rig_name: Optional[str] = None
    water_depth_ft: Optional[float] = None
    total_depth_md: Optional[float] = None
    total_depth_tvd: Optional[float] = None
    target_formation: Optional[str] = None
    operator_name: Optional[str] = None
    status: Optional[str] = None
    remarks: Optional[str] = None

    @property
    def duration_days(self) -> Optional[int]:
        """Calculate activity duration in days."""
        if self.end_date and self.start_date:
            return (self.end_date - self.start_date).days
        return None

@dataclass
class APDRecord:
    """Application for Permit to Drill record."""
    well_id: WellIdentifier
    application_date: date
    approval_date: Optional[date] = None
    status: APDStatus = APDStatus.PENDING
    permit_number: Optional[str] = None
    proposed_spud_date: Optional[date] = None
    proposed_total_depth: Optional[float] = None
    well_type: Optional[str] = None  # exploration, development, injection
    operator_name: Optional[str] = None
    surface_location: Optional[str] = None
    bottom_hole_location: Optional[str] = None

@dataclass
class WellActivity:
    """Complete activity history for a well."""
    well_id: WellIdentifier
    war_records: List[WARRecord] = field(default_factory=list)
    apd_records: List[APDRecord] = field(default_factory=list)
    first_activity: Optional[date] = None
    last_activity: Optional[date] = None

    def to_war_dataframe(self) -> pd.DataFrame:
        """Convert WAR records to DataFrame."""
        data = []
        for rec in self.war_records:
            data.append({
                'api_number': rec.well_id.api_number,
                'activity_type': rec.activity_type.value,
                'start_date': rec.start_date,
                'end_date': rec.end_date,
                'duration_days': rec.duration_days,
                'spud_date': rec.spud_date,
                'rig_name': rec.rig_name,
                'water_depth_ft': rec.water_depth_ft,
                'total_depth_md': rec.total_depth_md,
                'total_depth_tvd': rec.total_depth_tvd,
                'target_formation': rec.target_formation,
                'operator_name': rec.operator_name,
                'status': rec.status
            })
        return pd.DataFrame(data).sort_values('start_date') if data else pd.DataFrame()

    def to_apd_dataframe(self) -> pd.DataFrame:
        """Convert APD records to DataFrame."""
        data = []
        for rec in self.apd_records:
            data.append({
                'api_number': rec.well_id.api_number,
                'application_date': rec.application_date,
                'approval_date': rec.approval_date,
                'status': rec.status.value,
                'permit_number': rec.permit_number,
                'proposed_spud_date': rec.proposed_spud_date,
                'proposed_total_depth': rec.proposed_total_depth,
                'well_type': rec.well_type,
                'operator_name': rec.operator_name
            })
        return pd.DataFrame(data).sort_values('application_date') if data else pd.DataFrame()

    @property
    def total_drilling_days(self) -> int:
        """Total days spent drilling."""
        return sum(r.duration_days or 0 for r in self.war_records
                   if r.activity_type == ActivityType.DRILLING)

    @property
    def total_completion_days(self) -> int:
        """Total days spent on completions."""
        return sum(r.duration_days or 0 for r in self.war_records
                   if r.activity_type == ActivityType.COMPLETION)
```

### WAR/APD Data Models (continued)

```python
    def to_dataframe(self) -> pd.DataFrame:
=======
>>>>>>> origin/main
        """Convert production records to DataFrame."""
        data = []
        for rec in self.records:
            data.append({
                'date': rec.production_date,
                'oil_bbls': rec.oil_bbls,
                'gas_mcf': rec.gas_mcf,
                'water_bbls': rec.water_bbls,
                'condensate_bbls': rec.condensate_bbls,
                'days': rec.days_on_production,
                'oil_bopd': rec.oil_bopd,
                'gas_mcfd': rec.gas_mcfd,
                'boe': rec.boe,
                'status': rec.status.value
            })
        return pd.DataFrame(data).sort_values('date')

    @property
    def cumulative_oil(self) -> float:
        """Total cumulative oil production."""
        return sum(r.oil_bbls for r in self.records)

    @property
    def cumulative_gas(self) -> float:
        """Total cumulative gas production."""
        return sum(r.gas_mcf for r in self.records)

    @property
    def cumulative_boe(self) -> float:
        """Total cumulative BOE."""
        return sum(r.boe for r in self.records)
```

### BSEE Data Client

```python
import requests
import zipfile
import io
from pathlib import Path
from typing import Optional, List, Dict, Generator
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class BSEEDataClient:
    """
    Client for accessing BSEE production data.

    Supports both API access and file-based data extraction.
    """

    # BSEE data URLs
    BASE_URL = "https://www.data.bsee.gov"
    PRODUCTION_URL = f"{BASE_URL}/Production/Files"

    # Column mappings for BSEE data files
    PRODUCTION_COLUMNS = {
        'API_WELL_NUMBER': 'api_number',
        'PRODUCTION_DATE': 'production_date',
        'OIL': 'oil_bbls',
        'GAS': 'gas_mcf',
        'WATER': 'water_bbls',
        'CONDENSATE': 'condensate_bbls',
        'DAYS_ON_PROD': 'days_on_production',
        'WELL_STAT_CD': 'status_code'
    }

<<<<<<< HEAD
    # WAR (Well Activity Report) column mappings
    WAR_COLUMNS = {
        'API_WELL_NUMBER': 'api_number',
        'ACTIVITY_TYPE': 'activity_type',
        'START_DATE': 'start_date',
        'END_DATE': 'end_date',
        'SPUD_DATE': 'spud_date',
        'RIG_NAME': 'rig_name',
        'WATER_DEPTH': 'water_depth_ft',
        'TOTAL_DEPTH_MD': 'total_depth_md',
        'TOTAL_DEPTH_TVD': 'total_depth_tvd',
        'TARGET_FORMATION': 'target_formation',
        'OPERATOR_NAME': 'operator_name',
        'STATUS': 'status'
    }

    # APD (Application for Permit to Drill) column mappings
    APD_COLUMNS = {
        'API_WELL_NUMBER': 'api_number',
        'APPLICATION_DATE': 'application_date',
        'APPROVAL_DATE': 'approval_date',
        'STATUS': 'status',
        'PERMIT_NUMBER': 'permit_number',
        'PROPOSED_SPUD_DATE': 'proposed_spud_date',
        'PROPOSED_TD': 'proposed_total_depth',
        'WELL_TYPE': 'well_type',
        'OPERATOR_NAME': 'operator_name',
        'SURFACE_LOCATION': 'surface_location',
        'BHL_LOCATION': 'bottom_hole_location'
    }

    # Data URLs
    WAR_URL = f"{BASE_URL}/Well/Files/eWellWARRawData.zip"
    APD_URL = f"{BASE_URL}/Well/Files/APDRawData.zip"

=======
>>>>>>> origin/main
    def __init__(self, cache_dir: Path = None):
        """
        Initialize BSEE data client.

        Args:
            cache_dir: Directory for caching downloaded data
        """
        self.cache_dir = cache_dir or Path("data/bsee_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()

    def download_production_file(self, year: int, month: int = None) -> Path:
        """
        Download BSEE production data file.

        Args:
            year: Production year
            month: Optional month (downloads full year if not specified)

        Returns:
            Path to downloaded file
        """
        if month:
            filename = f"ogoramon{year}{month:02d}.zip"
        else:
            filename = f"ogoramon{year}.zip"

        cache_path = self.cache_dir / filename

        if cache_path.exists():
            logger.info(f"Using cached file: {cache_path}")
            return cache_path

        url = f"{self.PRODUCTION_URL}/{filename}"
        logger.info(f"Downloading: {url}")

        response = self.session.get(url)
        response.raise_for_status()

        cache_path.write_bytes(response.content)
        logger.info(f"Saved to: {cache_path}")

        return cache_path

    def extract_production_data(self, zip_path: Path) -> pd.DataFrame:
        """
        Extract production data from BSEE ZIP file.

        Args:
            zip_path: Path to ZIP file

        Returns:
            DataFrame with production records
        """
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Find the data file (usually .txt or .csv)
            data_files = [f for f in zf.namelist()
                         if f.endswith(('.txt', '.csv', '.dat'))]

            if not data_files:
                raise ValueError(f"No data file found in {zip_path}")

            with zf.open(data_files[0]) as f:
                # Try different delimiters
                try:
                    df = pd.read_csv(f, delimiter='\t', low_memory=False)
                except:
                    f.seek(0)
                    df = pd.read_csv(f, delimiter=',', low_memory=False)

        # Rename columns to standard names
        df = df.rename(columns={
            k: v for k, v in self.PRODUCTION_COLUMNS.items()
            if k in df.columns
        })

        return df

    def query_by_api(self, api_number: str,
                     start_year: int = None,
                     end_year: int = None) -> WellProduction:
        """
        Query production data for specific API number.

        Args:
            api_number: Well API number (10 or 14 digit)
            start_year: Start year for query
            end_year: End year for query

        Returns:
            WellProduction object with complete history
        """
        from datetime import datetime

        end_year = end_year or datetime.now().year
        start_year = start_year or (end_year - 20)  # Default 20 years

        well_id = WellIdentifier(api_number=api_number)
        records = []

        for year in range(start_year, end_year + 1):
            try:
                zip_path = self.download_production_file(year)
                df = self.extract_production_data(zip_path)

                # Filter for API number (match on first 10 digits)
                api_10 = well_id.api_10
                df_well = df[df['api_number'].astype(str).str[:10] == api_10]

                for _, row in df_well.iterrows():
                    records.append(self._row_to_record(row, well_id))

            except Exception as e:
                logger.warning(f"Error processing year {year}: {e}")
                continue

        production = WellProduction(well_id=well_id, records=records)

        if records:
            dates = [r.production_date for r in records]
            production.first_production = min(dates)
            production.last_production = max(dates)

        return production

    def query_by_block(self, area_code: str, block_number: str,
                       year: int) -> List[WellProduction]:
        """
        Query all wells in a specific OCS block.

        Args:
            area_code: OCS area code (e.g., 'GC', 'WR', 'MC')
            block_number: Block number
            year: Year to query

        Returns:
            List of WellProduction objects
        """
        zip_path = self.download_production_file(year)
        df = self.extract_production_data(zip_path)

        # Filter by area and block (column names may vary)
        area_col = next((c for c in df.columns if 'AREA' in c.upper()), None)
        block_col = next((c for c in df.columns if 'BLOCK' in c.upper()), None)

        if area_col and block_col:
            df_block = df[
                (df[area_col].astype(str).str.upper() == area_code.upper()) &
                (df[block_col].astype(str) == str(block_number))
            ]
        else:
            logger.warning("Could not find area/block columns")
            return []

        # Group by API number
        wells = {}
        for _, row in df_block.iterrows():
            api = str(row.get('api_number', ''))
            if api not in wells:
                well_id = WellIdentifier(
                    api_number=api,
                    area_code=area_code,
                    block_number=block_number
                )
                wells[api] = WellProduction(well_id=well_id, records=[])

            wells[api].records.append(self._row_to_record(row, wells[api].well_id))

        return list(wells.values())

    def _row_to_record(self, row: pd.Series, well_id: WellIdentifier) -> ProductionRecord:
        """Convert DataFrame row to ProductionRecord."""
        prod_date = row.get('production_date')
        if isinstance(prod_date, str):
            # Parse various date formats
            for fmt in ['%Y%m', '%Y-%m', '%Y/%m', '%Y%m%d', '%Y-%m-%d']:
                try:
                    prod_date = pd.to_datetime(prod_date, format=fmt).date()
                    break
                except:
                    continue
        elif hasattr(prod_date, 'date'):
            prod_date = prod_date.date()
        else:
            prod_date = date.today()

        return ProductionRecord(
            well_id=well_id,
            production_date=prod_date,
            oil_bbls=float(row.get('oil_bbls', 0) or 0),
            gas_mcf=float(row.get('gas_mcf', 0) or 0),
            water_bbls=float(row.get('water_bbls', 0) or 0),
            condensate_bbls=float(row.get('condensate_bbls', 0) or 0),
            days_on_production=int(row.get('days_on_production', 0) or 0),
            status=self._parse_status(row.get('status_code', ''))
        )

    def _parse_status(self, code: str) -> WellStatus:
        """Parse BSEE status code to WellStatus enum."""
        code = str(code).upper().strip()
        status_map = {
            'P': WellStatus.PRODUCING,
            'SI': WellStatus.SHUT_IN,
            'TA': WellStatus.TEMPORARILY_ABANDONED,
            'PA': WellStatus.PERMANENTLY_ABANDONED,
            'DR': WellStatus.DRILLING,
            'CO': WellStatus.COMPLETING
        }
        return status_map.get(code, WellStatus.PRODUCING)
<<<<<<< HEAD

    # ==================== WAR Data Methods ====================

    def download_war_file(self, use_cache: bool = True) -> Path:
        """
        Download BSEE Well Activity Report (WAR) data file.

        Args:
            use_cache: Use cached file if available

        Returns:
            Path to downloaded ZIP file
        """
        cache_path = self.cache_dir / "eWellWARRawData.zip"

        if use_cache and cache_path.exists():
            logger.info(f"Using cached WAR file: {cache_path}")
            return cache_path

        logger.info(f"Downloading WAR data from: {self.WAR_URL}")
        response = self.session.get(self.WAR_URL, timeout=2400)  # 40 min timeout
        response.raise_for_status()

        cache_path.write_bytes(response.content)
        logger.info(f"Saved WAR data: {len(response.content) / (1024*1024):.1f} MB")

        return cache_path

    def extract_war_data(self, zip_path: Path) -> pd.DataFrame:
        """
        Extract WAR data from BSEE ZIP file.

        Args:
            zip_path: Path to WAR ZIP file

        Returns:
            DataFrame with WAR records
        """
        with zipfile.ZipFile(zip_path, 'r') as zf:
            data_files = [f for f in zf.namelist()
                         if f.endswith(('.txt', '.csv', '.dat'))]

            if not data_files:
                raise ValueError(f"No data file found in {zip_path}")

            with zf.open(data_files[0]) as f:
                try:
                    df = pd.read_csv(f, delimiter='\t', low_memory=False)
                except:
                    f.seek(0)
                    df = pd.read_csv(f, delimiter=',', low_memory=False)

        # Rename columns
        df = df.rename(columns={
            k: v for k, v in self.WAR_COLUMNS.items()
            if k in df.columns
        })

        return df

    def query_war_by_api(self, api_number: str) -> WellActivity:
        """
        Query WAR data for specific API number.

        Args:
            api_number: Well API number (10 or 14 digit)

        Returns:
            WellActivity object with WAR records
        """
        zip_path = self.download_war_file()
        df = self.extract_war_data(zip_path)

        well_id = WellIdentifier(api_number=api_number)
        api_10 = well_id.api_10

        df_well = df[df['api_number'].astype(str).str[:10] == api_10]

        war_records = []
        for _, row in df_well.iterrows():
            war_records.append(self._row_to_war_record(row, well_id))

        activity = WellActivity(well_id=well_id, war_records=war_records)

        if war_records:
            dates = [r.start_date for r in war_records if r.start_date]
            if dates:
                activity.first_activity = min(dates)
                activity.last_activity = max(dates)

        return activity

    def query_war_by_block(self, area_code: str, block_number: str) -> List[WellActivity]:
        """
        Query WAR data for all wells in a block.

        Args:
            area_code: OCS area code (e.g., 'GC', 'WR', 'MC')
            block_number: Block number

        Returns:
            List of WellActivity objects
        """
        zip_path = self.download_war_file()
        df = self.extract_war_data(zip_path)

        area_col = next((c for c in df.columns if 'AREA' in c.upper()), None)
        block_col = next((c for c in df.columns if 'BLOCK' in c.upper()), None)

        if area_col and block_col:
            df_block = df[
                (df[area_col].astype(str).str.upper() == area_code.upper()) &
                (df[block_col].astype(str) == str(block_number))
            ]
        else:
            logger.warning("Could not find area/block columns in WAR data")
            return []

        wells = {}
        for _, row in df_block.iterrows():
            api = str(row.get('api_number', ''))
            if api not in wells:
                well_id = WellIdentifier(
                    api_number=api,
                    area_code=area_code,
                    block_number=block_number
                )
                wells[api] = WellActivity(well_id=well_id)

            wells[api].war_records.append(self._row_to_war_record(row, wells[api].well_id))

        return list(wells.values())

    def _row_to_war_record(self, row: pd.Series, well_id: WellIdentifier) -> WARRecord:
        """Convert DataFrame row to WARRecord."""
        def parse_date(val):
            if pd.isna(val):
                return None
            if isinstance(val, str):
                for fmt in ['%Y-%m-%d', '%Y%m%d', '%m/%d/%Y']:
                    try:
                        return pd.to_datetime(val, format=fmt).date()
                    except:
                        continue
            elif hasattr(val, 'date'):
                return val.date()
            return None

        activity_map = {
            'DRILL': ActivityType.DRILLING,
            'COMP': ActivityType.COMPLETION,
            'WORK': ActivityType.WORKOVER,
            'SIDE': ActivityType.SIDETRACK,
            'PA': ActivityType.PLUG_ABANDON,
            'TA': ActivityType.TEMPORARY_ABANDON,
            'RECOMP': ActivityType.RECOMPLETION,
            'STIM': ActivityType.STIMULATION,
            'LOG': ActivityType.LOGGING,
            'TEST': ActivityType.TESTING
        }

        activity_str = str(row.get('activity_type', '')).upper()
        activity_type = ActivityType.DRILLING
        for key, val in activity_map.items():
            if key in activity_str:
                activity_type = val
                break

        return WARRecord(
            well_id=well_id,
            activity_type=activity_type,
            start_date=parse_date(row.get('start_date')) or date.today(),
            end_date=parse_date(row.get('end_date')),
            spud_date=parse_date(row.get('spud_date')),
            rig_name=row.get('rig_name'),
            water_depth_ft=float(row.get('water_depth_ft', 0) or 0) if pd.notna(row.get('water_depth_ft')) else None,
            total_depth_md=float(row.get('total_depth_md', 0) or 0) if pd.notna(row.get('total_depth_md')) else None,
            total_depth_tvd=float(row.get('total_depth_tvd', 0) or 0) if pd.notna(row.get('total_depth_tvd')) else None,
            target_formation=row.get('target_formation'),
            operator_name=row.get('operator_name'),
            status=row.get('status')
        )

    # ==================== APD Data Methods ====================

    def download_apd_file(self, use_cache: bool = True) -> Path:
        """
        Download BSEE APD (Application for Permit to Drill) data file.

        Args:
            use_cache: Use cached file if available

        Returns:
            Path to downloaded ZIP file
        """
        cache_path = self.cache_dir / "APDRawData.zip"

        if use_cache and cache_path.exists():
            logger.info(f"Using cached APD file: {cache_path}")
            return cache_path

        logger.info(f"Downloading APD data from: {self.APD_URL}")
        response = self.session.get(self.APD_URL, timeout=600)  # 10 min timeout
        response.raise_for_status()

        cache_path.write_bytes(response.content)
        logger.info(f"Saved APD data: {len(response.content) / (1024*1024):.1f} MB")

        return cache_path

    def extract_apd_data(self, zip_path: Path) -> pd.DataFrame:
        """
        Extract APD data from BSEE ZIP file.

        Args:
            zip_path: Path to APD ZIP file

        Returns:
            DataFrame with APD records
        """
        with zipfile.ZipFile(zip_path, 'r') as zf:
            data_files = [f for f in zf.namelist()
                         if f.endswith(('.txt', '.csv', '.dat'))]

            if not data_files:
                raise ValueError(f"No data file found in {zip_path}")

            with zf.open(data_files[0]) as f:
                try:
                    df = pd.read_csv(f, delimiter='\t', low_memory=False)
                except:
                    f.seek(0)
                    df = pd.read_csv(f, delimiter=',', low_memory=False)

        df = df.rename(columns={
            k: v for k, v in self.APD_COLUMNS.items()
            if k in df.columns
        })

        return df

    def query_apd_by_api(self, api_number: str) -> List[APDRecord]:
        """
        Query APD records for specific API number.

        Args:
            api_number: Well API number

        Returns:
            List of APDRecord objects
        """
        zip_path = self.download_apd_file()
        df = self.extract_apd_data(zip_path)

        well_id = WellIdentifier(api_number=api_number)
        api_10 = well_id.api_10

        df_well = df[df['api_number'].astype(str).str[:10] == api_10]

        records = []
        for _, row in df_well.iterrows():
            records.append(self._row_to_apd_record(row, well_id))

        return records

    def _row_to_apd_record(self, row: pd.Series, well_id: WellIdentifier) -> APDRecord:
        """Convert DataFrame row to APDRecord."""
        def parse_date(val):
            if pd.isna(val):
                return None
            if isinstance(val, str):
                for fmt in ['%Y-%m-%d', '%Y%m%d', '%m/%d/%Y']:
                    try:
                        return pd.to_datetime(val, format=fmt).date()
                    except:
                        continue
            elif hasattr(val, 'date'):
                return val.date()
            return None

        status_map = {
            'PEND': APDStatus.PENDING,
            'APPR': APDStatus.APPROVED,
            'DENY': APDStatus.DENIED,
            'DENY': APDStatus.DENIED,
            'WITH': APDStatus.WITHDRAWN,
            'EXP': APDStatus.EXPIRED
        }

        status_str = str(row.get('status', '')).upper()
        status = APDStatus.PENDING
        for key, val in status_map.items():
            if key in status_str:
                status = val
                break

        return APDRecord(
            well_id=well_id,
            application_date=parse_date(row.get('application_date')) or date.today(),
            approval_date=parse_date(row.get('approval_date')),
            status=status,
            permit_number=row.get('permit_number'),
            proposed_spud_date=parse_date(row.get('proposed_spud_date')),
            proposed_total_depth=float(row.get('proposed_total_depth', 0) or 0) if pd.notna(row.get('proposed_total_depth')) else None,
            well_type=row.get('well_type'),
            operator_name=row.get('operator_name'),
            surface_location=row.get('surface_location'),
            bottom_hole_location=row.get('bottom_hole_location')
        )
=======
>>>>>>> origin/main
```

### Production Aggregator

```python
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
from datetime import date

class ProductionAggregator:
    """
    Aggregate production data across wells, fields, or time periods.
    """

    def __init__(self, wells: List[WellProduction]):
        """
        Initialize aggregator with well production data.

        Args:
            wells: List of WellProduction objects
        """
        self.wells = wells
        self._combined_df = None

    @property
    def combined_dataframe(self) -> pd.DataFrame:
        """Get combined production data as DataFrame."""
        if self._combined_df is None:
            dfs = []
            for well in self.wells:
                df = well.to_dataframe()
                df['api_number'] = well.well_id.api_number
                df['well_name'] = well.well_id.well_name
                dfs.append(df)

            self._combined_df = pd.concat(dfs, ignore_index=True)

        return self._combined_df

    def monthly_totals(self) -> pd.DataFrame:
        """Aggregate production by month."""
        df = self.combined_dataframe.copy()
        df['year_month'] = pd.to_datetime(df['date']).dt.to_period('M')

        return df.groupby('year_month').agg({
            'oil_bbls': 'sum',
            'gas_mcf': 'sum',
            'water_bbls': 'sum',
            'boe': 'sum',
            'days': 'sum',
            'api_number': 'nunique'
        }).rename(columns={'api_number': 'well_count'}).reset_index()

    def annual_totals(self) -> pd.DataFrame:
        """Aggregate production by year."""
        df = self.combined_dataframe.copy()
        df['year'] = pd.to_datetime(df['date']).dt.year

        return df.groupby('year').agg({
            'oil_bbls': 'sum',
            'gas_mcf': 'sum',
            'water_bbls': 'sum',
            'boe': 'sum',
            'days': 'sum',
            'api_number': 'nunique'
        }).rename(columns={'api_number': 'well_count'}).reset_index()

    def well_summary(self) -> pd.DataFrame:
        """Get summary statistics per well."""
        summaries = []
        for well in self.wells:
            df = well.to_dataframe()

            if len(df) == 0:
                continue

            summary = {
                'api_number': well.well_id.api_number,
                'well_name': well.well_id.well_name,
                'first_production': df['date'].min(),
                'last_production': df['date'].max(),
                'months_producing': len(df),
                'cumulative_oil': df['oil_bbls'].sum(),
                'cumulative_gas': df['gas_mcf'].sum(),
                'cumulative_boe': df['boe'].sum(),
                'peak_oil_bopd': df['oil_bopd'].max(),
                'peak_gas_mcfd': df['gas_mcfd'].max(),
                'avg_oil_bopd': df['oil_bopd'].mean(),
                'avg_gas_mcfd': df['gas_mcfd'].mean()
            }
            summaries.append(summary)

        return pd.DataFrame(summaries)

    def decline_curve_data(self, well: WellProduction) -> Dict:
        """
        Prepare data for decline curve analysis.

        Returns time on production and rate data.
        """
        df = well.to_dataframe()
        df = df[df['oil_bopd'] > 0].sort_values('date')

        if len(df) == 0:
            return {'time': [], 'rate': []}

        # Calculate months from first production
        first_date = df['date'].iloc[0]
        df['months'] = ((pd.to_datetime(df['date']) - pd.to_datetime(first_date))
                       .dt.days / 30.44).astype(int)

        return {
            'time': df['months'].tolist(),
            'rate': df['oil_bopd'].tolist(),
            'dates': df['date'].tolist()
        }
```

<<<<<<< HEAD
### Activity Aggregator

```python
from typing import Dict, List
import pandas as pd

class ActivityAggregator:
    """
    Aggregate WAR and APD data across wells, fields, or time periods.
    """

    def __init__(self, activities: List[WellActivity]):
        """
        Initialize aggregator with well activity data.

        Args:
            activities: List of WellActivity objects
        """
        self.activities = activities
        self._combined_war_df = None
        self._combined_apd_df = None

    @property
    def combined_war_dataframe(self) -> pd.DataFrame:
        """Get combined WAR data as DataFrame."""
        if self._combined_war_df is None:
            dfs = []
            for activity in self.activities:
                df = activity.to_war_dataframe()
                if not df.empty:
                    df['area_code'] = activity.well_id.area_code
                    df['block_number'] = activity.well_id.block_number
                    dfs.append(df)

            self._combined_war_df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

        return self._combined_war_df

    def activity_summary(self) -> pd.DataFrame:
        """Summarize activities by type."""
        df = self.combined_war_dataframe
        if df.empty:
            return pd.DataFrame()

        return df.groupby('activity_type').agg({
            'api_number': 'count',
            'duration_days': ['sum', 'mean', 'min', 'max']
        }).round(1)

    def drilling_timeline(self) -> pd.DataFrame:
        """Get drilling activity timeline."""
        df = self.combined_war_dataframe
        if df.empty:
            return pd.DataFrame()

        drilling = df[df['activity_type'] == 'drilling'].copy()
        drilling = drilling.sort_values('start_date')

        return drilling[['api_number', 'start_date', 'end_date', 'duration_days',
                        'rig_name', 'water_depth_ft', 'total_depth_md', 'operator_name']]

    def rig_utilization(self) -> pd.DataFrame:
        """Analyze rig utilization from WAR data."""
        df = self.combined_war_dataframe
        if df.empty:
            return pd.DataFrame()

        rig_summary = df.groupby('rig_name').agg({
            'api_number': 'nunique',
            'duration_days': 'sum',
            'start_date': 'min',
            'end_date': 'max'
        }).rename(columns={
            'api_number': 'wells_drilled',
            'duration_days': 'total_days'
        })

        return rig_summary.sort_values('total_days', ascending=False)

    def operator_activity(self) -> pd.DataFrame:
        """Analyze activity by operator."""
        df = self.combined_war_dataframe
        if df.empty:
            return pd.DataFrame()

        return df.groupby('operator_name').agg({
            'api_number': 'nunique',
            'activity_type': 'count',
            'duration_days': 'sum',
            'water_depth_ft': 'mean',
            'total_depth_md': 'mean'
        }).rename(columns={
            'api_number': 'unique_wells',
            'activity_type': 'total_activities',
            'duration_days': 'total_days',
            'water_depth_ft': 'avg_water_depth',
            'total_depth_md': 'avg_total_depth'
        }).round(0)

    def depth_statistics(self) -> Dict:
        """Calculate depth statistics from drilling data."""
        df = self.combined_war_dataframe
        drilling = df[df['activity_type'] == 'drilling']

        if drilling.empty:
            return {}

        return {
            'water_depth': {
                'min': drilling['water_depth_ft'].min(),
                'max': drilling['water_depth_ft'].max(),
                'mean': drilling['water_depth_ft'].mean(),
                'median': drilling['water_depth_ft'].median()
            },
            'total_depth_md': {
                'min': drilling['total_depth_md'].min(),
                'max': drilling['total_depth_md'].max(),
                'mean': drilling['total_depth_md'].mean(),
                'median': drilling['total_depth_md'].median()
            }
        }
```

=======
>>>>>>> origin/main
### Report Generator

```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

class BSEEReportGenerator:
    """Generate interactive HTML reports for BSEE data."""

    def __init__(self, aggregator: ProductionAggregator):
        """
        Initialize report generator.

        Args:
            aggregator: ProductionAggregator with well data
        """
        self.aggregator = aggregator

    def generate_field_report(self, output_path: Path, field_name: str = "Field"):
        """
        Generate comprehensive field production report.

        Args:
            output_path: Path for HTML output
            field_name: Name of the field for report title
        """
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Monthly Oil Production',
                'Monthly Gas Production',
                'Cumulative Production',
                'Well Count Over Time',
                'Water Cut Trend',
                'GOR Trend'
            ),
            vertical_spacing=0.08
        )

        monthly = self.aggregator.monthly_totals()
        monthly['date'] = monthly['year_month'].dt.to_timestamp()

        # Monthly oil production
        fig.add_trace(
            go.Bar(x=monthly['date'], y=monthly['oil_bbls']/1000,
                   name='Oil (Mbbls)', marker_color='green'),
            row=1, col=1
        )

        # Monthly gas production
        fig.add_trace(
            go.Bar(x=monthly['date'], y=monthly['gas_mcf']/1000,
                   name='Gas (MMCF)', marker_color='red'),
            row=1, col=2
        )

        # Cumulative production
        monthly['cum_oil'] = monthly['oil_bbls'].cumsum() / 1e6
        monthly['cum_gas'] = monthly['gas_mcf'].cumsum() / 1e6

        fig.add_trace(
            go.Scatter(x=monthly['date'], y=monthly['cum_oil'],
                      name='Cum Oil (MMbbls)', line=dict(color='green')),
            row=2, col=1
        )
        fig.add_trace(
            go.Scatter(x=monthly['date'], y=monthly['cum_gas'],
                      name='Cum Gas (BCF)', line=dict(color='red')),
            row=2, col=1
        )

        # Well count
        fig.add_trace(
            go.Scatter(x=monthly['date'], y=monthly['well_count'],
                      name='Active Wells', fill='tozeroy'),
            row=2, col=2
        )

        # Water cut
        df = self.aggregator.combined_dataframe.copy()
        df['date'] = pd.to_datetime(df['date'])
        monthly_avg = df.groupby(df['date'].dt.to_period('M')).agg({
            'oil_bbls': 'sum',
            'water_bbls': 'sum',
            'gas_mcf': 'sum'
        }).reset_index()
        monthly_avg['date'] = monthly_avg['date'].dt.to_timestamp()
        monthly_avg['water_cut'] = (monthly_avg['water_bbls'] /
                                    (monthly_avg['oil_bbls'] + monthly_avg['water_bbls'])) * 100
        monthly_avg['gor'] = monthly_avg['gas_mcf'] / monthly_avg['oil_bbls'].replace(0, np.nan)

        fig.add_trace(
            go.Scatter(x=monthly_avg['date'], y=monthly_avg['water_cut'],
                      name='Water Cut (%)', line=dict(color='blue')),
            row=3, col=1
        )

        # GOR
        fig.add_trace(
            go.Scatter(x=monthly_avg['date'], y=monthly_avg['gor'],
                      name='GOR (MCF/bbl)', line=dict(color='orange')),
            row=3, col=2
        )

        fig.update_layout(
            height=1000,
            title_text=f"{field_name} Production Analysis",
            showlegend=True
        )

        # Write report
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(str(output_path))

        return output_path

    def generate_well_report(self, well: WellProduction, output_path: Path):
        """Generate individual well production report."""
        df = well.to_dataframe()

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Daily Oil Rate',
                'Daily Gas Rate',
                'Cumulative Production',
                'Production Decline'
            )
        )

        # Oil rate
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['oil_bopd'],
                      name='Oil (BOPD)', line=dict(color='green')),
            row=1, col=1
        )

        # Gas rate
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['gas_mcfd'],
                      name='Gas (MCFD)', line=dict(color='red')),
            row=1, col=2
        )

        # Cumulative
        df['cum_oil'] = df['oil_bbls'].cumsum() / 1000
        df['cum_gas'] = df['gas_mcf'].cumsum() / 1000

        fig.add_trace(
            go.Scatter(x=df['date'], y=df['cum_oil'],
                      name='Cum Oil (Mbbls)'),
            row=2, col=1
        )

        # Semi-log decline plot
        df_producing = df[df['oil_bopd'] > 0]
        fig.add_trace(
            go.Scatter(x=df_producing['date'], y=df_producing['oil_bopd'],
                      name='Rate (BOPD)', mode='markers'),
            row=2, col=2
        )
        fig.update_yaxes(type='log', row=2, col=2)

        fig.update_layout(
            height=800,
            title_text=f"Well {well.well_id.api_number} Production History",
            showlegend=True
        )

        fig.write_html(str(output_path))
        return output_path
```

## YAML Configuration

### Query Configuration

```yaml
# config/bsee_query.yaml

metadata:
  task: bsee_data_extraction
  created: "2024-01-15"

query:
  type: by_block  # by_api, by_block, by_lease, by_field

  # API query parameters
  api_number: "1771049130"

  # Block query parameters
  area_code: "GC"  # Green Canyon
  block_number: "640"

  # Time range
  start_year: 2010
  end_year: 2024

data_options:
  include_gas: true
  include_water: true
  include_condensate: true
  normalize_rates: true  # Convert to daily rates

cache:
  enabled: true
  directory: "data/bsee_cache"
  expiry_days: 30

output:
  format: "csv"  # csv, parquet, json
  path: "data/results/bsee_extract.csv"

  report:
    enabled: true
    path: "reports/bsee_production.html"
    title: "BSEE Production Analysis"
```

<<<<<<< HEAD
### WAR Query Configuration

```yaml
# config/war_query.yaml

metadata:
  task: war_data_extraction
  created: "2024-01-15"

query:
  type: by_block  # by_api, by_block, by_area

  # API query parameters
  api_number: "1771049130"

  # Block query parameters
  area_code: "GC"  # Green Canyon
  block_number: "640"

activity_filters:
  types:
    - drilling
    - completion
    - workover
    - sidetrack
  start_date: "2020-01-01"
  end_date: "2024-12-31"

analysis:
  drilling_timeline: true
  rig_utilization: true
  operator_activity: true
  depth_statistics: true

cache:
  enabled: true
  directory: "data/bsee_cache"
  expiry_days: 7  # WAR data updates more frequently

output:
  format: "csv"
  war_data: "data/results/war_extract.csv"
  drilling_timeline: "data/results/drilling_timeline.csv"

  report:
    enabled: true
    path: "reports/war_activity.html"
    title: "Well Activity Report Analysis"
```

### APD Query Configuration

```yaml
# config/apd_query.yaml

metadata:
  task: apd_data_extraction

query:
  type: by_area
  area_code: "WR"  # Walker Ridge

status_filters:
  - approved
  - pending

date_range:
  start: "2023-01-01"
  end: "2024-12-31"

analysis:
  approval_timeline: true
  operator_summary: true
  well_type_breakdown: true

output:
  format: "csv"
  path: "data/results/apd_extract.csv"
```

=======
>>>>>>> origin/main
### Multi-Well Configuration

```yaml
# config/field_analysis.yaml

metadata:
  task: field_analysis
  field_name: "Lower Tertiary Development"

wells:
  - api_number: "1771049130"
    name: "Well A-1"
    type: "producer"

  - api_number: "1771049131"
    name: "Well A-2"
    type: "producer"

  - api_number: "1771049132"
    name: "Well B-1"
    type: "injector"

analysis:
  production_summary: true
  decline_analysis: true
  water_cut_trend: true
  gor_trend: true

time_range:
  start: "2015-01-01"
  end: "2024-12-31"

output:
  summary_csv: "data/results/field_summary.csv"
  well_reports: "reports/wells/"
  field_report: "reports/field_production.html"
```

## CLI Usage

### Basic Queries

```bash
# Query by API number
python -m bsee_extractor query --api 1771049130 --output data/well_production.csv

# Query by block
python -m bsee_extractor query --area GC --block 640 --year 2023

# Query multiple years
python -m bsee_extractor query --api 1771049130 --start-year 2010 --end-year 2024
```

### Report Generation

```bash
# Generate well report
python -m bsee_extractor report --api 1771049130 --output reports/well_report.html

# Generate field report from config
python -m bsee_extractor report --config config/field_analysis.yaml
```

<<<<<<< HEAD
### WAR Queries

```bash
# Query WAR data by API number
python -m bsee_extractor war --api 1771049130 --output data/war_well.csv

# Query WAR data by block
python -m bsee_extractor war --area GC --block 640 --output data/war_block.csv

# Filter by activity type
python -m bsee_extractor war --area WR --block 758 --activity drilling,completion

# Generate drilling timeline report
python -m bsee_extractor war-report --area GC --block 640 --output reports/drilling_timeline.html
```

### APD Queries

```bash
# Query APD data by API number
python -m bsee_extractor apd --api 1771049130 --output data/apd_well.csv

# Query APD data by area
python -m bsee_extractor apd --area WR --status approved,pending --output data/apd_area.csv

# Recent APD applications
python -m bsee_extractor apd --area GC --since 2023-01-01 --output data/recent_apd.csv
```

### Data Export

```bash
# Export production to CSV
=======
### Data Export

```bash
# Export to CSV
>>>>>>> origin/main
python -m bsee_extractor export --api 1771049130 --format csv --output data/export.csv

# Export to Parquet (for large datasets)
python -m bsee_extractor export --area GC --block 640 --format parquet --output data/block_production.parquet
<<<<<<< HEAD

# Export combined production + WAR data
python -m bsee_extractor export --api 1771049130 --include-war --format csv --output data/combined.csv
=======
>>>>>>> origin/main
```

## Usage Examples

### Example 1: Single Well Analysis

```python
from bsee_extractor import BSEEDataClient, BSEEReportGenerator

# Initialize client
client = BSEEDataClient(cache_dir=Path("data/bsee_cache"))

# Query well production
well = client.query_by_api("1771049130", start_year=2010, end_year=2024)

# Get production DataFrame
df = well.to_dataframe()
print(f"Records: {len(df)}")
print(f"Cumulative Oil: {well.cumulative_oil:,.0f} bbls")
print(f"Cumulative Gas: {well.cumulative_gas:,.0f} MCF")

# Generate report
from production_aggregator import ProductionAggregator
aggregator = ProductionAggregator([well])
reporter = BSEEReportGenerator(aggregator)
reporter.generate_well_report(well, Path("reports/well_analysis.html"))
```

### Example 2: Block-Level Analysis

```python
# Query all wells in Green Canyon Block 640
wells = client.query_by_block("GC", "640", year=2023)
print(f"Found {len(wells)} wells in GC 640")

# Aggregate production
aggregator = ProductionAggregator(wells)

# Monthly totals
monthly = aggregator.monthly_totals()
print(f"\n2023 Production:")
print(f"  Total Oil: {monthly['oil_bbls'].sum():,.0f} bbls")
print(f"  Total Gas: {monthly['gas_mcf'].sum():,.0f} MCF")

# Well summary
summary = aggregator.well_summary()
print(f"\nWell Rankings by Cumulative Oil:")
print(summary.sort_values('cumulative_oil', ascending=False)[
    ['api_number', 'cumulative_oil', 'peak_oil_bopd']
].head(10))

# Generate field report
reporter = BSEEReportGenerator(aggregator)
reporter.generate_field_report(
    Path("reports/gc640_production.html"),
    field_name="Green Canyon 640"
)
```

### Example 3: Decline Curve Preparation

```python
# Get decline curve data for type curve analysis
well = client.query_by_api("1771049130")
decline_data = aggregator.decline_curve_data(well)

# Prepare for Arps decline fitting
import numpy as np

time = np.array(decline_data['time'])
rate = np.array(decline_data['rate'])

# Filter to producing periods only
mask = rate > 0
time_producing = time[mask]
rate_producing = rate[mask]

# Export for external decline curve software
decline_df = pd.DataFrame({
    'months': time_producing,
    'oil_bopd': rate_producing
})
decline_df.to_csv("data/decline_input.csv", index=False)
```

<<<<<<< HEAD
### Example 4: WAR Activity Analysis

```python
from bsee_extractor import BSEEDataClient, ActivityAggregator

# Initialize client
client = BSEEDataClient(cache_dir=Path("data/bsee_cache"))

# Query WAR data for a specific well
well_activity = client.query_war_by_api("1771049130")

# Get WAR DataFrame
war_df = well_activity.to_war_dataframe()
print(f"Total activities: {len(war_df)}")
print(f"Activity types: {war_df['activity_type'].unique()}")

# Calculate drilling and completion durations
print(f"\nTotal drilling days: {well_activity.total_drilling_days}")
print(f"Total completion days: {well_activity.total_completion_days}")

# Detailed drilling history
drilling_df = war_df[war_df['activity_type'] == 'drilling']
print(f"\nDrilling Operations:")
print(drilling_df[['start_date', 'end_date', 'duration_days', 'rig_name', 'total_depth_md']])
```

### Example 5: Block-Level Drilling Analysis

```python
# Query all well activities in Walker Ridge Block 758
activities = client.query_war_by_block("WR", "758")
print(f"Found {len(activities)} wells with WAR records in WR 758")

# Aggregate activities
activity_agg = ActivityAggregator(activities)

# Drilling timeline for rig scheduling
drilling_timeline = activity_agg.drilling_timeline()
print("\nDrilling Timeline:")
print(drilling_timeline[['api_number', 'start_date', 'rig_name', 'duration_days']])

# Rig utilization analysis
rig_util = activity_agg.rig_utilization()
print("\nRig Utilization:")
print(rig_util)

# Operator activity summary
operator_summary = activity_agg.operator_activity()
print("\nOperator Activity:")
print(operator_summary)

# Depth statistics
depth_stats = activity_agg.depth_statistics()
print(f"\nWater Depth Range: {depth_stats['water_depth']['min']:.0f} - {depth_stats['water_depth']['max']:.0f} ft")
print(f"Avg Total Depth: {depth_stats['total_depth_md']['mean']:.0f} ft MD")
```

### Example 6: APD Tracking and Permit Analysis

```python
# Query APD records for a well
apd_records = client.query_apd_by_api("1771049130")
print(f"Found {len(apd_records)} APD records")

for apd in apd_records:
    print(f"\nPermit: {apd.permit_number}")
    print(f"  Application Date: {apd.application_date}")
    print(f"  Status: {apd.status.value}")
    print(f"  Well Type: {apd.well_type}")
    if apd.approval_date:
        print(f"  Approval Date: {apd.approval_date}")
        days_to_approve = (apd.approval_date - apd.application_date).days
        print(f"  Days to Approval: {days_to_approve}")
```

### Example 7: Combined Production + Activity Analysis

```python
# Get both production and activity data for a well
well_production = client.query_by_api("1771049130", start_year=2015)
well_activity = client.query_war_by_api("1771049130")

# Combine for comprehensive well analysis
print(f"Well: {well_production.well_id.api_number}")
print(f"\n--- Production Summary ---")
print(f"First Production: {well_production.first_production}")
print(f"Cumulative Oil: {well_production.cumulative_oil:,.0f} bbls")
print(f"Cumulative Gas: {well_production.cumulative_gas:,.0f} MCF")

print(f"\n--- Activity Summary ---")
print(f"First Activity: {well_activity.first_activity}")
print(f"Drilling Days: {well_activity.total_drilling_days}")
print(f"Completion Days: {well_activity.total_completion_days}")
print(f"Total WAR Records: {len(well_activity.war_records)}")

# Calculate time from spud to first production
war_df = well_activity.to_war_dataframe()
drilling_records = war_df[war_df['activity_type'] == 'drilling']
if not drilling_records.empty and well_production.first_production:
    spud_date = drilling_records['spud_date'].min()
    if spud_date:
        days_to_production = (well_production.first_production - spud_date).days
        print(f"\nDays from Spud to First Production: {days_to_production}")
```

=======
>>>>>>> origin/main
## Best Practices

### Data Caching
- Enable caching to avoid repeated downloads
- Set appropriate expiry for frequently updated data
- Use local cache for development, clear for production runs

### Query Optimization
- Query by year ranges to limit data volume
- Use block/area queries for field-level analysis
- Filter early in pipeline to reduce memory usage

### Error Handling
- Handle missing data periods gracefully
- Log warnings for data quality issues
- Validate API numbers before querying

### File Organization
```
project/
├── config/
│   ├── bsee_query.yaml
│   └── field_analysis.yaml
├── data/
│   ├── bsee_cache/         # Downloaded BSEE files
│   ├── raw/                # Raw extracted data
│   ├── processed/          # Cleaned data
│   └── results/            # Analysis outputs
├── reports/
│   ├── wells/              # Individual well reports
│   └── field_production.html
└── src/
    └── bsee_extractor/
        ├── client.py
        ├── models.py
        ├── aggregator.py
        └── reports.py
```

## Related Skills

<<<<<<< HEAD
- [npv-analyzer](../npv-analyzer/SKILL.md) - Economic analysis using BSEE production data
- [hse-risk-analyzer](../hse-risk-analyzer/SKILL.md) - HSE incident analysis and safety scoring
- [production-forecaster](../production-forecaster/SKILL.md) - Decline curve analysis using BSEE production
- [economic-sensitivity-analyzer](../economic-sensitivity-analyzer/SKILL.md) - Sensitivity and scenario analysis
=======
- [npv-analyzer](../npv-analyzer/SKILL.md) - Economic analysis using BSEE data
- [data-pipeline-processor](../../.claude/skills/development/data-pipeline-processor/SKILL.md) - General data processing
- [engineering-report-generator](../../.claude/skills/development/engineering-report-generator/SKILL.md) - Report generation
>>>>>>> origin/main
