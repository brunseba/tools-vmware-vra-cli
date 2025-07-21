"""Tests for the Configuration module."""

import pytest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from vmware_vra_cli.config import ConfigManager, get_config, update_config, save_login_config, config_manager


class TestConfigManager:
    """Test cases for ConfigManager class."""
    
    def test_init_default_config_path(self):
        """Test ConfigManager initialization with default config path."""
        with patch('vmware_vra_cli.config.Path.home') as mock_home:
            mock_home.return_value = Path('/home/testuser')
            manager = ConfigManager()
            expected_path = Path('/home/testuser/.vmware-vra-cli')
            assert manager.config_dir == expected_path
    
    def test_init_custom_config_path(self):
        """Test ConfigManager initialization with custom config path."""
        custom_path = "/custom/path"
        manager = ConfigManager(Path(custom_path))
        assert manager.config_dir == Path(custom_path)
    
    def test_default_config_values(self):
        """Test default configuration values."""
        expected_defaults = {
            "api_url": "https://vra.example.com",
            "tenant": "vsphere.local",
            "domain": None,
            "verify_ssl": True,
            "timeout": 30,
            "output_format": "table"
        }
        
        assert ConfigManager.DEFAULT_CONFIG == expected_defaults
    
    def test_load_config_defaults(self):
        """Test loading config returns defaults when no file exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(Path(temp_dir))
            config = manager.load_config()
            
            assert config["api_url"] == "https://vra.example.com"
            assert config["tenant"] == "vsphere.local"
            assert config["verify_ssl"] is True
    
    def test_load_config_from_file(self):
        """Test loading config from file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            config_file = config_dir / "config.json"
            
            # Create test config file
            test_config = {
                "api_url": "https://test.example.com",
                "tenant": "test.tenant"
            }
            
            with open(config_file, 'w') as f:
                json.dump(test_config, f)
            
            manager = ConfigManager(config_dir)
            config = manager.load_config()
            
            assert config["api_url"] == "https://test.example.com"
            assert config["tenant"] == "test.tenant"
            # Should still have defaults for other values
            assert config["verify_ssl"] is True
    
    @patch.dict(os.environ, {"VRA_URL": "https://env.example.com", "VRA_VERIFY_SSL": "false"})
    def test_load_config_from_environment(self):
        """Test loading config with environment variable overrides."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(Path(temp_dir))
            config = manager.load_config()
            
            assert config["api_url"] == "https://env.example.com"
            assert config["verify_ssl"] is False
    
    def test_save_config_success(self):
        """Test successful config saving."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(Path(temp_dir))
            test_config = {"api_url": "https://saved.example.com"}
            
            result = manager.save_config(test_config)
            
            assert result is True
            assert manager.config_file.exists()
            
            # Verify saved content
            with open(manager.config_file, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data["api_url"] == "https://saved.example.com"
    
    def test_update_config(self):
        """Test updating configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(Path(temp_dir))
            
            updated_config = manager.update_config(
                api_url="https://updated.example.com",
                tenant="updated.tenant"
            )
            
            assert updated_config["api_url"] == "https://updated.example.com"
            assert updated_config["tenant"] == "updated.tenant"
    
    def test_get_config_value(self):
        """Test getting specific config value."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(Path(temp_dir))
            
            value = manager.get_config_value("verify_ssl")
            assert value is True
            
            default_value = manager.get_config_value("nonexistent", "default")
            assert default_value == "default"
    
    def test_set_config_value(self):
        """Test setting specific config value."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(Path(temp_dir))
            
            manager.set_config_value("api_url", "https://set.example.com")
            
            config = manager.load_config()
            assert config["api_url"] == "https://set.example.com"
    
    @patch.dict(os.environ, {"VRA_URL": "https://env.example.com"})
    @patch('vmware_vra_cli.config.console')
    def test_set_config_value_with_env_warning(self, mock_console):
        """Test setting config value warns when env variable exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(Path(temp_dir))
            
            manager.set_config_value("api_url", "https://set.example.com")
            
            # Should print warning about environment override
            mock_console.print.assert_called()
            warning_calls = [call.args[0] for call in mock_console.print.call_args_list]
            assert any("Warning" in str(call) for call in warning_calls)
    
    def test_reset_config(self):
        """Test resetting configuration to defaults."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(Path(temp_dir))
            
            # Create a config file
            manager.update_config(api_url="https://temp.example.com")
            assert manager.config_file.exists()
            
            # Reset config
            reset_config = manager.reset_config()
            
            # File should be removed
            assert not manager.config_file.exists()
            
            # Should return defaults
            assert reset_config == ConfigManager.DEFAULT_CONFIG


class TestConfigFunctions:
    """Test cases for module-level config functions."""
    
    @patch.object(config_manager, 'load_config')
    def test_get_config(self, mock_load):
        """Test get_config function."""
        mock_load.return_value = {"test": "value"}
        
        result = get_config()
        
        mock_load.assert_called_once()
        assert result == {"test": "value"}
    
    @patch.object(config_manager, 'update_config')
    def test_update_config(self, mock_update):
        """Test update_config function."""
        mock_update.return_value = {"updated": "config"}
        
        result = update_config(api_url="https://test.com")
        
        mock_update.assert_called_once_with(api_url="https://test.com")
        assert result == {"updated": "config"}
    
    @patch.object(config_manager, 'update_config')
    def test_save_login_config_all_params(self, mock_update):
        """Test save_login_config with all parameters."""
        save_login_config(
            api_url="https://login.example.com",
            tenant="login.tenant",
            domain="login.domain"
        )
        
        mock_update.assert_called_once_with(
            api_url="https://login.example.com",
            tenant="login.tenant",
            domain="login.domain"
        )
    
    @patch.object(config_manager, 'update_config')
    def test_save_login_config_minimal_params(self, mock_update):
        """Test save_login_config with minimal parameters."""
        save_login_config(api_url="https://minimal.example.com")
        
        mock_update.assert_called_once_with(
            api_url="https://minimal.example.com"
        )


class TestConfigIntegration:
    """Integration tests for configuration management."""
    
    def test_full_config_workflow(self):
        """Test complete configuration workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(Path(temp_dir))
            
            # Step 1: Load initial config (should be defaults)
            config = manager.load_config()
            assert config["api_url"] == "https://vra.example.com"
            
            # Step 2: Update configuration
            updated_config = manager.update_config(
                api_url="https://workflow.example.com",
                tenant="workflow.tenant"
            )
            
            assert updated_config["api_url"] == "https://workflow.example.com"
            assert updated_config["tenant"] == "workflow.tenant"
            
            # Step 3: Verify file was saved
            assert manager.config_file.exists()
            
            # Step 4: Create new manager instance and verify persistence
            new_manager = ConfigManager(Path(temp_dir))
            reloaded_config = new_manager.load_config()
            
            assert reloaded_config["api_url"] == "https://workflow.example.com"
            assert reloaded_config["tenant"] == "workflow.tenant"
