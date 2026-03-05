# MARISOL.md — Pipeline Context for MagicGPT8Ball

## Project Overview
IoT Magic 8 Ball device with voice recognition and AI responses built on ESP32-S3 using PlatformIO and Arduino framework.

## Build & Run
- **Language**: cpp
- **Framework**: arduino
- **Docker image**: python:3.12-slim
- **Install deps**: `pip install --no-cache-dir platformio pytest 2>&1 | tail -5`
- **Run**: (see source code)

## Testing
- **Test framework**: none
- **Test command**: `python -m pytest tests/ -v`
- **Hardware mocks needed**: yes (platformio)
- **Last result**: 116/116 passed

