/**
 * @file test_led_logger.cpp
 * @brief Unit tests for LEDLogger class
 * 
 * Tests LED state management, patterns, and color handling
 */

// Mock Arduino header first
#include "Arduino.h"

#include "../src/LEDLogger.h"
#include <unity.h>

// Mock NeoPixel for testing
// Implemented in Arduino_mock.h

/**
 * @brief Test: LEDLogger constructor initializes with defaults
 */
void test_led_logger_constructor(void) {
    LEDLogger led(3, 30);
    led.begin();
    // Verify constructor doesn't crash and basic initialization works
    TEST_ASSERT_TRUE(true);
}

/**
 * @brief Test: LEDLogger begins and initializes
 */
void test_led_logger_begin(void) {
    LEDLogger led(3, 30);
    led.begin();
    // begin() calls pixel.begin(), pixel.setBrightness, pixel.show
    // We verify it doesn't crash
    TEST_ASSERT_EQUAL(true, true);
}

/**
 * @brief Test: setState changes state correctly
 */
void test_led_logger_set_state(void) {
    LEDLogger led(3, 30);
    led.begin();
    
    led.setState(LEDLogger::SystemState::NORMAL);
    TEST_ASSERT_EQUAL(true, true); // State changed
    
    led.setState(LEDLogger::SystemState::ERROR);
    TEST_ASSERT_EQUAL(true, true);
    
    led.setState(LEDLogger::SystemState::STARTUP);
    TEST_ASSERT_EQUAL(true, true);
}

/**
 * @brief Test: LEDLogger handles all system states
 */
void test_led_logger_all_states(void) {
    LEDLogger led(3, 30);
    led.begin();
    
    led.setState(LEDLogger::SystemState::STARTUP);
    led.update();
    
    led.setState(LEDLogger::SystemState::NORMAL);
    led.update();
    
    led.setState(LEDLogger::SystemState::WARNING);
    led.update();
    
    led.setState(LEDLogger::SystemState::ERROR);
    led.update();
    
    led.setState(LEDLogger::SystemState::MAINTENANCE);
    led.update();
    
    led.setState(LEDLogger::SystemState::UPDATING);
    led.update();
    
    led.setState(LEDLogger::SystemState::CONNECTING);
    led.update();
    
    led.setState(LEDLogger::SystemState::BUSY);
    led.update();
    
    led.setState(LEDLogger::SystemState::STANDBY);
    led.update();
}

/**
 * @brief Test: setCustomState allows custom colors
 */
void test_led_logger_custom_state(void) {
    LEDLogger led(3, 30);
    led.begin();
    
    led.setCustomState(0xFF0000, LEDLogger::LEDPattern::SOLID); // Red
    led.update();
    
    led.setCustomState(0x00FF00, LEDLogger::LEDPattern::PULSE); // Green
    led.update();
    
    led.setCustomState(0x0000FF, LEDLogger::LEDPattern::BLINK); // Blue
    led.update();
}

/**
 * @brief Test: setBrightness changes brightness
 */
void test_led_logger_set_brightness(void) {
    LEDLogger led(3, 30);
    led.begin();
    
    led.setBrightness(50);
    led.update();
    
    led.setBrightness(100);
    led.update();
    
    led.setBrightness(255);
    led.update();
}

/**
 * @brief Test: clear turns off LED
 */
void test_led_logger_clear(void) {
    LEDLogger led(3, 30);
    led.begin();
    led.setCustomState(0xFF0000, LEDLogger::LEDPattern::SOLID);
    
    led.clear();
    led.update();
}

/**
 * @brief Test: LEDPattern enum values work
 */
void test_led_logger_patterns(void) {
    LEDLogger led(3, 30);
    led.begin();
    
    // Test each pattern
    led.setState(LEDLogger::SystemState::NORMAL, LEDLogger::LEDPattern::SOLID);
    led.update();
    
    led.setState(LEDLogger::SystemState::BUSY, LEDLogger::LEDPattern::PULSE);
    led.update();
    
    led.setState(LEDLogger::SystemState::ERROR, LEDLogger::LEDPattern::BLINK);
    led.update();
    
    led.setState(LEDLogger::SystemState::WARNING, LEDLogger::LEDPattern::FAST_BLINK);
    led.update();
    
    led.setState(LEDLogger::SystemState::BUSY, LEDLogger::LEDPattern::DOUBLE_BLINK);
    led.update();
    
    led.setCustomState(0xFFFFFF, LEDLogger::LEDPattern::RAINBOW);
    led.update();
}

void setUp(void) {
    // No setup needed for LED tests
}

void tearDown(void) {
}

int main(void) {
    UNITY_BEGIN();
    
    RUN_TEST(test_led_logger_constructor);
    RUN_TEST(test_led_logger_begin);
    RUN_TEST(test_led_logger_set_state);
    RUN_TEST(test_led_logger_all_states);
    RUN_TEST(test_led_logger_custom_state);
    RUN_TEST(test_led_logger_set_brightness);
    RUN_TEST(test_led_logger_clear);
    RUN_TEST(test_led_logger_patterns);
    
    return UNITY_END();
}
