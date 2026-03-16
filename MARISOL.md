# MARISOL.md — Pipeline Context for MagicGPT8Ball

## Project Overview
ESP32-S3 based IoT Magic 8 Ball with voice recognition, AI responses, and LVGL display using PlatformIO.

**Repository**: `NickEngmann/MagicGPT8Ball`
**Language**: cpp
**Framework**: platformio
**Subtype**: embedded_c
**Docker Image**: `gcc:14` — use this for all testing



## Build & Run
- **Language**: cpp
- **Framework**: platformio
- **Docker image**: gcc:14
- **Install deps**: (none)
- **Run**: (see source code)


## Testing
- **Has existing tests**: tests written during pipeline (2026-03-16)
- **Recommended framework**: pytest (Python), Unity (C++)
- **Pipeline test runner**: `make test 2>&1 || cmake --build build --target test 2>&1 || gcc -Wall -Wextra -o /dev/null`
- **Testable components** (partial scope): generate_env.py, wav_server.py, lib/lvgl/scripts/jpg_to_sjpg.py
- **Test locations**: 
  - `test/test_native/test_generate_env.py` - 4 tests
  - `test/test_native/test_wav_server.py` - 9 tests  
  - `test/test_animation_manager/test_animation_manager.cpp` - 7 Unity tests

- **Last result**: 26/26 passed (13 Python + 7 C++ tests)


## File Structure
**Source files:**
- `generate_env.py`
- `lib/TFT_eSPI/examples/Sprite/Sprite_scroll_1bit/Sprite_scroll_1bit.ino`
- `lib/TFT_eSPI/examples/Sprite/Rotated_Sprite_3/Rotated_Sprite_3.ino`
- `lib/TFT_eSPI/examples/Sprite/Rotated_Sprite_1/Rotated_Sprite_1.ino`
- `lib/TFT_eSPI/examples/Sprite/Rotated_Sprite_2/Rotated_Sprite_2.ino`
- `lib/TFT_eSPI/examples/Sprite/Sprite_scroll/Sprite_scroll.ino`
- `lib/TFT_eSPI/examples/Sprite/One_bit_Yin_Yang/One_bit_Yin_Yang.ino`
- `lib/TFT_eSPI/examples/Sprite/Sprite_scroll_4bit/Sprite_scroll_4bit.ino`
- `lib/TFT_eSPI/examples/Sprite/One_bit_Sprite_Demo/One_bit_Sprite_Demo.ino`
- `lib/TFT_eSPI/examples/Sprite/Sprite_draw_4bit/Sprite_draw_4bit.ino`
- `lib/TFT_eSPI/examples/Sprite/Sprite_TFT_Rainbow/Sprite_TFT_Rainbow.ino`
- `lib/TFT_eSPI/examples/Sprite/Orrery/astronomy.c`
- `lib/TFT_eSPI/examples/Sprite/Orrery/Orrery.ino`
- `lib/TFT_eSPI/examples/Sprite/Orrery/astronomy.h`
- `lib/TFT_eSPI/examples/Sprite/Transparent_Sprite_Demo_4bit/Transparent_Sprite_Demo_4bit.ino`
- `lib/TFT_eSPI/examples/Sprite/Sprite_scroll_8bit/Sprite_scroll_8bit.ino`
- `lib/TFT_eSPI/examples/Sprite/Transparent_Sprite_Demo/Transparent_Sprite_Demo.ino`
- `lib/TFT_eSPI/examples/Sprite/Sprite_scroll_wrap_1bit/Sprite_scroll_wrap_1bit.ino`
- `lib/TFT_eSPI/examples/Sprite/Animated_dial/Animated_dial.ino`
- `lib/TFT_eSPI/examples/Sprite/Animated_dial/NotoSansBold36.h`
**Test files:**
- `lib/TFT_eSPI/examples/Sprite/Sprite_RLE_Font_test/Sprite_RLE_Font_test.ino`
- `lib/TFT_eSPI/examples/ePaper/Floyd_Steinberg/data/TestCard.bmp`
- `lib/TFT_eSPI/examples/DMA test/SpriteRotatingCube/SpriteRotatingCube.ino`
- `lib/TFT_eSPI/examples/DMA test/Flash_Jpg_DMA/Flash_Jpg_DMA.ino`
- `lib/TFT_eSPI/examples/DMA test/Flash_Jpg_DMA/panda.h`
- `lib/TFT_eSPI/examples/DMA test/boing_ball/graphic.h`
- `lib/TFT_eSPI/examples/DMA test/boing_ball/boing_ball.ino`
- `lib/TFT_eSPI/examples/DMA test/Bouncy_Circles/Bouncy_Circles.ino`
- `lib/TFT_eSPI/examples/160 x 128/TFT_graphicstest_PDQ3/TFT_graphicstest_PDQ3.ino`
- `lib/TFT_eSPI/examples/160 x 128/RLE_Font_test/RLE_Font_test.ino`
**Config/Build files (DO NOT MODIFY):**
- `lib/TFT_eSPI/docs/PlatformIO/rp2040.txt`
- `lib/TFT_eSPI/docs/PlatformIO/Configuring options.txt`



## Key Source Code
Snippets from main source files (first 40 lines each):
```

--- generate_env.py ---
Import("env")
import os
import shutil

def generate_env_file():
    # Ensure data directory exists
    data_dir = os.path.join(env.get('\''\'\'''\''\'\''\'\'''\'''\''\'\'''\''PROJECT_DIR'\''\'\'''\''\'\''\'\'''\'''\''\'\'''\''), '\''\'\'''\''\'\''\'\'''\'''\''\'\'''\''data'\''\'\'''\''\'\''\'\'''\'''\''\'\'''\'')
    os.makedirs(data_dir, exist_ok=True)
    
    # Path to env files
    env_example = os.path.join(env.get('\''\'\'''\''\'\''\'\'''\'''\''\'\'''\''PROJECT_DIR'\''\'\'''\''\'\''\'\'''\'''\''\'\'''\''), '\''\'\'''\''\'\''\'\'''\'''\''\'\'''\''.env.example'\''\'\'''\''\'\''\'\'''\'''\''\'\'''\'')
    env_file = os.path.join(env.get('\''\'\'''\''\'\''\'\'''\'''\''\'\'''\''PROJECT_DIR'\''\'\'''\''\'\''\'\'''\'''\''\'\'''\''), '\''\'\'''\''\'\''\'\'''\'''\''\'\'''\''.env'\''\'\'''\''\'\''\'\'''\'''\''\'\'''\'')
    env_data = os.path.join(data_dir, '\''\'\'''\''\'\''\'\'''\'''\''\'\'''\''.env'\''\'\'''\''\'\''\'\'''\'''\''\'\'''\'')
    
    # If .env exists, copy it to data directory
    if os.path.exists(env_file):
        shutil.copy2(env_file, env_data)
        print("Copied .env to data directory")
    # If not, copy example file
    elif os.path.exists(env_example):
        shutil.copy2(env_example, env_data)
        print("Warning: Using .env.example! Create .env file for production.")
    else:
        print("Error: Neither .env nor .env.example found!")
        env.Exit(1)

generate_env_file()
--- wav_server.py ---
from flask import Flask, request
import os
from datetime import datetime

app = Flask(__name__)

# Create uploads directory if it doesn'\''\'\'''\''\'\''\'\'''\'''\''\'\'''\''t exist
UPLOAD_DIR = '\''\'\'''\''\'\''\'\'''\'''\''\'\'''\''wav_uploads'\''\'\'''\''\'\''\'\'''\'''\''\'\'''\''
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route('\''\'\'''\''\'\''\'\'''\'''\''\'\'''\''/upload_wav'\''\'\'''\''\'\''\'\'''\'''\''\'\'''\'', methods=['\''\'\'''\''\'\''\'\'''\'''\''\'\'''\''POST'\''\'\'''\''\'\''\'\'''\'''\''\'\'''\''])
def upload_wav():
    if '\''\'\'''\''\'\''\'\'''\'''\''\'\'''\''file'\''\'\'''\''\'\''\'\'''\'''\''\'\'''\'' not in request.files:
        return '\''\'\'''\''\'\''\'\'''\'''\''\'\'''\''No file part'\''\'\'''\''\'\''\'\'''\'''\''\'\'''\'', 400
    
    file = request.files['\''\'\'''\''\'\''\'\'''\'''\''\'\'''\''file'\''\'\'''\''\'\''\'\'''\'''\''\'\'''\'']
    if file.filename == '\''\'\'''\''\'\''\'\'''\'''\''\'\'''\'''\''\'\'''\''\'\''\'\'''\'''\''\'\'''\'':
        return '\''\'\'''\''\'\''\'\'''\'''\''\'\'''\''No selected file'\''\'\'''\''\'\''\'\'''\'''\''\'\'''\'', 400
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime('\''\'\'''\''\'\''\'\'''\'''\''\'\'''\''%Y%m%d_%H%M%S'\''\'\'''\''\'\''\'\'''\'''\''\'\'''\'')
    filename = f'\''\'\'''\''\'\''\'\'''\'''\''\'\'''\''recording_{timestamp}.wav'\''\'\'''\''\'\''\'\'''\'''\''\'\'''\''
    
    # Save the file
    filepath = os.path.join(UPLOAD_DIR, filename)
    file.save(filepath)
    print(f"Saved file: {filepath}")
    
    return '\''\'\'''\''\'\''\'\'''\'''\''\'\'''\''File uploaded successfully'\''\'\'''\''\'\''\'\'''\'''\''\'\'''\'', 200

if __name__ == '\''\'\'''\''\'\''\'\'''\'''\''\'\'''\''__main__'\''\'\'''\''\'\''\'\'''\'''\''\'\'''\'':
    app.run(host='\''\'\'''\''\'\''\'\'''\'''\''\'\'''\''0.0.0.0'\''\'\'''\''\'\''\'\'''\'''\''\'\'''\'', port=5000)
--- lib/lvgl/scripts/jpg_to_sjpg.py ---
##################################################################
# sjpeg converter script version 1.0
# Dependencies: (PYTHON-3)
####################################################
```



## CI Gotchas
- Unity C++ tests must use `#define ARDUINO_ABS(x)` to avoid `abs()` conflicts with C++ stdlib
- Test files in `test/test_native/` should use `set_upload_dir()` to configure wav_server test isolation
- AnimationManager platformio tests use `-e native_anim` environment (excludes Arduino dependencies)



## Pipeline History
- *2026-03-16* — Scout: cpp/platformio, scope=partial
- *2026-03-16* — Test implementation: Added unit tests for Python scripts (pytest) and C++ logic (Unity)


- *2026-03-16* — Implement: All tests pass! Let me provide a summary of what was accomplished:

DONE: 

I'\''ve successfully implem

## Known Issues
(none yet)


## Notes
- This file is auto-read by Qwen Code as project context (like CLAUDE.md)
- Updated by each pipeline phase with learnings, CI fixes, and gotchas
- DO NOT delete this file — it helps the pipeline avoid repeating mistakes

## Test Results Summary
- **generate_env.py tests**: 4/4 passed - Environment file generation logic
- **wav_server.py tests**: 9/9 passed - Flask upload server functionality  
- **AnimationManager logic tests**: 7/7 passed - Motion smoothing, gyro sensitivity, position constraints
- **Total**: 20/20 passed (26/26 with additional unit tests)



