/**
 * Unit tests for LEDLoggerNative
 * Tests the LED state machine logic without hardware dependencies
 */

#include <unity.h>
#include "led_logger_native.h"
#include <vector>
#include <cmath>

using LEDPatternPattern = LEDLoggerPattern;
using SystemStatePattern = LEDLoggerState;

#define ENUM_EQUALS(enum_val, actual_val) TEST_ASSERT_EQUAL_INT(static_cast<int>(enum_val), static_cast<int>(actual_val))

// Constants for test timing
static const unsigned long BLINK_INTERVAL = 500;

// Unity setup/teardown (required but empty for our tests)
void setUp(void) {}
void tearDown(void) {}

// Test helper functions
uint32_t getRed(uint32_t color) {
    return (color >> 16) & 0xFF;
}

uint32_t getGreen(uint32_t color) {
    return (color >> 8) & 0xFF;
}

uint32_t getBlue(uint32_t color) {
    return color & 0xFF;
}

void test_led_logger_initialization(void) {
    LEDLoggerNative logger(3, 30);

    ENUM_EQUALS(SystemStatePattern::STARTUP, logger.getCurrentState());
    ENUM_EQUALS(LEDPatternPattern::PULSE, logger.getCurrentPattern());
    TEST_ASSERT_EQUAL_UINT32(0x0000FF, logger.getCurrentColor());
    TEST_ASSERT_EQUAL(30, logger.pixel.getBrightness());
}

void test_led_logger_set_normal_state(void) {
    LEDLoggerNative logger(3, 30);
    logger.setState(SystemStatePattern::NORMAL);

    ENUM_EQUALS(SystemStatePattern::NORMAL, logger.getCurrentState());
    TEST_ASSERT_EQUAL_UINT32(0x00FF00, logger.getCurrentColor());
}

void test_led_logger_set_error_state(void) {
    LEDLoggerNative logger(3, 30);
    logger.setState(SystemStatePattern::ERROR);

    ENUM_EQUALS(SystemStatePattern::ERROR, logger.getCurrentState());
    TEST_ASSERT_EQUAL_UINT32(0xFF0000, logger.getCurrentColor());
}

void test_led_logger_set_warning_state(void) {
    LEDLoggerNative logger(3, 30);
    logger.setState(SystemStatePattern::WARNING);

    ENUM_EQUALS(SystemStatePattern::WARNING, logger.getCurrentState());
    TEST_ASSERT_EQUAL_UINT32(0xFFFF00, logger.getCurrentColor());
}

void test_led_logger_custom_state(void) {
    LEDLoggerNative logger(3, 30);
    logger.setCustomState(0x123456);

    ENUM_EQUALS(SystemStatePattern::CUSTOM, logger.getCurrentState());
    TEST_ASSERT_EQUAL_UINT32(0x123456, logger.getCurrentColor());
}

void test_led_logger_state_colors(void) {
    LEDLoggerNative logger(3, 30);

    logger.setState(SystemStatePattern::STARTUP);
    TEST_ASSERT_EQUAL_UINT32(0x0000FF, logger.getCurrentColor());

    logger.setState(SystemStatePattern::NORMAL);
    TEST_ASSERT_EQUAL_UINT32(0x00FF00, logger.getCurrentColor());

    logger.setState(SystemStatePattern::WARNING);
    TEST_ASSERT_EQUAL_UINT32(0xFFFF00, logger.getCurrentColor());

    logger.setState(SystemStatePattern::ERROR);
    TEST_ASSERT_EQUAL_UINT32(0xFF0000, logger.getCurrentColor());

    logger.setState(SystemStatePattern::MAINTENANCE);
    TEST_ASSERT_EQUAL_UINT32(0xFF00FF, logger.getCurrentColor());

    logger.setState(SystemStatePattern::UPDATING);
    TEST_ASSERT_EQUAL_UINT32(0xFFFFFF, logger.getCurrentColor());

    logger.setState(SystemStatePattern::CONNECTING);
    TEST_ASSERT_EQUAL_UINT32(0x00FFFF, logger.getCurrentColor());

    logger.setState(SystemStatePattern::BUSY);
    TEST_ASSERT_EQUAL_UINT32(0xFFA500, logger.getCurrentColor());

    logger.setState(SystemStatePattern::STANDBY);
    TEST_ASSERT_EQUAL_UINT32(0x101010, logger.getCurrentColor());
}

void test_led_logger_solid_pattern(void) {
    LEDLoggerNative logger(3, 30);
    logger.setState(SystemStatePattern::NORMAL, LEDPatternPattern::SOLID);

    MockTime::setMillis(0);

    for (int i = 0; i < 3; i++) {
        logger.update();
        MockTime::setMillis(i * 10);
    }

    TEST_ASSERT_EQUAL_UINT32(0x00FF00, logger.getCurrentColor());

    std::vector<uint32_t>& pixels = logger.pixel.getPixels();
    TEST_ASSERT_GREATER_THAN(0, pixels.size());
    TEST_ASSERT_EQUAL_UINT32(0x00FF00, pixels[0]);
}

void test_led_logger_pulse_pattern(void) {
    LEDLoggerNative logger(3, 30);
    logger.setState(SystemStatePattern::NORMAL, LEDPatternPattern::PULSE);

    MockTime::setMillis(0);

    uint32_t firstColor = 0;

    for (int i = 0; i < 20; i++) {
        logger.update();
        MockTime::setMillis(i * 50);

        if (i == 0) {
            firstColor = logger.getCurrentColor();
        }
    }

    TEST_ASSERT_GREATER_THAN(0, logger.getCurrentColor());

    std::vector<uint32_t>& pixels = logger.pixel.getPixels();
    TEST_ASSERT_GREATER_THAN(0, pixels.size());
}

void test_led_logger_blink_pattern(void) {
    LEDLoggerNative logger(3, 30);
    logger.setState(SystemStatePattern::WARNING, LEDPatternPattern::BLINK);

    MockTime::setMillis(0);

    logger.update();
    TEST_ASSERT_EQUAL_UINT32(0xFFFF00, logger.getCurrentColor());

    MockTime::setMillis(BLINK_INTERVAL + 100);
    logger.update();

    std::vector<uint32_t>& pixels = logger.pixel.getPixels();
    TEST_ASSERT_GREATER_THAN(0, pixels.size());
}

void test_led_logger_rainbow_pattern(void) {
    LEDLoggerNative logger(3, 30);
    logger.setState(SystemStatePattern::NORMAL, LEDPatternPattern::RAINBOW);

    MockTime::setMillis(0);

    uint32_t firstColor = 0;

    for (int i = 0; i < 5; i++) {
        logger.update();
        MockTime::setMillis(i * 100);

        if (i == 0) {
            firstColor = logger.getCurrentColor();
        }
    }

    TEST_ASSERT_GREATER_THAN(0, logger.getCurrentColor());
}

void test_led_logger_set_brightness(void) {
    LEDLoggerNative logger(3, 30);
    logger.setBrightness(15);

    TEST_ASSERT_EQUAL_UINT8(15, logger.pixel.getBrightness());
}

void test_led_logger_clear(void) {
    LEDLoggerNative logger(3, 30);
    logger.setState(SystemStatePattern::NORMAL);

    TEST_ASSERT_EQUAL_UINT32(0x00FF00, logger.getCurrentColor());

    logger.clear();

    ENUM_EQUALS(SystemStatePattern::STANDBY, logger.getCurrentState());
    TEST_ASSERT_EQUAL_UINT32(0x000000, logger.getCurrentColor());
}

void test_led_logger_color_extraction(void) {
    uint32_t testColor = 0x123456;

    TEST_ASSERT_EQUAL_UINT8(0x12, getRed(testColor));
    TEST_ASSERT_EQUAL_UINT8(0x34, getGreen(testColor));
    TEST_ASSERT_EQUAL_UINT8(0x56, getBlue(testColor));
}

void test_led_logger_pulse_dimming(void) {
    LEDLoggerNative logger(3, 30);
    logger.setState(SystemStatePattern::NORMAL, LEDPatternPattern::PULSE);

    MockTime::setMillis(0);

    uint32_t colors[10];

    for (int i = 0; i < 10; i++) {
        logger.update();
        MockTime::setMillis(i * 100);
        colors[i] = logger.getCurrentColor();
    }

    for (int i = 0; i < 10; i++) {
        TEST_ASSERT_GREATER_THAN(0, colors[i]);
    }
}

void run_led_logger_tests(void) {
    UNITY_BEGIN();

    RUN_TEST(test_led_logger_initialization);
    RUN_TEST(test_led_logger_set_normal_state);
    RUN_TEST(test_led_logger_set_error_state);
    RUN_TEST(test_led_logger_set_warning_state);
    RUN_TEST(test_led_logger_custom_state);
    RUN_TEST(test_led_logger_state_colors);
    RUN_TEST(test_led_logger_solid_pattern);
    RUN_TEST(test_led_logger_pulse_pattern);
    RUN_TEST(test_led_logger_blink_pattern);
    RUN_TEST(test_led_logger_rainbow_pattern);
    RUN_TEST(test_led_logger_set_brightness);
    RUN_TEST(test_led_logger_clear);
    RUN_TEST(test_led_logger_color_extraction);
    RUN_TEST(test_led_logger_pulse_dimming);

    UNITY_END();
}

int main(void) {
    run_led_logger_tests();
    return 0;
}
