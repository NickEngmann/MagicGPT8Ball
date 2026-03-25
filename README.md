# Magic (GPT)8 Ball 🎱

## Overview

The Magic (GPT)8 Ball is a modern reinvention of the classic fortune-telling toy, powered by AI and IoT technology. It features voice recognition, motion sensing, and real-time AI responses through ChatGPT. When shaken, it records your question through a built-in microphone, processes it using OpenAI's APIs, and displays a mystical response on its integrated circular display.

## Features

- Voice-activated recording with automatic silence detection
- Motion-based activation using QMI8658 6-axis IMU
- Real-time transcription using OpenAI's Whisper API
- AI-powered responses from ChatGPT
- Smooth animations and UI transitions
- RGB LED status indicator
- Haptic feedback through dual vibration motors
- WiFi manager for easy network setup
- Offline mode with classic Magic 8 Ball responses
- Built-in battery management and charging

## Hardware Requirements

![Project Wiring Diagram](img/1.png)

### Core Components

- Waveshare ESP32-S3 1.28" LCD Development Board
  - ESP32-S3 microcontroller
  - 1.28" Round LCD Display (240×240 resolution)
  - Built-in QMI8658 6-axis IMU
  - USB-C for programming and charging
- MAX9814 Microphone Amplifier Module
- 2x Vibration Motors
- WS2812B RGB LED
- 1200mAh LiPo Battery
- 3D printed enclosure (files TBD)

### Pin Connections

#### Built-in Components (ESP32-S3 Board)

- LCD Display
  - DC: GPIO8
  - CS: GPIO9
  - CLK: GPIO10
  - MOSI: GPIO11
  - RST: GPIO12
  - BL: GPIO40
- QMI8658 IMU
  - SDA: GPIO6
  - SCL: GPIO7

#### External Components

- MAX9814 Microphone
  - VDD → 3.3V
  - GND → GND
  - OUT → GPIO2 (ADC1_CH1)
- Vibration Motors
  - Motor 1: GPIO5
  - Motor 2: GPIO13
- RGB LED: GPIO3

## Software Setup

### Development Environment

1. Install Visual Studio Code
2. Install PlatformIO IDE extension
3. Clone the repository:

   ```bash
   git clone https://github.com/NickEngmann/MagicGPT8Ball.git
   cd MagicGPT8Ball
   ```

### Dependencies

- WiFiManager for network configuration
- ArduinoJson (7.x) for API communication
- LVGL for UI and animations
- TFT_eSPI for display driver
- Adafruit_NeoPixel for RGB LED control

### APIs and Services

1. Set up a val.town account:
   - Deploy the included `val.town.js` function
   - Update the endpoint URL in `main.cpp`
2. Configure OpenAI API key in val.town environment

### Building and Flashing

1. Open project in VS Code with PlatformIO
2. Install dependencies:

   ```bash
   pio lib install
   ```

3. Build and upload:

   ```bash
   pio run --target upload
   ```

### Environment Configuration

1. In the project root directory, create a `.env` file with your val.town endpoint and device token:

   ```ini
   VALTOWN_URL="https://your-valtown-endpoint.val.run"
   DEVICE_TOKEN="your-device-token"
   ```

2. For reference, an `.env.example` file is provided:

   ```ini
   VALTOWN_URL="https://example-valtown-endpoint.val.run"
   DEVICE_TOKEN="example-device-token"
   ```

   **Note:** Never commit your actual `.env` file to version control. The `.env.example` file serves as a template.

3. File locations should follow this structure:

   ```
   MagicGPT8Ball/
   ├── .env                  # Your actual configuration (do not commit)
   ├── .env.example         # Template for others (safe to commit)
   ├── generate_env.py      # Handles environment setup
   ├── data/                # Generated during build
   └── ...
   ```

4. During build:
   - The system automatically copies your `.env` file to the device's filesystem
   - If `.env` is missing, it will use `.env.example` as a fallback
   - Environment variables are securely stored on the device

5. To update configuration:
   - Modify `.env` file
   - Rebuild and upload filesystem:

     ```bash
     pio run -t uploadfs
     ```

   - Upload program:

     ```bash
     pio run -t upload
     ```

## Usage Instructions

### First-Time Setup

1. Power on the device
2. Connect to "MagicGPT8Ball" WiFi network
3. Configure your WiFi through the captive portal
4. Device will restart and connect to your network

### Daily Use

1. Wake device by moving it or pressing the power button
2. Wait for "Shake me" prompt
3. Shake device to activate recording
4. Speak your question clearly
5. Wait for response (blue animation indicates processing)
6. Device will display the AI-generated response
7. Shake again for a new question

### LED Status Indicators

- Blue pulse: Starting up
- Solid green: Ready
- Red blink: Recording
- Cyan pulse: Processing
- Yellow blink: Offline mode
- Purple blink: Error state

## Advanced Features

### Debug Mode

Enable detailed logging by uncommenting `#define ENABLE_DEBUG` in the following files:

- `Recorder.h` - Audio debugging
- `main.cpp` - System debugging

### Voice Detection Parameters

Adjust sensitivity in `Recorder.h`:

- `AUDIO_THRESHOLD`: Voice detection threshold
- `SILENCE_TIMEOUT`: Silence duration before stopping
- `MAX_RECORD_SECONDS`: Maximum recording duration

### Animation Settings

Customize animations in `Animations.h`:

- `MOTION_SMOOTHING`: Movement smoothness
- `GYRO_SENSITIVITY`: Motion sensitivity
- `IDLE_AMPLITUDE`: Idle animation range

## Project Structure

```
├── src/
│   ├── main.cpp              # Main application logic
│   ├── Animations.*          # Display animations
│   ├── Recorder.*           # Audio recording
│   ├── TextStateManager.*   # Display text handling
│   ├── VibrationManager.*   # Haptic feedback
│   └── LEDLogger.*         # RGB LED control
├── lib/
│   └── QMI8658/            # IMU driver
└── val.town.js             # Serverless API handler
```

## Troubleshooting

### Common Issues

1. WiFi Connection Problems
   - Reset configuration by holding boot button
   - Check serial output for connection status
   - Verify network credentials in portal

2. Recording Issues
   - Check microphone connections
   - Verify ADC readings in debug mode
   - Adjust voice detection threshold

3. Display Problems
   - Verify SPI connections
   - Check power supply voltage
   - Update TFT_eSPI configuration

### Error Messages

- "Wifi: X" - No network connection
- "Error: processing request" - API communication failed
- "Error: recording failed" - Audio capture issue

<<<<<<< Updated upstream
=======
## Build Configuration

### PlatformIO Setup

**Board**: waveshare_esp32_s3
**Framework**: Arduino
**Platform**: espressif32@6.5.0
**Monitor Speed**: 115200 baud

**Build Commands**:

```bash
# Install library dependencies
pio lib install

# Build and upload firmware
pio run --target upload

# Upload filesystem only
pio run -t uploadfs

# Monitor serial output
pio mon

# Clean build artifacts
pio run --target clean
```

### Memory Configuration

- **Flash**: 16MB
- **PSRAM**: 8MB Quad SPI
- **Filesystem**: LittleFS (8MB partition)
- **Partitions**: default_8MB.csv

### Build System

Custom build scripts in `platformio.ini`:
- `generate_env.py` — Pre-build script that copies `.env` or `.env.example` to data directory
- LittleFS integration for environment variables storage

### Docker Support

Development can be performed in a Docker sandbox using:
- Image: `gcc:14`
- Command: `make test` for running pytest test suite

## Testing

### Test Suite Overview

The project includes comprehensive test suites using pytest for Python and Unity for C++ to validate module functionality without requiring hardware:

**Test Framework**: pytest 7.4.4 (Python 3.12.3), Unity (C++)
**Test Command**: `make test`, `pytest test/ -v`, or `python3 test_runner.py`
**Current Status**: 132 Python tests passed (100% pass rate)

### Test Files

#### Python Tests

| Test File | Tests | Module | Description |
|-----------|-------|--------|-------------|
| `test_integration_py.py` | 48 | Integration | Complete user journey flow tests |
| `test_integration_py_test.py` | 48 | Integration | Additional integration scenarios |
| `test_led_logger_py.py` | 9 | LEDLogger | RGB LED state and pattern tests |
| `test_recorder_py.py` | 9 | Recorder | Audio recording and buffer tests |
| `test_text_state_manager_py.py` | 16 | TextStateManager | Display state management tests |
| `test_vibration_manager_py.py` | 9 | VibrationManager | Motor control and timing tests |
| `test_environment_py.py` | 15 | Environment | Configuration and parsing tests |
| `test_native_tests.py` | 18 | Verification | Verifies C++ test file existence |

#### C++ Native Tests (Unity Framework)

| Test File | Tests | Module | Description |
|-----------|-------|--------|-------------|
| `test_native/test_environment.c` | 9 | Environment | .env file parsing tests |
| `test_native/test_recorder.c` | 11 | Recorder | Audio sampling tests |
| `test_native/test_vibration_manager.c` | 9 | Vibration | Motor control tests |
| `test_native/test_led_logger.c` | 11 | LED | State and pattern tests |
| `test_native/test_text_state_manager.c` | 11 | State | State machine tests |
| `test_native/test_wav_upload.c` | 12 | WAV | Upload and validation tests |

### Running Tests

```bash
# Run all tests using pytest
make test

# Run all tests using the test runner
python3 test_runner.py

# Run with verbose output
pytest test/ -v

# Run specific test file
pytest test/test_led_logger_py.py -v

# Run with coverage
pytest test/ -v --cov=. --cov-report=html
```

### Test Coverage

- **Unit Tests**: Individual module validation (LEDLogger, Recorder, TextStateManager, VibrationManager, Environment, WAV Upload)
- **Integration Tests**: Complete workflow scenarios (shake → record → upload → response)
- **Configuration Tests**: Audio parameters, pin assignments, timing constants
- **Error Handling**: WiFi disconnection, upload failures, invalid configurations
- **File Integrity**: WAV header structure validation, sample rate verification

All tests use mocked implementations to avoid hardware dependencies, allowing CI/CD integration and rapid development iteration.

### Native Test Directory

See `test/README.md` for detailed documentation on test structure, coverage, and examples.

## Documentation

- **MARISOL.md** - Pipeline context with build, test, and history information
- **Source Code** - Individual module documentation in header files
- **PlatformIO Docs** - https://docs.platformio.org/

>>>>>>> Stashed changes
## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow existing code style
4. Add unit tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Acknowledgments

- OpenAI for ChatGPT and Whisper APIs
- Waveshare for ESP32-S3 hardware
- LVGL team for graphics library
- val.town for serverless hosting
- Open source community for libraries and tools
