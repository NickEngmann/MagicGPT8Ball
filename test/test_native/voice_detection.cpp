/**
 * Voice detection algorithm implementation
 * Extracted from Recorder.cpp for native testing
 */

#include "voice_detection.h"

VoiceDetection::VoiceDetection(const Parameters& params)
    : params_(params), hasDetectedVoice_(false), lastVoiceDebugTime_(0) {
}

uint16_t VoiceDetection::getAmplitude(uint16_t sample) {
    // Sample is centered at 2048 (midpoint of 12-bit ADC)
    int16_t centered = static_cast<int16_t>(sample) - 2048;
    return std::abs(centered);
}

void VoiceDetection::analyzeSamples(const std::vector<uint16_t>& samples) {
    if (samples.empty()) {
        lastStats_ = {0.0f, 0, 0.0f, false};
        return;
    }
    
    uint16_t minAmplitude = 65535;
    uint16_t maxAmplitude = 0;
    uint32_t sumAmplitude = 0;
    int zeroCrossings = 0;
    int16_t lastSample = 0;
    
    for (size_t i = 0; i < samples.size(); i++) {
        uint16_t amplitude = getAmplitude(samples[i]);
        minAmplitude = std::min(minAmplitude, amplitude);
        maxAmplitude = std::max(maxAmplitude, amplitude);
        sumAmplitude += amplitude;
        
        // Count zero crossings
        int16_t currentSample = static_cast<int16_t>(samples[i]) - 2048;
        if (lastSample < 0 && currentSample >= 0) {
            zeroCrossings++;
        }
        lastSample = currentSample;
    }
    
    uint16_t avgAmplitude = static_cast<uint16_t>(sumAmplitude / samples.size());
    
    // Calculate zero crossing rate per second
    // Samples are at 32kHz, so each sample represents 1/32000 seconds
    float sampleDurationSec = samples.size() / 32000.0f;
    float crossingRate = sampleDurationSec > 0 ? 
                         (zeroCrossings / sampleDurationSec) : 0.0f;
    
    lastStats_.avgAmplitude = static_cast<float>(avgAmplitude);
    lastStats_.maxAmplitude = maxAmplitude;
    lastStats_.zeroCrossingRate = crossingRate;
    
    // Voice detection: either avg amplitude above threshold OR max amplitude > 2000
    // For 12-bit samples (0-4095), max possible amplitude is 2047
    lastStats_.hasVoice = (avgAmplitude > params_.amplitudeThreshold) ||
                          (maxAmplitude > 2000);
}

bool VoiceDetection::detectVoice(const std::vector<uint16_t>& samples) {
    analyzeSamples(samples);
    
    // Track voice detection
    if (lastStats_.hasVoice) {
        hasDetectedVoice_ = true;
        lastVoiceDebugTime_ = 0; // Reset debug timing
    }
    
    return lastStats_.hasVoice;
}
