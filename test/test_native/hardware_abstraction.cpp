/**
 * Hardware abstraction layer implementation for native testing
 */

#ifdef NATIVE_BUILD

#include "hardware_abstraction.h"
#include <cstdarg>
#include <chrono>
#include <map>
#include <unordered_map>
#include <cmath>
#include <fstream>
#include <sstream>

namespace Hardware {

// Timer implementation
unsigned long Timer::millis() {
    auto now = std::chrono::steady_clock::now();
    auto duration = now.time_since_epoch();
    return std::chrono::duration_cast<std::chrono::milliseconds>(duration).count();
}

void Timer::delay(unsigned long ms) {
    std::this_thread::sleep_for(std::chrono::milliseconds(ms));
}

unsigned long Timer::micros() {
    auto now = std::chrono::steady_clock::now();
    auto duration = now.time_since_epoch();
    return std::chrono::duration_cast<std::chrono::microseconds>(duration).count();
}

// GPIO state management
std::unordered_map<uint8_t, int> gpio_state;

void GPIO::pinMode(uint8_t pin, uint8_t mode) {
    gpio_state[pin] = mode;
    std::cout << "[GPIO] Pin " << (int)pin << " set to " 
              << (mode == INPUT ? "INPUT" : "OUTPUT") << std::endl;
}

void GPIO::digitalWrite(uint8_t pin, uint8_t value) {
    gpio_state[pin] = value;
    std::cout << "[GPIO] Pin " << (int)pin << " set to " 
              << (value == HIGH ? "HIGH" : "LOW") << std::endl;
}

int GPIO::digitalRead(uint8_t pin) {
    auto it = gpio_state.find(pin);
    return (it != gpio_state.end()) ? it->second : 0;
}

// ADC state
std::unordered_map<uint8_t, int16_t> adc_readings;
uint8_t adc_resolution = 12;
uint8_t adc_attenuation = 0;

int16_t ADC::read(uint8_t channel) {
    // Generate deterministic pseudo-random reading for testing
    int16_t base = 2048; // Midpoint for 12-bit
    int16_t variation = (channel * 100 + millis() % 200) - 100;
    variation = std::max(-500, std::min(500, variation));
    int16_t reading = base + variation;
    adc_readings[channel] = reading;
    return reading;
}

void ADC::setResolution(uint8_t bits) {
    adc_resolution = bits;
    std::cout << "[ADC] Resolution set to " << (int)bits << " bits" << std::endl;
}

void ADC::setAttenuation(uint8_t atten) {
    adc_attenuation = atten;
    std::cout << "[ADC] Attenuation set to " << (int)atten << " dB" << std::endl;
}

// NeoPixel implementation
std::vector<uint32_t> NeoPixel::pixels(1, 0);
uint8_t NeoPixel::brightness = 30;

void NeoPixel::begin() {
    std::cout << "[NeoPixel] Initialized with " << pixels.size() << " pixels" << std::endl;
}

void NeoPixel::show() {
    uint32_t color = pixels[0];
    uint8_t r = (color >> 16) & 0xFF;
    uint8_t g = (color >> 8) & 0xFF;
    uint8_t b = color & 0xFF;
    std::cout << "[NeoPixel] Show: RGB(" << (int)r << ", " << (int)g << ", " << (int)b 
              << ") Brightness: " << (int)brightness << std::endl;
}

void NeoPixel::setBrightness(uint8_t b) {
    brightness = b;
    std::cout << "[NeoPixel] Brightness set to " << (int)b << std::endl;
}

void NeoPixel::setPixelColor(uint8_t idx, uint32_t color) {
    while (pixels.size() <= idx) {
        pixels.push_back(0);
    }
    pixels[idx] = color;
    
    uint8_t r = (color >> 16) & 0xFF;
    uint8_t g = (color >> 8) & 0xFF;
    uint8_t b = color & 0xFF;
    std::cout << "[NeoPixel] Pixel " << (int)idx << " set to RGB(" 
              << (int)r << ", " << (int)g << ", " << (int)b << ")" << std::endl;
}

uint32_t NeoPixel::getPixelColor(uint8_t idx) {
    if (idx < pixels.size()) {
        return pixels[idx];
    }
    return 0;
}

uint16_t NeoPixel::ColorHSV(uint16_t hue) {
    // Simplified HSV to RGB conversion for testing
    uint8_t r = 0, g = 0, b = 0;
    
    hue = hue % 65536;
    uint16_t segment = hue / 2184; // 65536 / 30
    
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

uint32_t NeoPixel::gamma32(uint32_t color) {
    // Simplified gamma correction
    uint8_t r = (color >> 16) & 0xFF;
    uint8_t g = (color >> 8) & 0xFF;
    uint8_t b = color & 0xFF;
    
    r = (uint8_t)(pow(r / 255.0, 2.5) * 255);
    g = (uint8_t)(pow(g / 255.0, 2.5) * 255);
    b = (uint8_t)(pow(b / 255.0, 2.5) * 255);
    
    return ((uint32_t)r << 16) | ((uint32_t)g << 8) | b;
}

void NeoPixel::clear() {
    pixels.assign(1, 0);
    std::cout << "[NeoPixel] Cleared" << std::endl;
}

// Serial implementation
void Serial::print(const char* str) {
    std::cout << str;
}

void Serial::println(const char* str) {
    std::cout << str << std::endl;
}

void Serial::printf(const char* format, ...) {
    std::cout << "[Serial.printf] Format string: " << format << std::endl;
}

void Serial::flush() {
    std::cout.flush();
}

// Heap implementation
size_t Heap::getFreeHeapSize() {
    return 200000; // Simulate ESP32-S3 heap size
}

size_t Heap::getFreePSRAM() {
    return 4000000; // Simulate 4MB PSRAM
}

// Filesystem implementation
bool FS::exists(const char* path) {
    std::ifstream file(path);
    return file.good();
}

int FS::readFile(const char* path, uint8_t* buf, size_t len) {
    std::ifstream file(path, std::ios::binary);
    if (!file) return -1;
    
    file.read(reinterpret_cast<char*>(buf), len);
    return file.gcount();
}

int FS::writeFile(const char* path, const uint8_t* buf, size_t len) {
    std::ofstream file(path, std::ios::binary);
    if (!file) return -1;
    
    file.write(reinterpret_cast<const char*>(buf), len);
    return len;
}

} // namespace Hardware

#endif // NATIVE_BUILD
