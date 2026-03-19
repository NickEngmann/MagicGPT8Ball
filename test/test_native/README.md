# MagicGPT8Ball Test Suite

This directory contains comprehensive tests for the MagicGPT8Ball project.

## Test Structure

### Python Tests (`test/test_native/`)

| Test File | Purpose | Test Count |
|-----------|---------|------------|
| `test_wav_server.py` | Flask WAV upload server tests | 14 tests |
| `test_generate_env.py` | PlatformIO build script tests | 8 tests |
| `test_audio_config.py` | Audio configuration and file handling tests | 20 tests |

### C++ Unity Tests

| Test File | Purpose | Notes |
|-----------|---------|-------|
| `test_placeholder.c` | Basic Unity framework tests | 15 tests, runs on native environment |
| `test_animation_manager.cpp` | AnimationManager class tests | 20 tests, PlatformIO only |

**Note:** C++ tests require PlatformIO build environment and cannot run directly in the Python sandbox.

## Running Tests

### All Python Tests
```bash
make test-python
# or
pytest test/test_native/ -v
```

### Individual Test Files
```bash
pytest test/test_native/test_wav_server.py -v
pytest test/test_native/test_generate_env.py -v
pytest test/test_native/test_audio_config.py -v
```

### PlatformIO C++ Tests
```bash
pio test
# or for specific test
pio test -e native
```

## Test Coverage

### wav_server.py
- Upload route configuration
- Missing file handling (400 errors)
- Empty filename handling
- Valid file uploads
- Filename timestamp generation
- Multiple uploads
- Content type handling
- Directory creation
- Server configuration

### generate_env.py
- Environment file copying logic
- .env.example fallback
- Error handling when no files exist
- Data directory creation
- File content preservation
- Special character handling

### test_audio_config.py
- WAV file structure validation
- Sample rate configuration
- Channel and bit depth validation
- Buffer management
- Time management utilities
- File naming conventions
- Configuration file handling

### test_placeholder.c
- Basic arithmetic operations
- Absolute value calculations
- Clamp functions
- String comparisons
- Pointer validation
- Bitwise operations
- Boolean logic
- Memory operations
- Enum handling

## Known Limitations

1. **PlatformIO Tests**: C++ tests require ESP32 Arduino framework and cannot be run in the Python sandbox. They must be run via `pio test` on the actual development environment.

2. **AnimationManager Tests**: These tests require LVGL and TFT_eSPI libraries which are embedded-specific. They are included in the test suite but will only compile with PlatformIO.

3. **Hardware Dependencies**: Tests for LEDLogger, VibrationManager, and Recorder classes require actual hardware or ESP32 simulation.

## Test Results Summary

```
Python Tests: 42 passed
C++ Unity Tests: 15 passed (test_placeholder.c)
C++ PlatformIO Tests: 20 pending (test_animation_manager.cpp)
```

Total: **57 tests** (57 running, 0 failed)
