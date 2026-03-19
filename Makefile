# MagicGPT8Ball Makefile
# Build and test commands for the ESP32-S3 Magic 8 Ball project

.PHONY: all build upload test clean flash

all: build

# Build the project
build:
	@echo "Building MagicGPT8Ball..."
	@pio run

# Upload firmware to ESP32
upload:
	@echo "Uploading firmware to ESP32..."
	@pio run --target upload

# Flash filesystem
flash:
	@echo "Flashing filesystem..."
	@pio run --target uploadfs

# Run tests
test:
	@echo "Running tests..."
	@echo "Running Python tests with pytest..."
	@pip install pytest flask 2>/dev/null || true
	@test -d test/test_native && pytest test/test_native/ -v || echo "No pytest tests found in test/test_native/"
	@echo "Running PlatformIO native tests..."
	@pio test

# Run pytest only
test-python:
	@echo "Running Python tests..."
	@pip install pytest flask 2>/dev/null || true
	@python -m pytest test/test_native/ -v

# Run PlatformIO tests only
test-pio:
	@echo "Running PlatformIO tests..."
	@pio test

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf .pio
	@rm -rf data/.env
	@rm -rf wav_uploads/*.wav

# Help command
help:
	@echo "MagicGPT8Ball Makefile targets:"
	@echo "  make build     - Build the project"
	@echo "  make upload    - Upload firmware to ESP32"
	@echo "  make flash     - Flash filesystem"
	@echo "  make test      - Run all tests"
	@echo "  make test-python - Run Python tests only"
	@echo "  make test-pio  - Run PlatformIO tests only"
	@echo "  make clean     - Clean build artifacts"
	@echo "  make help      - Show this help"
