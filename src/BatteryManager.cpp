#include "BatteryManager.h"

#ifdef NATIVE_BUILD
#include <cmath>
#else
#include <driver/adc.h>
#include <esp_adc_cal.h>
#include <esp_system.h>
#endif

BatteryManager::BatteryManager(uint8_t voltagePin, uint8_t chargingPin)
    : _voltagePin(voltagePin),
      _chargingPin(chargingPin),
      _voltage(0),
      _batteryLevel(BatteryLevel::UNKNOWN),
      _chargingState(ChargingState::UNKNOWN),
      _isCharging(false),
      _calibrationFactor(1.0f),
      _minVoltage(UINT32_MAX),
      _maxVoltage(0),
      _voltageSum(0),
      _voltageSamples(0)
#ifdef NATIVE_BUILD
      , _mockVoltage(0),
      _mockCharging(false),
      _mockChargingState(ChargingState::UNKNOWN),
      _useMockValues(false)
#endif
{}

void BatteryManager::begin() {
#ifdef NATIVE_BUILD
    // In native build, initialize mock values
    _useMockValues = false;
    _mockVoltage = 0;
    _mockCharging = false;
    _mockChargingState = ChargingState::UNKNOWN;
#else
    // Configure ADC for voltage reading
    adc1_config_width(ADC_WIDTH_BIT_12);
    adc1_config_channel_atten(_voltagePin, ADC_ATTEN_DB_11);
    
    // Configure charging pin as input
    pinMode(_chargingPin, INPUT);
#endif
    
    // Reset statistics
    resetStats();
}

void BatteryManager::update() {
#ifdef NATIVE_BUILD
    // Use mock values if enabled for testing
    if (_useMockValues) {
        _voltage = _mockVoltage;
        _isCharging = _mockCharging;
        _chargingState = _mockChargingState;
    } else {
        // Simulate voltage reading for testing
        _voltage = 3800 + (rand() % 500); // Random voltage between 3800-4300mV
        _isCharging = false;
        _chargingState = calculateChargingState();
    }
#else
    // Read actual voltage from ADC
    _voltage = readVoltage();
    _isCharging = digitalRead(_chargingPin) == HIGH;
    _chargingState = calculateChargingState();
#endif
    
    // Calculate battery level
    _batteryLevel = calculateBatteryLevel(_voltage);
    
    // Update statistics
    updateStatistics();
}

BatteryManager::BatteryLevel BatteryManager::getBatteryLevel() const {
    return _batteryLevel;
}

uint32_t BatteryManager::getVoltage() const {
    return _voltage;
}

BatteryManager::ChargingState BatteryManager::getChargingState() const {
    return _chargingState;
}

bool BatteryManager::isLow() const {
    return _voltage < _lowThreshold;
}

bool BatteryManager::isCritical() const {
    return _voltage < _criticalThreshold;
}

bool BatteryManager::isCharging() const {
    return _isCharging;
}

uint32_t BatteryManager::getLowThreshold() const {
    return _lowThreshold;
}

uint32_t BatteryManager::getCriticalThreshold() const {
    return _criticalThreshold;
}

void BatteryManager::setCalibrationFactor(float factor) {
    if (factor > 0.0f && factor <= 2.0f) {
        _calibrationFactor = factor;
    }
}

float BatteryManager::getCalibrationFactor() const {
    return _calibrationFactor;
}

void BatteryManager::resetStats() {
    _minVoltage = UINT32_MAX;
    _maxVoltage = 0;
    _voltageSum = 0;
    _voltageSamples = 0;
}

uint32_t BatteryManager::getMinVoltage() const {
    return (_minVoltage == UINT32_MAX) ? 0 : _minVoltage;
}

uint32_t BatteryManager::getMaxVoltage() const {
    return _maxVoltage;
}

uint32_t BatteryManager::getAverageVoltage() const {
    return (_voltageSamples > 0) ? (_voltageSum / _voltageSamples) : 0;
}

#ifdef NATIVE_BUILD
void BatteryManager::setMockVoltage(uint32_t voltage) {
    _mockVoltage = voltage;
    _useMockValues = true;
}

void BatteryManager::setMockCharging(bool charging) {
    _mockCharging = charging;
    _useMockValues = true;
}

void BatteryManager::setMockChargingState(ChargingState state) {
    _mockChargingState = state;
    _useMockValues = true;
}

uint32_t BatteryManager::getMockVoltage() const {
    return _mockVoltage;
}

bool BatteryManager::getMockCharging() const {
    return _mockCharging;
}
#endif

uint32_t BatteryManager::readVoltage() {
#ifdef NATIVE_BUILD
    return _mockVoltage;
#else
    // Read ADC value
    uint16_t adcValue = adc1_get_raw(_voltagePin);
    return adcToMillivolts(adcValue);
#endif
}

uint32_t BatteryManager::adcToMillivolts(uint16_t adcValue) {
    // ESP32-S3 ADC: 12-bit, 3.3V reference
    // Voltage = (adcValue / 4095.0) * 3300 * calibrationFactor
    float voltage = (static_cast<float>(adcValue) / 4095.0f) * 3300.0f * _calibrationFactor;
    return static_cast<uint32_t>(voltage);
}

BatteryManager::BatteryLevel BatteryManager::calculateBatteryLevel(uint32_t voltage) {
    if (voltage >= _fullThreshold) {
        return BatteryLevel::FULL;
    } else if (voltage >= _highThreshold) {
        return BatteryLevel::HIGH;
    } else if (voltage >= _mediumThreshold) {
        return BatteryLevel::MEDIUM;
    } else if (voltage >= _lowThreshold) {
        return BatteryLevel::LOW;
    } else if (voltage >= _criticalThreshold) {
        return BatteryLevel::CRITICAL;
    }
    return BatteryLevel::CRITICAL;
}

BatteryManager::ChargingState BatteryManager::calculateChargingState() {
#ifdef NATIVE_BUILD
    return _mockChargingState;
#else
    if (_isCharging) {
        if (_voltage >= _fullThreshold) {
            return ChargingState::FULLY_CHARGED;
        }
        return ChargingState::CHARGING;
    }
    return ChargingState::DISCHARGING;
#endif
}

void BatteryManager::updateStatistics() {
    if (_voltage < _minVoltage) {
        _minVoltage = _voltage;
    }
    if (_voltage > _maxVoltage) {
        _maxVoltage = _voltage;
    }
    
    _voltageSum += _voltage;
    _voltageSamples++;
    
    // Keep running average limited to last 10 samples
    if (_voltageSamples > 10) {
        _voltageSum -= (_voltageSum / _voltageSamples);
        _voltageSamples = 10;
    }
}
