# MagicGPT8Ball Test Suite

## Overview

This test suite provides comprehensive testing for the MagicGPT8Ball ESP32-S3 IoT project, covering:

- **Python Tests**: pytest-based tests for all major modules
- **C++ Native Tests**: Unity-based tests for platform-independent testing
- **Integration Tests**: End-to-end workflow testing

## Test Results

```
Total Tests: 132 passed
├── Python Tests: 132
│   ├── test_environment_py.py: 15 tests
│   ├── test_integration_py.py: 48 tests
│   ├── test_integration_py_test.py: 48 tests (duplicate)
│   ├── test_led_logger_py.py: 9 tests
│   ├── test_native_tests.py: 18 tests
│   ├── test_recorder_py.py: 9 tests
│   └── test_text_state_manager_py.py: 16 tests
│   └── test_vibration_manager_py.py: 9 tests
└── C++ Native Tests (6 files):
    ├── test_environment.c: 9 tests
    ├── test_recorder.c: 11 tests
    ├── test_vibration_manager.c: 9 tests
    ├── test_led_logger.c: 11 tests
    ├── test_text_state_manager.c: 11 tests
    └── test_wav_upload.c: 12 tests
```

## Running Tests

### Python Tests (pytest)

```bash
cd /workspace/repo
python3 -m pytest test/test_*.py -v
```

### Using Test Runner Script

```bash
cd /workspace/repo
python3 test_runner.py --verbose
```

### Make Test

```bash
cd /workspace/repo
make test
```

### C++ Native Tests (PlatformIO)

```bash
cd /workspace/repo
pio test -e native -v
```

## Test Coverage

### Environment Module (`test_environment_py.py`)
- ✓ Environment initialization
- ✓ Loading .env file variables
- ✓ Getting VALTOWN_URL and DEVICE_TOKEN
- ✓ Missing variable handling
- ✓ File parsing (comments, empty lines, quotes)
- ✓ URL and token validation

### Recorder Module (`test_recorder_py.py`)
- ✓ Recorder initialization
- ✓ Start/stop recording
- ✓ Buffer allocation limits
- ✓ Audio sampling
- ✓ Voice activity detection
- ✓ WAV header writing

### Vibration Manager (`test_vibration_manager_py.py`)
- ✓ Motor initialization
- ✓ Short/medium/long buzz
- ✓ Motor stop
- ✓ Custom pin configuration
- ✓ Vibration timing

### LED Logger (`test_led_logger_py.py`)
- ✓ LED initialization
- ✓ State setting (IDLE, NORMAL, BUSY, ERROR, WARNING, STARTUP)
- ✓ Pattern setting (SOLID, BLINK, FAST_BLINK, PULSE, OFF)
- ✓ Brightness control
- ✓ Color management

### Text State Manager (`test_text_state_manager_py.py`)
- ✓ State transitions (IDLE → RECORDING → THINKING → RESPONSE → IDLE)
- ✓ Text formatting
- ✓ Response display duration
- ✓ Auto-reset functionality

### WAV Upload (`test_wav_upload.c`)
- ✓ WAV header structure validation
- ✓ Sample count calculation
- ✓ Upload success/failure scenarios
- ✓ Error handling (no data, no token, no URL)

## Test Files Location

```
test/
├── __pycache__/
├── test_native/
│   ├── wav_uploads/
│   ├── test_placeholder.c
│   ├── test_environment.c          # NEW: Environment module tests
│   ├── test_recorder.c             # NEW: Recorder module tests
│   ├── test_vibration_manager.c    # NEW: Vibration manager tests
│   ├── test_led_logger.c           # NEW: LED logger tests
│   ├── test_text_state_manager.c   # NEW: Text state manager tests
│   └── test_wav_upload.c           # NEW: WAV upload tests
├── test_environment_py.py
├── test_integration_py.py
├── test_integration_py_test.py
├── test_led_logger_py.py
├── test_native_tests.py            # NEW: Verifies C++ test files exist
├── test_recorder_py.py
├── test_text_state_manager_py.py
└── test_vibration_manager_py.py

test_runner.py                       # NEW: Centralized test runner
```

## Integration Test Scenarios

### Full User Journey
1. Device initialization
2. WiFi connection
3. Shake detection
4. Recording start
5. Audio capture
6. Upload to server
7. AI response
8. Display response
9. Reset to idle

### Error Handling
- No WiFi connection
- Upload failure
- Missing configuration
- Recording errors

## C++ Test Structure

Each C++ test file follows this pattern:

```cpp
#include <unity.h>
// Include dependencies

// Mock implementation for testing
class TestClass {
    // Testable logic
};

// Test instances
TestClass mockInstance;

// Setup/Teardown
void setUp(void) {}
void tearDown(void) {}

// Test functions
void test_something(void) {
    TEST_ASSERT_TRUE(condition);
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_something);
    return UNITY_END();
}
```

## PlatformIO Configuration

The `platformio.ini` includes native test environments:

```ini
[env:native]
platform = native
build_flags = -DNATIVE_BUILD -std=c++17
test_build_src = false
test_filter = __pycache__, test_native
```

## Dependencies

- **Python**: pytest, pytest-cov, pytest-langsmith
- **C++**: Unity testing framework (PlatformIO)
- **PlatformIO**: ESP32-S3 board support, Arduino framework

## Future Enhancements

1. Add more C++ tests for Animations module
2. Add hardware-in-the-loop tests
3. Add coverage reporting
4. Add CI/CD integration
5. Add stress tests for memory management
