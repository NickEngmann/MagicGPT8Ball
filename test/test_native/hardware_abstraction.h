/**
 * Hardware abstraction layer for native testing
 * Allows C++ components to be tested without Arduino hardware
 */

#ifndef HARDWARE_ABSTRACTION_H
#define HARDWARE_ABSTRACTION_H

#ifdef NATIVE_BUILD

// Native build (desktop testing)
#include <cstdint>
#include <functional>
#include <vector>
#include <memory>
#include <iostream>

namespace Hardware {

// Timer abstraction
class Timer {
public:
    static unsigned long millis();
    static void delay(unsigned long ms);
    static unsigned long micros();
};

// GPIO abstraction
class GPIO {
public:
    static void pinMode(uint8_t pin, uint8_t mode);
    static void digitalWrite(uint8_t pin, uint8_t value);
    static int digitalRead(uint8_t pin);
};

// ADC abstraction
class ADC {
public:
    static int16_t read(uint8_t channel);
    static void setResolution(uint8_t bits);
    static void setAttenuation(uint8_t atten);
};

// NeoPixel/Led abstraction
class NeoPixel {
public:
    static std::vector<uint32_t> pixels;
    static uint8_t brightness;
    
    static void begin();
    static void show();
    static void setBrightness(uint8_t b);
    static void setPixelColor(uint8_t idx, uint32_t color);
    static uint32_t getPixelColor(uint8_t idx);
    static uint16_t ColorHSV(uint16_t hue);
    static uint32_t gamma32(uint32_t color);
    static void clear();
};

// Serial abstraction
class Serial {
public:
    static void print(const char* str);
    static void println(const char* str);
    static void printf(const char* format, ...);
    static void flush();
};

// Heap abstraction
class Heap {
public:
    static size_t getFreeHeapSize();
    static size_t getFreePSRAM();
};

// Filesystem abstraction
class FS {
public:
    static bool exists(const char* path);
    static int readFile(const char* path, uint8_t* buf, size_t len);
    static int writeFile(const char* path, const uint8_t* buf, size_t len);
};

} // namespace Hardware

// Arduino compatibility macros
#define HIGH 1
#define LOW 0
#define INPUT 0
#define OUTPUT 1
#define uint8_t uint8_t
#define uint16_t uint16_t
#define uint32_t uint32_t
#define int16_t int16_t

#else

// Arduino build - use real Arduino headers
#include <Arduino.h>

#endif // NATIVE_BUILD

#endif // HARDWARE_ABSTRACTION_H
