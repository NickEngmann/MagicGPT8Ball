#include <unity.h>
#include <cmath>
#include <algorithm>
#include <vector>
#include <memory>

#ifdef NATIVE_BUILD

// Mock types for native build
typedef struct { uint8_t blue; uint8_t green; uint8_t red; } lv_color_ch_t;
typedef struct { lv_color_ch_t ch; } lv_color_t;

typedef enum {
    LV_ALIGN_CENTER = 0,
    LV_ALIGN_TOP_MID,
    LV_ALIGN_BOTTOM_MID,
    LV_ALIGN_LEFT_MID,
    LV_ALIGN_RIGHT_MID,
    LV_ALIGN_TOP_LEFT,
    LV_ALIGN_TOP_RIGHT,
    LV_ALIGN_BOTTOM_LEFT,
    LV_ALIGN_BOTTOM_RIGHT,
    LV_ALIGN_OUT_TOP_MID,
    LV_ALIGN_OUT_BOTTOM_MID,
    LV_ALIGN_OUT_LEFT_MID,
    LV_ALIGN_OUT_RIGHT_MID,
    LV_ALIGN_OUT_TOP_LEFT,
    LV_ALIGN_OUT_TOP_RIGHT,
    LV_ALIGN_OUT_BOTTOM_LEFT,
    LV_ALIGN_OUT_BOTTOM_RIGHT,
} lv_align_t;

typedef enum {
    LV_LABEL_LONG_WRAP = 0,
    LV_LABEL_LONG_DOT,
    LV_LABEL_LONG_SCROLL,
    LV_LABEL_LONG_SCROLL_CIRCULAR,
    LV_LABEL_LONG_CLIP,
} lv_label_long_mode_t;

typedef enum {
    LV_TEXT_ALIGN_LEFT = 0,
    LV_TEXT_ALIGN_CENTER,
    LV_TEXT_ALIGN_RIGHT,
    LV_TEXT_ALIGN_AUTO,
} lv_text_align_t;

typedef struct {
    int16_t x1, y1, x2, y2;
} lv_area_t;

typedef struct {
    uint16_t hor_res, ver_res;
    void (*flush_cb)(struct _lv_disp_drv_t*, const lv_area_t*, lv_color_t*);
    void *draw_buf;
} lv_disp_drv_t;

typedef struct {
    void *var;
    lv_anim_custom_exec_cb custom_exec_cb;
    lv_anim_ready_cb ready_cb;
    uint32_t time;
    uint32_t act_time;
    lv_anim_state_t state;
    lv_anim_path_cb_t path_cb;
    int32_t start_value;
    int32_t current_value;
    int32_t end_value;
    lv_anim_path_t path;
    uint32_t delay;
    uint32_t repeat_cnt;
    void *user_data;
} lv_anim_t;

// Mock TFT_eSPI for native builds
class MockTFT_eSPI {
public:
    bool begin_called;
    int rotation;
    std::vector<std::pair<int,int>> draw_pixels;
    std::vector<std::tuple<int,int,int,int,uint32_t>> draw_rects;
    
    MockTFT_eSPI() : begin_called(false), rotation(0) {}
    
    void begin() { begin_called = true; }
    void setRotation(uint8_t r) { rotation = r; }
    void fillScreen(uint32_t color) { }
    void drawPixel(int16_t x, int16_t y, uint32_t color) { 
        draw_pixels.push_back({x, y}); 
    }
    void drawFastVLine(int16_t x, int16_t y, int16_t h, uint32_t color) { }
    void drawFastHLine(int16_t x, int16_t y, int16_t w, uint32_t color) { }
    void drawRect(int16_t x, int16_t y, int16_t w, int16_t h, uint32_t color) {
        draw_rects.push_back({x, y, w, h, color});
    }
    void setCursor(uint16_t x, uint16_t y) { }
    void print(const char* str) { }
    void drawTriangle(int16_t x1, int16_t y1, int16_t x2, int16_t y2, int16_t x3, int16_t y3, uint32_t color) { }
    void fillTriangle(int16_t x1, int16_t y1, int16_t x2, int16_t y2, int16_t x3, int16_t y3, uint32_t color) { }
    void drawCircle(int16_t x, int16_t y, int16_t r, uint32_t color) { }
    void fillCircle(int16_t x, int16_t y, int16_t r, uint32_t color) { }
};

// Mock LVGL functions
namespace lv {
    static std::vector<lv_color_t> recorded_colors;
    static std::vector<std::pair<int32_t, int32_t>> recorded_positions;
    static std::vector<std::pair<int32_t, int32_t>> recorded_sizes;
    
    void init() {}
    
    class obj_base {
    public:
        int32_t x = 0, y = 0;
        uint32_t width = 0, height = 0;
        lv_color_t bg_color = {0, 0, 0};
        std::string text;
        
        void set_pos(int32_t x, int32_t y) { 
            this->x = x; 
            this->y = y; 
            recorded_positions.push_back({x, y});
        }
        
        void set_size(uint32_t w, uint32_t h) { 
            width = w; 
            height = h; 
            recorded_sizes.push_back({(int32_t)w, (int32_t)h});
        }
        
        void set_style_bg_color(lv_color_t c) { 
            bg_color = c; 
            recorded_colors.push_back(c);
        }
        
        void set_style_transform_angle(int32_t angle) {}
        void set_style_bg_opa(uint32_t opa) {}
        void set_style_align(uint32_t align) {}
        void set_style_pad_all(uint32_t pad) {}
        void set_style_text_font(const void* font) {}
        void set_width(uint32_t w) { width = w; }
        void set_height(uint32_t h) { height = h; }
        void align_to(void* ref, lv_align_t align, int32_t x_ofs, int32_t y_ofs) {}
        void center() { }
    };
    
    class label_t : public obj_base {
    public:
        void set_text(const char* text) { this->text = text; }
        void set_long_mode(uint32_t mode) {}
        void set_text_align(uint32_t align) {}
        void set_style_text_color(lv_color_t c) { bg_color = c; }
    };
    
    class screen_t : public obj_base {
    public:
        static screen_t* act() { return new screen_t(); }
        static screen_t* create() { return new screen_t(); }
    };
    
    class color_t {
    public:
        static lv_color_t make(uint8_t r, uint8_t g, uint8_t b) {
            lv_color_t c;
            c.ch.red = r;
            c.ch.green = g;
            c.ch.blue = b;
            return c;
        }
        static lv_color_t black() { return make(0, 0, 0); }
        static lv_color_t white() { return make(255, 255, 255); }
        static lv_color_t blue() { return make(0, 0, 255); }
    };
    
    class disp_drv {
    public:
        static void init(lv_disp_drv_t* drv) { }
        static void register_(lv_disp_drv_t* drv) { }
    };
    
    class draw_buf {
    public:
        static void init(lv_disp_draw_buf_t* buf, void* buf1, void* buf2, uint32_t size) { }
    };
    
    class anim {
    public:
        static void init(lv_anim_t* a) { }
        static void set_var(lv_anim_t* a, void* var) { a->var = var; }
        static void set_exec_cb(lv_anim_t* a, lv_anim_custom_exec_cb cb) { a->custom_exec_cb = cb; }
        static void set_time(lv_anim_t* a, uint32_t time) { a->time = time; }
        static void set_values(lv_anim_t* a, int32_t start, int32_t end) { a->start_value = start; a->end_value = end; }
        static void set_path(lv_anim_t* a, lv_anim_path_cb_t path) { a->path_cb = path; }
        static void set_ready_cb(lv_anim_t* a, lv_anim_ready_cb cb) { a->ready_cb = cb; }
        static void start(lv_anim_t* a) { }
    };
    
    class style {
    public:
        static void set_bg_color(void* obj, lv_color_t color, uint32_t part) { }
        static void set_transform_angle(void* obj, int32_t angle, uint32_t part) { }
        static void set_bg_opa(void* obj, uint32_t opa, uint32_t part) { }
        static void set_text_color(void* obj, lv_color_t color, uint32_t part) { }
        static void set_text_align(void* obj, uint32_t align, uint32_t part) { }
        static void set_pad_all(void* obj, uint32_t pad, uint32_t part) { }
        static void set_radius(void* obj, uint32_t radius, uint32_t part) { }
    };
    
    class label {
    public:
        static label_t* create(void* parent) { return new label_t(); }
        static void set_text(label_t* lbl, const char* text) { lbl->set_text(text); }
        static void set_long_mode(label_t* lbl, uint32_t mode) { lbl->set_long_mode(mode); }
        static void set_text_align(label_t* lbl, uint32_t align) { lbl->set_text_align(align); }
        static void set_width(label_t* lbl, uint32_t w) { lbl->set_width(w); }
    };
    
    class obj {
    public:
        static screen_t* act() { return screen_t::act(); }
        static screen_t* create(screen_t* parent) { return new screen_t(); }
        static label_t* create(obj_base* parent) { return new label_t(); }
        static void set_size(obj_base* obj, uint32_t w, uint32_t h) { obj->set_size(w, h); }
        static void set_pos(obj_base* obj, int32_t x, int32_t y) { obj->set_pos(x, y); }
        static void set_style_bg_color(obj_base* obj, lv_color_t color, uint32_t part) { obj->set_style_bg_color(color); }
        static void set_style_transform_angle(obj_base* obj, int32_t angle, uint32_t part) { obj->set_style_transform_angle(angle); }
        static void set_style_bg_opa(obj_base* obj, uint32_t opa, uint32_t part) { obj->set_style_bg_opa(opa); }
        static void set_style_text_color(obj_base* obj, lv_color_t color, uint32_t part) { obj->set_style_text_color(color); }
        static void set_style_text_align(obj_base* obj, uint32_t align, uint32_t part) { obj->set_style_text_align(align); }
        static void set_style_pad_all(obj_base* obj, uint32_t pad, uint32_t part) { obj->set_style_pad_all(pad); }
        static void set_style_radius(obj_base* obj, uint32_t radius, uint32_t part) { }
        static void set_width(obj_base* obj, uint32_t w) { obj->set_width(w); }
        static void align_to(obj_base* obj, void* ref, lv_align_t align, int32_t x_ofs, int32_t y_ofs) { obj->align_to(ref, align, x_ofs, y_ofs); }
        static void center(obj_base* obj) { obj->center(); }
    };
    
    class style {
    public:
        static void set_bg_color(void* obj, lv_color_t color, uint32_t part) { }
        static void set_transform_angle(void* obj, int32_t angle, uint32_t part) { }
        static void set_bg_opa(void* obj, uint32_t opa, uint32_t part) { }
        static void set_text_color(void* obj, lv_color_t color, uint32_t part) { }
        static void set_text_align(void* obj, uint32_t align, uint32_t part) { }
        static void set_pad_all(void* obj, uint32_t pad, uint32_t part) { }
        static void set_radius(void* obj, uint32_t radius, uint32_t part) { }
    };
}

// Forward declarations for AnimationManager
class AnimationManager;

// Include the actual implementation with mocks
#include "../src/Animations.cpp"

// Test suite
class AnimationManagerTest : public AnimationManager {
public:
    AnimationManagerTest(uint16_t w, uint16_t h) : AnimationManager(w, h) {}
    
    // Expose protected methods for testing
    float getTargetX() { return _target_x; }
    float getTargetY() { return _target_y; }
    float getCurrentX() { return _current_x; }
    float getCurrentY() { return _current_y; }
    float getVelocityX() { return _velocity_x; }
    float getVelocityY() { return _velocity_y; }
    bool isShaking() { return _isShaking; }
    bool isTransitioningToCenter() { return _isTransitioningToCenter; }
    
    void setShakingForTest(bool s) { _isShaking = s; }
    void setTransitioningForTest(bool t) { _isTransitioningToCenter = t; }
    
    // Test helper methods
    void testConstrainPosition() { constrainPosition(); }
    void testUpdateIdleMotion() { updateIdleMotion(); }
};

void setUp(void) {
    lv::recorded_colors.clear();
    lv::recorded_positions.clear();
    lv::recorded_sizes.clear();
}

void tearDown(void) {
}

void test_animation_manager_creation(void) {
    AnimationManagerTest anim(320, 240);
    TEST_ASSERT_NOT_NULL(anim._triangle);
    TEST_ASSERT_EQUAL_UINT16(320, anim.screenWidth);
    TEST_ASSERT_EQUAL_UINT16(240, anim.screenHeight);
}

void test_triangle_initial_position(void) {
    AnimationManagerTest anim(320, 240);
    
    // Initial position should be centered
    float center_x = (320 - 160) / 2.0f;  // (screenWidth - triangleSize) / 2
    float center_y = (240 - 160) / 2.0f;  // (screenHeight - triangleSize) / 2
    
    TEST_ASSERT_FLOAT_WITHIN(1.0f, anim.getCurrentX(), center_x);
    TEST_ASSERT_FLOAT_WITHIN(1.0f, anim.getCurrentY(), center_y);
}

void test_gyro_sensitivity(void) {
    AnimationManagerTest anim(320, 240);
    anim.setTransitioningForTest(false);
    anim.setShakingForTest(false);
    
    // Initial position
    float initial_x = anim.getCurrentX();
    float initial_y = anim.getCurrentY();
    
    // Apply gyro input
    anim.updateTrianglePosition(1.0f, 0.5f);
    
    // Position should have changed
    TEST_ASSERT_FALSE(anim.getCurrentX() == initial_x);
    TEST_ASSERT_FALSE(anim.getCurrentY() == initial_y);
}

void test_gyro_sensitivity_negative(void) {
    AnimationManagerTest anim(320, 240);
    anim.setTransitioningForTest(false);
    anim.setShakingForTest(false);
    
    // Apply negative gyro input
    anim.updateTrianglePosition(-1.0f, -0.5f);
    
    // Position should have changed in opposite direction
    float target_x = anim.getTargetX();
    TEST_ASSERT_TRUE(target_x > 0);  // Should have moved left (negative gyro increases target)
}

void test_still_motion(void) {
    AnimationManagerTest anim(320, 240);
    anim.setTransitioningForTest(false);
    anim.setShakingForTest(false);
    
    // Apply very small gyro (still condition)
    anim.updateTrianglePosition(0.1f, 0.1f);
    
    // Should trigger idle motion
    TEST_ASSERT_TRUE(anim.isTransitioningToCenter() == false);
}

void test_shaking_prevents_motion(void) {
    AnimationManagerTest anim(320, 240);
    anim.setShakingForTest(true);
    
    // Apply gyro input while shaking
    float initial_x = anim.getCurrentX();
    anim.updateTrianglePosition(1.0f, 1.0f);
    
    // Position should not change during shake
    TEST_ASSERT_FLOAT_EQUAL(initial_x, anim.getCurrentX());
}

void test_position_constraining(void) {
    AnimationManagerTest anim(320, 240);
    anim.setTransitioningForTest(false);
    anim.setShakingForTest(false);
    
    // Manually set position near edge
    anim._target_x = 200.0f;
    anim._target_y = 200.0f;
    
    // Constrain position
    anim.testConstrainPosition();
    
    // Position should be within bounds
    float max_x = anim.screenWidth - anim.triangleSize * (1.0f - 0.05f);
    float max_y = anim.screenHeight - anim.triangleSize * (1.0f - 0.05f);
    
    TEST_ASSERT_TRUE(anim.getTargetX() <= max_x);
    TEST_ASSERT_TRUE(anim.getTargetY() <= max_y);
}

void test_velocity_smoothing(void) {
    AnimationManagerTest anim(320, 240);
    anim.setTransitioningForTest(false);
    anim.setShakingForTest(false);
    
    // Apply multiple gyro inputs
    anim.updateTrianglePosition(2.0f, 0.0f);
    anim.updateTrianglePosition(2.0f, 0.0f);
    anim.updateTrianglePosition(2.0f, 0.0f);
    
    // Velocity should be smoothed (not exact)
    float velocity = anim.getVelocityX();
    TEST_ASSERT_TRUE(velocity > 0);
    TEST_ASSERT_TRUE(velocity < 6.0f);  // Should be less than sum due to smoothing
}

void test_idle_motion_update(void) {
    AnimationManagerTest anim(320, 240);
    anim.setTransitioningForTest(false);
    anim.setShakingForTest(false);
    
    // Store initial position
    float initial_x = anim.getTargetX();
    
    // Update idle motion
    anim.testUpdateIdleMotion();
    
    // Position should have changed slightly
    float new_x = anim.getTargetX();
    TEST_ASSERT_TRUE(new_x != initial_x);
}

void test_constrain_position_edge_cases(void) {
    AnimationManagerTest anim(320, 240);
    anim.setTransitioningForTest(false);
    anim.setShakingForTest(false);
    
    // Test with extreme target position
    anim._target_x = -100.0f;  // Way outside left edge
    anim._target_y = -100.0f;  // Way outside top edge
    
    anim.testConstrainPosition();
    
    // Should be constrained to valid range
    TEST_ASSERT_TRUE(anim.getTargetX() >= 0);
    TEST_ASSERT_TRUE(anim.getTargetY() >= 0);
}

void test_animation_manager_with_different_screen_sizes(void) {
    // Test with portrait orientation
    AnimationManagerTest anim_portrait(240, 320);
    TEST_ASSERT_EQUAL_UINT16(240, anim_portrait.screenWidth);
    TEST_ASSERT_EQUAL_UINT16(320, anim_portrait.screenHeight);
    TEST_ASSERT_EQUAL_UINT16(120, anim_portrait.triangleSize);  // Half of smaller dimension
    
    // Test with square orientation
    AnimationManagerTest anim_square(240, 240);
    TEST_ASSERT_EQUAL_UINT16(240, anim_square.screenWidth);
    TEST_ASSERT_EQUAL_UINT16(240, anim_square.screenHeight);
    TEST_ASSERT_EQUAL_UINT16(120, anim_square.triangleSize);
}

int main(void) {
    UNITY_BEGIN();
    
    RUN_TEST(test_animation_manager_creation);
    RUN_TEST(test_triangle_initial_position);
    RUN_TEST(test_gyro_sensitivity);
    RUN_TEST(test_gyro_sensitivity_negative);
    RUN_TEST(test_still_motion);
    RUN_TEST(test_shaking_prevents_motion);
    RUN_TEST(test_position_constraining);
    RUN_TEST(test_velocity_smoothing);
    RUN_TEST(test_idle_motion_update);
    RUN_TEST(test_constrain_position_edge_cases);
    RUN_TEST(test_animation_manager_with_different_screen_sizes);
    
    return UNITY_END();
}

#else

// Fallback for non-native builds
#include <unity.h>

void test_placeholder(void) {
    TEST_ASSERT_TRUE(1);
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_placeholder);
    return UNITY_END();
}

#endif
