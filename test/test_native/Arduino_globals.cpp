/**
 * @file Arduino_globals.cpp
 * @brief Global Arduino instance definitions for native builds
 *
 * Defines global Serial and LittleFS instances in a single file
 * to avoid multiple definition issues when compiling tests
 */

#include "Arduino_mock.h"

// Define global instances here to avoid multiple definition issues
SerialType Serial;
FS LittleFS;
