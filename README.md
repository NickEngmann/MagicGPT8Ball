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
MagicGPT8Ball/
├── src/                    # Main application source code
│   ├── main.cpp           # Application entry point and main loop
│   ├── Animations.cpp     # Display animation implementations
│   ├── Animations.h       # Animation module interface
│   ├── Recorder.cpp       # Audio recording and voice detection
│   ├── Recorder.h         # Recorder module interface
│   ├── TextStateManager.cpp # Display text state management
│   ├── TextStateManager.h # Text state manager interface
│   ├── VibrationManager.h # Haptic feedback control
│   ├── LEDLogger.cpp      # RGB LED state machine
│   ├── LEDLogger.h        # LED control interface
│   ├── TelemetryLogger.h  # Event logging and metrics
│   └── Environment.h      # Environment variable handling
├── lib/                    # External libraries
│   ├── lvgl/              # LVGL graphics library
│   ├── TFT_eSPI/          # Display driver library
│   ├── TFT_eSPI_Setups/   # Custom TFT_eSPI configurations
│   └── QMI8658/           # IMU sensor driver
├── test/                   # Test suite
│   ├── test_native/       # C++ Unity framework tests
│   │   ├── test_environment.c    # Environment module tests
│   │   ├── test_recorder.c       # Recorder module tests
│   │   ├── test_vibration_manager.c # Vibration tests
│   │   ├── test_led_logger.c     # LED logger tests
│   │   ├── test_text_state_manager.c # Text state tests
│   │   ├── test_wav_upload.c     # WAV header tests
│   │   ├── test_placeholder.c    # Framework smoke tests
│   │   └── test_telemetry_logger.c # Telemetry tests
│   ├── test_lvgl_render/      # LVGL rendering tests
│   │   └── test_render.c         # Display rendering tests
│   ├── test_generate_env.py     # Build script tests
│   ├── test_wav_server.py       # Server tests
│   ├── test_jpg_to_sjpg.py      # Image conversion tests
│   ├── test_telemetry_logger_py.py # Telemetry tests
│   └── test_runner.py           # Unified test runner
├── data/                   # Generated data (build output)
├── boards/                 # Board-specific configurations
├── hardware/               # Hardware documentation
├── img/                    # Images and diagrams
├── wav_uploads/           # Test WAV file uploads
├── val.town.js            # Serverless API handler
├── generate_env.py        # Build-time environment setup
├── wav_server.py          # Test WAV upload server
├── platformio.ini         # PlatformIO build configuration
├── .env.example           # Environment variable template
└── test_runner.py         # Unified test runner
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

## Testing

### Test Suite Overview

The project includes a comprehensive test suite with 108 tests covering Python utilities and C++ native modules.

**Test Coverage:**

| Test Suite | Type | Tests | Coverage |
|------------|------|-------|----------|
| `test_native/` | C++ Unity | 64 tests | Core modules: Recorder, VibrationManager, LEDLogger, TextStateManager, Environment |
| `test_lvgl_render/` | C++ Unity | 8 tests | LVGL rendering functionality |
| `test_generate_env.py` | Python unittest | 14 tests | Environment file generation |
| `test_wav_server.py` | Python unittest | 12 tests | Flask WAV upload server |
| `test_jpg_to_sjpg.py` | Python unittest | 24 tests | LVGL SJPG conversion |
| `test_telemetry_logger_py.py` | Python unittest | 17 tests | Telemetry logging |
| **Total** | | **139 tests** | |

### Running Tests

**Python Tests:**

```bash
cd test
python3 -m pytest . -v
```

**C++ Native Tests:**

```bash
python3 test_runner.py
```

**Individual Python Test Files:**

```bash
python3 test/test_generate_env.py
python3 test/test_wav_server.py
python3 test/test_jpg_to_sjpg.py
python3 test/test_telemetry_logger_py.py
```

### Test File Locations

```
test/
├── test_native/           # C++ Unity framework tests
│   ├── test_environment.c     # 8 tests - Environment variable loading
│   ├── test_recorder.c        # 6 tests - Audio recording functionality
│   ├── test_vibration_manager.c # 7 tests - Vibration motor control
│   ├── test_led_logger.c      # 7 tests - RGB LED state machine
│   ├── test_text_state_manager.c # 10 tests - Display text state transitions
│   ├── test_wav_upload.c      # 6 tests - WAV file header structure
│   ├── test_placeholder.c     # 10 tests - Unity framework smoke tests
│   └── test_telemetry_logger.c # 12 tests - Telemetry logging
├── test_lvgl_render/         # LVGL rendering tests
│   └── test_render.c           # 8 tests - Display rendering
├── test_generate_env.py      # 14 tests - Environment generation
├── test_wav_server.py        # 12 tests - WAV upload server
├── test_jpg_to_sjpg.py       # 24 tests - Image conversion
├── test_telemetry_logger_py.py # 17 tests - Telemetry logging
└── test_runner.py            # Unified test runner
```

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
