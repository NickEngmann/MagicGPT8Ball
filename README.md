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
- LVGL-based graphical interface with motion tracking

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
- QMI8658 IMU driver

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

### PlatformIO Configuration

The project uses PlatformIO with the following configuration (from `platformio.ini`):

- **Platform**: `espressif32@6.5.0`
- **Board**: `waveshare_esp32_s3`
- **Framework**: Arduino
- **Filesystem**: LittleFS
- **Monitor Speed**: 115200

#### Build Environment

- **Library Dependencies**:
  - [WiFiManager](https://github.com/tzapu/WiFiManager.git)
  - ArduinoJson ^7.2.1
  - Adafruit NeoPixel ^1.12.0
- **Build Flags**: `-DCONFIG_LITTLEFS_FOR_IDF_3_2`
- **Extra Scripts**: `pre:generate_env.py`

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

### Audio Recording Parameters

The recorder uses the following default settings (configurable in `Recorder.h`):

- **Sample Rate**: 32000 Hz
- **Channels**: Mono (1)
- **Bit Depth**: 16-bit
- **DC Offset**: 1250 (1.25V bias from MAX9814)
- **Silence Timeout**: 2000 ms
- **Audio Threshold**: 500 (sensitivity for voice detection)
- **Maximum Recording Duration**: 10 seconds

### Animation Settings

Customize animations in `Animations.h`:

- **Motion Smoothing**: `MOTION_SMOOTHING = 0.95f` (velocity tracking factor)
- **Gyro Sensitivity**: `GYRO_SENSITIVITY = 0.08f` (motion response factor)
- **Idle Amplitude**: `IDLE_AMPLITUDE = 15.0f` (floating animation range)
- **Idle Speed**: `IDLE_SPEED = 0.001f` (animation timing)
- **Screen Margin**: `SCREEN_MARGIN = 0.4f` (circular boundary ratio)
- **Edge Buffer**: `EDGE_BUFFER = 0.15f` (allowable overflow)
- **Font Reduction**: `FONT_REDUCTION = 90` (label font size percentage)

## Project Structure

```
├── src/
│   ├── main.cpp              # Main application logic
│   ├── Animations.*          # Display animations and LVGL interface
│   ├── Recorder.*           # Audio recording and voice detection
│   ├── TextStateManager.*   # Display text handling
│   ├── VibrationManager.*   # Haptic feedback control
│   ├── LEDLogger.*          # RGB LED status indicators
│   └── Environment.h        # Configuration management
├── lib/
│   ├── lvgl/                # LVGL graphics library
│   ├── TFT_eSPI/            # Display driver
│   ├── QMI8658/             # IMU driver
│   └── TFT_eSPI_Setups/     # Custom display setup
├── boards/
│   └── waveshare_esp32_s3.json  # Board configuration
├── hardware/
│   ├── magic8ball.fzz       # Circuit design (Fritzing)
│   └── vibration_motor_circuit/
├── data/                    # Device filesystem (generated)
├── test/                    # Unit tests
├── val.town.js             # Serverless API handler
├── generate_env.py         # Build script for .env handling
├── wav_server.py           # Flask server for WAV uploads
└── platformio.ini          # PlatformIO configuration
```

## Testing

### Python Tests

Test scripts for Python utilities:

- **Test Location**: `test/test_native/`
- **Framework**: pytest
- **Coverage**:
  - `test_generate_env.py` - Environment file generation (4 tests)
  - `test_wav_server.py` - Flask upload server (9 tests)

### C++ Unit Tests

Unity framework tests for embedded logic:

- **Test Location**: `test/test_animation_manager/`
- **Framework**: Unity
- **Coverage**:
  - `test_animation_manager.cpp` - AnimationManager logic (7 tests)
  - Tests verify motion smoothing, gyro sensitivity, and position constraints

#### Test Execution

Run tests in sandbox container:

```bash
# Python tests
cd test/test_native
pytest

# C++ tests (requires PlatformIO native environment)
pio test -e native_anim
```

**CI Gotchas**:
- Unity C++ tests must use `#define ARDUINO_ABS(x)` to avoid `abs()` conflicts with C++ stdlib
- Test files in `test/test_native/` should use `set_upload_dir()` to configure wav_server test isolation
- AnimationManager platformio tests use `-e native_anim` environment (excludes Arduino dependencies)

## Troubleshooting

### Common Issues

1. **WiFi Connection Problems**
   - Reset configuration by holding boot button
   - Check serial output for connection status
   - Verify network credentials in portal

2. **Recording Issues**
   - Check microphone connections
   - Verify ADC readings in debug mode
   - Adjust voice detection threshold in `Recorder.h`

3. **Display Problems**
   - Verify SPI connections
   - Check power supply voltage
   - Update TFT_eSPI configuration

4. **Motion Detection Issues**
   - Calibrate IMU at startup
   - Check gyro sensitivity settings in `Animations.h`
   - Verify IMU is properly initialized

### Debug Mode

Enable detailed logging by uncommenting `#define ENABLE_DEBUG` in the following files:

- `Recorder.h` - Audio debugging
- `main.cpp` - System debugging

### Error Messages

- "Wifi: X" - No network connection
- "Error: processing request" - API communication failed
- "Error: recording failed" - Audio capture issue
- "ADC not initialized" - Microphone ADC setup failure

### Serial Debug Output

Monitor serial output at 115200 baud:

```bash
pio monitor
```

Key debug indicators:
- ADC voltage readings (should be ~1250 for DC offset)
- Buffer status (recording progress)
- Memory usage (heap and PSRAM)
- Recording state transitions

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

## Technical Details

### Audio Processing

The audio recorder uses ESP32's ADC1 peripheral with the following characteristics:

- **ADC Resolution**: 12-bit
- **Attenuation**: 11dB (3.3V range)
- **Channel**: ADC1_CHANNEL_1 (GPIO2)
- **Buffer Size**: Up to 640KB (10s @ 32kHz, mono, 16-bit)
- **Memory Allocation**: Preferential PSRAM usage with heap fallback

### Motion Tracking

The AnimationManager implements a physics-based motion system:

- **Velocity Integration**: Exponential moving average with smoothing factor
- **Position Constraints**: Circular boundary with rectangular overflow handling
- **Idle Animation**: Sinusoidal combination for organic floating motion
- **Gyro Calibration**: Threshold-based stillness detection (±0.5g)

### Display Configuration

LVGL integration with TFT_eSPI:

- **Screen Resolution**: 240×240 pixels
- **Buffer Size**: ~5760 colors (10% of screen)
- **Color Format**: 16-bit RGB565
- **Animation**: Hardware-accelerated transitions (800ms)
- **Font**: Montserrat 14px with line spacing

### Filesystem Management

LittleFS integration for persistent data:

- **Mount Point**: `/data`
- **Configuration**: Environment files for API credentials
- **Build Script**: `generate_env.py` (PlatformIO pre-build)
- **Auto-provisioning**: Falls back to `.env.example` if missing
