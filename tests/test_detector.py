"""
Unit tests for the Detector classes.
"""

import unittest
import tempfile
import os
import time
from detection_agent.detector import (
    BaseDetector, FileDetector, ProcessDetector, Detector
)


class MockDetector(BaseDetector):
    """Mock detector for testing."""
    
    def __init__(self, name="mock_detector"):
        super().__init__(name)
        self.detection_results = []
    
    def detect(self):
        """Return mock detection results."""
        return self.detection_results.copy()


class TestBaseDetector(unittest.TestCase):
    """Test cases for the BaseDetector base class."""
    
    def test_initialization(self):
        """Test detector initialization."""
        detector = MockDetector("test_detector")
        
        self.assertEqual(detector.name, "test_detector")
        self.assertTrue(detector.is_enabled())
        self.assertIsNone(detector.last_detection_time)
    
    def test_enable_disable(self):
        """Test enabling and disabling detector."""
        detector = MockDetector()
        
        # Initially enabled
        self.assertTrue(detector.is_enabled())
        
        # Disable
        detector.disable()
        self.assertFalse(detector.is_enabled())
        
        # Enable again
        detector.enable()
        self.assertTrue(detector.is_enabled())


class TestFileDetector(unittest.TestCase):
    """Test cases for the FileDetector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_file.txt")
        
        # Create a test file
        with open(self.test_file, 'w') as f:
            f.write("initial content")
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_file):
            os.unlink(self.test_file)
        os.rmdir(self.temp_dir)
    
    def test_initialization(self):
        """Test file detector initialization."""
        detector = FileDetector([self.temp_dir])
        
        self.assertEqual(detector.name, "file_detector")
        self.assertEqual(detector.watch_paths, [self.temp_dir])
        self.assertTrue(detector.is_enabled())
    
    def test_default_watch_paths(self):
        """Test default watch paths."""
        detector = FileDetector()
        self.assertEqual(detector.watch_paths, ["."])
    
    def test_detect_no_changes(self):
        """Test detection when no changes occurred."""
        detector = FileDetector([self.temp_dir])
        
        # First detection should initialize cache, no changes
        results = detector.detect()
        # Since we just created the detector, files should be detected as created
        self.assertGreaterEqual(len(results), 0)
        
        # Second detection should show no changes
        results = detector.detect()
        self.assertEqual(len(results), 0)
    
    def test_detect_file_modification(self):
        """Test detection of file modifications."""
        detector = FileDetector([self.temp_dir])
        
        # Initialize cache
        detector.detect()
        
        # Sleep briefly to ensure timestamp difference
        time.sleep(0.1)
        
        # Modify the file
        with open(self.test_file, 'w') as f:
            f.write("modified content")
        
        # Detect changes
        results = detector.detect()
        
        # Should detect the modification
        self.assertGreater(len(results), 0)
        
        # Check the detection result
        modification_detected = any(
            result["type"] == "file_change" and 
            result["action"] == "modified" and
            self.test_file in result["path"]
            for result in results
        )
        self.assertTrue(modification_detected)
    
    def test_detect_new_file(self):
        """Test detection of new files."""
        detector = FileDetector([self.temp_dir])
        
        # Initialize cache
        detector.detect()
        
        # Create a new file
        new_file = os.path.join(self.temp_dir, "new_file.txt")
        with open(new_file, 'w') as f:
            f.write("new file content")
        
        try:
            # Detect changes
            results = detector.detect()
            
            # Should detect the new file
            self.assertGreater(len(results), 0)
            
            # Check the detection result
            creation_detected = any(
                result["type"] == "file_change" and 
                result["action"] == "created" and
                new_file in result["path"]
                for result in results
            )
            self.assertTrue(creation_detected)
            
        finally:
            if os.path.exists(new_file):
                os.unlink(new_file)
    
    def test_detect_disabled(self):
        """Test detection when detector is disabled."""
        detector = FileDetector([self.temp_dir])
        detector.disable()
        
        results = detector.detect()
        self.assertEqual(len(results), 0)
    
    def test_detect_nonexistent_path(self):
        """Test detection with non-existent paths."""
        detector = FileDetector(["/nonexistent/path"])
        
        # Should not raise an exception
        results = detector.detect()
        self.assertEqual(len(results), 0)


class TestProcessDetector(unittest.TestCase):
    """Test cases for the ProcessDetector class."""
    
    def test_initialization(self):
        """Test process detector initialization."""
        detector = ProcessDetector()
        
        self.assertEqual(detector.name, "process_detector")
        self.assertTrue(detector.is_enabled())
    
    def test_detect(self):
        """Test process detection."""
        detector = ProcessDetector()
        
        results = detector.detect()
        
        # Should return some results (mock implementation)
        self.assertGreaterEqual(len(results), 0)
        
        # Check that timestamp is updated
        self.assertIsNotNone(detector.last_detection_time)
    
    def test_detect_disabled(self):
        """Test detection when detector is disabled."""
        detector = ProcessDetector()
        detector.disable()
        
        results = detector.detect()
        self.assertEqual(len(results), 0)


class TestDetector(unittest.TestCase):
    """Test cases for the main Detector coordinator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = Detector()
        self.mock_detector1 = MockDetector("mock1")
        self.mock_detector2 = MockDetector("mock2")
    
    def test_initialization(self):
        """Test detector coordinator initialization."""
        self.assertEqual(len(self.detector.detectors), 0)
        self.assertEqual(len(self.detector.results), 0)
    
    def test_add_detector(self):
        """Test adding detectors."""
        self.detector.add_detector(self.mock_detector1)
        
        self.assertEqual(len(self.detector.detectors), 1)
        self.assertIn("mock1", self.detector.detectors)
        self.assertEqual(self.detector.detectors["mock1"], self.mock_detector1)
    
    def test_remove_detector(self):
        """Test removing detectors."""
        self.detector.add_detector(self.mock_detector1)
        self.detector.add_detector(self.mock_detector2)
        
        # Remove existing detector
        result = self.detector.remove_detector("mock1")
        self.assertTrue(result)
        self.assertEqual(len(self.detector.detectors), 1)
        self.assertNotIn("mock1", self.detector.detectors)
        
        # Try to remove non-existent detector
        result = self.detector.remove_detector("nonexistent")
        self.assertFalse(result)
    
    def test_get_detector(self):
        """Test getting detectors by name."""
        self.detector.add_detector(self.mock_detector1)
        
        # Get existing detector
        detector = self.detector.get_detector("mock1")
        self.assertEqual(detector, self.mock_detector1)
        
        # Get non-existent detector
        detector = self.detector.get_detector("nonexistent")
        self.assertIsNone(detector)
    
    def test_run_all_detections(self):
        """Test running all detections."""
        # Set up mock detection results
        self.mock_detector1.detection_results = [
            {"type": "test1", "timestamp": time.time()}
        ]
        self.mock_detector2.detection_results = [
            {"type": "test2", "timestamp": time.time()}
        ]
        
        self.detector.add_detector(self.mock_detector1)
        self.detector.add_detector(self.mock_detector2)
        
        results = self.detector.run_all_detections()
        
        # Should collect results from both detectors
        self.assertEqual(len(results), 2)
        
        # Check that results are stored in history
        self.assertEqual(len(self.detector.get_detection_history()), 2)
    
    def test_run_detections_with_disabled_detector(self):
        """Test running detections with disabled detectors."""
        self.mock_detector1.detection_results = [
            {"type": "test1", "timestamp": time.time()}
        ]
        self.mock_detector2.detection_results = [
            {"type": "test2", "timestamp": time.time()}
        ]
        
        # Disable one detector
        self.mock_detector2.disable()
        
        self.detector.add_detector(self.mock_detector1)
        self.detector.add_detector(self.mock_detector2)
        
        results = self.detector.run_all_detections()
        
        # Should only get results from enabled detector
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["type"], "test1")
    
    def test_detection_history(self):
        """Test detection history management."""
        self.mock_detector1.detection_results = [
            {"type": "test", "timestamp": time.time()}
        ]
        
        self.detector.add_detector(self.mock_detector1)
        
        # Run detections multiple times
        self.detector.run_all_detections()
        self.detector.run_all_detections()
        
        history = self.detector.get_detection_history()
        self.assertEqual(len(history), 2)
        
        # Test clearing history
        self.detector.clear_history()
        history = self.detector.get_detection_history()
        self.assertEqual(len(history), 0)
    
    def test_detection_error_handling(self):
        """Test error handling during detection."""
        # Create a detector that raises an exception
        class ErrorDetector(BaseDetector):
            def detect(self):
                raise Exception("Test error")
        
        error_detector = ErrorDetector("error_detector")
        self.detector.add_detector(error_detector)
        
        results = self.detector.run_all_detections()
        
        # Should capture the error as a detection result
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["type"], "detection_error")
        self.assertEqual(results[0]["detector"], "error_detector")
        self.assertIn("Test error", results[0]["error"])


if __name__ == '__main__':
    unittest.main()