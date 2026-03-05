# MARISOL.md — Pipeline Context

## Project Overview
Magic (GPT)8 Ball is an IoT fortune-telling device built on ESP32-S3 hardware using PlatformIO and Arduino framework. It features voice recognition via microphone array, motion sensing with QMI8658 accelerometer, 320x240 TFT display with LVGL graphics, and AI-powered responses via OpenAI ChatGPT and Whisper APIs. The device connects to WiFi and communicates with a serverless backend hosted on val.town.

## Build & Run
- **Language**: C++ (Arduino framework)
- **Framework**: PlatformIO, ESP32 Arduino core
- **Docker image**: platformio/platformio-arduino:latest (Ubuntu-based PlatformIO image)
- **Install deps**: `pip install --no-cache-dir platformio` then `pio run` (installs Arduino libraries via lib_deps)
- **Run**: No runnable entry point — this is embedded hardware firmware. Upload to ESP32-S3 device via `pio run --target upload` or `pio upload`

## Testing
- **Test framework**: None (hardware-dependent embedded project)
- **Test command**: No automated tests available — project requires physical ESP32-S3 hardware with QMI8658 sensor, microphone array, and TFT display
- **Hardware mocks needed**: Yes — requires ESP32-S3, QMI8658 accelerometer, 320x240 SPI TFT display, I2S microphone array
- **Known test issues**: Cannot run tests in container environment; requires physical hardware for any validation

## Pipeline History
- Initial project setup with PlatformIO and ESP32-S3 target
- Integration with OpenAI Whisper API for voice recognition
- Integration with OpenAI ChatGPT API for AI responses
- LVGL graphics library integration for display rendering
- WiFiManager integration for WiFi configuration

## Known Issues
- No automated testing possible without hardware
- Requires external API keys (OpenAI) for full functionality
- Hardware dependencies: QMI8658 sensor, I2S microphone, 320x240 TFT display
- PlatformIO build requires ESP32 Arduino core installed

## Notes
- Source code in `src/` directory with main.cpp as entry point
- Custom libraries in `lib/` directory (LVGL, TFT_eSPI, QMI8658)
- Uses LittleFS for file storage (display fonts, animations)
- Hardware: ESP32-S3-WROOM-1 or compatible module
- Build target: `esp32s3` in platformio.ini
- PlatformIO environment: `waveshare_esp32_s3`
- Dependencies include: WiFiManager, LVGL, TFT_eSPI, QMI8658, I2S microphone library
