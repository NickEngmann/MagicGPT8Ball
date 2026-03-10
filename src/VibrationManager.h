#ifndef VIBRATION_MANAGER_H
#define VIBRATION_MANAGER_H

#ifdef NATIVE_BUILD


#else
#include <Arduino.h>
#endif

class VibrationManager {
public:
    // Constructor
    VibrationManager(uint8_t motor1Pin = 5, uint8_t motor2Pin = 13) 
        : _motor1Pin(motor1Pin), _motor2Pin(motor2Pin), _isVibrating(false), _startTime(0), _duration(0) {}

#ifdef NATIVE_BUILD
    // Native build - mock implementations
    void begin() {}
    void startVibration(unsigned long duration) {
        _isVibrating = true;
        _startTime = std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::steady_clock::now().time_since_epoch()).count();
        _duration = duration;
    }
    void stop() {
        _isVibrating = false;
    }
    void update() {
        if (_isVibrating) {
            auto now = std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::steady_clock::now().time_since_epoch()).count();
            if ((now - _startTime) >= (long)_duration) {
                stop();
            }
        }
    }
    void shortBuzz() { startVibration(100); }
    void mediumBuzz() { startVibration(250); }
    void longBuzz() { startVibration(500); }
    void doubleBuzz() {
        startVibration(100);
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        startVibration(100);
    }
#else
    // Arduino build
    void begin() {
        pinMode(_motor1Pin, OUTPUT);
        pinMode(_motor2Pin, OUTPUT);
        stop();
    }
    void startVibration(unsigned long duration) {
        _isVibrating = true;
        _startTime = millis();
        _duration = duration;
        digitalWrite(_motor1Pin, HIGH);
        digitalWrite(_motor2Pin, HIGH);
    }
    void stop() {
        _isVibrating = false;
        digitalWrite(_motor1Pin, LOW);
        digitalWrite(_motor2Pin, LOW);
    }
    void update() {
        if (_isVibrating && (millis() - _startTime >= _duration)) {
            stop();
        }
    }
    void shortBuzz() { startVibration(100); }
    void mediumBuzz() { startVibration(250); }
    void longBuzz() { startVibration(500); }
    void doubleBuzz() {
        startVibration(100);
        delay(100);
        startVibration(100);
    }
#endif

    bool isVibrating() const {
        return _isVibrating;
    }

private:
    uint8_t _motor1Pin;
    uint8_t _motor2Pin;
    bool _isVibrating;
    unsigned long _startTime;
    unsigned long _duration;
};

#endif // VIBRATION_MANAGER_H