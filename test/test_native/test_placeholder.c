/**
 * Basic Unity framework test for platform initialization
 * Tests basic system functionality without hardware dependencies.
 */

#include <unity.h>
#include <stdint.h>
#include <string.h>

// Define ARDUINO_ABS to avoid conflicts with C++ stdlib
#define ARDUINO_ABS(x) ((x) < 0 ? -(x) : (x))

// Basic math test functions
int16_t abs_value(int16_t value) {
    return (value < 0) ? -value : value;
}

uint8_t clamp_uint8(uint16_t value, uint8_t min, uint8_t max) {
    if (value < min) return min;
    if (value > max) return max;
    return (uint8_t)value;
}

float clamp_float(float value, float min, float max) {
    if (value < min) return min;
    if (value > max) return max;
    return value;
}

// Test setup/teardown
void setUp(void) {}
void tearDown(void) {}

// Test cases
void test_abs_positive(void) {
    TEST_ASSERT_EQUAL_INT(42, abs_value(42));
}

void test_abs_negative(void) {
    TEST_ASSERT_EQUAL_INT(42, abs_value(-42));
}

void test_abs_zero(void) {
    TEST_ASSERT_EQUAL_INT(0, abs_value(0));
}

void test_clamp_within_bounds(void) {
    TEST_ASSERT_EQUAL_UINT8(50, clamp_uint8(50, 0, 100));
}

void test_clamp_below_min(void) {
    TEST_ASSERT_EQUAL_UINT8(10, clamp_uint8(5, 10, 100));
}

void test_clamp_above_max(void) {
    TEST_ASSERT_EQUAL_UINT8(100, clamp_uint8(150, 0, 100));
}

void test_clamp_float(void) {
    TEST_ASSERT_FLOAT_WITHIN(0.01f, 50.0f, clamp_float(50.0f, 0.0f, 100.0f));
    TEST_ASSERT_FLOAT_WITHIN(0.01f, 10.0f, clamp_float(5.0f, 10.0f, 100.0f));
    TEST_ASSERT_FLOAT_WITHIN(0.01f, 100.0f, clamp_float(150.0f, 0.0f, 100.0f));
}

void test_string_comparison(void) {
    const char* test_str = "test";
    TEST_ASSERT_EQUAL_STRING("test", test_str);
}

void test_pointer_validation(void) {
    int test_var = 42;
    int* ptr = &test_var;
    TEST_ASSERT_NOT_NULL(ptr);
    TEST_ASSERT_EQUAL_INT(42, *ptr);
}

void test_bitwise_operations(void) {
    uint8_t value = 0b10101010;
    uint8_t result = value & 0b11110000;
    TEST_ASSERT_EQUAL_UINT8(0b10100000, result);
}

void test_arithmetic_operations(void) {
    int16_t a = 10;
    int16_t b = 5;
    TEST_ASSERT_EQUAL_INT(15, a + b);
    TEST_ASSERT_EQUAL_INT(5, a - b);
    TEST_ASSERT_EQUAL_INT(50, a * b);
    TEST_ASSERT_EQUAL_INT(2, a / b);
}

void test_boolean_logic(void) {
    uint8_t flag1 = 1;
    uint8_t flag2 = 0;
    TEST_ASSERT_TRUE(flag1);
    TEST_ASSERT_FALSE(flag2);
    TEST_ASSERT_EQUAL_UINT8(1, flag1 && flag1);
    TEST_ASSERT_EQUAL_UINT8(0, flag1 && flag2);
}

void test_memory_operations(void) {
    uint8_t buffer[10];
    memset(buffer, 0, sizeof(buffer));
    for (int i = 0; i < 10; i++) {
        TEST_ASSERT_EQUAL_UINT8(0, buffer[i]);
    }
}

void test_minimum_maximum(void) {
    int16_t a = 10;
    int16_t b = 5;
    TEST_ASSERT_EQUAL_INT(5, a < b ? a : b);
    TEST_ASSERT_EQUAL_INT(10, a > b ? a : b);
}

void test_enum_basic(void) {
    enum TestState { STATE_IDLE, STATE_ACTIVE, STATE_ERROR };
    TEST_ASSERT_EQUAL_INT(STATE_IDLE, STATE_IDLE);
    TEST_ASSERT_EQUAL_INT(STATE_ACTIVE, STATE_ACTIVE);
    TEST_ASSERT_EQUAL_INT(STATE_ERROR, STATE_ERROR);
}

int main(void) {
    UNITY_BEGIN();
    
    RUN_TEST(test_abs_positive);
    RUN_TEST(test_abs_negative);
    RUN_TEST(test_abs_zero);
    RUN_TEST(test_clamp_within_bounds);
    RUN_TEST(test_clamp_below_min);
    RUN_TEST(test_clamp_above_max);
    RUN_TEST(test_clamp_float);
    RUN_TEST(test_string_comparison);
    RUN_TEST(test_pointer_validation);
    RUN_TEST(test_bitwise_operations);
    RUN_TEST(test_arithmetic_operations);
    RUN_TEST(test_boolean_logic);
    RUN_TEST(test_memory_operations);
    RUN_TEST(test_minimum_maximum);
    RUN_TEST(test_enum_basic);
    
    return UNITY_END();
}
