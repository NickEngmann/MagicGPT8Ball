#include <stdio.h>
#include "lvgl.h"
#include "unity.h"

/* Forward declarations for Unity test functions */
void test_lvgl_init(void);
void test_lvgl_render(void);

int main(int argc, char **argv) {
    printf("Running native LVGL tests...\n");
    
    /* Run Unity tests */
    UNITY_BEGIN();
    RUN_TEST(test_lvgl_init);
    RUN_TEST(test_lvgl_render);
    return UNITY_END();
}
