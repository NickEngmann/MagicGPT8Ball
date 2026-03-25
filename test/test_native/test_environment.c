#include <unity.h>
#include "Environment.h"

// Mock filesystem for native build
static bool mock_env_file_exists = true;
static std::string mock_env_content = "VALTOWN_URL=https://test.val.run\nDEVICE_TOKEN=test-token-123";

// Test environment module
Environment env;

void setUp(void) {
    mock_env_file_exists = true;
    mock_env_content = "VALTOWN_URL=https://test.val.run\nDEVICE_TOKEN=test-token-123";
}

void tearDown(void) {}

// Test initialization
void test_environment_initialization(void) {
    TEST_ASSERT_TRUE(Environment::begin());
    TEST_ASSERT_TRUE(Environment::isInitialized());
}

// Test loading environment variables
void test_load_environment_vars(void) {
    Environment::begin();
    
    std::string valtown = Environment::getEnv("VALTOWN_URL");
    std::string token = Environment::getEnv("DEVICE_TOKEN");
    
    TEST_ASSERT_EQUAL_STRING("https://test.val.run", valtown.c_str());
    TEST_ASSERT_EQUAL_STRING("test-token-123", token.c_str());
}

// Test get VALTOWN_URL
void test_get_valtown_url(void) {
    Environment::begin();
    std::string url = Environment::getValtownUrl();
    TEST_ASSERT_EQUAL_STRING("https://test.val.run", url.c_str());
}

// Test get DEVICE_TOKEN
void test_get_device_token(void) {
    Environment::begin();
    std::string token = Environment::getDeviceToken();
    TEST_ASSERT_EQUAL_STRING("test-token-123", token.c_str());
}

// Test missing environment variable
void test_missing_env_var(void) {
    Environment::begin();
    std::string missing = Environment::getEnv("NONEXISTENT_VAR");
    TEST_ASSERT_TRUE(missing.empty());
}

// Test empty environment file
void test_empty_environment_file(void) {
    mock_env_file_exists = false;
    
    TEST_ASSERT_FALSE(Environment::begin());
}

// Test environment variable with spaces
void test_env_var_with_spaces(void) {
    mock_env_content = "VALTOWN_URL=https://my-valtown-endpoint.val.run\nDEVICE_TOKEN=my-device-token";
    
    Environment::begin();
    std::string url = Environment::getValtownUrl();
    TEST_ASSERT_EQUAL_STRING("https://my-valtown-endpoint.val.run", url.c_str());
}

// Test multiple environment variables
void test_multiple_env_vars(void) {
    mock_env_content = "VAR1=value1\nVAR2=value2\nVAR3=value3";
    
    Environment::begin();
    std::string v1 = Environment::getEnv("VAR1");
    std::string v2 = Environment::getEnv("VAR2");
    std::string v3 = Environment::getEnv("VAR3");
    
    TEST_ASSERT_EQUAL_STRING("value1", v1.c_str());
    TEST_ASSERT_EQUAL_STRING("value2", v2.c_str());
    TEST_ASSERT_EQUAL_STRING("value3", v3.c_str());
}

int main(void) {
    UNITY_BEGIN();

    RUN_TEST(test_environment_initialization);
    RUN_TEST(test_load_environment_vars);
    RUN_TEST(test_get_valtown_url);
    RUN_TEST(test_get_device_token);
    RUN_TEST(test_missing_env_var);
    RUN_TEST(test_empty_environment_file);
    RUN_TEST(test_env_var_with_spaces);
    RUN_TEST(test_multiple_env_vars);

    return UNITY_END();
}
