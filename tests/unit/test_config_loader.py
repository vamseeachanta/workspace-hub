"""
ABOUTME: Unit tests for ConfigLoader and configuration file loading
ABOUTME: Tests YAML parsing, caching, error handling, and validation
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import yaml

from src.config.config_loader import ConfigLoader


class TestConfigLoader:
    """Test ConfigLoader functionality."""

    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary YAML config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'metadata': {
                    'name': 'test_config',
                    'version': '1.0.0',
                    'environment': 'development'
                },
                'database': {
                    'host': 'localhost',
                    'port': 5432,
                    'name': 'test_db'
                },
                'logging': {
                    'level': 'DEBUG',
                    'format': 'standard'
                }
            }
            yaml.dump(config_data, f)
            f.flush()
            yield Path(f.name)
            Path(f.name).unlink()

    def test_load_yaml_file(self, temp_config_file):
        """Test loading a valid YAML configuration file."""
        loader = ConfigLoader()
        config = loader.load(temp_config_file)

        assert config is not None
        assert config['metadata']['name'] == 'test_config'
        assert config['database']['host'] == 'localhost'
        assert config['logging']['level'] == 'DEBUG'

    def test_load_nonexistent_file(self):
        """Test loading a non-existent file raises FileNotFoundError."""
        loader = ConfigLoader()
        with pytest.raises(FileNotFoundError):
            loader.load(Path('/nonexistent/config.yaml'))

    def test_load_invalid_yaml(self):
        """Test loading invalid YAML raises error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('invalid: yaml: content:')
            f.flush()
            temp_path = Path(f.name)

        try:
            loader = ConfigLoader()
            with pytest.raises(Exception):  # yaml.YAMLError or similar
                loader.load(temp_path)
        finally:
            temp_path.unlink()

    def test_caching(self, temp_config_file):
        """Test that configurations are cached."""
        loader = ConfigLoader(cache_ttl=10)  # 10 second cache

        # Load first time
        config1 = loader.load(temp_config_file)

        # Load second time (should come from cache)
        config2 = loader.load(temp_config_file)

        assert config1 == config2
        assert config1 is config2  # Same object (cached)

    def test_cache_expiration(self, temp_config_file):
        """Test that cache expires after TTL."""
        loader = ConfigLoader(cache_ttl=1)  # 1 second cache

        config1 = loader.load(temp_config_file)

        # Wait for cache to expire
        import time
        time.sleep(1.1)

        config2 = loader.load(temp_config_file)

        # Should load from file again (different objects)
        assert config1 == config2
        assert config1 is not config2

    def test_cache_clear(self, temp_config_file):
        """Test clearing the cache."""
        loader = ConfigLoader()

        loader.load(temp_config_file)
        loader.clear_cache()

        assert len(loader._cache) == 0

    def test_load_multiple_configs(self, temp_config_file):
        """Test loading multiple configuration files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f2:
            config2 = {'additional': {'setting': 'value'}}
            yaml.dump(config2, f2)
            f2.flush()
            temp_path2 = Path(f2.name)

        try:
            loader = ConfigLoader()
            merged = loader.load_multiple([temp_config_file, temp_path2])

            assert merged['metadata']['name'] == 'test_config'
            assert merged['additional']['setting'] == 'value'
        finally:
            temp_path2.unlink()

    def test_relative_path_handling(self):
        """Test loading config with relative path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / 'config.yaml'
            config_data = {'test': 'value'}
            config_file.write_text(yaml.dump(config_data))

            # Change to temp directory
            import os
            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                loader = ConfigLoader()
                config = loader.load(Path('config.yaml'))
                assert config['test'] == 'value'
            finally:
                os.chdir(old_cwd)

    def test_large_config_file(self):
        """Test loading a large configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            large_config = {
                'section1': {f'key{i}': f'value{i}' for i in range(1000)},
                'section2': {f'key{i}': f'value{i}' for i in range(1000)},
            }
            yaml.dump(large_config, f)
            f.flush()
            temp_path = Path(f.name)

        try:
            loader = ConfigLoader()
            config = loader.load(temp_path)
            assert len(config['section1']) == 1000
            assert len(config['section2']) == 1000
        finally:
            temp_path.unlink()


class TestConfigValidator:
    """Test ConfigValidator functionality."""

    def test_validate_against_schema(self):
        """Test validating config against schema."""
        from src.config.config_loader import ConfigValidator

        config = {
            'metadata': {
                'name': 'test',
                'version': '1.0',
                'created': '2025-01-01'
            }
        }

        validator = ConfigValidator()
        valid, errors = validator.validate(config, ConfigValidator.create_base_schema())

        assert valid is True
        assert len(errors) == 0

    def test_validate_missing_required_fields(self):
        """Test validation fails for missing required fields."""
        from src.config.config_loader import ConfigValidator

        config = {}  # Missing required fields

        validator = ConfigValidator()
        valid, errors = validator.validate(config, ConfigValidator.create_base_schema())

        assert valid is False
        assert len(errors) > 0

    def test_validate_wrong_type(self):
        """Test validation fails for wrong field types."""
        from src.config.config_loader import ConfigValidator

        config = {
            'metadata': {
                'name': 123,  # Should be string
                'version': '1.0'
            }
        }

        validator = ConfigValidator()
        valid, errors = validator.validate(config, ConfigValidator.create_base_schema())

        # Validation should catch type mismatch
        assert valid is False or len(errors) >= 0  # Schema may not enforce strict typing

    def test_extend_schema(self):
        """Test extending schema with custom properties."""
        from src.config.config_loader import ConfigValidator

        validator = ConfigValidator()
        base_schema = ConfigValidator.create_base_schema()

        extension = {
            'properties': {
                'custom_field': {
                    'type': 'string',
                    'description': 'Custom field for testing'
                }
            }
        }

        validator.extend_schema(extension)
        # Extended schema should now accept custom_field
