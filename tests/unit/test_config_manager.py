"""
ABOUTME: Unit tests for ConfigManager and configuration access patterns
ABOUTME: Tests dot-notation access, configuration sections, and state management
"""

import pytest
import tempfile
from pathlib import Path
import yaml

from src.config.config_manager import ConfigManager


class TestConfigManager:
    """Test ConfigManager unified interface."""

    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'metadata': {
                    'name': 'test_app',
                    'version': '1.0.0'
                },
                'database': {
                    'host': 'localhost',
                    'port': 5432,
                    'credentials': {
                        'username': 'admin',
                        'password': 'secret'
                    }
                },
                'logging': {
                    'level': 'INFO',
                    'handlers': ['console', 'file']
                }
            }
            yaml.dump(config_data, f)
            f.flush()
            yield Path(f.name)
            Path(f.name).unlink()

    def test_load_configuration(self, temp_config_file):
        """Test loading configuration from file."""
        manager = ConfigManager()
        success = manager.load_config(temp_config_file)

        assert success is True

    def test_get_value_by_key(self, temp_config_file):
        """Test retrieving values using dot notation."""
        manager = ConfigManager()
        manager.load_config(temp_config_file)

        # Test nested access
        assert manager.get('metadata.name') == 'test_app'
        assert manager.get('database.host') == 'localhost'
        assert manager.get('database.port') == 5432
        assert manager.get('database.credentials.username') == 'admin'

    def test_get_with_default(self, temp_config_file):
        """Test retrieving non-existent value with default."""
        manager = ConfigManager()
        manager.load_config(temp_config_file)

        value = manager.get('nonexistent.key', default='default_value')
        assert value == 'default_value'

    def test_set_value(self, temp_config_file):
        """Test setting configuration values."""
        manager = ConfigManager()
        manager.load_config(temp_config_file)

        manager.set('database.new_field', 'new_value')
        assert manager.get('database.new_field') == 'new_value'

    def test_set_nested_value(self, temp_config_file):
        """Test setting nested configuration values."""
        manager = ConfigManager()
        manager.load_config(temp_config_file)

        manager.set('new_section.nested.deep', 'deep_value')
        assert manager.get('new_section.nested.deep') == 'deep_value'

    def test_get_section(self, temp_config_file):
        """Test retrieving entire configuration section."""
        manager = ConfigManager()
        manager.load_config(temp_config_file)

        database_config = manager.get_section('database')
        assert database_config['host'] == 'localhost'
        assert database_config['port'] == 5432
        assert 'credentials' in database_config

    def test_get_nonexistent_section(self, temp_config_file):
        """Test getting non-existent section returns empty dict."""
        manager = ConfigManager()
        manager.load_config(temp_config_file)

        section = manager.get_section('nonexistent')
        assert section == {}

    def test_validate_configuration(self, temp_config_file):
        """Test configuration validation."""
        manager = ConfigManager()
        manager.load_config(temp_config_file)

        valid, errors = manager.validate()
        # Should be valid as we're loading from known good config
        assert valid is True or len(errors) == 0

    def test_reload_configuration(self, temp_config_file):
        """Test reloading configuration clears cache."""
        manager = ConfigManager()
        manager.load_config(temp_config_file)

        old_value = manager.get('metadata.name')

        # Reload should clear cache and reload
        manager.reload(temp_config_file)

        new_value = manager.get('metadata.name')
        assert old_value == new_value

    def test_configuration_persistence(self, temp_config_file):
        """Test that configuration changes persist during session."""
        manager = ConfigManager()
        manager.load_config(temp_config_file)

        manager.set('test_key', 'test_value')
        assert manager.get('test_key') == 'test_value'

        manager.set('test_key', 'updated_value')
        assert manager.get('test_key') == 'updated_value'

    def test_list_sections(self, temp_config_file):
        """Test listing top-level configuration sections."""
        manager = ConfigManager()
        manager.load_config(temp_config_file)

        # Should have access to configuration sections
        assert manager.get('metadata') is not None
        assert manager.get('database') is not None
        assert manager.get('logging') is not None

    def test_overwrite_existing_value(self, temp_config_file):
        """Test overwriting existing configuration values."""
        manager = ConfigManager()
        manager.load_config(temp_config_file)

        original = manager.get('database.host')
        assert original == 'localhost'

        manager.set('database.host', 'remote.example.com')
        assert manager.get('database.host') == 'remote.example.com'

    def test_empty_configuration(self):
        """Test working with empty configuration."""
        manager = ConfigManager()

        # Should handle empty config gracefully
        manager.set('initial_key', 'initial_value')
        assert manager.get('initial_key') == 'initial_value'

    def test_list_all_keys(self, temp_config_file):
        """Test retrieving all configuration keys."""
        manager = ConfigManager()
        manager.load_config(temp_config_file)

        # Get all top-level keys
        config = manager.config
        assert 'metadata' in config
        assert 'database' in config
        assert 'logging' in config

    def test_configuration_type_preservation(self, temp_config_file):
        """Test that configuration value types are preserved."""
        manager = ConfigManager()
        manager.load_config(temp_config_file)

        # Verify types
        assert isinstance(manager.get('database.port'), int)
        assert isinstance(manager.get('metadata.name'), str)
        assert isinstance(manager.get('logging.handlers'), list)

    def test_special_characters_in_values(self):
        """Test handling special characters in configuration values."""
        manager = ConfigManager()

        special_value = 'value with !@#$%^&*() special chars'
        manager.set('special.key', special_value)

        assert manager.get('special.key') == special_value

    def test_load_invalid_file(self):
        """Test loading invalid configuration file."""
        manager = ConfigManager()

        with pytest.raises(FileNotFoundError):
            manager.load_config(Path('/nonexistent/file.yaml'))

    def test_configuration_isolation(self):
        """Test that multiple managers don't share configuration."""
        manager1 = ConfigManager()
        manager2 = ConfigManager()

        manager1.set('test_key', 'value1')
        manager2.set('test_key', 'value2')

        assert manager1.get('test_key') == 'value1'
        assert manager2.get('test_key') == 'value2'
