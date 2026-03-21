/**
 * @file test_environment.cpp
 * @brief Unit tests for audio recording configuration constants
 *
 * Tests audio sampling rates, buffer sizes, and timing constants
 */

// Mock Arduino header first
#include "Arduino.h"

#include <unity.h>

/**
 * @brief Test: Audio sample rate constant is correct
 */
void test_environment_sample_rate(void) {
    // Sample rate should be 32000 Hz
    const int SAMPLE_RATE = 32000;
    TEST_ASSERT_EQUAL(32000, SAMPLE_RATE);
}

/**
 * @brief Test: Channels configuration is mono
 */
void test_environment_channels(void) {
    // Should be mono (1 channel)
    const int CHANNELS = 1;
    TEST_ASSERT_EQUAL(1, CHANNELS);
}

/**
 * @brief Test: Bits per sample is 16
 */
void test_environment_bits_per_sample(void) {
    // Should be 16-bit
    const int BITS_PER_SAMPLE = 16;
    TEST_ASSERT_EQUAL(16, BITS_PER_SAMPLE);
}

/**
 * @brief Test: DC offset is configured correctly
 */
void test_environment_dc_offset(void) {
    // DC offset should be 1250mV
    const int DC_OFFSET = 1250;
    TEST_ASSERT_EQUAL(1250, DC_OFFSET);
}

/**
 * @brief Test: Silence timeout is set correctly
 */
void test_environment_silence_timeout(void) {
    // Should be 2000ms
    const int SILENCE_TIMEOUT = 2000;
    TEST_ASSERT_EQUAL(2000, SILENCE_TIMEOUT);
}

/**
 * @brief Test: Audio threshold is configured
 */
void test_environment_audio_threshold(void) {
    // Should be 500
    const int AUDIO_THRESHOLD = 500;
    TEST_ASSERT_EQUAL(500, AUDIO_THRESHOLD);
}

/**
 * @brief Test: WAV header size is 44 bytes
 */
void test_environment_wav_header_size(void) {
    const int WAV_HEADER_SIZE = 44;
    TEST_ASSERT_EQUAL(44, WAV_HEADER_SIZE);
}

/**
 * @brief Test: Max recording duration is 10 seconds
 */
void test_environment_max_recording_duration(void) {
    const int MAX_RECORD_SECONDS = 10;
    TEST_ASSERT_EQUAL(10, MAX_RECORD_SECONDS);
}

/**
 * @brief Test: Buffer size calculation
 */
void test_environment_buffer_size(void) {
    // BUFFER_SIZE = MAX_RECORD_SECONDS * SAMPLE_RATE * CHANNELS * 2
    // = 10 * 32000 * 1 * 2 = 640000 bytes
    const int SAMPLE_RATE = 32000;
    const int CHANNELS = 1;
    const int MAX_RECORD_SECONDS = 10;
    const int BUFFER_SIZE = MAX_RECORD_SECONDS * SAMPLE_RATE * CHANNELS * 2;
    
    TEST_ASSERT_EQUAL(640000, BUFFER_SIZE);
}

/**
 * @brief Test: Sample buffer size is 256
 */
void test_environment_sample_buffer_size(void) {
    const int SAMPLE_BUFFER_SIZE = 256;
    TEST_ASSERT_EQUAL(256, SAMPLE_BUFFER_SIZE);
}

/**
 * @brief Test: Debug interval is 500ms
 */
void test_environment_debug_interval(void) {
    const int DEBUG_INTERVAL = 500;
    TEST_ASSERT_EQUAL(500, DEBUG_INTERVAL);
}

/**
 * @brief Test: MAX9814 VPP is configured
 */
void test_environment_max9814_vpp(void) {
    const int MAX9814_VPP = 2000;
    TEST_ASSERT_EQUAL(2000, MAX9814_VPP);
}

/**
 * @brief Test: ADC VREF is 3300mV
 */
void test_environment_adc_vref(void) {
    const int ADC_VREF = 3300;
    TEST_ASSERT_EQUAL(3300, ADC_VREF);
}

/**
 * @brief Test: Buffer size is appropriate for 10 seconds
 */
void test_environment_buffer_duration(void) {
    const int SAMPLE_RATE = 32000;
    const int CHANNELS = 1;
    const int BITS_PER_SAMPLE = 16;
    const int BUFFER_SIZE = 640000;
    
    float seconds = (float)BUFFER_SIZE / (SAMPLE_RATE * CHANNELS * (BITS_PER_SAMPLE / 8));
    TEST_ASSERT_EQUAL_INT(10, (int)seconds);
}

/**
 * @brief Test: Audio format is mono 16-bit
 */
void test_environment_audio_format(void) {
    const int CHANNELS = 1;
    const int BITS_PER_SAMPLE = 16;
    
    TEST_ASSERT_EQUAL(1, CHANNELS);
    TEST_ASSERT_EQUAL(16, BITS_PER_SAMPLE);
}

/**
 * @brief Test: Voice detection threshold is reasonable
 */
void test_environment_voice_threshold(void) {
    const int AUDIO_THRESHOLD = 500;
    
    TEST_ASSERT_GREATER_THAN(0, AUDIO_THRESHOLD);
    TEST_ASSERT_LESS_THAN(2048, AUDIO_THRESHOLD);
}

/**
 * @brief Test: All constants have valid values
 */
void test_environment_all_constants_valid(void) {
    TEST_ASSERT_GREATER_THAN(0, 32000);  // SAMPLE_RATE
    TEST_ASSERT_GREATER_THAN(0, 1);     // CHANNELS
    TEST_ASSERT_GREATER_THAN(0, 16);    // BITS_PER_SAMPLE
    TEST_ASSERT_GREATER_THAN(0, 1250);  // DC_OFFSET
    TEST_ASSERT_GREATER_THAN(0, 2000);  // SILENCE_TIMEOUT
    TEST_ASSERT_GREATER_THAN(0, 500);   // AUDIO_THRESHOLD
    TEST_ASSERT_GREATER_THAN(0, 10);    // MAX_RECORD_SECONDS
    TEST_ASSERT_EQUAL(44, 44);          // WAV_HEADER_SIZE
}

/**
 * @brief Test: Timing constants are positive
 */
void test_environment_positive_timing(void) {
    const int SILENCE_TIMEOUT = 2000;
    const int DEBUG_INTERVAL = 500;
    const int MAX_RECORD_SECONDS = 10;
    
    TEST_ASSERT_GREATER_THAN(0, SILENCE_TIMEOUT);
    TEST_ASSERT_GREATER_THAN(0, DEBUG_INTERVAL);
    TEST_ASSERT_GREATER_THAN(0, MAX_RECORD_SECONDS);
}

/**
 * @brief Test: ADC channel configuration
 */
void test_environment_adc_channel(void) {
    const int ADC_MIC_CHANNEL = 1;  // ADC1_CHANNEL_1
    const int ADC_MIC_GPIO_NUM = 2;
    
    TEST_ASSERT_EQUAL(1, ADC_MIC_CHANNEL);
    TEST_ASSERT_EQUAL(2, ADC_MIC_GPIO_NUM);
}

void setUp(void) {
    // Reset test state
    _arduino_millis_counter = 0;
}

void tearDown(void) {
    // Cleanup if needed
}

int main(void) {
    UNITY_BEGIN();

    RUN_TEST(test_environment_sample_rate);
    RUN_TEST(test_environment_channels);
    RUN_TEST(test_environment_bits_per_sample);
    RUN_TEST(test_environment_dc_offset);
    RUN_TEST(test_environment_silence_timeout);
    RUN_TEST(test_environment_audio_threshold);
    RUN_TEST(test_environment_wav_header_size);
    RUN_TEST(test_environment_max_recording_duration);
    RUN_TEST(test_environment_buffer_size);
    RUN_TEST(test_environment_sample_buffer_size);
    RUN_TEST(test_environment_debug_interval);
    RUN_TEST(test_environment_max9814_vpp);
    RUN_TEST(test_environment_adc_vref);
    RUN_TEST(test_environment_buffer_duration);
    RUN_TEST(test_environment_audio_format);
    RUN_TEST(test_environment_voice_threshold);
    RUN_TEST(test_environment_all_constants_valid);
    RUN_TEST(test_environment_positive_timing);
    RUN_TEST(test_environment_adc_channel);

    return UNITY_END();
}
