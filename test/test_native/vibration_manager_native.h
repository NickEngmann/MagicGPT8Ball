#ifndef VIBRATION_MANAGER_NATIVE_H
#define VIBRATION_MANAGER_NATIVE_H

#include <cstdint>
#include <functional>
#include <chrono>
#include <iostream>

// Mock GPIO state
class MockGPIO {
public:
    static std::unordered_map<uint8_t, int> pins;
    
    static void pinMode(uint8_t pin, uint8_t mode);
    static void digitalWrite(uint8_t pin, uint8_t value);
    static int digitalRead(uint8_t pin);
};

// VibrationManager implementation for native testing
class VibrationManagerNative {
public:
    VibrationManagerNative(uint8_t motor1Pin = 5, uint8_t motor2Pin = 13);
    
    void begin();
    void update();
    void startVibration(unsigned long duration);
    void stop();
    
    // Predefined patterns
    void shortBuzz();
    void mediumBuzz();
    void longBuzz();
    void doubleBuzz();
    
    bool isVibrating() const { return isVibrating_; }
    unsigned long getStartTime() const { return startTime_; }
    unsigned long getDuration() const { return duration_; }
    
    // For testing
    uint8_t getMotor1Pin() const { return motor1Pin_; }
    uint8_t getMotor2Pin() const { return motor2Pin_; }
    
private:
    uint8_t motor1Pin_;
    uint8_t motor2Pin_;
    bool isVibrating_;
    unsigned long startTime_;
    unsigned long duration_;
    
    unsigned long currentMillis();
};

// MockTime for testing
class MockTime {
public:
    static void setMillis(unsigned long ms);
    static unsigned long getMillis();
    static unsigned long millis();
    
private:
    static unsigned long mockTime;
};

#endif // VIBRATION_MANAGER_NATIVE_H
