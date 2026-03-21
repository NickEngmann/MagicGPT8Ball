/**
 * @file Arduino.h
 * @brief Arduino compatibility header for native (PC) builds
 *
 * Redirects all Arduino includes to our mock implementations
 * This allows existing embedded code to compile on non-embedded platforms
 */

#ifndef ARDUINO_H
#define ARDUINO_H

// Include our mock implementations
#include "Arduino_mock.h"

// Include standard Arduino library headers (they're just includes of mock)
#include <pins_arduino.h>
#include <wiring.h>
#include <wiring_private.h>
#include <digital_write.h>
#include <analog_write.h>
#include <math.h>
#include <string.h>

#endif // ARDUINO_H
