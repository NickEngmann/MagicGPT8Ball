#ifndef ARDUINO_H
#define ARDUINO_H

#include <stdint.h>
#include <string.h>
#include <math.h>
#include <stdio.h>

// Mock Arduino types
typedef uint8_t byte;
typedef unsigned int uint;
typedef unsigned long ulong;

// Mock Arduino functions
inline void delay(unsigned long ms) { (void)ms; }
inline void delayMicroseconds(unsigned long us) { (void)us; }
inline unsigned long millis() { return 0; }
inline unsigned long micros() { return 0; }
inline void noInterrupts() {}
inline void interrupts() {}
inline void pinMode(uint8_t, uint8_t) {}
inline void digitalWrite(uint8_t, uint8_t) {}
inline int digitalRead(uint8_t) { return 0; }
inline void analogWrite(uint8_t, uint8_t) {}
inline int analogRead(uint8_t) { return 0; }
inline void analogReadResolution(uint8_t) {}
inline int analogWriteResolution(uint8_t) { return 12; }
inline void attachInterrupt(uint8_t, void (*)(), int) {}
inline void detachInterrupt(uint8_t) {}
inline void SerialPrint(const char* s) { printf("%s", s); }
inline void SerialPrintln(const char* s) { printf("%s\n", s); }

#endif
