#include <unity.h>
#include "VibrationManager.h"

// Mock GPIO functions
static bool mockPinStates[2] = {false, false};
static unsigned long mockStartTime = 0;

void setUp(void) {
    mockPinStates[0] = false;
    mockPinStates[1] = false;
    mockStartTime = 0;
}

void tearDown(void) {
}

// Test constructor with default pins
test_constructor_default_pins() {
    VibrationManager manager;
    TEST_ASSERT_NOT_NULL(&manager);
}

// Test constructor with custom pins
test_constructor_custom_pins() {
    VibrationManager manager(10, 11);
    TEST_ASSERT_NOT_NULL(&manager);
}

// Test startVibration method
test_start_vibration() {
    VibrationManager manager;
    
    // Start vibration for 1000ms
    manager.startVibration(1000);
    
    // Check if vibrating
    TEST_ASSERT_TRUE(manager.isVibrating());
    
    // Check if pins are set HIGH
    TEST_ASSERT_TRUE(manager.getMotor1PinState());
    TEST_ASSERT_TRUE(manager.getMotor2PinState());
}

// Test stopVibration method
test_stop_vibration() {
    VibrationManager manager;
    
    // Start vibration
    manager.startVibration(1000);
    TEST_ASSERT_TRUE(manager.isVibrating());
    
    // Stop vibration
    manager.stopVibration();
    
    // Check if not vibrating
    TEST_ASSERT_FALSE(manager.isVibrating());
    
    // Check if pins are set LOW
    TEST_ASSERT_FALSE(manager.getMotor1PinState());
    TEST_ASSERT_FALSE(manager.getMotor2PinState());
}

// Test vibration duration
test_vibration_duration() {
    VibrationManager manager;
    
    // Start vibration for 500ms
    manager.startVibration(500);
    
    // Simulate time passing
    mockStartTime = 600; // 600ms passed
    
    // Check if vibration has stopped due to duration
    TEST_ASSERT_FALSE(manager.isVibrating());
}

// Test update method with time progression
test_update_with_time_progression() {
    VibrationManager manager;
    
    // Start vibration for 1000ms
    manager.startVibration(1000);
    TEST_ASSERT_TRUE(manager.isVibrating());
    
    // Simulate update at 500ms (still within duration)
    mockStartTime = 500;
    manager.update(mockStartTime);
    TEST_ASSERT_TRUE(manager.isVibrating());
    
    // Simulate update at 1500ms (past duration)
    mockStartTime = 1500;
    manager.update(mockStartTime);
    TEST_ASSERT_FALSE(manager.isVibrating());
}

// Test update method when not vibrating
test_update_when_not_vibrating() {
    VibrationManager manager;
    
    // Ensure not vibrating
    manager.stopVibration();
    TEST_ASSERT_FALSE(manager.isVibrating());
    
    // Simulate update
    mockStartTime = 1000;
    manager.update(mockStartTime);
    
    // Should still not be vibrating
    TEST_ASSERT_FALSE(manager.isVibrating());
}

// Test vibration with very short duration
test_vibration_short_duration() {
    VibrationManager manager;
    
    // Start vibration for 10ms
    manager.startVibration(10);
    
    // Simulate time passing (20ms)
    mockStartTime = 20;
    manager.update(mockStartTime);
    
    // Should have stopped
    TEST_ASSERT_FALSE(manager.isVibrating());
}

// Test vibration with zero duration
test_vibration_zero_duration() {
    VibrationManager manager;
    
    // Start vibration for 0ms
    manager.startVibration(0);
    
    // Should not be vibrating
    TEST_ASSERT_FALSE(manager.isVibrating());
}

// Test stopVibration when not vibrating
test_stop_when_not_vibrating() {
    VibrationManager manager;
    
    // Ensure not vibrating
    manager.stopVibration();
    
    // Should still not be vibrating
    TEST_ASSERT_FALSE(manager.isVibrating());
}

int main(void) {
    UNITY_BEGIN();
    
    RUN_TEST(test_constructor_default_pins);
    RUN_TEST(test_constructor_custom_pins);
    RUN_TEST(test_start_vibration);
    RUN_TEST(test_stop_vibration);
    RUN_TEST(test_vibration_duration);
    RUN_TEST(test_update_with_time_progression);
    RUN_TEST(test_update_when_not_vibrating);
    RUN_TEST(test_vibration_short_duration);
    RUN_TEST(test_vibration_zero_duration);
    RUN_TEST(test_stop_when_not_vibrating);
    
    return UNITY_END();
}
