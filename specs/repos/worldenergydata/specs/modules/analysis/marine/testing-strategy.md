# Marine Safety Incidents Database - Testing Strategy

> Version: 1.0.0
> Last Updated: 2025-10-03
> Status: Active

## Table of Contents

1. [Testing Pyramid](#testing-pyramid)
2. [Test Coverage Targets](#test-coverage-targets)
3. [Unit Testing](#unit-testing)
4. [Integration Testing](#integration-testing)
5. [End-to-End Testing](#end-to-end-testing)
6. [Performance Testing](#performance-testing)
7. [Security Testing](#security-testing)
8. [Test Fixtures](#test-fixtures)
9. [Test Infrastructure](#test-infrastructure)
10. [Test Data Management](#test-data-management)
11. [Quality Gates](#quality-gates)

---

## Testing Pyramid

### Distribution Strategy

```
         /\
        /E2E\      10% - Critical user workflows
       /------\
      /Integr.\   30% - Component integration
     /----------\
    /   Unit     \ 60% - Business logic & edge cases
   /--------------\
```

### Rationale

- **Unit Tests (60%)**: Fast execution, isolated testing, foundation for refactoring
- **Integration Tests (30%)**: Verify component interactions, database operations
- **E2E Tests (10%)**: Validate critical user workflows, high-value scenarios

### Target Distribution

| Test Type | Quantity | Execution Time | Maintenance |
|-----------|----------|----------------|-------------|
| Unit | ~500 tests | <2 minutes | Low |
| Integration | ~150 tests | <5 minutes | Medium |
| E2E | ~25 tests | <10 minutes | High |
| **Total** | **~675 tests** | **<17 minutes** | **Average** |

---

## Test Coverage Targets

### Overall Coverage Goals

- **Minimum**: 80% overall coverage
- **Target**: 90% overall coverage
- **Critical paths**: 100% coverage

### Component-Specific Targets

| Component | Statements | Branches | Functions | Lines | Priority |
|-----------|-----------|----------|-----------|-------|----------|
| **Scrapers** | 90% | 85% | 90% | 90% | Critical |
| BSEE Scraper | 90% | 85% | 90% | 90% | Critical |
| USCG Scraper | 90% | 85% | 90% | 90% | Critical |
| NTSB Scraper | 90% | 85% | 90% | 90% | Critical |
| **Processors** | 85% | 80% | 85% | 85% | High |
| Data Deduplication | 95% | 90% | 95% | 95% | Critical |
| Cross-referencing | 90% | 85% | 90% | 90% | Critical |
| **API** | 90% | 85% | 90% | 90% | Critical |
| GraphQL Resolvers | 90% | 85% | 90% | 90% | Critical |
| REST Endpoints | 90% | 85% | 90% | 90% | Critical |
| **Database** | 85% | 80% | 85% | 85% | High |
| Models | 90% | 85% | 90% | 90% | High |
| Migrations | 80% | 75% | 80% | 80% | Medium |
| **Utilities** | 80% | 75% | 80% | 80% | Medium |

### Coverage by Feature

```python
# .coveragerc configuration
[run]
source = src/
omit =
    */tests/*
    */migrations/*
    */config/*
    */venv/*

[report]
precision = 2
show_missing = True
skip_covered = False

# Fail CI if coverage drops below threshold
fail_under = 80

[html]
directory = htmlcov

[xml]
output = coverage.xml
```

---

## Unit Testing

### Test Organization

```
tests/
├── unit/
│   ├── scrapers/
│   │   ├── test_bsee_scraper.py          (120 tests)
│   │   ├── test_uscg_scraper.py          (100 tests)
│   │   ├── test_ntsb_scraper.py          (80 tests)
│   │   └── test_base_scraper.py          (50 tests)
│   ├── processors/
│   │   ├── test_deduplication.py         (60 tests)
│   │   ├── test_cross_reference.py       (40 tests)
│   │   └── test_validators.py            (30 tests)
│   ├── models/
│   │   ├── test_incident_model.py        (40 tests)
│   │   ├── test_vessel_model.py          (30 tests)
│   │   └── test_location_model.py        (25 tests)
│   ├── api/
│   │   ├── test_graphql_resolvers.py     (50 tests)
│   │   └── test_rest_endpoints.py        (40 tests)
│   └── utils/
│       ├── test_date_parser.py           (20 tests)
│       └── test_geocoder.py              (15 tests)
└── Total: ~500 unit tests
```

### BSEE Scraper Unit Tests

```python
# tests/unit/scrapers/test_bsee_scraper.py

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from src.scrapers.bsee_scraper import BSEEScraper
from src.models.incident import Incident

class TestBSEEScraper:
    """
    Test suite for BSEE scraper functionality.
    Coverage target: 90%+ statements, 85%+ branches
    """

    @pytest.fixture
    def scraper(self):
        """Fixture providing configured scraper instance."""
        return BSEEScraper(
            base_url="https://www.bsee.gov/stats-facts",
            cache_dir="tests/fixtures/cache",
            rate_limit=1.0
        )

    @pytest.fixture
    def sample_html(self):
        """Sample BSEE incident page HTML."""
        return """
        <html>
            <div class="incident-detail">
                <h2>Incident #2024-001</h2>
                <p class="date">2024-01-15</p>
                <p class="location">Gulf of Mexico</p>
                <p class="description">Fire on platform</p>
            </div>
        </html>
        """

    # ==================== Basic Functionality ====================

    def test_initialization(self, scraper):
        """Test scraper initializes with correct configuration."""
        assert scraper.base_url == "https://www.bsee.gov/stats-facts"
        assert scraper.rate_limit == 1.0
        assert scraper.session is not None

    def test_session_headers(self, scraper):
        """Test HTTP session has proper headers."""
        assert 'User-Agent' in scraper.session.headers
        assert 'Accept' in scraper.session.headers

    # ==================== HTML Parsing ====================

    def test_parse_incident_page_success(self, scraper, sample_html):
        """Test successful parsing of incident detail page."""
        incident = scraper.parse_incident_page(sample_html)

        assert incident is not None
        assert incident['incident_id'] == '2024-001'
        assert incident['date'] == datetime(2024, 1, 15)
        assert incident['location'] == 'Gulf of Mexico'
        assert 'Fire on platform' in incident['description']

    def test_parse_incident_missing_fields(self, scraper):
        """Test handling of incomplete incident data."""
        html = "<html><div class='incident-detail'><h2>Incomplete</h2></div></html>"
        incident = scraper.parse_incident_page(html)

        # Should return partial data with defaults
        assert incident is not None
        assert incident.get('incident_id') is not None
        assert incident.get('date') is None  # Missing date

    def test_parse_malformed_html(self, scraper):
        """Test handling of malformed HTML."""
        html = "<html><div class='broken'><p>No closing tag"

        # Should handle gracefully without raising
        incident = scraper.parse_incident_page(html)
        assert incident is None or isinstance(incident, dict)

    # ==================== Data Extraction ====================

    def test_extract_incident_id(self, scraper):
        """Test incident ID extraction from various formats."""
        test_cases = [
            ("Incident #2024-001", "2024-001"),
            ("BSEE-2024-001", "BSEE-2024-001"),
            ("Incident 2024-001", "2024-001"),
            ("No ID here", None),
        ]

        for input_text, expected in test_cases:
            result = scraper.extract_incident_id(input_text)
            assert result == expected

    def test_extract_date_formats(self, scraper):
        """Test date parsing supports multiple formats."""
        test_cases = [
            ("2024-01-15", datetime(2024, 1, 15)),
            ("01/15/2024", datetime(2024, 1, 15)),
            ("January 15, 2024", datetime(2024, 1, 15)),
            ("15-Jan-2024", datetime(2024, 1, 15)),
            ("Invalid date", None),
        ]

        for input_date, expected in test_cases:
            result = scraper.extract_date(input_date)
            assert result == expected

    def test_extract_location_normalization(self, scraper):
        """Test location string normalization."""
        test_cases = [
            ("Gulf of Mexico", "Gulf of Mexico"),
            ("  Gulf of Mexico  ", "Gulf of Mexico"),
            ("GULF OF MEXICO", "Gulf of Mexico"),
            ("", None),
            (None, None),
        ]

        for input_loc, expected in test_cases:
            result = scraper.extract_location(input_loc)
            assert result == expected

    # ==================== Pagination ====================

    @patch('requests.Session.get')
    def test_pagination_single_page(self, mock_get, scraper):
        """Test scraping when results fit on single page."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><div class='pagination'></div></html>"
        mock_get.return_value = mock_response

        pages = list(scraper.get_all_pages())

        assert len(pages) == 1
        mock_get.assert_called_once()

    @patch('requests.Session.get')
    def test_pagination_multiple_pages(self, mock_get, scraper):
        """Test scraping across multiple pages."""
        mock_responses = [
            Mock(status_code=200, text="<html>Page 1</html>"),
            Mock(status_code=200, text="<html>Page 2</html>"),
            Mock(status_code=200, text="<html>Page 3</html>"),
        ]
        mock_get.side_effect = mock_responses

        scraper.max_pages = 3
        pages = list(scraper.get_all_pages())

        assert len(pages) == 3
        assert mock_get.call_count == 3

    # ==================== Rate Limiting ====================

    @patch('time.sleep')
    @patch('requests.Session.get')
    def test_rate_limiting_enforced(self, mock_get, mock_sleep, scraper):
        """Test rate limiting between requests."""
        mock_get.return_value = Mock(status_code=200, text="<html></html>")
        scraper.rate_limit = 2.0  # 2 seconds between requests

        scraper.fetch_page("https://example.com/page1")
        scraper.fetch_page("https://example.com/page2")

        mock_sleep.assert_called_with(2.0)

    # ==================== Error Handling ====================

    @patch('requests.Session.get')
    def test_http_404_handling(self, mock_get, scraper):
        """Test handling of 404 Not Found errors."""
        mock_get.return_value = Mock(status_code=404)

        result = scraper.fetch_page("https://example.com/missing")

        assert result is None

    @patch('requests.Session.get')
    def test_http_500_retry(self, mock_get, scraper):
        """Test retry logic for 500 server errors."""
        mock_get.side_effect = [
            Mock(status_code=500),  # First attempt fails
            Mock(status_code=500),  # Second attempt fails
            Mock(status_code=200, text="<html>Success</html>")  # Third succeeds
        ]

        scraper.max_retries = 3
        result = scraper.fetch_page("https://example.com/flaky")

        assert result is not None
        assert mock_get.call_count == 3

    @patch('requests.Session.get')
    def test_network_timeout(self, mock_get, scraper):
        """Test handling of network timeout errors."""
        from requests.exceptions import Timeout
        mock_get.side_effect = Timeout("Connection timeout")

        result = scraper.fetch_page("https://example.com/slow")

        assert result is None

    # ==================== Data Validation ====================

    def test_validate_incident_complete(self, scraper):
        """Test validation accepts complete incident data."""
        incident = {
            'incident_id': '2024-001',
            'date': datetime(2024, 1, 15),
            'location': 'Gulf of Mexico',
            'description': 'Fire on platform'
        }

        assert scraper.validate_incident(incident) is True

    def test_validate_incident_missing_required(self, scraper):
        """Test validation rejects incidents missing required fields."""
        incident = {
            'incident_id': '2024-001',
            # Missing required 'date' field
            'location': 'Gulf of Mexico'
        }

        assert scraper.validate_incident(incident) is False

    # ==================== Deduplication ====================

    def test_deduplication_identical(self, scraper):
        """Test deduplication detects identical incidents."""
        incident1 = {'incident_id': '2024-001', 'date': datetime(2024, 1, 15)}
        incident2 = {'incident_id': '2024-001', 'date': datetime(2024, 1, 15)}

        assert scraper.is_duplicate(incident1, incident2) is True

    def test_deduplication_different(self, scraper):
        """Test deduplication allows different incidents."""
        incident1 = {'incident_id': '2024-001', 'date': datetime(2024, 1, 15)}
        incident2 = {'incident_id': '2024-002', 'date': datetime(2024, 1, 16)}

        assert scraper.is_duplicate(incident1, incident2) is False

    # ==================== Edge Cases ====================

    def test_empty_response(self, scraper):
        """Test handling of empty HTTP response."""
        result = scraper.parse_incident_page("")
        assert result is None

    def test_unicode_characters(self, scraper):
        """Test handling of unicode in incident data."""
        html = """
        <html>
            <div class="incident-detail">
                <h2>Incident #2024-001</h2>
                <p class="description">Explosión en plataforma</p>
            </div>
        </html>
        """

        incident = scraper.parse_incident_page(html)
        assert incident is not None
        assert 'Explosión' in incident['description']

    def test_large_description(self, scraper):
        """Test handling of very long description text."""
        description = "A" * 10000  # 10,000 character description
        html = f"""
        <html>
            <div class="incident-detail">
                <h2>Incident #2024-001</h2>
                <p class="description">{description}</p>
            </div>
        </html>
        """

        incident = scraper.parse_incident_page(html)
        assert incident is not None
        assert len(incident['description']) == 10000

    # ==================== Caching ====================

    def test_cache_miss(self, scraper, tmp_path):
        """Test cache returns None on miss."""
        scraper.cache_dir = tmp_path
        result = scraper.get_cached_page("https://example.com/new")
        assert result is None

    def test_cache_hit(self, scraper, tmp_path):
        """Test cache returns stored content on hit."""
        scraper.cache_dir = tmp_path
        url = "https://example.com/cached"
        content = "<html>Cached content</html>"

        scraper.cache_page(url, content)
        result = scraper.get_cached_page(url)

        assert result == content

    def test_cache_expiry(self, scraper, tmp_path):
        """Test cache respects expiry time."""
        scraper.cache_dir = tmp_path
        scraper.cache_ttl = 1  # 1 second TTL
        url = "https://example.com/expire"

        scraper.cache_page(url, "<html>Old</html>")

        import time
        time.sleep(2)  # Wait for cache to expire

        result = scraper.get_cached_page(url)
        assert result is None


# ==================== USCG Scraper Tests ====================

class TestUSCGScraper:
    """
    Test suite for USCG scraper functionality.
    Coverage target: 90%+ statements, 85%+ branches
    """

    @pytest.fixture
    def scraper(self):
        from src.scrapers.uscg_scraper import USCGScraper
        return USCGScraper(
            base_url="https://cgmix.uscg.mil",
            api_key="test_key"
        )

    def test_api_authentication(self, scraper):
        """Test API authentication headers."""
        assert 'Authorization' in scraper.session.headers
        assert scraper.session.headers['Authorization'].startswith('Bearer')

    def test_json_parsing(self, scraper):
        """Test JSON response parsing."""
        json_data = {
            'incidents': [
                {
                    'id': 'USCG-2024-001',
                    'date': '2024-01-15',
                    'type': 'Fire'
                }
            ]
        }

        incidents = scraper.parse_json_response(json_data)
        assert len(incidents) == 1
        assert incidents[0]['incident_id'] == 'USCG-2024-001'

    def test_date_range_filtering(self, scraper):
        """Test filtering incidents by date range."""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)

        params = scraper.build_query_params(start_date, end_date)

        assert params['start_date'] == '2024-01-01'
        assert params['end_date'] == '2024-12-31'


# ==================== NTSB Scraper Tests ====================

class TestNTSBScraper:
    """
    Test suite for NTSB scraper functionality.
    Coverage target: 90%+ statements, 85%+ branches
    """

    @pytest.fixture
    def scraper(self):
        from src.scrapers.ntsb_scraper import NTSBScraper
        return NTSBScraper(base_url="https://data.ntsb.gov")

    def test_xml_parsing(self, scraper):
        """Test XML response parsing."""
        xml_data = """
        <investigations>
            <investigation>
                <id>MAR-24-001</id>
                <date>2024-01-15</date>
                <synopsis>Marine incident</synopsis>
            </investigation>
        </investigations>
        """

        incidents = scraper.parse_xml_response(xml_data)
        assert len(incidents) == 1
        assert incidents[0]['incident_id'] == 'MAR-24-001'

    def test_status_filtering(self, scraper):
        """Test filtering by investigation status."""
        params = scraper.build_query_params(status='final')
        assert params['status'] == 'final'
```

### Deduplication Unit Tests

```python
# tests/unit/processors/test_deduplication.py

import pytest
from datetime import datetime, timedelta
from src.processors.deduplication import DeduplicationEngine
from src.models.incident import Incident

class TestDeduplicationEngine:
    """
    Test suite for incident deduplication logic.
    Coverage target: 95%+ (critical component)
    """

    @pytest.fixture
    def engine(self):
        return DeduplicationEngine(
            similarity_threshold=0.85,
            date_window_days=3
        )

    # ==================== Exact Matches ====================

    def test_exact_duplicate_detection(self, engine):
        """Test detection of exact duplicate incidents."""
        incident1 = Incident(
            incident_id="2024-001",
            source="BSEE",
            date=datetime(2024, 1, 15),
            location="Gulf of Mexico",
            description="Fire on platform Alpha"
        )

        incident2 = Incident(
            incident_id="USCG-2024-001",  # Different ID
            source="USCG",
            date=datetime(2024, 1, 15),
            location="Gulf of Mexico",
            description="Fire on platform Alpha"
        )

        assert engine.is_duplicate(incident1, incident2) is True
        assert engine.similarity_score(incident1, incident2) > 0.95

    # ==================== Fuzzy Matching ====================

    def test_fuzzy_description_matching(self, engine):
        """Test fuzzy matching of similar descriptions."""
        incident1 = Incident(
            date=datetime(2024, 1, 15),
            description="Fire on offshore platform Alpha in Gulf of Mexico"
        )

        incident2 = Incident(
            date=datetime(2024, 1, 15),
            description="Platform Alpha fire in Gulf of Mexico offshore"
        )

        # Same incident, different wording
        assert engine.is_duplicate(incident1, incident2) is True

    def test_typo_tolerance(self, engine):
        """Test tolerance for minor typos."""
        incident1 = Incident(
            date=datetime(2024, 1, 15),
            description="Explosion on platform"
        )

        incident2 = Incident(
            date=datetime(2024, 1, 15),
            description="Explos1on on platfrom"  # Typos
        )

        # Should still match despite typos
        similarity = engine.similarity_score(incident1, incident2)
        assert similarity > engine.similarity_threshold

    # ==================== Date Window ====================

    def test_date_window_within(self, engine):
        """Test incidents within date window can be duplicates."""
        incident1 = Incident(date=datetime(2024, 1, 15))
        incident2 = Incident(date=datetime(2024, 1, 17))  # 2 days later

        # Within 3-day window
        assert engine.within_date_window(incident1, incident2) is True

    def test_date_window_outside(self, engine):
        """Test incidents outside date window are not duplicates."""
        incident1 = Incident(date=datetime(2024, 1, 15))
        incident2 = Incident(date=datetime(2024, 1, 20))  # 5 days later

        # Outside 3-day window
        assert engine.within_date_window(incident1, incident2) is False

    # ==================== Location Matching ====================

    def test_location_exact_match(self, engine):
        """Test exact location matching."""
        incident1 = Incident(location="Gulf of Mexico")
        incident2 = Incident(location="Gulf of Mexico")

        assert engine.locations_match(incident1, incident2) is True

    def test_location_coordinate_proximity(self, engine):
        """Test coordinate-based location matching."""
        incident1 = Incident(
            latitude=28.5000,
            longitude=-89.5000
        )

        incident2 = Incident(
            latitude=28.5010,  # ~1km difference
            longitude=-89.5010
        )

        # Within proximity threshold
        assert engine.locations_match(incident1, incident2) is True

    # ==================== Multi-Source Deduplication ====================

    def test_cross_source_matching(self, engine):
        """Test matching incidents from different sources."""
        bsee_incident = Incident(
            source="BSEE",
            incident_id="BSEE-2024-001",
            date=datetime(2024, 1, 15),
            description="Platform fire"
        )

        uscg_incident = Incident(
            source="USCG",
            incident_id="USCG-2024-042",
            date=datetime(2024, 1, 15),
            description="Fire on platform"
        )

        ntsb_incident = Incident(
            source="NTSB",
            incident_id="MAR-24-001",
            date=datetime(2024, 1, 16),
            description="Platform fire incident"
        )

        # All three should match
        assert engine.is_duplicate(bsee_incident, uscg_incident) is True
        assert engine.is_duplicate(bsee_incident, ntsb_incident) is True
        assert engine.is_duplicate(uscg_incident, ntsb_incident) is True

    # ==================== Performance ====================

    def test_batch_deduplication_performance(self, engine):
        """Test deduplication performance with large dataset."""
        import time

        # Create 1000 incidents
        incidents = [
            Incident(
                incident_id=f"INC-{i}",
                date=datetime(2024, 1, 1) + timedelta(days=i % 30),
                description=f"Incident {i}"
            )
            for i in range(1000)
        ]

        start = time.time()
        duplicates = engine.find_duplicates(incidents)
        duration = time.time() - start

        # Should complete under 5 seconds
        assert duration < 5.0
```

---

## Integration Testing

### Test Organization

```
tests/
├── integration/
│   ├── test_scraper_pipeline.py      (30 tests)
│   ├── test_api_integration.py       (40 tests)
│   ├── test_database_operations.py   (50 tests)
│   ├── test_cross_reference.py       (20 tests)
│   └── test_geocoding_service.py     (10 tests)
└── Total: ~150 integration tests
```

### Scraper Pipeline Tests

```python
# tests/integration/test_scraper_pipeline.py

import pytest
from testcontainers.postgres import PostgresContainer
from src.scrapers.pipeline import ScraperPipeline
from src.database import Database

class TestScraperPipeline:
    """
    Integration tests for complete scraper pipeline.
    Tests scrapers → processors → database flow.
    """

    @pytest.fixture(scope="class")
    def postgres(self):
        """PostgreSQL test container."""
        with PostgresContainer("postgres:17") as postgres:
            yield postgres

    @pytest.fixture
    def database(self, postgres):
        """Database connection to test container."""
        db = Database(postgres.get_connection_url())
        db.create_tables()
        yield db
        db.drop_tables()

    @pytest.fixture
    def pipeline(self, database):
        """Configured scraper pipeline."""
        return ScraperPipeline(
            database=database,
            scrapers=['bsee', 'uscg', 'ntsb'],
            enable_deduplication=True
        )

    def test_full_pipeline_execution(self, pipeline, database):
        """Test complete pipeline from scraping to storage."""
        # Execute pipeline
        results = pipeline.run(
            start_date='2024-01-01',
            end_date='2024-01-31'
        )

        # Verify results
        assert results['total_scraped'] > 0
        assert results['total_stored'] > 0
        assert results['duplicates_removed'] >= 0

        # Verify database contains data
        incidents = database.query("SELECT COUNT(*) FROM incidents").scalar()
        assert incidents == results['total_stored']

    def test_pipeline_deduplication(self, pipeline, database):
        """Test deduplication across multiple sources."""
        results = pipeline.run(
            start_date='2024-01-01',
            end_date='2024-01-31'
        )

        # Check for cross-reference links
        cross_refs = database.query(
            "SELECT COUNT(*) FROM incident_cross_references"
        ).scalar()

        assert cross_refs > 0  # Should find some duplicates

    def test_pipeline_error_recovery(self, pipeline):
        """Test pipeline continues after individual scraper failure."""
        # Simulate scraper failure
        pipeline.scrapers['bsee'].base_url = "https://invalid-url.example"

        results = pipeline.run(
            start_date='2024-01-01',
            end_date='2024-01-31',
            continue_on_error=True
        )

        # Should still get results from other scrapers
        assert results['errors']['bsee'] > 0
        assert results['total_scraped'] > 0  # From USCG and NTSB
```

### API Integration Tests

```python
# tests/integration/test_api_integration.py

import pytest
from fastapi.testclient import TestClient
from src.api.app import create_app
from testcontainers.postgres import PostgresContainer

class TestAPIIntegration:
    """
    Integration tests for API endpoints with real database.
    """

    @pytest.fixture(scope="class")
    def postgres(self):
        with PostgresContainer("postgres:17") as postgres:
            yield postgres

    @pytest.fixture
    def client(self, postgres):
        app = create_app(database_url=postgres.get_connection_url())
        return TestClient(app)

    @pytest.fixture
    def sample_data(self, postgres):
        """Load sample incidents into test database."""
        # Insert test data
        pass

    def test_graphql_query_incidents(self, client, sample_data):
        """Test GraphQL query for incidents."""
        query = """
            query {
                incidents(limit: 10) {
                    id
                    date
                    description
                    source
                }
            }
        """

        response = client.post("/graphql", json={"query": query})

        assert response.status_code == 200
        data = response.json()
        assert 'data' in data
        assert len(data['data']['incidents']) <= 10

    def test_rest_api_filtering(self, client, sample_data):
        """Test REST API with filters."""
        response = client.get(
            "/api/v1/incidents",
            params={
                'source': 'BSEE',
                'start_date': '2024-01-01',
                'end_date': '2024-12-31'
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert all(inc['source'] == 'BSEE' for inc in data['incidents'])

    def test_api_pagination(self, client, sample_data):
        """Test API pagination."""
        # First page
        page1 = client.get("/api/v1/incidents?page=1&per_page=10")
        assert page1.status_code == 200
        assert len(page1.json()['incidents']) == 10

        # Second page
        page2 = client.get("/api/v1/incidents?page=2&per_page=10")
        assert page2.status_code == 200

        # Different results
        assert page1.json()['incidents'] != page2.json()['incidents']
```

### Database Integration Tests

```python
# tests/integration/test_database_operations.py

import pytest
from datetime import datetime
from testcontainers.postgres import PostgresContainer
from src.database import Database
from src.models.incident import Incident

class TestDatabaseOperations:
    """
    Integration tests for database operations.
    Tests models, queries, migrations, constraints.
    """

    @pytest.fixture(scope="class")
    def postgres(self):
        with PostgresContainer("postgres:17") as postgres:
            yield postgres

    @pytest.fixture
    def db(self, postgres):
        database = Database(postgres.get_connection_url())
        database.create_tables()
        yield database
        database.drop_tables()

    def test_incident_crud(self, db):
        """Test complete CRUD operations for incidents."""
        # Create
        incident = Incident(
            incident_id="TEST-001",
            source="BSEE",
            date=datetime(2024, 1, 15),
            description="Test incident"
        )
        db.save(incident)

        # Read
        loaded = db.get(Incident, incident.id)
        assert loaded.incident_id == "TEST-001"

        # Update
        loaded.description = "Updated description"
        db.save(loaded)

        reloaded = db.get(Incident, incident.id)
        assert reloaded.description == "Updated description"

        # Delete
        db.delete(loaded)
        assert db.get(Incident, incident.id) is None

    def test_complex_query_performance(self, db):
        """Test performance of complex analytical queries."""
        import time

        # Insert 10,000 incidents
        incidents = [
            Incident(
                incident_id=f"PERF-{i}",
                source="BSEE",
                date=datetime(2024, 1, 1),
                description=f"Incident {i}"
            )
            for i in range(10000)
        ]
        db.bulk_insert(incidents)

        # Complex aggregation query
        start = time.time()
        results = db.query("""
            SELECT
                source,
                DATE_TRUNC('month', date) as month,
                COUNT(*) as count,
                AVG(severity) as avg_severity
            FROM incidents
            WHERE date >= '2024-01-01'
            GROUP BY source, month
            ORDER BY month, source
        """).all()
        duration = time.time() - start

        # Should complete under 100ms
        assert duration < 0.1
        assert len(results) > 0

    def test_transaction_rollback(self, db):
        """Test transaction rollback on error."""
        with pytest.raises(Exception):
            with db.transaction():
                incident = Incident(incident_id="ROLLBACK-001")
                db.save(incident)

                # Force error
                raise Exception("Simulated error")

        # Verify rollback
        assert db.query(Incident).filter_by(
            incident_id="ROLLBACK-001"
        ).first() is None
```

---

## End-to-End Testing

### Test Organization

```
tests/
├── e2e/
│   ├── test_user_workflows.py        (15 tests)
│   ├── test_data_pipeline.py         (5 tests)
│   └── test_api_scenarios.py         (5 tests)
└── Total: ~25 e2e tests
```

### User Workflow Tests

```python
# tests/e2e/test_user_workflows.py

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestUserWorkflows:
    """
    End-to-end tests for critical user workflows.
    Uses Selenium for browser automation.
    """

    @pytest.fixture
    def browser(self):
        """Selenium WebDriver instance."""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        yield driver
        driver.quit()

    def test_search_and_view_incident(self, browser):
        """
        User story: Search for incident and view details.

        Steps:
        1. Navigate to search page
        2. Enter search criteria
        3. Submit search
        4. Click on result
        5. View incident details
        """
        browser.get("https://localhost:8000/search")

        # Enter search
        search_box = browser.find_element(By.ID, "search-query")
        search_box.send_keys("platform fire")

        # Submit
        search_button = browser.find_element(By.ID, "search-submit")
        search_button.click()

        # Wait for results
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "search-result"))
        )

        # Click first result
        first_result = browser.find_element(By.CLASS_NAME, "search-result")
        first_result.click()

        # Verify incident details page
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "incident-details"))
        )

        assert "Incident Details" in browser.title

    def test_filter_by_date_range(self, browser):
        """
        User story: Filter incidents by date range.
        """
        browser.get("https://localhost:8000/search")

        # Set date range
        start_date = browser.find_element(By.ID, "start-date")
        start_date.send_keys("01/01/2024")

        end_date = browser.find_element(By.ID, "end-date")
        end_date.send_keys("12/31/2024")

        # Apply filter
        apply_button = browser.find_element(By.ID, "apply-filters")
        apply_button.click()

        # Verify results are within date range
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "search-result"))
        )

        # All results should show 2024 dates
        results = browser.find_elements(By.CLASS_NAME, "incident-date")
        for result in results:
            assert "2024" in result.text

    def test_export_search_results(self, browser):
        """
        User story: Export search results to CSV.
        """
        browser.get("https://localhost:8000/search")

        # Perform search
        search_box = browser.find_element(By.ID, "search-query")
        search_box.send_keys("fire")
        browser.find_element(By.ID, "search-submit").click()

        # Wait for results
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "search-result"))
        )

        # Click export
        export_button = browser.find_element(By.ID, "export-csv")
        export_button.click()

        # Verify download started
        import time
        time.sleep(2)  # Wait for download

        # Check download directory for CSV file
        # (Implementation depends on download directory configuration)
```

---

## Performance Testing

### Load Testing

```python
# tests/performance/test_load.py

import pytest
from locust import HttpUser, task, between

class IncidentSearchUser(HttpUser):
    """
    Locust load test for incident search API.

    Simulates realistic user behavior:
    - 60% searches
    - 30% detail views
    - 10% exports
    """

    wait_time = between(1, 3)  # Realistic user think time

    @task(6)
    def search_incidents(self):
        """Search for incidents (60% of traffic)."""
        self.client.get("/api/v1/incidents", params={
            'query': 'fire',
            'limit': 20
        })

    @task(3)
    def view_incident_detail(self):
        """View incident details (30% of traffic)."""
        self.client.get("/api/v1/incidents/BSEE-2024-001")

    @task(1)
    def export_results(self):
        """Export search results (10% of traffic)."""
        self.client.get("/api/v1/export", params={
            'format': 'csv',
            'query': 'platform'
        })


# Run load test:
# locust -f tests/performance/test_load.py --host=http://localhost:8000
# Target: 1000 concurrent users, <200ms p95 response time
```

### Stress Testing

```python
# tests/performance/test_stress.py

import pytest
import asyncio
from concurrent.futures import ThreadPoolExecutor

class TestStressScenarios:
    """
    Stress tests to identify breaking points.
    """

    @pytest.mark.stress
    async def test_concurrent_writes(self):
        """Test database performance under concurrent writes."""
        async def write_incident(i):
            incident = Incident(
                incident_id=f"STRESS-{i}",
                date=datetime.now(),
                description=f"Stress test incident {i}"
            )
            await db.save_async(incident)

        # 1000 concurrent writes
        tasks = [write_incident(i) for i in range(1000)]
        start = time.time()
        await asyncio.gather(*tasks)
        duration = time.time() - start

        # Should complete under 10 seconds
        assert duration < 10.0

    @pytest.mark.stress
    def test_search_under_load(self):
        """Test search performance under high load."""
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [
                executor.submit(
                    lambda: requests.get("http://localhost:8000/api/v1/incidents")
                )
                for _ in range(10000)
            ]

            # Wait for all requests
            responses = [f.result() for f in futures]

            # Check success rate
            success_rate = sum(1 for r in responses if r.status_code == 200) / len(responses)

            # Should maintain 99% success rate
            assert success_rate >= 0.99
```

### Performance Benchmarks

```python
# tests/performance/benchmarks.py

import pytest
from datetime import datetime

class TestPerformanceBenchmarks:
    """
    Performance benchmarks for key operations.
    """

    def test_scraper_throughput(self, benchmark):
        """Benchmark scraper processing throughput."""
        scraper = BSEEScraper()

        result = benchmark(
            scraper.scrape_incidents,
            start_date='2024-01-01',
            end_date='2024-01-31'
        )

        # Should process at least 100 incidents/second
        assert result['throughput'] >= 100

    def test_deduplication_performance(self, benchmark):
        """Benchmark deduplication algorithm."""
        engine = DeduplicationEngine()
        incidents = [create_incident() for _ in range(1000)]

        result = benchmark(engine.find_duplicates, incidents)

        # Should process 1000 incidents under 2 seconds
        assert benchmark.stats['mean'] < 2.0

    def test_database_query_performance(self, benchmark):
        """Benchmark common database queries."""
        result = benchmark(
            db.query,
            """
            SELECT * FROM incidents
            WHERE date >= '2024-01-01'
            AND severity >= 3
            ORDER BY date DESC
            LIMIT 100
            """
        )

        # Should complete under 50ms
        assert benchmark.stats['mean'] < 0.05
```

---

## Security Testing

### OWASP Top 10 Tests

```python
# tests/security/test_owasp.py

import pytest
from src.api.app import create_app

class TestOWASPTop10:
    """
    Security tests covering OWASP Top 10 vulnerabilities.
    """

    def test_sql_injection_prevention(self, client):
        """A01:2021 - Injection"""
        # Attempt SQL injection
        response = client.get(
            "/api/v1/incidents",
            params={'query': "'; DROP TABLE incidents; --"}
        )

        # Should not execute SQL
        assert response.status_code in [200, 400]

        # Verify table still exists
        result = db.query("SELECT COUNT(*) FROM incidents").scalar()
        assert result >= 0

    def test_authentication_required(self, client):
        """A02:2021 - Broken Authentication"""
        # Attempt to access protected endpoint without auth
        response = client.post("/api/v1/admin/incidents")

        assert response.status_code == 401

    def test_xss_prevention(self, client):
        """A03:2021 - Cross-Site Scripting"""
        # Attempt XSS attack
        response = client.post("/api/v1/incidents", json={
            'description': '<script>alert("XSS")</script>'
        })

        # Verify response is sanitized
        assert '<script>' not in response.text
        assert '&lt;script&gt;' in response.text

    def test_sensitive_data_exposure(self, client):
        """A04:2021 - Insecure Design"""
        response = client.get("/api/v1/incidents/BSEE-2024-001")
        data = response.json()

        # Should not expose sensitive internal data
        assert 'password' not in data
        assert 'api_key' not in data
        assert 'internal_notes' not in data

    def test_rate_limiting(self, client):
        """A05:2021 - Security Misconfiguration"""
        # Make 1000 requests rapidly
        responses = [
            client.get("/api/v1/incidents")
            for _ in range(1000)
        ]

        # Should trigger rate limiting
        assert any(r.status_code == 429 for r in responses)
```

### Penetration Testing

```bash
# tests/security/pentest.sh

#!/bin/bash
# Automated penetration testing script

# OWASP ZAP scan
docker run -t owasp/zap2docker-stable zap-baseline.py \
    -t http://localhost:8000 \
    -r zap-report.html

# SQL injection testing
sqlmap -u "http://localhost:8000/api/v1/incidents?query=test" \
    --batch --level=5 --risk=3

# XSS testing
xsser --url "http://localhost:8000/api/v1/incidents" \
    --auto

# SSL/TLS testing
testssl.sh https://localhost:8443

# API security testing
apisec scan http://localhost:8000/openapi.json
```

---

## Test Fixtures

### Fixture Organization

```
tests/
├── fixtures/
│   ├── incidents/
│   │   ├── bsee_sample.json          (100 incidents)
│   │   ├── uscg_sample.json          (100 incidents)
│   │   ├── ntsb_sample.json          (50 incidents)
│   │   └── edge_cases.json           (50 edge cases)
│   ├── html/
│   │   ├── bsee_incident_page.html
│   │   ├── uscg_search_results.html
│   │   └── ntsb_investigation.html
│   ├── mock_responses/
│   │   ├── api_responses.yaml
│   │   └── error_responses.yaml
│   └── databases/
│       ├── test_seed.sql
│       └── performance_seed.sql
```

### Pytest Fixtures

```python
# tests/conftest.py

import pytest
import json
from pathlib import Path
from testcontainers.postgres import PostgresContainer
from src.database import Database

# ==================== Shared Fixtures ====================

@pytest.fixture(scope="session")
def fixtures_dir():
    """Path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"

@pytest.fixture(scope="session")
def sample_incidents(fixtures_dir):
    """Load sample incidents from all sources."""
    incidents = {}
    for source in ['bsee', 'uscg', 'ntsb']:
        with open(fixtures_dir / f"incidents/{source}_sample.json") as f:
            incidents[source] = json.load(f)
    return incidents

@pytest.fixture(scope="session")
def edge_cases(fixtures_dir):
    """Load edge case test data."""
    with open(fixtures_dir / "incidents/edge_cases.json") as f:
        return json.load(f)

# ==================== Database Fixtures ====================

@pytest.fixture(scope="session")
def postgres_container():
    """PostgreSQL container for integration tests."""
    with PostgresContainer("postgres:17") as postgres:
        yield postgres

@pytest.fixture
def test_db(postgres_container):
    """Clean database for each test."""
    db = Database(postgres_container.get_connection_url())
    db.create_tables()
    yield db
    db.drop_tables()

@pytest.fixture
def seeded_db(test_db, sample_incidents):
    """Database pre-populated with sample data."""
    for source, incidents in sample_incidents.items():
        test_db.bulk_insert(incidents)
    return test_db

# ==================== HTTP Mocking ====================

@pytest.fixture
def mock_bsee_response(fixtures_dir):
    """Mock BSEE HTML response."""
    with open(fixtures_dir / "html/bsee_incident_page.html") as f:
        return f.read()

@pytest.fixture
def mock_uscg_api(requests_mock, fixtures_dir):
    """Mock USCG API responses."""
    with open(fixtures_dir / "mock_responses/api_responses.yaml") as f:
        import yaml
        responses = yaml.safe_load(f)

    for endpoint, response in responses['uscg'].items():
        requests_mock.get(
            f"https://cgmix.uscg.mil{endpoint}",
            json=response
        )

    return requests_mock

# ==================== Factory Fixtures ====================

@pytest.fixture
def incident_factory():
    """Factory for creating test incidents."""
    def create_incident(**kwargs):
        defaults = {
            'incident_id': 'TEST-001',
            'source': 'BSEE',
            'date': datetime(2024, 1, 15),
            'description': 'Test incident'
        }
        defaults.update(kwargs)
        return Incident(**defaults)
    return create_incident

@pytest.fixture
def batch_incident_factory(incident_factory):
    """Factory for creating multiple incidents."""
    def create_batch(count=10, **kwargs):
        return [
            incident_factory(incident_id=f"TEST-{i:03d}", **kwargs)
            for i in range(count)
        ]
    return create_batch
```

### Realistic Test Data

```json
// tests/fixtures/incidents/bsee_sample.json

{
  "incidents": [
    {
      "incident_id": "BSEE-2024-001",
      "source": "BSEE",
      "date": "2024-01-15",
      "operator": "Example Energy Corp",
      "facility": "Platform Alpha",
      "location": "Gulf of Mexico",
      "latitude": 28.5000,
      "longitude": -89.5000,
      "incident_type": "Fire",
      "severity": 3,
      "fatalities": 0,
      "injuries": 2,
      "description": "Fire in compressor room caused by equipment failure. Two workers sustained minor burns. Platform evacuated and fire extinguished within 30 minutes.",
      "cause": "Equipment failure - compressor malfunction",
      "investigation_status": "Final",
      "lessons_learned": "Enhanced inspection protocols for compressor systems implemented.",
      "attachments": [
        {
          "type": "investigation_report",
          "url": "https://www.bsee.gov/reports/2024-001.pdf"
        }
      ]
    }
    // ... 99 more realistic incidents
  ]
}
```

```json
// tests/fixtures/incidents/edge_cases.json

{
  "edge_cases": [
    {
      "name": "Missing required fields",
      "incident": {
        "incident_id": "EDGE-001"
        // Missing date, description, etc.
      }
    },
    {
      "name": "Extreme coordinates",
      "incident": {
        "incident_id": "EDGE-002",
        "latitude": 90.0,
        "longitude": 180.0
      }
    },
    {
      "name": "Very long description",
      "incident": {
        "incident_id": "EDGE-003",
        "description": "A".repeat(100000)
      }
    },
    {
      "name": "Special characters in text",
      "incident": {
        "incident_id": "EDGE-004",
        "description": "Incident with émojis 🔥, unicode ñ, and <html>tags</html>"
      }
    },
    {
      "name": "Future date",
      "incident": {
        "incident_id": "EDGE-005",
        "date": "2099-12-31"
      }
    }
  ]
}
```

---

## Test Infrastructure

### Pytest Configuration

```ini
# pytest.ini

[pytest]
# Test discovery
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Output
addopts =
    -ra
    --strict-markers
    --strict-config
    --showlocals
    --tb=short
    --cov=src
    --cov-report=html
    --cov-report=xml
    --cov-report=term-missing:skip-covered
    --cov-fail-under=80

# Test markers
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (database, API)
    e2e: End-to-end tests (slow, full workflows)
    performance: Performance and load tests
    security: Security and penetration tests
    slow: Tests that take >1 second
    stress: Stress tests (may consume significant resources)

# Test paths
testpaths = tests

# Coverage
[coverage:run]
source = src/
omit =
    */tests/*
    */migrations/*
    */venv/*

[coverage:report]
precision = 2
skip_covered = False
show_missing = True

[coverage:html]
directory = htmlcov
```

### Testcontainers Setup

```python
# tests/infrastructure/containers.py

from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
from testcontainers.compose import DockerCompose

class TestInfrastructure:
    """
    Manage test infrastructure containers.
    """

    @staticmethod
    def postgres():
        """PostgreSQL 17 container."""
        return PostgresContainer(
            image="postgres:17",
            username="test",
            password="test",
            dbname="test_db"
        )

    @staticmethod
    def redis():
        """Redis container for caching tests."""
        return RedisContainer(image="redis:7-alpine")

    @staticmethod
    def full_stack():
        """Complete application stack via docker-compose."""
        return DockerCompose(
            filepath="tests/docker-compose.test.yml",
            compose_file_name="docker-compose.test.yml",
            pull=True
        )
```

### CI/CD Integration

```yaml
# .github/workflows/tests.yml

name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  unit-tests:
    name: Unit Tests
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run unit tests
        run: |
          pytest tests/unit/ \
            --cov=src \
            --cov-report=xml \
            --cov-report=term \
            -v

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
          flags: unittests

  integration-tests:
    name: Integration Tests
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:17
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Run integration tests
        run: |
          pytest tests/integration/ \
            --cov=src \
            --cov-append \
            -v
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/test

  e2e-tests:
    name: E2E Tests
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Compose
        run: |
          docker-compose -f docker-compose.test.yml up -d
          sleep 10  # Wait for services

      - name: Run E2E tests
        run: |
          pytest tests/e2e/ -v

      - name: Teardown
        run: docker-compose -f docker-compose.test.yml down

  security-tests:
    name: Security Tests
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Run Bandit (security linter)
        run: |
          pip install bandit
          bandit -r src/ -f json -o bandit-report.json

      - name: Run Safety (dependency check)
        run: |
          pip install safety
          safety check --json

      - name: OWASP ZAP scan
        uses: zaproxy/action-baseline@v0.10.0
        with:
          target: 'http://localhost:8000'
```

---

## Test Data Management

### Version Control

```gitignore
# .gitignore - Test data management

# Exclude large test data files
tests/fixtures/large_datasets/
tests/performance/datasets/

# Include sample data
!tests/fixtures/incidents/*.json
!tests/fixtures/html/*.html

# Exclude generated test artifacts
htmlcov/
.coverage
.pytest_cache/
*.pyc
__pycache__/
```

### Data Generation Scripts

```python
# tests/scripts/generate_test_data.py

"""
Generate realistic test data for marine incidents.
"""

import json
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

def generate_incident(incident_id: int) -> dict:
    """Generate single realistic incident."""
    incident_types = ['Fire', 'Explosion', 'Collision', 'Grounding', 'Capsizing']
    severities = [1, 2, 3, 4, 5]

    return {
        'incident_id': f"GEN-{incident_id:05d}",
        'source': random.choice(['BSEE', 'USCG', 'NTSB']),
        'date': fake.date_between(start_date='-5y', end_date='today').isoformat(),
        'operator': fake.company(),
        'facility': f"Platform {fake.bothify('??-###')}",
        'location': random.choice([
            'Gulf of Mexico',
            'Atlantic Ocean',
            'Pacific Ocean',
            'Caribbean Sea'
        ]),
        'latitude': fake.latitude(),
        'longitude': fake.longitude(),
        'incident_type': random.choice(incident_types),
        'severity': random.choice(severities),
        'fatalities': random.randint(0, 5),
        'injuries': random.randint(0, 20),
        'description': fake.paragraph(nb_sentences=5),
        'cause': fake.sentence(),
        'investigation_status': random.choice(['Preliminary', 'Active', 'Final'])
    }

def generate_dataset(count: int, output_file: str):
    """Generate complete dataset."""
    incidents = [generate_incident(i) for i in range(count)]

    with open(output_file, 'w') as f:
        json.dump({'incidents': incidents}, f, indent=2)

    print(f"Generated {count} incidents → {output_file}")

if __name__ == '__main__':
    # Generate various dataset sizes
    generate_dataset(100, 'tests/fixtures/incidents/generated_100.json')
    generate_dataset(1000, 'tests/fixtures/incidents/generated_1000.json')
    generate_dataset(10000, 'tests/fixtures/incidents/generated_10000.json')
```

### Snapshot Testing

```python
# tests/utils/snapshot.py

import json
from pathlib import Path

class SnapshotTester:
    """
    Snapshot testing for API responses and data structures.
    """

    def __init__(self, snapshot_dir: str = "tests/snapshots"):
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(exist_ok=True)

    def assert_matches_snapshot(self, name: str, data: dict):
        """Compare data against stored snapshot."""
        snapshot_file = self.snapshot_dir / f"{name}.json"

        if snapshot_file.exists():
            # Compare with existing snapshot
            with open(snapshot_file) as f:
                expected = json.load(f)

            assert data == expected, f"Snapshot mismatch for {name}"
        else:
            # Create new snapshot
            with open(snapshot_file, 'w') as f:
                json.dump(data, f, indent=2)

            print(f"Created new snapshot: {name}")

    def update_snapshot(self, name: str, data: dict):
        """Force update existing snapshot."""
        snapshot_file = self.snapshot_dir / f"{name}.json"

        with open(snapshot_file, 'w') as f:
            json.dump(data, f, indent=2)


# Usage in tests:
def test_api_response_format(snapshot):
    response = client.get("/api/v1/incidents/BSEE-2024-001")
    snapshot.assert_matches_snapshot("incident_detail_response", response.json())
```

---

## Quality Gates

### Pre-Commit Requirements

```yaml
# .pre-commit-config.yaml

repos:
  - repo: local
    hooks:
      - id: pytest-unit
        name: Run unit tests
        entry: pytest tests/unit/ -v --tb=short
        language: system
        pass_filenames: false
        always_run: true

      - id: coverage-check
        name: Check test coverage
        entry: pytest tests/unit/ --cov=src --cov-fail-under=80
        language: system
        pass_filenames: false
        always_run: true

      - id: security-check
        name: Security scan
        entry: bandit -r src/ -ll
        language: system
        pass_filenames: false
        always_run: true
```

### Production Deployment Gates

**Required before production deployment:**

1. **Test Coverage**: ≥80% overall, ≥90% for critical paths
2. **Test Pass Rate**: 100% (no failing tests)
3. **Performance**: All benchmarks meet targets
4. **Security**: Zero critical vulnerabilities
5. **Integration Tests**: All pass with production-like data
6. **Load Tests**: System handles expected traffic + 50% margin
7. **Manual QA**: Critical workflows validated by humans

### Continuous Monitoring

```python
# tests/monitoring/test_production.py

import pytest
from src.monitoring import HealthCheck

class TestProductionHealth:
    """
    Continuous health checks for production system.
    Run every 5 minutes via cron.
    """

    def test_api_availability(self):
        """API endpoints respond within SLA."""
        response = requests.get("https://api.marine-incidents.gov/health")
        assert response.status_code == 200
        assert response.elapsed.total_seconds() < 1.0

    def test_database_connection(self):
        """Database connection pool healthy."""
        health = HealthCheck()
        assert health.check_database() is True

    def test_scraper_freshness(self):
        """Data is fresh (updated within 24 hours)."""
        latest = db.query(
            "SELECT MAX(scraped_at) FROM incidents"
        ).scalar()

        age_hours = (datetime.now() - latest).total_seconds() / 3600
        assert age_hours < 24

    def test_error_rate(self):
        """Error rate below threshold."""
        errors = get_error_count_last_hour()
        requests = get_request_count_last_hour()

        error_rate = errors / requests if requests > 0 else 0
        assert error_rate < 0.01  # <1% error rate
```

---

## Summary

### Testing Metrics Dashboard

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Total Tests** | 675 | TBD | 🟡 |
| **Unit Tests** | 500 | TBD | 🟡 |
| **Integration Tests** | 150 | TBD | 🟡 |
| **E2E Tests** | 25 | TBD | 🟡 |
| **Coverage** | 80% | TBD | 🟡 |
| **Execution Time** | <17min | TBD | 🟡 |
| **Pass Rate** | 100% | TBD | 🟡 |

### Implementation Priority

**Phase 1: Foundation (Week 1-2)**
1. Set up pytest infrastructure
2. Implement unit tests for scrapers (350 tests)
3. Configure testcontainers
4. Set up CI/CD pipeline

**Phase 2: Integration (Week 3-4)**
5. Database integration tests (50 tests)
6. API integration tests (40 tests)
7. Pipeline integration tests (30 tests)

**Phase 3: Quality (Week 5-6)**
8. E2E workflow tests (25 tests)
9. Performance benchmarks
10. Security testing

**Phase 4: Optimization (Week 7-8)**
11. Load testing
12. Test data refinement
13. Documentation and training

---

**Testing Philosophy**: Tests are not just quality gates—they're design documentation, regression prevention, and confidence enablers. Invest heavily in comprehensive, maintainable tests.
