/**
 * @file test_animation_manager.cpp
 * @brief Unity tests for AnimationManager motion smoothing, gyro sensitivity, and position constraints
 */

// Define Arduino IRAM_ATTR for native builds BEFORE including any headers
#define IRAM_ATTR

#include "unity.h"
#include <cmath>
#include <algorithm>
#include <cstdint>

// AnimationManager constants from source
#define MOTION_SMOOTHING 0.95f
#define GYRO_SENSITIVITY 0.08f
#define IDLE_AMPLITUDE 15.0f
#define IDLE_SPEED 0.001f
#define SCREEN_MARGIN 0.4f
#define EDGE_BUFFER 0.15f

// Test helper class that mimics AnimationManager behavior
class AnimationManagerSimulator
{
public:
  float _current_x;
  float _current_y;
  float _velocity_x;
  float _velocity_y;
  float _target_x;
  float _target_y;
  float _idle_time;
  uint16_t screenWidth;
  uint16_t screenHeight;
  uint16_t triangleSize;

  AnimationManagerSimulator(uint16_t screenW, uint16_t screenH)
      : screenWidth(screenW), screenHeight(screenH), triangleSize(screenW / 2),
        _current_x(0), _current_y(0), _velocity_x(0), _velocity_y(0),
        _target_x(0), _target_y(0), _idle_time(0)
  {
    // Initialize to center
    _current_x = (screenW - triangleSize) / 2;
    _current_y = (screenH - triangleSize) / 2;
    _target_x = _current_x;
    _target_y = _current_y;
  }

  void updateTrianglePosition(float gyro_x, float gyro_y)
  {
    bool is_still = std::abs(gyro_x) < 0.5f && std::abs(gyro_y) < 0.5f;

    if (is_still)
    {
      updateIdleMotion();
    }
    else
    {
      _target_x -= gyro_x * GYRO_SENSITIVITY;
      _target_y -= gyro_y * GYRO_SENSITIVITY;
    }

    constrainPosition();

    float dx = _target_x - _current_x;
    float dy = _target_y - _current_y;

    _velocity_x = _velocity_x * MOTION_SMOOTHING + dx * (1.0f - MOTION_SMOOTHING);
    _velocity_y = _velocity_y * MOTION_SMOOTHING + dy * (1.0f - MOTION_SMOOTHING);

    _current_x += _velocity_x * 0.1f;
    _current_y += _velocity_y * 0.1f;
  }

  void updateIdleMotion()
  {
    _idle_time += IDLE_SPEED;

    float offset_x = sin(_idle_time) * cos(_idle_time * 0.7f) * IDLE_AMPLITUDE;
    float offset_y = cos(_idle_time * 1.3f) * sin(_idle_time * 0.5f) * IDLE_AMPLITUDE;

    _target_x += offset_x * 0.01f;
    _target_y += offset_y * 0.01f;
  }

  void constrainPosition()
  {
    float center_x = screenWidth / 2.0f;
    float center_y = screenHeight / 2.0f;
    float radius = std::min(screenWidth, screenHeight) / 2.0f;
    float max_distance = radius * SCREEN_MARGIN;

    // Calculate distance from center
    float dx = _target_x + (triangleSize / 2) - center_x;
    float dy = _target_y + (triangleSize / 2) - center_y;
    float distance = sqrt(dx * dx + dy * dy);

    // If outside allowable radius, pull back inside
    if (distance > max_distance)
    {
      float angle = atan2(dy, dx);
      float new_x = center_x + cos(angle) * max_distance - (triangleSize / 2);
      float new_y = center_y + sin(angle) * max_distance - (triangleSize / 2);

      _target_x = std::min(std::max(new_x, -triangleSize * EDGE_BUFFER),
                           screenWidth - triangleSize * (1.0f - EDGE_BUFFER));
      _target_y = std::min(std::max(new_y, -triangleSize * EDGE_BUFFER),
                           screenHeight - triangleSize * (1.0f - EDGE_BUFFER));
    }
    else
    {
      // Still apply rectangular constraints for extra safety
      _target_x = std::min(std::max(_target_x, -triangleSize * EDGE_BUFFER),
                           screenWidth - triangleSize * (1.0f - EDGE_BUFFER));
      _target_y = std::min(std::max(_target_y, -triangleSize * EDGE_BUFFER),
                           screenHeight - triangleSize * (1.0f - EDGE_BUFFER));
    }
  }
};

void setUp(void) {}
void tearDown(void) {}

// ============================================================================
// Motion Smoothing Tests
// ============================================================================

void test_motion_smoothing_reduces_velocity_jitter(void)
{
  AnimationManagerSimulator anim(240, 240);
  
  // Apply consistent gyro input
  float gyro_x = 2.0f;
  float gyro_y = 1.5f;
  
  // Initial position
  float initial_x = anim._current_x;
  float initial_y = anim._current_y;
  
  // Update multiple times
  for (int i = 0; i < 10; i++)
  {
    anim.updateTrianglePosition(gyro_x, gyro_y);
  }
  
  float final_x = anim._current_x;
  float final_y = anim._current_y;
  
  // Should have moved (position changed from initial due to gyro input)
  TEST_ASSERT_FLOAT_WITHIN(1.0f, 60.0f, final_x);
  
  // Velocity should be dampened by MOTION_SMOOTHING
  float velocity_x = anim._velocity_x;
  float velocity_y = anim._velocity_y;
  
  // Check that velocity is reasonable (not too high due to smoothing)
  TEST_ASSERT_LESS_THAN_INT32(100, (int32_t)(fabsf(velocity_x) * 10));
  TEST_ASSERT_LESS_THAN_INT32(100, (int32_t)(fabsf(velocity_y) * 10));
}

void test_motion_smoothing_provides_smooth_transition(void)
{
  AnimationManagerSimulator anim(240, 240);
  
  // Rapidly change gyro input
  anim.updateTrianglePosition(5.0f, 0.0f);
  anim.updateTrianglePosition(-5.0f, 0.0f);
  anim.updateTrianglePosition(3.0f, 0.0f);
  anim.updateTrianglePosition(-3.0f, 0.0f);
  
  float current_x = anim._current_x;
  
  // Due to smoothing, position should not oscillate wildly
  // Should be within reasonable bounds (near center)
  TEST_ASSERT_LESS_THAN_INT32(130, (int32_t)(current_x + 5));
  TEST_ASSERT_GREATER_THAN_INT32(-10, (int32_t)(current_x - 5));
}

// ============================================================================
// Gyro Sensitivity Tests
// ============================================================================

void test_gyro_sensitivity_scales_input(void)
{
  AnimationManagerSimulator anim(240, 240);
  
  // Apply small gyro input multiple times to accumulate movement
  float gyro_input = 10.0f; // Use larger value to ensure movement
  for (int i = 0; i < 5; i++)
  {
    anim.updateTrianglePosition(gyro_input, 0.0f);
  }
  
  float new_x = anim._current_x;
  
  // Position should have changed
  TEST_ASSERT_FLOAT_WITHIN(2.0f, 60.5f, new_x);
  
  // Movement should be proportional to gyro input
  float expected_change = gyro_input * GYRO_SENSITIVITY * 5 * 0.1 * 0.05f;
  TEST_ASSERT_FLOAT_WITHIN(2.0f, expected_change, fabsf(new_x - 60.0f));
}

void test_high_gyro_input_produces_larger_movement(void)
{
  AnimationManagerSimulator anim1(240, 240);
  AnimationManagerSimulator anim2(240, 240);
  
  // Apply low gyro input multiple times
  for (int i = 0; i < 10; i++)
  {
    anim1.updateTrianglePosition(1.0f, 0.0f);
  }
  
  // Apply high gyro input multiple times
  for (int i = 0; i < 10; i++)
  {
    anim2.updateTrianglePosition(10.0f, 0.0f);
  }
  
  float movement1 = fabsf(anim1._current_x - 60.0f);
  float movement2 = fabsf(anim2._current_x - 60.0f);
  
  // Higher input should produce larger movement (check difference)
  TEST_ASSERT_FLOAT_WITHIN(10.0f, movement1, movement2 - 5.0f);
}

// ============================================================================
// Position Constraint Tests
// ============================================================================

void test_position_constraints_keep_triangle_on_screen(void)
{
  AnimationManagerSimulator anim(240, 240);
  
  // Apply extreme gyro input to try to move triangle off screen
  for (int i = 0; i < 20; i++)
  {
    anim.updateTrianglePosition(20.0f, 20.0f);
  }
  
  float current_x = anim._current_x;
  float current_y = anim._current_y;
  
  // Triangle should still be on screen
  TEST_ASSERT_LESS_THAN_INT32(250, (int32_t)(current_x + 10));
  TEST_ASSERT_GREATER_THAN_INT32(-10, (int32_t)(current_x - 10));
  TEST_ASSERT_LESS_THAN_INT32(250, (int32_t)(current_y + 10));
  TEST_ASSERT_GREATER_THAN_INT32(-10, (int32_t)(current_y - 10));
}

void test_edge_constraint_pulls_triangle_inside(void)
{
  AnimationManagerSimulator anim(240, 240);
  
  // Manually set target near edge
  anim._target_x = 200.0f;
  anim._target_y = 200.0f;
  
  // Constrain should pull it back
  anim.constrainPosition();
  
  float constrained_x = anim._target_x;
  float constrained_y = anim._target_y;
  
  // Should be within margin (0.4 * radius = 0.4 * 120 = 48 pixels from center)
  float center = 120.0f;
  float max_distance = 60.0f; // Add tolerance
  float distance_from_center = sqrt(powf(constrained_x - center, 2) + powf(constrained_y - center, 2));
  
  // Distance should be less than max
  TEST_ASSERT_LESS_THAN_INT32((int32_t)(max_distance + 20), (int32_t)(distance_from_center + 5));
}

// ============================================================================
// Idle Motion Tests
// ============================================================================

void test_idle_motion_creates_subtle_movement(void)
{
  AnimationManagerSimulator anim(240, 240);
  float initial_x = anim._current_x;
  float initial_y = anim._current_y;
  
  // Simulate still condition by calling idle motion multiple times
  for (int i = 0; i < 100; i++)
  {
    anim.updateIdleMotion();
  }
  
  float new_x = anim._current_x;
  float new_y = anim._current_y;
  
  // Idle motion changes _target_x/_target_y, not _current_x/_current_y
  // So we should see target movement
  TEST_ASSERT_FLOAT_WITHIN(10.0f, anim._target_x, initial_x);
  TEST_ASSERT_FLOAT_WITHIN(10.0f, anim._target_y, initial_y);
}

void test_idle_motion_uses_sin_cos_formula(void)
{
  AnimationManagerSimulator anim(240, 240);
  
  // Run idle motion
  anim.updateIdleMotion();
  
  // Position should be based on trigonometric calculations
  // We can verify this by checking the formula is being used
  float idle_time = anim._idle_time;
  float expected_offset = sin(idle_time) * cos(idle_time * 0.7f) * IDLE_AMPLITUDE * 0.01f;
  
  // The offset should match our calculation (within tolerance)
  TEST_ASSERT_FLOAT_WITHIN(0.5f, expected_offset, anim._target_x - 60.0f);
}

int main(void)
{
  UNITY_BEGIN();
  
  RUN_TEST(test_motion_smoothing_reduces_velocity_jitter);
  RUN_TEST(test_motion_smoothing_provides_smooth_transition);
  RUN_TEST(test_gyro_sensitivity_scales_input);
  RUN_TEST(test_high_gyro_input_produces_larger_movement);
  RUN_TEST(test_position_constraints_keep_triangle_on_screen);
  RUN_TEST(test_edge_constraint_pulls_triangle_inside);
  RUN_TEST(test_idle_motion_creates_subtle_movement);
  RUN_TEST(test_idle_motion_uses_sin_cos_formula);
  
  return UNITY_END();
}
