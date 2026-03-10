#ifndef BATTERY_MANAGER_H
#define BATTERY_MANAGER_H

#ifndef NATIVE_BUILD
#include <Arduino.h>
#endif

#ifdef NATIVE_BUILD
#include <map>
#include <functional>
#include <ctime>

// Mock millis() for native builds
unsigned long millis() {
    static unsigned long start = std::time(nullptr) * 1000;
    return std::time(nullptr) * 1000 - start;
}
#endif

class BatteryManager {
public:
    // Battery states
    enum class State {
        DISCHARGING,
        CHARGING,
        FULL,
        LOW,
        CRITICAL
    };

    // Battery levels (0-100%)
    enum class Level {
        CRITICAL = 0,
        LOW = 20,
        MEDIUM = 50,
        HIGH = 80,
        FULL = 100
    };

    // Callback type for battery level changes
#ifdef NATIVE_BUILD
    using BatteryLevelCallback = std::function<void(int level, State state)>;
#else
    using BatteryLevelCallback = void (*)(int, State);
#endif

    // Constructor
    BatteryManager();

    // Initialize battery monitoring
    // On native builds, use simulated values
    // On hardware, reads from ADC pin
    void begin(uint8_t adcPin = 36);

    // Get current battery level (0-100)
    int getBatteryLevel();

    // Get current battery state
    State getState();

    // Check if battery is low (below threshold)
    bool isLowBattery();

    // Check if battery is critical (below 10%)
    bool isCriticalBattery();

    // Register callback for battery level changes
    void registerCallback(BatteryLevelCallback callback);

    // Update battery state (call periodically)
    void update();

#ifdef NATIVE_BUILD
    // Public method for testing
    void setSimulatedVoltage(int voltage_mV) { simulatedVoltage = voltage_mV; useSimulatedValues = true; }
#endif

    // Get battery voltage (mV)
    // On native builds, returns simulated value
    // On hardware, calculates from ADC reading
    int getVoltage();

    // Get estimated time until critical (minutes)
    // Returns -1 if charging or full
    int getEstimatedTimeUntilCritical();

    // Reset low battery warning
    void resetLowBatteryWarning();

    // Get time since last low battery warning (milliseconds)
    unsigned long getLowBatteryWarningTime();

private:
    // ADC calibration constants
    static constexpr float VOLTAGE_DIVIDER_RATIO = 2.0f;
    static constexpr float ADC_MAX = 4095.0f;
    static constexpr float VREF = 3.3f;
    static constexpr float BATTERY_FULL_VOLTAGE = 4200.0f;
    static constexpr float BATTERY_EMPTY_VOLTAGE = 3000.0f;

    // Internal state
    int batteryLevel;
    State currentState;
    uint8_t adcPin;
    bool initialized;
    bool lowBatteryWarningActive;
    unsigned long lastLowBatteryWarningTime;

#ifdef NATIVE_BUILD
    // Simulated values for testing
    std::map<int, int> simulatedVoltageMap;
    bool useSimulatedValues;
    int simulatedVoltage;
#else
    // Hardware-specific: ADC calibration
    esp_adc_cal_characteristics_t adcChars;
#endif

    // Helper methods
    void calculateLevelFromVoltage(int voltage);
    void updateState();
    void triggerLowBatteryWarning();
    int voltageToLevel(int voltage);
    int levelToVoltage(int level);

#ifdef NATIVE_BUILD
    void initializeSimulatedValues();
#endif
};

#endif // BATTERY_MANAGER_H
