#ifndef Arduino_h
#define Arduino_h

#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>

// Basic types
#define boolean bool
#define byte unsigned char
#define HIGH 1
#define LOW 0

// Pin definitions
#define INPUT 0
#define OUTPUT 1
#define INPUT_PULLUP 2
#define INPUT_PULLDOWN 3

// Digital functions
void digitalWrite(uint8_t pin, uint8_t value);
int digitalRead(uint8_t pin);
void pinMode(uint8_t pin, uint8_t mode);

// Analog functions
void analogWrite(uint8_t pin, int value);
int analogRead(uint8_t pin);
int analogReadResolution(uint8_t bits);
void analogWriteResolution(uint8_t bits);

// Timing functions
unsigned long millis();
unsigned long micros();
void delay(unsigned long ms);
void delayMicroseconds(unsigned long us);

// Random functions
long random(long howbig);
long random(long howsmall, long howbig);
void randomSeed(unsigned int seed);

// Serial functions
class SerialPort {
public:
    void begin(long baudrate) {}
    void print(const char* str) {}
    void println(const char* str) {}
    void print(const String& str) {}
    void println(const String& str) {}
    int available() { return 0; }
    int read() { return -1; }
    void flush() {}
};
extern SerialPort Serial;

// String class
class String {
public:
    String() {}
    String(const char* str) {}
    String(const String& str) {}
    operator const char*() const { return ""; }
    int length() const { return 0; }
    int indexOf(char c) const { return -1; }
    int lastIndexOf(char c) const { return -1; }
    char charAt(int index) const { return 0; }
    String substring(int beginIndex, int endIndex) const { return String(); }
    String toLowerCase() const { return String(); }
    String toUpperCase() const { return String(); }
    bool equals(const char* str) const { return false; }
    bool equals(const String& str) const { return false; }
    bool equalsIgnoreCase(const String& str) const { return false; }
    bool startsWith(const char* prefix) const { return false; }
    bool endsWith(const char* suffix) const { return false; }
    char* c_str() const { return (char*)""; }
    String operator+(const String& str) const { return String(); }
    String operator+(const char* str) const { return String(); }
    char& operator[](int index) { static char c; return c; }
    int operator==(const char* str) const { return 0; }
    int operator==(const String& str) const { return 0; }
    int operator!=(const char* str) const { return 1; }
    int operator!=(const String& str) const { return 1; }
    int operator<(const String& str) const { return 0; }
    int operator>(const String& str) const { return 0; }
    int operator<=(const String& str) const { return 0; }
    int operator>=(const String& str) const { return 0; }
};

// Arduino core functions
void noInterrupts();
void interrupts();
void attachInterrupt(int pin, void (*isr)(), int mode);
void detachInterrupt(int pin);

// Bit manipulation
#define bit(b) (1UL << (b))
#define bitSet(value, bit) ((value) |= bit(bit))
#define bitClear(value, bit) ((value) &= ~bit(bit))
#define bitWrite(value, bit, bitvalue) ((bitvalue) ? bitSet(value, bit) : bitClear(value, bit))
#define bitRead(value, bit) (((value) >> (bit)) & 0x01)

// Min/Max
#define min(a,b) ((a)<(b)?(a):(b))
#define max(a,b) ((a)>(b)?(a):(b))
#define abs(x) ((x)>0?(x):-(x))
#define constrain(amt,low,high) ((amt)<(low)?(low):((amt)>(high)?(high):(amt)))

// Round
#define round(x)     ((x)>=0?(long)((x)+0.5):(long)((x)-0.5))

// Degrees to radians
#define radians(deg) ((deg)*0.0174532925)

// Radians to degrees
#define degrees(rad) ((rad)*57.2957795131)

// Map function
long map(long x, long in_min, long in_max, long out_min, long out_max);

// Floating point
#define isFinite(x) 1
#define isInf(x) 0
#define isNan(x) 0

#endif // Arduino_h
