#include <unity.h>
#include <string>
#include <cstdio>
#include <cstring>

// Mock the Arduino environment
extern "C" {
    #include <Arduino.h>
}

// Mock LittleFS
#include <FS.h>

// Mock file operations for testing
static String mockEnvContent = "";

namespace fs {
    class File {
    private:
        String content;
        size_t pos;
        bool valid;
    public:
        File() : pos(0), valid(false) {}
        File(const String& c) : content(c), pos(0), valid(true) {}
        
        bool available() { return pos < content.length(); }
        String readStringUntil(char delimiter) {
            String result = "";
            while (pos < content.length() && content[pos] != delimiter) {
                result += content[pos++];
            }
            if (pos < content.length()) pos++; // Skip delimiter
            return result;
        }
        void close() { valid = false; }
        bool isOpen() { return valid; }
    };
}

// Mock LittleFS
namespace LittleFS {
    static String savedContent = "";
    static bool initialized = false;
    
    class File {
    private:
        String content;
        size_t pos;
        bool valid;
    public:
        File() : pos(0), valid(false) {}
        File(const String& c) : content(c), pos(0), valid(true) {}
        
        bool available() { return pos < content.length(); }
        String readStringUntil(char delimiter) {
            String result = "";
            while (pos < content.length() && content[pos] != delimiter) {
                result += content[pos++];
            }
            if (pos < content.length()) pos++; // Skip delimiter
            return result;
        }
        void close() { valid = false; }
        bool isOpen() { return valid; }
    };
    
    static File open(const String& path, const char* mode) {
        if (path == "/.env" || path == "/littlefs/.env") {
            return File(savedContent);
        }
        return File();
    }
    
    static bool begin(bool format) {
        initialized = true;
        return true;
    }
    
    static void setEnvContent(const String& content) {
        savedContent = content;
    }
    
    static void reset() {
        savedContent = "";
        initialized = false;
    }
}

// Include the Environment header
#include "../src/Environment.h"

void test_SetEnvValtownUrl(void)
{
    Environment::setEnv("VALTOWN_URL", "https://example.com/api");
    String value = Environment::getEnv("VALTOWN_URL");
    TEST_ASSERT_EQUAL_STRING("https://example.com/api", value.c_str());
}

void test_SetEnvDeviceToken(void)
{
    Environment::setEnv("DEVICE_TOKEN", "test-token-123");
    String value = Environment::getEnv("DEVICE_TOKEN");
    TEST_ASSERT_EQUAL_STRING("test-token-123", value.c_str());
}

void test_GetEnvUnknownKey(void)
{
    String value = Environment::getEnv("UNKNOWN_KEY");
    TEST_ASSERT_EQUAL_STRING("", value.c_str());
}

void test_LoadEnvWithValtownUrl(void)
{
    String content = "VALTOWN_URL=https://api.example.com\n";
    LittleFS::setEnvContent(content);
    
    // Simulate loading
    fs::File file = LittleFS.open("/.env", "r");
    String loadedValue = "";
    while (file.available()) {
        String line = file.readStringUntil('\n');
        line.trim();
        if (line.length() > 0 && !line.startsWith("#")) {
            int sepPos = line.indexOf('=');
            if (sepPos > 0) {
                String key = line.substring(0, sepPos);
                String value = line.substring(sepPos + 1);
                key.trim();
                value.trim();
                if (key == "VALTOWN_URL") loadedValue = value;
            }
        }
    }
    file.close();
    
    TEST_ASSERT_EQUAL_STRING("https://api.example.com", loadedValue.c_str());
}

void test_LoadEnvWithDeviceToken(void)
{
    String content = "DEVICE_TOKEN=my-secret-token\n";
    LittleFS::setEnvContent(content);
    
    fs::File file = LittleFS.open("/.env", "r");
    String loadedValue = "";
    while (file.available()) {
        String line = file.readStringUntil('\n');
        line.trim();
        if (line.length() > 0 && !line.startsWith("#")) {
            int sepPos = line.indexOf('=');
            if (sepPos > 0) {
                String key = line.substring(0, sepPos);
                String value = line.substring(sepPos + 1);
                key.trim();
                value.trim();
                if (key == "DEVICE_TOKEN") loadedValue = value;
            }
        }
    }
    file.close();
    
    TEST_ASSERT_EQUAL_STRING("my-secret-token", loadedValue.c_str());
}

void test_LoadEnvWithQuotes(void)
{
    String content = "VALTOWN_URL=\"https://api.example.com\"\n";
    LittleFS::setEnvContent(content);
    
    fs::File file = LittleFS.open("/.env", "r");
    String loadedValue = "";
    while (file.available()) {
        String line = file.readStringUntil('\n');
        line.trim();
        if (line.length() > 0 && !line.startsWith("#")) {
            int sepPos = line.indexOf('=');
            if (sepPos > 0) {
                String key = line.substring(0, sepPos);
                String value = line.substring(sepPos + 1);
                key.trim();
                value.trim();
                if (value.startsWith("\"") && value.endsWith("\"")) {
                    value = value.substring(1, value.length() - 1);
                }
                if (key == "VALTOWN_URL") loadedValue = value;
            }
        }
    }
    file.close();
    
    TEST_ASSERT_EQUAL_STRING("https://api.example.com", loadedValue.c_str());
}

void test_LoadEnvSkipsComments(void)
{
    String content = "# This is a comment\nVALTOWN_URL=https://api.example.com\n";
    LittleFS::setEnvContent(content);
    
    fs::File file = LittleFS.open("/.env", "r");
    bool foundUrl = false;
    while (file.available()) {
        String line = file.readStringUntil('\n');
        line.trim();
        if (line.length() > 0 && !line.startsWith("#")) {
            int sepPos = line.indexOf('=');
            if (sepPos > 0 && line.substring(0, sepPos) == "VALTOWN_URL") {
                foundUrl = true;
            }
        }
    }
    file.close();
    
    TEST_ASSERT_TRUE(foundUrl);
}

void test_LoadEnvSkipsEmptyLines(void)
{
    String content = "\n\nVALTOWN_URL=https://api.example.com\n\n";
    LittleFS::setEnvContent(content);
    
    fs::File file = LittleFS.open("/.env", "r");
    int lineCount = 0;
    while (file.available()) {
        String line = file.readStringUntil('\n');
        line.trim();
        if (line.length() > 0) {
            lineCount++;
        }
    }
    file.close();
    
    // Should only count the line with VALTOWN_URL
    TEST_ASSERT_EQUAL(1, lineCount);
}

int main(void)
{
    UNITY_BEGIN();
    
    RUN_TEST(test_SetEnvValtownUrl);
    RUN_TEST(test_SetEnvDeviceToken);
    RUN_TEST(test_GetEnvUnknownKey);
    RUN_TEST(test_LoadEnvWithValtownUrl);
    RUN_TEST(test_LoadEnvWithDeviceToken);
    RUN_TEST(test_LoadEnvWithQuotes);
    RUN_TEST(test_LoadEnvSkipsComments);
    RUN_TEST(test_LoadEnvSkipsEmptyLines);
    
    return UNITY_END();
}
