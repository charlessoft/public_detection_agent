"""
Configuration management for the detection agent.
"""

import json
import os
from typing import Dict, Any, Optional


class Config:
    """Configuration manager for detection agent settings."""
    
    DEFAULT_CONFIG = {
        "detection_interval": 30,
        "max_threads": 4,
        "log_level": "INFO",
        "output_format": "json",
        "enabled_detectors": ["file", "network", "process"]
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to configuration file. If None, uses defaults.
        """
        self._config = self.DEFAULT_CONFIG.copy()
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)
    
    def load_from_file(self, config_file: str) -> None:
        """
        Load configuration from a JSON file.
        
        Args:
            config_file: Path to the configuration file.
            
        Raises:
            FileNotFoundError: If config file doesn't exist.
            ValueError: If config file is invalid JSON.
        """
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
                self._config.update(file_config)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key.
            default: Default value if key not found.
            
        Returns:
            Configuration value or default.
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key.
            value: Value to set.
        """
        self._config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.
        
        Returns:
            Dictionary of all configuration values.
        """
        return self._config.copy()
    
    def validate(self) -> bool:
        """
        Validate the current configuration.
        
        Returns:
            True if configuration is valid, False otherwise.
        """
        required_keys = ["detection_interval", "max_threads", "log_level"]
        
        for key in required_keys:
            if key not in self._config:
                return False
        
        # Validate specific values
        if not isinstance(self._config["detection_interval"], int) or self._config["detection_interval"] <= 0:
            return False
        
        if not isinstance(self._config["max_threads"], int) or self._config["max_threads"] <= 0:
            return False
        
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self._config["log_level"] not in valid_log_levels:
            return False
        
        return True