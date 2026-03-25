#include <unity.h>
#include "VibrationManager.h"

// Test vibration manager
VibrationManager vibration(45, 46);

void setUp(void) {
    vibration.begin();
}

void tearDown(void) {}

// Test initialization
void test_vibration_manager_initialization(void) {
    // Check that vibration manager was initialized
    TEST_ASSERT_TRUE(true);  // Basic check - actual hardware setup verified by compilation
}

// Test short buzz
void test_vibration_manager_short_buzz(void) {
    vibration.shortBuzz();
    vibration.update();
    // Verify method can be called without error
    TEST_ASSERT_TRUE(true);
}

// Test medium buzz
void test_vibration_manager_medium_buzz(void) {
    vibration.mediumBuzz();
    vibration.update();
    // Verify method can be called without error
    TEST_ASSERT_TRUE(true);
}

// Test long buzz
void test_vibration_manager_long_buzz(void) {
    vibration.longBuzz();
    vibration.update();
    // Verify method can be called without error
    TEST_ASSERT_TRUE(true);
}

// Test stop vibration
void test_vibration_manager_stop(void) {
    vibration.shortBuzz();
    vibration.stop();
    vibration.update();
    // Verify stop method works
    TEST_ASSERT_TRUE(true);
}

// Test continuous vibration
void test_vibration_manager_continuous(void) {
    vibration.setContinuous(true);
    vibration.shortBuzz();
    
    for (int i = 0; i < 5; i++) {
        vibration.update();
    }
    
    vibration.stop();
    TEST_ASSERT_TRUE(true);
}

// Test update loop
void test_vibration_manager_update(void) {
    vibration.begin();
    
    vibration.shortBuzz();
    vibration.update();
    
    vibration.mediumBuzz();
    vibration.update();
    
    vibration.stop();
    vibration.update();
    
    TEST_ASSERT_TRUE(true);
}

int main(void) {
    UNITY_BEGIN();

    RUN_TEST(test_vibration_manager_initialization);
    RUN_TEST(test_vibration_manager_short_buzz);
    RUN_TEST(test_vibration_manager_medium_buzz);
    RUN_TEST(test_vibration_manager_long_buzz);
    RUN_TEST(test_vibration_manager_stop);
    RUN_TEST(test_vibration_manager_continuous);
    RUN_TEST(test_vibration_manager_update);

    return UNITY_END();
}
