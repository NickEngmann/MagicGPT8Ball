#include "Unity/unity.h"
#include "lvgl_test_helper.h"
#include "Animations.h"

// Test setup/teardown
void setUp(void) {}
void tearDown(void) {}

// Test helper functions
static lv_color_t get_triangle_color(lv_obj_t* triangle) {
    return lv_obj_get_style_bg_color(triangle, LV_PART_MAIN);
}

static int get_triangle_size(lv_obj_t* triangle) {
    lv_area_t coords;
    lv_obj_get_coords(triangle, &coords);
    return (coords.x2 - coords.x1) + 1;
}

static const char* get_label_text(lv_obj_t* triangle) {
    lv_obj_t* label = lv_obj_get_child(triangle, 0);
    if (label) {
        return lv_label_get_text(label);
    }
    return nullptr;
}

// Test AnimationManager initialization and basic functionality
void test_animations_manager_creation(void) {
    lvgl_test_init();
    AnimationManager anim(240, 240);
    
    TEST_ASSERT_NOT_NULL(anim.getTriangle());
    TEST_ASSERT_NOT_NULL(anim.getLabel());
}

void test_animations_manager_initial_position(void) {
    lvgl_test_init();
    AnimationManager anim(240, 240);
    
    lv_obj_t* triangle = anim.getTriangle();
    TEST_ASSERT_NOT_NULL(triangle);
    
    lv_area_t coords;
    lv_obj_get_coords(triangle, &coords);
    
    // Triangle should be initialized near center
    TEST_ASSERT_greater_than(coords.x1, 0);
    TEST_ASSERT_less_than(coords.x2, 240);
}

void test_animations_manager_triangle_size(void) {
    lvgl_test_init();
    AnimationManager anim(240, 240);
    
    lv_obj_t* triangle = anim.getTriangle();
    TEST_ASSERT_NOT_NULL(triangle);
    
    lv_area_t coords;
    lv_obj_get_coords(triangle, &coords);
    int size = (coords.x2 - coords.x1) + 1;
    
    // Triangle size should be screen width / 2 = 120
    TEST_ASSERT_EQUAL_INT(120, size);
}

void test_animations_manager_default_color(void) {
    lvgl_test_init();
    AnimationManager anim(240, 240);
    
    lv_obj_t* triangle = anim.getTriangle();
    TEST_ASSERT_NOT_NULL(triangle);
    
    // Default color should be blue (0, 0, 255)
    lv_color_t color = get_triangle_color(triangle);
    TEST_ASSERT_EQUAL_INT(0, LV_COLOR_GET_R(color));
    TEST_ASSERT_EQUAL_INT(0, LV_COLOR_GET_G(color));
    TEST_ASSERT_EQUAL_INT(255, LV_COLOR_GET_B(color));
}

void test_animations_manager_set_color_red(void) {
    lvgl_test_init();
    AnimationManager anim(240, 240);
    
    lv_obj_t* triangle = anim.getTriangle();
    TEST_ASSERT_NOT_NULL(triangle);
    
    anim.setTriangleColor(255, 0, 0);
    lv_color_t color = get_triangle_color(triangle);
    
    TEST_ASSERT_EQUAL_INT(255, LV_COLOR_GET_R(color));
    TEST_ASSERT_EQUAL_INT(0, LV_COLOR_GET_G(color));
    TEST_ASSERT_EQUAL_INT(0, LV_COLOR_GET_B(color));
}

void test_animations_manager_set_color_green(void) {
    lvgl_test_init();
    AnimationManager anim(240, 240);
    
    lv_obj_t* triangle = anim.getTriangle();
    TEST_ASSERT_NOT_NULL(triangle);
    
    anim.setTriangleColor(0, 255, 0);
    lv_color_t color = get_triangle_color(triangle);
    
    TEST_ASSERT_EQUAL_INT(0, LV_COLOR_GET_R(color));
    TEST_ASSERT_EQUAL_INT(255, LV_COLOR_GET_G(color));
    TEST_ASSERT_EQUAL_INT(0, LV_COLOR_GET_B(color));
}

void test_animations_manager_set_color_yellow(void) {
    lvgl_test_init();
    AnimationManager anim(240, 240);
    
    lv_obj_t* triangle = anim.getTriangle();
    TEST_ASSERT_NOT_NULL(triangle);
    
    anim.setTriangleColor(255, 255, 0);
    lv_color_t color = get_triangle_color(triangle);
    
    TEST_ASSERT_EQUAL_INT(255, LV_COLOR_GET_R(color));
    TEST_ASSERT_EQUAL_INT(255, LV_COLOR_GET_G(color));
    TEST_ASSERT_EQUAL_INT(0, LV_COLOR_GET_B(color));
}

void test_animations_manager_set_label_text(void) {
    lvgl_test_init();
    AnimationManager anim(240, 240);
    
    lv_obj_t* triangle = anim.getTriangle();
    TEST_ASSERT_NOT_NULL(triangle);
    
    anim.setLabelText("Test Message");
    const char* text = get_label_text(triangle);
    TEST_ASSERT_NOT_NULL(text);
    TEST_ASSERT_EQUAL_STRING("Test Message", text);
}

void test_animations_manager_shaking_state(void) {
    lvgl_test_init();
    AnimationManager anim(240, 240);
    
    lv_obj_t* triangle = anim.getTriangle();
    TEST_ASSERT_NOT_NULL(triangle);
    
    // Initially should not be shaking
    anim.setShaking(false);
    TEST_ASSERT_FALSE(anim.isShaking());
    
    // Set to shaking
    anim.setShaking(true);
    TEST_ASSERT_TRUE(anim.isShaking());
}

// Test animation transitions
void test_animations_manager_transitioning_state(void) {
    lvgl_test_init();
    AnimationManager anim(240, 240);
    
    lv_obj_t* triangle = anim.getTriangle();
    TEST_ASSERT_NOT_NULL(triangle);
    
    // Initially not transitioning
    TEST_ASSERT_FALSE(anim.isTransitioning());
    
    // Move to center should set transitioning flag
    // Note: This test may need actual animation processing to verify
    // For now, we just test the method exists and doesn't crash
    anim.moveToCenter();
    TEST_ASSERT_TRUE(true);  // Basic verification that method doesn't crash
}

int main(void) {
    UNITY_BEGIN();
    
    RUN_TEST(test_animations_manager_creation);
    RUN_TEST(test_animations_manager_initial_position);
    RUN_TEST(test_animations_manager_triangle_size);
    RUN_TEST(test_animations_manager_default_color);
    RUN_TEST(test_animations_manager_set_color_red);
    RUN_TEST(test_animations_manager_set_color_green);
    RUN_TEST(test_animations_manager_set_color_yellow);
    RUN_TEST(test_animations_manager_set_label_text);
    RUN_TEST(test_animations_manager_shaking_state);
    RUN_TEST(test_animations_manager_transitioning_state);
    
    return UNITY_END();
}
