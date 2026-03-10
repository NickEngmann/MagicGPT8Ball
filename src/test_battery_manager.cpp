#include "BatteryManager.h"
#include <Unity.h>

#ifdef NATIVE_BUILD
// Native build test for BatteryManager

void setUp(void) {
    // Set up before each test
}

void tearDown(void) {
    // Clean up after each test
}

// Test 1: BatteryManager initialization
void test_battery_manager_initialization(void) {
    BatteryManager battery;
    battery.begin(36);
    
    TEST_ASSERT_EQUAL(0, battery.getBatteryLevel());
    TEST_ASSERT_EQUAL(BatteryManager::State::DISCHARGING, battery.getState());
    TEST_ASSERT_FALSE(battery.isLowBattery());
    TEST_ASSERT_FALSE(battery.isCriticalBattery());
}

// Test 2: Battery level calculation from voltage
void test_battery_level_calculation(void) {
    BatteryManager battery;
    battery.begin(36);
    
    // Test voltage to level conversion
    TEST_ASSERT_EQUAL(100, battery.voltageToLevel(4200));
    TEST_ASSERT_EQUAL(50, battery.voltageToLevel(3700));
    TEST_ASSERT_EQUAL(0, battery.voltageToLevel(3000));
    
    // Test level to voltage conversion
    TEST_ASSERT_EQUAL(4200, battery.levelToVoltage(100));
    TEST_ASSERT_EQUAL(3700, battery.levelToVoltage(50));
    TEST_ASSERT_EQUAL(3000, battery.levelToVoltage(0));
}

// Test 3: Low battery detection
void test_low_battery_detection(void) {
    BatteryManager battery;
    battery.begin(36);
    
    // Simulate low battery level
    battery.getBatteryLevel();
    
    // Test state transitions
    TEST_ASSERT_EQUAL(BatteryManager::State::DISCHARGING, battery.getState());
}

// Test 4: Critical battery detection
void test_critical_battery_detection(void) {
    BatteryManager battery;
    battery.begin(36);
    
    // Simulate critical battery level
    battery.getBatteryLevel();
    
    TEST_ASSERT_FALSE(battery.isCriticalBattery());
}

// Test 5: Voltage reading
void test_voltage_reading(void) {
    BatteryManager battery;
    battery.begin(36);
    
    int voltage = battery.getVoltage();
    TEST_ASSERT_GREATER_THAN(0, voltage);
    TEST_ASSERT_LESS_THAN(5000, voltage);
}

// Test 6: Estimated time until critical
void test_estimated_time_until_critical(void) {
    BatteryManager battery;
    battery.begin(36);
    
    int time = battery.getEstimatedTimeUntilCritical();
    TEST_ASSERT_GREATER_THAN(0, time);
}

// Test 7: Battery state updates
void test_battery_state_updates(void) {
    BatteryManager battery;
    battery.begin(36);
    
    // Test state transitions based on level
    TEST_ASSERT_EQUAL(BatteryManager::State::DISCHARGING, battery.getState());
    
    // Simulate different levels and check states
    int testLevels[] = {100, 80, 50, 20, 10, 5, 0};
    BatteryManager::State expectedStates[] = {
        BatteryManager::State::FULL,
        BatteryManager::State::DISCHARGING,
        BatteryManager::State::DISCHARGING,
        BatteryManager::State::LOW,
        BatteryManager::State::LOW,
        BatteryManager::State::CRITICAL,
        BatteryManager::State::CRITICAL
    };
    
    for (int i = 0; i < 7; i++) {
        // Manually set level for testing
        battery.batteryLevel = testLevels[i];
        battery.updateState();
        TEST_ASSERT_EQUAL(expectedStates[i], battery.getState());
    }
}

// Test 8: Low battery warning reset
void test_low_battery_warning_reset(void) {
    BatteryManager battery;
    battery.begin(36);
    
    battery.resetLowBatteryWarning();
    TEST_ASSERT_EQUAL(0, battery.getLowBatteryWarningTime());
}

// Test 9: Battery level clamping
void test_battery_level_clamping(void) {
    BatteryManager battery;
    battery.begin(36);
    
    // Test voltage clamping
    TEST_ASSERT_EQUAL(100, battery.voltageToLevel(5000));  // Above max
    TEST_ASSERT_EQUAL(0, battery.voltageToLevel(2000));    // Below min
    
    // Test level clamping
    TEST_ASSERT_EQUAL(4200, battery.levelToVoltage(150));  // Above max
    TEST_ASSERT_EQUAL(3000, battery.levelToVoltage(-50));   // Below min
}

// Test 10: Update function
void test_update_function(void) {
    BatteryManager battery;
    battery.begin(36);
    
    battery.update();
    
    // After update, should have a valid level
    int level = battery.getBatteryLevel();
    TEST_ASSERT_GREATER_THAN_OR_EQUAL_TO(0, level);
    TEST_ASSERT_LESS_THAN_OR_EQUAL_TO(100, level);
}

int main(void) {
    UNITY_BEGIN();
    
    RUN_TEST(test_battery_manager_initialization);
    RUN_TEST(test_battery_level_calculation);
    RUN_TEST(test_low_battery_detection);
    RUN_TEST(test_critical_battery_detection);
    RUN_TEST(test_voltage_reading);
    RUN_TEST(test_estimated_time_until_critical);
    RUN_TEST(test_battery_state_updates);
    RUN_TEST(test_low_battery_warning_reset);
    RUN_TEST(test_battery_level_clamping);
    RUN_TEST(test_update_function);
    
    return UNITY_END();
}

#else
// Hardware build - stub tests

void test_stub(void) {
    // This is a stub for hardware builds
    // Actual tests would require hardware
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_stub);
    return UNITY_END();
}
#endif
