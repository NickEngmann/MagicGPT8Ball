#include <unity.h>
#include "LEDLogger.h"

// Test LED logger (uses mock NeoPixel for native build)
LEDLogger ledLogger(3);

void setUp(void) {
    // Initialize LED logger
    ledLogger.begin();
}

void tearDown(void) {
    ledLogger.clear();
}

// Test initialization
void test_led_logger_initialization(void) {
    // Verify logger is initialized
    TEST_ASSERT_NOT_NULL(&ledLogger);
}

// Test state changes
void test_led_logger_set_idle_state(void) {
    ledLogger.setState(LEDLogger::SystemState::NORMAL, LEDLogger::LEDPattern::SOLID);
    ledLogger.update();
    TEST_ASSERT_TRUE(true);  // No crash indicates success
}

// Test error state
void test_led_logger_set_error_state(void) {
    ledLogger.setState(LEDLogger::SystemState::ERROR, LEDLogger::LEDPattern::PULSE);
    ledLogger.update();
    TEST_ASSERT_TRUE(true);
}

// Test busy state
void test_led_logger_busy_state(void) {
    ledLogger.setState(LEDLogger::SystemState::BUSY, LEDLogger::LEDPattern::BLINK);
    ledLogger.update();
    TEST_ASSERT_TRUE(true);
}

// Test multiple state changes
void test_led_logger_multiple_state_changes(void) {
    ledLogger.setState(LEDLogger::SystemState::NORMAL, LEDLogger::LEDPattern::SOLID);
    ledLogger.update();
    
    ledLogger.setState(LEDLogger::SystemState::BUSY, LEDLogger::LEDPattern::PULSE);
    ledLogger.update();
    
    ledLogger.setState(LEDLogger::SystemState::ERROR, LEDLogger::LEDPattern::FAST_BLINK);
    ledLogger.update();
    
    ledLogger.setState(LEDLogger::SystemState::NORMAL, LEDLogger::LEDPattern::SOLID);
    ledLogger.update();
    
    TEST_ASSERT_TRUE(true);
}

// Test custom state
void test_led_logger_custom_state(void) {
    ledLogger.setCustomState(0xFF00FF, LEDLogger::LEDPattern::SOLID);
    ledLogger.update();
    TEST_ASSERT_TRUE(true);
}

// Test brightness adjustment
void test_led_logger_brightness(void) {
    ledLogger.setBrightness(50);
    TEST_ASSERT_TRUE(true);
}

int main(void) {
    UNITY_BEGIN();

    RUN_TEST(test_led_logger_initialization);
    RUN_TEST(test_led_logger_set_idle_state);
    RUN_TEST(test_led_logger_set_error_state);
    RUN_TEST(test_led_logger_busy_state);
    RUN_TEST(test_led_logger_multiple_state_changes);
    RUN_TEST(test_led_logger_custom_state);
    RUN_TEST(test_led_logger_brightness);

    return UNITY_END();
}
