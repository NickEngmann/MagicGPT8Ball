#include <unity.h>
#include <algorithm>
#include <cmath>
#include <vector>

// Test Recorder module functionality
class TestRecorder {
private:
    std::vector<uint8_t> audioBuffer;
    size_t bufferIndex;
    bool isRecording;
    unsigned long recordStartTime;
    const size_t MAX_RECORD_SIZE = 320000; // 10 seconds at 32kHz, 16-bit, mono
    
public:
    TestRecorder() : bufferIndex(0), isRecording(false), recordStartTime(0) {}
    
    bool begin() {
        audioBuffer.clear();
        audioBuffer.resize(MAX_RECORD_SIZE, 0);
        return true;
    }
    
    bool startRecording() {
        if (isRecording) {
            return false;
        }
        audioBuffer.clear();
        audioBuffer.resize(MAX_RECORD_SIZE, 0);
        bufferIndex = 0;
        isRecording = true;
        recordStartTime = millisMock();
        return true;
    }
    
    void stopRecording() {
        isRecording = false;
    }
    
    void update() {
        if (!isRecording) {
            return;
        }
        
        // Simulate audio sampling
        addMockAudioSample();
    }
    
    uint8_t* getBuffer() {
        return bufferIndex > 0 ? audioBuffer.data() : nullptr;
    }
    
    size_t getBufferSize() {
        return bufferIndex;
    }
    
    bool isRecordingState() {
        return isRecording;
    }
    
    float getRecordingProgress() {
        if (!isRecording || recordStartTime == 0) {
            return 0.0f;
        }
        unsigned long elapsed = millisMock() - recordStartTime;
        return std::min(1.0f, static_cast<float>(elapsed) / 10000.0f);
    }
    
    uint16_t getMockAudioSample() {
        // Simulate ADC values (mono, 16-bit)
        static uint16_t sampleCounter = 0;
        sampleCounter++;
        
        // Create a simple sine wave pattern for testing
        float frequency = 440.0f; // A4 note
        float phase = (sampleCounter * 2 * M_PI * frequency) / 32000.0f;
        int16_t value = static_cast<int16_t>(2048 + 1000 * sin(phase));
        
        return static_cast<uint16_t>(value & 0xFFFF);
    }
    
    void addMockAudioSample() {
        if (bufferIndex + 2 <= MAX_RECORD_SIZE) {
            uint16_t sample = getMockAudioSample();
            audioBuffer[bufferIndex++] = sample & 0xFF;
            audioBuffer[bufferIndex++] = (sample >> 8) & 0xFF;
        }
    }
    
    bool detectVoiceActivity(const std::vector<uint8_t>& buffer, size_t size) {
        if (size < 256) {
            return false;
        }
        
        // Calculate average amplitude
        int32_t sum = 0;
        for (size_t i = 0; i < size; i += 2) {
            uint16_t sample = buffer[i] | (buffer[i + 1] << 8);
            int16_t normalized = static_cast<int16_t>(sample) - 1250; // Remove DC offset
            sum += std::abs(normalized);
        }
        
        float avgAmplitude = static_cast<float>(sum) / (size / 2);
        return avgAmplitude > 500; // AUDIO_THRESHOLD
    }
    
    void writeWAVHeader(uint8_t* header, size_t sampleCount) {
        // Basic WAV header structure
        // This is a simplified version for testing
        if (sampleCount > 0 && header) {
            // RIFF header (first 4 bytes)
            header[0] = 'R'; header[1] = 'I'; header[2] = 'F'; header[3] = 'F';
        }
    }
    
    void updateWAVHeader(uint8_t* header, size_t sampleCount) {
        if (header && sampleCount > 0) {
            // Update file size in header
            size_t fileSize = 44 + (sampleCount * 2);
            header[18] = fileSize & 0xFF;
            header[19] = (fileSize >> 8) & 0xFF;
            header[20] = (fileSize >> 16) & 0xFF;
            header[21] = (fileSize >> 24) & 0xFF;
            // Update data size in header
            size_t dataSize = sampleCount * 2;
            header[34] = dataSize & 0xFF;
            header[35] = (dataSize >> 8) & 0xFF;
            header[36] = (dataSize >> 16) & 0xFF;
            header[37] = (dataSize >> 24) & 0xFF;
        }
    }
    
    static unsigned long millisMock() {
        static unsigned long mockTime = 0;
        return mockTime++;
    }
    
    static void setMillisMock(unsigned long time) {
        mockTime = time;
    }
};

// Recorder mock for testing
TestRecorder mockRecorder;

void setUp(void) {
    mockRecorder.begin();
}

void tearDown(void) {}

void test_recorder_initialization(void) {
    TEST_ASSERT_TRUE(mockRecorder.begin());
    TEST_ASSERT_FALSE(mockRecorder.isRecordingState());
}

void test_recorder_start_stop(void) {
    TEST_ASSERT_TRUE(mockRecorder.startRecording());
    TEST_ASSERT_TRUE(mockRecorder.isRecordingState());
    
    mockRecorder.update();
    TEST_ASSERT_GREATER_THAN(0, mockRecorder.getBufferSize());
    
    mockRecorder.stopRecording();
    TEST_ASSERT_FALSE(mockRecorder.isRecordingState());
}

void test_recorder_buffer_allocation(void) {
    TEST_ASSERT_TRUE(mockRecorder.startRecording());
    TEST_ASSERT_NOT_NULL(mockRecorder.getBuffer());
    TEST_ASSERT_EQUAL_UINT(320000, mockRecorder.getBufferSize()); // Initial size
    mockRecorder.stopRecording();
}

void test_recorder_audio_sampling(void) {
    mockRecorder.startRecording();
    
    // Run update multiple times to collect samples
    for (int i = 0; i < 100; i++) {
        mockRecorder.update();
        TEST_ASSERT_GREATER_THAN(0, mockRecorder.getBufferSize());
    }
    
    TEST_ASSERT_GREATER_THAN(100, mockRecorder.getBufferSize());
    mockRecorder.stopRecording();
}

void test_recorder_voice_activity_detection(void) {
    // Create a buffer with voice-like activity
    std::vector<uint8_t> activeBuffer(512, 0);
    
    // Add some amplitude variations
    for (size_t i = 0; i < activeBuffer.size(); i += 2) {
        activeBuffer[i] = 1000 + (i % 500);
        activeBuffer[i + 1] = 256;
    }
    
    TEST_ASSERT_TRUE(mockRecorder.detectVoiceActivity(activeBuffer, activeBuffer.size()));
    
    // Create a quiet buffer
    std::vector<uint8_t> quietBuffer(512, 0);
    std::fill(quietBuffer.begin(), quietBuffer.end(), 1250);
    
    TEST_ASSERT_FALSE(mockRecorder.detectVoiceActivity(quietBuffer, quietBuffer.size()));
}

void test_recorder_wav_header_write(void) {
    uint8_t header[44] = {0};
    mockRecorder.writeWAVHeader(header, 1000);
    
    TEST_ASSERT_EQUAL_INT('R', header[0]);
    TEST_ASSERT_EQUAL_INT('I', header[1]);
    TEST_ASSERT_EQUAL_INT('F', header[2]);
    TEST_ASSERT_EQUAL_INT('F', header[3]);
}

void test_recorder_wav_header_update(void) {
    uint8_t header[44] = {0};
    size_t sampleCount = 2000;
    
    mockRecorder.updateWAVHeader(header, sampleCount);
    
    // Check that header was written
    TEST_ASSERT_EQUAL_INT('R', header[0]);
    TEST_ASSERT_EQUAL_INT('F', header[3]);
}

void test_recorder_progress_calculation(void) {
    TestRecorder::setMillisMock(0);
    mockRecorder.startRecording();
    TEST_ASSERT_EQUAL_FLOAT(0.0f, mockRecorder.getRecordingProgress());
    
    TestRecorder::setMillisMock(5000);
    TEST_ASSERT_EQUAL_FLOAT(0.5f, mockRecorder.getRecordingProgress());
    
    TestRecorder::setMillisMock(15000);
    TEST_ASSERT_EQUAL_FLOAT(1.0f, mockRecorder.getRecordingProgress());
    
    mockRecorder.stopRecording();
}

void test_recorder_buffer_overflow_protection(void) {
    mockRecorder.startRecording();
    
    // Simulate recording beyond max duration
    for (int i = 0; i < 50000; i++) {
        mockRecorder.update();
    }
    
    // Buffer should not exceed max size
    TEST_ASSERT_LESS_THAN_OR_EQUAL(320000, mockRecorder.getBufferSize());
    mockRecorder.stopRecording();
}

void test_recorder_restart_after_stop(void) {
    mockRecorder.startRecording();
    size_t firstBufferSize = mockRecorder.getBufferSize();
    mockRecorder.stopRecording();
    
    mockRecorder.startRecording();
    TEST_ASSERT_GREATER_THAN(firstBufferSize, mockRecorder.getBufferSize());
    mockRecorder.stopRecording();
}

void test_recorder_buffer_null_when_not_recording(void) {
    mockRecorder.stopRecording();
    TEST_ASSERT_NULL(mockRecorder.getBuffer());
}

int main(void) {
    UNITY_BEGIN();
    
    RUN_TEST(test_recorder_initialization);
    RUN_TEST(test_recorder_start_stop);
    RUN_TEST(test_recorder_buffer_allocation);
    RUN_TEST(test_recorder_audio_sampling);
    RUN_TEST(test_recorder_voice_activity_detection);
    RUN_TEST(test_recorder_wav_header_write);
    RUN_TEST(test_recorder_wav_header_update);
    RUN_TEST(test_recorder_progress_calculation);
    RUN_TEST(test_recorder_buffer_overflow_protection);
    RUN_TEST(test_recorder_restart_after_stop);
    RUN_TEST(test_recorder_buffer_null_when_not_recording);
    
    return UNITY_END();
}
