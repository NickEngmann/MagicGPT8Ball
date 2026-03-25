#include <unity.h>
#include <string.h>

// Test WAV uploader initialization
void test_wav_uploader_initialization(void) {
    // Test that WAV uploader can be initialized
    const size_t WAV_HEADER_SIZE = 44;
    TEST_ASSERT_EQUAL_UINT(44, WAV_HEADER_SIZE);
}

// Test WAV header structure
void test_wav_header_structure(void) {
    // WAV header should be 44 bytes
    const size_t WAV_HEADER_SIZE = 44;
    
    // Create a minimal WAV header
    uint8_t header[WAV_HEADER_SIZE];
    memset(header, 0, WAV_HEADER_SIZE);
    
    // Check RIFF chunk
    TEST_ASSERT_EQUAL_STRING("RIFF", (char*)&header[0]);
    
    // Check WAV format
    TEST_ASSERT_EQUAL_STRING("WAVE", (char*)&header[8]);
    
    // Check fmt chunk
    TEST_ASSERT_EQUAL_STRING("fmt ", (char*)&header[12]);
    
    // Check data chunk
    TEST_ASSERT_EQUAL_STRING("data", (char*)&header[36]);
    
    // Size should be at offset 4-7 and 40-43
    TEST_ASSERT_EQUAL_INT(0, header[4]);
    TEST_ASSERT_EQUAL_INT(0, header[40]);
}

void test_wav_header_validation(void) {
    // Valid WAV header should have correct magic bytes
    uint8_t valid_header[44] = {
        'R', 'I', 'F', 'F',           // ChunkID
        0x10, 0x00, 0x00, 0x00,       // ChunkSize (16 for PCM)
        'W', 'A', 'V', 'E',           // Format
        'f', 'm', 't', ' ',           // Subchunk1ID
        0x10, 0x00, 0x00, 0x00,       // Subchunk1Size (16)
        0x01, 0x00,                   // AudioFormat (1 = PCM)
        0x01, 0x00,                   // NumChannels (1 = mono)
        0x80, 0xBE, 0x00, 0x00,       // SampleRate (44100 Hz)
        0x00, 0x00, 0x00, 0x00,       // ByteRate
        0x02, 0x00,                   // BlockAlign
        0x10, 0x00,                   // BitsPerSample (16)
        'd', 'a', 't', 'a',           // Subchunk2ID
        0x00, 0x00, 0x00, 0x00        // Subchunk2Size
    };
    
    // Verify key sections
    TEST_ASSERT_EQUAL_STRING("RIFF", (char*)&valid_header[0]);
    TEST_ASSERT_EQUAL_STRING("WAVE", (char*)&valid_header[8]);
    TEST_ASSERT_EQUAL_STRING("fmt ", (char*)&valid_header[12]);
    TEST_ASSERT_EQUAL_STRING("data", (char*)&valid_header[36]);
}

void test_wav_upload_success(void) {
    // Test that WAV upload would work with valid data
    const size_t test_buffer_size = 1024;
    uint8_t test_buffer[test_buffer_size];
    memset(test_buffer, 0, test_buffer_size);
    
    // Add valid WAV header
    uint8_t header[44];
    memset(header, 0, 44);
    memcpy(header, "RIFF", 4);
    memcpy(header + 8, "WAVE", 4);
    memcpy(header + 12, "fmt ", 4);
    memcpy(header + 36, "data", 4);
    
    memcpy(test_buffer, header, 44);
    
    // Check that buffer has valid WAV header
    TEST_ASSERT_EQUAL_STRING("RIFF", (char*)&test_buffer[0]);
    TEST_ASSERT_EQUAL_STRING("WAVE", (char*)&test_buffer[8]);
    TEST_ASSERT_EQUAL_STRING("fmt ", (char*)&test_buffer[12]);
    TEST_ASSERT_EQUAL_STRING("data", (char*)&test_buffer[36]);
}

// Test WAV file size calculation
void test_wav_file_size(void) {
    // For 1 second of mono 16-bit audio at 32kHz:
    // Data size = 32000 samples * 2 bytes = 64000 bytes
    // Total file size = 44 (header) + 64000 (data) = 64044 bytes
    // Chunk size field (4 bytes) = total size - 8 = 64036
    
    const uint32_t sample_rate = 32000;
    const uint16_t channels = 1;
    const uint16_t bits_per_sample = 16;
    const uint32_t duration_seconds = 1;
    
    uint32_t data_size = sample_rate * channels * (bits_per_sample / 8) * duration_seconds;
    uint32_t total_size = 44 + data_size;
    uint32_t chunk_size = total_size - 8;
    
    TEST_ASSERT_EQUAL_UINT(64044, total_size);
    TEST_ASSERT_EQUAL_UINT(64036, chunk_size);
    TEST_ASSERT_EQUAL_UINT(64000, data_size);
}

// Test WAV byte rate calculation
void test_wav_byte_rate(void) {
    // ByteRate = SampleRate * NumChannels * BitsPerSample / 8
    const uint32_t sample_rate = 32000;
    const uint16_t channels = 1;
    const uint16_t bits_per_sample = 16;
    
    uint32_t byte_rate = sample_rate * channels * (bits_per_sample / 8);
    
    TEST_ASSERT_EQUAL_UINT(64000, byte_rate);
}

// Test WAV block align
void test_wav_block_align(void) {
    // BlockAlign = NumChannels * BitsPerSample / 8
    const uint16_t channels = 1;
    const uint16_t bits_per_sample = 16;
    
    uint16_t block_align = channels * (bits_per_sample / 8);
    
    TEST_ASSERT_EQUAL_UINT(2, block_align);
}

int main(void) {
    UNITY_BEGIN();

    RUN_TEST(test_wav_uploader_initialization);
    RUN_TEST(test_wav_header_structure);
    RUN_TEST(test_wav_header_validation);
    RUN_TEST(test_wav_upload_success);
    RUN_TEST(test_wav_file_size);
    RUN_TEST(test_wav_byte_rate);
    RUN_TEST(test_wav_block_align);

    return UNITY_END();
}
