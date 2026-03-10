#ifndef LVGL_TEST_HELPER_H
#define LVGL_TEST_HELPER_H

/*
 * LVGL Headless Test Helper — memory framebuffer + PPM export
 *
 * Provides a complete headless display driver for LVGL that renders
 * to an in-memory framebuffer. Exports PPM screenshots (zero deps).
 * Works with LVGL 7.x and 8.x.
 *
 * CRITICAL: Call lvgl_test_init() ONCE at the start. For each test,
 * use lvgl_test_new_screen() to get a fresh screen (uses immediate
 * lv_disp_load_scr, NOT animated lv_scr_load which needs extra ticks).
 *
 * Usage in test file:
 *   #include "lvgl_test_helper.h"
 *   void setUp(void) {}
 *   void tearDown(void) {}
 *   void test_my_widget(void) {
 *       lvgl_test_init();  // safe to call multiple times (no-op after first)
 *       lv_obj_t *scr = lvgl_test_new_screen();
 *       lv_obj_t *label = lv_label_create(scr, NULL);
 *       lv_label_set_text(label, "Hello");
 *       LVGL_STYLE_TEXT(label, LVGL_COLOR_DARK);
 *       lvgl_test_render();
 *       TEST_ASSERT_NOT_NULL(label);
 *       lvgl_test_save_ppm("screenshots/my_test.ppm");
 *   }
 */

#include "../../lib/lvgl/lvgl.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#ifndef DISP_HOR_RES
#ifdef LV_HOR_RES_MAX
#define DISP_HOR_RES LV_HOR_RES_MAX
#else
#define DISP_HOR_RES 240
#endif
#endif

#ifndef DISP_VER_RES
#ifdef LV_VER_RES_MAX
#define DISP_VER_RES LV_VER_RES_MAX
#else
#define DISP_VER_RES 240
#endif
#endif

/* ---- Color palette for visible widget styling ---- */
#define LVGL_COLOR_TEAL  LV_COLOR_MAKE(0x00, 0x96, 0x88)
#define LVGL_COLOR_DARK  LV_COLOR_MAKE(0x26, 0x32, 0x38)
#define LVGL_COLOR_BG    LV_COLOR_MAKE(0xEC, 0xEF, 0xF1)
#define LVGL_COLOR_GRAY  LV_COLOR_MAKE(0xB0, 0xBE, 0xC5)
#define LVGL_COLOR_WHITE LV_COLOR_MAKE(0xFF, 0xFF, 0xFF)

/* Convenience macros for common styling */
#define LVGL_STYLE_TEXT(obj, color) \
    lv_obj_set_style_local_text_color(obj, LV_LABEL_PART_MAIN, LV_STATE_DEFAULT, color)

#define LVGL_STYLE_BAR(bar) do { \
    lv_obj_set_style_local_bg_color(bar, LV_BAR_PART_BG, LV_STATE_DEFAULT, LVGL_COLOR_GRAY); \
    lv_obj_set_style_local_bg_opa(bar, LV_BAR_PART_BG, LV_STATE_DEFAULT, LV_OPA_COVER); \
    lv_obj_set_style_local_radius(bar, LV_BAR_PART_BG, LV_STATE_DEFAULT, 12); \
    lv_obj_set_style_local_bg_color(bar, LV_BAR_PART_INDIC, LV_STATE_DEFAULT, LVGL_COLOR_TEAL); \
    lv_obj_set_style_local_bg_opa(bar, LV_BAR_PART_INDIC, LV_STATE_DEFAULT, LV_OPA_COVER); \
    lv_obj_set_style_local_radius(bar, LV_BAR_PART_INDIC, LV_STATE_DEFAULT, 12); \
} while(0)

#define LVGL_STYLE_ARC(arc) do { \
    lv_obj_set_style_local_line_color(arc, LV_ARC_PART_INDIC, LV_STATE_DEFAULT, LVGL_COLOR_TEAL); \
    lv_obj_set_style_local_line_width(arc, LV_ARC_PART_INDIC, LV_STATE_DEFAULT, 10); \
    lv_obj_set_style_local_line_color(arc, LV_ARC_PART_BG, LV_STATE_DEFAULT, LVGL_COLOR_GRAY); \
    lv_obj_set_style_local_line_width(arc, LV_ARC_PART_BG, LV_STATE_DEFAULT, 10); \
} while(0)

#define LVGL_STYLE_BTN(btn) do { \
    lv_obj_set_style_local_bg_color(btn, LV_BTN_PART_MAIN, LV_STATE_DEFAULT, LVGL_COLOR_TEAL); \
    lv_obj_set_style_local_bg_opa(btn, LV_BTN_PART_MAIN, LV_STATE_DEFAULT, LV_OPA_COVER); \
    lv_obj_set_style_local_radius(btn, LV_BTN_PART_MAIN, LV_STATE_DEFAULT, 12); \
    lv_obj_set_style_local_border_width(btn, LV_BTN_PART_MAIN, LV_STATE_DEFAULT, 0); \
} while(0)

/* Global framebuffer — accessible from tests for pixel assertions */
static lv_color_t _test_fb[DISP_HOR_RES * DISP_VER_RES];
static lv_color_t _test_draw_buf[DISP_HOR_RES * 10];
static lv_disp_t *_test_display = NULL;
static uint32_t _test_tick = 0;
static int _test_initialized = 0;

/* LVGL 7.x uses lv_disp_buf_t + drv.buffer; 8.x uses lv_disp_draw_buf_t + drv.draw_buf */
#if LVGL_VERSION_MAJOR >= 8
static lv_disp_draw_buf_t _test_disp_buf;
#else
static lv_disp_buf_t _test_disp_buf;
#endif

static void _test_flush_cb(lv_disp_drv_t *drv, const lv_area_t *area, lv_color_t *color_p) {
    for (int y = area->y1; y <= area->y2; y++) {
        for (int x = area->x1; x <= area->x2; x++) {
            _test_fb[y * DISP_HOR_RES + x] = *color_p;
            color_p++;
        }
    }
    lv_disp_flush_ready(drv);
}

/* Initialize LVGL once. Safe to call multiple times (no-op after first).
 * CRITICAL: lv_init() must only be called ONCE per process. Calling it
 * again corrupts internal state and causes blank renders. */
static lv_disp_t* lvgl_test_init(void) {
    if (_test_initialized) return _test_display;

    lv_init();

#if LVGL_VERSION_MAJOR >= 8
    lv_disp_draw_buf_init(&_test_disp_buf, _test_draw_buf, NULL, DISP_HOR_RES * 10);
    static lv_disp_drv_t disp_drv;
    lv_disp_drv_init(&disp_drv);
    disp_drv.draw_buf = &_test_disp_buf;
    disp_drv.flush_cb = _test_flush_cb;
    disp_drv.hor_res = DISP_HOR_RES;
    disp_drv.ver_res = DISP_VER_RES;
    _test_display = lv_disp_drv_register(&disp_drv);
#else
    lv_disp_buf_init(&_test_disp_buf, _test_draw_buf, NULL, DISP_HOR_RES * 10);
    static lv_disp_drv_t disp_drv;
    lv_disp_drv_init(&disp_drv);
    disp_drv.buffer = &_test_disp_buf;
    disp_drv.flush_cb = _test_flush_cb;
    disp_drv.hor_res = DISP_HOR_RES;
    disp_drv.ver_res = DISP_VER_RES;
    _test_display = lv_disp_drv_register(&disp_drv);
#endif

    _test_initialized = 1;
    return _test_display;
}

/* Create a fresh screen with background color and load it immediately.
 * Uses lv_disp_load_scr() (immediate) NOT lv_scr_load() (animated).
 * lv_scr_load() has a 300ms animation that needs many extra ticks. */
static lv_obj_t* lvgl_test_new_screen(void) {
    lv_obj_t *scr = lv_obj_create(NULL, NULL);
    lv_obj_set_style_local_bg_color(scr, LV_OBJ_PART_MAIN, LV_STATE_DEFAULT, LVGL_COLOR_BG);
    lv_obj_set_style_local_bg_opa(scr, LV_OBJ_PART_MAIN, LV_STATE_DEFAULT, LV_OPA_COVER);
    lv_disp_load_scr(scr);  /* immediate — no animation delay */
    return scr;
}

/* Render LVGL to framebuffer with full flush.
 * First pass: 30 ticks for normal rendering.
 * Then invalidate entire screen + 10 more ticks to catch any missed regions. */
static void lvgl_test_render(void) {
    for (int i = 0; i < 30; i++) {
        _test_tick += 30;
        lv_tick_inc(30);
#if LVGL_VERSION_MAJOR >= 8
        lv_timer_handler();
#else
        lv_task_handler();
#endif
    }
    /* Force full refresh */
    lv_obj_invalidate(lv_scr_act());
    for (int i = 0; i < 10; i++) {
        _test_tick += 10;
        lv_tick_inc(10);
#if LVGL_VERSION_MAJOR >= 8
        lv_timer_handler();
#else
        lv_task_handler();
#endif
    }
}

/* Legacy alias for backward compatibility */
static void lvgl_test_pump(int frames) {
    for (int i = 0; i < frames; i++) {
        _test_tick += 5;
        lv_tick_inc(5);
#if LVGL_VERSION_MAJOR >= 8
        lv_timer_handler();
#else
        lv_task_handler();
#endif
    }
}

/* Get pixel color at (x, y) from the framebuffer */
static lv_color_t lvgl_test_get_pixel(int x, int y) {
    if (x < 0 || x >= DISP_HOR_RES || y < 0 || y >= DISP_VER_RES) {
        lv_color_t black;
        black.full = 0;
        return black;
    }
    return _test_fb[y * DISP_HOR_RES + x];
}

/* Check if any non-background pixels exist in the framebuffer */
static int lvgl_test_has_content(void) {
    lv_color_t bg = LVGL_COLOR_BG;
    for (int i = 0; i < DISP_HOR_RES * DISP_VER_RES; i++) {
        if (_test_fb[i].full != bg.full && _test_fb[i].full != 0) return 1;
    }
    return 0;
}

/* Save framebuffer as PPM (zero dependencies — no libpng needed) */
static int lvgl_test_save_ppm(const char *path) {
    FILE *fp = fopen(path, "wb");
    if (!fp) return -1;
    fprintf(fp, "P6
%d %d
255
", DISP_HOR_RES, DISP_VER_RES);
    for (int i = 0; i < DISP_HOR_RES * DISP_VER_RES; i++) {
        lv_color_t c = _test_fb[i];
        uint8_t rgb[3];
#if LV_COLOR_DEPTH == 16
        rgb[0] = (LV_COLOR_GET_R(c) * 255) / 31;
        rgb[1] = (LV_COLOR_GET_G(c) * 255) / 63;
        rgb[2] = (LV_COLOR_GET_B(c) * 255) / 31;
#else
        rgb[0] = LV_COLOR_GET_R(c);
        rgb[1] = LV_COLOR_GET_G(c);
        rgb[2] = LV_COLOR_GET_B(c);
#endif
        fwrite(rgb, 1, 3, fp);
    }
    fclose(fp);
    return 0;
}

/* Save screenshot with auto-numbered filename to a directory */
static int _test_screenshot_count = 0;
static void lvgl_test_screenshot(const char *dir, const char *name) {
    char path[256], cmd[300];
    snprintf(cmd, sizeof(cmd), "mkdir -p %s", dir);
    system(cmd);
    snprintf(path, sizeof(path), "%s/%02d_%s.ppm", dir, _test_screenshot_count++, name);
    lvgl_test_save_ppm(path);
    printf("  Screenshot: %s
", path);
}

#endif /* LVGL_TEST_HELPER_H */
