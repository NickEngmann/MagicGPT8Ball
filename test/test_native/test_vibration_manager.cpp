/**
 * Unit tests for VibrationManagerNative
 * Tests the vibration motor control logic without hardware dependencies
 */

#include <unity.h>
#include "vibration_manager_native.h"
#include <unordered_map>

// Unity setup/teardown
void setUp(void) {}
void tearDown(void) {}

void test_vibration_manager_initialization(void) {
    VibrationManagerNative vib(5, 13);
    
    TEST_ASSERT_EQUAL_UINT8(5, vib.getMotor1Pin());
    TEST_ASSERT_EQUAL_UINT8(13, vib.getMotor2Pin());
    TEST_ASSERT_FALSE(vib.isVibrating());
    TEST_ASSERT_EQUAL_UINT32(0, vib.getStartTime());
    TEST_ASSERT_EQUAL_UINT32(0, vib.getDuration());
}

void test_vibration_manager_begin(void) {
    VibrationManagerNative vib(5, 13);
    vib.begin();
    
    // Pins should be configured as outputs
    TEST_ASSERT_TRUE(MockGPIO::pins.find(5) != MockGPIO::pins.end());
    TEST_ASSERT_TRUE(MockGPIO::pins.find(13) != MockGPIO::pins.end());
    
    // Motors should be off initially
    TEST_ASSERT_FALSE(vib.isVibrating());
}

void test_vibration_manager_start_stop(void) {
    VibrationManagerNative vib(5, 13);
    vib.begin();
    
    MockTime::setMillis(0);
    vib.startVibration(1000);
    
    TEST_ASSERT_TRUE(vib.isVibrating());
    TEST_ASSERT_EQUAL_UINT32(0, vib.getStartTime());
    TEST_ASSERT_EQUAL_UINT32(1000, vib.getDuration());
    
    vib.stop();
    TEST_ASSERT_FALSE(vib.isVibrating());
}

void test_vibration_manager_auto_stop(void) {
    VibrationManagerNative vib(5, 13);
    vib.begin();
    
    MockTime::setMillis(0);
    vib.startVibration(100);
    
    TEST_ASSERT_TRUE(vib.isVibrating());
    
    // Simulate time passing
    MockTime::setMillis(50);
    vib.update();
    TEST_ASSERT_TRUE(vib.isVibrating());
    
    MockTime::setMillis(150);
    vib.update();
    TEST_ASSERT_FALSE(vib.isVibrating());
}

void test_vibration_manager_short_buzz(void) {
    VibrationManagerNative vib(5, 13);
    vib.begin();
    
    MockTime::setMillis(0);
    vib.shortBuzz();
    
    TEST_ASSERT_TRUE(vib.isVibrating());
    TEST_ASSERT_EQUAL_UINT32(100, vib.getDuration());
}

void test_vibration_manager_medium_buzz(void) {
    VibrationManagerNative vib(5, 13);
    vib.begin();
    
    MockTime::setMillis(0);
    vib.mediumBuzz();
    
    TEST_ASSERT_TRUE(vib.isVibrating());
    TEST_ASSERT_EQUAL_UINT32(250, vib.getDuration());
}

void test_vibration_manager_long_buzz(void) {
    VibrationManagerNative vib(5, 13);
    vib.begin();
    
    MockTime::setMillis(0);
    vib.longBuzz();
    
    TEST_ASSERT_TRUE(vib.isVibrating());
    TEST_ASSERT_EQUAL_UINT32(500, vib.getDuration());
}

void test_vibration_manager_double_buzz(void) {
    VibrationManagerNative vib(5, 13);
    vib.begin();
    
    MockTime::setMillis(0);
    vib.doubleBuzz();
    
    // After double buzz, second buzz should be active
    TEST_ASSERT_TRUE(vib.isVibrating());
    TEST_ASSERT_EQUAL_UINT32(100, vib.getDuration());
}

void test_vibration_manager_gpio_state(void) {
    VibrationManagerNative vib(5, 13);
    vib.begin();
    MockTime::setMillis(0);
    vib.startVibration(1000);

    TEST_ASSERT_EQUAL_INT(1, MockGPIO::pins[5]);   // Motor 1 HIGH
    TEST_ASSERT_EQUAL_INT(1, MockGPIO::pins[13]);  // Motor 2 HIGH
}

void test_vibration_manager_custom_pins(void) {
    VibrationManagerNative vib(10, 11);
    vib.begin();
    
    TEST_ASSERT_EQUAL_UINT8(10, vib.getMotor1Pin());
    TEST_ASSERT_EQUAL_UINT8(11, vib.getMotor2Pin());
}

void test_vibration_manager_update_while_inactive(void) {
    VibrationManagerNative vib(5, 13);
    vib.begin();
    
    MockTime::setMillis(0);
    // Don't start vibration
    vib.update();
    
    TEST_ASSERT_FALSE(vib.isVibrating());
}

void test_vibration_manager_update_timing(void) {
    VibrationManagerNative vib(5, 13);
    vib.begin();
    
    MockTime::setMillis(0);
    vib.startVibration(50);
    
    // Update at 25ms - should still be vibrating
    MockTime::setMillis(25);
    vib.update();
    TEST_ASSERT_TRUE(vib.isVibrating());
    
    // Update at 51ms - should have stopped
    MockTime::setMillis(51);
    vib.update();
    TEST_ASSERT_FALSE(vib.isVibrating());
}

void run_vibration_manager_tests(void) {
    UNITY_BEGIN();
    
    RUN_TEST(test_vibration_manager_initialization);
    RUN_TEST(test_vibration_manager_begin);
    RUN_TEST(test_vibration_manager_start_stop);
    RUN_TEST(test_vibration_manager_auto_stop);
    RUN_TEST(test_vibration_manager_short_buzz);
    RUN_TEST(test_vibration_manager_medium_buzz);
    RUN_TEST(test_vibration_manager_long_buzz);
    RUN_TEST(test_vibration_manager_double_buzz);
    RUN_TEST(test_vibration_manager_gpio_state);
    RUN_TEST(test_vibration_manager_custom_pins);
    RUN_TEST(test_vibration_manager_update_while_inactive);
    RUN_TEST(test_vibration_manager_update_timing);
    
    UNITY_END();
}

int main(void) {
    run_vibration_manager_tests();
    return 0;
}
