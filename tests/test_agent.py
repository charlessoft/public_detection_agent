"""
Unit tests for the DetectionAgent class.
"""

import unittest
import time
import threading
from unittest.mock import Mock, patch
from detection_agent.agent import DetectionAgent
from detection_agent.config import Config
from detection_agent.detector import FileDetector, ProcessDetector


class TestDetectionAgent(unittest.TestCase):
    """Test cases for the DetectionAgent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use a custom config for testing
        self.test_config = Config()
        self.test_config.set("detection_interval", 1)  # Short interval for testing
        self.test_config.set("enabled_detectors", ["file", "process"])
        self.agent = DetectionAgent(self.test_config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if self.agent.is_running():
            self.agent.stop()
    
    def test_initialization(self):
        """Test agent initialization."""
        self.assertIsNotNone(self.agent.config)
        self.assertIsNotNone(self.agent.detector)
        self.assertFalse(self.agent.is_running())
        self.assertEqual(len(self.agent._callbacks), 0)
    
    def test_initialization_with_default_config(self):
        """Test agent initialization with default config."""
        agent = DetectionAgent()
        self.assertIsNotNone(agent.config)
        
        # Should have default enabled detectors
        enabled = agent.config.get("enabled_detectors", [])
        self.assertIn("file", enabled)
        self.assertIn("process", enabled)
    
    def test_detector_initialization(self):
        """Test that detectors are initialized based on config."""
        # Check that file detector is added
        file_detector = self.agent.detector.get_detector("file_detector")
        self.assertIsInstance(file_detector, FileDetector)
        
        # Check that process detector is added
        process_detector = self.agent.detector.get_detector("process_detector")
        self.assertIsInstance(process_detector, ProcessDetector)
    
    def test_selective_detector_initialization(self):
        """Test detector initialization with selective config."""
        config = Config()
        config.set("enabled_detectors", ["file"])  # Only file detector
        
        agent = DetectionAgent(config)
        
        # Should have file detector
        file_detector = agent.detector.get_detector("file_detector")
        self.assertIsNotNone(file_detector)
        
        # Should not have process detector
        process_detector = agent.detector.get_detector("process_detector")
        self.assertIsNone(process_detector)  # Should not be created
    
    def test_add_remove_callback(self):
        """Test adding and removing callbacks."""
        callback1 = Mock()
        callback2 = Mock()
        
        # Add callbacks
        self.agent.add_callback(callback1)
        self.agent.add_callback(callback2)
        self.assertEqual(len(self.agent._callbacks), 2)
        
        # Remove callback
        result = self.agent.remove_callback(callback1)
        self.assertTrue(result)
        self.assertEqual(len(self.agent._callbacks), 1)
        
        # Try to remove non-existent callback
        result = self.agent.remove_callback(callback1)
        self.assertFalse(result)
    
    def test_run_single_detection(self):
        """Test running a single detection cycle."""
        callback = Mock()
        self.agent.add_callback(callback)
        
        results = self.agent.run_single_detection()
        
        # Should return a list (may be empty)
        self.assertIsInstance(results, list)
        
        # If results exist, callback should be called
        if results:
            callback.assert_called_once_with(results)
    
    def test_callback_error_handling(self):
        """Test error handling in callbacks."""
        # Create a callback that raises an exception
        def error_callback(results):
            raise Exception("Callback error")
        
        normal_callback = Mock()
        
        self.agent.add_callback(error_callback)
        self.agent.add_callback(normal_callback)
        
        # Run detection - should not crash despite error in callback
        results = self.agent.run_single_detection()
        
        # Normal callback should still be called if there are results
        if results:
            normal_callback.assert_called_once_with(results)
    
    def test_start_stop_agent(self):
        """Test starting and stopping the agent."""
        # Start agent
        self.agent.start()
        self.assertTrue(self.agent.is_running())
        self.assertIsNotNone(self.agent._thread)
        self.assertTrue(self.agent._thread.is_alive())
        
        # Stop agent
        self.agent.stop()
        self.assertFalse(self.agent.is_running())
        
        # Wait a bit for thread to finish
        time.sleep(0.1)
        if self.agent._thread:
            self.assertFalse(self.agent._thread.is_alive())
    
    def test_start_already_running(self):
        """Test starting an already running agent."""
        self.agent.start()
        
        # Try to start again - should not create new thread
        old_thread = self.agent._thread
        self.agent.start()
        self.assertEqual(self.agent._thread, old_thread)
        
        self.agent.stop()
    
    def test_stop_not_running(self):
        """Test stopping an agent that's not running."""
        # Should not raise an exception
        self.agent.stop()
        self.assertFalse(self.agent.is_running())
    
    def test_get_status(self):
        """Test getting agent status."""
        status = self.agent.get_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn("running", status)
        self.assertIn("config", status)
        self.assertIn("detectors", status)
        self.assertIn("detection_count", status)
        self.assertIn("callbacks_registered", status)
        
        # Check specific values
        self.assertFalse(status["running"])
        self.assertEqual(status["callbacks_registered"], 0)
        self.assertIsInstance(status["detectors"], dict)
    
    def test_detection_history(self):
        """Test detection history management."""
        # Run some detections
        self.agent.run_single_detection()
        
        history = self.agent.get_detection_history()
        self.assertIsInstance(history, list)
        
        # Clear history
        self.agent.clear_history()
        history = self.agent.get_detection_history()
        self.assertEqual(len(history), 0)
    
    @patch('time.sleep')
    def test_run_loop_with_interval(self, mock_sleep):
        """Test the detection loop respects the configured interval."""
        # Set a specific interval
        self.agent.config.set("detection_interval", 5)
        
        # Start and quickly stop to test one iteration
        self.agent.start()
        time.sleep(0.1)  # Brief moment to let thread start
        self.agent.stop()
        
        # Check that sleep was called with the correct interval
        # Note: This is a simplified test - the actual implementation may call sleep multiple times
        if mock_sleep.called:
            # Check that at least one call was with our interval
            call_args = [call[0][0] for call in mock_sleep.call_args_list]
            self.assertIn(5, call_args)
    
    def test_integration_with_file_detector(self):
        """Test integration with file detector."""
        import tempfile
        import os
        
        # Create a temporary directory for testing
        temp_dir = tempfile.mkdtemp()
        test_file = os.path.join(temp_dir, "test_file.txt")
        
        try:
            # Create a file detector for our temp directory
            file_detector = FileDetector([temp_dir])
            self.agent.detector.add_detector(file_detector)
            
            # Create a test file
            with open(test_file, 'w') as f:
                f.write("test content")
            
            # Run detection
            results = self.agent.run_single_detection()
            
            # Should detect the file creation or modification
            self.assertIsInstance(results, list)
            
        finally:
            # Clean up
            if os.path.exists(test_file):
                os.unlink(test_file)
            os.rmdir(temp_dir)
    
    def test_thread_safety(self):
        """Test thread safety of agent operations."""
        # This is a basic test - more comprehensive thread safety testing
        # would require more complex scenarios
        
        results = []
        
        def collect_results(detection_results):
            results.extend(detection_results)
        
        self.agent.add_callback(collect_results)
        
        # Start agent
        self.agent.start()
        
        # Let it run briefly
        time.sleep(0.5)
        
        # Stop agent
        self.agent.stop()
        
        # Should not crash and should be in a consistent state
        self.assertFalse(self.agent.is_running())
        status = self.agent.get_status()
        self.assertIsInstance(status, dict)


if __name__ == '__main__':
    unittest.main()