.PHONY: test clean test-python test-cpp

# Default test target
test: test-python test-cpp

# Run Python tests
test-python:
	@echo "Running Python tests..."
	pytest test/test_native/ -v

# Run C++ Unity tests (if any exist)
test-cpp:
	@echo "Running C++ tests..."
	@if [ -f test/test_native/test_placeholder ]; then \
		./test/test_native/test_placeholder; \
	else \
		echo "No C++ tests compiled"; \
	fi
	@if [ -f test/test_native/test_animation_manager ]; then \
		./test/test_native/test_animation_manager; \
	fi

# Build C++ test
build-test:
	@echo "Building C++ tests..."
	@# Build placeholder test with ESP32 compatibility defines
	g++ -DLV_BUILD_TEST -DIRAM_ATTR= -I test/test_native -I lib/lvgl/tests/unity -o test/test_native/test_placeholder test/test_native/test_placeholder.c lib/lvgl/tests/unity/unity.c
	@# Build Animation Manager Unity tests
	g++ -DLV_BUILD_TEST -DIRAM_ATTR= -I test/test_native -I lib/lvgl/tests/unity -o test/test_native/test_animation_manager test/test_native/test_animation_manager.cpp lib/lvgl/tests/unity/unity.c

# Clean test artifacts
clean:
	@echo "Cleaning test artifacts..."
	rm -f test/test_native/test_placeholder
	rm -rf .pytest_cache __pycache__
	rm -rf test/test_native/wav_uploads/*.wav
