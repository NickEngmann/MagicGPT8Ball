/**
 * @file analog_write.h
 * @brief Analog I/O functions for native builds
 */

#ifndef ANALOG_WRITE_H
#define ANALOG_WRITE_H

#include <stdint.h>

void analogWrite(uint8_t pin, int value);
int analogRead(uint8_t pin);

#endif // ANALOG_WRITE_H
