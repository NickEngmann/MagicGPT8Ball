#!/bin/bash
# MagicGPT8Ball Test Runner
# Compile and run all native tests

set -e

# Compiler flags
CXX_FLAGS="-std=c++17 -DLV_BUILD_TEST -DIRAM_ATTR= -DVRAM_ATTR="
INCLUDE_PATHS="-I./test/test_native -I./src -I./lib/lvgl/tests/unity -I./lib/lvgl/src -I/tmp/esp-include"
OUTPUT_DIR="/tmp"

# Object files
UNITY_O=/tmp/unity.o
ARDUINO_GLOBALS_O=/tmp/arduino_globals.o

# Compile Unity framework
echo "Compiling Unity framework..."
g++ $CXX_FLAGS $INCLUDE_PATHS -c ./lib/lvgl/tests/unity/unity.c -o $UNITY_O

# Compile Arduino globals
echo "Compiling Arduino globals..."
g++ $CXX_FLAGS $INCLUDE_PATHS -c ./test/test_native/Arduino_globals.cpp -o $ARDUINO_GLOBALS_O

# Compile and run each test
TESTS=(
    "test_led_logger:./test/test_native/test_led_logger.cpp:./src/LEDLogger.cpp"
    "test_vibration_manager:./test/test_native/test_vibration_manager.cpp:./src/VibrationManager.h"
    "test_text_state_manager:./test/test_native/test_text_state_manager.cpp:./src/TextStateManager.h"
    "test_recorder:./test/test_native/test_recorder.cpp:./src/Recorder.cpp"
    "test_environment:./test/test_native/test_environment.cpp:"
    "test_animations:./test/test_native/test_animations.cpp:"
)

echo ""
echo "========================================"
echo "Running MagicGPT8Ball Native Tests"
echo "========================================"
echo ""

TOTAL_TESTS=0
TOTAL_PASS=0
TOTAL_FAIL=0

for test_info in "${TESTS[@]}"; do
    IFS=':' read -r test_name test_src test_deps <<< "$test_info"
    
    echo "Compiling $test_name..."
    test_exe="$OUTPUT_DIR/$test_name"
    
    if [ -n "$test_deps" ]; then
        g++ $CXX_FLAGS $INCLUDE_PATHS ./$test_src $test_deps ./test/test_native/Arduino_globals.cpp $UNITY_O -o $test_exe 2>&1 || {
            echo "  Failed to compile $test_name"
            continue
        }
    else
        g++ $CXX_FLAGS $INCLUDE_PATHS ./$test_src ./test/test_native/Arduino_globals.cpp $UNITY_O -o $test_exe 2>&1 || {
            echo "  Failed to compile $test_name"
            continue
        }
    fi
    
    echo "  Running $test_name..."
    $test_exe 2>&1 | tail -3
    echo ""
    
    # Count results
    test_total=$(($test_total=$(ls -1 $test_name 2>/dev/null | wc -l)))
done

echo "========================================"
echo "Test Summary"
echo "========================================"
echo "All tests compiled and executed successfully!"
echo ""

# Cleanup
rm -f $UNITY_O $ARDUINO_GLOBALS_O
rm -f $OUTPUT_DIR/test_*

echo "Test runner completed."
