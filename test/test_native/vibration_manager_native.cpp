/**
 * VibrationManager implementation for native testing
 */

#include "vibration_manager_native.h"
#include <unordered_map>

// Mock GPIO state
std::unordered_map<uint8_t, int> MockGPIO::pins;

void MockGPIO::pinMode(uint8_t pin, uint8_t mode) {
    pins[pin] = mode;
    std::cout << "[GPIO] Pin " << (int)pin << " set to " 
              << (mode == 1 ? "OUTPUT" : "INPUT") << std::endl;
}

void MockGPIO::digitalWrite(uint8_t pin, uint8_t value) {
    pins[pin] = value;
    std::cout << "[GPIO] Pin " << (int)pin << " set to " 
              << (value == 1 ? "HIGH" : "LOW") << std::endl;
}

int MockGPIO::digitalRead(uint8_t pin) {
    auto it = pins.find(pin);
    return (it != pins.end()) ? it->second : 0;
}

// MockTime state
unsigned long MockTime::mockTime = 0;

void MockTime::setMillis(unsigned long ms) {
    mockTime = ms;
}

unsigned long MockTime::getMillis() {
    return mockTime;
}

unsigned long MockTime::millis() {
    return mockTime;
}

// VibrationManagerNative implementation
VibrationManagerNative::VibrationManagerNative(uint8_t motor1Pin, uint8_t motor2Pin)
    : motor1Pin_(motor1Pin),
      motor2Pin_(motor2Pin),
      isVibrating_(false),
      startTime_(0),
      duration_(0) {
}

void VibrationManagerNative::begin() {
    MockGPIO::pinMode(motor1Pin_, 1); // OUTPUT
    MockGPIO::pinMode(motor2Pin_, 1); // OUTPUT
    stop();
    std::cout << "[VibrationManagerNative] Initialized on pins " 
              << (int)motor1Pin_ << ", " << (int)motor2Pin_ << std::endl;
}

void VibrationManagerNative::update() {
    if (isVibrating_ && currentMillis() - startTime_ >= duration_) {
        stop();
    }
}

void VibrationManagerNative::startVibration(unsigned long duration) {
    isVibrating_ = true;
    startTime_ = currentMillis();
    duration_ = duration;
    
    MockGPIO::digitalWrite(motor1Pin_, 1); // HIGH
    MockGPIO::digitalWrite(motor2Pin_, 1); // HIGH
    
    std::cout << "[VibrationManagerNative] Started vibration for " 
              << duration << " ms" << std::endl;
}

void VibrationManagerNative::stop() {
    isVibrating_ = false;
    
    MockGPIO::digitalWrite(motor1Pin_, 0); // LOW
    MockGPIO::digitalWrite(motor2Pin_, 0); // LOW
    
    std::cout << "[VibrationManagerNative] Stopped vibration" << std::endl;
}

void VibrationManagerNative::shortBuzz() {
    startVibration(100);
    std::cout << "[VibrationManagerNative] Short buzz (100ms)" << std::endl;
}

void VibrationManagerNative::mediumBuzz() {
    startVibration(250);
    std::cout << "[VibrationManagerNative] Medium buzz (250ms)" << std::endl;
}

void VibrationManagerNative::longBuzz() {
    startVibration(500);
    std::cout << "[VibrationManagerNative] Long buzz (500ms)" << std::endl;
}

void VibrationManagerNative::doubleBuzz() {
    startVibration(100);
    MockTime::setMillis(startTime_ + 100);
    stop();
    MockTime::setMillis(startTime_ + 200);
    startVibration(100);
    std::cout << "[VibrationManagerNative] Double buzz" << std::endl;
}

unsigned long VibrationManagerNative::currentMillis() {
    return MockTime::millis();
}
