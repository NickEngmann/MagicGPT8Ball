#include "unity.h"
#include <stdio.h>

void setUp(void) {}
void tearDown(void) {}

void test_placeholder_passes(void) {
    TEST_ASSERT_TRUE(1);
}

void test_math_operations(void) {
    int a = 5;
    int b = 3;
    TEST_ASSERT_EQUAL(8, a + b);
    TEST_ASSERT_EQUAL(2, a - b);
    TEST_ASSERT_EQUAL(15, a * b);
    TEST_ASSERT_EQUAL(1, a / b);
}

void test_string_comparison(void) {
    const char* str1 = "hello";
    const char* str2 = "hello";
    TEST_ASSERT_EQUAL_STRING(str1, str2);
}

int main(void) {
    printf("Running Unity tests...\n");
    UNITY_BEGIN();
    
    RUN_TEST(test_placeholder_passes);
    RUN_TEST(test_math_operations);
    RUN_TEST(test_string_comparison);
    
    printf("All tests completed!\n");
    return UNITY_END();
}
