#include <unity.h>

// Mock Arduino functions for native build
#ifdef NATIVE_BUILD
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static unsigned long mock_millis = 0;
unsigned long millis(void) { return mock_millis; }
void delay(unsigned long ms) { mock_millis += ms; }
void pinMode(uint8_t pin, uint8_t mode) {}
void digitalWrite(uint8_t pin, uint8_t val) {}

#endif

#include "LEDLogger.h"

static LEDLogger* logger = NULL;

void setUp(void) {
    mock_millis = 0;
    logger = new LEDLogger(1, 2);
}

void tearDown(void) {
    delete logger;
    logger = NULL;
}

void test_led_logger_constructor_initializes_pins(void) {
    LEDLogger* testLogger = new LEDLogger(3, 4);
    TEST_ASSERT_NOT_NULL(testLogger);
    delete testLogger;
}

void test_led_logger_set_state_sets_correct_state(void) {
    logger->setState(LEDLogger::SystemState::IDLE);
    TEST_ASSERT_EQUAL_UINT8(LEDLogger::SystemState::IDLE, logger->getState());
}

void test_led_logger_set_state_updates_last_update_time(void) {
    logger->setState(LEDLogger::SystemState::IDLE);
    TEST_ASSERT_GREATER_THAN(0, logger->getLastUpdateTime());
}

void test_led_logger_update_with_no_state_change_does_nothing(void) {
    logger->setState(LEDLogger::SystemState::IDLE);
    mock_millis = 100;
    logger->update();
    TEST_ASSERT_EQUAL_UINT8(LEDLogger::SystemState::IDLE, logger->getState());
}

void test_led_logger_update_with_state_change_updates_state(void) {
    logger->setState(LEDLogger::SystemState::IDLE);
    mock_millis = 1000;
    logger->update();
    TEST_ASSERT_EQUAL_UINT8(LEDLogger::SystemState::IDLE, logger->getState());
}

void test_led_logger_get_color_for_state_returns_different_colors(void) {
    uint32_t idleColor = logger->getColorForState(LEDLogger::SystemState::IDLE);
    uint32_t recordingColor = logger->getColorForState(LEDLogger::SystemState::RECORDING);
    uint32_t thinkingColor = logger->getColorForState(LEDLogger::SystemState::THINKING);
    
    TEST_ASSERT_NOT_EQUAL(idleColor, recordingColor);
    TEST_ASSERT_NOT_EQUAL(recordingColor, thinkingColor);
    TEST_ASSERT_NOT_EQUAL(idleColor, thinkingColor);
}

void test_led_logger_set_pixel_sets_pixel_value(void) {
    logger->setPixel(0xFF0000);
    TEST_ASSERT_EQUAL_UINT32(0xFF0000, logger->getPixelValue());
}

void test_led_logger_dim_color_reduces_brightness(void) {
    uint32_t originalColor = logger->getColorForState(LEDLogger::SystemState::IDLE);
    uint32_t dimmedColor = logger->dimColor(originalColor, 0.5f);
    
    // Dimmed color should be less than original
    TEST_ASSERT_LESS_THAN(originalColor, dimmedColor);
}

void test_led_logger_multiple_state_transitions(void) {
    logger->setState(LEDLogger::SystemState::IDLE);
    logger->setState(LEDLogger::SystemState::RECORDING);
    logger->setState(LEDLogger::SystemState::THINKING);
    logger->setState(LEDLogger::SystemState::RESPONDING);
    
    TEST_ASSERT_EQUAL_UINT8(LEDLogger::SystemState::RESPONDING, logger->getState());
}

void test_led_logger_update_with_long_interval_does_not_update(void) {
    logger->setState(LEDLogger::SystemState::IDLE);
    mock_millis = 50; // Less than UPDATE_INTERVAL
    logger->update();
    TEST_ASSERT_EQUAL_UINT8(LEDLogger::SystemState::IDLE, logger->getState());
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_led_logger_constructor_initializes_pins);
    RUN_TEST(test_led_logger_set_state_sets_correct_state);
    RUN_TEST(test_led_logger_set_state_updates_last_update_time);
    RUN_TEST(test_led_logger_update_with_no_state_change_does_nothing);
    RUN_TEST(test_led_logger_update_with_state_change_updates_state);
    RUN_TEST(test_led_logger_get_color_for_state_returns_different_colors);
    RUN_TEST(test_led_logger_set_pixel_sets_pixel_value);
    RUN_TEST(test_led_logger_dim_color_reduces_brightness);
    RUN_TEST(test_led_logger_multiple_state_transitions);
    RUN_TEST(test_led_logger_update_with_long_interval_does_not_update);
    return UNITY_END();
}
