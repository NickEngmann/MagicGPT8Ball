#ifndef LED_LOGGER_NATIVE_H
#define LED_LOGGER_NATIVE_H

#include <cstdint>
#include <functional>
#include <vector>
#include <memory>
#include <chrono>

// Mock Arduino types
typedef uint8_t uint8;
typedef uint16_t uint16;
typedef uint32_t uint32;
typedef int8_t int8;
typedef int16_t int16;
typedef int32_t int32;

// Adafruit NeoPixel mock class for testing
class MockNeoPixel {
public:
    MockNeoPixel(uint8_t num_pixels, uint8_t pin, uint8_t type);
    
    void begin();
    void show();
    void setBrightness(uint8_t brightness);
    void setPixelColor(uint8_t idx, uint32_t color);
    uint32_t getPixelColor(uint8_t idx);
    uint16_t ColorHSV(uint16_t hue);
    uint32_t gamma32(uint32_t color);
    void clear();
    
    // For testing
    std::vector<uint32_t>& getPixels() { return pixels; }
    const std::vector<uint32_t>& getPixelsConst() const { return pixels; }
    uint8_t getBrightness() const { return brightness; }
    bool lastShowFlag = false;
    
private:
    std::vector<uint32_t> pixels;
    uint8_t brightness;
};

// LED Logger implementation for native testing
class LEDLoggerNative {
public:
    // Standard system states
    enum class SystemState {
        STARTUP,
        NORMAL,
        WARNING,
        ERROR,
        MAINTENANCE,
        UPDATING,
        CONNECTING,
        BUSY,
        STANDBY,
        CUSTOM
    };
    
    // Patterns
    enum class LEDPattern {
        SOLID,
        PULSE,
        BLINK,
        FAST_BLINK,
        DOUBLE_BLINK,
        RAINBOW
    };
    
    LEDLoggerNative(uint8_t pin, uint8_t brightness = 30);
    
    void begin();
    void update();
    void setState(SystemState state, LEDPattern pattern = LEDPattern::SOLID);
    void setCustomState(uint32_t color, LEDPattern pattern = LEDPattern::SOLID);
    void setBrightness(uint8_t brightness);
    void clear();
    
    // Getters for testing
    SystemState getCurrentState() const { return currentState; }
    LEDPattern getCurrentPattern() const { return currentPattern; }
    uint32_t getCurrentColor() const { return currentColor; }
    const std::vector<uint32_t>& getPixels() const { return pixel.getPixelsConst(); }
    
    // Mock the hardware
    MockNeoPixel pixel;
    
private:
    SystemState currentState;
    LEDPattern currentPattern;
    unsigned long lastUpdate;
    float pulseValue;
    bool increasing;
    uint32_t currentColor;
    uint8_t brightness;
    
    // Color constants
    static constexpr uint32_t COLOR_STARTUP = 0x0000FF;
    static constexpr uint32_t COLOR_NORMAL = 0x00FF00;
    static constexpr uint32_t COLOR_WARNING = 0xFFFF00;
    static constexpr uint32_t COLOR_ERROR = 0xFF0000;
    static constexpr uint32_t COLOR_MAINTENANCE = 0xFF00FF;
    static constexpr uint32_t COLOR_UPDATING = 0xFFFFFF;
    static constexpr uint32_t COLOR_CONNECTING = 0x00FFFF;
    static constexpr uint32_t COLOR_BUSY = 0xFFA500;
    static constexpr uint32_t COLOR_STANDBY = 0x101010;
    
    static constexpr unsigned long PULSE_INTERVAL = 30;
    static constexpr unsigned long BLINK_INTERVAL = 500;
    static constexpr unsigned long FAST_BLINK_INTERVAL = 100;
    
    void updatePattern();
    uint32_t getColorForState(SystemState state);
    void setPixel(uint32_t color);
    uint32_t dimColor(uint32_t color, float factor);
};

// Type aliases for easier access in tests
using LEDLoggerState = LEDLoggerNative::SystemState;
using LEDLoggerPattern = LEDLoggerNative::LEDPattern;

// Mock millis() for testing
class MockTime {
public:
    static void setMillis(unsigned long ms);
    static unsigned long getMillis();
    static unsigned long millis();
    static void delay(unsigned long ms);
    
private:
    static unsigned long mockTime;
};

#endif // LED_LOGGER_NATIVE_H
