# Magic (GPT)8 Ball 🎱

## Overview

The Magic (GPT)8 Ball is a modern reinvention of the classic fortune-telling toy, powered by AI and IoT technology. It features voice recognition, motion sensing, and an OLED display. The device records audio when shaken, sends it to OpenAI's Whisper API for transcription, processes it with ChatGPT, and responds with voice synthesis.

## Features

- Voice recognition using OpenAI's Whisper API
- AI-powered responses using ChatGPT
- Motion detection with ESP32-S3
- OLED display for visual responses
- WAV file upload server for testing and development

## Hardware

- ESP32-S3 microcontroller
- Waveshare ESP32-S3 OLED board
- Microphone for audio input
- OLED display for visual output

## Software Dependencies

- PlatformIO for ESP32 firmware development
- Python 3.12+ for WAV upload server
- OpenAI API keys for Whisper and ChatGPT

## Installation

### ESP32 Firmware

1. Install PlatformIO IDE or CLI
2. Clone this repository
3. Configure your OpenAI API keys in `.env` (see `.env.example`)
4. Build and upload: `pio run --target upload`

### WAV Upload Server

The project includes a Python Flask server for uploading WAV audio files:

```bash
pip install flask
python wav_server.py
```

The server will start on `http://0.0.0.0:5000` and accept WAV file uploads at the `/upload_wav` endpoint.

## WAV Upload Server API

### POST /upload_wav

Uploads a WAV file from the ESP32 device.

**Request:**
- Method: POST
- Endpoint: `/upload_wav`
- Content-Type: multipart/form-data
- File field: `file`

**Response:**
- 200 OK: "File uploaded successfully"
- Files are saved to `wav_uploads/` directory with timestamps

## Testing

Run tests with pytest:

```bash
python -m pytest tests/ -v
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for ChatGPT and Whisper APIs
- Waveshare for ESP32-S3 hardware
- LVGL team for graphics library
- val.town for serverless hosting
- Open source community for libraries and tools
