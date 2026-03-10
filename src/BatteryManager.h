#ifndef BATTERY_MANAGER_H
#define BATTERY_MANAGER_H

#include <Arduino.h>

#ifdef NATIVE_BUILD
#include <map>
#endif

class BatteryManager {
public:
    enum class BatteryLevel {
        UNKNOWN = -1,
        CRITICAL = 0,
        LOW = 1,
        MEDIUM = 2,
        HIGH = 3,
        FULL = 4
    };

    enum class ChargingState {
        DISCHARGING = 0,
        CHARGING = 1,
        FULLY_CHARGED = 2,
        UNKNOWN = 3
    };

    // Constructor
    BatteryManager(uint8_t voltagePin = 34, uint8_t chargingPin = 35);

    // Initialize the battery monitoring system
    void begin();

    // Update battery status (call periodically in main loop)
    void update();

    // Get current battery level
    BatteryLevel getBatteryLevel() const;

    // Get current voltage in millivolts
    uint32_t getVoltage() const;

    // Get charging state
    ChargingState getChargingState() const;

    // Check if battery is low (below threshold)
    bool isLow() const;

    // Check if battery is critical (below critical threshold)
    bool isCritical() const;

    // Check if device is charging
    bool isCharging() const;

    // Get voltage threshold for low battery warning
    uint32_t getLowThreshold() const;

    // Get voltage threshold for critical battery warning
    uint32_t getCriticalThreshold() const;

    // Set voltage calibration factor (for different battery configurations)
    void setCalibrationFactor(float factor);

    // Get calibration factor
    float getCalibrationFactor() const;

    // Reset battery statistics
    void resetStats();

    // Get minimum voltage recorded since last reset
    uint32_t getMinVoltage() const;

    // Get maximum voltage recorded since last reset
    uint32_t getMaxVoltage() const;

    // Get average voltage over last 10 samples
    uint32_t getAverageVoltage() const;

#ifdef NATIVE_BUILD
    // Mock voltage for testing (set before calling update)
    void setMockVoltage(uint32_t voltage);
    void setMockCharging(bool charging);
    void setMockChargingState(ChargingState state);
    
    // Get mock voltage
    uint32_t getMockVoltage() const;
    
    // Get mock charging state
    bool getMockCharging() const;
#endif

private:
    uint8_t _voltagePin;
    uint8_t _chargingPin;
    
    uint32_t _voltage;
    BatteryLevel _batteryLevel;
    ChargingState _chargingState;
    bool _isCharging;
    
    float _calibrationFactor;
    
    // Statistics tracking
    uint32_t _minVoltage;
    uint32_t _maxVoltage;
    uint32_t _voltageSum;
    uint8_t _voltageSamples;
    
    // Voltage thresholds (in millivolts)
    static constexpr uint32_t _criticalThreshold = 3200;
    static constexpr uint32_t _lowThreshold = 3500;
    static constexpr uint32_t _mediumThreshold = 3800;
    static constexpr uint32_t _highThreshold = 4000;
    static constexpr uint32_t _fullThreshold = 4200;
    
    // Helper methods
    uint32_t readVoltage();
    uint32_t adcToMillivolts(uint16_t adcValue);
    BatteryLevel calculateBatteryLevel(uint32_t voltage);
    ChargingState calculateChargingState();
    void updateStatistics();
    
#ifdef NATIVE_BUILD
    // Mock values for testing
    uint32_t _mockVoltage;
    bool _mockCharging;
    ChargingState _mockChargingState;
    bool _useMockValues;
#endif
};

#endif // BATTERY_MANAGER_H
