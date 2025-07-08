"""
Test runner script for all unit tests.
"""

import unittest
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import test modules
from tests.test_config import TestConfig
from tests.test_detector import (
    TestBaseDetector, TestFileDetector, TestProcessDetector, TestDetector
)
from tests.test_agent import TestDetectionAgent


def create_test_suite():
    """Create a test suite containing all test cases."""
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add test cases from each module
    test_suite.addTest(loader.loadTestsFromTestCase(TestConfig))
    test_suite.addTest(loader.loadTestsFromTestCase(TestBaseDetector))
    test_suite.addTest(loader.loadTestsFromTestCase(TestFileDetector))
    test_suite.addTest(loader.loadTestsFromTestCase(TestProcessDetector))
    test_suite.addTest(loader.loadTestsFromTestCase(TestDetector))
    test_suite.addTest(loader.loadTestsFromTestCase(TestDetectionAgent))
    
    return test_suite


def run_tests():
    """Run all tests and return the result."""
    # Create test suite
    suite = create_test_suite()
    
    # Create test runner
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    # Run tests
    result = runner.run(suite)
    
    # Return success/failure
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)