#ifndef UNITY_H
#define UNITY_H

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

// Minimal Unity testing framework for native builds
#define UNITY_OUTPUT_CHAR(a) putchar(a)
#define UNITY_OUTPUT_FLUSH() fflush(stdout)
#define UNITY_OUTPUT_START() printf("\n")
#define UNITY_OUTPUT_END() printf("\n")

#define UNITY_TEST_ASSERT(condition, line, message) do { \
    if (!(condition)) { \
        printf("FAIL: %s at line %d: %s\n", message, line, #condition); \
        exit(1); \
    } \
} while(0)

#define UNITY_TEST_ASSERT_NULL(ptr, line, message) UNITY_TEST_ASSERT(((ptr) == NULL), line, message)
#define UNITY_TEST_ASSERT_NOT_NULL(ptr, line, message) UNITY_TEST_ASSERT(((ptr) != NULL), line, message)
#define UNITY_TEST_ASSERT_EQUAL_INT(expected, actual, line, message) UNITY_TEST_ASSERT((expected) == (actual), line, message)
#define UNITY_TEST_ASSERT_EQUAL_UINT(expected, actual, line, message) UNITY_TEST_ASSERT((expected) == (unsigned int)(actual), line, message)
#define UNITY_TEST_ASSERT_EQUAL_FLOAT(expected, actual, line, message) UNITY_TEST_ASSERT(((expected) == (actual)), line, message)
#define UNITY_TEST_ASSERT_EQUAL_DOUBLE(expected, actual, line, message) UNITY_TEST_ASSERT(((expected) == (actual)), line, message)
#define UNITY_TEST_ASSERT_EQUAL_CHAR(expected, actual, line, message) UNITY_TEST_ASSERT((expected) == (char)(actual), line, message)

#define TEST_ASSERT_TRUE(condition) UNITY_TEST_ASSERT((condition), __LINE__, "Test failed")
#define TEST_ASSERT_FALSE(condition) UNITY_TEST_ASSERT(!(condition), __LINE__, "Test failed")
#define TEST_ASSERT_NULL(ptr) UNITY_TEST_ASSERT_NULL(ptr, __LINE__, "Pointer should be null")
#define TEST_ASSERT_NOT_NULL(ptr) UNITY_TEST_ASSERT_NOT_NULL(ptr, __LINE__, "Pointer should not be null")
#define TEST_ASSERT_EQUAL_INT(expected, actual) UNITY_TEST_ASSERT_EQUAL_INT(expected, actual, __LINE__, "Values should be equal")
#define TEST_ASSERT_EQUAL_UINT(expected, actual) UNITY_TEST_ASSERT_EQUAL_UINT(expected, actual, __LINE__, "Values should be equal")
#define TEST_ASSERT_EQUAL_FLOAT(expected, actual) UNITY_TEST_ASSERT_EQUAL_FLOAT(expected, actual, __LINE__, "Values should be equal")
#define TEST_ASSERT_EQUAL_DOUBLE(expected, actual) UNITY_TEST_ASSERT_EQUAL_DOUBLE(expected, actual, __LINE__, "Values should be equal")
#define TEST_ASSERT_EQUAL_CHAR(expected, actual) UNITY_TEST_ASSERT_EQUAL_CHAR(expected, actual, __LINE__, "Values should be equal")

#define TEST_ASSERT_TRUE_MESSAGE(condition, message) UNITY_TEST_ASSERT((condition), __LINE__, message)
#define TEST_ASSERT_FALSE_MESSAGE(condition, message) UNITY_TEST_ASSERT(!(condition), __LINE__, message)
#define TEST_ASSERT_NULL_MESSAGE(ptr, message) UNITY_TEST_ASSERT_NULL(ptr, __LINE__, message)
#define TEST_ASSERT_NOT_NULL_MESSAGE(ptr, message) UNITY_TEST_ASSERT_NOT_NULL(ptr, __LINE__, message)
#define TEST_ASSERT_EQUAL_INT_MESSAGE(expected, actual, message) UNITY_TEST_ASSERT_EQUAL_INT(expected, actual, __LINE__, message)
#define TEST_ASSERT_EQUAL_UINT_MESSAGE(expected, actual, message) UNITY_TEST_ASSERT_EQUAL_UINT(expected, actual, __LINE__, message)
#define TEST_ASSERT_EQUAL_FLOAT_MESSAGE(expected, actual, message) UNITY_TEST_ASSERT_EQUAL_FLOAT(expected, actual, __LINE__, message)
#define TEST_ASSERT_EQUAL_DOUBLE_MESSAGE(expected, actual, message) UNITY_TEST_ASSERT_EQUAL_DOUBLE(expected, actual, __LINE__, message)
#define TEST_ASSERT_EQUAL_CHAR_MESSAGE(expected, actual, message) UNITY_TEST_ASSERT_EQUAL_CHAR(expected, actual, __LINE__, message)

#define TEST_ASSERT_EQUAL_HEX8(expected, actual) UNITY_TEST_ASSERT_EQUAL_CHAR((int8_t)(expected), (int8_t)(actual), __LINE__, "Hex8 values should be equal")
#define TEST_ASSERT_EQUAL_HEX16(expected, actual) UNITY_TEST_ASSERT_EQUAL_INT((int16_t)(expected), (int16_t)(actual), __LINE__, "Hex16 values should be equal")
#define TEST_ASSERT_EQUAL_HEX32(expected, actual) UNITY_TEST_ASSERT_EQUAL_INT((int32_t)(expected), (int32_t)(actual), __LINE__, "Hex32 values should be equal")

#define TEST_ASSERT_EQUAL_INT8(expected, actual) UNITY_TEST_ASSERT_EQUAL_CHAR((int8_t)(expected), (int8_t)(actual), __LINE__, "Int8 values should be equal")
#define TEST_ASSERT_EQUAL_INT16(expected, actual) UNITY_TEST_ASSERT_EQUAL_INT((int16_t)(expected), (int16_t)(actual), __LINE__, "Int16 values should be equal")
#define TEST_ASSERT_EQUAL_INT32(expected, actual) UNITY_TEST_ASSERT_EQUAL_INT((int32_t)(expected), (int32_t)(actual), __LINE__, "Int32 values should be equal")

#define TEST_ASSERT_EQUAL_UINT8(expected, actual) UNITY_TEST_ASSERT_EQUAL_CHAR((uint8_t)(expected), (uint8_t)(actual), __LINE__, "Uint8 values should be equal")
#define TEST_ASSERT_EQUAL_UINT16(expected, actual) UNITY_TEST_ASSERT_EQUAL_INT((uint16_t)(expected), (uint16_t)(actual), __LINE__, "Uint16 values should be equal")
#define TEST_ASSERT_EQUAL_UINT32(expected, actual) UNITY_TEST_ASSERT_EQUAL_INT((uint32_t)(expected), (uint32_t)(actual), __LINE__, "Uint32 values should be equal")

#define TEST_ASSERT_EQUAL_HEX(expected, actual) UNITY_TEST_ASSERT_EQUAL_INT((int)(expected), (int)(actual), __LINE__, "Hex values should be equal")

#define TEST_ASSERT_INT_WITHIN(delta, expected, actual) UNITY_TEST_ASSERT(((expected) - (actual)) <= (delta), __LINE__, "Values should be within delta")
#define TEST_ASSERT_INT8_WITHIN(delta, expected, actual) UNITY_TEST_ASSERT(((expected) - (actual)) <= (delta), __LINE__, "Int8 values should be within delta")
#define TEST_ASSERT_INT16_WITHIN(delta, expected, actual) UNITY_TEST_ASSERT(((expected) - (actual)) <= (delta), __LINE__, "Int16 values should be within delta")
#define TEST_ASSERT_INT32_WITHIN(delta, expected, actual) UNITY_TEST_ASSERT(((expected) - (actual)) <= (delta), __LINE__, "Int32 values should be within delta")

#define TEST_ASSERT_UINT_WITHIN(delta, expected, actual) UNITY_TEST_ASSERT(((expected) - (actual)) <= (delta), __LINE__, "Uint values should be within delta")
#define TEST_ASSERT_UINT8_WITHIN(delta, expected, actual) UNITY_TEST_ASSERT(((expected) - (actual)) <= (delta), __LINE__, "Uint8 values should be within delta")
#define TEST_ASSERT_UINT16_WITHIN(delta, expected, actual) UNITY_TEST_ASSERT(((expected) - (actual)) <= (delta), __LINE__, "Uint16 values should be within delta")
#define TEST_ASSERT_UINT32_WITHIN(delta, expected, actual) UNITY_TEST_ASSERT(((expected) - (actual)) <= (delta), __LINE__, "Uint32 values should be within delta")

#define TEST_ASSERT_FLOAT_WITHIN(delta, expected, actual) UNITY_TEST_ASSERT(((expected) - (actual)) <= (delta), __LINE__, "Float values should be within delta")
#define TEST_ASSERT_DOUBLE_WITHIN(delta, expected, actual) UNITY_TEST_ASSERT(((expected) - (actual)) <= (delta), __LINE__, "Double values should be within delta")

#define TEST_ASSERT_EQUAL_STRING(expected, actual) UNITY_TEST_ASSERT(strcmp((expected), (actual)) == 0, __LINE__, "Strings should be equal")
#define TEST_ASSERT_EQUAL_STRING_MESSAGE(expected, actual, message) UNITY_TEST_ASSERT(strcmp((expected), (actual)) == 0, __LINE__, message)

#define TEST_ASSERT_EQUAL_MEMORY(expected, actual, len) UNITY_TEST_ASSERT(memcmp((expected), (actual), (len)) == 0, __LINE__, "Memory should be equal")
#define TEST_ASSERT_EQUAL_MEMORY_MESSAGE(expected, actual, len, message) UNITY_TEST_ASSERT(memcmp((expected), (actual), (len)) == 0, __LINE__, message)

#define TEST_ASSERT_EQUAL_HEX8_MESSAGE(expected, actual, message) UNITY_TEST_ASSERT_EQUAL_CHAR((int8_t)(expected), (int8_t)(actual), __LINE__, message)
#define TEST_ASSERT_EQUAL_HEX16_MESSAGE(expected, actual, message) UNITY_TEST_ASSERT_EQUAL_INT((int16_t)(expected), (int16_t)(actual), __LINE__, message)
#define TEST_ASSERT_EQUAL_HEX32_MESSAGE(expected, actual, message) UNITY_TEST_ASSERT_EQUAL_INT((int32_t)(expected), (int32_t)(actual), __LINE__, message)

#define TEST_ASSERT_EQUAL_INT8_MESSAGE(expected, actual, message) UNITY_TEST_ASSERT_EQUAL_CHAR((int8_t)(expected), (int8_t)(actual), __LINE__, message)
#define TEST_ASSERT_EQUAL_INT16_MESSAGE(expected, actual, message) UNITY_TEST_ASSERT_EQUAL_INT((int16_t)(expected), (int16_t)(actual), __LINE__, message)
#define TEST_ASSERT_EQUAL_INT32_MESSAGE(expected, actual, message) UNITY_TEST_ASSERT_EQUAL_INT((int32_t)(expected), (int32_t)(actual), __LINE__, message)

#define TEST_ASSERT_EQUAL_UINT8_MESSAGE(expected, actual, message) UNITY_TEST_ASSERT_EQUAL_CHAR((uint8_t)(expected), (uint8_t)(actual), __LINE__, message)
#define TEST_ASSERT_EQUAL_UINT16_MESSAGE(expected, actual, message) UNITY_TEST_ASSERT_EQUAL_INT((uint16_t)(expected), (uint16_t)(actual), __LINE__, message)
#define TEST_ASSERT_EQUAL_UINT32_MESSAGE(expected, actual, message) UNITY_TEST_ASSERT_EQUAL_INT((uint32_t)(expected), (uint32_t)(actual), __LINE__, message)

#define TEST_ASSERT_EQUAL_HEX_MESSAGE(expected, actual, message) UNITY_TEST_ASSERT_EQUAL_INT((int)(expected), (int)(actual), __LINE__, message)

#define TEST_ASSERT_INT_WITHIN_MESSAGE(delta, expected, actual, message) UNITY_TEST_ASSERT(((expected) - (actual)) <= (delta), __LINE__, message)
#define TEST_ASSERT_INT8_WITHIN_MESSAGE(delta, expected, actual, message) UNITY_TEST_ASSERT(((expected) - (actual)) <= (delta), __LINE__, message)
#define TEST_ASSERT_INT16_WITHIN_MESSAGE(delta, expected, actual, message) UNITY_TEST_ASSERT(((expected) - (actual)) <= (delta), __LINE__, message)
#define TEST_ASSERT_INT32_WITHIN_MESSAGE(delta, expected, actual, message) UNITY_TEST_ASSERT(((expected) - (actual)) <= (delta), __LINE__, message)

#define TEST_ASSERT_UINT_WITHIN_MESSAGE(delta, expected, actual, message) UNITY_TEST_ASSERT(((expected) - (actual)) <= (delta), __LINE__, message)
#define TEST_ASSERT_UINT8_WITHIN_MESSAGE(delta, expected, actual, message) UNITY_TEST_ASSERT(((expected) - (actual)) <= (delta), __LINE__, message)
#define TEST_ASSERT_UINT16_WITHIN_MESSAGE(delta, expected, actual, message) UNITY_TEST_ASSERT(((expected) - (actual)) <= (delta), __LINE__, message)
#define TEST_ASSERT_UINT32_WITHIN_MESSAGE(delta, expected, actual, message) UNITY_TEST_ASSERT(((expected) - (actual)) <= (delta), __LINE__, message)

#define TEST_ASSERT_FLOAT_WITHIN_MESSAGE(delta, expected, actual, message) UNITY_TEST_ASSERT(((expected) - (actual)) <= (delta), __LINE__, message)
#define TEST_ASSERT_DOUBLE_WITHIN_MESSAGE(delta, expected, actual, message) UNITY_TEST_ASSERT(((expected) - (actual)) <= (delta), __LINE__, message)

#define TEST_ASSERT_EQUAL_STRING_MESSAGE(expected, actual, message) UNITY_TEST_ASSERT(strcmp((expected), (actual)) == 0, __LINE__, message)

#define TEST_ASSERT_EQUAL_MEMORY_MESSAGE(expected, actual, len, message) UNITY_TEST_ASSERT(memcmp((expected), (actual), (len)) == 0, __LINE__, message)

#define TEST_FAIL() do { printf("FAIL: Test failed at line %d\n", __LINE__); exit(1); } while(0)
#define TEST_FAIL_MESSAGE(message) do { printf("FAIL: %s at line %d\n", message, __LINE__); exit(1); } while(0)

#define TEST_CASE(name) void name(void)
#define TEST(name) TEST_CASE(name)

#define TEST_ASSERT(condition) UNITY_TEST_ASSERT((condition), __LINE__, "Test failed")
#define TEST_ASSERT_MESSAGE(condition, message) UNITY_TEST_ASSERT((condition), __LINE__, message)

#endif // UNITY_H
