/**
 * Voice detection algorithm for the MagicGPT8Ball recorder
 * Extracted from Recorder.cpp for unit testing
 * This module provides voice activity detection without hardware dependencies
 */

#ifndef VOICE_DETECTION_H
#define VOICE_DETECTION_H

#include <cstdint>
#include <vector>
#include <cmath>
#include <memory>

class VoiceDetection {
public:
    // Voice detection parameters
    struct Parameters {
        float amplitudeThreshold;      // Minimum average amplitude to detect voice
        float minZeroCrossingRate;     // Minimum zero crossings per second
        unsigned long silenceTimeout;  // ms before stopping recording after voice detected
        float voiceDetectionInterval;  // Debug print interval in ms
        
        Parameters()
            : amplitudeThreshold(1000.0f)
            , minZeroCrossingRate(50.0f)
            , silenceTimeout(2000)
            , voiceDetectionInterval(500) {}
    };
    
    VoiceDetection(const Parameters& params = Parameters());
    
    /**
     * Detect voice activity in a buffer of samples
     * @param samples Vector of 12-bit ADC samples (centered at 2048)
     * @return true if voice activity detected
     */
    bool detectVoice(const std::vector<uint16_t>& samples);
    
    /**
     * Get statistics about the last detection
     */
    struct DetectionStats {
        float avgAmplitude;
        uint16_t maxAmplitude;
        float zeroCrossingRate;
        bool hasVoice;
    };
    
    DetectionStats getLastStats() const { return lastStats_; }
    
    bool hasDetectedVoice() const { return hasDetectedVoice_; }
    void resetDetection() { hasDetectedVoice_ = false; }
    
private:
    Parameters params_;
    DetectionStats lastStats_;
    bool hasDetectedVoice_;
    unsigned long lastVoiceDebugTime_;
    
    void analyzeSamples(const std::vector<uint16_t>& samples);
    uint16_t getAmplitude(uint16_t sample);
};

#endif // VOICE_DETECTION_H
