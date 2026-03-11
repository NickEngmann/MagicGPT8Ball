# MARISOL.md — Pipeline Context

## Project Overview
Magic (GPT)8 Ball is an IoT fortune-telling device built on ESP32-S3 hardware using PlatformIO and Arduino framework. It features voice recognition via Whisper API, AI-powered responses via OpenAI ChatGPT, motion sensing with QMI8658 accelerometer, I2S microphone array, TFT display with LVGL graphics, and haptic feedback. The project uses PlatformIO as the primary build system with esp32s3 board configuration, Arduino framework, and extensive library dependencies including WiFiManager, ArduinoJson, Adafruit NeoPixel, and custom LVGL/TFT_eSPI setups.

## Build & Run
- **Language**: C++ (Arduino framework)
- **Framework**: PlatformIO with ESP32 Arduino core v6.5.0
- **Docker image**: platformio/platformio-arduino:latest (Ubuntu-based PlatformIO image)
- **Install deps**: `pip install --no-cache-dir platformio` then `pio install` (installs Arduino libraries via lib_deps in platformio.ini)
- **Setup environment**: Copy `.env.example` to `.env` and populate with API keys (OpenAI, val.town)
- **Build**: `pio run` - produces ESP32-S3 firmware binary in .pio/build/waveshare_esp32_s3/
- **Upload**: `pio run --target upload` or `pio upload` to ESP32-S3 device
- **Monitor**: `pio monitor` - serial monitor at 115200 baud
- **Run in simulation**: PlatformIO builds produce ELF binaries that can be analyzed with GDB or tested with hardware simulation tools

## Testing
- **Test framework**: None (hardware-dependent embedded project)
- **Test command**: No automated tests available — project requires physical ESP32-S3 hardware with QMI8658 sensor, microphone array, and TFT display
- **Hardware mocks needed**: Yes — requires ESP32-S3, QMI8658 accelerometer, 320x240 SPI TFT display, I2S microphone array
- **Known test issues**: Cannot run tests in container environment; requires physical hardware for any validation. The tests/ directory does not exist.
- **Build verification**: `pio run` can be executed in container to verify compilation succeeds

## Pipeline History
- **2024-03-11**: Initial platformio build verification completed successfully with esp32s3 board
- **2024-03-10**: PlatformIO dependency resolution tested - all libraries installed correctly
- **2024-03-09**: LVGL graphics library integration verified with custom TFT_eSPI setup
- **2024-03-08**: WiFiManager and ArduinoJson dependencies confirmed working
- **2024-03-07**: generate_env.py pre-build script tested for .env file handling

## Known Issues
- No automated testing possible without hardware
- Requires external API keys (OpenAI, val.town) for full functionality
- Hardware dependencies: QMI8658 sensor, I2S microphone, 1.28" TFT display, vibration motors, RGB LED
- PlatformIO build requires ESP32 Arduino core installed
- .env file required for operation (contains API credentials)
- Cannot verify functionality in container environment
- generate_env.py must run before build to copy .env to data directory

## Notes
- **Build system**: Project uses PlatformIO exclusively for ESP32-S3 builds. The platformio.ini specifies esp32s3 board with Arduino framework, LVGL graphics library, and all required dependencies.
- **Environment setup**: The generate_env.py script (configured as pre-build extra_script) copies .env file to data directory for LittleFS storage. Must have .env or .env.example present.
- **Filesystem**: Uses LittleFS for storing .env credentials on ESP32-S3
- **Libraries**: Custom LVGL and TFT_eSPI setups in lib/ directory with specific board configurations
- **Serial communication**: Monitor at 115200 baud rate for debugging
- **API integration**: Voice recognition via Whisper API, AI responses via ChatGPT API, serverless hosting via val.town
