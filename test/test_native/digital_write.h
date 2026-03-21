/**
 * @file digital_write.h
 * @brief Digital I/O functions for native builds
 */

#ifndef DIGITAL_WRITE_H
#define DIGITAL_WRITE_H

#include <stdint.h>

void digitalWrite(uint8_t pin, uint8_t value);
int digitalRead(uint8_t pin);

#endif // DIGITAL_WRITE_H
