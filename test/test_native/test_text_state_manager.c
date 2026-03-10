// Test file for TextStateManager
#include <unity.h>
#include "../src/TextStateManager.h"

#ifdef NATIVE_BUILD
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Mock millis()
static unsigned long mock_millis = 0;
unsigned long millis() { return mock_millis; }

// Mock Serial
void Serial_print(const char* s) { printf("%s", s); }
void Serial_println(const char* s) { printf("%s\n", s); }
void Serial_begin(unsigned long baud) { (void)baud; }
void Serial_flush() {}
void Serial_write(int c) { putchar(c); }
int Serial_available() { return 0; }
int Serial_read() { return -1; }

// Mock random functions (rename to avoid conflict with stdlib.h)
int mock_random(int max) { return rand() % max; }
int mock_random_range(int min, int max) { return min + rand() % (max - min); }

// Mock max()
int max(int a, int b) { return a > b ? a : b; }

// Mock min()
int min(int a, int b) { return a < b ? a : b; }

// Mock delay()
void delay(unsigned long ms) { (void)ms; }

#endif

static TextStateManager* manager;

void setUp(void) {
#ifdef NATIVE_BUILD
    mock_millis = 0;
#endif
    manager = textStateManager_create();
}

void tearDown(void) {
    if (manager) {
        textStateManager_destroy(manager);
        manager = NULL;
    }
}

void test_create_and_destroy(void) {
    TEST_ASSERT_NOT_NULL(manager);
}

void test_set_text_initial(void) {
    textStateManager_setText(manager, "Hello World");
    TEST_ASSERT_EQUAL_STRING("Hello World", textStateManager_getText(manager));
}

void test_set_text_unicode(void) {
    textStateManager_setText(manager, "Hello 世界");
    TEST_ASSERT_EQUAL_STRING("Hello 世界", textStateManager_getText(manager));
}

void test_set_text_special_chars(void) {
    textStateManager_setText(manager, "Test!@#$%^&*()");
    TEST_ASSERT_EQUAL_STRING("Test!@#$%^&*()", textStateManager_getText(manager));
}

void test_set_text_empty(void) {
    textStateManager_setText(manager, "");
    TEST_ASSERT_EQUAL_STRING("", textStateManager_getText(manager));
}

void test_set_text_max_length(void) {
    char long_text[257];
    memset(long_text, 'A', 256);
    long_text[256] = '\0';
    textStateManager_setText(manager, long_text);
    TEST_ASSERT_EQUAL_STRING(long_text, textStateManager_getText(manager));
}

void test_set_text_truncation(void) {
    char long_text[300];
    memset(long_text, 'B', 299);
    long_text[299] = '\0';
    textStateManager_setText(manager, long_text);
    char expected[257];
    memset(expected, 'B', 256);
    expected[256] = '\0';
    TEST_ASSERT_EQUAL_STRING(expected, textStateManager_getText(manager));
}

void test_set_text_short(void) {
    textStateManager_setText(manager, "Hi");
    TEST_ASSERT_EQUAL_STRING("Hi", textStateManager_getText(manager));
}

void test_set_text_spaces(void) {
    textStateManager_setText(manager, "   Multiple   Spaces   ");
    TEST_ASSERT_EQUAL_STRING("   Multiple   Spaces   ", textStateManager_getText(manager));
}

void test_set_text_newlines(void) {
    textStateManager_setText(manager, "Line1\nLine2\nLine3");
    TEST_ASSERT_EQUAL_STRING("Line1\nLine2\nLine3", textStateManager_getText(manager));
}

void test_set_text_tabs(void) {
    textStateManager_setText(manager, "Tab1\tTab2\tTab3");
    TEST_ASSERT_EQUAL_STRING("Tab1\tTab2\tTab3", textStateManager_getText(manager));
}

void test_set_text_mixed_special(void) {
    textStateManager_setText(manager, "Mixed: \n\t!@#$%^&*() 世界");
    TEST_ASSERT_EQUAL_STRING("Mixed: \n\t!@#$%^&*() 世界", textStateManager_getText(manager));
}

void test_get_text_null(void) {
    TEST_ASSERT_EQUAL_STRING("", textStateManager_getText(manager));
}

void test_set_text_after_clear(void) {
    textStateManager_setText(manager, "First");
    textStateManager_setText(manager, "");
    textStateManager_setText(manager, "Second");
    TEST_ASSERT_EQUAL_STRING("Second", textStateManager_getText(manager));
}

void test_set_text_russian(void) {
    textStateManager_setText(manager, "Привет мир");
    TEST_ASSERT_EQUAL_STRING("Привет мир", textStateManager_getText(manager));
}

void test_set_text_arabic(void) {
    textStateManager_setText(manager, "مرحبا بالعالم");
    TEST_ASSERT_EQUAL_STRING("مرحبا بالعالم", textStateManager_getText(manager));
}

void test_set_text_hebrew(void) {
    textStateManager_setText(manager, "שלום עולם");
    TEST_ASSERT_EQUAL_STRING("שלום עולם", textStateManager_getText(manager));
}

void test_set_text_emoji(void) {
    textStateManager_setText(manager, "Hello 😀 World 🌍");
    TEST_ASSERT_EQUAL_STRING("Hello 😀 World 🌍", textStateManager_getText(manager));
}

void test_set_text_mixed_scripts(void) {
    textStateManager_setText(manager, "Hello 世界 Привет مرحبا");
    TEST_ASSERT_EQUAL_STRING("Hello 世界 Привет مرحبا", textStateManager_getText(manager));
}

void test_set_text_very_long(void) {
    char very_long[1000];
    memset(very_long, 'X', 999);
    very_long[999] = '\0';
    textStateManager_setText(manager, very_long);
    char expected[257];
    memset(expected, 'X', 256);
    expected[256] = '\0';
    TEST_ASSERT_EQUAL_STRING(expected, textStateManager_getText(manager));
}

void test_set_text_single_char(void) {
    textStateManager_setText(manager, "X");
    TEST_ASSERT_EQUAL_STRING("X", textStateManager_getText(manager));
}

void test_set_text_two_chars(void) {
    textStateManager_setText(manager, "XY");
    TEST_ASSERT_EQUAL_STRING("XY", textStateManager_getText(manager));
}

void test_set_text_three_chars(void) {
    textStateManager_setText(manager, "XYZ");
    TEST_ASSERT_EQUAL_STRING("XYZ", textStateManager_getText(manager));
}

void test_set_text_boundary_256(void) {
    char boundary[257];
    memset(boundary, 'Z', 256);
    boundary[256] = '\0';
    textStateManager_setText(manager, boundary);
    TEST_ASSERT_EQUAL_STRING(boundary, textStateManager_getText(manager));
}

void test_set_text_boundary_257(void) {
    char boundary[258];
    memset(boundary, 'Z', 257);
    boundary[257] = '\0';
    textStateManager_setText(manager, boundary);
    char expected[257];
    memset(expected, 'Z', 256);
    expected[256] = '\0';
    TEST_ASSERT_EQUAL_STRING(expected, textStateManager_getText(manager));
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_create_and_destroy);
    RUN_TEST(test_set_text_initial);
    RUN_TEST(test_set_text_unicode);
    RUN_TEST(test_set_text_special_chars);
    RUN_TEST(test_set_text_empty);
    RUN_TEST(test_set_text_max_length);
    RUN_TEST(test_set_text_truncation);
    RUN_TEST(test_set_text_short);
    RUN_TEST(test_set_text_spaces);
    RUN_TEST(test_set_text_newlines);
    RUN_TEST(test_set_text_tabs);
    RUN_TEST(test_set_text_mixed_special);
    RUN_TEST(test_get_text_null);
    RUN_TEST(test_set_text_after_clear);
    RUN_TEST(test_set_text_russian);
    RUN_TEST(test_set_text_arabic);
    RUN_TEST(test_set_text_hebrew);
    RUN_TEST(test_set_text_emoji);
    RUN_TEST(test_set_text_mixed_scripts);
    RUN_TEST(test_set_text_very_long);
    RUN_TEST(test_set_text_single_char);
    RUN_TEST(test_set_text_two_chars);
    RUN_TEST(test_set_text_three_chars);
    RUN_TEST(test_set_text_boundary_256);
    RUN_TEST(test_set_text_boundary_257);
    return UNITY_END();
}
