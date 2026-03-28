/**
 * Unit tests for VoiceDetection
 * Tests the voice activity detection algorithm without hardware dependencies
 */

#include <unity.h>
#include "voice_detection.h"
#include <vector>
#include <cmath>

// Unity setup/teardown
void setUp(void) {}
void tearDown(void) {}

void createSilenceSamples(std::vector<uint16_t>& samples, size_t count) {
    samples.clear();
    samples.reserve(count);
    for (size_t i = 0; i < count; i++) {
        samples.push_back(2048); // Center value (no signal)
    }
}

void createLowAmplitudeSamples(std::vector<uint16_t>& samples, size_t count) {
    samples.clear();
    samples.reserve(count);
    for (size_t i = 0; i < count; i++) {
        samples.push_back(2048 + (i % 100 - 50)); // Small variations
    }
}

void createHighAmplitudeSamples(std::vector<uint16_t>& samples, size_t count) {
    samples.clear();
    samples.reserve(count);
    for (size_t i = 0; i < count; i++) {
        // Generate samples with high amplitude variations (centered at 2048)
        // To get max amplitude > 4000, we need values like 0 (amplitude=2048) or 4095 (amplitude=2047)
        // But we also need avg amplitude > 1000, so mix of high and low values
        if (i % 4 == 0) {
            samples.push_back(0);           // amplitude 2048
        } else if (i % 4 == 1) {
            samples.push_back(4095);        // amplitude 2047
        } else if (i % 4 == 2) {
            samples.push_back(500);         // amplitude 1548
        } else {
            samples.push_back(3500);        // amplitude 1452
        }
    }
}

void createSineWaveSamples(std::vector<uint16_t>& samples, size_t count,
                           float frequency, float amplitude) {
    samples.clear();
    samples.reserve(count);
    for (size_t i = 0; i < count; i++) {
        float sinValue = std::sin(2.0f * M_PI * frequency * i / 32000.0f);
        int16_t value = static_cast<int16_t>(amplitude * sinValue);
        uint16_t sample = 2048 + value;  // Clamp will happen automatically
        if (sample > 4095) sample = 4095;
        if (sample < 0) sample = 0;
        samples.push_back(sample);
    }
}

void test_voice_detection_silence(void) {
    VoiceDetection detector;
    std::vector<uint16_t> samples;
    createSilenceSamples(samples, 256);
    
    bool hasVoice = detector.detectVoice(samples);
    TEST_ASSERT_FALSE(hasVoice);
    
    auto stats = detector.getLastStats();
    TEST_ASSERT_LESS_THAN(100.0f, stats.avgAmplitude);
    TEST_ASSERT_EQUAL_UINT16(0, stats.maxAmplitude);
}

void test_voice_detection_low_amplitude(void) {
    VoiceDetection detector;
    std::vector<uint16_t> samples;
    createLowAmplitudeSamples(samples, 256);
    
    bool hasVoice = detector.detectVoice(samples);
    TEST_ASSERT_FALSE(hasVoice);
    
    auto stats = detector.getLastStats();
    TEST_ASSERT_LESS_THAN(1000.0f, stats.avgAmplitude);
}

void test_voice_detection_high_amplitude(void) {
    VoiceDetection detector;
    std::vector<uint16_t> samples;
    createHighAmplitudeSamples(samples, 256);

    bool hasVoice = detector.detectVoice(samples);
    TEST_ASSERT_TRUE(hasVoice);

    auto stats = detector.getLastStats();
    TEST_ASSERT_GREATER_THAN(1000.0f, stats.avgAmplitude);
    // Max amplitude for 12-bit samples is ~2047, so check avg amplitude as the main indicator
    TEST_ASSERT_GREATER_THAN(1500.0f, stats.avgAmplitude);
}

void test_voice_detection_max_amplitude_threshold(void) {
    VoiceDetection detector;
    std::vector<uint16_t> samples;

    // Create sample with very high single spike (should trigger)
    samples.push_back(2048);
    samples.push_back(2048 + 2047); // amplitude 2047, max possible for 12-bit
    samples.push_back(2048);

    bool hasVoice = detector.detectVoice(samples);
    TEST_ASSERT_TRUE(hasVoice);

    auto stats = detector.getLastStats();
    // Check max amplitude > 2000
    TEST_ASSERT_GREATER_THAN(2000, stats.maxAmplitude);
}

void test_voice_detection_empty_samples(void) {
    VoiceDetection detector;
    std::vector<uint16_t> samples;
    
    bool hasVoice = detector.detectVoice(samples);
    TEST_ASSERT_FALSE(hasVoice);
    
    auto stats = detector.getLastStats();
    TEST_ASSERT_EQUAL_FLOAT(0.0f, stats.avgAmplitude);
    TEST_ASSERT_EQUAL_UINT16(0, stats.maxAmplitude);
}

void test_voice_detection_zero_crossings(void) {
    VoiceDetection detector;
    std::vector<uint16_t> samples;
    
    // Create alternating high/low pattern (many zero crossings)
    for (size_t i = 0; i < 256; i++) {
        samples.push_back(i % 2 == 0 ? 0 : 4095);
    }
    
    bool hasVoice = detector.detectVoice(samples);
    TEST_ASSERT_TRUE(hasVoice);
    
    auto stats = detector.getLastStats();
    TEST_ASSERT_GREATER_THAN(1000.0f, stats.avgAmplitude);
    // Should have very high zero crossing rate
    TEST_ASSERT_GREATER_THAN(5000.0f, stats.zeroCrossingRate);
}

void test_voice_detection_sine_wave_low_freq(void) {
    VoiceDetection detector;
    std::vector<uint16_t> samples;
    
    // Low frequency sine wave with high amplitude
    createSineWaveSamples(samples, 256, 100.0f, 3000.0f);
    
    bool hasVoice = detector.detectVoice(samples);
    TEST_ASSERT_TRUE(hasVoice);
    
    auto stats = detector.getLastStats();
    TEST_ASSERT_GREATER_THAN(1000.0f, stats.avgAmplitude);
}

void test_voice_detection_sine_wave_high_freq(void) {
    VoiceDetection detector;
    std::vector<uint16_t> samples;

    // High frequency sine wave with high amplitude
    createSineWaveSamples(samples, 256, 4000.0f, 1800.0f);

    bool hasVoice = detector.detectVoice(samples);
    TEST_ASSERT_TRUE(hasVoice);

    auto stats = detector.getLastStats();
    TEST_ASSERT_GREATER_THAN(900.0f, stats.avgAmplitude);
}

void test_voice_detection_sine_wave_small_amplitude(void) {
    VoiceDetection detector;
    std::vector<uint16_t> samples;
    
    // Small amplitude sine wave (below threshold)
    createSineWaveSamples(samples, 256, 1000.0f, 500.0f);
    
    bool hasVoice = detector.detectVoice(samples);
    TEST_ASSERT_FALSE(hasVoice);
    
    auto stats = detector.getLastStats();
    TEST_ASSERT_LESS_THAN(1000.0f, stats.avgAmplitude);
}

void test_voice_detection_custom_parameters(void) {
    VoiceDetection::Parameters params;
    params.amplitudeThreshold = 20.0f; // Low threshold

    VoiceDetection detector(params);
    std::vector<uint16_t> samples;

    // Small variations that would trigger with lowered threshold
    // Low amplitude samples have avg ~25
    createLowAmplitudeSamples(samples, 256);

    bool hasVoice = detector.detectVoice(samples);
    TEST_ASSERT_TRUE(hasVoice); // Should detect with lowered threshold
}

void test_voice_detection_reset_detection(void) {
    VoiceDetection detector;
    std::vector<uint16_t> samples;
    
    createHighAmplitudeSamples(samples, 256);
    detector.detectVoice(samples);
    
    TEST_ASSERT_TRUE(detector.hasDetectedVoice());
    
    detector.resetDetection();
    TEST_ASSERT_FALSE(detector.hasDetectedVoice());
    
    // Create silence
    createSilenceSamples(samples, 256);
    detector.detectVoice(samples);
    
    // hasDetectedVoice_ only becomes true when voice is actually detected
    TEST_ASSERT_FALSE(detector.hasDetectedVoice());
}

void test_voice_detection_amplitude_calculation(void) {
    VoiceDetection detector;
    std::vector<uint16_t> samples;
    
    // Known amplitude values
    samples.push_back(2048);   // amplitude 0
    samples.push_back(3048);   // amplitude 1000
    samples.push_back(1048);   // amplitude 1000
    samples.push_back(2548);   // amplitude 500
    
    detector.detectVoice(samples);
    
    auto stats = detector.getLastStats();
    TEST_ASSERT_EQUAL_FLOAT(625.0f, stats.avgAmplitude); // (0+1000+1000+500)/4
    TEST_ASSERT_EQUAL_UINT16(1000, stats.maxAmplitude);
}

void test_voice_detection_buffer_sizes(void) {
    VoiceDetection detector;
    
    // Test with different buffer sizes
    std::vector<uint16_t> samples4;
    std::vector<uint16_t> samples256;
    std::vector<uint16_t> samples1024;
    
    createHighAmplitudeSamples(samples4, 4);
    createHighAmplitudeSamples(samples256, 256);
    createHighAmplitudeSamples(samples1024, 1024);
    
    TEST_ASSERT_TRUE(detector.detectVoice(samples4));
    TEST_ASSERT_TRUE(detector.detectVoice(samples256));
    TEST_ASSERT_TRUE(detector.detectVoice(samples1024));
}

void test_voice_detection_noise_floor(void) {
    VoiceDetection detector;
    std::vector<uint16_t> samples;
    
    // Add random noise below threshold
    for (size_t i = 0; i < 256; i++) {
        samples.push_back(2048 + ((i * 123) % 200 - 100));
    }
    
    bool hasVoice = detector.detectVoice(samples);
    TEST_ASSERT_FALSE(hasVoice);
    
    auto stats = detector.getLastStats();
    TEST_ASSERT_LESS_THAN(1000.0f, stats.avgAmplitude);
}

void run_voice_detection_tests(void) {
    UNITY_BEGIN();
    
    RUN_TEST(test_voice_detection_silence);
    RUN_TEST(test_voice_detection_low_amplitude);
    RUN_TEST(test_voice_detection_high_amplitude);
    RUN_TEST(test_voice_detection_max_amplitude_threshold);
    RUN_TEST(test_voice_detection_empty_samples);
    RUN_TEST(test_voice_detection_zero_crossings);
    RUN_TEST(test_voice_detection_sine_wave_low_freq);
    RUN_TEST(test_voice_detection_sine_wave_high_freq);
    RUN_TEST(test_voice_detection_sine_wave_small_amplitude);
    RUN_TEST(test_voice_detection_custom_parameters);
    RUN_TEST(test_voice_detection_reset_detection);
    RUN_TEST(test_voice_detection_amplitude_calculation);
    RUN_TEST(test_voice_detection_buffer_sizes);
    RUN_TEST(test_voice_detection_noise_floor);
    
    UNITY_END();
}

int main(void) {
    run_voice_detection_tests();
    return 0;
}
