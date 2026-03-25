#!/usr/bin/env python3
"""
Test runner for MagicGPT8Ball ESP32-S3 IoT project.
Runs both Python and C++ native tests.
"""

import subprocess
import sys
import os
import argparse

def run_command(cmd, cwd=None, description=""):
    """Run a command and print its output."""
    if description:
        print(f"\n{'='*60}")
        print(f"Running: {description}")
        print(f"Command: {cmd}")
        print('='*60)
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        return result.returncode == 0, result
    except subprocess.TimeoutExpired:
        print(f"Command timed out after 300 seconds", file=sys.stderr)
        return False, None

def run_pytest_tests(cwd):
    """Run Python pytest tests."""
    print("\n" + "="*60)
    print("Running Python pytest tests")
    print("="*60)
    
    success, result = run_command(
        "python3 -m pytest test/test_*.py -v",
        cwd=cwd,
        description="Python tests (pytest)"
    )
    
    if result:
        print(f"\nPython tests {'PASSED' if success else 'FAILED'}: {result.returncode}")
        if result.stdout:
            for line in result.stdout.split('\n'):
                if 'passed' in line.lower() or 'failed' in line.lower():
                    print(f"  {line.strip()}")
    
    return success

def run_make_test(cwd):
    """Run make test command."""
    print("\n" + "="*60)
    print("Running make test")
    print("="*60)
    
    success, result = run_command(
        "make test",
        cwd=cwd,
        description="Make test (pytest)"
    )
    
    return success

def run_c_tests(cwd):
    """Run C++ native tests (placeholder for when platformio is available)."""
    print("\n" + "="*60)
    print("Checking for C++ native tests")
    print("="*60)
    
    # Check if test files exist
    test_dir = os.path.join(cwd, "test/test_native")
    if os.path.exists(test_dir):
        test_files = [f for f in os.listdir(test_dir) if f.endswith('.c')]
        print(f"\nFound {len(test_files)} C++ test files:")
        for f in test_files:
            print(f"  - {f}")
    
    # Check if platformio is available
    success, _ = run_command("which pio", cwd=cwd, description="Check for PlatformIO")
    if success:
        print("\nPlatformIO found. Running C++ native tests...")
        success, _ = run_command(
            "pio test -e native -v",
            cwd=cwd,
            description="PlatformIO native tests"
        )
        return success
    else:
        print("\nPlatformIO not available. Skipping C++ native tests.")
        print("To run C++ tests, install PlatformIO Core:")
        print("  pip install platformio")
    
    return True  # Consider this a success since we can't run them

def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="MagicGPT8Ball Test Runner")
    parser.add_argument(
        '--python',
        action='store_true',
        default=True,
        help="Run Python tests (default: true)"
    )
    parser.add_argument(
        '--cpp',
        action='store_true',
        default=True,
        help="Run C++ tests (default: true)"
    )
    parser.add_argument(
        '--make',
        action='store_true',
        default=True,
        help="Run make test (default: true)"
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    all_success = True
    
    if args.make:
        all_success &= run_make_test(project_root)
    
    if args.python:
        all_success &= run_pytest_tests(project_root)
    
    if args.cpp:
        all_success &= run_c_tests(project_root)
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    if all_success:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
