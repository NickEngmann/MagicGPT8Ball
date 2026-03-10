#include "lvgl_test_helper.h"
#include "../src/Animations.h"
#include <Arduino.h>

// Mock Arduino functions for testing
extern "C" {
  uint32_t millis() { return 1000; }
  uint32_t micros() { return 1000; }
  void delay(uint32_t ms) {}
  void delayMicroseconds(uint32_t us) {}
  void randomSeed(uint32_t seed) {}
  int random(int max) { return 0; }
  int random(int min, int max) { return min; }
}

// Test AnimationManager initialization
TEST(test_animation_manager_initialization) {
  AnimationManager anim(240, 240);
  
  // Test that constructor creates valid objects
  TEST_ASSERT_NOT_NULL(anim.getTriangle());
  TEST_ASSERT_NOT_NULL(anim.getLabel());
  
  // Test initial state
  TEST_ASSERT_FALSE(anim.isShaking());
  TEST_ASSERT_FALSE(anim.isTransitioning());
}

// Test animation state changes
TEST(test_animation_state_changes) {
  AnimationManager anim(240, 240);
  
  // Test shaking state
  anim.setShaking(true);
  TEST_ASSERT_TRUE(anim.isShaking());
  
  anim.setShaking(false);
  TEST_ASSERT_FALSE(anim.isShaking());
}

// Test label text setting
TEST(test_label_text_setting) {
  AnimationManager anim(240, 240);
  
  // Test setting label text
  anim.setLabelText("Test Response");
  
  // Verify the label object exists and has text
  TEST_ASSERT_NOT_NULL(anim.getLabel());
  
  // Test formatted label text
  anim.setLabelTextFormatted("Value: %d", 42);
  TEST_ASSERT_NOT_NULL(anim.getLabel());
}

// Test triangle color setting
TEST(test_triangle_color_setting) {
  AnimationManager anim(240, 240);
  
  // Test setting different colors
  anim.setTriangleColor(255, 0, 0);  // Red
  anim.setTriangleColor(0, 255, 0);  // Green
  anim.setTriangleColor(0, 0, 255);  // Blue
  
  // Verify triangle object still exists
  TEST_ASSERT_NOT_NULL(anim.getTriangle());
}

// Test movement animation
TEST(test_movement_animation) {
  AnimationManager anim(240, 240);
  
  // Test moving to center
  anim.moveToCenter();
  TEST_ASSERT_FALSE(anim.isTransitioning());
  
  // Test idle motion update
  anim.updateIdleMotion();
  
  // Test position update with gyro values
  anim.updateTrianglePosition(0.5f, 0.3f);
}

// Test display flush callback
TEST(test_display_flush_callback) {
  // Verify the static callback function exists and is callable
  lv_area_t area;
  area.x1 = 0;
  area.y1 = 0;
  area.x2 = 239;
  area.y2 = 239;
  
  lv_color_t color = lv_color_make(255, 0, 0);
  
  // This should not crash
  AnimationManager::displayFlushCallback(nullptr, &area, &color);
  TEST_ASSERT_TRUE(true);  // If we get here, no crash occurred
}
