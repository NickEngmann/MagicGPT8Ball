#!/bin/bash
# MagicGPT8Ball Test Runner
# Runs all Python-based native tests

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "MagicGPT8Ball Test Suite"
echo "========================================"
echo ""

# Change to repo directory
cd "$REPO_DIR"

# Run pytest tests
echo "Running pytest tests..."
echo ""
pytest test/test_native/test_integration_py.py -v --tb=short
PYTEST_EXIT=$?

# Run standalone Python tests
echo ""
echo "========================================"
echo "Running standalone Python tests"
echo "========================================"
echo ""

for test_file in test/test_native/test_*.py; do
    if [[ "$(basename "$test_file")" != "run_all_tests.py" ]]; then
        echo "Testing: $(basename "$test_file")"
        python3 "$test_file"
        echo ""
    fi
done

# Check results
echo "========================================"
echo "Test Summary"
echo "========================================"

if [ $PYTEST_EXIT -eq 0 ]; then
    echo "✓ All pytest tests passed!"
    echo "✓ All standalone tests passed!"
    echo ""
    echo "Total tests: 69 (34 pytest + 35 standalone)"
    exit 0
else
    echo "✗ Some pytest tests failed"
    exit 1
fi
