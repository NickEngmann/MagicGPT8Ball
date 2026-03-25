#ifndef TELEMETRY_LOGGER_H
#define TELEMETRY_LOGGER_H

#include <Arduino.h>
#include <vector>
#include <map>
#include <string>

#ifdef NATIVE_BUILD
#include <ctime>
#else
#include "HardwareSerial.h"
#endif

// Telemetry data structure for storing usage metrics
struct TelemetryData {
    unsigned long timestamp;
    std::string event_type;
    std::string category;
    std::string details;
    int duration_ms;
    bool success;
    
    TelemetryData() : timestamp(0), event_type(""), category(""), 
                      details(""), duration_ms(0), success(false) {}
};

// TelemetryLogger - Tracks and logs system usage statistics
class TelemetryLogger {
public:
    enum class EventType {
        SHAKE_DETECTED,      // User shook the ball
        RECORDING_STARTED,   // Audio recording began
        RECORDING_COMPLETED, // Audio recording finished
        RESPONSE_SHOWN,      // Magic 8 ball response displayed
        WIFI_ERROR,          // WiFi connection error
        API_REQUEST,         // API call made
        API_RESPONSE,        // API response received
        SYSTEM_STARTUP,      // System startup
        SYSTEM_SHUTDOWN,     // System shutdown
        ERROR,               // Generic error
        CUSTOM               // Custom event type
    };

    enum class Category {
        USER_ACTION,         // Direct user interaction
        SYSTEM,              // System-level events
        NETWORK,             // Network/WiFi events
        AUDIO,               // Audio/recording events
        DISPLAY,             // Display-related events
        ERROR_EVENT          // Error conditions
    };

    TelemetryLogger(uint8_t max_events = 100);
    ~TelemetryLogger();
    
    // Initialization
    void begin();
    void clear();
    
    // Event logging
    void logEvent(EventType type, const std::string& details = "", 
                  int duration_ms = 0, bool success = true);
    
    void logEvent(Category category, EventType type, 
                  const std::string& details = "", int duration_ms = 0, 
                  bool success = true);
    
    // Convenience methods for common events
    void logShake();
    void logRecordingStart();
    void logRecordingComplete(bool success, int duration_ms);
    void logResponseShown(const std::string& response, int duration_ms);
    void logApiRequest(bool success, int duration_ms);
    void logWifiError();
    void logStartup();
    void logError(const std::string& error_message);
    
    // Query methods
    size_t getEventCount() const;
    size_t getEventCountByType(EventType type) const;
    size_t getEventCountByCategory(Category category) const;
    
    std::string getSummary() const;
    std::string getJSONSummary() const;
    
    // Event retrieval
    const std::vector<TelemetryData>& getEvents() const;
    const TelemetryData* getLatestEvent() const;
    const TelemetryData* getEventByIndex(size_t index) const;
    
    // Statistics
    unsigned long getTotalEvents() const;
    unsigned long getUniqueEventTypes() const;
    unsigned long getAverageResponseTime() const;
    float getSuccessRate() const;
    
    // Export methods
    void exportToSerial();
    std::string exportToString();
    
private:
    std::vector<TelemetryData> events;
    size_t max_events;
    std::map<std::string, unsigned long> event_counts;
    std::map<std::string, unsigned long> category_counts;
    
    // Helpers
    std::string eventTypeToString(EventType type) const;
    std::string categoryToString(Category category) const;
    std::string timestampToString(unsigned long timestamp) const;
    size_t getEarliestIndex() const;
    void updateStatistics();
    void trimOldEvents();
};

#endif // TELEMETRY_LOGGER_H
