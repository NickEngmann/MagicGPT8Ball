#include "TelemetryLogger.h"
#include <sstream>

#ifdef NATIVE_BUILD
#include <cmath>
#else
// For Arduino/ESP32 builds
#include <Arduino.h>
#endif

TelemetryLogger::TelemetryLogger(uint8_t max_events) 
    : max_events(max_events) {
}

TelemetryLogger::~TelemetryLogger() {
    // Cleanup
}

void TelemetryLogger::begin() {
    clear();
#ifdef NATIVE_BUILD
    Serial.println("TelemetryLogger initialized with max " + 
                   std::to_string(max_events) + " events");
#endif
}

void TelemetryLogger::clear() {
    events.clear();
    event_counts.clear();
    category_counts.clear();
    updateStatistics();
}

void TelemetryLogger::logEvent(EventType type, const std::string& details,
                               int duration_ms, bool success) {
    logEvent(Category::USER_ACTION, type, details, duration_ms, success);
}

void TelemetryLogger::logEvent(Category category, EventType type,
                               const std::string& details, int duration_ms,
                               bool success) {
    TelemetryData data;
    data.timestamp = millis();
    data.category = categoryToString(category);
    data.event_type = eventTypeToString(type);
    data.details = details;
    data.duration_ms = duration_ms;
    data.success = success;
    
    events.push_back(data);
    updateStatistics();
    trimOldEvents();
}

void TelemetryLogger::logShake() {
    logEvent(Category::USER_ACTION, EventType::SHAKE_DETECTED, 
             "Shake detected", 0, true);
}

void TelemetryLogger::logRecordingStart() {
    logEvent(Category::AUDIO, EventType::RECORDING_STARTED, 
             "Recording started", 0, true);
}

void TelemetryLogger::logRecordingComplete(bool success, int duration_ms) {
    logEvent(Category::AUDIO, EventType::RECORDING_COMPLETED, 
             std::to_string(duration_ms) + "ms", duration_ms, success);
}

void TelemetryLogger::logResponseShown(const std::string& response, 
                                       int duration_ms) {
    logEvent(Category::DISPLAY, EventType::RESPONSE_SHOWN, 
             response.length() > 20 ? response.substr(0, 20) + "..." : response,
             duration_ms, true);
}

void TelemetryLogger::logApiRequest(bool success, int duration_ms) {
    logEvent(Category::NETWORK, EventType::API_REQUEST, 
             success ? "API call successful" : "API call failed", 
             duration_ms, success);
}

void TelemetryLogger::logWifiError() {
    logEvent(Category::NETWORK, EventType::WIFI_ERROR, 
             "WiFi connection error", 0, false);
}

void TelemetryLogger::logStartup() {
    logEvent(Category::SYSTEM, EventType::SYSTEM_STARTUP, 
             "System startup", 0, true);
}

void TelemetryLogger::logError(const std::string& error_message) {
    logEvent(Category::ERROR_EVENT, EventType::ERROR, 
             error_message, 0, false);
}

size_t TelemetryLogger::getEventCount() const {
    return events.size();
}

size_t TelemetryLogger::getEventCountByType(EventType type) const {
    std::string type_str = eventTypeToString(type);
    auto it = event_counts.find(type_str);
    return (it != event_counts.end()) ? it->second : 0;
}

size_t TelemetryLogger::getEventCountByCategory(Category category) const {
    std::string cat_str = categoryToString(category);
    auto it = category_counts.find(cat_str);
    return (it != it_end()) ? it->second : 0;
}

std::string TelemetryLogger::getSummary() const {
    std::ostringstream oss;
    
    oss << "=== Telemetry Summary ===\n"
        << "Total Events: " << events.size() << "\n"
        << "Unique Event Types: " << event_counts.size() << "\n"
        << "Event Categories:\n";
    
    for (const auto& pair : category_counts) {
        oss << "  - " << pair.first << ": " << pair.second << "\n";
    }
    
    oss << "\nEvent Types:\n";
    for (const auto& pair : event_counts) {
        oss << "  - " << pair.first << ": " << pair.second << "\n";
    }
    
    oss << "\n=== End Summary ===\n";
    
    return oss.str();
}

std::string TelemetryLogger::getJSONSummary() const {
    std::ostringstream oss;
    oss << "{\n";
    oss << "  \"total_events\": " << events.size() << ",\n";
    oss << "  \"unique_event_types\": " << event_counts.size() << ",\n";
    oss << "  \"categories\": {\n";
    
    bool first = true;
    for (const auto& pair : category_counts) {
        if (!first) oss << ",\n";
        oss << "    \"" << pair.first << "\": " << pair.second;
        first = false;
    }
    oss << "\n  },\n";
    
    oss << "  \"event_types\": {\n";
    first = true;
    for (const auto& pair : event_counts) {
        if (!first) oss << ",\n";
        oss << "    \"" << pair.first << "\": " << pair.second;
        first = false;
    }
    oss << "\n  }\n";
    
    oss << "}\n";
    
    return oss.str();
}

const std::vector<TelemetryData>& TelemetryLogger::getEvents() const {
    return events;
}

const TelemetryData* TelemetryLogger::getLatestEvent() const {
    if (events.empty()) {
        return nullptr;
    }
    return &events.back();
}

const TelemetryData* TelemetryLogger::getEventByIndex(size_t index) const {
    if (index >= events.size()) {
        return nullptr;
    }
    return &events[index];
}

unsigned long TelemetryLogger::getTotalEvents() const {
    return events.size();
}

unsigned long TelemetryLogger::getUniqueEventTypes() const {
    return event_counts.size();
}

unsigned long TelemetryLogger::getAverageResponseTime() const {
    unsigned long total_time = 0;
    int response_count = 0;
    
    for (const auto& event : events) {
        if (event.event_type == "RESPONSE_SHOWN" || 
            event.event_type == "API_REQUEST" ||
            event.event_type == "RECORDING_COMPLETED") {
            total_time += event.duration_ms;
            response_count++;
        }
    }
    
    return (response_count > 0) ? (total_time / response_count) : 0;
}

float TelemetryLogger::getSuccessRate() const {
    if (events.empty()) {
        return 0.0f;
    }
    
    int success_count = 0;
    for (const auto& event : events) {
        if (event.success) {
            success_count++;
        }
    }
    
    return static_cast<float>(success_count) / static_cast<float>(events.size()) * 100.0f;
}

void TelemetryLogger::exportToSerial() {
#ifdef NATIVE_BUILD
    Serial.println(getSummary());
#else
    // For ESP32 build, use the Serial port
    Serial.println(getSummary());
#endif
}

std::string TelemetryLogger::exportToString() {
    return getSummary();
}

std::string TelemetryLogger::eventTypeToString(EventType type) const {
    switch (type) {
        case EventType::SHAKE_DETECTED: return "SHAKE_DETECTED";
        case EventType::RECORDING_STARTED: return "RECORDING_STARTED";
        case EventType::RECORDING_COMPLETED: return "RECORDING_COMPLETED";
        case EventType::RESPONSE_SHOWN: return "RESPONSE_SHOWN";
        case EventType::WIFI_ERROR: return "WIFI_ERROR";
        case EventType::API_REQUEST: return "API_REQUEST";
        case EventType::API_RESPONSE: return "API_RESPONSE";
        case EventType::SYSTEM_STARTUP: return "SYSTEM_STARTUP";
        case EventType::SYSTEM_SHUTDOWN: return "SYSTEM_SHUTDOWN";
        case EventType::ERROR: return "ERROR";
        case EventType::CUSTOM: return "CUSTOM";
        default: return "UNKNOWN";
    }
}

std::string TelemetryLogger::categoryToString(Category category) const {
    switch (category) {
        case Category::USER_ACTION: return "USER_ACTION";
        case Category::SYSTEM: return "SYSTEM";
        case Category::NETWORK: return "NETWORK";
        case Category::AUDIO: return "AUDIO";
        case Category::DISPLAY: return "DISPLAY";
        case Category::ERROR_EVENT: return "ERROR_EVENT";
        default: return "UNKNOWN";
    }
}

std::string TelemetryLogger::timestampToString(unsigned long timestamp) const {
    std::ostringstream oss;
    oss << timestamp << "ms";
    return oss.str();
}

size_t TelemetryLogger::getEarliestIndex() const {
    return 0;
}

void TelemetryLogger::updateStatistics() {
    // Clear existing statistics
    event_counts.clear();
    category_counts.clear();
    
    // Count events by type and category
    for (const auto& event : events) {
        event_counts[event.event_type]++;
        category_counts[event.category]++;
    }
}

void TelemetryLogger::trimOldEvents() {
    while (events.size() > max_events) {
        events.erase(events.begin());
    }
    updateStatistics();
}
