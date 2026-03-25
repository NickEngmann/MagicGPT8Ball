#include <unity.h>
#include <string>
#include <vector>
#include <map>
#include <cstring>

// Test WAV file upload functionality
class TestWAVUploader {
public:
    struct UploadResult {
        bool success;
        int httpCode;
        std::string message;
        size_t bytesSent;
    };
    
private:
    std::vector<uint8_t> wavBuffer;
    std::map<std::string, std::string> headers;
    std::string baseUrl;
    
public:
    TestWAVUploader() {}
    
    bool initialize(const std::string& url) {
        baseUrl = url;
        wavBuffer.clear();
        headers.clear();
        return !url.empty();
    }
    
    void addMetadata(uint8_t* data, size_t size) {
        // Simulate adding metadata to buffer
        for (size_t i = 0; i < size; i++) {
            wavBuffer.push_back(data[i]);
        }
    }
    
    void buildWAVHeader(size_t sampleCount) {
        // Build basic WAV header (44 bytes)
        std::vector<uint8_t> header(44, 0);
        
        // RIFF header
        header[0] = 'R'; header[1] = 'I'; header[2] = 'F'; header[3] = 'F';
        
        // File size (little-endian)
        size_t fileSize = 36 + (sampleCount * 2);
        header[4] = fileSize & 0xFF;
        header[5] = (fileSize >> 8) & 0xFF;
        header[6] = (fileSize >> 16) & 0xFF;
        header[7] = (fileSize >> 24) & 0xFF;
        
        // WAVE header
        header[8] = 'W'; header[9] = 'A'; header[10] = 'V'; header[11] = 'E';
        
        // fmt chunk
        header[12] = 'f'; header[13] = 'm'; header[14] = 't'; header[15] = ' ';
        header[16] = 16; header[17] = 0; header[18] = 0; header[19] = 0; // Chunk size
        header[20] = 1; header[21] = 0; // Audio format (PCM)
        header[22] = 1; header[23] = 0; // Channels (mono)
        header[24] = 0x80; header[25] = 0x78; // Sample rate (32000 Hz)
        header[26] = 0x00; header[27] = 0x00;
        header[28] = 0x00; header[29] = 0x7A; // Byte rate (64000)
        header[30] = 0x00; header[31] = 0x00;
        header[32] = 2; header[33] = 0; // Block align
        header[34] = 16; header[35] = 0; // Bits per sample
        
        // data chunk
        header[36] = 'd'; header[37] = 'a'; header[38] = 't'; header[39] = 'a';
        size_t dataSize = sampleCount * 2;
        header[40] = dataSize & 0xFF;
        header[41] = (dataSize >> 8) & 0xFF;
        header[42] = (dataSize >> 16) & 0xFF;
        header[43] = (dataSize >> 24) & 0xFF;
        
        wavBuffer = header;
    }
    
    void addAudioSamples(const uint8_t* samples, size_t sampleCount) {
        for (size_t i = 0; i < sampleCount; i++) {
            // Add 16-bit sample (little-endian)
            wavBuffer.push_back(samples[i * 2]);
            wavBuffer.push_back(samples[i * 2 + 1]);
        }
    }
    
    size_t getBufferSize() {
        return wavBuffer.size();
    }
    
    uint8_t* getBuffer() {
        return wavBuffer.data();
    }
    
    UploadResult upload(const std::string& token) {
        UploadResult result;
        result.success = false;
        result.httpCode = 0;
        result.bytesSent = wavBuffer.size();
        
        if (wavBuffer.empty()) {
            result.message = "No WAV data to upload";
            return result;
        }
        
        if (token.empty()) {
            result.message = "Missing device token";
            return result;
        }
        
        if (baseUrl.empty()) {
            result.message = "Missing upload URL";
            return result;
        }
        
        // Simulate successful upload
        result.success = true;
        result.httpCode = 200;
        result.message = "Upload successful";
        
        return result;
    }
    
    static bool isValidWAVHeader(const uint8_t* header) {
        if (!header) return false;
        
        // Check RIFF signature
        if (header[0] != 'R' || header[1] != 'I' || 
            header[2] != 'F' || header[3] != 'F') {
            return false;
        }
        
        // Check WAVE signature
        if (header[8] != 'W' || header[9] != 'A' || 
            header[10] != 'V' || header[11] != 'E') {
            return false;
        }
        
        // Check fmt chunk
        if (header[12] != 'f' || header[13] != 'm' || 
            header[14] != 't' || header[15] != ' ') {
            return false;
        }
        
        // Check data chunk
        if (header[36] != 'd' || header[37] != 'a' || 
            header[38] != 't' || header[39] != 'a') {
            return false;
        }
        
        return true;
    }
    
    static size_t calculateWAVSize(size_t sampleCount) {
        return 44 + (sampleCount * 2); // Header + samples
    }
};

// WAVUploader mock for testing
TestWAVUploader wavUploader;

void setUp(void) {
    wavUploader.initialize("http://192.168.1.108:5000/upload_wav");
}

void tearDown(void) {}

void test_wav_uploader_initialization(void) {
    TEST_ASSERT_TRUE(wavUploader.initialize("http://localhost:5000/upload"));
    TEST_ASSERT_EQUAL_STRING("http://localhost:5000/upload", 
                            wavUploader.baseUrl.c_str());
}

void test_wav_uploader_invalid_url(void) {
    TEST_ASSERT_FALSE(wavUploader.initialize(""));
}

void test_wav_header_structure(void) {
    wavUploader.buildWAVHeader(1000);
    TEST_ASSERT_GREATER_THAN(44, wavUploader.getBufferSize());
    
    uint8_t* buffer = wavUploader.getBuffer();
    TEST_ASSERT_TRUE(TestWAVUploader::isValidWAVHeader(buffer));
}

void test_wav_header_validation(void) {
    // Create valid header
    wavUploader.buildWAVHeader(1000);
    TEST_ASSERT_TRUE(TestWAVUploader::isValidWAVHeader(wavUploader.getBuffer()));
    
    // Create invalid header
    std::vector<uint8_t> invalidHeader(44, 0);
    invalidHeader[0] = 'X';
    TEST_ASSERT_FALSE(TestWAVUploader::isValidWAVHeader(invalidHeader.data()));
}

void test_wav_sample_count_calculation(void) {
    size_t sampleCount = 2048;
    size_t expectedSize = wavUploader.calculateWAVSize(sampleCount);
    
    wavUploader.buildWAVHeader(sampleCount);
    TEST_ASSERT_EQUAL_UINT(expectedSize, wavUploader.getBufferSize());
}

void test_wav_upload_success(void) {
    wavUploader.buildWAVHeader(1000);
    
    TestWAVUploader::UploadResult result = wavUploader.upload("test-token-123");
    
    TEST_ASSERT_TRUE(result.success);
    TEST_ASSERT_EQUAL_INT(200, result.httpCode);
    TEST_ASSERT_GREATER_THAN(0, result.bytesSent);
}

void test_wav_upload_no_data(void) {
    TestWAVUploader::UploadResult result = wavUploader.upload("test-token");
    
    TEST_ASSERT_FALSE(result.success);
    TEST_ASSERT_EQUAL_STRING("No WAV data to upload", result.message.c_str());
}

void test_wav_upload_no_token(void) {
    wavUploader.buildWAVHeader(1000);
    
    TestWAVUploader::UploadResult result = wavUploader.upload("");
    
    TEST_ASSERT_FALSE(result.success);
    TEST_ASSERT_EQUAL_STRING("Missing device token", result.message.c_str());
}

void test_wav_upload_no_url(void) {
    wavUploader.initialize("");
    wavUploader.buildWAVHeader(1000);
    
    TestWAVUploader::UploadResult result = wavUploader.upload("test-token");
    
    TEST_ASSERT_FALSE(result.success);
    TEST_ASSERT_EQUAL_STRING("Missing upload URL", result.message.c_str());
}

void test_wav_multiple_samples(void) {
    std::vector<uint8_t> samples(2048, 0);
    for (size_t i = 0; i < 1024; i++) {
        samples[i * 2] = i & 0xFF;
        samples[i * 2 + 1] = (i >> 8) & 0xFF;
    }
    
    wavUploader.buildWAVHeader(1024);
    wavUploader.addAudioSamples(samples.data(), 1024);
    
    TEST_ASSERT_EQUAL_UINT(44 + 2048, wavUploader.getBufferSize());
    
    TestWAVUploader::UploadResult result = wavUploader.upload("test-token");
    TEST_ASSERT_TRUE(result.success);
}

void test_wav_header_size(void) {
    wavUploader.buildWAVHeader(1000);
    TEST_ASSERT_EQUAL_UINT(44, wavUploader.getBufferSize()); // Just header
    
    wavUploader.addAudioSamples(new uint8_t[2000], 1000);
    TEST_ASSERT_EQUAL_UINT(2044, wavUploader.getBufferSize()); // Header + samples
    
    delete[] new uint8_t[2000];
}

void test_wav_file_size_calculation(void) {
    TEST_ASSERT_EQUAL_UINT(44 + 2000, 
                          TestWAVUploader::calculateWAVSize(1000));
    TEST_ASSERT_EQUAL_UINT(44 + 64000, 
                          TestWAVUploader::calculateWAVSize(32000));
    TEST_ASSERT_EQUAL_UINT(44 + 320000, 
                          TestWAVUploader::calculateWAVSize(160000));
}

int main(void) {
    UNITY_BEGIN();
    
    RUN_TEST(test_wav_uploader_initialization);
    RUN_TEST(test_wav_uploader_invalid_url);
    RUN_TEST(test_wav_header_structure);
    RUN_TEST(test_wav_header_validation);
    RUN_TEST(test_wav_sample_count_calculation);
    RUN_TEST(test_wav_upload_success);
    RUN_TEST(test_wav_upload_no_data);
    RUN_TEST(test_wav_upload_no_token);
    RUN_TEST(test_wav_upload_no_url);
    RUN_TEST(test_wav_multiple_samples);
    RUN_TEST(test_wav_header_size);
    RUN_TEST(test_wav_file_size_calculation);
    
    return UNITY_END();
}
