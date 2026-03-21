/**
 * @file wiring.h
 * @brief Arduino wiring functions for native builds
 */

#ifndef WIRING_H
#define WIRING_H

#include <stdint.h>

// Basic Arduino functions
void pinMode(uint8_t, uint8_t);
void digitalWrite(uint8_t, uint8_t);
int digitalRead(uint8_t);
void analogWrite(uint8_t, int);
int analogRead(uint8_t);
unsigned long millis();
unsigned long micros();
void delay(unsigned long);
void delayMicroseconds(unsigned long);

#endif // WIRING_H
