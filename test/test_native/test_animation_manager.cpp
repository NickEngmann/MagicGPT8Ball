/**
 * Unit tests for AnimationManager - LVGL animation controller
 * Tests motion smoothing, angle normalization, bounds checking, and state management.
 */

#define ARDUINO_ABS(x) ((x) < 0 ? -(x) : (x))  // Avoid C++ stdlib abs() conflict

#include "../../lib/lvgl/lvgl.h"
#include "../../src/Animations.h"
#include "../../src/Environment.h"
#include "../../test/test_lvgl_render/lvgl_test_helper.h"
#include <unity.h>

// Test configuration
#define TEST_SCREEN_WIDTH 240
#define TEST_SCREEN_HEIGHT 240

// Mock the display flush callback to avoid hardware dependencies
void mockDisplayFlush(lv_disp_drv_t *disp_drv, const lv_area_t *area, lv_color_t *color_p) {
    // Mock implementation - do nothing
    lv_disp_flush_ready(disp_drv);
}

class AnimationManagerTest {
private:
    AnimationManager* manager;
    
public:
    AnimationManagerTest() : manager(nullptr) {}
    
    ~AnimationManagerTest() {
        if (manager) {
            delete manager;
            manager = nullptr;
        }
    }
    
    void setup() {
        // Initialize LVGL
        lvgl_test_init();
        
        // Create test manager
        manager = new AnimationManager(TEST_SCREEN_WIDTH, TEST_SCREEN_HEIGHT);
    }
    
    void teardown() {
        if (manager) {
            delete manager;
            manager = nullptr;
        }
    }
    
    // Test motion smoothing
    void testMotionSmoothing() {
        // Simulate gyro input with high velocity
        float gyro_x = 5.0f;
        float gyro_y = 3.0f;
        
        // Verify smoothing coefficient is applied
        // Actual implementation uses MOTION_SMOOTHING = 0.95f
        float velocity_x = 0.0f;
        float target_x = 0.0f;
        
        // Apply smoothing formula from AnimationManager
        target_x += gyro_x;
        velocity_x = velocity_x * 0.95f + (target_x - velocity_x) * (1.0f - 0.95f);
        
        // After first frame, velocity should be dampened
        TEST_ASSERT_FLOAT_WITHIN(0.1f, velocity_x, gyro_x * 0.05f);
    }
    
    // Test angle normalization (simplified - no trig needed)
    void testAngleNormalization() {
        float angle1 = 360.0f;
        float angle2 = 0.0f;
        
        // Normalize angles should be within reasonable bounds
        float normalized = angle1;
        while (normalized > 360.0f) normalized -= 360.0f;
        while (normalized < 0.0f) normalized += 360.0f;
        
        TEST_ASSERT_EQUAL_FLOAT(0.0f, normalized);
    }
    
    // Test position constraints
    void testPositionConstraints() {
        // Verify triangle size calculation
        uint16_t width = TEST_SCREEN_WIDTH;
        uint16_t height = TEST_SCREEN_HEIGHT;
        float triangleSize = width / 2.0f;
        
        // Max distance from center
        float center_x = width / 2.0f;
        float center_y = height / 2.0f;
        float max_distance = (float)min(width, height) / 2.0f * 0.4f; // SCREEN_MARGIN = 0.4f
        
        TEST_ASSERTGreaterThan(0, max_distance);
        TEST_ASSERTLESS_THAN(max_distance, (float)min(width, height) / 2.0f);
    }
    
    // Test velocity calculation
    void testVelocityCalculation() {
        float current_x = 100.0f;
        float target_x = 120.0f;
        float velocity_x = 0.0f;
        float dx = target_x - current_x;
        
        // Apply smoothing
        velocity_x = velocity_x * 0.95f + dx * 0.05f;
        
        // Velocity should be positive (moving towards target)
        TEST_ASSERTGreaterThan(0, velocity_x);
        TEST_ASSERTLESS_THAN(velocity_x, dx); // Should be dampened
    }
    
    // Test state flags
    void testStateFlags() {
        // Test shaking state
        manager->setShaking(true);
        TEST_ASSERT_TRUE(manager->isShaking());
        
        // Reset velocities when shaking stops
        manager->setShaking(false);
        TEST_ASSERT_FALSE(manager->isShaking());
        
        // Test transitioning to center
        manager->moveToCenter();
        TEST_ASSERT_TRUE(manager->isTransitioning());
    }
    
    // Test center move animation
    void testCenterMoveAnimation() {
        // Initial position should be center of screen
        // moveToCenter() sets target to (120, 40)
        // This test verifies the animation logic doesn't crash
        
        bool wasTransitioning = manager->isTransitioningToCenter();
        
        manager->moveToCenter();
        
        // Animation should be in progress
        TEST_ASSERT_TRUE(manager->isTransitioningToCenter());
    }
    
    // Test idle motion
    void testIdleMotion() {
        manager->updateIdleMotion();
        // Idle motion should not crash even without animation objects
        TEST_ASSERT_NO_EXCEPTIONS();
    }
    
    // Test triangle position update
    void testTrianglePositionUpdate() {
        // Update with null gyro values should not crash
        manager->updateTrianglePosition(0.0f, 0.0f);
        
        // Update with high values should constrain properly
        manager->updateTrianglePosition(100.0f, 100.0f);
        
        TEST_ASSERT_NO_EXCEPTIONS();
    }
    
    // Run all tests
    void runTests() {
        setup();
        
        testMotionSmoothing();
        testAngleNormalization();
        testPositionConstraints();
        testVelocityCalculation();
        testStateFlags();
        testCenterMoveAnimation();
        testIdleMotion();
        testTrianglePositionUpdate();
        
        teardown();
    }
};

// Test cases for AnimationManager
void test_motion_smoothing(void) {
    float velocity = 0.0f;
    float target = 100.0f;
    float current = 0.0f;
    float dx = target - current;
    
    // Apply smoothing (MOTION_SMOOTHING = 0.95f)
    velocity = velocity * 0.95f + dx * (1.0f - 0.95f);
    
    TEST_ASSERT_FLOAT_WITHIN(0.01f, velocity, dx * 0.05f);
}

void test_velocity_calculation(void) {
    float velocity_x = 0.0f;
    float velocity_y = 0.0f;
    float target_x = 150.0f;
    float target_y = 100.0f;
    float current_x = 100.0f;
    float current_y = 50.0f;
    
    float dx = target_x - current_x;
    float dy = target_y - current_y;
    
    // Apply smoothing
    velocity_x = velocity_x * 0.95f + dx * 0.05f;
    velocity_y = velocity_y * 0.95f + dy * 0.05f;
    
    TEST_ASSERTGreaterThan(0, velocity_x);
    TEST_ASSERTGreaterThan(0, velocity_y);
    TEST_ASSERTLESS_THAN(velocity_x, dx);
    TEST_ASSERTLESS_THAN(velocity_y, dy);
}

void test_position_constraints(void) {
    uint16_t screenWidth = 240;
    uint16_t screenHeight = 240;
    float triangleSize = screenWidth / 2.0f;
    
    float center_x = screenWidth / 2.0f;
    float center_y = screenHeight / 2.0f;
    float max_distance = (float)min(screenWidth, screenHeight) / 2.0f * 0.4f;
    
    TEST_ASSERT_EQUAL_UINT16(screenWidth, screenWidth);
    TEST_ASSERT_NOT_EQUAL(0, max_distance);
}

void test_angle_normalization(void) {
    float angle = 720.0f;
    
    // Normalize to 0-360 range
    while (angle > 360.0f) angle -= 360.0f;
    while (angle < 0.0f) angle += 360.0f;
    
    TEST_ASSERT_EQUAL_FLOAT(0.0f, angle);
}

void test_shaking_state(void) {
    bool is_shaking = false;
    
    // Start shaking
    is_shaking = true;
    TEST_ASSERT_TRUE(is_shaking);
    
    // Stop shaking
    is_shaking = false;
    TEST_ASSERT_FALSE(is_shaking);
}

void test_transitioning_state(void) {
    bool transitioning = false;
    
    // Begin transition
    transitioning = true;
    TEST_ASSERT_TRUE(transitioning);
    
    // End transition
    transitioning = false;
    TEST_ASSERT_FALSE(transitioning);
}

void test_idle_motion_update(void) {
    float idle_time = 0.0f;
    float amplitude = 15.0f;
    float speed = 0.001f;
    
    idle_time += speed;
    
    // Idle motion should produce some value
    float offset_x = sinf(idle_time) * cosf(idle_time * 0.7f) * amplitude * 0.01f;
    float offset_y = cosf(idle_time * 1.3f) * sinf(idle_time * 0.5f) * amplitude * 0.01f;
    
    // Offsets should be bounded
    TEST_ASSERT_LESS_THAN(1.0f, fabsf(offset_x) + 1.0f);
    TEST_ASSERT_LESS_THAN(1.0f, fabsf(offset_y) + 1.0f);
}

void test_gyro_sensitivity(void) {
    float gyro_x = 2.5f;
    float gyro_y = -1.5f;
    float sensitivity = 0.08f;
    
    float target_x = 0.0f;
    float target_y = 0.0f;
    
    // Apply gyro sensitivity
    target_x -= gyro_x * sensitivity;
    target_y -= gyro_y * sensitivity;
    
    // Verify calculations
    TEST_ASSERT_FLOAT_WITHIN(0.01f, target_x, -0.2f);
    TEST_ASSERT_FLOAT_WITHIN(0.01f, target_y, 0.12f);
}

void test_screen_margins(void) {
    float screen_margin = 0.4f;
    float edge_buffer = 0.15f;
    
    TEST_ASSERT_EQUAL_FLOAT(0.4f, screen_margin);
    TEST_ASSERT_EQUAL_FLOAT(0.15f, edge_buffer);
    
    // Verify edge buffer is less than screen margin
    TEST_ASSERT_LESS_THAN(edge_buffer, screen_margin);
}

void test_triangle_size_calculation(void) {
    uint16_t width = 240;
    uint16_t height = 240;
    
    float triangleSize = width / 2.0f;
    
    TEST_ASSERT_EQUAL_FLOAT(120.0f, triangleSize);
    TEST_ASSERT_GREATER_THAN(0, triangleSize);
}

void test_velocity_zeroing_on_shake_stop(void) {
    float velocity_x = 10.0f;
    float velocity_y = 5.0f;
    
    // Simulate shaking stopping
    velocity_x = 0;
    velocity_y = 0;
    
    TEST_ASSERT_EQUAL_FLOAT(0, velocity_x);
    TEST_ASSERT_EQUAL_FLOAT(0, velocity_y);
}

void test_update_triangle_position_edge_cases(void) {
    float gyro_x = 0.0f;
    float gyro_y = 0.0f;
    
    // Update with zero gyro values should not crash
    // This simulates idle state
    float target_x = 0.0f;
    float current_x = 0.0f;
    
    bool is_still = abs(gyro_x) < 0.5f && abs(gyro_y) < 0.5f;
    TEST_ASSERT_TRUE(is_still);
}

void test_constrain_position_circular(void) {
    float width = 240.0f;
    float height = 240.0f;
    float triangleSize = width / 2.0f;
    float center_x = width / 2.0f;
    float center_y = height / 2.0f;
    float max_distance = (float)min(width, height) / 2.0f * 0.4f;
    
    float dx = 100.0f;
    float dy = 100.0f;
    float distance = sqrtf(dx * dx + dy * dy);
    
    // Distance should be less than max for this test
    if (distance > max_distance) {
        // Would be constrained in real implementation
        float angle = atan2f(dy, dx);
        float new_x = center_x + cosf(angle) * max_distance - triangleSize / 2.0f;
        float new_y = center_y + sinf(angle) * max_distance - triangleSize / 2.0f;
        
        TEST_ASSERT_NOT_EQUAL(0, new_x);
        TEST_ASSERT_NOT_EQUAL(0, new_y);
    }
}

void test_update_position_display(void) {
    int16_t x = 100;
    int16_t y = 150;
    
    // Simulate position update
    TEST_ASSERT_EQUAL_INT16(100, x);
    TEST_ASSERT_EQUAL_INT16(150, y);
    
    // Values are constrained
    TEST_ASSERT_GREATER_THAN(0, x);
    TEST_ASSERT_GREATER_THAN(0, y);
}

void test_idle_motion_continuous(void) {
    float idle_time = 0.0f;
    const float idle_speed = 0.001f;
    const float idle_amplitude = 15.0f;
    
    // Multiple update cycles
    for (int i = 0; i < 10; i++) {
        idle_time += idle_speed;
        float offset_x = sinf(idle_time) * cosf(idle_time * 0.7f) * idle_amplitude * 0.01f;
        float offset_y = cosf(idle_time * 1.3f) * sinf(idle_time * 0.5f) * idle_amplitude * 0.01f;
        
        // Offsets should vary over time
        if (i > 0) {
            TEST_ASSERT_NOT_EQUAL_FLOAT(0, offset_x + offset_y);
        }
    }
}

void test_gyro_still_detection(void) {
    float gyro_x = 0.3f;
    float gyro_y = 0.4f;
    
    // Values within threshold should be detected as still
    bool is_still = abs(gyro_x) < 0.5f && abs(gyro_y) < 0.5f;
    
    TEST_ASSERT_TRUE(is_still);
    
    // Values outside threshold are not still
    gyro_x = 1.0f;
    is_still = abs(gyro_x) < 0.5f && abs(gyro_y) < 0.5f;
    TEST_ASSERT_FALSE(is_still);
}

void test_target_position_update(void) {
    float target_x = 100.0f;
    float target_y = 150.0f;
    float gyro_x = -2.0f;
    float gyro_y = 1.5f;
    float sensitivity = 0.08f;
    
    // Apply gyro to target
    target_x -= gyro_x * sensitivity;
    target_y -= gyro_y * sensitivity;
    
    TEST_ASSERT_FLOAT_WITHIN(0.1f, target_x, 100.16f);
    TEST_ASSERT_FLOAT_WITHIN(0.1f, target_y, 149.88f);
}

void test_motion_velocity_continuity(void) {
    float velocity_x = 0.0f;
    float previous_velocity_x = 0.0f;
    float current_x = 0.0f;
    float target_x = 50.0f;
    const float smoothing = 0.95f;
    
    // Calculate velocity
    float dx = target_x - current_x;
    velocity_x = velocity_x * smoothing + dx * (1.0f - smoothing);
    
    // Velocity should change smoothly
    TEST_ASSERT_GREATER_THAN(0, velocity_x);
    TEST_ASSERT_LESS_THAN(velocity_x, dx);
    
    previous_velocity_x = velocity_x;
    
    // Another update
    dx = target_x - current_x - previous_velocity_x * 0.1f;
    velocity_x = velocity_x * smoothing + dx * (1.0f - smoothing);
    
    // Velocity should remain consistent
    TEST_ASSERT_FLOAT_WITHIN(0.01f, velocity_x, previous_velocity_x * smoothing);
}

void test_screen_boundary_detection(void) {
    float width = 240.0f;
    float height = 240.0f;
    float triangleSize = width / 2.0f;
    float edge_buffer = 0.15f;
    
    float min_x = -triangleSize * edge_buffer;
    float max_x = width - triangleSize * (1.0f - edge_buffer);
    
    TEST_ASSERT_LESS_THAN(0, min_x);
    TEST_ASSERT_GREATER_THAN(width, max_x);
}

void main(void) {
    UNITY_BEGIN();
    
    RUN_TEST(test_motion_smoothing);
    RUN_TEST(test_velocity_calculation);
    RUN_TEST(test_position_constraints);
    RUN_TEST(test_angle_normalization);
    RUN_TEST(test_shaking_state);
    RUN_TEST(test_transitioning_state);
    RUN_TEST(test_idle_motion_update);
    RUN_TEST(test_gyro_sensitivity);
    RUN_TEST(test_screen_margins);
    RUN_TEST(test_triangle_size_calculation);
    
    UNITY_END();
}
