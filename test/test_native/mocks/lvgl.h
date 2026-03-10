#ifndef lvgl_h
#define lvgl_h

#include <stdint.h>
#include <stddef.h>

typedef uint32_t lv_coord_t;
typedef uint32_t lv_color_t;
typedef uint32_t lv_opa_t;
typedef uint8_t lv_state_t;
typedef uint32_t lv_style_prop_t;
typedef uint32_t lv_style_selector_t;

typedef struct { lv_coord_t x; lv_coord_t y; } lv_point_t;
typedef struct { lv_coord_t x1; lv_coord_t y1; lv_coord_t x2; lv_coord_t y2; } lv_area_t;
typedef struct { void (*callback)(void *); void *var; int32_t speed; int32_t path; int32_t act_time; int32_t time_total; uint8_t ease_cb; uint8_t play_back; uint8_t play_reverse; uint8_t reverse_cb; uint8_t finished_cb; } lv_anim_t;

typedef struct { void *ptr; uint32_t size; uint8_t *data; } lv_fs_file_t;
typedef struct { void *ptr; uint32_t size; uint8_t *data; } lv_fs_dir_t;

#define LV_COLOR_DEPTH 32
#define LV_DPI_DEF 130
#define LV_HOR_RES_MAX 480
#define LV_VER_RES_MAX 320
#define LV_STYLE_TRANSITION_DUR_DEF 0
#define LV_STYLE_TRANSITION_DUR_NORMAL 150
#define LV_STYLE_TRANSITION_DUR_ENTER 150
#define LV_STYLE_TRANSITION_DUR_EXIT 100
#define LV_STYLE_PROP_COUNT 64
#define LV_DIR_NONE 0
#define LV_DIR_IN 1
#define LV_DIR_OUT 2
#define LV_EVENT_PRESSED 0
#define LV_EVENT_PRESSED_IN 1
#define LV_EVENT_PRESSED_OUT 2
#define LV_EVENT_CLICKED 3
#define LV_EVENT_SHORT_CLICKED 4
#define LV_EVENT_LONG_PRESSED 5
#define LV_EVENT_LONG_PRESSED_REPEAT 6
#define LV_EVENT_DRAW_MAIN 7
#define LV_EVENT_DRAW_POST 8
#define LV_EVENT_DRAW_PART_BEGIN 9
#define LV_EVENT_DRAW_PART_END 10
#define LV_EVENT_RELEASED 11
#define LV_EVENT_SCROLL_BEGIN 12
#define LV_EVENT_SCROLL_END 13
#define LV_EVENT_SCROLL 14
#define LV_EVENT_VALUE_CHANGED 15
#define LV_EVENT_INSERT 16
#define LV_EVENT_DELETE 17
#define LV_EVENT_CHILD_CHANGED 18
#define LV_EVENT_CHILD_CREATED 19
#define LV_EVENT_CHILD_DELETED 20
#define LV_EVENT_SIZE_CHANGED 21
#define LV_EVENT_STYLE_CHANGED 22
#define LV_EVENT_LAYOUT_CHANGED 23
#define LV_EVENT_GET_SELF_SIZE 24
#define LV_EVENT_HIT_TEST 26
#define LV_EVENT_COVER_CHECK 27
#define LV_EVENT_REFR_EXT_DRAW_SIZE 28
#define LV_EVENT_MSG_RECEIVED 29
#define LV_EVENT_SEND_MSG 30
#define LV_EVENT_DESIGN 31
#define LV_EVENT_DRAW_SETUP 32
#define LV_EVENT_DRAW_REF 33
#define LV_EVENT_INVALIDATE_AREA 34
#define LV_EVENT_VALIDATION 35
#define LV_EVENT_ALL 36
#define LV_OBJ_CLASS_EXT_SIZE 40
#define LV_BTN_CLASS_EXT_SIZE 40
#define LV_LABEL_CLASS_EXT_SIZE 40
#define LV_IMG_CLASS_EXT_SIZE 40
#define LV_ARC_CLASS_EXT_SIZE 40
#define LV_SLIDER_CLASS_EXT_SIZE 40
#define LV_BAR_CLASS_EXT_SIZE 40
#define LV_CHECKBOX_CLASS_EXT_SIZE 40
#define LV_SWITCH_CLASS_EXT_SIZE 40
#define LV_ROLLER_CLASS_EXT_SIZE 40
#define LV_MSGBOX_CLASS_EXT_SIZE 40
#define LV_KEYBOARD_CLASS_EXT_SIZE 40
#define LV_DROPDOWN_CLASS_EXT_SIZE 40
#define LV_LIST_CLASS_EXT_SIZE 40
#define LV_CALENDAR_CLASS_EXT_SIZE 40
#define LV_TABVIEW_CLASS_EXT_SIZE 40
#define LV_TILEVIEW_CLASS_EXT_SIZE 40
#define LV_MAP_CLASS_EXT_SIZE 40
#define LV_CANVAS_CLASS_EXT_SIZE 40
#define LV_IMGBTN_CLASS_EXT_SIZE 40
#define LV_LABEL_CLASS_EXT_SIZE 40
#define LV_LINE_CLASS_EXT_SIZE 40
#define LV_LVGL_H_INCLUDE_SIMPLE
#define LV_USE_LOG 1
#define LV_LOG_LEVEL LV_LOG_LEVEL_WARN
#define LV_LOG_PRINTF 0
#define LV_USE_THEME_DEFAULT 1
#define LV_USE_THEME_MONO 1
#define LV_USE_THEME_ALIEN 1
#define LV_USE_THEME_NIGHT 1
#define LV_USE_THEME_LIGHT 1
#define LV_USE_THEME_ROBOTO 1
#define LV_USE_THEME_MATERIAL 1
#define LV_USE_THEME_TEMPL 1
#define LV_USE_THEME_DEFAULT_COLOR_PRIMARY lv_color_hex(0x01a2b1)
#define LV_USE_THEME_DEFAULT_COLOR_SECONDARY lv_color_hex(0x01a2b1)
#define LV_USE_THEME_DEFAULT_BG_COLOR lv_color_hex(0xffffff)
#define LV_USE_THEME_DEFAULT_FG_COLOR lv_color_hex(0x000000)
#define LV_USE_THEME_DEFAULT_MAIN_COLOR lv_color_hex(0x01a2b1)
#define LV_USE_THEME_DEFAULT_BORDER_WIDTH 2
#define LV_USE_THEME_DEFAULT_OUTLINE_WIDTH 2
#define LV_USE_THEME_DEFAULT_SHADOW_WIDTH 2
#define LV_USE_THEME_DEFAULT_RADIUS 4
#define LV_USE_THEME_DEFAULT_MARGIN 2
#define LV_USE_THEME_DEFAULT_SPACING 8
#define LV_USE_THEME_DEFAULT_PAD_X 12
#define LV_USE_THEME_DEFAULT_PAD_Y 12
#define LV_USE_THEME_DEFAULT_PAD_SCRL 4
#define LV_USE_THEME_DEFAULT_TEXT_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_ICON_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_IMG_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_BTN_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_LABEL_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_ARC_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_SLIDER_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_BAR_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_CHECKBOX_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_SWITCH_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_ROLLER_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_MSGBOX_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_KEYBOARD_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_DROPDOWN_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_LIST_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_CALENDAR_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_TABVIEW_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_TILEVIEW_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_MAP_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_CANVAS_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_IMGBTN_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_LINE_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_LABEL_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_ARC_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_SLIDER_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_BAR_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_CHECKBOX_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_SWITCH_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_ROLLER_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_MSGBOX_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_KEYBOARD_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_DROPDOWN_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_LIST_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_CALENDAR_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_TABVIEW_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_TILEVIEW_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_MAP_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_CANVAS_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_IMGBTN_FONT lv_font_default
#define LV_USE_THEME_DEFAULT_LINE_FONT lv_font_default

#endif // lvgl_h
