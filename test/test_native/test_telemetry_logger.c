#include <unity.h>
#include "TelemetryLogger.h"
#include <vector>

// Mock millis for testing
static unsigned long mock_millis = 0;
unsigned long millisMock() {
    return mock_millis;
}

void setMillisMock(unsigned long time) {
    mock_millis = time;
}

// Test telemetry logger
TelemetryLogger telemetry(50);

void setUp(void) {
    telemetry.clear();
    setMillisMock(0);
}

void tearDown(void) {}

// Test initialization
void test_telemetry_initialization(void) {
    telemetry.begin();
    
    TEST_ASSERT_EQUAL_UINT(0, telemetry.getEventCount());
    TEST_ASSERT_EQUAL_UINT(0, telemetry.getTotalEvents());
    TEST_ASSERT_EQUAL_UINT(0, telemetry.getUniqueEventTypes());
}

// Test basic event logging
void test_telemetry_log_shake(void) {
    telemetry.logShake();
    
    TEST_ASSERT_EQUAL_UINT(1, telemetry.getEventCount());
    TEST_ASSERT_EQUAL_UINT(1, telemetry.getEventCountByType(TelemetryLogger::EventType::SHAKE_DETECTED));
    
    const TelemetryData* latest = telemetry.getLatestEvent();
    TEST_ASSERT_NOT_NULL(latest);
    TEST_ASSERT_EQUAL_STRING("SHAKE_DETECTED", latest->event_type.c_str());
    TEST_ASSERT_TRUE(latest->success);
}

// Test recording logging
void test_telemetry_log_recording_start(void) {
    telemetry.logRecordingStart();
    
    TEST_ASSERT_EQUAL_UINT(1, telemetry.getEventCount());
    const TelemetryData* latest = telemetry.getLatestEvent();
    TEST_ASSERT_EQUAL_STRING("RECORDING_STARTED", latest->event_type.c_str());
}

void test_telemetry_log_recording_complete_success(void) {
    telemetry.logRecordingComplete(true, 5000);
    
    TEST_ASSERT_EQUAL_UINT(1, telemetry.getEventCount());
    const TelemetryData* latest = telemetry.getLatestEvent();
    TEST_ASSERT_EQUAL_STRING("RECORDING_COMPLETED", latest->event_type.c_str());
    TEST_ASSERT_EQUAL_INT(5000, latest->duration_ms);
    TEST_ASSERT_TRUE(latest->success);
    TEST_ASSERT_TRUE(latest->details.find("5000ms") != std::string::npos);
}

void test_telemetry_log_recording_complete_failure(void) {
    telemetry.logRecordingComplete(false, 3000);
    
    const TelemetryData* latest = telemetry.getLatestEvent();
    TEST_ASSERT_FALSE(latest->success);
    TEST_ASSERT_EQUAL_INT(3000, latest->duration_ms);
}

// Test response logging
void test_telemetry_log_response(void) {
    telemetry.logResponseShown("It is certain", 7000);
    
    TEST_ASSERT_EQUAL_UINT(1, telemetry.getEventCount());
    const TelemetryData* latest = telemetry.getLatestEvent();
    TEST_ASSERT_EQUAL_STRING("RESPONSE_SHOWN", latest->event_type.c_str());
    TEST_ASSERT_EQUAL_INT(7000, latest->duration_ms);
}

void test_telemetry_log_response_truncation(void) {
    std::string long_response = "This is a very long response that should be truncated for logging purposes";
    telemetry.logResponseShown(long_response, 1000);
    
    const TelemetryData* latest = telemetry.getLatestEvent();
    TEST_ASSERT_TRUE(latest->details.length() <= 23); // 20 chars + "..."
    TEST_ASSERT_TRUE(latest->details.find("...") != std::string::npos);
}

// Test API request logging
void test_telemetry_log_api_request_success(void) {
    telemetry.logApiRequest(true, 1500);
    
    const TelemetryData* latest = telemetry.getLatestEvent();
    TEST_ASSERT_EQUAL_STRING("API_REQUEST", latest->event_type.c_str());
    TEST_ASSERT_TRUE(latest->success);
    TEST_ASSERT_EQUAL_INT(1500, latest->duration_ms);
}

void test_telemetry_log_api_request_failure(void) {
    telemetry.logApiRequest(false, 0);
    
    const TelemetryData* latest = telemetry.getLatestEvent();
    TEST_ASSERT_FALSE(latest->success);
    TEST_ASSERT_EQUAL_STRING("API_REQUEST", latest->event_type.c_str());
}

// Test error logging
void test_telemetry_log_error(void) {
    telemetry.logError("WiFi connection failed");
    
    TEST_ASSERT_EQUAL_UINT(1, telemetry.getEventCount());
    const TelemetryData* latest = telemetry.getLatestEvent();
    TEST_ASSERT_EQUAL_STRING("ERROR", latest->event_type.c_str());
    TEST_ASSERT_FALSE(latest->success);
    TEST_ASSERT_TRUE(latest->details.find("WiFi") != std::string::npos);
}

// Test startup logging
void test_telemetry_log_startup(void) {
    telemetry.logStartup();
    
    TEST_ASSERT_EQUAL_UINT(1, telemetry.getEventCount());
    const TelemetryData* latest = telemetry.getLatestEvent();
    TEST_ASSERT_EQUAL_STRING("SYSTEM_STARTUP", latest->event_type.c_str());
    TEST_ASSERT_TRUE(latest->success);
}

// Test event categorization
void test_telemetry_event_categories(void) {
    telemetry.logShake();  // USER_ACTION
    telemetry.logRecordingStart();  // AUDIO
    telemetry.logApiRequest(true, 1000);  // NETWORK
    telemetry.logError("Test error");  // ERROR_EVENT
    
    TEST_ASSERT_EQUAL_UINT(1, telemetry.getEventCountByCategory(
        TelemetryLogger::Category::USER_ACTION));
    TEST_ASSERT_EQUAL_UINT(1, telemetry.getEventCountByCategory(
        TelemetryLogger::Category::AUDIO));
    TEST_ASSERT_EQUAL_UINT(1, telemetry.getEventCountByCategory(
        TelemetryLogger::Category::NETWORK));
    TEST_ASSERT_EQUAL_UINT(1, telemetry.getEventCountByCategory(
        TelemetryLogger::Category::ERROR_EVENT));
}

// Test statistics
void test_telemetry_statistics_success_rate(void) {
    telemetry.logApiRequest(true, 1000);
    telemetry.logApiRequest(true, 1500);
    telemetry.logApiRequest(false, 0);
    telemetry.logApiRequest(true, 2000);
    
    float success_rate = telemetry.getSuccessRate();
    TEST_ASSERT_EQUAL_FLOAT(75.0f, success_rate);
}

void test_telemetry_statistics_empty(void) {
    TEST_ASSERT_EQUAL_FLOAT(0.0f, telemetry.getSuccessRate());
    TEST_ASSERT_EQUAL_UINT(0, telemetry.getAverageResponseTime());
}

void test_telemetry_average_response_time(void) {
    telemetry.logResponseShown("Response 1", 1000);
    telemetry.logResponseShown("Response 2", 2000);
    telemetry.logResponseShown("Response 3", 3000);
    
    unsigned long avg = telemetry.getAverageResponseTime();
    TEST_ASSERT_EQUAL_UINT(2000, avg);
}

// Test event retrieval
void test_telemetry_get_latest_event(void) {
    telemetry.logShake();
    telemetry.logRecordingStart();
    telemetry.logRecordingComplete(true, 5000);
    
    const TelemetryData* latest = telemetry.getLatestEvent();
    TEST_ASSERT_NOT_NULL(latest);
    TEST_ASSERT_EQUAL_STRING("RECORDING_COMPLETED", latest->event_type.c_str());
    TEST_ASSERT_EQUAL_INT(5000, latest->duration_ms);
}

void test_telemetry_get_event_by_index(void) {
    telemetry.logShake();
    telemetry.logRecordingStart();
    telemetry.logRecordingComplete(true, 5000);
    
    const TelemetryData* event0 = telemetry.getEventByIndex(0);
    const TelemetryData* event1 = telemetry.getEventByIndex(1);
    const TelemetryData* event2 = telemetry.getEventByIndex(2);
    
    TEST_ASSERT_NOT_NULL(event0);
    TEST_ASSERT_NOT_NULL(event1);
    TEST_ASSERT_NOT_NULL(event2);
    TEST_ASSERT_EQUAL_STRING("SHAKE_DETECTED", event0->event_type.c_str());
    TEST_ASSERT_EQUAL_STRING("RECORDING_STARTED", event1->event_type.c_str());
    TEST_ASSERT_EQUAL_STRING("RECORDING_COMPLETED", event2->event_type.c_str());
}

void test_telemetry_get_invalid_index(void) {
    telemetry.logShake();
    
    const TelemetryData* invalid = telemetry.getEventByIndex(100);
    TEST_ASSERT_NULL(invalid);
}

void test_telemetry_get_events_vector(void) {
    telemetry.logShake();
    telemetry.logRecordingStart();
    
    const std::vector<TelemetryData>& events = telemetry.getEvents();
    TEST_ASSERT_EQUAL_UINT(2, events.size());
}

// Test summary generation
void test_telemetry_summary(void) {
    telemetry.logShake();
    telemetry.logRecordingStart();
    telemetry.logRecordingComplete(true, 5000);
    
    std::string summary = telemetry.getSummary();
    TEST_ASSERT_TRUE(summary.find("Total Events") != std::string::npos);
    TEST_ASSERT_TRUE(summary.find("Unique Event Types") != std::string::npos);
    TEST_ASSERT_TRUE(summary.find("SHAKE_DETECTED") != std::string::npos);
    TEST_ASSERT_TRUE(summary.find("RECORDING_COMPLETED") != std::string::npos);
}

void test_telemetry_json_summary(void) {
    telemetry.logShake();
    telemetry.logRecordingStart();
    telemetry.logRecordingComplete(true, 5000);
    
    std::string json = telemetry.getJSONSummary();
    TEST_ASSERT_TRUE(json.find("{") != std::string::npos);
    TEST_ASSERT_TRUE(json.find("total_events") != std::string::npos);
    TEST_ASSERT_TRUE(json.find("categories") != std::string::npos);
}

// Test event limit trimming
void test_telemetry_event_limit_trimming(void) {
    TelemetryLogger limited_telemetry(3);
    
    limited_telemetry.logShake();
    limited_telemetry.logRecordingStart();
    limited_telemetry.logRecordingComplete(true, 5000);
    
    TEST_ASSERT_EQUAL_UINT(3, limited_telemetry.getEventCount());
    
    // Add one more event - should trim oldest
    limited_telemetry.logResponseShown("Response", 1000);
    
    TEST_ASSERT_EQUAL_UINT(3, limited_telemetry.getEventCount());
    
    // Oldest event (SHAKE_DETECTED) should be removed
    const TelemetryData* earliest = limited_telemetry.getEventByIndex(0);
    TEST_ASSERT_NOT_EQUAL_STRING("SHAKE_DETECTED", earliest->event_type.c_str());
}

// Test timestamp tracking
void test_telemetry_timestamps(void) {
    setMillisMock(1000);
    telemetry.logShake();
    
    setMillisMock(2000);
    telemetry.logRecordingStart();
    
    const TelemetryData* event0 = telemetry.getLatestEvent();
    TEST_ASSERT_EQUAL_UINT(2000, event0->timestamp);
}

// Test clear functionality
void test_telemetry_clear(void) {
    telemetry.logShake();
    telemetry.logRecordingStart();
    
    TEST_ASSERT_EQUAL_UINT(2, telemetry.getEventCount());
    
    telemetry.clear();
    
    TEST_ASSERT_EQUAL_UINT(0, telemetry.getEventCount());
    TEST_ASSERT_EQUAL_UINT(0, telemetry.getUniqueEventTypes());
}

// Test multiple event types
void test_telemetry_multiple_event_types(void) {
    telemetry.logShake();
    telemetry.logRecordingStart();
    telemetry.logRecordingComplete(true, 5000);
    telemetry.logResponseShown("It is certain", 7000);
    telemetry.logApiRequest(true, 1500);
    
    TEST_ASSERT_EQUAL_UINT(5, telemetry.getEventCount());
    TEST_ASSERT_EQUAL_UINT(5, telemetry.getUniqueEventTypes());
}

int main(void) {
    UNITY_BEGIN();
    
    RUN_TEST(test_telemetry_initialization);
    RUN_TEST(test_telemetry_log_shake);
    RUN_TEST(test_telemetry_log_recording_start);
    RUN_TEST(test_telemetry_log_recording_complete_success);
    RUN_TEST(test_telemetry_log_recording_complete_failure);
    RUN_TEST(test_telemetry_log_response);
    RUN_TEST(test_telemetry_log_response_truncation);
    RUN_TEST(test_telemetry_log_api_request_success);
    RUN_TEST(test_telemetry_log_api_request_failure);
    RUN_TEST(test_telemetry_log_error);
    RUN_TEST(test_telemetry_log_startup);
    RUN_TEST(test_telemetry_event_categories);
    RUN_TEST(test_telemetry_statistics_success_rate);
    RUN_TEST(test_telemetry_statistics_empty);
    RUN_TEST(test_telemetry_average_response_time);
    RUN_TEST(test_telemetry_get_latest_event);
    RUN_TEST(test_telemetry_get_event_by_index);
    RUN_TEST(test_telemetry_get_invalid_index);
    RUN_TEST(test_telemetry_get_events_vector);
    RUN_TEST(test_telemetry_summary);
    RUN_TEST(test_telemetry_json_summary);
    RUN_TEST(test_telemetry_event_limit_trimming);
    RUN_TEST(test_telemetry_timestamps);
    RUN_TEST(test_telemetry_clear);
    RUN_TEST(test_telemetry_multiple_event_types);
    
    return UNITY_END();
}
