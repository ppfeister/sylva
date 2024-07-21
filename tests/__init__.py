import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def load_tests(loader, tests, pattern):
    """Test loader function for unittest discovery."""
    test_suite = unittest.TestSuite()
    for all_test_suite in unittest.defaultTestLoader.discover(os.path.dirname(__file__), pattern='test_*.py'):
        for test_suite in all_test_suite:
            test_suite.addTests(test_suite)
    return test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(load_tests())