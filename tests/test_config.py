"""
Unit tests for the Config class.
"""

import unittest
import tempfile
import os
import json
from detection_agent.config import Config


class TestConfig(unittest.TestCase):
    """Test cases for the Config class."""
    
    def test_default_config(self):
        """Test default configuration initialization."""
        config = Config()
        
        # Test default values
        self.assertEqual(config.get("detection_interval"), 30)
        self.assertEqual(config.get("max_threads"), 4)
        self.assertEqual(config.get("log_level"), "INFO")
        self.assertEqual(config.get("output_format"), "json")
        self.assertEqual(config.get("enabled_detectors"), ["file", "network", "process"])
    
    def test_get_with_default(self):
        """Test getting configuration values with defaults."""
        config = Config()
        
        # Test existing key
        self.assertEqual(config.get("detection_interval"), 30)
        
        # Test non-existing key with default
        self.assertEqual(config.get("non_existing_key", "default_value"), "default_value")
        
        # Test non-existing key without default
        self.assertIsNone(config.get("non_existing_key"))
    
    def test_set_config(self):
        """Test setting configuration values."""
        config = Config()
        
        config.set("detection_interval", 60)
        self.assertEqual(config.get("detection_interval"), 60)
        
        config.set("new_key", "new_value")
        self.assertEqual(config.get("new_key"), "new_value")
    
    def test_get_all(self):
        """Test getting all configuration values."""
        config = Config()
        all_config = config.get_all()
        
        self.assertIsInstance(all_config, dict)
        self.assertIn("detection_interval", all_config)
        self.assertIn("max_threads", all_config)
        self.assertIn("log_level", all_config)
        
        # Test that it returns a copy
        all_config["new_key"] = "new_value"
        self.assertNotIn("new_key", config.get_all())
    
    def test_load_from_file(self):
        """Test loading configuration from a file."""
        test_config = {
            "detection_interval": 45,
            "log_level": "DEBUG",
            "custom_setting": "test_value"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_config, f)
            config_file = f.name
        
        try:
            config = Config(config_file)
            
            # Test that custom values override defaults
            self.assertEqual(config.get("detection_interval"), 45)
            self.assertEqual(config.get("log_level"), "DEBUG")
            self.assertEqual(config.get("custom_setting"), "test_value")
            
            # Test that unspecified defaults remain
            self.assertEqual(config.get("max_threads"), 4)
            
        finally:
            os.unlink(config_file)
    
    def test_load_from_nonexistent_file(self):
        """Test loading from a non-existent file uses defaults."""
        config = Config("nonexistent_file.json")
        
        # Should use default values
        self.assertEqual(config.get("detection_interval"), 30)
        self.assertEqual(config.get("log_level"), "INFO")
    
    def test_load_invalid_json(self):
        """Test loading invalid JSON file raises ValueError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            config_file = f.name
        
        try:
            config = Config()
            with self.assertRaises(ValueError):
                config.load_from_file(config_file)
                
        finally:
            os.unlink(config_file)
    
    def test_validate_valid_config(self):
        """Test validation of valid configuration."""
        config = Config()
        self.assertTrue(config.validate())
    
    def test_validate_invalid_detection_interval(self):
        """Test validation fails with invalid detection_interval."""
        config = Config()
        
        # Test negative value
        config.set("detection_interval", -1)
        self.assertFalse(config.validate())
        
        # Test zero value
        config.set("detection_interval", 0)
        self.assertFalse(config.validate())
        
        # Test non-integer value
        config.set("detection_interval", "invalid")
        self.assertFalse(config.validate())
    
    def test_validate_invalid_max_threads(self):
        """Test validation fails with invalid max_threads."""
        config = Config()
        
        # Test negative value
        config.set("max_threads", -1)
        self.assertFalse(config.validate())
        
        # Test zero value
        config.set("max_threads", 0)
        self.assertFalse(config.validate())
        
        # Test non-integer value
        config.set("max_threads", "invalid")
        self.assertFalse(config.validate())
    
    def test_validate_invalid_log_level(self):
        """Test validation fails with invalid log_level."""
        config = Config()
        
        config.set("log_level", "INVALID")
        self.assertFalse(config.validate())
        
        # Test valid log levels
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in valid_levels:
            config.set("log_level", level)
            self.assertTrue(config.validate())
    
    def test_validate_missing_required_keys(self):
        """Test validation fails with missing required keys."""
        config = Config()
        
        # Remove a required key
        config._config.pop("detection_interval")
        self.assertFalse(config.validate())


if __name__ == '__main__':
    unittest.main()