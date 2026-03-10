#include <unity.h>
#include "BatteryManager.h"
#include <cmath>

// Test setup
void setUp(void) {
}

void tearDown(void) {
}

void test_battery_manager_initialization(void) {
    BatteryManager bm(34, 35);
    
    // Check initial values
    TEST_ASSERT_EQUAL(0, bm.getBatteryVoltage());
    TEST_ASSERT_EQUAL(0, bm.getBatteryLevel());
    TEST_ASSERT_EQUAL(false, bm.isCharging());
    TEST_ASSERT_EQUAL(false, bm.isLow());
    TEST_ASSERT_EQUAL(false, bm.isCritical());
}

void test_battery_manager_voltage_conversion(void) {
    BatteryManager bm(34, 35);
    
    // Set mock voltage
    bm.setMockVoltage(3700);
    bm.setUseMockValues(true);
    
    // Check voltage reading
    TEST_ASSERT_EQUAL(3700, bm.getBatteryVoltage());
    
    // Test with different voltages
    bm.setMockVoltage(3000);
    TEST_ASSERT_EQUAL(3000, bm.getBatteryVoltage());
    
    bm.setMockVoltage(4200);
    TEST_ASSERT_EQUAL(4200, bm.getBatteryVoltage());
}

void test_battery_manager_get_battery_level(void) {
    BatteryManager bm(34, 35);
    
    // Set voltage and use mock values
    bm.setMockVoltage(3700);
    bm.setUseMockValues(true);
    
    // Check battery level for different voltages
    bm.setMockVoltage(3000);  // Low battery
    TEST_ASSERT_EQUAL(1, (int)bm.getBatteryLevel());
    
    bm.setMockVoltage(3500);  // Medium battery
    TEST_ASSERT_EQUAL(2, (int)bm.getBatteryLevel());
    
    bm.setMockVoltage(3800);  // High battery
    TEST_ASSERT_EQUAL(3, (int)bm.getBatteryLevel());
    
    bm.setMockVoltage(4100);  // Full battery
    TEST_ASSERT_EQUAL(4, (int)bm.getBatteryLevel());
}

void test_battery_manager_is_low(void) {
    BatteryManager bm(34, 35);
    
    bm.setMockVoltage(3000);  // Low battery
    bm.setUseMockValues(true);
    TEST_ASSERT_TRUE(bm.isLow());
    
    bm.setMockVoltage(3500);  // Medium battery
    TEST_ASSERT_FALSE(bm.isLow());
    
    bm.setMockVoltage(3900);  // High battery
    TEST_ASSERT_FALSE(bm.isLow());
}

void test_battery_manager_is_critical(void) {
    BatteryManager bm(34, 35);
    
    bm.setMockVoltage(2800);  // Critical battery
    bm.setUseMockValues(true);
    TEST_ASSERT_TRUE(bm.isCritical());
    
    bm.setMockVoltage(3200);  // Low battery
    TEST_ASSERT_FALSE(bm.isCritical());
    
    bm.setMockVoltage(3500);  // Medium battery
    TEST_ASSERT_FALSE(bm.isCritical());
}

void test_battery_manager_charging_status(void) {
    BatteryManager bm(34, 35);
    
    bm.setMockCharging(false);
    TEST_ASSERT_FALSE(bm.isCharging());
    
    bm.setMockCharging(true);
    TEST_ASSERT_TRUE(bm.isCharging());
}

void test_battery_manager_voltage_thresholds(void) {
    BatteryManager bm(34, 35);
    
    // Test critical threshold (default 3000mV)
    bm.setMockVoltage(2900);
    bm.setUseMockValues(true);
    TEST_ASSERT_TRUE(bm.isCritical());
    
    // Test low threshold (default 3200mV)
    bm.setMockVoltage(3100);
    TEST_ASSERT_TRUE(bm.isLow());
    
    // Test normal voltage
    bm.setMockVoltage(3700);
    TEST_ASSERT_FALSE(bm.isLow());
    TEST_ASSERT_FALSE(bm.isCritical());
}

void test_battery_manager_set_thresholds(void) {
    BatteryManager bm(34, 35);
    
    // Set custom thresholds
    bm.setLowThreshold(3500);
    bm.setCriticalThreshold(3200);
    
    // Test with voltage between new thresholds
    bm.setMockVoltage(3300);
    bm.setUseMockValues(true);
    TEST_ASSERT_TRUE(bm.isLow());
    TEST_ASSERT_FALSE(bm.isCritical());
    
    bm.setMockVoltage(3100);
    TEST_ASSERT_TRUE(bm.isCritical());
}

int main(void) {
    UNITY_BEGIN();
    
    RUN_TEST(test_battery_manager_initialization);
    RUN_TEST(test_battery_manager_voltage_conversion);
    RUN_TEST(test_battery_manager_get_battery_level);
    RUN_TEST(test_battery_manager_is_low);
    RUN_TEST(test_battery_manager_is_critical);
    RUN_TEST(test_battery_manager_charging_status);
    RUN_TEST(test_battery_manager_voltage_thresholds);
    RUN_TEST(test_battery_manager_set_thresholds);
    
    return UNITY_END();
}
