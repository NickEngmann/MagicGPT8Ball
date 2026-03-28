/**
 * LEDLogger implementation for native testing
 * Provides the same functionality as the Arduino version but works on desktop
 */

#include "led_logger_native.h"
#include <iostream>
#include <thread>
#include <chrono>
#include <cmath>

// Mock time state
unsigned long MockTime::mockTime = 0;

MockNeoPixel::MockNeoPixel(uint8_t num_pixels, uint8_t pin, uint8_t type) : brightness(30) {
    pixels.resize(num_pixels, 0);
    std::cout << "[NeoPixel Mock] Created with " << num_pixels << " pixels" << std::endl;
}

void MockNeoPixel::begin() {
    std::cout << "[NeoPixel Mock] begin()" << std::endl;
}

void MockNeoPixel::show() {
    lastShowFlag = true;
    std::cout << "[NeoPixel Mock] show() - RGB(" 
              << ((pixels[0] >> 16) & 0xFF) << "," 
              << ((pixels[0] >> 8) & 0xFF) << "," 
              << (pixels[0] & 0xFF) << ")" << std::endl;
}

void MockNeoPixel::setBrightness(uint8_t b) {
    brightness = b;
    std::cout << "[NeoPixel Mock] setBrightness(" << (int)b << ")" << std::endl;
}

void MockNeoPixel::setPixelColor(uint8_t idx, uint32_t color) {
    pixels[idx] = color;
}

uint32_t MockNeoPixel::getPixelColor(uint8_t idx) {
    return idx < pixels.size() ? pixels[idx] : 0;
}

uint16_t MockNeoPixel::ColorHSV(uint16_t hue) {
    uint8_t r = 0, g = 0, b = 0;
    hue = hue % 65536;
    uint16_t segment = hue / 2184;
    
    switch (segment) {
        case 0: r = 255; g = (hue % 2184) * 255 / 2184; b = 0; break;
        case 1: r = 255 - ((hue % 2184) * 255 / 2184); g = 255; b = 0; break;
        case 2: r = 0; g = 255; b = (hue % 2184) * 255 / 2184; break;
        case 3: r = 0; g = 255 - ((hue % 2184) * 255 / 2184); b = 255; break;
        case 4: r = (hue % 2184) * 255 / 2184; g = 0; b = 255; break;
        default: r = 255; g = 0; b = 255 - ((hue % 2184) * 255 / 2184); break;
    }
    
    return ((uint32_t)r << 16) | ((uint32_t)g << 8) | b;
}

uint32_t MockNeoPixel::gamma32(uint32_t color) {
    uint8_t r = (color >> 16) & 0xFF;
    uint8_t g = (color >> 8) & 0xFF;
    uint8_t b = color & 0xFF;
    
    r = (uint8_t)(pow(r / 255.0, 2.5) * 255);
    g = (uint8_t)(pow(g / 255.0, 2.5) * 255);
    b = (uint8_t)(pow(b / 255.0, 2.5) * 255);
    
    return ((uint32_t)r << 16) | ((uint32_t)g << 8) | b;
}

void MockNeoPixel::clear() {
    pixels.assign(1, 0);
}

void MockTime::setMillis(unsigned long ms) {
    mockTime = ms;
}

unsigned long MockTime::getMillis() {
    return mockTime;
}

unsigned long MockTime::millis() {
    return mockTime;
}

void MockTime::delay(unsigned long ms) {
    std::this_thread::sleep_for(std::chrono::milliseconds(ms));
}

// LEDLoggerNative implementation
LEDLoggerNative::LEDLoggerNative(uint8_t pin, uint8_t brightness) 
    : pixel(1, pin, 1), // NEO_GRB + NEO_KHZ400 = 1
      currentState(SystemState::STARTUP),
      currentPattern(LEDPattern::PULSE),
      lastUpdate(0),
      pulseValue(0),
      increasing(true),
      currentColor(COLOR_STARTUP),
      brightness(brightness) {
}

void LEDLoggerNative::begin() {
    pixel.begin();
    pixel.setBrightness(brightness);
    pixel.show();
}

void LEDLoggerNative::setState(SystemState state, LEDPattern pattern) {
    currentState = state;
    currentPattern = pattern;
    currentColor = getColorForState(state);
    pulseValue = 0;
    increasing = true;
    lastUpdate = MockTime::millis();
    
    std::cout << "[LEDLoggerNative] State changed to " 
              << (int)state << ", Pattern: " << (int)pattern << std::endl;
}

void LEDLoggerNative::setCustomState(uint32_t color, LEDPattern pattern) {
    currentState = SystemState::CUSTOM;
    currentPattern = pattern;
    currentColor = color;
    pulseValue = 0;
    increasing = true;
    lastUpdate = MockTime::millis();
    
    std::cout << "[LEDLoggerNative] Custom state with color 0x" 
              << std::hex << color << std::dec << std::endl;
}

void LEDLoggerNative::setBrightness(uint8_t newBrightness) {
    brightness = newBrightness;
    pixel.setBrightness(brightness);
    pixel.show();
}

void LEDLoggerNative::clear() {
    pixel.clear();
    pixel.show();
    currentState = SystemState::STANDBY;
    currentPattern = LEDPattern::SOLID;
    currentColor = 0;
}

void LEDLoggerNative::update() {
    updatePattern();
    pixel.show();
}

void LEDLoggerNative::updatePattern() {
    unsigned long now = MockTime::millis();
    
    switch (currentPattern) {
        case LEDPattern::SOLID:
            setPixel(currentColor);
            break;
            
        case LEDPattern::PULSE:
            if (now - lastUpdate >= PULSE_INTERVAL) {
                if (increasing) {
                    pulseValue += 0.05;
                    if (pulseValue >= 1.0) {
                        pulseValue = 1.0;
                        increasing = false;
                    }
                } else {
                    pulseValue -= 0.05;
                    if (pulseValue <= 0.0) {
                        pulseValue = 0.0;
                        increasing = true;
                    }
                }
                setPixel(dimColor(currentColor, pulseValue));
                lastUpdate = now;
            }
            break;
            
        case LEDPattern::BLINK:
            if (now - lastUpdate >= BLINK_INTERVAL) {
                static bool isOn = false;
                isOn = !isOn;
                setPixel(isOn ? currentColor : 0);
                lastUpdate = now;
            }
            break;
            
        case LEDPattern::FAST_BLINK:
            if (now - lastUpdate >= FAST_BLINK_INTERVAL) {
                static bool isOn = false;
                isOn = !isOn;
                setPixel(isOn ? currentColor : 0);
                lastUpdate = now;
            }
            break;
            
        case LEDPattern::DOUBLE_BLINK:
            if (now - lastUpdate >= BLINK_INTERVAL) {
                static uint8_t blinkState = 0;
                switch (blinkState) {
                    case 0: setPixel(currentColor); break;
                    case 1: setPixel(0); break;
                    case 2: setPixel(currentColor); break;
                    case 3: setPixel(0); break;
                    default: blinkState = 0; break;
                }
                blinkState = (blinkState + 1) % 5;
                lastUpdate = now;
            }
            break;
            
        case LEDPattern::RAINBOW:
            if (now - lastUpdate >= PULSE_INTERVAL) {
                static uint16_t hue = 0;
                hue += 256;
                if (hue >= 65536) hue = 0;
                setPixel(pixel.gamma32(pixel.ColorHSV(hue)));
                lastUpdate = now;
            }
            break;
    }
}

uint32_t LEDLoggerNative::getColorForState(SystemState state) {
    switch (state) {
        case SystemState::STARTUP: return COLOR_STARTUP;
        case SystemState::NORMAL: return COLOR_NORMAL;
        case SystemState::WARNING: return COLOR_WARNING;
        case SystemState::ERROR: return COLOR_ERROR;
        case SystemState::MAINTENANCE: return COLOR_MAINTENANCE;
        case SystemState::UPDATING: return COLOR_UPDATING;
        case SystemState::CONNECTING: return COLOR_CONNECTING;
        case SystemState::BUSY: return COLOR_BUSY;
        case SystemState::STANDBY: return COLOR_STANDBY;
        default: return COLOR_NORMAL;
    }
}

void LEDLoggerNative::setPixel(uint32_t color) {
    pixel.setPixelColor(0, color);
}

uint32_t LEDLoggerNative::dimColor(uint32_t color, float factor) {
    uint8_t r = (color >> 16) & 0xFF;
    uint8_t g = (color >> 8) & 0xFF;
    uint8_t b = color & 0xFF;
    
    r = static_cast<uint8_t>(r * factor);
    g = static_cast<uint8_t>(g * factor);
    b = static_cast<uint8_t>(b * factor);
    
    return ((uint32_t)r << 16) | ((uint32_t)g << 8) | b;
}
