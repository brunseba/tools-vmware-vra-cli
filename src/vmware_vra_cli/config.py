"""Configuration management for VMware vRA CLI

This module handles persistent configuration storage and retrieval for the CLI,
including API URL, tenant, domain, and other settings.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console

console = Console()


class ConfigManager:
    """Manages persistent configuration for the VMware vRA CLI."""
    
    # Default configuration values
    DEFAULT_CONFIG = {
        "api_url": "https://vra.example.com",
        "tenant": "vsphere.local",
        "domain": None,
        "verify_ssl": True,
        "timeout": 30,
        "output_format": "table"
    }
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize configuration manager.
        
        Args:
            config_dir: Custom configuration directory path
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # Default to user's home directory
            self.config_dir = Path.home() / ".vmware-vra-cli"
        
        self.config_file = self.config_dir / "config.json"
        self._ensure_config_dir()
    
    def _ensure_config_dir(self) -> None:
        """Ensure the configuration directory exists."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            console.print(f"[yellow]Warning: Could not create config directory: {e}[/yellow]")
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file and environment variables.
        
        Returns:
            Combined configuration dictionary
        """
        # Start with defaults
        config = self.DEFAULT_CONFIG.copy()
        
        # Override with file-based config
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    config.update(file_config)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load config file: {e}[/yellow]")
        
        # Override with environment variables
        env_overrides = {
            "api_url": os.getenv("VRA_URL"),
            "tenant": os.getenv("VRA_TENANT"), 
            "domain": os.getenv("VRA_DOMAIN"),
            "verify_ssl": os.getenv("VRA_VERIFY_SSL"),
            "timeout": os.getenv("VRA_TIMEOUT"),
            "output_format": os.getenv("VRA_OUTPUT_FORMAT")
        }
        
        for key, value in env_overrides.items():
            if value is not None:
                # Handle boolean conversion for verify_ssl
                if key == "verify_ssl":
                    config[key] = value.lower() == "true"
                elif key == "timeout":
                    try:
                        config[key] = int(value)
                    except ValueError:
                        console.print(f"[yellow]Warning: Invalid timeout value: {value}[/yellow]")
                else:
                    config[key] = value
        
        return config
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file.
        
        Args:
            config: Configuration dictionary to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Filter out None values and environment-only settings
            filtered_config = {
                k: v for k, v in config.items() 
                if v is not None and k not in ["timeout"]  # timeout is often env-specific
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(filtered_config, f, indent=2)
            return True
        except Exception as e:
            console.print(f"[yellow]Warning: Could not save config file: {e}[/yellow]")
            return False
    
    def update_config(self, **updates) -> Dict[str, Any]:
        """Update configuration with new values and save.
        
        Args:
            **updates: Configuration keys and values to update
            
        Returns:
            Updated configuration dictionary
        """
        config = self.load_config()
        config.update(updates)
        
        # Save to file
        self.save_config(config)
        
        return config
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a specific configuration value.
        
        Args:
            key: Configuration key to retrieve
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        config = self.load_config()
        return config.get(key, default)
    
    def set_config_value(self, key: str, value: Any) -> None:
        """Set a specific configuration value and save.
        
        Args:
            key: Configuration key to set
            value: Value to set
        """
        # Check if this setting will be overridden by environment variable
        env_mapping = {
            "api_url": "VRA_URL",
            "tenant": "VRA_TENANT", 
            "domain": "VRA_DOMAIN",
            "verify_ssl": "VRA_VERIFY_SSL",
            "timeout": "VRA_TIMEOUT",
            "output_format": "VRA_OUTPUT_FORMAT"
        }
        
        env_key = env_mapping.get(key)
        if env_key and os.getenv(env_key):
            console.print(f"[yellow]⚠️  Warning: Setting '{key}' will be overridden by environment variable '{env_key}'[/yellow]")
            console.print(f"[yellow]   Current env value: {os.getenv(env_key)}[/yellow]")
            console.print(f"[yellow]   To use the config file value, unset the environment variable: unset {env_key}[/yellow]")
        
        self.update_config(**{key: value})
    
    def reset_config(self) -> Dict[str, Any]:
        """Reset configuration to defaults.
        
        Returns:
            Reset configuration dictionary
        """
        # Remove config file if it exists
        if self.config_file.exists():
            try:
                self.config_file.unlink()
            except Exception as e:
                console.print(f"[yellow]Warning: Could not remove config file: {e}[/yellow]")
        
        return self.DEFAULT_CONFIG.copy()
    
    def show_config(self) -> Dict[str, Any]:
        """Show current configuration including sources.
        
        Returns:
            Current configuration dictionary
        """
        return self.load_config()
    
    def get_config_file_path(self) -> Path:
        """Get the path to the configuration file.
        
        Returns:
            Path to configuration file
        """
        return self.config_file


# Global config manager instance
config_manager = ConfigManager()


def get_config() -> Dict[str, Any]:
    """Get current configuration.
    
    Returns:
        Current configuration dictionary
    """
    return config_manager.load_config()


def update_config(**updates) -> Dict[str, Any]:
    """Update configuration with new values.
    
    Args:
        **updates: Configuration keys and values to update
        
    Returns:
        Updated configuration dictionary
    """
    return config_manager.update_config(**updates)


def save_login_config(api_url: str, tenant: Optional[str] = None, domain: Optional[str] = None) -> None:
    """Save login configuration parameters.
    
    Args:
        api_url: API URL to save
        tenant: Tenant to save (optional)
        domain: Domain to save (optional)
    """
    updates = {"api_url": api_url}
    
    if tenant:
        updates["tenant"] = tenant
    
    if domain:
        updates["domain"] = domain
    
    config_manager.update_config(**updates)
