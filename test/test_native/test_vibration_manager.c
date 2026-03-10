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

#include "VibrationManager.h"

static VibrationManager* manager = NULL;

void setUp(void) {
    mock_millis = 0;
    manager = new VibrationManager(5, 13);
}

void tearDown(void) {
    delete manager;
    manager = NULL;
}

void test_vibration_manager_constructor_initializes_pins(void) {
    VibrationManager* testMgr = new VibrationManager(10, 11);
    TEST_ASSERT_NOT_NULL(testMgr);
    delete testMgr;
}

void test_vibration_manager_start_vibration_sets_state(void) {
    manager->startVibration(1000);
    TEST_ASSERT_TRUE(manager->isVibrating());
}

void test_vibration_manager_stop_vibration_clears_state(void) {
    manager->startVibration(1000);
    manager->stop();
    TEST_ASSERT_FALSE(manager->isVibrating());
}

void test_vibration_manager_update_with_elapsed_time_stops_vibration(void) {
    manager->startVibration(500);
    mock_millis = 600; // Time has elapsed
    manager->update();
    TEST_ASSERT_FALSE(manager->isVibrating());
}

void test_vibration_manager_update_with_not_elapsed_time_keeps_vibrating(void) {
    manager->startVibration(1000);
    mock_millis = 500; // Time has not elapsed
    manager->update();
    TEST_ASSERT_TRUE(manager->isVibrating());
}

void test_vibration_manager_update_with_zero_duration_stops_immediately(void) {
    manager->startVibration(0);
    mock_millis = 100;
    manager->update();
    TEST_ASSERT_FALSE(manager->isVibrating());
}

void test_vibration_manager_multiple_start_stop_cycles(void) {
    for (int i = 0; i < 5; i++) {
        manager->startVibration(500);
        TEST_ASSERT_TRUE(manager->isVibrating());
        manager->stop();
        TEST_ASSERT_FALSE(manager->isVibrating());
    }
}

void test_vibration_manager_update_with_no_vibration_does_nothing(void) {
    mock_millis = 1000;
    manager->update();
    TEST_ASSERT_FALSE(manager->isVibrating());
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_vibration_manager_constructor_initializes_pins);
    RUN_TEST(test_vibration_manager_start_vibration_sets_state);
    RUN_TEST(test_vibration_manager_stop_vibration_clears_state);
    RUN_TEST(test_vibration_manager_update_with_elapsed_time_stops_vibration);
    RUN_TEST(test_vibration_manager_update_with_not_elapsed_time_keeps_vibrating);
    RUN_TEST(test_vibration_manager_update_with_zero_duration_stops_immediately);
    RUN_TEST(test_vibration_manager_multiple_start_stop_cycles);
    RUN_TEST(test_vibration_manager_update_with_no_vibration_does_nothing);
    return UNITY_END();
}
