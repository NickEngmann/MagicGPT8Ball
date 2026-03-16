/**
 * @file test_animation_manager.cpp
 * @brief Unit tests for AnimationManager class logic
 * 
 * Tests core animation logic using mock implementations.
 * Note: Some tests require actual LVGL/TFT_eSPI initialization.
 */

#include <unity.h>
#include <math.h>
#include <float.h>
#include <algorithm>
#include <cstdio>

// Helper functions to mimic Arduino functions
float min(float a, float b) { return a < b ? a : b; }
float max(float a, float b) { return a > b ? a : b; }
template<typename T>
T constrain(T val, T minVal, T maxVal) {
    if (val < minVal) return minVal;
    if (val > maxVal) return maxVal;
    return val;
}
#define ARDUINO_ABS(x) ((x) < 0 ? -(x) : (x))
static constexpr float MOTION_SMOOTHING = 0.95f;
static constexpr float GYRO_SENSITIVITY = 0.08f;
static constexpr float IDLE_AMPLITUDE = 15.0f;
static constexpr float IDLE_SPEED = 0.001f;
static constexpr float SCREEN_MARGIN = 0.4f;
static constexpr float EDGE_BUFFER = 0.15f;

// Helper functions for testing motion logic
void test_motion_smoothing(void) {
    float velocity = 0.0f;
    float target = 10.0f;
    
    // Apply smoothing
    velocity = velocity * MOTION_SMOOTHING + (target - velocity) * (1.0f - MOTION_SMOOTHING);
    
    // Velocity should be closer to target than before
    TEST_ASSERT_FLOAT_WITHIN(0.1f, velocity, 0.5f);
}

void test_gyro_sensitivity(void) {
    float target_x = 100.0f;
    float target_y = 100.0f;
    float gyro_x = -2.0f;
    float gyro_y = -2.0f;
    
    // Apply gyro input
    target_x -= gyro_x * GYRO_SENSITIVITY;
    target_y -= gyro_y * GYRO_SENSITIVITY;
    
    // Position should change by gyro * sensitivity
    TEST_ASSERT_FLOAT_WITHIN(0.01f, target_x, 100.16f);
    TEST_ASSERT_FLOAT_WITHIN(0.01f, target_y, 100.16f);
}

void test_idle_motion_calculation(void) {
    float idle_time = 0.0f;
    float offset_x = 0.0f;
    float offset_y = 0.0f;
    
    // Update idle time
    idle_time += IDLE_SPEED;
    
    // Calculate offsets using trig functions
    offset_x = sin(idle_time) * cos(idle_time * 0.7f) * IDLE_AMPLITUDE;
    offset_y = cos(idle_time * 1.3f) * sin(idle_time * 0.5f) * IDLE_AMPLITUDE;
    
    // Apply tiny fraction to offset
    float target_x = 100.0f;
    float target_y = 100.0f;
    target_x += offset_x * 0.01f;
    target_y += offset_y * 0.01f;
    
    // Should still be close to original position
    TEST_ASSERT_FLOAT_WITHIN(0.5f, target_x, 100.0f);
    TEST_ASSERT_FLOAT_WITHIN(0.5f, target_y, 100.0f);
}

void test_position_constrain_circle(void) {
    float screenWidth = 240.0f;
    float screenHeight = 240.0f;
    float triangleSize = 120.0f;
    
    float center_x = screenWidth / 2.0f;
    float center_y = screenHeight / 2.0f;
    float radius = min(screenWidth, screenHeight) / 2.0f;
    float max_distance = radius * SCREEN_MARGIN;
    
    // Position far outside
    float test_x = 1000.0f;
    float test_y = 1000.0f;
    
    float dx = test_x + (triangleSize / 2) - center_x;
    float dy = test_y + (triangleSize / 2) - center_y;
    float distance = sqrt(dx * dx + dy * dy);
    
    // Distance should be constrained
    if (distance > max_distance) {
        float angle = atan2(dy, dx);
        float new_x = center_x + cos(angle) * max_distance - (triangleSize / 2);
        float new_y = center_y + sin(angle) * max_distance - (triangleSize / 2);
        
        test_x = new_x;
        test_y = new_y;
    }
    
    // Position should now be within bounds
    TEST_ASSERT_TRUE(test_x > -100.0f && test_x < 200.0f);
    TEST_ASSERT_TRUE(test_y > -100.0f && test_y < 200.0f);
}

void test_position_constrain_rectangular(void) {
    float screenWidth = 240.0f;
    float screenHeight = 240.0f;
    float triangleSize = 120.0f;
    
    float test_x = 1000.0f;
    float test_y = 1000.0f;
    
    // Apply rectangular constraints
    test_x = constrain(test_x, -triangleSize * EDGE_BUFFER,
                      screenWidth - triangleSize * (1.0f - EDGE_BUFFER));
    test_y = constrain(test_y, -triangleSize * EDGE_BUFFER,
                      screenHeight - triangleSize * (1.0f - EDGE_BUFFER));
    
    // Position should be within screen bounds
    TEST_ASSERT_TRUE(test_x >= -18.0f && test_x <= 168.0f);
    TEST_ASSERT_TRUE(test_y >= -18.0f && test_y <= 168.0f);
}

void test_velocity_damping(void) {
    float velocity_x = 100.0f;
    float velocity_y = -50.0f;
    float target_x = 0.0f;
    float target_y = 0.0f;
    
    // Apply smoothing: velocity += (target - velocity) * (1 - smoothing)
    // velocity_new = velocity * smoothing + (target - velocity) * (1 - smoothing)
    //             = velocity * smoothing + target * (1 - smoothing) - velocity * (1 - smoothing)
    //             = velocity * (smoothing + smoothing - 1) + target * (1 - smoothing)
    //             = velocity * (2*smoothing - 1) + target * (1 - smoothing)
    
    float smoothing = MOTION_SMOOTHING;
    float alpha = 1.0f - smoothing;
    
    float new_velocity_x = velocity_x * smoothing + (target_x - velocity_x) * alpha;
    float new_velocity_y = velocity_y * smoothing + (target_y - velocity_y) * alpha;
    
    // With smoothing=0.95, alpha=0.05
    // new_v = 100 * 0.95 + (0 - 100) * 0.05 = 95 - 5 = 90
    // new_v = -50 * 0.95 + (0 - (-50)) * 0.05 = -47.5 + 2.5 = -45
    
    TEST_ASSERT_FLOAT_WITHIN(1.0f, new_velocity_x, 90.0f);
    TEST_ASSERT_FLOAT_WITHIN(1.0f, new_velocity_y, -45.0f);
    
    velocity_x = new_velocity_x;
    velocity_y = new_velocity_y;
}

// Test motion state flags
void test_motion_state_flags(void) {
    // Simulate gyro readings
    float gyro_x = 0.0f;
    float gyro_y = 0.0f;
    
    // Check if motion is still
    bool is_still = ARDUINO_ABS(gyro_x) < 0.5f && ARDUINO_ABS(gyro_y) < 0.5f;
    
    TEST_ASSERT_TRUE(is_still);
    
    // Simulate actual motion
    gyro_x = 5.0f;
    gyro_y = 3.0f;
    
    is_still = ARDUINO_ABS(gyro_x) < 0.5f && ARDUINO_ABS(gyro_y) < 0.5f;
    
    TEST_ASSERT_FALSE(is_still);
}

// Run all tests
int main(void) {
    UNITY_BEGIN();
    
    RUN_TEST(test_motion_smoothing);
    RUN_TEST(test_gyro_sensitivity);
    RUN_TEST(test_idle_motion_calculation);
    RUN_TEST(test_position_constrain_circle);
    RUN_TEST(test_position_constrain_rectangular);
    RUN_TEST(test_velocity_damping);
    RUN_TEST(test_motion_state_flags);
    
    UNITY_END();
    return 0;
}
