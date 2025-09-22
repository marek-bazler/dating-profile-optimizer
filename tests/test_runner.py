"""
Test runner with coverage reporting
"""

import unittest
import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

def run_tests_with_coverage():
    """Run all tests with coverage reporting"""
    try:
        import coverage
        
        # Initialize coverage
        cov = coverage.Coverage(source=['src'])
        cov.start()
        
        # Discover and run tests
        loader = unittest.TestLoader()
        start_dir = Path(__file__).parent
        suite = loader.discover(start_dir, pattern='test_*.py')
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Stop coverage and generate report
        cov.stop()
        cov.save()
        
        print("\n" + "="*50)
        print("COVERAGE REPORT")
        print("="*50)
        cov.report()
        
        # Generate HTML report
        html_dir = Path(__file__).parent.parent / "htmlcov"
        cov.html_report(directory=str(html_dir))
        print(f"\nHTML coverage report generated in: {html_dir}")
        
        return result.wasSuccessful()
        
    except ImportError:
        print("Coverage package not installed. Running tests without coverage...")
        return run_tests_without_coverage()

def run_tests_without_coverage():
    """Run all tests without coverage reporting"""
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests_with_coverage()
    sys.exit(0 if success else 1)