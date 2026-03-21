/**
 * @file Arduino_mock.h
 * @brief Minimal mock Arduino header for native (PC) builds
 *
 * Provides Arduino-like functionality for testing on non-embedded platforms
 */

#ifndef ARDUINO_MOCK_H
#define ARDUINO_MOCK_H

#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <algorithm>
#include <stdarg.h>
#include <vector>
using namespace std;

// Arduino basic types
typedef unsigned char byte;

// Arduino constants
#define HIGH 1
#define LOW 0
#define INPUT 0
#define OUTPUT 1

// String class mock (similar to Arduino String)
class String {
public:
    String() : _data("") {}
    String(const char* s) : _data(s ? s : "") {}
    String(const String& other) : _data(other._data) {}
    String(const std::string& s) : _data(s) {}
    
    const char* c_str() const { return _data.c_str(); }
    operator const char*() const { return _data.c_str(); }
    
    String& operator=(const String& other) {
        _data = other._data;
        return *this;
    }
    
    bool operator==(const String& other) const { return _data == other._data; }
    bool operator==(const char* s) const { return _data == s; }
    bool operator!=(const String& other) const { return _data != other._data; }
    
    int length() const { return (int)_data.length(); }
    size_t size() const { return _data.length(); }
    
    int indexOf(char c) const {
        size_t pos = _data.find(c);
        return (int)(pos == std::string::npos ? -1 : pos);
    }
    
    int indexOf(const char* substr) const {
        size_t pos = _data.find(substr);
        return (int)(pos == std::string::npos ? -1 : pos);
    }
    
    String substring(int start) const {
        if (start < 0 || (size_t)start >= _data.length()) return String("");
        return String(_data.substr(start));
    }
    
    String substring(int start, int end) const {
        if (start < 0 || end > (int)_data.length() || start >= end) return String("");
        return String(_data.substr(start, end - start));
    }
    
    String& trim() {
        size_t start = _data.find_first_not_of(" \t\n\r");
        if (start == std::string::npos) {
            _data = "";
            return *this;
        }
        size_t end = _data.find_last_not_of(" \t\n\r");
        _data = _data.substr(start, end - start + 1);
        return *this;
    }
    
    void toLowerCase() {
        std::transform(_data.begin(), _data.end(), _data.begin(), ::tolower);
    }
    
    void toUpperCase() {
        std::transform(_data.begin(), _data.end(), _data.begin(), ::toupper);
    }
    
    String& operator+=(const String& other) {
        _data += other._data;
        return *this;
    }
    
    String& operator+=(const char* s) {
        if (s) _data += s;
        return *this;
    }
    
    String& operator+=(char c) {
        _data += c;
        return *this;
    }
    
    bool startsWith(const char* prefix) const {
        return _data.rfind(prefix, 0) == 0;
    }
    
    char charAt(int index) const {
        if (index < 0 || (size_t)index >= _data.length()) return '\0';
        return _data[index];
    }
    
    void setCharAt(char c, int index) {
        if (index >= 0 && (size_t)index < _data.length()) {
            _data[index] = c;
        }
    }
    
    int lastIndexOf(char c) const {
        size_t pos = _data.rfind(c);
        return (int)(pos == std::string::npos ? -1 : pos);
    }
    
    char* toCharArray(char* buf, size_t size) const {
        strncpy(buf, _data.c_str(), size - 1);
        buf[size - 1] = '\0';
        return buf;
    }
    
private:
    std::string _data;
};

// Arduino timing functions
static unsigned long _arduino_millis_counter = 0;
static unsigned long millis() { return _arduino_millis_counter++; }
static unsigned long micros() { return millis() * 1000; }
static void delay(unsigned long ms) { (void)ms; }
static void delayMicroseconds(unsigned long us) { (void)us; }
static void randomSeed(unsigned long seed) { (void)seed; }
static long random(long max) { (void)max; return 0; }
static long random(long min, long max) { (void)min; (void)max; return 0; }
static long map(long x, long in_min, long in_max) {
    if (in_max == in_min) return in_min;
    return (x - in_min) * (in_max - in_min) / (in_max - in_min) + in_min;
}

// Arduino I/O
static bool _pin_states[30] = {false};

static void pinMode(uint8_t pin, uint8_t mode) {
    (void)pin; (void)mode;
}

static void digitalWrite(uint8_t pin, uint8_t val) {
    if (pin < 30) _pin_states[pin] = (val == HIGH);
}

static int digitalRead(uint8_t pin) {
    if (pin < 30) return _pin_states[pin] ? HIGH : LOW;
    return LOW;
}

static void analogWrite(uint8_t pin, int value) {
    (void)pin; (void)value;
}

static int analogRead(uint8_t pin) {
    (void)pin;
    return 2048;
}

// Arduino serial
class SerialType {
public:
    void println(const char* s) { printf("%s\n", s); }
    void println(int n) { printf("%d\n", n); }
    void println(unsigned int n) { printf("%u\n", n); }
    void println(long n) { printf("%ld\n", n); }
    void println(float n, int decimals) { printf("%.*f\n", decimals, n); }
    void println(double n, int decimals) { printf("%.*f\n", decimals, n); }
    void println(const String& s) { printf("%s\n", s.c_str()); }
    
    void printf(const char* format, ...) {
        va_list args;
        va_start(args, format);
        vprintf(format, args);
        va_end(args);
    }
    
    void begin(long baud) { (void)baud; printf("\nSerial initialized at %ld baud\n", baud); }
    void print(const char* s) { printf("%s", s); }
    void print(int n) { printf("%d", n); }
    void print(unsigned int n) { printf("%u", n); }
    void print(long n) { printf("%ld", n); }
    void print(float n, int decimals) { printf("%.*f", decimals, n); }
    void print(const String& s) { printf("%s", s.c_str()); }
    void print(char c) { printf("%c", c); }
    
    int available() { return 0; }
    int read() { return -1; }
    void flush() {}
    bool exists() { return true; }
    operator bool() { return true; }
};

// File class mock
class File {
public:
    File() : _pos(0) {}
    File(const char* data) : _data(data ? data : ""), _pos(0) {}

    int read() {
        if (_pos < (int)_data.length()) return (unsigned char)_data[_pos++];
        return -1;
    }

    int read(uint8_t* buf, size_t size) {
        size_t available = _data.length() - _pos;
        size_t toRead = size < available ? size : available;
        if (buf && toRead > 0) {
            memcpy(buf, _data.c_str() + _pos, toRead);
        }
        _pos += toRead;
        return (int)toRead;
    }

    size_t write(const uint8_t* buf, size_t size) {
        _data.append((const char*)buf, size);
        return size;
    }

    int available() { return (int)(_data.length() - _pos); }
    void close() { _pos = _data.length(); }
    uint32_t position() { return _pos; }
    uint32_t size() { return _data.length(); }
    operator bool() { return true; }
    
    String readString() {
        String result(_data.substr(_pos));
        _pos = _data.length();
        return result;
    }
    
    String readStringUntil(char terminator) {
        size_t end = _data.find(terminator, _pos);
        if (end == std::string::npos) {
            end = _data.length();
        }
        String result(_data.substr(_pos, end - _pos));
        _pos = end;
        if (end < _data.length() && _data[end] == terminator) {
            _pos++;
        }
        return result;
    }

private:
    std::string _data;
    uint32_t _pos;
};

// File system mock
class FS {
public:
    class File {
    public:
        File() : _pos(0) {}
        int read() { return -1; }
        int available() { return 0; }
        String readStringUntil(char terminator) {
            (void)terminator;
            return String("");
        }
        bool close() { return true; }
        operator bool() { return true; }
        size_t read(uint8_t* buf, size_t size) {
            (void)buf; (void)size;
            return 0;
        }
    private:
        size_t _pos;
    };
    
    File open(const char* path, const char* mode = "r") {
        (void)path; (void)mode;
        return File();
    }
    bool begin(bool formatOnFail) { (void)formatOnFail; return true; }
    bool mount() { return true; }
    bool unmount() { return true; }
    bool remove(const char* path) { (void)path; return true; }
    bool mkdir(const char* path) { (void)path; return true; }
    bool exists(const char* path) { (void)path; return true; }
};

// Forward declare global instances - defined in Arduino_globals.cpp
extern SerialType Serial;
extern FS LittleFS;

#endif // ARDUINO_MOCK_H
