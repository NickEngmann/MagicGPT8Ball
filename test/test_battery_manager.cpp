#include "unity.h"
#include "../src/BatteryManager.cpp"

BatteryManager* g_battery = nullptr;

void setUp(void) {
    g_battery = new BatteryManager();
    g_battery->begin();
}

void tearDown(void) {
    delete g_battery;
    g_battery = nullptr;
}

void test_battery_init_default_level(void) {
    g_battery->setSimulatedVoltage(4200);
    int level = g_battery->getBatteryLevel();
    TEST_ASSERT_EQUAL(100, level);
}

void test_battery_level_full_charge(void) {
    g_battery->setSimulatedVoltage(4200);
    int level = g_battery->getBatteryLevel();
    TEST_ASSERT_EQUAL(100, level);
}

void test_battery_level_half_charge(void) {
    g_battery->setSimulatedVoltage(3750);
    int level = g_battery->getBatteryLevel();
    TEST_ASSERT_EQUAL(50, level);
}

void test_battery_level_low_charge(void) {
    g_battery->setSimulatedVoltage(3600);
    int level = g_battery->getBatteryLevel();
    TEST_ASSERT_GREATER_OR_EQUAL(0, level);
    TEST_ASSERT_LESS_OR_EQUAL(100, level);
}

void test_battery_level_critical_charge(void) {
    g_battery->setSimulatedVoltage(3300);
    int level = g_battery->getBatteryLevel();
    TEST_ASSERT_EQUAL(0, level);
}

void test_battery_level_quarter_charge(void) {
    g_battery->setSimulatedVoltage(3525);
    int level = g_battery->getBatteryLevel();
    TEST_ASSERT_EQUAL(25, level);
}

void test_battery_level_three_quarter_charge(void) {
    g_battery->setSimulatedVoltage(3975);
    int level = g_battery->getBatteryLevel();
    TEST_ASSERT_EQUAL(75, level);
}

void test_battery_level_ninety_percent_charge(void) {
    g_battery->setSimulatedVoltage(4080);
    int level = g_battery->getBatteryLevel();
    TEST_ASSERT_EQUAL(90, level);
}

void test_battery_level_ten_percent_charge(void) {
    g_battery->setSimulatedVoltage(3390);
    int level = g_battery->getBatteryLevel();
    TEST_ASSERT_EQUAL(10, level);
}

void test_battery_level_five_percent_charge(void) {
    g_battery->setSimulatedVoltage(3345);
    int level = g_battery->getBatteryLevel();
    TEST_ASSERT_EQUAL(5, level);
}
