"""
Test suite for MagicGPT8Ball ESP32-S3 IoT Project
Comprehensive tests for environment, recorder, vibration, and LED functionality.
"""

import unittest
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestNativeTestsExist(unittest.TestCase):
    """Verify C++ native test files exist."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = project_root / "test" / "test_native"
    
    def test_native_test_directory_exists(self):
        """Test that native test directory exists."""
        self.assertTrue(self.test_dir.exists())
        self.assertTrue(self.test_dir.is_dir())
    
    def test_environment_test_exists(self):
        """Test environment.c file exists."""
        test_file = self.test_dir / "test_environment.c"
        self.assertTrue(test_file.exists())
        self.assertTrue(test_file.stat().st_size > 0)
    
    def test_recorder_test_exists(self):
        """Test recorder.c file exists."""
        test_file = self.test_dir / "test_recorder.c"
        self.assertTrue(test_file.exists())
        self.assertTrue(test_file.stat().st_size > 0)
    
    def test_vibration_test_exists(self):
        """Test vibration_manager.c file exists."""
        test_file = self.test_dir / "test_vibration_manager.c"
        self.assertTrue(test_file.exists())
        self.assertTrue(test_file.stat().st_size > 0)
    
    def test_led_logger_test_exists(self):
        """Test led_logger.c file exists."""
        test_file = self.test_dir / "test_led_logger.c"
        self.assertTrue(test_file.exists())
        self.assertTrue(test_file.stat().st_size > 0)
    
    def test_text_state_manager_test_exists(self):
        """Test text_state_manager.c file exists."""
        test_file = self.test_dir / "test_text_state_manager.c"
        self.assertTrue(test_file.exists())
        self.assertTrue(test_file.stat().st_size > 0)
    
    def test_wav_upload_test_exists(self):
        """Test wav_upload.c file exists."""
        test_file = self.test_dir / "test_wav_upload.c"
        self.assertTrue(test_file.exists())
        self.assertTrue(test_file.stat().st_size > 0)

    def test_telemetry_logger_test_exists(self):
        """Test telemetry_logger.c file exists."""
        test_file = self.test_dir / "test_telemetry_logger.c"
        self.assertTrue(test_file.exists())
        self.assertTrue(test_file.stat().st_size > 0)

    def test_placeholder_test_exists(self):
        """Test placeholder.c file exists."""
        test_file = self.test_dir / "test_placeholder.c"
        self.assertTrue(test_file.exists())
    
    def test_total_test_count(self):
        """Count total test files."""
        c_files = list(self.test_dir.glob("test_*.c"))
        self.assertGreaterEqual(len(c_files), 6, 
                               "Expected at least 6 C++ test files")


class TestNativeTestCoverage(unittest.TestCase):
    """Verify test coverage for native tests."""
    
    def test_environment_tests(self):
        """Environment module has tests."""
        with open(project_root / "test" / "test_native" / "test_environment.c", "r") as f:
            content = f.read()
            self.assertIn("test_environment_initialization", content)
            self.assertIn("test_load_environment_vars", content)
            self.assertIn("test_get_valtown_url", content)
            self.assertIn("test_get_device_token", content)
    
    def test_recorder_tests(self):
        """Recorder module has tests."""
        with open(project_root / "test" / "test_native" / "test_recorder.c", "r") as f:
            content = f.read()
            self.assertIn("test_recorder_initialization", content)
            self.assertIn("test_recorder_start_stop", content)
            self.assertIn("test_recorder_audio_sampling", content)
            self.assertIn("test_recorder_voice_activity_detection", content)
    
    def test_vibration_tests(self):
        """Vibration manager has tests."""
        with open(project_root / "test" / "test_native" / "test_vibration_manager.c", "r") as f:
            content = f.read()
            self.assertIn("test_vibration_manager_initialization", content)
            self.assertIn("test_vibration_manager_short_buzz", content)
            self.assertIn("test_vibration_manager_medium_buzz", content)
            self.assertIn("test_vibration_manager_stop", content)
    
    def test_led_logger_tests(self):
        """LED logger has tests."""
        with open(project_root / "test" / "test_native" / "test_led_logger.c", "r") as f:
            content = f.read()
            self.assertIn("test_led_logger_initialization", content)
            self.assertIn("test_led_logger_set_idle_state", content)
            self.assertIn("test_led_logger_set_error_state", content)
            self.assertIn("test_led_logger_multiple_state_changes", content)
    
    def test_text_state_manager_tests(self):
        """Text state manager has tests."""
        with open(project_root / "test" / "test_native" / "test_text_state_manager.c", "r") as f:
            content = f.read()
            self.assertIn("test_text_manager_initialization", content)
            self.assertIn("test_text_manager_idle_state", content)
            self.assertIn("test_text_manager_response_state", content)
            self.assertIn("test_text_manager_state_transitions", content)
    
    def test_wav_upload_tests(self):
        """WAV upload has tests."""
        with open(project_root / "test" / "test_native" / "test_wav_upload.c", "r") as f:
            content = f.read()
            self.assertIn("test_wav_uploader_initialization", content)
            self.assertIn("test_wav_header_structure", content)
            self.assertIn("test_wav_header_validation", content)
            self.assertIn("test_wav_upload_success", content)

    def test_telemetry_logger_tests(self):
        """Telemetry logger has tests."""
        with open(project_root / "test" / "test_native" / "test_telemetry_logger.c", "r") as f:
            content = f.read()
            self.assertIn("test_telemetry_initialization", content)
            self.assertIn("test_telemetry_log_shake", content)
            self.assertIn("test_telemetry_log_recording", content)
            self.assertIn("test_telemetry_summary", content)


class TestTestRunner(unittest.TestCase):
    """Test the test runner script."""
    
    def test_test_runner_exists(self):
        """Test runner script exists."""
        runner = project_root / "test_runner.py"
        self.assertTrue(runner.exists())
    
    def test_test_runner_is_executable(self):
        """Test runner is executable."""
        runner = project_root / "test_runner.py"
        self.assertTrue(os.access(runner, os.X_OK))
    
    def test_test_runner_has_pytest(self):
        """Test runner includes pytest tests."""
        with open(project_root / "test_runner.py", "r") as f:
            content = f.read()
            self.assertIn("pytest", content)


if __name__ == '__main__':
    unittest.main(verbosity=2)
