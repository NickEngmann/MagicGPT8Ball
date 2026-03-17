#define ARDUINO_ABS(x) ((x) >= 0 ? (x) : (-(x)))
extern "C" {
#include "unity.h"
}
#include <cmath>

// Animation Manager logic tests
void setUp(void) {
    // Setup before each test
}

void tearDown(void) {
    // Cleanup after each test
}

static float normalize_angle(float angle) {
    while (angle > 180.0f) angle -= 360.0f;
    while (angle < -180.0f) angle += 360.0f;
    return angle;
}

static float smooth_motion(float current, float target, float speed) {
    float diff = target - current;
    if (std::abs(diff) < speed) return target;
    return current + speed * (diff > 0 ? 1.0f : -1.0f);
}

static bool is_position_valid(float x, float y, float max_x, float max_y) {
    return x >= 0 && x <= max_x && y >= 0 && y <= max_y;
}

void test_normalize_angle_zero(void) {
    float result = normalize_angle(0.0f);
    TEST_ASSERT_EQUAL_FLOAT(0.0f, result);
}

void test_normalize_angle_within_range(void) {
    float result = normalize_angle(45.0f);
    TEST_ASSERT_EQUAL_FLOAT(45.0f, result);
}

void test_normalize_angle_above_range(void) {
    float result = normalize_angle(270.0f);
    TEST_ASSERT_EQUAL_FLOAT(-90.0f, result);
}

void test_normalize_angle_below_range(void) {
    float result = normalize_angle(-270.0f);
    TEST_ASSERT_EQUAL_FLOAT(90.0f, result);
}

void test_smooth_motion_converging(void) {
    float result = smooth_motion(10.0f, 50.0f, 10.0f);
    TEST_ASSERT_EQUAL_FLOAT(20.0f, result);
}

void test_smooth_motion_target_reached(void) {
    float result = smooth_motion(50.0f, 50.0f, 10.0f);
    TEST_ASSERT_EQUAL_FLOAT(50.0f, result);
}

void test_position_valid_inside_bounds(void) {
    TEST_ASSERT_TRUE(is_position_valid(50.0f, 50.0f, 100.0f, 100.0f));
}

void test_position_valid_at_edge(void) {
    TEST_ASSERT_TRUE(is_position_valid(0.0f, 0.0f, 100.0f, 100.0f));
    TEST_ASSERT_TRUE(is_position_valid(100.0f, 100.0f, 100.0f, 100.0f));
}

void test_position_invalid_outside_bounds(void) {
    TEST_ASSERT_FALSE(is_position_valid(-1.0f, 50.0f, 100.0f, 100.0f));
    TEST_ASSERT_FALSE(is_position_valid(101.0f, 50.0f, 100.0f, 100.0f));
}

int main(void) {
    UNITY_BEGIN();
    
    RUN_TEST(test_normalize_angle_zero);
    RUN_TEST(test_normalize_angle_within_range);
    RUN_TEST(test_normalize_angle_above_range);
    RUN_TEST(test_normalize_angle_below_range);
    
    RUN_TEST(test_smooth_motion_converging);
    RUN_TEST(test_smooth_motion_target_reached);
    
    RUN_TEST(test_position_valid_inside_bounds);
    RUN_TEST(test_position_valid_at_edge);
    RUN_TEST(test_position_invalid_outside_bounds);
    
    return UNITY_END();
}
