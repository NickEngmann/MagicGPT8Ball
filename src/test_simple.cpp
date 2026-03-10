// Simple test to verify PlatformIO test setup works
#include <Unity.h>

void test_simple_pass(void) {
    TEST_ASSERT_TRUE(true);
}

void test_simple_addition(void) {
    int result = 2 + 2;
    TEST_ASSERT_EQUAL(4, result);
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_simple_pass);
    RUN_TEST(test_simple_addition);
    return UNITY_END();
}
