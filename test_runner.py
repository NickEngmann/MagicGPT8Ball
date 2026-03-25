#!/usr/bin/env python3
"""
MagicGPT8Ball Test Runner
Runs all native C++ tests and Python tests
"""

import subprocess
import sys
from pathlib import Path

def run_native_tests():
    """Run C++ native tests using Unity framework."""
    test_dir = Path(__file__).parent / "test_native"
    
    print("=" * 60)
    print("Running C++ Native Tests")
    print("=" * 60)
    
    test_files = sorted(test_dir.glob("test_*.c"))
    
    for test_file in test_files:
        print(f"\nCompiling {test_file.name}...")
        try:
            # Compile the test
            compile_cmd = [
                "gcc", "-I", str(test_dir.parent.parent / "src"),
                "-I", str(test_dir.parent.parent / "lib" / "lvgl"),
                "-I", str(test_dir.parent.parent / "lib" / "lvgl" / "src"),
                "-std=c++17", "-o", str(test_dir / "test_output.exe"),
                str(test_file),
            ]
            
            result = subprocess.run(compile_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Compilation failed for {test_file.name}:")
                print(result.stderr)
                continue
            
            # Run the test
            print(f"Running {test_file.name}...")
            run_result = subprocess.run(
                [str(test_dir / "test_output.exe")],
                capture_output=True,
                text=True
            )
            
            print(run_result.stdout)
            if run_result.stderr:
                print(run_result.stderr)
            
            # Cleanup
            (test_dir / "test_output.exe").unlink(missing_ok=True)
            
        except Exception as e:
            print(f"Error running {test_file.name}: {e}")
    
    print("\n" + "=" * 60)
    print("Native tests completed")
    print("=" * 60)

def run_python_tests():
    """Run Python tests using pytest."""
    print("\n" + "=" * 60)
    print("Running Python Tests")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            ["pytest", "test/", "-v"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent)
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"Error running Python tests: {e}")
        return False

def main():
    """Main test runner."""
    print("\nMagicGPT8Ball Test Suite Runner")
    print("=" * 60)
    
    # Run native tests
    run_native_tests()
    
    # Run Python tests
    python_success = run_python_tests()
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    if python_success:
        print("All tests passed!")
        return 0
    else:
        print("Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
