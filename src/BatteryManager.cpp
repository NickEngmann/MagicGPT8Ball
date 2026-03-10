#include "BatteryManager.h"
#include <cmath>

#ifdef NATIVE_BUILD
#include <algorithm>
#endif

BatteryManager::BatteryManager()
    : batteryLevel(0),
      currentState(State::DISCHARGING),
      adcPin(36),
      initialized(false),
      lowBatteryWarningActive(false),
      lastLowBatteryWarningTime(0)
#ifdef NATIVE_BUILD
      ,
      useSimulatedValues(false),
      simulatedVoltage(3700)
#endif
{
}

void BatteryManager::begin(uint8_t pin) {
    adcPin = pin;

#ifdef NATIVE_BUILD
    // Initialize simulated values for testing
    initializeSimulatedValues();
    useSimulatedValues = true;
    initialized = true;
#else
    // Hardware-specific initialization
    // ESP32 ADC calibration
    esp_adc_cal_characteristics_t adc_chars;
    esp_adc_cal_characterize(
        ADC_UNIT_1,
        ADC_ATTEN_DB_11,
        12,
        1100,
        &adc_chars
    );
    initialized = true;
#endif
}

int BatteryManager::getBatteryLevel() {
    if (!initialized) {
        return 0;
    }

#ifdef NATIVE_BUILD
    // Use simulated voltage for testing
    simulatedVoltage = simulatedVoltageMap.count(batteryLevel) ? 
                       simulatedVoltageMap[batteryLevel] : simulatedVoltage;
    calculateLevelFromVoltage(simulatedVoltage);
#else
    // Read ADC and calculate level
    uint32_t adcReading = analogRead(adcPin);
    float voltage = (adcReading * VREF * VOLTAGE_DIVIDER_RATIO) / ADC_MAX;
    int voltage_mV = static_cast<int>(voltage * 1000);
    calculateLevelFromVoltage(voltage_mV);
#endif

    return batteryLevel;
}

BatteryManager::State BatteryManager::getState() {
    if (!initialized) {
        return State::DISCHARGING;
    }

#ifdef NATIVE_BUILD
    simulatedVoltage = simulatedVoltageMap.count(batteryLevel) ? 
                       simulatedVoltageMap[batteryLevel] : simulatedVoltage;
    calculateLevelFromVoltage(simulatedVoltage);
#else
    uint32_t adcReading = analogRead(adcPin);
    float voltage = (adcReading * VREF * VOLTAGE_DIVIDER_RATIO) / ADC_MAX;
    int voltage_mV = static_cast<int>(voltage * 1000);
    calculateLevelFromVoltage(voltage_mV);
#endif

    return currentState;
}

bool BatteryManager::isLowBattery() {
    if (!initialized) {
        return false;
    }

    int level = getBatteryLevel();
    return level <= static_cast<int>(Level::LOW);
}

bool BatteryManager::isCriticalBattery() {
    if (!initialized) {
        return false;
    }

    int level = getBatteryLevel();
    return level <= static_cast<int>(Level::CRITICAL);
}

void BatteryManager::registerCallback(BatteryLevelCallback callback) {
    // Callback registration is handled by the caller
    // This is a placeholder for future implementation
}

void BatteryManager::update() {
    if (!initialized) {
        return;
    }

    getBatteryLevel();
    updateState();

    // Check for low battery condition
    if (isLowBattery() && !lowBatteryWarningActive) {
        triggerLowBatteryWarning();
    }
}

int BatteryManager::getVoltage() {
    if (!initialized) {
        return 0;
    }

#ifdef NATIVE_BUILD
    simulatedVoltage = simulatedVoltageMap.count(batteryLevel) ? 
                       simulatedVoltageMap[batteryLevel] : simulatedVoltage;
    return simulatedVoltage;
#else
    uint32_t adcReading = analogRead(adcPin);
    float voltage = (adcReading * VREF * VOLTAGE_DIVIDER_RATIO) / ADC_MAX;
    return static_cast<int>(voltage * 1000);
#endif
}

int BatteryManager::getEstimatedTimeUntilCritical() {
    if (!initialized) {
        return -1;
    }

    int level = getBatteryLevel();

    // If charging or full, return -1
    if (level >= static_cast<int>(Level::FULL)) {
        return -1;
    }

#ifdef NATIVE_BUILD
    // Simulate discharge rate: 5% per 30 minutes
    int minutesPerPercent = 6; // 30 minutes / 5%
    int remainingPercent = level;
    return remainingPercent * minutesPerPercent;
#else
    // Real hardware: estimate based on discharge rate
    // This would need calibration based on actual usage
    // For now, use a simple estimate
    int minutesPerPercent = 6; // 5% per 30 minutes
    int remainingPercent = level;
    return remainingPercent * minutesPerPercent;
#endif
}

void BatteryManager::resetLowBatteryWarning() {
    lowBatteryWarningActive = false;
    lastLowBatteryWarningTime = 0;
}

unsigned long BatteryManager::getLowBatteryWarningTime() {
    return lastLowBatteryWarningTime;
}

void BatteryManager::calculateLevelFromVoltage(int voltage) {
    // Clamp voltage to valid range
    voltage = std::max(static_cast<int>(BATTERY_EMPTY_VOLTAGE),
                       std::min(static_cast<int>(BATTERY_FULL_VOLTAGE), voltage));

    // Calculate percentage
    float range = BATTERY_FULL_VOLTAGE - BATTERY_EMPTY_VOLTAGE;
    float normalized = (voltage - BATTERY_EMPTY_VOLTAGE) / range;
    batteryLevel = static_cast<int>(normalized * 100);
}

void BatteryManager::updateState() {
    if (batteryLevel >= static_cast<int>(Level::FULL)) {
        currentState = State::FULL;
    } else if (batteryLevel <= static_cast<int>(Level::CRITICAL)) {
        currentState = State::CRITICAL;
    } else if (batteryLevel <= static_cast<int>(Level::LOW)) {
        currentState = State::LOW;
    } else {
        currentState = State::DISCHARGING;
    }
}

void BatteryManager::triggerLowBatteryWarning() {
    lowBatteryWarningActive = true;
    lastLowBatteryWarningTime = millis();

    // Trigger callback if registered
    // This would be implemented in the main application
}

int BatteryManager::voltageToLevel(int voltage) {
    // Clamp voltage to valid range
    voltage = std::max(static_cast<int>(BATTERY_EMPTY_VOLTAGE),
                       std::min(static_cast<int>(BATTERY_FULL_VOLTAGE), voltage));

    // Calculate percentage
    float range = BATTERY_FULL_VOLTAGE - BATTERY_EMPTY_VOLTAGE;
    float normalized = (voltage - BATTERY_EMPTY_VOLTAGE) / range;
    return static_cast<int>(normalized * 100);
}

int BatteryManager::levelToVoltage(int level) {
    // Clamp level to valid range
    level = std::max(0, std::min(100, level));

    // Calculate voltage
    float range = BATTERY_FULL_VOLTAGE - BATTERY_EMPTY_VOLTAGE;
    float voltage = BATTERY_EMPTY_VOLTAGE + (level / 100.0f) * range;
    return static_cast<int>(voltage);
}

#ifdef NATIVE_BUILD
void BatteryManager::initializeSimulatedValues() {
    // Create a mapping from battery level to voltage for testing
    simulatedVoltageMap.clear();

    // Simulate realistic battery discharge curve
    // Voltage drops faster at low levels
    simulatedVoltageMap[100] = 4200;
    simulatedVoltageMap[90] = 4100;
    simulatedVoltageMap[80] = 4000;
    simulatedVoltageMap[70] = 3900;
    simulatedVoltageMap[60] = 3800;
    simulatedVoltageMap[50] = 3700;
    simulatedVoltageMap[40] = 3600;
    simulatedVoltageMap[30] = 3500;
    simulatedVoltageMap[20] = 3400;
    simulatedVoltageMap[10] = 3300;
    simulatedVoltageMap[5] = 3200;
    simulatedVoltageMap[0] = 3000;
}
#endif
