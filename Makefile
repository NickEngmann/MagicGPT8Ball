.PHONY: test test-python test-cpp clean-python clean

# Run Python tests
test-python:
	python -m pytest test/test_native/ -v --tb=short

# Run C++ tests (Unity-based)
test-cpp:
	@echo "C++ tests would be run here with Unity framework"

# Run all tests
test: test-python test-cpp

# Clean Python test artifacts
clean-python:
	find test -name "*.pyc" -delete
	find test -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache

# Clean everything
clean: clean-python
