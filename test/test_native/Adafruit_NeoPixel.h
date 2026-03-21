/**
 * @file Adafruit_NeoPixel.h
 * @brief Mock Adafruit_NeoPixel for native builds
 */

#ifndef ADAFRUIT_NEOPIXEL_H
#define ADAFRUIT_NEOPIXEL_H

#include <stdint.h>

// NeoPixel type constants
#define NEO_GRB 0
#define NEO_RGB 1
#define NEO_KHZ400 0
#define NEO_KHZ800 1

class Adafruit_NeoPixel {
public:
    Adafruit_NeoPixel(int n, uint8_t p, uint8_t t = NEO_GRB + NEO_KHZ800) 
        : _numLEDs(n), _pin(p), _brightness(30) {}
    
    void begin() {}
    void show() {}
    void clear() {}
    void setPixelColor(uint8_t n, uint32_t c) {
        if (n < 1) return;
        _pixelColors[0] = c;
    }
    void setBrightness(uint8_t b) { _brightness = b; }
    uint8_t getBrightness() { return _brightness; }
    
    static uint32_t ColorHSV(uint32_t h) { return h; }
    static uint32_t Color(uint8_t r, uint8_t g, uint8_t b) {
        return ((uint32_t)r << 16) | ((uint32_t)g << 8) | (uint32_t)b;
    }
    
    uint32_t gamma32(uint32_t h) { return h; }
    
private:
    int _numLEDs;
    uint8_t _pin;
    uint8_t _brightness;
    uint32_t _pixelColors[1];
};

#endif // ADAFRUIT_NEOPIXEL_H
