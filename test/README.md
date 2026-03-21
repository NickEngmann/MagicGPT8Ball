# MagicGPT8Ball Test Suite

This directory contains comprehensive unit tests for the MagicGPT8Ball project.

## Test Files

### Pytest Tests
- `test_integration_py.py` - Comprehensive pytest suite covering all major modules

### Standalone Python Tests
- `test_led_logger_py.py` - LEDLogger functionality tests
- `test_vibration_manager_py.py` - VibrationManager functionality tests
- `test_text_state_manager_py.py` - TextStateManager functionality tests
- `test_environment_py.py` - Environment variable handling tests

## Running Tests

### Using Pytest
```bash
pytest test/test_native/test_integration_py.py -v
```

### Using Standalone Test Runner
```bash
python3 test/test_native/run_all_tests.py
```

### Using Bash Script
```bash
bash test/run_tests.sh
```

## Test Coverage

- **LEDLogger**: 6 tests (state management, patterns, brightness)
- **VibrationManager**: 9 tests (vibration patterns, timing, control)
- **TextStateManager**: 10 tests (state transitions, text generation)
- **Environment**: 10 tests (variable loading, parsing)
- **Pytest Integration**: 34 tests (comprehensive coverage)

**Total: 69 tests**

## Test Architecture

Tests use mock implementations of Arduino dependencies to allow testing on non-embedded platforms. The test modules implement Python versions of the C++ classes, maintaining the same interface and behavior.

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

```bash
# Quick test run
pytest test/test_native/test_integration_py.py --tb=short

# Full test suite
bash test/run_tests.sh

# Test with coverage (if pytest-cov is available)
pytest test/test_native/test_integration_py.py --cov=test/test_native --cov-report=html
```
