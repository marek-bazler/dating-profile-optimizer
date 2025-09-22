#!/usr/bin/env python3
"""
Main test runner script
"""

import sys
import subprocess
from pathlib import Path

def install_test_requirements():
    """Install test requirements"""
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "test_requirements.txt"
        ])
        print("Test requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install test requirements: {e}")
        return False

def run_tests():
    """Run the test suite"""
    try:
        # Change to project directory
        project_dir = Path(__file__).parent
        
        # Run tests
        result = subprocess.run([
            sys.executable, "-m", "tests.test_runner"
        ], cwd=project_dir)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

def main():
    """Main function"""
    print("Dating Profile Optimizer - Test Suite")
    print("="*50)
    
    # Install test requirements
    print("Installing test requirements...")
    if not install_test_requirements():
        print("Failed to install test requirements. Continuing anyway...")
    
    print("\nRunning tests...")
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())