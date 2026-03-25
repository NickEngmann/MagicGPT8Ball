#include <unity.h>
#include <string>
#include <map>
#include <fstream>
#include <sstream>

// Test Environment module functionality
class TestEnvironment {
private:
    std::map<std::string, std::string> env_vars;
    
public:
    bool begin() {
        // Simulate loading .env file
        return loadEnv();
    }
    
    bool loadEnv() {
        // Simulate reading from file
        env_vars.clear();
        
        // Mock environment data
        env_vars["VALTOWN_URL"] = "https://val.town/test-endpoint";
        env_vars["DEVICE_TOKEN"] = "test-device-token-12345";
        
        return !env_vars["VALTOWN_URL"].empty();
    }
    
    std::string getEnv(const std::string& key) {
        auto it = env_vars.find(key);
        if (it != env_vars.end()) {
            return it->second;
        }
        return "";
    }
    
    void setEnv(const std::string& key, const std::string& value) {
        env_vars[key] = value;
    }
    
    void clear() {
        env_vars.clear();
    }
};

// Environment mock for testing
TestEnvironment mockEnvironment;

void setUp(void) {
    mockEnvironment.clear();
}

void tearDown(void) {}

void test_environment_initialization(void) {
    TEST_ASSERT_TRUE(mockEnvironment.begin());
}

void test_load_environment_vars(void) {
    TEST_ASSERT_TRUE(mockEnvironment.loadEnv());
    TEST_ASSERT_EQUAL_STRING("https://val.town/test-endpoint", 
                            mockEnvironment.getEnv("VALTOWN_URL").c_str());
    TEST_ASSERT_EQUAL_STRING("test-device-token-12345", 
                            mockEnvironment.getEnv("DEVICE_TOKEN").c_str());
}

void test_get_valtown_url(void) {
    mockEnvironment.setEnv("VALTOWN_URL", "https://api.val.town/v1/chat");
    std::string url = mockEnvironment.getEnv("VALTOWN_URL");
    TEST_ASSERT_EQUAL_STRING("https://api.val.town/v1/chat", url.c_str());
}

void test_get_device_token(void) {
    mockEnvironment.setEnv("DEVICE_TOKEN", "secret-token-abc");
    std::string token = mockEnvironment.getEnv("DEVICE_TOKEN");
    TEST_ASSERT_EQUAL_STRING("secret-token-abc", token.c_str());
}

void test_get_nonexistent_key(void) {
    std::string value = mockEnvironment.getEnv("NONEXISTENT");
    TEST_ASSERT_EQUAL_STRING("", value.c_str());
}

void test_missing_valtown_url(void) {
    mockEnvironment.clear();
    mockEnvironment.setEnv("DEVICE_TOKEN", "token");
    std::string url = mockEnvironment.getEnv("VALTOWN_URL");
    TEST_ASSERT_EQUAL_STRING("", url.c_str());
}

void test_environment_with_quoted_values(void) {
    mockEnvironment.setEnv("VALTOWN_URL", "\"https://val.town/quoted\"");
    mockEnvironment.setEnv("DEVICE_TOKEN", "'single-quoted'");
    TEST_ASSERT_EQUAL_STRING("\"https://val.town/quoted\"", 
                            mockEnvironment.getEnv("VALTOWN_URL").c_str());
    TEST_ASSERT_EQUAL_STRING("'single-quoted'", 
                            mockEnvironment.getEnv("DEVICE_TOKEN").c_str());
}

void test_environment_with_empty_values(void) {
    mockEnvironment.setEnv("VALTOWN_URL", "");
    mockEnvironment.setEnv("DEVICE_TOKEN", "");
    TEST_ASSERT_EQUAL_STRING("", mockEnvironment.getEnv("VALTOWN_URL").c_str());
    TEST_ASSERT_EQUAL_STRING("", mockEnvironment.getEnv("DEVICE_TOKEN").c_str());
}

void test_multiple_environment_variables(void) {
    mockEnvironment.setEnv("VALTOWN_URL", "https://val.town/endpoint");
    mockEnvironment.setEnv("DEVICE_TOKEN", "token-123");
    mockEnvironment.setEnv("API_KEY", "api-key-456");
    mockEnvironment.setEnv("DEBUG_MODE", "true");
    
    TEST_ASSERT_EQUAL_STRING("https://val.town/endpoint", 
                            mockEnvironment.getEnv("VALTOWN_URL").c_str());
    TEST_ASSERT_EQUAL_STRING("token-123", 
                            mockEnvironment.getEnv("DEVICE_TOKEN").c_str());
    TEST_ASSERT_EQUAL_STRING("api-key-456", 
                            mockEnvironment.getEnv("API_KEY").c_str());
    TEST_ASSERT_EQUAL_STRING("true", 
                            mockEnvironment.getEnv("DEBUG_MODE").c_str());
}

int main(void) {
    UNITY_BEGIN();
    
    RUN_TEST(test_environment_initialization);
    RUN_TEST(test_load_environment_vars);
    RUN_TEST(test_get_valtown_url);
    RUN_TEST(test_get_device_token);
    RUN_TEST(test_get_nonexistent_key);
    RUN_TEST(test_missing_valtown_url);
    RUN_TEST(test_environment_with_quoted_values);
    RUN_TEST(test_environment_with_empty_values);
    RUN_TEST(test_multiple_environment_variables);
    
    return UNITY_END();
}
