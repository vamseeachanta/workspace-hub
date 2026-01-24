# Testing Framework Standards

> **Version:** 1.0.0
> **Last Updated:** 2026-01-13
> **Status:** Mandatory for all workspace-hub repositories
> **Scope:** All 25+ repositories across Work (Tier 1-3) and Personal tiers

## Overview

This document defines universal testing standards for all repositories in workspace-hub. The framework establishes minimum requirements for test organization, coverage, and execution while allowing domain-specific customization for different repository types.

**Key Principles:**
- Test-Driven Development (TDD) mandatory for all new features
- Clear test organization by type (unit, integration, performance, domain-specific)
- Real data preferred over mocks where practical
- Comprehensive CI/CD integration with automated reporting
- Progressive coverage goals (80% minimum → 90%+ target)

**Coverage Targets by Repository Tier:**
- **Tier 1 (Production/Strategic):** 85% minimum, 95%+ target
- **Tier 2 (Active Development):** 80% minimum, 90%+ target
- **Tier 3 (Maintenance):** 80% minimum, 85%+ target

---

## Testing Framework Selection

### Primary: pytest (Python)

**Why pytest:**
- Rich fixture system for test organization
- Plugin ecosystem (pytest-cov, pytest-mock, pytest-benchmark, pytest-asyncio)
- Parametrized testing for comprehensive coverage
- Clear, readable test output
- Native CI/CD integration
- Performance testing with benchmarking

**Required Core Packages:**
```txt
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.1
pytest-asyncio>=0.21.0
pytest-benchmark>=4.0.0
pytest-xdist>=3.3.0              # Parallel execution
pytest-timeout>=2.1.0            # Test timeouts
pytest-html>=3.2.0               # HTML reports
```

**Installation:**
```bash
uv pip install pytest pytest-cov pytest-mock pytest-asyncio pytest-benchmark pytest-xdist pytest-timeout pytest-html
```

### Secondary: Jest (JavaScript/TypeScript)

**Why Jest:**
- Zero-config for most projects
- Built-in code coverage
- Snapshot testing
- Excellent TypeScript support
- Parallel test execution

**Required Packages:**
```json
{
  "devDependencies": {
    "jest": "^29.6.0",
    "@types/jest": "^29.5.3",
    "ts-jest": "^29.1.1",
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0",
    "jest-extended": "^4.0.0"
  }
}
```

### Tertiary: bats-core (Bash/Shell Scripts)

**Why bats-core:**
- TAP-compliant output
- Excellent for CLI testing
- Minimal syntax, easy to learn
- Integration test support

**Installation:**
```bash
npm install -g bats
```

---

## Test Organization Structure

### Directory Hierarchy

Every repository MUST follow this structure:

```
repository/
├── src/                          # Source code
│   └── modules/
│       └── module_name/
│           ├── __init__.py
│           └── core.py
├── tests/                        # All test files
│   ├── unit/                     # Unit tests
│   │   ├── test_module_name.py
│   │   ├── test_core.py
│   │   └── fixtures/
│   │       └── sample_data.json
│   ├── integration/              # Integration tests
│   │   ├── test_module_integration.py
│   │   ├── test_workflow_e2e.py
│   │   └── fixtures/
│   │       └── test_database.db
│   ├── performance/              # Performance/benchmark tests
│   │   ├── test_performance_constraints.py
│   │   └── benchmarks.py
│   ├── domain/                   # Domain-specific tests
│   │   ├── test_llm_integration.py
│   │   ├── test_database_operations.py
│   │   ├── test_api_endpoints.py
│   │   ├── test_etl_pipelines.py
│   │   ├── test_scrapy_spiders.py
│   │   └── test_selenium_flows.py
│   ├── conftest.py               # pytest fixtures and config
│   ├── pytest.ini                # pytest configuration
│   └── __init__.py
├── pyproject.toml                # Python project config
└── .coveragerc                   # Coverage configuration
```

### File Naming Conventions

| Test Type | Naming Pattern | Example |
|-----------|----------------|---------|
| Unit tests | `test_<module_name>.py` | `test_user_service.py` |
| Integration tests | `test_<feature>_integration.py` | `test_auth_flow_integration.py` |
| Performance tests | `test_<feature>_performance.py` | `test_api_performance.py` |
| Domain tests (LLM) | `test_llm_<feature>.py` | `test_llm_embeddings.py` |
| Domain tests (API) | `test_api_<endpoint>.py` | `test_api_users.py` |
| Domain tests (DB) | `test_db_<entity>.py` | `test_db_migrations.py` |
| Fixtures | Stored in `tests/<type>/fixtures/` | `sample_data.json` |
| Conftest | `conftest.py` (pytest standard) | `tests/conftest.py` |

---

## Testing Levels

### 1. Unit Tests

**Purpose:** Test individual functions/methods in complete isolation

**Characteristics:**
- Test single units of code (functions, methods, classes)
- Mock all external dependencies
- Fast execution (<100ms per test, ideally <10ms)
- No file I/O, database access, or network calls
- Completely deterministic results
- Comprehensive coverage of edge cases

**Directory:** `tests/unit/`

**Example (Python):**
```python
import pytest
from src.modules.user_service import UserService
from unittest.mock import Mock

class TestUserService:
    """Unit tests for UserService."""

    @pytest.fixture
    def user_service(self):
        """Create UserService with mocked dependencies."""
        mock_db = Mock()
        mock_logger = Mock()
        return UserService(db=mock_db, logger=mock_logger)

    def test_user_creation_with_valid_email(self, user_service):
        """Test that user is created with valid email."""
        user = user_service.create_user(
            username="testuser",
            email="test@example.com"
        )

        assert user.username == "testuser"
        assert user.email == "test@example.com"

    def test_user_creation_with_invalid_email(self, user_service):
        """Test that invalid email raises ValueError."""
        with pytest.raises(ValueError, match="Invalid email"):
            user_service.create_user(
                username="testuser",
                email="invalid-email"
            )

    @pytest.mark.parametrize("email,expected", [
        ("test@example.com", True),
        ("test@example.co.uk", True),
        ("invalid@", False),
        ("@example.com", False),
        ("noatsign.com", False),
    ])
    def test_email_validation_parametrized(self, user_service, email, expected):
        """Parametrized test for email validation."""
        result = user_service.is_valid_email(email)
        assert result == expected
```

**Best Practices:**
- ✅ One test per logical unit
- ✅ Use parametrized tests for multiple input scenarios
- ✅ Mock external dependencies completely
- ✅ Descriptive test names explaining what is tested
- ✅ Use fixtures for setup/teardown
- ❌ Never call real APIs or databases in unit tests
- ❌ Never use sleep() or time-dependent logic
- ❌ Never have interdependent unit tests

**Marker:**
```python
@pytest.mark.unit
def test_something():
    pass
```

**Run Only Unit Tests:**
```bash
pytest tests/unit/ -m unit
# Or directly:
pytest tests/unit/
```

---

### 2. Integration Tests

**Purpose:** Test interactions between components and systems

**Characteristics:**
- Test component integration (multiple units working together)
- Use real dependencies where practical
- May include file I/O, database operations, external service mocking
- Test data flow between modules
- Verify error propagation and recovery
- Slower than unit tests (100ms-5s range acceptable)
- Deterministic results with controlled test data

**Directory:** `tests/integration/`

**Example (Python):**
```python
import pytest
import tempfile
from pathlib import Path
from src.modules.pipeline import DataPipeline
from src.modules.storage import DataStore

class TestDataPipelineIntegration:
    """Integration tests for DataPipeline with real storage."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            store = DataStore(str(db_path))
            yield store
            store.cleanup()

    @pytest.fixture
    def pipeline(self, temp_db):
        """Create pipeline with real storage backend."""
        return DataPipeline(storage=temp_db)

    def test_pipeline_end_to_end_with_valid_data(self, pipeline):
        """Test complete pipeline execution with valid data."""
        input_data = {
            "values": [1, 2, 3, 4, 5],
            "metadata": {"source": "test"}
        }

        result = pipeline.process(input_data)

        assert result["status"] == "success"
        assert result["record_count"] == 5
        assert pipeline.storage.get_record_count() == 5

    def test_pipeline_error_recovery(self, pipeline):
        """Test pipeline handles errors gracefully and recovers."""
        invalid_data = {"invalid_key": "value"}  # Missing required fields

        result = pipeline.process(invalid_data)

        assert result["status"] == "error"
        assert "error_message" in result
        # Verify storage is not corrupted
        assert pipeline.storage.get_record_count() == 0

    def test_pipeline_with_large_dataset(self, pipeline):
        """Test pipeline handles large datasets efficiently."""
        large_dataset = {
            "values": list(range(10000)),
            "metadata": {"size": "large"}
        }

        result = pipeline.process(large_dataset)

        assert result["status"] == "success"
        assert result["record_count"] == 10000
        assert pipeline.storage.get_record_count() == 10000

    def test_concurrent_pipeline_operations(self, pipeline):
        """Test pipeline handles concurrent operations safely."""
        import concurrent.futures

        def process_batch(batch_num):
            data = {"values": list(range(100)), "batch": batch_num}
            return pipeline.process(data)

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [process_batch(i) for i in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert all(r["status"] == "success" for r in results)
        assert pipeline.storage.get_record_count() == 500
```

**Best Practices:**
- ✅ Use real services where practical (real databases, file systems)
- ✅ Use test containers/fixtures for isolated environments
- ✅ Mock only external services (APIs, third-party services)
- ✅ Test error paths and recovery mechanisms
- ✅ Verify data flow between components
- ✅ Use realistic test data
- ❌ Don't mock your own code
- ❌ Don't test implementation details
- ❌ Don't make external API calls to production services

**Marker:**
```python
@pytest.mark.integration
def test_something():
    pass
```

**Run Only Integration Tests:**
```bash
pytest tests/integration/ -m integration
```

---

### 3. Performance Tests

**Purpose:** Ensure code meets performance requirements and constraints

**Characteristics:**
- Measure execution time and resource usage
- Verify operations complete within thresholds
- Test with realistic data sizes
- Track performance trends over time
- Fail if performance regressions detected
- Run on every commit in CI/CD
- Report benchmarking results

**Directory:** `tests/performance/`

**Example (Python with pytest-benchmark):**
```python
import pytest
from src.modules.algorithms import sort_large_dataset, calculate_statistics

class TestPerformanceConstraints:
    """Performance tests for algorithm constraints."""

    @pytest.mark.performance
    def test_sort_completes_within_time_limit(self, benchmark):
        """Verify sorting completes within 500ms for 10k items."""
        data = list(range(10000, 0, -1))  # Worst case: reverse sorted

        result = benchmark(sort_large_dataset, data)

        assert len(result) == 10000
        assert result == sorted(data)
        # Benchmark stats automatically recorded
        assert benchmark.stats['mean'] < 0.5  # 500ms threshold

    @pytest.mark.performance
    @pytest.mark.slow
    def test_large_dataset_processing(self, benchmark):
        """Verify processing of 100k items completes in time limit."""
        large_data = {
            "values": list(range(100000)),
            "metadata": {"type": "large"}
        }

        result = benchmark(calculate_statistics, large_data)

        assert result["count"] == 100000
        assert benchmark.stats['mean'] < 2.0  # 2 second limit

    def test_memory_efficiency(self):
        """Test memory usage stays within limits."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB

        # Run operation
        data = list(range(1000000))
        sorted_data = sort_large_dataset(data)

        memory_after = process.memory_info().rss / 1024 / 1024
        memory_increase = memory_after - memory_before

        # Memory increase should be reasonable (not exponential)
        assert memory_increase < 500  # Less than 500MB increase

    @pytest.mark.parametrize("size", [100, 1000, 10000])
    def test_performance_scaling(self, benchmark, size):
        """Test that algorithm scales linearly."""
        data = list(range(size, 0, -1))

        result = benchmark(sort_large_dataset, data)

        assert len(result) == size
        # Performance should scale roughly linearly
        # (allows for ~5x slowdown for each 10x data increase)
```

**Configuration (pytest.ini):**
```ini
[tool:pytest]
markers =
    performance: Performance benchmark tests with time thresholds
    slow: Slow tests (>1 second execution time)

# Benchmark configuration
benchmark_max_time = 1.0
benchmark_min_rounds = 5
benchmark_warmup = true

# Timeout for individual tests
timeout = 300  # 5 minutes max per test
```

**Performance Thresholds by Operation Type:**

| Operation Type | Max Duration | Max Memory | Notes |
|----------------|--------------|-----------|-------|
| Simple calculation | 100ms | 10MB | Should complete instantly |
| File I/O (100KB) | 500ms | 50MB | Network-independent |
| Database query | 1s | 100MB | Simple query, optimized |
| API call | 5s | 100MB | Includes network latency |
| Large dataset (100k) | 2s | 500MB | Scales with data size |
| ETL pipeline | 10s | 1GB | Complex transformation |

**Best Practices:**
- ✅ Run with `--benchmark-only` flag in CI/CD
- ✅ Warm up benchmarks before timing
- ✅ Use realistic data sizes
- ✅ Run multiple iterations for consistency
- ✅ Track trends over time
- ✅ Fail CI/CD on regressions
- ❌ Don't benchmark in debug mode
- ❌ Don't benchmark with system under load
- ❌ Don't set unrealistic thresholds

**Marker:**
```python
@pytest.mark.performance
@pytest.mark.slow
def test_something(benchmark):
    pass
```

**Run Only Performance Tests:**
```bash
pytest tests/performance/ -m performance --benchmark-only
```

---

### 4. Domain-Specific Tests

Domain-specific tests are required for repositories working in particular domains. These tests validate domain-specific requirements and constraints.

#### 4.1 LLM/AI Integration Tests

**Purpose:** Test AI model integrations, embeddings, and language model interactions

**Applicable to:** worldenergydata, digitalmodel, aceengineercode, energy

**File Location:** `tests/domain/test_llm_<feature>.py`

**Example:**
```python
import pytest
from src.modules.llm_service import EmbeddingService, CompletionService

class TestLLMIntegration:
    """Tests for LLM integration."""

    @pytest.fixture
    def embedding_service(self):
        """Create embedding service with real model."""
        return EmbeddingService(model="text-embedding-3-small")

    @pytest.fixture
    def completion_service(self):
        """Create completion service with mocked API."""
        return CompletionService(api_key="test-key")

    @pytest.mark.llm
    def test_embedding_generation(self, embedding_service):
        """Test that embeddings are generated correctly."""
        text = "The quick brown fox jumps over the lazy dog"

        embedding = embedding_service.embed(text)

        assert isinstance(embedding, list)
        assert len(embedding) == 1536  # OpenAI embedding dimension
        assert all(isinstance(x, float) for x in embedding)

    @pytest.mark.llm
    @pytest.mark.slow
    def test_embedding_similarity(self, embedding_service):
        """Test that similar texts have high similarity."""
        text1 = "The cat sat on the mat"
        text2 = "A feline rested on the rug"
        text3 = "Programming is fun"

        emb1 = embedding_service.embed(text1)
        emb2 = embedding_service.embed(text2)
        emb3 = embedding_service.embed(text3)

        similarity_12 = embedding_service.cosine_similarity(emb1, emb2)
        similarity_13 = embedding_service.cosine_similarity(emb1, emb3)

        # Similar texts should have higher similarity
        assert similarity_12 > similarity_13

    @pytest.mark.llm
    def test_completion_generation(self, completion_service):
        """Test that text completion works correctly."""
        prompt = "Write a one-sentence summary of machine learning:"

        response = completion_service.complete(
            prompt=prompt,
            max_tokens=100,
            temperature=0.7
        )

        assert response is not None
        assert len(response) > 0
        assert isinstance(response, str)

    @pytest.mark.llm
    def test_completion_with_constraints(self, completion_service):
        """Test that completion respects constraints."""
        prompt = "List 3 programming languages:"

        response = completion_service.complete(
            prompt=prompt,
            max_tokens=50,  # Very limited
            temperature=0.0  # Deterministic
        )

        assert response is not None
        assert len(response.split()) <= 20  # Rough word count check
```

**Marker:**
```python
@pytest.mark.llm
def test_something():
    pass
```

**Skip LLM Tests (for offline testing):**
```bash
pytest -m "not llm"
```

---

#### 4.2 Database Tests

**Purpose:** Test database operations, migrations, and data integrity

**Applicable to:** digitalmodel, worldenergydata, aceengineercode, assetutilities

**File Location:** `tests/domain/test_db_<entity>.py`

**Example:**
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.modules.models import Base, User, Product
from src.modules.database import Database

class TestDatabaseOperations:
    """Tests for database operations."""

    @pytest.fixture
    def db_session(self):
        """Create in-memory SQLite database for testing."""
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    @pytest.mark.database
    def test_user_creation(self, db_session):
        """Test that users are created correctly."""
        user = User(username="testuser", email="test@example.com")
        db_session.add(user)
        db_session.commit()

        retrieved = db_session.query(User).filter_by(username="testuser").first()

        assert retrieved is not None
        assert retrieved.email == "test@example.com"

    @pytest.mark.database
    def test_unique_constraint_violation(self, db_session):
        """Test that unique constraints are enforced."""
        from sqlalchemy.exc import IntegrityError

        user1 = User(username="testuser", email="test1@example.com")
        user2 = User(username="testuser", email="test2@example.com")

        db_session.add(user1)
        db_session.commit()
        db_session.add(user2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    @pytest.mark.database
    def test_relationship_cascade_delete(self, db_session):
        """Test that cascade delete works correctly."""
        user = User(username="testuser", email="test@example.com")
        product1 = Product(name="Product 1", user=user)
        product2 = Product(name="Product 2", user=user)

        db_session.add_all([user, product1, product2])
        db_session.commit()

        user_id = user.id
        db_session.delete(user)
        db_session.commit()

        # Verify user and related products are deleted
        assert db_session.query(User).filter_by(id=user_id).first() is None
        assert db_session.query(Product).filter_by(user_id=user_id).count() == 0

    @pytest.mark.database
    @pytest.mark.slow
    def test_bulk_insert_performance(self, db_session):
        """Test that bulk inserts perform efficiently."""
        users = [User(username=f"user{i}", email=f"user{i}@example.com") for i in range(1000)]

        db_session.bulk_save_objects(users)
        db_session.commit()

        assert db_session.query(User).count() == 1000
```

**Marker:**
```python
@pytest.mark.database
def test_something():
    pass
```

---

#### 4.3 API Endpoint Tests

**Purpose:** Test HTTP API endpoints, request/response validation

**Applicable to:** digitalmodel, aceengineer-website, energy, assetutilities

**File Location:** `tests/domain/test_api_<endpoint>.py`

**Example:**
```python
import pytest
from fastapi.testclient import TestClient
from src.main import app

class TestUserAPI:
    """Tests for user API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client for API."""
        return TestClient(app)

    @pytest.mark.api
    def test_get_user_success(self, client):
        """Test successful user retrieval."""
        response = client.get("/api/users/1")

        assert response.status_code == 200
        assert response.json()["id"] == 1
        assert "username" in response.json()

    @pytest.mark.api
    def test_get_user_not_found(self, client):
        """Test 404 when user doesn't exist."""
        response = client.get("/api/users/99999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.api
    def test_create_user_with_valid_data(self, client):
        """Test user creation with valid data."""
        user_data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "securepass123"
        }

        response = client.post("/api/users", json=user_data)

        assert response.status_code == 201
        assert response.json()["username"] == "newuser"

    @pytest.mark.api
    def test_create_user_invalid_email(self, client):
        """Test user creation validation."""
        user_data = {
            "username": "newuser",
            "email": "invalid-email",
            "password": "securepass123"
        }

        response = client.post("/api/users", json=user_data)

        assert response.status_code == 422  # Unprocessable Entity
        assert "email" in response.json()["detail"][0]["loc"]

    @pytest.mark.api
    @pytest.mark.parametrize("status_code,expected_message", [
        (200, "OK"),
        (201, "Created"),
        (400, "Bad Request"),
        (401, "Unauthorized"),
        (404, "Not Found"),
        (500, "Internal Server Error"),
    ])
    def test_status_code_responses(self, client, status_code, expected_message):
        """Test various API status code responses."""
        # This is a simplified example
        assert status_code in [200, 201, 400, 401, 404, 500]
```

**Marker:**
```python
@pytest.mark.api
def test_something():
    pass
```

---

#### 4.4 ETL Pipeline Tests

**Purpose:** Test data extraction, transformation, and loading operations

**Applicable to:** worldenergydata, assetutilities, energy, aceengineercode

**File Location:** `tests/domain/test_etl_<pipeline>.py`

**Example:**
```python
import pytest
import pandas as pd
from src.modules.etl import DataExtractor, DataTransformer, DataLoader

class TestETLPipeline:
    """Tests for ETL pipeline operations."""

    @pytest.fixture
    def sample_csv_data(self, tmp_path):
        """Create sample CSV file for testing."""
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'value': [10.5, 20.3, 15.8],
            'category': ['A', 'B', 'A']
        })
        file_path = tmp_path / "sample.csv"
        df.to_csv(file_path, index=False)
        return str(file_path)

    @pytest.mark.etl
    def test_data_extraction(self, sample_csv_data):
        """Test data extraction from CSV."""
        extractor = DataExtractor(format='csv')
        data = extractor.extract(sample_csv_data)

        assert len(data) == 3
        assert list(data.columns) == ['id', 'value', 'category']

    @pytest.mark.etl
    def test_data_transformation(self):
        """Test data transformation operations."""
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'value': [10.5, 20.3, 15.8],
            'category': ['A', 'B', 'A']
        })

        transformer = DataTransformer()
        transformed = transformer.transform(df)

        # Verify transformations applied
        assert transformed['value'].dtype == 'float64'
        assert transformed['category'].str.isupper().all()

    @pytest.mark.etl
    def test_data_validation(self):
        """Test data validation during transformation."""
        df_invalid = pd.DataFrame({
            'id': [1, 2, None],  # Missing value
            'value': [10.5, 'invalid', 15.8],  # Non-numeric
            'category': ['A', 'B', 'A']
        })

        transformer = DataTransformer()

        # Should handle validation gracefully
        with pytest.raises(ValueError, match="Invalid data"):
            transformer.transform(df_invalid)

    @pytest.mark.etl
    @pytest.mark.slow
    def test_large_dataset_etl(self):
        """Test ETL pipeline with large dataset."""
        # Create 100k row dataset
        df = pd.DataFrame({
            'id': range(100000),
            'value': [i * 1.5 for i in range(100000)],
            'category': ['A', 'B', 'C'] * 33333 + ['A']
        })

        transformer = DataTransformer()
        transformed = transformer.transform(df)

        assert len(transformed) == 100000
        assert transformed['value'].max() > 100000
```

**Marker:**
```python
@pytest.mark.etl
def test_something():
    pass
```

---

#### 4.5 Web Scraping Tests (Scrapy)

**Purpose:** Test web scraping spiders and data extraction

**Applicable to:** worldenergydata, data-scraping projects

**File Location:** `tests/domain/test_scrapy_<spider>.py`

**Example:**
```python
import pytest
from scrapy.http import HtmlResponse
from src.spiders.energy_spider import EnergySpider

class TestEnergySpider:
    """Tests for energy data scraping spider."""

    @pytest.fixture
    def spider(self):
        """Create spider instance."""
        return EnergySpider()

    @pytest.fixture
    def sample_response(self):
        """Create mock HTML response."""
        html = '''
        <html>
            <body>
                <div class="energy-item">
                    <span class="name">Solar Farm A</span>
                    <span class="capacity">100 MW</span>
                    <span class="location">California</span>
                </div>
                <div class="energy-item">
                    <span class="name">Wind Farm B</span>
                    <span class="capacity">250 MW</span>
                    <span class="location">Texas</span>
                </div>
            </body>
        </html>
        '''
        return HtmlResponse(
            url="http://example.com/energy",
            body=html.encode('utf-8')
        )

    @pytest.mark.scrapy
    def test_spider_extracts_items(self, spider, sample_response):
        """Test that spider extracts energy items correctly."""
        items = list(spider.parse(sample_response))

        assert len(items) == 2
        assert items[0]['name'] == 'Solar Farm A'
        assert items[0]['capacity'] == '100 MW'

    @pytest.mark.scrapy
    def test_spider_handles_missing_fields(self, spider):
        """Test spider handles missing fields gracefully."""
        html = '''
        <html>
            <body>
                <div class="energy-item">
                    <span class="name">Solar Farm A</span>
                    <!-- missing capacity -->
                    <span class="location">California</span>
                </div>
            </body>
        </html>
        '''
        response = HtmlResponse(
            url="http://example.com/energy",
            body=html.encode('utf-8')
        )

        items = list(spider.parse(response))

        assert items[0]['capacity'] is None or 'capacity' not in items[0]

    @pytest.mark.scrapy
    @pytest.mark.slow
    def test_spider_pagination(self, spider):
        """Test spider handles pagination correctly."""
        # Mock implementation test
        assert spider.allowed_domains == ['example.com']
```

**Marker:**
```python
@pytest.mark.scrapy
def test_something():
    pass
```

---

#### 4.6 Selenium Browser Tests

**Purpose:** Test web application UI and user interactions

**Applicable to:** aceengineer-website, aceengineer-admin, digitalmodel (if web UI)

**File Location:** `tests/domain/test_selenium_<feature>.py`

**Example:**
```python
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestLoginFlow:
    """Tests for user login flow using Selenium."""

    @pytest.fixture(scope="session")
    def driver(self):
        """Create Selenium WebDriver."""
        driver = webdriver.Chrome()
        yield driver
        driver.quit()

    @pytest.fixture
    def login_page(self, driver):
        """Navigate to login page."""
        driver.get("http://localhost:8000/login")
        yield driver

    @pytest.mark.selenium
    def test_login_with_valid_credentials(self, login_page):
        """Test login with valid credentials."""
        username_input = login_page.find_element(By.ID, "username")
        password_input = login_page.find_element(By.ID, "password")
        submit_button = login_page.find_element(By.CSS_SELECTOR, "button[type='submit']")

        username_input.send_keys("testuser")
        password_input.send_keys("correctpassword")
        submit_button.click()

        # Wait for redirect to dashboard
        WebDriverWait(login_page, 10).until(
            EC.presence_of_element_located((By.ID, "dashboard"))
        )

        assert "dashboard" in login_page.current_url

    @pytest.mark.selenium
    def test_login_with_invalid_credentials(self, login_page):
        """Test login error with invalid credentials."""
        username_input = login_page.find_element(By.ID, "username")
        password_input = login_page.find_element(By.ID, "password")
        submit_button = login_page.find_element(By.CSS_SELECTOR, "button[type='submit']")

        username_input.send_keys("testuser")
        password_input.send_keys("wrongpassword")
        submit_button.click()

        # Wait for error message
        error_msg = WebDriverWait(login_page, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "error-message"))
        )

        assert "Invalid credentials" in error_msg.text

    @pytest.mark.selenium
    @pytest.mark.slow
    def test_complete_user_workflow(self, driver):
        """Test complete user workflow through application."""
        # Login
        driver.get("http://localhost:8000/login")
        driver.find_element(By.ID, "username").send_keys("testuser")
        driver.find_element(By.ID, "password").send_keys("password")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Wait for dashboard
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dashboard"))
        )

        # Navigate to profile
        driver.find_element(By.ID, "profile-link").click()

        # Verify profile page loaded
        assert "profile" in driver.current_url

        # Logout
        driver.find_element(By.ID, "logout-button").click()

        # Should be back at login
        assert "login" in driver.current_url
```

**Marker:**
```python
@pytest.mark.selenium
def test_something():
    pass
```

---

## Coverage Requirements

### Minimum Coverage Targets

Coverage is measured by code coverage tools (pytest-cov) and enforced in CI/CD.

**By Repository Tier:**

| Tier | Minimum | Target | Repository Examples |
|------|---------|--------|---------------------|
| **Tier 1** (Production Critical) | 85% | 95%+ | digitalmodel, worldenergydata, assetutilities, teamresumes |
| **Tier 2** (Active Development) | 80% | 90%+ | aceengineercode, energy, frontierdeepwater, seanation, doris, saipem, rock-oil-field |
| **Tier 3** (Maintenance) | 80% | 85%+ | aceengineer-website, aceengineer-admin, hobbies, investments, ai-native-traditional-eng |
| **Personal** (Individual Projects) | 75% | 80%+ | All personal repositories |

### Coverage Exclusion Patterns

The following patterns are acceptable to exclude from coverage requirements:

```ini
# .coveragerc
[run]
source = src/
omit =
    */tests/*
    */venv/*
    */site-packages/*
    */__pycache__/*
    */migrations/*           # Database migrations
    */static/*               # Static assets
    */templates/*            # HTML templates
    */__main__.py           # CLI entry points (often simple)

[report]
precision = 2
show_missing = True
skip_covered = False

# Fail CI/CD if below threshold
fail_under = 80  # Tier 2/3 minimum

# Exclude specific lines with pragma
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstractmethod
```

### Coverage Enforcement in CI/CD

**GitHub Actions Example:**
```yaml
- name: Run tests with coverage
  run: |
    pytest --cov=src \
            --cov-report=xml \
            --cov-report=html \
            --cov-report=term \
            --cov-fail-under=80

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
    fail_ci_if_error: true
    flags: unittests
    name: codecov-umbrella
```

**Local Coverage Report:**
```bash
# Generate HTML report
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Generate summary
pytest --cov=src --cov-report=term-missing
```

---

## Test Markers Reference

### Standard Markers

All markers are defined in `pytest.ini`:

```ini
[tool:pytest]
markers =
    unit: Unit tests (isolated components)
    integration: Integration tests (component interactions)
    performance: Performance benchmark tests
    slow: Slow tests (>1 second execution time)
    llm: LLM/AI integration tests
    database: Database operation tests
    api: API endpoint tests
    etl: ETL pipeline tests
    scrapy: Web scraping tests
    selenium: Browser automation tests
    smoke: Quick smoke tests (critical path only)
    security: Security-related tests
```

### Using Markers

**Single Marker:**
```python
@pytest.mark.unit
def test_something():
    pass

@pytest.mark.slow
def test_long_operation():
    pass
```

**Multiple Markers:**
```python
@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.database
def test_database_performance():
    pass
```

**Run Tests by Marker:**
```bash
# Run only unit tests
pytest -m unit

# Run unit and integration tests
pytest -m "unit or integration"

# Run everything except slow tests
pytest -m "not slow"

# Run performance tests only
pytest -m performance

# Run LLM tests
pytest -m llm

# Skip LLM tests (for offline/CI testing)
pytest -m "not llm"

# Run integration tests that are not slow
pytest -m "integration and not slow"

# Run all database-related tests
pytest -m database
```

### Custom Repository Markers

Repositories can define additional markers specific to their domain:

```ini
# Additional markers for energy domain
markers =
    well_analysis: Well engineering analysis tests
    reservoir: Reservoir simulation tests
    production: Production forecast tests
    safety: Safety case evaluation tests
```

---

## Test Data Management

### Fixtures Organization

Fixtures should be organized by scope and purpose:

```python
# tests/conftest.py - Session-level fixtures

import pytest
from pathlib import Path
import json

# Session-scope fixtures (created once per test session)
@pytest.fixture(scope="session")
def test_data_dir():
    """Get path to test data directory."""
    return Path(__file__).parent / "fixtures"

@pytest.fixture(scope="session")
def config():
    """Load test configuration."""
    config_path = Path(__file__).parent / "fixtures" / "test_config.json"
    with open(config_path) as f:
        return json.load(f)

# Module-scope fixtures (created once per module)
@pytest.fixture(scope="module")
def database():
    """Create test database for module."""
    db = Database(":memory:")
    db.create_tables()
    yield db
    db.cleanup()

# Function-scope fixtures (created for each test function)
@pytest.fixture
def sample_data():
    """Provide sample data for testing."""
    return {
        "id": 1,
        "name": "Test Item",
        "value": 100.0
    }

@pytest.fixture
def mock_api_response(mocker):
    """Mock external API response."""
    mock = mocker.patch("requests.get")
    mock.return_value.json.return_value = {
        "status": "success",
        "data": [{"id": 1, "value": 100}]
    }
    return mock
```

### Fixture Locations

```
tests/
├── conftest.py                     # Global fixtures
├── unit/
│   ├── conftest.py                # Unit test fixtures
│   ├── fixtures/
│   │   └── sample_data.json
│   └── test_module.py
├── integration/
│   ├── conftest.py                # Integration test fixtures
│   ├── fixtures/
│   │   └── test_database.db
│   └── test_workflow.py
└── domain/
    ├── conftest.py                # Domain-specific fixtures
    └── test_llm_integration.py
```

### Factory Patterns vs Mocking

**When to Use Factories:**
- Creating complex test objects with many attributes
- Testing with multiple variations of similar objects
- Building realistic object graphs

```python
import factory
from src.models import User, Profile

class UserFactory(factory.Factory):
    """Factory for User objects."""
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    is_active = True
    profile = factory.SubFactory(ProfileFactory)

class ProfileFactory(factory.Factory):
    """Factory for Profile objects."""
    class Meta:
        model = Profile

    bio = "Test user bio"
    avatar_url = "http://example.com/avatar.jpg"

# Usage in tests
def test_user_creation():
    user = UserFactory(username="custom_user")
    assert user.username == "custom_user"
    assert user.profile is not None
```

**When to Use Mocking:**
- Isolating unit tests from external dependencies
- Simulating error conditions
- Testing error handling

```python
from unittest.mock import Mock, patch

def test_api_call_error_handling():
    mock_api = Mock()
    mock_api.get.side_effect = ConnectionError("Network error")

    with patch("src.api.client", mock_api):
        result = fetch_data()
        assert result["status"] == "error"
```

### Real Data vs Generated Data

**Use Real Data When:**
- Testing integration with real systems (databases, APIs)
- Data format/structure is important
- Performance characteristics depend on data shape

**Use Generated Data When:**
- Testing with large datasets
- Testing edge cases systematically
- Performance testing with parametrized sizes

```python
import factory_boy

# Real data from fixtures
def test_with_real_data(test_data_dir):
    with open(test_data_dir / "production_data.json") as f:
        data = json.load(f)
    result = process_data(data)
    assert result is not None

# Generated data for edge cases
@pytest.mark.parametrize("size", [0, 1, 100, 10000])
def test_with_generated_data(size):
    data = [{"id": i, "value": i * 1.5} for i in range(size)]
    result = process_data(data)
    assert len(result) == size
```

---

## Testing Best Practices

### Naming Conventions

**Test Functions:**
```python
# Pattern: test_<unit>_<action>_<expected_result>
def test_user_service_create_user_with_valid_email():
    """Test that create_user succeeds with valid email."""
    pass

def test_user_service_create_user_raises_error_with_invalid_email():
    """Test that create_user raises ValueError with invalid email."""
    pass

def test_data_pipeline_handles_large_datasets_efficiently():
    """Test that pipeline processes large datasets within time limit."""
    pass
```

**Test Classes:**
```python
# Pattern: Test<UnitBeingTested>
class TestUserService:
    """All tests for UserService class."""
    pass

class TestDataPipelineIntegration:
    """Integration tests for DataPipeline."""
    pass
```

### Test Organization by Module

Keep test structure parallel to source structure:

```
src/                           tests/
├── modules/                   ├── unit/
│   ├── user/                  │   ├── test_user_service.py
│   │   └── service.py         │   ├── test_user_validator.py
│   │   └── validator.py       │   ├── conftest.py
│   └── data/                  │   └── fixtures/
│       └── pipeline.py        └── integration/
│                                  ├── test_user_workflow.py
│                                  ├── test_data_flow.py
│                                  └── fixtures/
```

### Assertion Patterns

**Clear, Specific Assertions:**
```python
# ❌ Bad: Generic assertion
assert result

# ✅ Good: Specific assertion with context
assert result["status"] == "success", "Expected status to be 'success'"
assert len(result["items"]) == 5, f"Expected 5 items, got {len(result['items'])}"
assert result["timestamp"] is not None
```

**Multiple Assertions in Test:**
```python
def test_user_creation_returns_complete_object():
    """Test that user creation returns all required fields."""
    user = create_user("testuser", "test@example.com")

    # All assertions test one logical unit
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.created_at is not None
    assert user.is_active is True
```

**Using pytest Assertions:**
```python
def test_using_pytest_assertions():
    """Show pytest assertion capabilities."""
    data = [1, 2, 3, 4, 5]

    assert 3 in data
    assert data == [1, 2, 3, 4, 5]
    assert len(data) == 5
    assert all(x > 0 for x in data)

    with pytest.raises(ValueError, match="Invalid input"):
        validate_data("invalid")

    assert data != [5, 4, 3, 2, 1]
```

### Error Handling in Tests

**Testing Exceptions:**
```python
def test_validation_raises_error_on_invalid_input():
    """Test that validation raises appropriate error."""
    with pytest.raises(ValueError, match="Email must contain @"):
        validate_email("invalid-email")

def test_operation_raises_multiple_error_types():
    """Test handling of different error types."""
    with pytest.raises((ConnectionError, TimeoutError)):
        try_network_operation()

def test_exception_message_and_code():
    """Test exception details."""
    with pytest.raises(ValidationError) as exc_info:
        validate_data(invalid_data)

    assert "Invalid field" in str(exc_info.value)
    assert exc_info.value.code == "INVALID_FIELD"
```

### Test Independence

**Each test must be independent:**
```python
# ❌ Bad: Tests depend on execution order
def test_1_create_user():
    global user
    user = User(username="testuser")
    db.save(user)

def test_2_retrieve_user():
    retrieved = db.get_user(user.id)  # Depends on test_1
    assert retrieved.username == "testuser"

# ✅ Good: Each test creates its own data
@pytest.fixture
def user():
    """Create fresh user for each test."""
    user = User(username="testuser")
    db.save(user)
    yield user
    db.delete(user)

def test_create_user(user):
    assert user.id is not None

def test_retrieve_user(user):
    retrieved = db.get_user(user.id)
    assert retrieved.username == "testuser"
```

---

## CI/CD Integration

### GitHub Actions Configuration

**Full Testing Pipeline:**
```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install UV package manager
      run: |
        curl -LsSf https://astral.sh/uv/install.sh | sh

    - name: Install dependencies
      run: |
        uv pip install -r requirements.txt
        uv pip install pytest pytest-cov pytest-mock pytest-asyncio pytest-benchmark

    - name: Lint with flake8
      run: |
        pip install flake8
        flake8 src/ --max-line-length=100 --count --statistics

    - name: Run unit tests
      run: |
        pytest tests/unit/ -v --cov=src --cov-report=xml --cov-fail-under=80

    - name: Run integration tests
      run: |
        pytest tests/integration/ -v --cov=src --cov-report=xml --cov-append

    - name: Run performance tests
      if: github.event_name == 'push' && github.ref == 'refs/heads/main'
      run: |
        pytest tests/performance/ -v --benchmark-only

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: true

    - name: Generate coverage badge
      run: |
        coverage-badge -o coverage.svg -f

    - name: Comment PR with test results
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          const coverage = fs.readFileSync('coverage.txt', 'utf8');
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: `## Test Results\n\n${coverage}`
          });
```

### Parallel Test Execution

**Running Tests in Parallel:**
```bash
# Using pytest-xdist for parallel execution
pytest tests/ -n auto  # Auto-detect number of CPUs

# Specific number of workers
pytest tests/ -n 4

# With coverage (more complex)
pytest tests/ -n 4 --cov=src --cov-report=term
```

**pytest.ini Configuration:**
```ini
[tool:pytest]
# Run tests in parallel by default
addopts = -n auto --tb=short

# Test execution settings
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

### Coverage Reporting

**Generate Coverage Reports:**
```bash
# Terminal report
pytest --cov=src --cov-report=term-missing

# HTML report
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Multiple formats
pytest --cov=src \
       --cov-report=term \
       --cov-report=html \
       --cov-report=xml
```

### Test Failure Handling

**Stop on First Failure:**
```bash
pytest -x  # Stop on first failure

# Fail fast but run all first 10 failures
pytest --maxfail=10
```

**Rerun Failed Tests:**
```bash
pytest --lf   # Last failed
pytest --ff   # Failed first
pytest --cache-clear  # Clear cache
```

---

## Repository-Specific Adaptations

### Tier 1 Repositories (Production Critical)

**Repositories:** digitalmodel, worldenergydata, assetutilities, teamresumes

**Additional Requirements:**
- 85% minimum coverage (strict enforcement)
- All tests must pass before merge
- Performance tests on every commit
- Mutation testing (advanced feature)
- Property-based testing (advanced feature)

**Configuration (pyproject.toml):**
```toml
[tool.pytest.ini_options]
minversion = "7.0"
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
    "-n", "auto",
    "--cov=src",
    "--cov-fail-under=85",
    "--cov-report=html",
    "--cov-report=term",
    "--timeout=300",
    "-m", "not slow"  # Skip slow tests in local dev
]
testpaths = ["tests"]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "performance: Performance tests",
    "slow: Slow tests",
    "mutation: Mutation testing",
]

[tool.coverage.run]
source = ["src"]
branch = true
omit = ["*/tests/*", "*/venv/*"]

[tool.coverage.report]
fail_under = 85
precision = 2
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
]
```

**Mutation Testing (Advanced):**
```bash
pip install mutmut

# Run mutation tests
mutmut run --tests-dir tests/unit/

# Generate HTML report
mutmut html
```

**Property-Based Testing (Advanced):**
```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_sort_is_idempotent(data):
    """Test that sorting twice gives same result."""
    sorted_once = sort_data(data)
    sorted_twice = sort_data(sorted_once)
    assert sorted_once == sorted_twice

@given(st.emails())
def test_email_validation_accepts_valid_emails(email):
    """Test that validation accepts all valid emails."""
    assert is_valid_email(email)
```

### Tier 2 Repositories (Active Development)

**Repositories:** aceengineercode, energy, frontierdeepwater, seanation, doris, saipem, rock-oil-field

**Requirements:**
- 80% minimum coverage
- Standard pytest configuration
- Integration tests for workflows
- Optional performance tests

**Configuration (pyproject.toml):**
```toml
[tool.pytest.ini_options]
minversion = "7.0"
addopts = [
    "-v",
    "--tb=short",
    "-n", "auto",
    "--cov=src",
    "--cov-fail-under=80",
    "--cov-report=term",
    "--timeout=300",
]
testpaths = ["tests"]
```

### Tier 3 Repositories (Maintenance Mode)

**Repositories:** aceengineer-website, aceengineer-admin, hobbies, investments

**Requirements:**
- 80% minimum coverage
- Baseline pytest configuration
- Focus on regression testing
- Optional advanced features

**Minimal Configuration (pytest.ini):**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
addopts = -v --tb=short --cov=src --cov-fail-under=80
```

---

## Implementation Checklist

Use this checklist when setting up testing in a new repository or improving existing test coverage.

### Phase 1: Configuration Setup

- [ ] Create `tests/` directory with proper structure
- [ ] Create `tests/conftest.py` with global fixtures
- [ ] Create `pytest.ini` with markers and configuration
- [ ] Update `pyproject.toml` with pytest settings and dependencies
- [ ] Create `.coveragerc` with coverage configuration
- [ ] Add pytest to CI/CD pipeline (GitHub Actions)
- [ ] Configure coverage reporting to Codecov

### Phase 2: Test Organization

- [ ] Create `tests/unit/` with unit test template
- [ ] Create `tests/integration/` with integration test template
- [ ] Create `tests/performance/` with performance test template
- [ ] Create `tests/domain/` subdirectory for domain-specific tests
- [ ] Create `tests/fixtures/` for test data
- [ ] Add domain-specific test subdirectories as needed:
  - `test_llm_*.py` for LLM tests
  - `test_db_*.py` for database tests
  - `test_api_*.py` for API tests
  - `test_etl_*.py` for ETL tests

### Phase 3: Initial Test Writing

- [ ] Write unit tests for critical functions (TDD)
- [ ] Write integration tests for workflows
- [ ] Add parametrized tests for edge cases
- [ ] Create fixtures for common test data
- [ ] Write domain-specific tests if applicable
- [ ] Achieve minimum 80% coverage

### Phase 4: CI/CD Integration

- [ ] Add test step to GitHub Actions
- [ ] Configure coverage enforcement
- [ ] Setup coverage badge in README
- [ ] Configure test failure notifications
- [ ] Test parallel execution locally
- [ ] Verify performance benchmarks run correctly

### Phase 5: Documentation

- [ ] Document testing approach in repository README
- [ ] Add testing guidelines to CONTRIBUTING.md
- [ ] Document custom markers and fixtures
- [ ] Add examples of test patterns in code
- [ ] Link to workspace-hub testing standards

### Phase 6: Continuous Improvement

- [ ] Review test coverage weekly
- [ ] Identify and fix coverage gaps
- [ ] Optimize slow tests
- [ ] Refactor test fixtures for reusability
- [ ] Update tests when fixing bugs
- [ ] Maintain test documentation

---

## Troubleshooting

### Common Issues and Solutions

**Issue: Tests pass locally but fail in CI/CD**

**Causes:**
- Environment differences (Python version, dependencies)
- Timing-sensitive tests
- File path assumptions
- Database state issues

**Solutions:**
```bash
# Test with same Python version as CI
python3.11 -m pytest

# Run tests in deterministic order
pytest --randomly-dont-shuffle

# Check file paths are absolute
pytest -v --tb=long

# Isolate database state
pytest --forked  # If using pytest-forked
```

**Issue: Tests are too slow**

**Solutions:**
```bash
# Identify slow tests
pytest --durations=10  # Show 10 slowest tests

# Skip slow tests in development
pytest -m "not slow"

# Run only unit tests
pytest tests/unit/

# Use parallel execution
pytest -n auto
```

**Issue: Coverage not meeting minimum**

**Solutions:**
```bash
# Show which lines aren't covered
pytest --cov=src --cov-report=term-missing

# Generate HTML for detailed analysis
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Find coverage gaps by module
pytest --cov=src --cov-report=term-missing | grep -v "^src/.*100%"
```

**Issue: Flaky tests failing intermittently**

**Solutions:**
```bash
# Run test multiple times
pytest --count=10 tests/path/to/test.py

# Run with different random seed
pytest --randomly-seed=12345

# Check for timing dependencies
# Add pytest.mark.flaky and investigate
```

**Issue: Fixture conflicts or not working**

**Solutions:**
```python
# Debug fixture discovery
pytest --fixtures | grep fixture_name

# Check fixture scope
@pytest.fixture(scope="function")  # Not session
def my_fixture():
    pass

# Use fixture directly in test
def test_something(my_fixture):
    print(f"Fixture value: {my_fixture}")
```

---

## Repository-Specific Examples

### Example 1: Energy Domain Repository (worldenergydata)

**Test Structure:**
```
tests/
├── unit/
│   ├── test_bsee_parser.py          # BSEE data parsing
│   ├── test_production_calculator.py # Production calculations
│   └── fixtures/
│       └── sample_well_data.json
├── integration/
│   ├── test_bsee_workflow.py
│   └── fixtures/
│       └── test_database.db
└── domain/
    ├── test_etl_bsee_pipeline.py    # ETL tests
    ├── test_db_production_data.py    # Database tests
    └── test_llm_embeddings.py        # RAG embeddings
```

**Specific Markers:**
```python
@pytest.mark.parametrize("well_type,expected", [
    ("vertical", "standard"),
    ("deviated", "complex"),
    ("horizontal", "complex"),
])
def test_well_analysis_by_type(well_type, expected):
    pass
```

### Example 2: Marine Engineering Repository (frontierdeepwater)

**Test Structure:**
```
tests/
├── unit/
│   ├── test_stress_calculator.py
│   ├── test_buckling_analysis.py
│   └── test_fatigue_assessment.py
├── integration/
│   └── test_structural_analysis_workflow.py
└── domain/
    ├── test_db_structural_data.py
    └── test_api_analysis_results.py
```

**Custom Markers:**
```ini
markers =
    structural: Structural analysis tests
    stress: Stress analysis tests
    buckling: Buckling analysis tests
    fatigue: Fatigue analysis tests
```

### Example 3: Web Application Repository (aceengineer-website)

**Test Structure:**
```
tests/
├── unit/
│   ├── test_user_service.py
│   └── test_auth_service.py
├── integration/
│   └── test_user_workflow.py
└── domain/
    ├── test_api_users.py
    ├── test_api_products.py
    └── test_selenium_ui_flow.py
```

**Selenium Setup:**
```python
# tests/domain/conftest.py
@pytest.fixture(scope="session")
def selenium_driver():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()
```

---

## Advanced Features

### Property-Based Testing (Hypothesis)

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers(), min_size=1))
def test_sort_produces_sorted_list(unsorted):
    """Test that any list of integers can be sorted."""
    result = sort_data(unsorted)
    assert result == sorted(unsorted)

@given(st.text())
def test_email_validation_never_crashes(text):
    """Test that validation handles any input without crashing."""
    try:
        is_valid_email(text)
    except Exception as e:
        pytest.fail(f"Validation raised: {e}")
```

### Parametrized Testing

```python
@pytest.mark.parametrize("operation,a,b,expected", [
    ("add", 1, 2, 3),
    ("add", -1, -2, -3),
    ("add", 0, 0, 0),
    ("subtract", 5, 3, 2),
    ("multiply", 3, 4, 12),
    ("divide", 10, 2, 5),
])
def test_calculator(operation, a, b, expected):
    """Test calculator with multiple input combinations."""
    calc = Calculator()
    result = getattr(calc, operation)(a, b)
    assert result == expected
```

### Async Test Support

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test async functions."""
    result = await async_operation()
    assert result == expected

@pytest.mark.asyncio
async def test_async_with_timeout():
    """Test async with timeout."""
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(slow_operation(), timeout=1.0)
```

---

## Migration from Existing Tests

### Converting unittest to pytest

**Before (unittest):**
```python
import unittest

class TestUserService(unittest.TestCase):
    def setUp(self):
        self.service = UserService()

    def tearDown(self):
        self.service.cleanup()

    def test_create_user(self):
        user = self.service.create_user("testuser")
        self.assertEqual(user.username, "testuser")

    def test_invalid_username(self):
        with self.assertRaises(ValueError):
            self.service.create_user("")

if __name__ == '__main__':
    unittest.main()
```

**After (pytest):**
```python
import pytest
from src.user_service import UserService

@pytest.fixture
def service():
    svc = UserService()
    yield svc
    svc.cleanup()

def test_create_user(service):
    user = service.create_user("testuser")
    assert user.username == "testuser"

def test_invalid_username(service):
    with pytest.raises(ValueError):
        service.create_user("")
```

---

## References and Resources

### Documentation
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [pytest-benchmark Documentation](https://pytest-benchmark.readthedocs.io/)
- [Hypothesis Testing](https://hypothesis.readthedocs.io/)
- [Factory Boy](https://factoryboy.readthedocs.io/)

### Related Workspace Hub Documentation
- [File Organization Standards](docs/modules/standards/FILE_ORGANIZATION_STANDARDS.md)
- [Development Workflow](docs/modules/workflow/DEVELOPMENT_WORKFLOW.md)
- [HTML Reporting Standards](docs/modules/standards/HTML_REPORTING_STANDARDS.md)
- [Logging Standards](docs/modules/standards/LOGGING_STANDARDS.md)

### Tools
- **pytest:** Test framework - https://pytest.org/
- **pytest-cov:** Coverage plugin - https://pytest-cov.readthedocs.io/
- **pytest-mock:** Mocking support - https://pytest-mock.readthedocs.io/
- **pytest-benchmark:** Performance benchmarking - https://pytest-benchmark.readthedocs.io/
- **Hypothesis:** Property-based testing - https://hypothesis.readthedocs.io/
- **Factory Boy:** Test data generation - https://factoryboy.readthedocs.io/
- **Selenium:** Browser automation - https://www.selenium.dev/
- **Scrapy:** Web scraping - https://scrapy.org/

---

## Compliance and Enforcement

### Pre-Commit Hook

```bash
#!/bin/bash
# .githooks/pre-commit

set -e

# Run tests
pytest tests/ -v --tb=short

# Check coverage
pytest --cov=src --cov-fail-under=80

echo "✓ All tests passed"
```

### PR Merge Requirements

Pull requests cannot be merged without:
- ✅ All tests passing
- ✅ Minimum coverage met (80% for Tier 2/3, 85% for Tier 1)
- ✅ Coverage not decreased from main branch
- ✅ CI/CD pipeline green
- ✅ Code review approval

### Non-Compliance Consequences

- Tier 1 repos (digitalmodel, worldenergydata, etc.): PR blocked immediately
- Tier 2 repos: Warning → 48-hour remediation window → Forced merge if not fixed
- Tier 3 repos: Advisory → Tracked for improvement → No hard block

---

## Summary

This comprehensive testing framework ensures:

✅ **Consistency** across all 25+ repositories
✅ **Quality** with minimum 80% coverage, target 90%+
✅ **Efficiency** through organized test types and CI/CD automation
✅ **Flexibility** with domain-specific test categories
✅ **Maintainability** with clear organization and documentation
✅ **Progressiveness** with tiered requirements by repository importance

**Implementation Priority:**
1. **Phase 1:** Setup pytest configuration and basic structure
2. **Phase 2:** Write unit and integration tests (TDD)
3. **Phase 3:** Add CI/CD integration and coverage reporting
4. **Phase 4:** Implement domain-specific tests as applicable
5. **Phase 5:** Achieve coverage targets and continuous improvement

---

**Version:** 1.0.0
**Last Updated:** 2026-01-13
**Status:** Mandatory for all repositories
**Next Review:** 2026-04-13
